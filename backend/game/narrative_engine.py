"""
D&D 5e Narrative Engine

AI-powered scene generation using RAG + LLM for immersive storytelling.

Features:
- Opening scene generation with party context
- Player choice processing
- Combat trigger detection
- NPC dialogue generation
- Scene continuity tracking
- RAG integration for adventure guidance
"""

import json
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass
from sqlalchemy.orm import Session

try:
    from ..models import GameSession, GameEvent, NPC
    from ..database import get_db
    from .session_manager import SessionManager
    from .combat_engine import CombatEngine, CombatantData
    from ..services.dnd_mcp_client import DndMcpClient
except ImportError:
    from backend.models import GameSession, GameEvent, NPC
    from backend.database import get_db
    from backend.game.session_manager import SessionManager
    from backend.game.combat_engine import CombatEngine, CombatantData
    from backend.services.dnd_mcp_client import DndMcpClient


@dataclass
class Scene:
    """A narrative scene with description and choices"""
    description: str
    location: str
    choices: List[Dict[str, Any]]
    detected_events: List[str]
    atmosphere: Optional[str] = None
    npcs_present: Optional[List[str]] = None


@dataclass
class PlayerChoice:
    """A player's chosen action"""
    choice_id: int
    choice_text: str
    choice_type: str  # exploration, social, combat_trigger, skill_check


class NarrativeEngine:
    """
    AI-powered narrative generation using RAG + LLM
    
    Integrates with:
    - RAG system for adventure guidance and flavor
    - LLM for scene generation
    - Combat engine for encounters
    - Session manager for state persistence
    """
    
    def __init__(
        self,
        db: Session,
        embedder=None,
        llm_client=None
    ):
        """
        Initialize narrative engine
        
        Args:
            db: Database session
            embedder: Embedding model for RAG queries
            llm_client: LLM client for text generation
        """
        self.db = db
        self.embedder = embedder
        self.llm = llm_client
        self.session_mgr = SessionManager(db)
        self.combat_engine = CombatEngine(db)
        self.mcp_client = DndMcpClient()  # D&D 5e API client
    
    async def generate_opening_scene(
        self,
        game_session: GameSession,
        adventure_type: str = "fantasy_adventure",
        starting_location: Optional[str] = None
    ) -> Scene:
        """
        Generate opening scene for a new adventure
        
        Process:
        1. Get party composition from party_members
        2. Query RAG for adventure structure guidance
           - adventures_md: "adventure opening", "hooks"
           - dm_tools_core: chambers, atmospheres
        3. Construct LLM prompt with:
           - Party details (classes, levels, backgrounds)
           - Adventure creation guidance from RAG
           - Scene generation instructions
        4. Generate opening scene with LLM
        5. Extract 3-4 player choices
        6. Save to game_state
        7. Log scene generation event
        8. Return Scene object
        
        Args:
            game_session: Active game session
            adventure_type: Type of adventure (fantasy_adventure, mystery, etc.)
            starting_location: Optional starting location override
        
        Returns:
            Scene object with description and choices
        
        Example:
            >>> scene = await engine.generate_opening_scene(session)
            >>> print(scene.description)
            "You stand at the entrance to the ancient ruins..."
            >>> print(scene.choices)
            [{"id": 1, "text": "Investigate the door", "type": "exploration"}, ...]
        """
        # Get party composition
        party_members = self.session_mgr.get_party_status(game_session.id)
        
        if not party_members:
            return Scene(
                description="No party members found. Please add characters to the party first.",
                location="Unknown",
                choices=[],
                detected_events=[]
            )
        
        # Build party context
        party_context = self._build_party_context(party_members)
        
        # Query RAG for adventure guidance (if available)
        rag_context = ""
        if self.embedder:
            rag_context = await self._query_rag_for_opening(adventure_type, party_context)
        
        # Determine starting location
        location = starting_location or self._suggest_starting_location(adventure_type)
        
        # Build LLM prompt
        prompt = self._build_opening_scene_prompt(
            party_context=party_context,
            location=location,
            adventure_type=adventure_type,
            rag_context=rag_context
        )
        
        # Generate scene with LLM (or use fallback)
        if self.llm:
            scene_data = await self._generate_scene_with_llm(prompt)
        else:
            scene_data = self._generate_fallback_opening_scene(location, party_context)
        
        # Parse scene data
        scene = Scene(
            description=scene_data.get("description", ""),
            location=location,
            choices=scene_data.get("choices", []),
            detected_events=scene_data.get("detected_events", []),
            atmosphere=scene_data.get("atmosphere"),
            npcs_present=scene_data.get("npcs_present", [])
        )
        
        # Save to game state
        self.session_mgr.save_state(
            game_session_id=game_session.id,
            state_dict={
                "current_scene": {
                    "description": scene.description,
                    "location": scene.location,
                    "choices": scene.choices,
                    "atmosphere": scene.atmosphere
                }
            },
            merge=True
        )
        
        # Log scene generation
        self.session_mgr.log_event(
            game_session_id=game_session.id,
            event_type="scene_generated",
            description=f"Opening scene: {location}",
            state_snapshot={
                "scene_type": "opening",
                "location": location,
                "party_size": len(party_members),
                "choice_count": len(scene.choices)
            }
        )
        
        return scene
    
    async def process_player_choice(
        self,
        game_session: GameSession,
        choice: PlayerChoice
    ) -> Scene:
        """
        Process player's choice and generate next scene
        
        Process:
        1. Update game_state with player decision
        2. Query RAG for relevant context:
           - If exploration: dm_tools_core, adventures_md
           - If social: npcs, dialogue patterns
           - If potential combat: monsters_md, encounters
        3. Construct LLM prompt with:
           - Current game state
           - Party status
           - Previous events (last 5 from game_events)
           - RAG context
        4. Generate next scene
        5. Detect scene type:
           - Combat: trigger combat_engine.start_combat()
           - Skill check: return check prompt
           - Exploration: present new choices
        6. Update game_state
        7. Log scene event
        8. Return Scene object
        
        Args:
            game_session: Active game session
            choice: Player's chosen action
        
        Returns:
            Next scene with new choices or combat initiation
        """
        # Log player choice
        self.session_mgr.log_event(
            game_session_id=game_session.id,
            event_type="player_choice",
            description=f"Choice: {choice.choice_text}",
            state_snapshot={
                "choice_id": choice.choice_id,
                "choice_text": choice.choice_text,
                "choice_type": choice.choice_type
            }
        )
        
        # Get current game state
        current_state = self.session_mgr.load_state(game_session.id)
        current_scene = current_state.get("current_scene", {})
        
        # Get recent events for context
        recent_events = self.session_mgr.get_event_log(
            game_session_id=game_session.id,
            limit=5
        )
        
        # Get party status
        party_members = self.session_mgr.get_party_status(game_session.id)
        party_context = self._build_party_context(party_members)
        
        # Query RAG based on choice type
        rag_context = ""
        if self.embedder:
            rag_context = await self._query_rag_for_choice(
                choice=choice,
                current_location=current_scene.get("location", "unknown"),
                party_context=party_context
            )
        
        # Build continuation prompt
        prompt = self._build_continuation_prompt(
            choice=choice,
            current_scene=current_scene,
            recent_events=recent_events,
            party_context=party_context,
            rag_context=rag_context
        )
        
        # Generate next scene
        if self.llm:
            scene_data = await self._generate_scene_with_llm(prompt)
        else:
            scene_data = self._generate_fallback_continuation(choice, current_scene)
        
        # Check for combat trigger
        if choice.choice_type == "combat_trigger" or "combat" in scene_data.get("detected_events", []):
            # Initiate combat
            combat_data = scene_data.get("combat_setup", {})
            if combat_data:
                combat = await self._initiate_combat(
                    game_session=game_session,
                    combat_data=combat_data,
                    location=current_scene.get("location", "battlefield")
                )
                scene_data["combat_id"] = combat.id
        
        # Parse scene
        scene = Scene(
            description=scene_data.get("description", ""),
            location=scene_data.get("location", current_scene.get("location", "unknown")),
            choices=scene_data.get("choices", []),
            detected_events=scene_data.get("detected_events", []),
            atmosphere=scene_data.get("atmosphere"),
            npcs_present=scene_data.get("npcs_present", [])
        )
        
        # Save updated state
        self.session_mgr.save_state(
            game_session_id=game_session.id,
            state_dict={
                "current_scene": {
                    "description": scene.description,
                    "location": scene.location,
                    "choices": scene.choices,
                    "atmosphere": scene.atmosphere
                },
                "last_choice": {
                    "choice_text": choice.choice_text,
                    "choice_type": choice.choice_type
                }
            },
            merge=True
        )
        
        # Log scene generation
        self.session_mgr.log_event(
            game_session_id=game_session.id,
            event_type="scene_generated",
            description=f"Scene: {scene.location}",
            state_snapshot={
                "scene_type": "continuation",
                "location": scene.location,
                "choice_count": len(scene.choices),
                "events": scene.detected_events
            }
        )
        
        return scene
    
    async def generate_npc_dialogue(
        self,
        game_session: GameSession,
        npc_name: str,
        player_message: str
    ) -> str:
        """
        Generate NPC dialogue response
        
        Process:
        1. Get or create NPC record
        2. Get NPC personality from dialogue_history
        3. Query RAG for similar dialogue patterns (if available)
        4. Generate contextual response
        5. Update npc.dialogue_history
        6. Return NPC response
        
        Args:
            game_session: Active game session
            npc_name: Name of the NPC
            player_message: What the player said
        
        Returns:
            NPC's dialogue response
        """
        # Get or create NPC
        npc = self.db.query(NPC).filter(
            NPC.game_session_id == game_session.id,
            NPC.name == npc_name
        ).first()
        
        if not npc:
            # Create new NPC
            npc = NPC(
                game_session_id=game_session.id,
                name=npc_name,
                location=self.session_mgr.load_state(game_session.id).get("current_scene", {}).get("location", "unknown"),
                dialogue_history=[],
                relationship_status={}
            )
            self.db.add(npc)
            self.db.commit()
        
        # Build dialogue context
        dialogue_history = npc.dialogue_history or []
        
        # Query RAG for dialogue patterns (if available)
        rag_context = ""
        if self.embedder:
            rag_context = await self._query_rag_for_dialogue(npc_name, player_message)
        
        # Generate response with LLM or fallback
        if self.llm:
            prompt = self._build_dialogue_prompt(
                npc_name=npc_name,
                npc_personality=npc.personality,
                dialogue_history=dialogue_history,
                player_message=player_message,
                rag_context=rag_context
            )
            response = await self._generate_dialogue_with_llm(prompt)
        else:
            response = self._generate_fallback_dialogue(npc_name, player_message)
        
        # Update dialogue history
        dialogue_history.append({
            "player": player_message,
            "npc": response,
            "timestamp": "current"  # Would use actual timestamp
        })
        npc.dialogue_history = dialogue_history
        self.db.commit()
        
        # Log dialogue
        self.session_mgr.log_event(
            game_session_id=game_session.id,
            event_type="npc_dialogue",
            description=f"{npc_name}: {response[:100]}...",
            state_snapshot={
                "npc_name": npc_name,
                "player_message": player_message,
                "npc_response": response
            }
        )
        
        return response
    
    async def describe_combat_round(
        self,
        combat_id: int,
        last_action: Optional[Dict] = None
    ) -> str:
        """
        Generate narrative description of combat round
        
        Args:
            combat_id: ID of active combat
            last_action: Last action taken (attack result, etc.)
        
        Returns:
            Dramatic combat narration
        """
        # Get combat state
        combat_state = self.combat_engine.get_combat_state(combat_id)
        
        # Build combat context
        combat_context = {
            "round": combat_state.round_number,
            "current_turn": combat_state.turn_order[combat_state.current_turn] if combat_state.current_turn < len(combat_state.turn_order) else None,
            "participants": combat_state.participants,
            "last_action": last_action
        }
        
        # Generate description
        if self.llm:
            prompt = self._build_combat_narration_prompt(combat_context)
            description = await self._generate_combat_narration_with_llm(prompt)
        else:
            description = self._generate_fallback_combat_narration(combat_context)
        
        return description
    
    # ========================================================================
    # PRIVATE HELPER METHODS
    # ========================================================================
    
    def _build_party_context(self, party_members: List[Dict]) -> str:
        """Build party composition context string"""
        if not party_members:
            return "No party members"
        
        party_lines = []
        for member in party_members:
            char = member.get("character", {})
            party_lines.append(
                f"- {char.get('name', 'Unknown')}: Level {char.get('level', 1)} "
                f"{char.get('class_', 'Unknown')} "
                f"({member.get('current_hp')}/{member.get('max_hp')} HP, AC {char.get('armor_class', 10)})"
            )
        
        return "\n".join(party_lines)
    
    def _suggest_starting_location(self, adventure_type: str) -> str:
        """Suggest starting location based on adventure type"""
        locations = {
            "fantasy_adventure": "The Crossroads Tavern",
            "mystery": "The abandoned manor",
            "dungeon_crawl": "The entrance to the ancient ruins",
            "wilderness": "The edge of the dark forest",
            "urban": "The bustling city marketplace"
        }
        return locations.get(adventure_type, "A mysterious location")
    
    async def _query_rag_for_opening(self, adventure_type: str, party_context: str) -> str:
        """Query RAG for adventure opening guidance"""
        # Placeholder - would implement actual RAG query
        # query = f"adventure opening hooks {adventure_type} party introduction"
        # results = await self.embedder.search(query, top_k=3)
        # return "\n".join([r.text for r in results])
        return ""
    
    async def _query_rag_for_choice(self, choice: PlayerChoice, current_location: str, party_context: str) -> str:
        """Query RAG based on player choice type"""
        # Placeholder - would implement actual RAG query
        return ""
    
    async def _query_rag_for_dialogue(self, npc_name: str, player_message: str) -> str:
        """Query RAG for dialogue patterns"""
        # Placeholder - would implement actual RAG query
        return ""
    
    def _build_opening_scene_prompt(
        self,
        party_context: str,
        location: str,
        adventure_type: str,
        rag_context: str
    ) -> str:
        """Build LLM prompt for opening scene"""
        prompt = f"""You are an expert D&D Dungeon Master running a 5e campaign.

PARTY COMPOSITION:
{party_context}

ADVENTURE TYPE: {adventure_type}
STARTING LOCATION: {location}

{f"ADVENTURE GUIDANCE (from DMG):\\n{rag_context}\\n" if rag_context else ""}

TASK: Generate an engaging opening scene for this adventure.

Requirements:
1. Describe the scene vividly (2-3 paragraphs)
2. Include sensory details (sights, sounds, smells)
3. Present 3-4 meaningful choices for the players
4. Set up potential for adventure

Format response as JSON:
{{
  "description": "...",
  "location": "{location}",
  "atmosphere": "...",
  "choices": [
    {{"id": 1, "text": "...", "type": "exploration"}},
    {{"id": 2, "text": "...", "type": "social"}},
    {{"id": 3, "text": "...", "type": "skill_check"}},
    {{"id": 4, "text": "...", "type": "combat_trigger"}}
  ],
  "detected_events": [],
  "npcs_present": [...]
}}
"""
        return prompt
    
    def _build_continuation_prompt(
        self,
        choice: PlayerChoice,
        current_scene: Dict,
        recent_events: List,
        party_context: str,
        rag_context: str
    ) -> str:
        """Build LLM prompt for scene continuation"""
        prompt = f"""You are an expert D&D Dungeon Master running a 5e campaign.

PARTY STATUS:
{party_context}

CURRENT LOCATION: {current_scene.get('location', 'unknown')}

PLAYER'S CHOICE: {choice.choice_text}
CHOICE TYPE: {choice.choice_type}

RECENT EVENTS:
{self._format_recent_events(recent_events)}

{f"RELEVANT CONTEXT (from adventure guides):\\n{rag_context}\\n" if rag_context else ""}

TASK: Generate the next scene based on the player's choice.

Requirements:
1. Describe what happens as a result of their choice (2-3 paragraphs)
2. Maintain narrative continuity
3. Present 3-4 new meaningful choices
4. Include consequences of their action

Format response as JSON:
{{
  "description": "...",
  "location": "...",
  "atmosphere": "...",
  "choices": [...],
  "detected_events": ["combat", "skill_check:perception:DC15", etc.],
  "npcs_present": [...],
  "combat_setup": {{  // Only if combat triggered
    "enemies": [
      {{"name": "Goblin", "count": 2, "hp": 7, "ac": 15, "initiative_bonus": 2}}
    ]
  }}
}}
"""
        return prompt
    
    def _build_dialogue_prompt(
        self,
        npc_name: str,
        npc_personality: Optional[str],
        dialogue_history: List[Dict],
        player_message: str,
        rag_context: str
    ) -> str:
        """Build LLM prompt for NPC dialogue"""
        history_text = "\n".join([
            f"Player: {d.get('player', '')}\n{npc_name}: {d.get('npc', '')}"
            for d in dialogue_history[-3:]  # Last 3 exchanges
        ])
        
        prompt = f"""You are {npc_name}, an NPC in a D&D campaign.

PERSONALITY: {npc_personality or "Neutral, helpful"}

PREVIOUS CONVERSATION:
{history_text}

PLAYER SAYS: "{player_message}"

{f"DIALOGUE GUIDANCE:\\n{rag_context}\\n" if rag_context else ""}

TASK: Respond in character as {npc_name}. Keep response 1-3 sentences.
Be natural, stay in character, and advance the conversation.

Response:"""
        return prompt
    
    def _build_combat_narration_prompt(self, combat_context: Dict) -> str:
        """Build LLM prompt for combat narration"""
        prompt = f"""You are a D&D Dungeon Master narrating combat.

ROUND: {combat_context['round']}
CURRENT TURN: {combat_context['current_turn'].get('name', 'Unknown') if combat_context['current_turn'] else 'Starting'}

PARTICIPANTS:
{self._format_combat_participants(combat_context['participants'])}

LAST ACTION:
{self._format_last_action(combat_context.get('last_action'))}

TASK: Provide dramatic combat narration (2-3 sentences).
Describe the action vividly and prompt for next action.

Narration:"""
        return prompt
    
    def _format_recent_events(self, events: List) -> str:
        """Format recent events for prompts"""
        if not events:
            return "No recent events"
        
        return "\n".join([
            f"- {e.description}"
            for e in events[-5:]
        ])
    
    def _format_combat_participants(self, participants: List[Dict]) -> str:
        """Format combat participants for prompts"""
        lines = []
        for p in participants:
            status = "DEFEATED" if p.get('defeated') else f"{p.get('current_hp')}/{p.get('max_hp')} HP"
            lines.append(f"- {p.get('name')}: {status}")
        return "\n".join(lines)
    
    def _format_last_action(self, action: Optional[Dict]) -> str:
        """Format last combat action for prompts"""
        if not action:
            return "Combat just started"
        return action.get("description", "Unknown action")
    
    async def _generate_scene_with_llm(self, prompt: str) -> Dict:
        """Generate scene using LLM (placeholder)"""
        # Would call actual LLM API
        # response = await self.llm.generate(prompt)
        # return json.loads(response)
        return {}
    
    async def _generate_dialogue_with_llm(self, prompt: str) -> str:
        """Generate dialogue using LLM (placeholder)"""
        # Would call actual LLM API
        return "I'm sorry, I cannot help with that right now."
    
    async def _generate_combat_narration_with_llm(self, prompt: str) -> str:
        """Generate combat narration using LLM (placeholder)"""
        # Would call actual LLM API
        return "The battle rages on!"
    
    def _generate_fallback_opening_scene(self, location: str, party_context: str) -> Dict:
        """Generate fallback opening scene without LLM"""
        return {
            "description": f"You find yourselves at {location}. The air is thick with anticipation as your party gathers, ready for adventure. What will you do?",
            "location": location,
            "atmosphere": "Anticipatory",
            "choices": [
                {"id": 1, "text": "Look around carefully", "type": "exploration"},
                {"id": 2, "text": "Talk to nearby NPCs", "type": "social"},
                {"id": 3, "text": "Search for danger", "type": "skill_check"},
                {"id": 4, "text": "Prepare for trouble", "type": "combat_trigger"}
            ],
            "detected_events": [],
            "npcs_present": []
        }
    
    def _generate_fallback_continuation(self, choice: PlayerChoice, current_scene: Dict) -> Dict:
        """Generate fallback continuation without LLM"""
        return {
            "description": f"You decide to {choice.choice_text.lower()}. The situation evolves around you.",
            "location": current_scene.get("location", "unknown"),
            "atmosphere": "Evolving",
            "choices": [
                {"id": 1, "text": "Continue forward", "type": "exploration"},
                {"id": 2, "text": "Investigate further", "type": "skill_check"},
                {"id": 3, "text": "Prepare for combat", "type": "combat_trigger"}
            ],
            "detected_events": []
        }
    
    def _generate_fallback_dialogue(self, npc_name: str, player_message: str) -> str:
        """Generate fallback dialogue without LLM"""
        return f"{npc_name} nods thoughtfully and says, 'That's interesting. Tell me more.'"
    
    def _generate_fallback_combat_narration(self, combat_context: Dict) -> str:
        """Generate fallback combat narration without LLM"""
        current = combat_context.get('current_turn', {})
        if current:
            return f"Round {combat_context['round']}: {current.get('name', 'Unknown')}'s turn. What do you do?"
        return f"Round {combat_context['round']}: The battle continues!"
    
    async def _initiate_combat(
        self,
        game_session: GameSession,
        combat_data: Dict,
        location: str
    ) -> Any:
        """Initiate combat encounter from scene data"""
        # Parse combat setup
        enemies = combat_data.get("enemies", [])
        
        # Get party members
        party_members = self.session_mgr.get_party_status(game_session.id)
        
        # Build combatants list
        combatants = []
        
        # Add party members
        for member in party_members:
            char = member.get("character", {})
            combatants.append(CombatantData(
                name=char.get("name", "Unknown"),
                initiative_bonus=char.get("dexterity_modifier", 0),
                max_hp=member.get("max_hp", 10),
                current_hp=member.get("current_hp", 10),
                ac=char.get("armor_class", 10),
                is_player=True,
                character_id=member.get("character_id")
            ))
        
        # Add enemies
        for enemy_group in enemies:
            name = enemy_group.get("name", "Enemy")
            count = enemy_group.get("count", 1)
            
            for i in range(count):
                enemy_name = f"{name} {i+1}" if count > 1 else name
                combatants.append(CombatantData(
                    name=enemy_name,
                    initiative_bonus=enemy_group.get("initiative_bonus", 0),
                    max_hp=enemy_group.get("hp", 10),
                    current_hp=enemy_group.get("hp", 10),
                    ac=enemy_group.get("ac", 10),
                    is_player=False,
                    monster_type=name.lower()
                ))
        
        # Start combat
        combat = self.combat_engine.start_combat(
            game_session_id=game_session.id,
            participants=combatants,
            location=location
        )
        
        return combat
    
    # ============================================================================
    # D&D MCP INTEGRATION - Spell & Monster Lookup
    # ============================================================================
    
    async def process_spell_cast(
        self,
        spell_name: str,
        caster_name: str,
        target: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process spell casting with official D&D 5e spell data.
        
        Fetches spell details from MCP client and returns formatted
        information for narrative integration.
        
        Args:
            spell_name: Name of spell (e.g., "Fireball", "Cure Wounds")
            caster_name: Name of character casting spell
            target: Optional target of spell
        
        Returns:
            Dictionary with spell data:
            {
                "success": bool,
                "spell": {...},  # Full spell data from MCP
                "narrative": str,  # Formatted description
                "damage": str,  # Damage dice if applicable
                "save_dc": str,  # Saving throw info
                "error": str  # If lookup failed
            }
        
        Example:
            >>> result = await engine.process_spell_cast("Fireball", "Gandalf")
            >>> print(result["narrative"])
            "Gandalf casts Fireball (3rd-level Evocation). Each creature in a 
             20-foot-radius sphere must make a Dexterity saving throw..."
        """
        try:
            # Fetch spell from D&D 5e API via MCP
            spell_data = await self.mcp_client.get_spell(spell_name)
            
            if not spell_data or "error" in spell_data:
                return {
                    "success": False,
                    "error": f"Spell '{spell_name}' not found in D&D 5e database",
                    "narrative": f"{caster_name} attempts to cast {spell_name}, but the spell fizzles..."
                }
            
            # Extract key spell information
            spell = spell_data.get("spell", {})
            level = spell.get("level", 0)
            school = spell.get("school", {}).get("name", "")
            casting_time = spell.get("casting_time", "1 action")
            spell_range = spell.get("range", "")
            components = spell.get("components", [])
            duration = spell.get("duration", "")
            description = spell.get("desc", [""])[0] if spell.get("desc") else ""
            
            # Check for damage
            damage_info = ""
            if spell.get("damage"):
                damage_type = spell["damage"].get("damage_type", {}).get("name", "")
                damage_at_slot_level = spell["damage"].get("damage_at_slot_level", {})
                if damage_at_slot_level:
                    first_level = list(damage_at_slot_level.values())[0]
                    damage_info = f" Damage: {first_level} {damage_type}"
            
            # Check for saving throw
            save_info = ""
            if spell.get("dc"):
                save_type = spell["dc"].get("dc_type", {}).get("name", "")
                save_info = f" Save: {save_type} DC"
            
            # Build narrative description
            level_str = "cantrip" if level == 0 else f"{level}{'st' if level == 1 else 'nd' if level == 2 else 'rd' if level == 3 else 'th'}-level"
            components_str = ", ".join(components)
            
            target_str = f" targeting {target}" if target else ""
            
            narrative = (
                f"{caster_name} casts **{spell_name}** ({level_str} {school}){target_str}. "
                f"*Casting Time: {casting_time}, Range: {spell_range}, Components: {components_str}, "
                f"Duration: {duration}*\n\n"
                f"{description[:200]}..."
            )
            
            return {
                "success": True,
                "spell": spell,
                "spell_name": spell_name,
                "level": level,
                "school": school,
                "narrative": narrative,
                "damage": damage_info,
                "save_dc": save_info,
                "full_description": description,
                "components": components,
                "range": spell_range,
                "duration": duration
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "narrative": f"{caster_name} attempts to cast {spell_name}, but something goes wrong..."
            }
    
    async def spawn_monster(
        self,
        monster_name: str,
        count: int = 1,
        location: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Spawn monster(s) with official D&D 5e stat blocks.
        
        Fetches monster data from MCP client and returns formatted
        information for combat encounters.
        
        Args:
            monster_name: Name of monster (e.g., "Goblin", "Ancient Red Dragon")
            count: Number of monsters to spawn
            location: Optional location description
        
        Returns:
            Dictionary with monster data:
            {
                "success": bool,
                "monster": {...},  # Full monster data from MCP
                "narrative": str,  # Formatted spawn description
                "combatants": [...],  # CombatantData objects for combat engine
                "error": str  # If lookup failed
            }
        
        Example:
            >>> result = await engine.spawn_monster("Goblin", count=3)
            >>> print(result["narrative"])
            "3 Goblins appear! CR 1/4, AC 15, HP 7 each."
        """
        try:
            # Fetch monster from D&D 5e API via MCP
            monster_data = await self.mcp_client.get_monster(monster_name)
            
            if not monster_data or "error" in monster_data:
                return {
                    "success": False,
                    "error": f"Monster '{monster_name}' not found in D&D 5e database",
                    "narrative": f"You sense a presence, but nothing appears..."
                }
            
            # Extract monster stats
            monster = monster_data.get("monster", {})
            name = monster.get("name", monster_name)
            size = monster.get("size", "")
            monster_type = monster.get("type", "")
            alignment = monster.get("alignment", "")
            ac = monster.get("armor_class", [{}])[0].get("value", 10) if monster.get("armor_class") else 10
            hp_dice = monster.get("hit_points_roll", "1d8")
            hp = monster.get("hit_points", 10)
            cr = monster.get("challenge_rating", 0)
            
            # Get abilities for initiative
            dex_score = monster.get("dexterity", 10)
            dex_modifier = (dex_score - 10) // 2
            
            # Build narrative description
            location_str = f" in {location}" if location else ""
            count_str = f"{count} " if count > 1 else "A "
            plural_name = name if count == 1 else f"{name}s"
            
            narrative = (
                f"{count_str}**{plural_name}** {'appear' if count > 1 else 'appears'}{location_str}! "
                f"*{size} {monster_type}, {alignment}. "
                f"CR {cr}, AC {ac}, HP {hp} each ({hp_dice}).*\n\n"
            )
            
            # Add description if available
            if monster.get("desc"):
                narrative += f"{monster['desc'][:150]}..."
            
            # Build combatant data for combat engine
            combatants = []
            for i in range(count):
                combatant_name = f"{name} {i+1}" if count > 1 else name
                combatants.append(CombatantData(
                    name=combatant_name,
                    initiative_bonus=dex_modifier,
                    max_hp=hp,
                    current_hp=hp,
                    ac=ac,
                    is_player=False,
                    monster_type=name.lower()
                ))
            
            return {
                "success": True,
                "monster": monster,
                "monster_name": name,
                "count": count,
                "narrative": narrative,
                "combatants": combatants,
                "ac": ac,
                "hp": hp,
                "cr": cr,
                "dex_modifier": dex_modifier,
                "size": size,
                "type": monster_type,
                "alignment": alignment
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "narrative": f"You sense a {monster_name} nearby, but it remains hidden..."
            }
    
    async def enhance_scene_with_dnd_content(
        self,
        scene_description: str,
        context: Dict[str, Any]
    ) -> str:
        """
        Enhance scene description with relevant D&D content from MCP.
        
        Analyzes scene for D&D entities (spells, monsters, items) and
        enriches description with official data where applicable.
        
        Args:
            scene_description: Raw scene text
            context: Additional context (party level, location, etc.)
        
        Returns:
            Enhanced scene description with D&D details
        
        Example:
            >>> enhanced = await engine.enhance_scene_with_dnd_content(
            ...     "A wizard casts Fireball at the goblins",
            ...     {"party_level": 5}
            ... )
        """
        # This is a placeholder for future enhancement
        # Could use NLP to detect spell/monster names and auto-lookup
        return scene_description

