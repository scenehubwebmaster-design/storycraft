"""
Auto-logging system for extracting journal entries from DM messages.

Uses LLM to analyze DM responses and extract:
- NPCs introduced
- Locations visited
- Quest updates
- Important decisions
- Combat encounters
- Loot acquired
"""

import json
import logging
import os
from typing import List, Dict, Optional
from sqlalchemy.orm import Session

from .models import JournalEntry, NPC, Quest, Campaign, GameSession, ChatMessage

logger = logging.getLogger(__name__)

# Import Groq client if available
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    Groq = None
    GROQ_AVAILABLE = False
    logger.warning("Groq client not available - auto-journal will be disabled")


async def extract_journal_entries_from_message(
    db: Session,
    message: ChatMessage,
    campaign_id: int
) -> List[JournalEntry]:
    """
    Analyze a DM message and extract journal-worthy events.
    
    Returns list of created JournalEntry objects.
    """
    if not message.content or message.role != "assistant":
        return []
    
    # Get campaign context
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign or not campaign.game_session_id:
        return []
    
    game_session = db.query(GameSession).filter(GameSession.id == campaign.game_session_id).first()
    if not game_session:
        return []
    
    logger.info(f"[Auto-Journal] Analyzing message {message.id} for journal entries...")
    
    # Build extraction prompt
    extraction_prompt = f"""You are a D&D campaign journal assistant. Analyze the following DM message and extract key events that should be logged in the campaign journal.

**DM Message:**
{message.content}

**Current Campaign Context:**
- Campaign: {campaign.name}
- Scene Type: {campaign.scene_type or 'unknown'}
- Party Level: {campaign.party_level}

**Extract the following types of events:**
1. **NPCs Met**: New characters introduced (name, description, role)
2. **Locations Visited**: New places the party enters or discovers
3. **Quest Updates**: Quest accepted, progressed, or completed
4. **Decisions**: Important choices made by the party
5. **Combat**: Combat encounters started or resolved
6. **Loot**: Significant items obtained

**Return JSON array with this exact structure:**
```json
[
  {{
    "type": "npc_met|location_visited|quest_update|decision|combat|loot",
    "title": "Short title (e.g., 'Met Elara the Merchant')",
    "description": "Detailed description of the event",
    "importance": 1-5 (1=minor, 5=critical to story),
    "tags": ["tag1", "tag2"],
    "metadata": {{
      "npc_name": "string (for npc_met)",
      "npc_description": "string (for npc_met)",
      "npc_role": "string (for npc_met)",
      "location_name": "string (for location_visited)",
      "quest_title": "string (for quest_update)",
      "quest_status": "accepted|in_progress|completed|failed (for quest_update)"
    }}
  }}
]
```

**Rules:**
- Only extract events that actually happened (not hypotheticals or descriptions)
- Be concise but informative
- Importance: 1=flavor text, 3=notable event, 5=critical plot point
- Return empty array [] if no journal-worthy events found
- Return ONLY valid JSON, no markdown formatting or explanations

**JSON Output:**"""

    try:
        # Check if Groq is available
        if not GROQ_AVAILABLE:
            logger.warning("[Auto-Journal] Groq client not available, skipping extraction")
            return []
        
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            logger.warning("[Auto-Journal] GROQ_API_KEY not configured, skipping extraction")
            return []
        
        # Call LLM for extraction
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # Fast model for structured extraction
            messages=[
                {"role": "system", "content": "You are a JSON extraction assistant. Return only valid JSON arrays."},
                {"role": "user", "content": extraction_prompt}
            ],
            temperature=0.3,  # Low temperature for consistent extraction
            max_tokens=2000
        )
        
        # Parse response
        response_text = response.choices[0].message.content.strip()
        
        # Clean potential markdown code fences
        if response_text.startswith("```"):
            # Remove first and last lines (code fences)
            lines = response_text.split("\n")
            response_text = "\n".join(lines[1:-1]) if len(lines) > 2 else response_text
        
        if response_text.startswith("json"):
            response_text = response_text[4:].strip()
        
        # Parse JSON
        extracted_events = json.loads(response_text)
        
        if not isinstance(extracted_events, list):
            logger.warning(f"[Auto-Journal] Expected array, got: {type(extracted_events)}")
            return []
        
        logger.info(f"[Auto-Journal] Extracted {len(extracted_events)} events")
        
        # Create journal entries and related entities
        created_entries = []
        
        for event_data in extracted_events:
            try:
                entry = await _create_journal_entry_from_event(
                    db=db,
                    event_data=event_data,
                    campaign=campaign,
                    game_session=game_session,
                    message=message
                )
                if entry:
                    created_entries.append(entry)
            except Exception as e:
                logger.error(f"[Auto-Journal] Failed to create entry from event: {e}")
                continue
        
        logger.info(f"[Auto-Journal] Created {len(created_entries)} journal entries")
        return created_entries
        
    except json.JSONDecodeError as e:
        logger.error(f"[Auto-Journal] Failed to parse JSON response: {e}")
        logger.error(f"[Auto-Journal] Response text: {response_text[:500]}")
        return []
    except Exception as e:
        logger.error(f"[Auto-Journal] Extraction failed: {e}")
        import traceback
        traceback.print_exc()
        return []


async def _create_journal_entry_from_event(
    db: Session,
    event_data: Dict,
    campaign: Campaign,
    game_session: GameSession,
    message: ChatMessage
) -> Optional[JournalEntry]:
    """
    Create a journal entry and related entities (NPC, Quest) from extracted event data.
    """
    entry_type = event_data.get("type")
    title = event_data.get("title")
    description = event_data.get("description")
    importance = event_data.get("importance", 3)
    tags = event_data.get("tags", [])
    metadata = event_data.get("metadata", {})
    
    if not entry_type or not title:
        logger.warning("[Auto-Journal] Missing required fields: type or title")
        return None
    
    # Handle NPC creation
    npc_id = None
    if entry_type == "npc_met" and "npc_name" in metadata:
        npc = await _create_or_update_npc(
            db=db,
            game_session_id=game_session.id,
            name=metadata["npc_name"],
            description=metadata.get("npc_description"),
            role=metadata.get("npc_role"),
            location=metadata.get("location"),
            first_met_session=message.session_id,
            importance=importance
        )
        if npc:
            npc_id = npc.id
    
    # Handle Quest creation/update
    quest_id = None
    if entry_type == "quest_update" and "quest_title" in metadata:
        quest = await _create_or_update_quest(
            db=db,
            game_session_id=game_session.id,
            title=metadata["quest_title"],
            description=description,
            status=metadata.get("quest_status", "in_progress")
        )
        if quest:
            quest_id = quest.id
    
    # Extract location name
    location_name = None
    if entry_type == "location_visited":
        location_name = metadata.get("location_name")
    elif "location" in metadata:
        location_name = metadata["location"]
    
    # Create journal entry
    entry = JournalEntry(
        campaign_id=campaign.id,
        chat_session_id=message.session_id,
        chat_message_id=message.id,
        entry_type=entry_type,
        title=title,
        description=description,
        npc_id=npc_id,
        quest_id=quest_id,
        location_name=location_name,
        importance=importance,
        tags=tags
    )
    
    db.add(entry)
    db.commit()
    db.refresh(entry)
    
    logger.info(f"[Auto-Journal] Created entry: {title} (type={entry_type})")
    return entry


async def _create_or_update_npc(
    db: Session,
    game_session_id: int,
    name: str,
    description: Optional[str] = None,
    role: Optional[str] = None,
    location: Optional[str] = None,
    first_met_session: Optional[int] = None,
    importance: int = 3
) -> Optional[NPC]:
    """
    Create a new NPC or update existing one.
    """
    # Check if NPC already exists
    existing_npc = db.query(NPC).filter(
        NPC.game_session_id == game_session_id,
        NPC.name == name
    ).first()
    
    if existing_npc:
        # Update if new info provided
        if description and not existing_npc.description:
            existing_npc.description = description
        if role and not existing_npc.role:
            existing_npc.role = role
        if location:
            existing_npc.location = location
        if importance > (existing_npc.importance or 1):
            existing_npc.importance = importance
        
        db.commit()
        db.refresh(existing_npc)
        logger.info(f"[Auto-Journal] Updated existing NPC: {name}")
        return existing_npc
    
    # Create new NPC
    npc = NPC(
        game_session_id=game_session_id,
        name=name,
        description=description,
        role=role,
        location=location,
        first_met_session=first_met_session,
        importance=importance
    )
    
    db.add(npc)
    db.commit()
    db.refresh(npc)
    
    logger.info(f"[Auto-Journal] Created new NPC: {name}")
    return npc


async def _create_or_update_quest(
    db: Session,
    game_session_id: int,
    title: str,
    description: Optional[str] = None,
    status: str = "in_progress"
) -> Optional[Quest]:
    """
    Create a new quest or update existing one.
    """
    # Check if quest already exists
    existing_quest = db.query(Quest).filter(
        Quest.game_session_id == game_session_id,
        Quest.title == title
    ).first()
    
    if existing_quest:
        # Update status
        if status and existing_quest.status != status:
            existing_quest.status = status
            if status == "completed":
                from datetime import datetime
                existing_quest.completed_at = datetime.utcnow()
        
        db.commit()
        db.refresh(existing_quest)
        logger.info(f"[Auto-Journal] Updated quest: {title} -> {status}")
        return existing_quest
    
    # Create new quest
    quest = Quest(
        game_session_id=game_session_id,
        title=title,
        description=description,
        status=status
    )
    
    db.add(quest)
    db.commit()
    db.refresh(quest)
    
    logger.info(f"[Auto-Journal] Created new quest: {title}")
    return quest
