from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from datetime import datetime

from sqlalchemy.orm import Session
from ..database import get_db
from .. import models
from .monsters import search_monsters
from .references import do_reference_search
from .generation import call_llm
from ..events import event_stream, publish_event
from ..query_analyzer import analyze_query, get_search_summary
from ..game.dm_chat_handler import DMChatHandler
from ..journal_auto_logger import extract_journal_entries_from_message
import logging

logger = logging.getLogger(__name__)

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
    
    # Load DM roll setting from user settings
    dm_roll_for_players = False
    try:
        settings = db.query(models.UserSettings).first()
        if settings:
            dm_roll_for_players = settings.dm_roll_for_players or False
    except Exception as e:
        print(f"[Game Chat] Could not load dm_roll_for_players setting: {e}")
    
    dm_handler = DMChatHandler(
        db=db,
        provider=lm_studio_url,
        model=model,
        dm_roll_for_players=dm_roll_for_players
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
    
    # Auto-log journal entries from DM response (non-blocking)
    if game_session.campaign_id:
        try:
            import asyncio
            # Run auto-logging in background (don't await to avoid blocking response)
            asyncio.create_task(
                extract_journal_entries_from_message(
                    db=db,
                    message=assistant_msg,
                    campaign_id=game_session.campaign_id
                )
            )
        except Exception as e:
            # Log error but don't fail the request
            print(f"[Auto-Journal] Failed to extract entries: {e}")

    # --- Scene summarization and asynchronous image generation ---
    # Run the same scene summarizer used by the session generation flow so
    # the assistant message gets a Stable Diffusion-friendly prompt and
    # descriptor list persisted. Then schedule background SD generation.
    try:
        scene_descriptors = None
        scene_prompt = None
        try:
            from .generation import SceneSummarizeRequest, summarize_scene_for_image

            print("[Game Chat] Invoking scene summarizer for assistant message")
            summ_req = SceneSummarizeRequest(text=assistant_msg.content or "", provider="groq", model="llama-3.3-70b-versatile")
            summ_res = await summarize_scene_for_image(summ_req)
            scene_descriptors = summ_res.get("descriptors")
            scene_prompt = summ_res.get("prompt")
            print("[Game Chat] Scene summarizer returned prompt/descriptors")
        except Exception as se:
            print(f"[Game Chat] Scene summarizer failed: {se}")
            scene_descriptors = None
            scene_prompt = None

        # Persist summarizer output into the assistant message meta and schedule background image generation
        if scene_prompt or scene_descriptors:
            if assistant_msg.meta is None:
                assistant_msg.meta = {}
            assistant_msg.meta.setdefault('scene_image', {})
            assistant_msg.meta['scene_image'].update({
                'prompt': scene_prompt,
                'descriptors': scene_descriptors,
                'generated_at': datetime.utcnow().isoformat()
            })
            db.add(assistant_msg)
            db.commit()
            db.refresh(assistant_msg)

            # Schedule background SD generation (non-blocking)
            try:
                import asyncio
                from ..database import SessionLocal

                async def _generate_and_cache_image_game(msg_id: int, prompt_text: str, descriptors_text: str | None):
                    print(f"[Background Scene Image - game_chat] ========== TASK STARTED for message {msg_id} ==========")
                    try:
                        print(f"[Background Scene Image - game_chat] Starting generation for message {msg_id}")
                        from ..image_generation import generate_location_image

                        print(f"[Background Scene Image - game_chat] Calling generate_location_image with prompt: {prompt_text[:100] if prompt_text else 'NO PROMPT'}...")
                        gen = await generate_location_image(
                            prompt=prompt_text or (descriptors_text or ""),
                            provider="stablediffusion",
                            model=None,
                            aspect_ratio="16:9",
                            style="fantasy",
                            use_llm=False,
                        )

                        print(f"[Background Scene Image - game_chat] Generation completed. Result keys: {list(gen.keys())}")
                        image_b64 = gen.get("image_base64") or gen.get("image")
                        
                        if not image_b64:
                            print(f"[Background Scene Image - game_chat] ERROR: No image data in result. Full result: {gen}")
                            return
                        
                        print(f"[Background Scene Image - game_chat] Image data extracted, length: {len(image_b64)} bytes")

                        db2 = SessionLocal()
                        try:
                            msg = db2.query(models.ChatMessage).filter(models.ChatMessage.id == msg_id).first()
                            if not msg:
                                print(f"[Background Scene Image - game_chat] ERROR: Message {msg_id} not found in database")
                                return
                            if not msg.meta:
                                msg.meta = {}
                            si = msg.meta.get("scene_image", {})
                            si.update({
                                "image": image_b64,
                                "cached": True,
                                "generated_at": datetime.utcnow().isoformat(),
                                "prompt": prompt_text,
                                "descriptors": descriptors_text,
                                "provider": gen.get("provider"),
                                "model": gen.get("model"),
                            })
                            msg.meta["scene_image"] = si
                            db2.add(msg)
                            db2.commit()
                            
                            print("[Background Scene Image - game_chat] Database commit successful")
                            
                            # Ensure the ORM object is refreshed so subsequent reads see the update
                            try:
                                db2.refresh(msg)
                                print("[Background Scene Image - game_chat] Message refreshed from database")
                            except Exception as refresh_error:
                                print(f"[Background Scene Image - game_chat] WARNING: Refresh failed: {refresh_error}")
                                
                            # Log debug information about the cached image
                            img_len = len(image_b64) if image_b64 else 0
                            print(f"[Background Scene Image - game_chat] SUCCESS: Cached image for message {msg.id}, bytes={img_len}")
                            
                            # Publish SSE event
                            print(f"[Background Scene Image - game_chat] Publishing SSE event for session {msg.session_id}, message {msg.id}")
                            try:
                                publish_event(msg.session_id, {
                                    "type": "message_metadata_updated",
                                    "message_id": msg.id,
                                    "metadata": {"scene_image": si}
                                })
                                print("[Background Scene Image - game_chat] SSE event published successfully")
                            except Exception as sse_error:
                                print(f"[Background Scene Image - game_chat] ERROR: Failed to publish SSE event: {sse_error}")
                        finally:
                            db2.close()
                            print("[Background Scene Image - game_chat] Database connection closed")
                    except Exception as e:
                        import traceback
                        print(f"[Background Scene Image - game_chat] FAILED: {e}")
                        print(f"[Background Scene Image - game_chat] Traceback: {traceback.format_exc()}")

                print(f"[Game Chat] *** CREATING BACKGROUND TASK for message {assistant_msg.id} with prompt: {(scene_prompt or '')[:50]}...")
                asyncio.create_task(_generate_and_cache_image_game(assistant_msg.id, scene_prompt or "", scene_descriptors))
                print("[Game Chat] *** Background task created successfully")
            except Exception as e:
                print(f"[Game Chat] Failed to schedule background image generation: {e}")
    except Exception as e:
        print(f"[Game Chat] Scene summarization flow error: {e}")
    
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
                    character_context += f"\n## {char.name}"
                    if char.dnd_class:
                        character_context += f" (Level {char.dnd_level or 1} {char.dnd_class}"
                        if char.dnd_species:
                            character_context += f" {char.dnd_species}"
                        if char.dnd_background:
                            character_context += f", {char.dnd_background} background"
                        character_context += ")"
                    
                    # Core Stats
                    if char.dnd_armor_class:
                        character_context += f"\n  AC: {char.dnd_armor_class}"
                    if char.dnd_hit_points_max or char.dnd_hit_points:
                        hp_max = char.dnd_hit_points_max or char.dnd_hit_points
                        hp_current = char.dnd_hit_points_current if char.dnd_hit_points_current is not None else hp_max
                        character_context += f", HP: {hp_current}/{hp_max}"
                    if char.dnd_speed:
                        character_context += f", Speed: {char.dnd_speed} ft"
                    if char.dnd_initiative:
                        character_context += f", Initiative: {char.dnd_initiative}"
                    
                    # Ability Scores and Modifiers
                    if char.dnd_ability_scores:
                        character_context += "\n  Abilities: "
                        ability_parts = []
                        for ability in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
                            score = char.dnd_ability_scores.get(ability)
                            if score:
                                modifier = char.dnd_ability_modifiers.get(ability, 0) if char.dnd_ability_modifiers else (score - 10) // 2
                                mod_str = f"+{modifier}" if modifier >= 0 else str(modifier)
                                ability_parts.append(f"{ability[:3].upper()} {score} ({mod_str})")
                        character_context += ", ".join(ability_parts)
                    
                    # Skills and Proficiencies
                    if char.dnd_skills:
                        character_context += f"\n  Skills: {', '.join(char.dnd_skills)}"
                    
                    if char.dnd_proficiencies:
                        prof = char.dnd_proficiencies
                        if prof.get('saves'):
                            character_context += f"\n  Saving Throws: {', '.join(prof['saves'])}"
                        if prof.get('weapons'):
                            character_context += f"\n  Weapon Proficiencies: {', '.join(prof['weapons'])}"
                        if prof.get('armor'):
                            character_context += f"\n  Armor Proficiencies: {', '.join(prof['armor'])}"
                    
                    # Equipment
                    if char.dnd_equipment:
                        eq = char.dnd_equipment
                        if eq.get('weapons'):
                            character_context += f"\n  Weapons: {', '.join([w.get('name', w) if isinstance(w, dict) else str(w) for w in eq['weapons']])}"
                        if eq.get('armor'):
                            armor_items = eq['armor'] if isinstance(eq['armor'], list) else [eq['armor']]
                            character_context += f"\n  Armor: {', '.join([a.get('name', a) if isinstance(a, dict) else str(a) for a in armor_items])}"
                    
                    # Spellcasting
                    if char.dnd_spellcasting:
                        sc = char.dnd_spellcasting
                        if sc.get('ability'):
                            character_context += f"\n  Spellcasting: {sc['ability']}-based"
                        if sc.get('dc'):
                            character_context += f", Spell Save DC {sc['dc']}"
                        if sc.get('attack'):
                            attack_bonus = sc['attack']
                            character_context += f", Spell Attack {'+' if attack_bonus >= 0 else ''}{attack_bonus}"
                        if sc.get('spells_known'):
                            character_context += f"\n  Spells Known: {', '.join(sc['spells_known'][:10])}"  # Show first 10 spells
                            if len(sc['spells_known']) > 10:
                                character_context += f" (+{len(sc['spells_known']) - 10} more)"
                    
                    # Features and Abilities
                    if char.dnd_features:
                        features = char.dnd_features
                        if features.get('class'):
                            class_features = features['class'][:5] if isinstance(features['class'], list) else [features['class']]
                            character_context += f"\n  Class Features: {', '.join([f.get('name', f) if isinstance(f, dict) else str(f) for f in class_features])}"
                        if features.get('racial'):
                            racial_features = features['racial'][:3] if isinstance(features['racial'], list) else [features['racial']]
                            character_context += f"\n  Racial Traits: {', '.join([f.get('name', f) if isinstance(f, dict) else str(f) for f in racial_features])}"
                    
                    # Languages
                    if char.dnd_languages:
                        character_context += f"\n  Languages: {', '.join(char.dnd_languages)}"
                    
                    # Personality and background details from structured_data
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
                
                character_context += "\n**DM INSTRUCTIONS FOR CHARACTER INTEGRATION:**\n"
                character_context += "- Reference character abilities and spells when suggesting actions\n"
                character_context += "- Mention their skills when relevant challenges arise\n"
                character_context += "- Use their equipment in descriptions (e.g., 'Your longsword gleams...')\n"
                character_context += "- Incorporate their personality traits, ideals, bonds, and flaws into roleplay moments\n"
                character_context += "- Suggest using class features when appropriate for the situation\n"
                character_context += "- Remember their languages when NPCs speak\n"
                character_context += "- Track their HP, conditions, and resources during combat\n"
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

**Action Formatting:** To help players respond quickly, format suggested actions using **bold text** for narrative choices (e.g., **Approach the stranger** – Ask about the quest) or markdown tables for skill checks:

| Action | Suggested Roll | DC |
|--------|----------------|-----|
| Perception to search the room | d20 + Perception | 12 |

These will automatically become clickable buttons for the player.

"""

    # Check if DM should roll for players during skill checks, saves, and combat
    # This setting influences whether the DM AI will proactively make rolls or ask players to roll
    dm_roll_instructions = ""
    try:
        settings = db.query(models.UserSettings).first()
        if settings and settings.dm_roll_for_players:
            dm_roll_instructions = """
**IMPORTANT - DM ROLLS FOR PLAYERS:** The table has enabled "DM Rolls for Players" mode. This means:
- When a character attempts a skill check, ability check, or saving throw, YOU should roll for them.
- Format the roll result in a clear, easy-to-read way: "**[Character Name]'s [Skill] Check**: Rolled 1d20+X = [RESULT] vs DC Y"
- Always roll for attack rolls in combat, ability checks, and saving throws.
- Still narrate the outcome naturally and dramatically.
- If they ask you to roll, do so. Don't ask them to roll - you handle it.

This enables faster, more streamlined gameplay where the DM takes action economy.
"""
    except Exception as e:
        print(f"[DM Settings] Could not load dm_roll_for_players setting: {e}")

    prompt = f"{system_prompt}{dm_roll_instructions}{campaign_context}{character_context}Use the following documents as context:\n\n{context}\n\nConversation:\n{conversation}\n\nAssistant:"

    # Call the centralized LLM helper
    try:
        # Use the heavy creative model by default for story generation (Groq endpoint model alias)
        default_story_model = s.model or "openai/gpt-oss-120b"
        content, metadata = await call_llm(prompt, s.provider or 'groq', default_story_model)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM call failed: {e}")

    # Server-side: run a second sub-prompt to summarize the DM narration into
    # a concise Stable Diffusion-friendly prompt and a comma-separated
    # descriptor list. Attach these to the message metadata so the UI and
    # scene-image endpoint can use them without an extra client round-trip.
    scene_descriptors = None
    scene_prompt = None
    try:
        import json
        import re

        # Use the centralized summarization endpoint helper to produce descriptors and prompt
        try:
            from .generation import SceneSummarizeRequest, summarize_scene_for_image

            logger.info("[Scene Summarizer] invoking summarize_scene_for_image helper")
            print("[Scene Summarizer] invoking summarize_scene_for_image helper")
            summ_req = SceneSummarizeRequest(text=content or "", provider="groq", model="llama-3.3-70b-versatile")
            summ_res = await summarize_scene_for_image(summ_req)
            scene_descriptors = summ_res.get("descriptors")
            scene_prompt = summ_res.get("prompt")
            logger.info("[Scene Summarizer] helper returned descriptors/prompt")
            print("[Scene Summarizer] helper returned descriptors/prompt")
        except Exception as se:
            logger.exception(f"[Scene Summarizer] helper failed: {se}")
            print(f"[Scene Summarizer] helper failed: {se}")
            scene_descriptors = None
            scene_prompt = None
    except Exception as e:
        # Don't fail the whole generation if summarization fails; log and continue
        print(f"[Scene Summarizer] failed: {e}")

    # persist assistant message and include retrieval provenance and any
    # scene summarizer output in message meta
    last_index = db.query(models.ChatMessage).filter(models.ChatMessage.session_id == session_id).order_by(models.ChatMessage.message_index.desc()).first()
    next_index = (last_index.message_index + 1) if last_index else 0

    meta_dict = None
    if retrievals_for_meta:
        meta_dict = {
            'retrievals': retrievals_for_meta,
            'retrieval_query': retrieval_query,
        }

    # Attach scene summarizer output if available
    if scene_prompt or scene_descriptors:
        if meta_dict is None:
            meta_dict = {}
        meta_dict['scene_image'] = {
            'prompt': scene_prompt,
            'descriptors': scene_descriptors,
            'generated_at': datetime.utcnow().isoformat()
        }

    m = models.ChatMessage(
        session_id=session_id,
        role='assistant',
        content=content,
        message_index=next_index,
        meta=meta_dict,
    )
    db.add(m)
    db.commit()
    db.refresh(m)

    # After persisting the assistant message, dispatch an async background
    # task to send the summarizer prompt to Stable Diffusion and cache the
    # generated image into the message metadata. We create the task after
    # commit so the background worker can open its own DB session and update
    # the persisted message safely.
    try:
        import asyncio
        from ..database import SessionLocal

        async def _generate_and_cache_image(msg_id: int, prompt_text: str, descriptors_text: str | None):
            try:
                print(f"[Background Scene Image] Starting generation for message {msg_id}")
                # Use the image generation helper which is async
                from ..image_generation import generate_location_image

                # Call SD with the concise prompt we obtained from the summarizer.
                # We prefer location image helper for scene prompts.
                print(f"[Background Scene Image] Calling generate_location_image with prompt: {prompt_text[:100]}...")
                gen = await generate_location_image(
                    prompt=prompt_text or (descriptors_text or ""),
                    provider="stablediffusion",
                    model=None,
                    aspect_ratio="16:9",
                    style="fantasy",
                    use_llm=False,
                )

                print(f"[Background Scene Image] Generation completed. Result keys: {list(gen.keys())}")
                print("[Background Scene Image] Generation completed, extracting image data...")
                image_b64 = gen.get("image_base64") or gen.get("image")
                
                if not image_b64:
                    print(f"[Background Scene Image] ERROR: No image data in generation result. Full result: {gen}")
                    return

                print(f"[Background Scene Image] Image data extracted, length: {len(image_b64)} bytes")

                # Open a fresh DB session to update the message meta
                db2 = SessionLocal()
                try:
                    msg = db2.query(models.ChatMessage).filter(models.ChatMessage.id == msg_id).first()
                    if not msg:
                        return
                    if not msg.meta:
                        msg.meta = {}
                    si = msg.meta.get("scene_image", {})
                    si.update({
                        "image": image_b64,
                        "cached": True,
                        "generated_at": datetime.utcnow().isoformat(),
                        "prompt": prompt_text,
                        "descriptors": descriptors_text,
                        "provider": gen.get("provider"),
                        "model": gen.get("model"),
                    })
                    msg.meta["scene_image"] = si
                    db2.add(msg)
                    db2.commit()
                    
                    # Log the update
                    img_len = len(image_b64) if image_b64 else 0
                    print(f"[Background Scene Image] SUCCESS: Cached image in message {msg_id} metadata, bytes={img_len}")
                    
                    # Publish an event so connected clients can pick up updated metadata
                    try:
                        print(f"[Background Scene Image] Publishing SSE event for session {msg.session_id}, message {msg.id}")
                        publish_event(msg.session_id, {
                            "type": "message_metadata_updated",
                            "message_id": msg.id,
                            "metadata": {"scene_image": si}
                        })
                        print("[Background Scene Image] SSE event published successfully")
                    except Exception as e:
                        # Non-fatal if publish fails
                        print(f"[Background Scene Image] ERROR: Failed to publish SSE event: {e}")
                        pass
                finally:
                    db2.close()
            except Exception as e:
                import traceback
                print(f"[Background Scene Image] FAILED: {e}")
                print(f"[Background Scene Image] Traceback: {traceback.format_exc()}")

        # Only schedule background generation if we have a prompt
        if scene_prompt or scene_descriptors:
            # schedule but don't await
            asyncio.create_task(_generate_and_cache_image(m.id, scene_prompt or "", scene_descriptors))
    except Exception as e:
        print(f"[Scene Image Dispatch] failed to schedule background task: {e}")

    return {"assistant_message": m.to_dict(), "generation": metadata}


@router.get("/sessions/{session_id}/events")
async def session_events(session_id: int):
    """Server-Sent Events endpoint for session-scoped updates.

    Clients can connect with EventSource to receive JSON events when
    message metadata (like scene_image) is updated.
    """
    # Use the async generator from backend.events
    return StreamingResponse(event_stream(session_id), media_type="text/event-stream")


@router.post("/sessions/{session_id}/messages/{message_id}/tts")
async def generate_tts_for_message(
    session_id: int,
    message_id: int,
    voice: str = "alloy",  # Default to OpenAI-compatible voice
    flavor_text_only: bool = False,
    db: Session = Depends(get_db)
):
    """Generate text-to-speech audio for a chat message.
    
    Returns WAV audio file (16-bit PCM, 24kHz, mono).
    
    Args:
        session_id: Chat session ID
        message_id: Message ID to convert to speech
        voice: Voice to use (OpenAI: alloy/echo/fable/onyx/nova/shimmer, KittenTTS: tara/leah/jess/leo/dan/mia/zac/zoe)
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
        # Get user settings to determine TTS provider
        settings = db.query(models.UserSettings).first()
        
        # No defaults - if no settings, TTS is not configured
        if not settings or not settings.tts_provider:
            raise HTTPException(
                status_code=400,
                detail="TTS provider not configured. Please set your TTS preferences in settings."
            )
        
        tts_provider = settings.tts_provider
        tts_model = settings.tts_model if settings.tts_model else "standard"
        tts_speed = settings.tts_speed if settings.tts_speed else 1.0
        
        # Map voice based on provider (handle KittenTTS voices being sent to OpenAI)
        if tts_provider == "openai":
            # If a KittenTTS voice was provided, use the saved voice from settings or default to alloy
            kitten_voices = ["tara", "leah", "jess", "leo", "dan", "mia", "zac", "zoe"]
            if voice in kitten_voices:
                # Use the voice saved in settings (should be OpenAI voice) or default
                voice = settings.tts_voice if settings.tts_voice else "alloy"
                print(f"[TTS] Mapped KittenTTS voice to OpenAI voice: {voice}")
        
        print(f"[TTS] Using provider: {tts_provider}, voice: {voice}, model: {tts_model}, speed: {tts_speed}")
        
        # Route to appropriate TTS service based on provider - NO FALLBACKS
        if tts_provider == "openai":
            # Use OpenAI TTS service
            from ..openai_tts_service import get_openai_tts_service
            
            tts = get_openai_tts_service(
                voice=voice,
                model=tts_model,
                audio_format="wav"  # Frontend expects WAV
            )
            
            # Generate speech audio with OpenAI
            audio_data = tts.generate_speech(
                text=message.content,
                voice=voice,
                model=tts_model,
                speed=tts_speed,
                output_format="wav"
            )
            
            print(f"[TTS] Generated {len(audio_data)} bytes with OpenAI TTS")
        
        elif tts_provider == "kitten":
            # Use KittenTTS service
            from ..tts_service import get_tts_service
            
            tts = get_tts_service()
            
            # Generate speech audio with KittenTTS
            audio_data = tts.generate_speech(
                text=message.content,
                voice=voice,
                add_dm_personality=True,
                flavor_text_only=flavor_text_only
            )
            
            print(f"[TTS] Generated {len(audio_data)} bytes with KittenTTS")
        
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported TTS provider: {tts_provider}. Supported providers: 'openai', 'kitten'"
            )
        
        # Store TTS metadata in message (not the audio itself, which is too large)
        # This helps frontend know TTS was previously generated
        if message.meta is None:
            message.meta = {}
        
        if 'tts_history' not in message.meta:
            message.meta['tts_history'] = []
        
        message.meta['tts_history'].append({
            "voice": voice,
            "provider": tts_provider,
            "model": tts_model,
            "flavor_text_only": flavor_text_only,
            "generated_at": datetime.utcnow().isoformat(),
            "audio_size_bytes": len(audio_data)
        })
        db.commit()
        print(f"[TTS] Saved generation metadata to message {message_id}")
        
        # Return as streaming audio
        return StreamingResponse(
            iter([audio_data]),
            media_type="audio/wav",
            headers={
                "Content-Disposition": f"inline; filename=message_{message_id}.wav"
            }
        )
        
    except ImportError as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"TTS service not available: {str(e)}. Install required packages."
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
    
    # Check for cached scene image in message metadata (unless force_generate)
    if not force_generate and message.meta and 'scene_image' in message.meta:
        cached_data = message.meta['scene_image']
        print(f"[Scene Image] Returning cached image for message {message_id}")
        return {
            "image": cached_data.get('image'),
            "prompt": cached_data.get('prompt'),
            "negative_prompt": cached_data.get('negative_prompt'),
            "generation_info": {},
            "message_id": message_id,
            "session_id": session_id,
            "cached": True,  # Indicate this is from cache
            "generated_at": cached_data.get('generated_at')
        }
    
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
        
        # Cache the scene image in message metadata for persistence
        if message.meta is None:
            message.meta = {}

        message.meta['scene_image'] = {
            "image": image_data,
            "prompt": base_prompt,
            "negative_prompt": negative_prompt,
            "generated_at": datetime.utcnow().isoformat(),
            "force_generate": force_generate,
            "location_hint": location_hint
        }
        db.add(message)
        db.commit()
        # Refresh the ORM object so callers see the updated meta immediately
        try:
            db.refresh(message)
        except Exception:
            pass
        # Debug logging
        try:
            img_len = len(image_data) if image_data else 0
            print(f"[Scene Image] Cached image in message {message_id} metadata, bytes={img_len}")
        except Exception:
            pass
        try:
            publish_event(message.session_id, {
                "type": "message_metadata_updated",
                "message_id": message.id,
                "metadata": {"scene_image": message.meta['scene_image']}
            })
        except Exception:
            pass
        
        return {
            "image": image_data,
            "prompt": base_prompt,
            "negative_prompt": negative_prompt,
            "generation_info": result.get('info', {}),
            "message_id": message_id,
            "session_id": session_id,
            "cached": False  # Freshly generated
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


# ============================================================================
# DIALOGUE TTS ENDPOINT - For sequential dialogue narration
# ============================================================================

class DialogueTTSRequest(BaseModel):
    text: str
    voice: str = "leah"  # Default female voice


@router.post("/tts/dialogue")
async def generate_dialogue_tts(
    request: DialogueTTSRequest,
    db: Session = Depends(get_db)
):
    """Generate TTS for a single dialogue snippet.
    
    Simplified endpoint for dialogue narration - no message association needed.
    Always uses KittenTTS for consistent voice quality across dialogue.
    
    Args:
        text: Dialogue text to narrate
        voice: KittenTTS voice (tara, leah, jess, mia, leo, dan, zac, zoe)
    
    Returns:
        StreamingResponse: WAV audio file
    """
    try:
        from ..tts_service import get_tts_service
        
        tts = get_tts_service()
        
        # Generate speech audio with KittenTTS
        # Use the chunking strategy to handle any length dialogue
        audio_data = tts.generate_speech(
            text=request.text,
            voice=request.voice,
            add_dm_personality=False,  # Dialogue is already in character
            flavor_text_only=False  # Use full text as provided
        )
        
        print(f"[Dialogue TTS] Generated {len(audio_data)} bytes for voice '{request.voice}'")
        
        # Return as streaming audio
        return StreamingResponse(
            iter([audio_data]),
            media_type="audio/wav",
            headers={
                "Content-Disposition": f"inline; filename=dialogue_{request.voice}.wav"
            }
        )
        
    except ImportError as e:
        raise HTTPException(
            status_code=500,
            detail=f"TTS service not available: {str(e)}"
        )
    except Exception as e:
        import traceback
        print(f"[ERROR] Dialogue TTS generation failed: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Dialogue TTS generation failed: {str(e)}"
        )
