from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from sqlalchemy.orm import Session
from ..database import get_db
from .. import models
from .monsters import search_monsters
from .references import do_reference_search
from .generation import call_llm
from ..query_analyzer import analyze_query, get_search_summary
from ..game.dm_chat_handler import DMChatHandler

router = APIRouter()


class CreateSessionRequest(BaseModel):
    title: str | None = None
    user_id: int | None = None
    provider: str | None = None
    model: str | None = None
    include_context: bool = True
    top_k: int = 5


class CreateMessageRequest(BaseModel):
    role: str
    content: str


class UpdateSessionRequest(BaseModel):
    title: str | None = None
    provider: str | None = None
    model: str | None = None
    include_context: bool | None = None
    top_k: int | None = None


@router.post("/sessions")
def create_session(req: CreateSessionRequest, db: Session = Depends(get_db)):
    s = models.ChatSession(
        title=req.title,
        user_id=req.user_id,
        provider=req.provider,
        model=req.model,
        include_context=req.include_context,
        top_k=req.top_k,
    )
    db.add(s)
    db.commit()
    db.refresh(s)
    return s.to_dict()


@router.get("/sessions")
def list_sessions(db: Session = Depends(get_db)):
    sessions = db.query(models.ChatSession).filter(models.ChatSession.is_active).all()
    return [s.to_dict(include_messages=False) for s in sessions]


@router.get("/sessions/{session_id}")
def get_session(session_id: int, db: Session = Depends(get_db)):
    s = db.query(models.ChatSession).filter(models.ChatSession.id == session_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    return s.to_dict()


@router.post("/sessions/{session_id}/messages")
def add_message(session_id: int, req: CreateMessageRequest, db: Session = Depends(get_db)):
    s = db.query(models.ChatSession).filter(models.ChatSession.id == session_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")

    # compute next message index
    last_index = db.query(models.ChatMessage).filter(models.ChatMessage.session_id == session_id).order_by(models.ChatMessage.message_index.desc()).first()
    next_index = (last_index.message_index + 1) if last_index else 0

    m = models.ChatMessage(
        session_id=session_id,
        role=req.role,
        content=req.content,
        message_index=next_index,
    )
    db.add(m)
    db.commit()
    db.refresh(m)
    return m.to_dict()


@router.delete("/sessions/{session_id}")
def delete_session(session_id: int, db: Session = Depends(get_db)):
    s = db.query(models.ChatSession).filter(models.ChatSession.id == session_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    s.is_active = False
    db.commit()
    return {"ok": True}


@router.patch("/sessions/{session_id}")
def update_session(session_id: int, req: UpdateSessionRequest, db: Session = Depends(get_db)):
    s = db.query(models.ChatSession).filter(models.ChatSession.id == session_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    if req.title is not None:
        s.title = req.title
    if req.provider is not None:
        s.provider = req.provider
    if req.model is not None:
        s.model = req.model
    if req.include_context is not None:
        s.include_context = req.include_context
    if req.top_k is not None:
        s.top_k = req.top_k
    db.commit()
    db.refresh(s)
    return s.to_dict()


@router.post("/sessions/{session_id}/game-chat")
async def generate_game_chat(
    session_id: int,
    game_session_id: int,
    db: Session = Depends(get_db)
):
    """Generate a DM response for game session chat.
    
    This endpoint processes player messages through the AI DM system,
    integrating dice rolling, combat, narrative, and NPC dialogue.
    
    Args:
        session_id: Chat session ID for conversation history
        game_session_id: Game session ID for game state
    
    Returns:
        DM response with game state updates
    """
    # Verify chat session exists
    chat_session = db.query(models.ChatSession).filter(
        models.ChatSession.id == session_id
    ).first()
    if not chat_session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    # Verify game session exists
    game_session = db.query(models.GameSession).filter(
        models.GameSession.id == game_session_id
    ).first()
    if not game_session:
        raise HTTPException(status_code=404, detail="Game session not found")
    
    # Get last user message from chat session
    last_msg = db.query(models.ChatMessage).filter(
        models.ChatMessage.session_id == session_id,
        models.ChatMessage.role == 'user',
        models.ChatMessage.is_deleted.is_(False)
    ).order_by(models.ChatMessage.message_index.desc()).first()
    
    if not last_msg:
        raise HTTPException(status_code=400, detail="No user message found in session")
    
    # Initialize DM chat handler with LM Studio configuration
    lm_studio_url = chat_session.provider if chat_session.provider and 'http' in chat_session.provider else "http://100.120.44.114:1234/v1"
    model = chat_session.model or "local-model"
    
    dm_handler = DMChatHandler(
        db=db,
        lm_studio_url=lm_studio_url,
        model=model
    )
    
    # Process game message through DM handler
    try:
        dm_response = await dm_handler.process_game_message(
            game_session=game_session,
            user_message=last_msg.content
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DM processing failed: {e}")
    
    # Create assistant message with DM response
    last_index = db.query(models.ChatMessage).filter(
        models.ChatMessage.session_id == session_id
    ).order_by(models.ChatMessage.message_index.desc()).first()
    next_index = (last_index.message_index + 1) if last_index else 0
    
    assistant_msg = models.ChatMessage(
        session_id=session_id,
        role='assistant',
        content=dm_response.message,
        message_index=next_index,
        meta={
            'game_session_id': game_session_id,
            'game_state_changed': dm_response.game_state_changed,
            'scene_changed': dm_response.scene_changed,
            'combat_started': dm_response.combat_started,
            'combat_ended': dm_response.combat_ended,
            'events': dm_response.events
        }
    )
    db.add(assistant_msg)
    
    # Log events to game session
    for event in dm_response.events:
        game_event = models.GameEvent(
            session_id=game_session_id,
            event_type=event.get('type', 'unknown'),
            event_data=event
        )
        db.add(game_event)
    
    db.commit()
    db.refresh(assistant_msg)
    db.refresh(game_session)
    
    return {
        "assistant_message": assistant_msg.to_dict(),
        "game_state": game_session.game_state,
        "dm_response": {
            "game_state_changed": dm_response.game_state_changed,
            "scene_changed": dm_response.scene_changed,
            "combat_started": dm_response.combat_started,
            "combat_ended": dm_response.combat_ended,
            "events": dm_response.events
        }
    }


@router.post("/sessions/{session_id}/generate")
async def generate_for_session(session_id: int, db: Session = Depends(get_db)):
    """Generate an assistant response for the session.

    This composes the conversation, optionally retrieves context (monsters),
    calls the LLM helper and persists the assistant message.
    """
    s = db.query(models.ChatSession).filter(models.ChatSession.id == session_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")

    # load messages ordered by index and filter out deleted messages
    msgs = db.query(models.ChatMessage).filter(
        models.ChatMessage.session_id == session_id,
        models.ChatMessage.is_deleted.is_(False),
    ).order_by(models.ChatMessage.message_index).all()

    # Build full conversation text for persistence/logging
    conversation = "\n".join([f"{m.role.upper()}: {m.content}" for m in msgs])

    # Use only the last N messages for retrieval to keep queries focused
    N = 3
    last_msgs = msgs[-N:] if len(msgs) > N else msgs
    retrieval_query = "\n".join([m.content for m in last_msgs])

    docs = []
    retrievals_for_meta = []
    if s.include_context and retrieval_query.strip():
        # Retrieve from both monsters AND references
        monster_docs = []
        reference_docs = []
        
        try:
            # Search monsters
            res = search_monsters(q=retrieval_query, k=s.top_k or 5)
            monster_docs = res.get('results') if isinstance(res, dict) else []
            print(f"[DEBUG] Monster search returned {len(monster_docs)} results")
        except Exception as e:
            print(f"[DEBUG] Monster search failed: {e}")
            monster_docs = []
        
        try:
            # Analyze query to extract structured search parameters
            query_params = analyze_query(retrieval_query)
            search_summary = get_search_summary(query_params)
            print(f"[DEBUG] Query analysis: {search_summary}")
            print(f"[DEBUG] Extracted params: {query_params}")
            
            # Search references with extracted filters
            reference_docs = do_reference_search(
                q=retrieval_query,
                ref_type=query_params.get('ref_type'),
                k=s.top_k or 5,
                db=db,
                level=query_params.get('level'),
                rarity=query_params.get('rarity'),
                school=query_params.get('school'),
                category=query_params.get('category'),
                tags=query_params.get('tags')
            )
            print(f"[DEBUG] Reference search returned {len(reference_docs)} results")
        except Exception as e:
            print(f"[DEBUG] Reference search failed: {e}")
            reference_docs = []
        
        # Merge results - interleave by taking half from each source for better diversity
        # This ensures we get both monsters AND references in the top results
        half_k = (s.top_k or 5) // 2
        docs = monster_docs[:half_k] + reference_docs[:half_k]
        
        # If one source has fewer results, fill remaining slots with the other
        remaining_slots = (s.top_k or 5) - len(docs)
        if remaining_slots > 0:
            docs.extend(monster_docs[half_k:half_k + remaining_slots])
        remaining_slots = (s.top_k or 5) - len(docs)
        if remaining_slots > 0:
            docs.extend(reference_docs[half_k:half_k + remaining_slots])

        # Normalize retrievals for storing in message meta and returning in the generation metadata
        for d in (docs or []):
            retrieval = {
                'id': d.get('id') or d.get('slug') or d.get('name'),
                'name': d.get('name') or d.get('title') or None,
                'summary': d.get('summary') or d.get('description') or (d.get('content') or '')[:200] + '...' if d.get('content') else None,
                'source_url': d.get('url') or d.get('source_url') or None,
                'type': 'monster' if d.get('cr') else 'reference',  # distinguish type for UI display
                'ref_type': d.get('ref_type') if d.get('ref_type') else None,
            }
            retrievals_for_meta.append(retrieval)

    context = "\n\n".join([
        (f"DOC {i+1}: {d.get('name') or d.get('title')}\n{d.get('summary') or d.get('description') or (d.get('content') or '')[:500]}")
        for i, d in enumerate(docs or [])
    ])

    # Check if this session has an active campaign
    campaign_context = ""
    try:
        from backend.models import Campaign
        campaign = db.query(Campaign).filter(Campaign.chat_session_id == session_id).first()
        if campaign:
            # Extract template metadata from campaign description
            import re
            import json
            metadata_match = re.search(r'\[AI_DM_METADATA: ({.*?})\]', campaign.description or '')
            metadata = json.loads(metadata_match.group(1)) if metadata_match else {}
            
            campaign_context = f"""
**ACTIVE CAMPAIGN: {campaign.title}**
- Type: {campaign.campaign_type}
- Setting: {campaign.setting}
- Difficulty: {campaign.difficulty}
- Current Level: {campaign.current_level}
- Adventure Template: {metadata.get('template_id', 'custom')}
- Opening Scene: {metadata.get('opening_scene', 'standard')}
- Campaign Tone: {metadata.get('campaign_tone', 'heroic_fantasy')}

You are the Dungeon Master for this campaign. Maintain consistency with the campaign details above, use the specified tone, and reference the adventure template from your knowledge base when appropriate.

"""
    except Exception as e:
        print(f"[DEBUG] Could not load campaign context: {e}")

    # Build character context from active characters in recent messages
    character_context = ""
    try:
        # Get active character IDs from last few user messages
        recent_user_msgs = db.query(models.ChatMessage).filter(
            models.ChatMessage.session_id == session_id,
            models.ChatMessage.role == 'user',
            models.ChatMessage.is_deleted.is_(False)
        ).order_by(models.ChatMessage.message_index.desc()).limit(3).all()
        
        active_char_ids = set()
        for msg in recent_user_msgs:
            if msg.meta and 'active_character_ids' in msg.meta:
                active_char_ids.update(msg.meta['active_character_ids'])
        
        if active_char_ids:
            # Load full character details
            characters = db.query(models.Character).filter(
                models.Character.id.in_(active_char_ids)
            ).all()
            
            if characters:
                character_context = "\n**ACTIVE PLAYER CHARACTERS:**\n"
                for char in characters:
                    character_context += f"\n{char.name}"
                    if char.dnd_class:
                        character_context += f" (Level {char.dnd_level or 1} {char.dnd_class}"
                        if char.dnd_species:
                            character_context += f" {char.dnd_species}"
                        character_context += ")"
                    
                    # Add personality and background details from structured_data
                    if char.structured_data:
                        sd = char.structured_data
                        if sd.get('personality_traits'):
                            character_context += f"\n  Personality: {', '.join(sd['personality_traits']) if isinstance(sd['personality_traits'], list) else sd['personality_traits']}"
                        if sd.get('ideals'):
                            character_context += f"\n  Ideals: {sd['ideals']}"
                        if sd.get('bonds'):
                            character_context += f"\n  Bonds: {sd['bonds']}"
                        if sd.get('flaws'):
                            character_context += f"\n  Flaws: {sd['flaws']}"
                    
                    # Add legacy fields if structured_data not available
                    if char.personality and not char.structured_data:
                        character_context += f"\n  Personality: {char.personality[:200]}"
                    if char.background and not char.structured_data:
                        character_context += f"\n  Background: {char.background[:200]}"
                    
                    character_context += "\n"
                
                character_context += "\nAs DM, you should reference these character details when appropriate to create a more immersive, personalized experience. Mention their ideals when moral choices arise, their bonds when relationships are relevant, and their flaws to create interesting roleplay moments.\n"
    except Exception as e:
        print(f"[DEBUG] Could not load character context: {e}")

    system_prompt = """You are an expert Dungeon Master for Dungeons & Dragons 5th Edition. 

Your responsibilities:
- Narrate vivid, immersive scenes with rich descriptions
- Roleplay NPCs with distinct personalities and voices
- Apply D&D 5e rules accurately and fairly
- Ask for dice rolls when appropriate (attacks, saves, checks)
- Track combat, initiative, HP, and conditions
- Create engaging encounters and meaningful choices
- Adapt to player actions and maintain story flow
- Reference the Player's Handbook and other source material

When describing scenes, use evocative language. When voicing NPCs, give them personality. When combat begins, be clear about initiative, positioning, and options.

"""

    prompt = f"{system_prompt}{campaign_context}{character_context}Use the following documents as context:\n\n{context}\n\nConversation:\n{conversation}\n\nAssistant:"

    # Call the centralized LLM helper
    try:
        content, metadata = await call_llm(prompt, s.provider or 'groq', s.model or None)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM call failed: {e}")

    # persist assistant message and include retrieval provenance in message meta
    last_index = db.query(models.ChatMessage).filter(models.ChatMessage.session_id == session_id).order_by(models.ChatMessage.message_index.desc()).first()
    next_index = (last_index.message_index + 1) if last_index else 0
    m = models.ChatMessage(
        session_id=session_id,
        role='assistant',
        content=content,
        message_index=next_index,
        meta={
            'retrievals': retrievals_for_meta,
            'retrieval_query': retrieval_query,
        } if retrievals_for_meta else None,
    )
    db.add(m)
    db.commit()
    db.refresh(m)

    return {"assistant_message": m.to_dict(), "generation": metadata}


@router.post("/sessions/{session_id}/messages/{message_id}/tts")
async def generate_tts_for_message(
    session_id: int,
    message_id: int,
    voice: str = "tara",
    flavor_text_only: bool = False,
    db: Session = Depends(get_db)
):
    """Generate text-to-speech audio for a chat message using Kitten TTS.
    
    Returns WAV audio file (16-bit PCM, 24kHz, mono).
    
    Args:
        session_id: Chat session ID
        message_id: Message ID to convert to speech
        voice: Voice to use (tara, leah, jess, leo, dan, mia, zac, zoe)
        flavor_text_only: If True, narrate only flavor/narrative text (skip mechanics)
    
    Returns:
        StreamingResponse: WAV audio file
    """
    # Verify session exists
    session = db.query(models.ChatSession).filter(
        models.ChatSession.id == session_id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get message
    message = db.query(models.ChatMessage).filter(
        models.ChatMessage.id == message_id,
        models.ChatMessage.session_id == session_id
    ).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    # Only generate TTS for assistant messages
    if message.role != 'assistant':
        raise HTTPException(
            status_code=400, 
            detail="TTS only available for assistant messages"
        )
    
    try:
        # Import TTS service (lazy load)
        from ..tts_service import get_tts_service
        
        tts = get_tts_service()
        
        # Generate speech audio
        audio_data = tts.generate_speech(
            text=message.content,
            voice=voice,
            add_dm_personality=True,
            flavor_text_only=flavor_text_only
        )
        
        # Return as streaming audio
        return StreamingResponse(
            iter([audio_data]),
            media_type="audio/wav",
            headers={
                "Content-Disposition": f"inline; filename=message_{message_id}.wav"
            }
        )
        
    except ImportError:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail="TTS service not available. Install kittentts: pip install https://github.com/KittenML/KittenTTS/releases/download/0.1/kittentts-0.1.0-py3-none-any.whl && pip install soundfile"
        )
    except Exception as e:
        import traceback
        print(f"[ERROR] TTS generation failed for message {message_id}: {e}")
        print(f"[ERROR] Message content: {message.content[:100]}...")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"TTS generation failed: {str(e)}"
        )


@router.post("/sessions/{session_id}/messages/{message_id}/scene-image")
async def generate_scene_image_for_message(
    session_id: int,
    message_id: int,
    force_generate: bool = False,
    location_hint: str | None = None,
    db: Session = Depends(get_db)
):
    """Generate a scene image for a chat message using Stable Diffusion.
    
    Analyzes the DM response and generates a contextual fantasy scene image.
    
    Args:
        session_id: Chat session ID
        message_id: Message ID to generate scene for
        force_generate: Force generation even if content seems unsuitable
        location_hint: Optional location type hint (e.g., "tavern", "dungeon")
    
    Returns:
        Dict with base64 image and prompt info
    """
    # Verify session exists
    session = db.query(models.ChatSession).filter(
        models.ChatSession.id == session_id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get message
    message = db.query(models.ChatMessage).filter(
        models.ChatMessage.id == message_id,
        models.ChatMessage.session_id == session_id
    ).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    # Only generate images for assistant messages
    if message.role != 'assistant':
        raise HTTPException(
            status_code=400, 
            detail="Scene images only available for DM responses"
        )
    
    try:
        from ..scene_image_utils import (
            extract_scene_prompt,
            build_scene_negative_prompt,
            enhance_prompt_for_location,
            should_generate_scene_image
        )
        from ..stablediffusion_client import StableDiffusionClient
        
        # Check if scene is worth generating
        if not force_generate and not should_generate_scene_image(message.content):
            raise HTTPException(
                status_code=400,
                detail="Message does not contain suitable scene description for image generation"
            )
        
        # Extract visual prompt from DM response
        base_prompt = extract_scene_prompt(message.content)
        if not base_prompt:
            raise HTTPException(
                status_code=400,
                detail="Could not extract visual description from message"
            )
        
        # Enhance with location hint if provided
        if location_hint:
            base_prompt = enhance_prompt_for_location(base_prompt, location_hint)
        
        # Build negative prompt
        negative_prompt = build_scene_negative_prompt()
        
        # Generate image using SD
        sd_client = StableDiffusionClient()
        result = sd_client.generate_image(
            prompt=base_prompt,
            negative_prompt=negative_prompt,
            steps=30,
            width=768,
            height=512,
            cfg_scale=7.5
        )
        
        # Check for image in response (supports both 'image' and 'image_base64' keys)
        image_data = result.get('image') or result.get('image_base64')
        if not image_data:
            raise HTTPException(
                status_code=500,
                detail="Stable Diffusion did not return an image"
            )
        
        return {
            "image": image_data,
            "prompt": base_prompt,
            "negative_prompt": negative_prompt,
            "generation_info": result.get('info', {}),
            "message_id": message_id,
            "session_id": session_id
        }
        
    except ImportError as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Scene image generation dependencies not available: {str(e)}"
        )
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        import traceback
        print(f"[ERROR] Scene image generation failed for message {message_id}: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Scene image generation failed: {str(e)}"
        )
