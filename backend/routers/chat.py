from fastapi import APIRouter, Depends, HTTPException
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

    prompt = f"Use the following documents as context and answer the user's last message as the assistant.\n\n{context}\n\nConversation:\n{conversation}\n\nAssistant:"

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
