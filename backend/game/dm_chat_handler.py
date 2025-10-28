"""
DM Chat Handler - Natural Language Interface for AI Dungeon Master

This module provides a chat-based interface that connects all game systems
(dice, combat, narrative) through natural language processing.

Architecture:
1. Process player messages through intent classification (exploration/combat/dialogue/command)
2. Route to appropriate game system based on intent
3. Generate contextual DM responses using LLM
4. Maintain conversation history and game state consistency
5. Log all interactions for narrative continuity

LLM Provider Support:
- Named providers: openai, anthropic, google, groq
- Local LM Studio: URL-based (http://host:port/v1)
- Unified interface via call_llm() from generation.py
"""

import json
from typing import List, Dict, Any
from dataclasses import dataclass
from enum import Enum

from sqlalchemy.orm import Session
from backend.models import GameSession
from backend.game.dice_roller import DiceRoller
from backend.game.combat_engine import CombatEngine
from backend.game.narrative_engine import NarrativeEngine

# Import unified LLM interface
from backend.routers.generation import call_llm

try:
    from backend.services.dnd_mcp_client import DndMcpClient
except ImportError:
    DndMcpClient = None  # MCP client not available


class IntentType(Enum):
    """Types of player intents that can be detected"""
    EXPLORATION = "exploration"  # Moving, investigating, exploring
    COMBAT_ACTION = "combat_action"  # Attacking, casting spells in combat
    DIALOGUE = "dialogue"  # Talking to NPCs
    COMMAND = "command"  # Slash commands (/roll, /hp, /status)
    UNKNOWN = "unknown"


@dataclass
class Intent:
    """Parsed player intent with routing information"""
    type: IntentType
    confidence: float
    entities: Dict[str, Any]  # Extracted entities (target, dice, location, etc.)
    raw_message: str


@dataclass
class DMResponse:
    """DM response with game state updates"""
    message: str
    game_state_changed: bool
    scene_changed: bool
    combat_started: bool
    combat_ended: bool
    events: List[Dict[str, Any]]  # Game events that occurred
    suggested_actions: List[Dict[str, Any]] = None  # Structured action suggestions
    
    def __post_init__(self):
        """Initialize suggested_actions as empty list if None"""
        if self.suggested_actions is None:
            self.suggested_actions = []


class DMChatHandler:
    """
    Main AI DM chat interface that orchestrates all game systems.
    
    This handler acts as the "brain" of the AI DM, processing natural language
    player input and coordinating responses across dice rolling, combat, narrative,
    and dialogue systems.
    
    Supports multiple LLM providers:
    - Named providers: openai, anthropic, google, groq
    - Local LM Studio: URL (e.g., http://100.120.44.114:1234/v1)
    """
    
    def __init__(
        self,
        db: Session,
        provider: str = "http://100.120.44.114:1234/v1",
        model: str = "local-model",
        dm_roll_for_players: bool = False
    ):
        """
        Initialize DM chat handler with all game system dependencies.
        
        Args:
            db: Database session for state persistence
            provider: LLM provider (named provider or URL for LM Studio)
            model: Model identifier for the provider
            dm_roll_for_players: If True, DM AI rolls for players during checks
        """
        self.db = db
        self.provider = provider
        self.model = model
        self.dm_roll_for_players = dm_roll_for_players
        
        # Initialize game system components
        self.dice_roller = DiceRoller()
        self.combat_engine = CombatEngine(db)
        self.narrative_engine = NarrativeEngine(db)
        
        # Initialize MCP client if available
        self.mcp_client = DndMcpClient() if DndMcpClient else None
        
        # Conversation context (per session)
        self.conversation_history: Dict[int, List[Dict[str, str]]] = {}
        
    async def process_game_message(
        self,
        game_session: GameSession,
        user_message: str,
        max_history: int = 10
    ) -> DMResponse:
        """
        Process a player's chat message and generate an appropriate DM response.
        
        This is the main entry point for the chat interface. It:
        1. Maintains conversation history
        2. Parses player intent
        3. Routes to appropriate game system
        4. Generates contextual response
        5. Updates game state
        6. Logs events
        
        Args:
            game_session: Active game session
            user_message: Player's natural language message
            max_history: Maximum conversation history to maintain
            
        Returns:
            DMResponse with message and state changes
        """
        session_id = game_session.id
        
        # Initialize conversation history if needed
        if session_id not in self.conversation_history:
            self.conversation_history[session_id] = []
        
        # Add user message to history
        self.conversation_history[session_id].append({
            "role": "user",
            "content": user_message
        })
        
        # Trim history to max_history messages
        if len(self.conversation_history[session_id]) > max_history * 2:  # *2 for user+assistant pairs
            self.conversation_history[session_id] = self.conversation_history[session_id][-max_history * 2:]
        
        # Check for slash commands first
        if user_message.strip().startswith('/'):
            return await self._handle_command(game_session, user_message)
        
        # Detect spell casting (auto-lookup if MCP available)
        if self.mcp_client:
            spell_detected, spell_name = await self._detect_spell_cast(user_message)
            if spell_detected:
                # Prepend spell info to response
                spell_info = await self._lookup_spell(spell_name)
                user_message = f"{user_message}\n\n[Auto-looked up spell: {spell_name}]\n{spell_info}"
        
        # Detect monster mentions (auto-suggest spawn if MCP available)
        if self.mcp_client:
            monster_detected, monster_name = await self._detect_monster_mention(user_message)
            if monster_detected:
                # Add monster info as context hint
                monster_info = await self._lookup_monster(monster_name)
                user_message = f"{user_message}\n\n[Auto-looked up monster: {monster_name}]\n{monster_info}"
        
        # Parse intent using LLM
        intent = await self._parse_intent(game_session, user_message)
        
        # Route based on intent
        if intent.type == IntentType.COMMAND:
            response = await self._handle_command(game_session, user_message)
        elif intent.type == IntentType.COMBAT_ACTION:
            response = await self._handle_combat_action(game_session, intent)
        elif intent.type == IntentType.DIALOGUE:
            response = await self._handle_dialogue(game_session, intent)
        elif intent.type == IntentType.EXPLORATION:
            response = await self._handle_exploration(game_session, intent)
        else:
            response = await self._handle_unknown(game_session, user_message)
        
        # Add DM response to conversation history
        self.conversation_history[session_id].append({
            "role": "assistant",
            "content": response.message
        })
        
        return response
    
    async def _parse_intent(self, game_session: GameSession, user_message: str) -> Intent:
        """
        Parse player message to determine intent using LLM.
        
        Uses structured JSON output to classify intent and extract entities.
        
        Expected JSON format:
        {
            "intent": "exploration|combat_action|dialogue|command|unknown",
            "confidence": 0.0-1.0,
            "entities": {
                "target": "goblin",
                "action": "attack",
                "dice": "1d20+5",
                "npc_name": "Innkeeper",
                "location": "tavern basement"
            }
        }
        """
        # Build game context
        game_context = self._build_game_context(game_session)
        
        # Intent classification prompt
        system_prompt = """You are an AI assistant helping a D&D Dungeon Master classify player actions.
Analyze the player's message and determine their intent. Return ONLY valid JSON.

Intent types:
- exploration: Player is moving, investigating, or exploring the environment
- combat_action: Player is attacking, casting spells, or taking combat actions
- dialogue: Player is talking to an NPC
- command: Player used a slash command (/roll, /hp, /status)
- unknown: Unable to determine intent

Extract relevant entities like target, action, dice notation, NPC name, location, etc.

Return JSON format:
{
    "intent": "<intent_type>",
    "confidence": <0.0-1.0>,
    "entities": {<extracted entities>}
}"""
        
        try:
            # Convert messages to prompt string for unified LLM interface
            prompt = f"{system_prompt}\n\nGame context:\n{game_context}\n\nPlayer message: {user_message}"
            
            # Call unified LLM interface
            response_text, metadata = await call_llm(
                prompt=prompt,
                provider=self.provider,
                model=self.model
            )
            
            # Parse JSON response
            parsed = json.loads(response_text)
            
            return Intent(
                type=IntentType(parsed.get('intent', 'unknown')),
                confidence=parsed.get('confidence', 0.5),
                entities=parsed.get('entities', {}),
                raw_message=user_message
            )
            
        except Exception as e:
            print(f"Intent parsing failed: {e}")
            # Fallback to simple heuristics
            return self._fallback_intent_parse(user_message)
    
    def _fallback_intent_parse(self, message: str) -> Intent:
        """Simple heuristic-based intent parsing when LLM fails"""
        msg_lower = message.lower()
        
        # Check for commands
        if msg_lower.startswith('/'):
            return Intent(IntentType.COMMAND, 1.0, {}, message)
        
        # Check for combat keywords
        combat_keywords = ['attack', 'hit', 'strike', 'cast', 'shoot', 'stab', 'slash']
        if any(kw in msg_lower for kw in combat_keywords):
            return Intent(IntentType.COMBAT_ACTION, 0.7, {}, message)
        
        # Check for dialogue keywords
        dialogue_keywords = ['say', 'ask', 'tell', 'speak', 'talk', 'whisper']
        if any(kw in msg_lower for kw in dialogue_keywords):
            return Intent(IntentType.DIALOGUE, 0.7, {}, message)
        
        # Default to exploration
        return Intent(IntentType.EXPLORATION, 0.5, {}, message)
    
    async def _handle_command(self, game_session: GameSession, message: str) -> DMResponse:
        """Handle slash commands like /roll, /hp, /status"""
        parts = message.strip().split(maxsplit=1)
        command = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        events = []
        
        if command == '/roll':
            # Roll dice
            if not args:
                return DMResponse(
                    message="Please specify dice notation. Example: /roll 1d20+5",
                    game_state_changed=False,
                    scene_changed=False,
                    combat_started=False,
                    combat_ended=False,
                    events=[]
                )
            
            try:
                result = self.dice_roller.roll(args)
                message = f"🎲 Rolling {args}:\n{result['formatted']}\n**Total: {result['total']}**"
                
                events.append({
                    "type": "dice_roll",
                    "notation": args,
                    "total": result['total'],
                    "details": result
                })
                
            except ValueError as e:
                message = f"❌ Invalid dice notation: {e}"
        
        elif command == '/hp':
            # Show or update HP
            if not args:
                # Show current HP for all party members
                party_status = game_session.game_state.get('party_status', {})
                if not party_status:
                    message = "No party members found."
                else:
                    lines = ["**Party HP:**"]
                    for char_name, status in party_status.items():
                        hp = status.get('current_hp', 0)
                        max_hp = status.get('max_hp', 0)
                        lines.append(f"- {char_name}: {hp}/{max_hp} HP")
                    message = "\n".join(lines)
            else:
                message = "HP modification not yet implemented. Use /hp to view current HP."
        
        elif command == '/status':
            # Show game status
            lines = [
                "**Game Status:**",
                f"Session ID: {game_session.id}",
                f"Party: {', '.join(game_session.game_state.get('party_status', {}).keys()) or 'Empty'}",
            ]
            
            # Combat status
            combat_state = game_session.game_state.get('combat_state')
            if combat_state and combat_state.get('active'):
                lines.append(f"⚔️ **In Combat** - Round {combat_state.get('round', 1)}")
                current_turn = combat_state.get('current_turn', 0)
                combatants = combat_state.get('combatants', [])
                if combatants and current_turn < len(combatants):
                    lines.append(f"Current Turn: {combatants[current_turn].get('name', 'Unknown')}")
            else:
                lines.append("Status: Exploring")
            
            # Current scene
            current_scene = game_session.game_state.get('current_scene')
            if current_scene:
                location = current_scene.get('location', 'Unknown')
                lines.append(f"Location: {location}")
            
            message = "\n".join(lines)
        
        elif command == '/spell':
            # Look up D&D spell
            if not self.mcp_client:
                message = "❌ D&D MCP client not available. Cannot look up spells."
            elif not args:
                message = "Please specify a spell name. Example: /spell Fireball"
            else:
                message = await self._lookup_spell(args.strip())
        
        elif command == '/monster':
            # Look up D&D monster
            if not self.mcp_client:
                message = "❌ D&D MCP client not available. Cannot look up monsters."
            elif not args:
                message = "Please specify a monster name. Example: /monster Goblin"
            else:
                message = await self._lookup_monster(args.strip())
        
        elif command == '/item':
            # Look up D&D magic item
            if not self.mcp_client:
                message = "❌ D&D MCP client not available. Cannot look up items."
            elif not args:
                message = "Please specify an item name. Example: /item Bag of Holding"
            else:
                message = await self._lookup_item(args.strip())
        
        else:
            message = f"Unknown command: {command}\nAvailable: /roll, /hp, /status, /spell, /monster, /item"
        
        return DMResponse(
            message=message,
            game_state_changed=False,
            scene_changed=False,
            combat_started=False,
            combat_ended=False,
            events=events
        )
    
    async def _handle_combat_action(self, game_session: GameSession, intent: Intent) -> DMResponse:
        """Handle combat actions (attacks, spells, etc.)"""
        events = []
        
        # Check if in combat
        combat_state = game_session.game_state.get('combat_state')
        if not combat_state or not combat_state.get('active'):
            return DMResponse(
                message="You're not in combat. Explore or initiate combat first.",
                game_state_changed=False,
                scene_changed=False,
                combat_started=False,
                combat_ended=False,
                events=[]
            )
        
        combat_id = combat_state.get('id')
        if not combat_id:
            return DMResponse(
                message="Error: Combat ID not found.",
                game_state_changed=False,
                scene_changed=False,
                combat_started=False,
                combat_ended=False,
                events=[]
            )
        
        # Process attack through combat engine
        try:
            # Extract action details from intent
            target = intent.entities.get('target', 'enemy')
            action_type = intent.entities.get('action', 'attack')
            
            # Get current combatant
            current_turn = combat_state.get('current_turn', 0)
            combatants = combat_state.get('combatants', [])
            
            if not combatants or current_turn >= len(combatants):
                message = "Error: No valid combatant for current turn."
            else:
                attacker_name = combatants[current_turn].get('name')
                
                # Find target in combatants
                target_combatant = None
                for c in combatants:
                    if target.lower() in c.get('name', '').lower():
                        target_combatant = c
                        break
                
                if not target_combatant:
                    message = f"Target '{target}' not found in combat."
                else:
                    # Process attack using combat engine
                    result = self.combat_engine.process_attack(
                        combat_id=combat_id,
                        attacker_name=attacker_name,
                        target_name=target_combatant['name'],
                        attack_bonus=combatants[current_turn].get('attack_bonus', 5),
                        damage_dice=combatants[current_turn].get('damage_dice', '1d8+3')
                    )
                    
                    # Generate narrative description
                    narrative = await self.narrative_engine.describe_combat_round(
                        combat_id=combat_id,
                        last_action=result
                    )
                    
                    message = narrative
                    
                    events.append({
                        "type": "combat_action",
                        "action": action_type,
                        "attacker": attacker_name,
                        "target": target_combatant['name'],
                        "result": result
                    })
                    
                    # Check if combat ended
                    updated_state = self.combat_engine.get_combat_state(combat_id)
                    combat_ended = not updated_state.get('active', False)
                    
                    if combat_ended:
                        message += "\n\n🎉 **Combat Ended!**"
            
        except Exception as e:
            message = f"Error processing combat action: {e}"
            combat_ended = False
        
        return DMResponse(
            message=message,
            game_state_changed=True,
            scene_changed=False,
            combat_started=False,
            combat_ended=combat_ended,
            events=events
        )
    
    async def _handle_dialogue(self, game_session: GameSession, intent: Intent) -> DMResponse:
        """Handle NPC dialogue"""
        npc_name = intent.entities.get('npc_name', 'Mysterious Figure')
        player_message = intent.raw_message
        
        try:
            # Generate NPC response through narrative engine
            npc_response = await self.narrative_engine.generate_npc_dialogue(
                game_session=game_session,
                npc_name=npc_name,
                player_message=player_message
            )
            
            message = f"**{npc_name}:** {npc_response}"
            
            events = [{
                "type": "npc_dialogue",
                "npc": npc_name,
                "player_message": player_message,
                "npc_response": npc_response
            }]
            
        except Exception as e:
            message = f"Error generating NPC dialogue: {e}"
            events = []
        
        return DMResponse(
            message=message,
            game_state_changed=False,
            scene_changed=False,
            combat_started=False,
            combat_ended=False,
            events=events
        )
    
    async def _handle_exploration(self, game_session: GameSession, intent: Intent) -> DMResponse:
        """Handle exploration actions"""
        from backend.game.narrative_engine import PlayerChoice
        
        # Create player choice from intent
        choice = PlayerChoice(
            text=intent.raw_message,
            intent=intent.type.value,
            target=intent.entities.get('target'),
            location=intent.entities.get('location')
        )
        
        try:
            # Process through narrative engine
            scene = await self.narrative_engine.process_player_choice(
                game_session=game_session,
                choice=choice
            )
            
            message = scene.description
            events = []
            combat_started = False
            suggested_actions = scene.suggested_actions if hasattr(scene, 'suggested_actions') else []
            
            # Check for combat trigger
            if scene.detected_events:
                for event in scene.detected_events:
                    if event.get('type') == 'combat':
                        combat_started = True
                        message += "\n\n⚔️ **Combat Started!**"
                        events.append(event)
            
            # Add available choices (keep for backward compatibility)
            if scene.choices:
                message += "\n\n**What do you do?**"
                for i, c in enumerate(scene.choices, 1):
                    message += f"\n{i}. {c}"
            
        except Exception as e:
            message = f"Error processing exploration: {e}"
            combat_started = False
            events = []
            suggested_actions = []
        
        return DMResponse(
            message=message,
            game_state_changed=True,
            scene_changed=True,
            combat_started=combat_started,
            combat_ended=False,
            events=events,
            suggested_actions=suggested_actions
        )
    
    async def _handle_unknown(self, game_session: GameSession, user_message: str) -> DMResponse:
        """Handle unknown intents with general DM response"""
        # Generate contextual response using LLM
        game_context = self._build_game_context(game_session)
        
        # Build system prompt with conditional DM roll instructions
        system_prompt = """You are a D&D Dungeon Master. Generate a helpful response to the player's message.
Keep it concise (2-3 sentences). Stay in character as the DM. Guide the player on what they can do.

If appropriate, provide 2-3 suggested actions in JSON format at the end:

SUGGESTED_ACTIONS:
[
  {"action": "...", "roll": "Skill (d20 + X)", "dc": "15", "type": "skill_check"},
  {"action": "...", "roll": null, "dc": null, "type": "dialogue"}
]

Use this format only if the player needs guidance on what to do next."""

        # Add DM roll instructions if enabled
        if self.dm_roll_for_players:
            system_prompt += """

**IMPORTANT - YOU ROLL FOR PLAYERS:** The DM Roll setting is ENABLED. This means:
- When a character attempts a skill check, ability check, or saving throw, YOU should roll for them.
- Format roll results clearly: "**[Character Name]'s [Skill] Check**: Rolled d20+X = [RESULT]"
- Always roll for attack rolls and saving throws.
- Narrate the outcome dramatically after the roll.
- Don't ask the player to roll - you handle it immediately."""
        
        try:
            # Build prompt for unified LLM interface
            prompt = f"{system_prompt}\n\nGame context:\n{game_context}\n\nPlayer: {user_message}"
            
            # Call unified LLM interface
            message, metadata = await call_llm(
                prompt=prompt,
                provider=self.provider,
                model=self.model
            )
            
            # Try to extract suggested actions from response
            suggested_actions = []
            if "SUGGESTED_ACTIONS:" in message:
                parts = message.split("SUGGESTED_ACTIONS:")
                message = parts[0].strip()
                try:
                    import json
                    actions_json = parts[1].strip()
                    suggested_actions = json.loads(actions_json)
                except Exception:
                    pass  # Failed to parse, continue without actions
            
        except Exception:
            message = "I'm not sure what you mean. Try /help for available commands, or describe what you'd like to do in more detail."
            suggested_actions = []
        
        return DMResponse(
            message=message,
            game_state_changed=False,
            scene_changed=False,
            combat_started=False,
            combat_ended=False,
            events=[],
            suggested_actions=suggested_actions
        )
    
    def _build_game_context(self, game_session: GameSession) -> str:
        """
        Build game context for LLM prompts with CONDITIONAL character stats.
        
        Uses heuristic to determine if full character stats are needed based on
        recent conversation context. Saves tokens during roleplay-heavy scenes.
        """
        lines = []
        
        # Current scene
        current_scene = game_session.game_state.get('current_scene')
        if current_scene:
            lines.append(f"Location: {current_scene.get('location', 'Unknown')}")
            lines.append(f"Scene: {current_scene.get('description', '')[:200]}...")
        
        # Combat status
        combat_state = game_session.game_state.get('combat_state')
        in_combat = combat_state and combat_state.get('active')
        
        if in_combat:
            lines.append(f"Combat: Active (Round {combat_state.get('round', 1)})")
            combatants = combat_state.get('combatants', [])
            if combatants:
                lines.append(f"Combatants: {', '.join(c.get('name', 'Unknown') for c in combatants)}")
        
        # Determine if we need full character stats (combat always needs stats)
        session_id = game_session.id
        needs_full_stats = in_combat or self._should_include_stats(session_id)
        
        # Debug logging to show optimization in action
        if needs_full_stats:
            print(f"[DM Context] Including FULL character stats (combat={in_combat}, keywords detected)")
        else:
            print("[DM Context] Using COMPACT mode (names only) - no mechanical keywords detected")
        
        # Party members - full stats or names only
        if game_session.party_members:
            if needs_full_stats:
                # Include full character stats for mechanical interactions
                lines.append("\n=== PARTY CHARACTERS (FULL STATS) ===")
                lines.extend(self._format_full_party_stats(game_session))
            else:
                # Just include names and basic info for roleplay
                lines.append("\n=== PARTY ===")
                party_names = []
                for party_member in game_session.party_members:
                    if party_member.is_active and party_member.character:
                        char = party_member.character
                        if char.is_dnd:
                            char_class = char.dnd_class or "Adventurer"
                            level = char.dnd_level or 1
                            party_names.append(f"{char.name} ({char_class} {level})")
                        else:
                            party_names.append(char.name)
                lines.append(", ".join(party_names))
        
        return "\n".join(lines) if lines else "New game session"
    
    def _should_include_stats(self, session_id: int) -> bool:
        """
        Heuristic to determine if full character stats are needed.
        
        Checks recent conversation history for mechanical keywords that indicate
        the DM needs character stats (skill checks, attacks, spells, etc.)
        
        Args:
            session_id: Game session ID
            
        Returns:
            bool: True if stats should be included
        """
        # Get recent conversation history (last 3 messages)
        if session_id not in self.conversation_history:
            return True  # First message - include stats
        
        recent_messages = self.conversation_history[session_id][-6:]  # Last 3 user+assistant pairs
        
        # Keywords that indicate mechanical gameplay
        mechanical_keywords = [
            # Dice and checks (be specific to avoid false positives)
            ' roll ', ' check ', 'saving throw', ' save ', ' skill check',
            'd20', 'd12', 'd10', 'd8', 'd6', 'd4',
            # Combat actions
            ' attack ', ' hit ', ' damage ', ' strike ', ' shoot ', ' stab ', ' slash ',
            'attack roll', 'damage roll',
            # Spellcasting
            ' cast ', 'i cast', 'casting', ' spell ', ' cantrip', ' ritual', 'concentration',
            # Resources
            ' hp ', 'hit points', ' healing ', 'heal ', 'take damage',
            'spell slot', 'ki point', ' rage', 'channel divinity', 'action surge',
            # Stats
            ' ac ', 'armor class', ' initiative', ' modifier', ' bonus',
            'strength check', 'dexterity check', 'constitution check',
            'intelligence check', 'wisdom check', 'charisma check',
            'str check', 'dex check', 'con check', 'int check', 'wis check', 'cha check',
            # Combat state
            'in combat', ' fight ', ' battle ', 'combat begins', ' turn ', ' round ',
            'roll initiative',
            # Conditions
            'poisoned', 'stunned', 'paralyzed', 'prone', 'restrained', 'blinded',
            'charmed', 'deafened', 'frightened', 'grappled', 'incapacitated',
            # Items and equipment (be specific)
            'equip weapon', 'equip armor', 'drink potion', 'use potion',
            'attune', 'unequip'
        ]
        
        # Check last few messages for keywords
        combined_text = " ".join([msg['content'].lower() for msg in recent_messages])
        
        return any(keyword in combined_text for keyword in mechanical_keywords)
    
    def _format_full_party_stats(self, game_session: GameSession) -> list:
        """
        Format full character stats for all party members.
        
        Args:
            game_session: Game session with party members
            
        Returns:
            list: Lines of formatted character stats
        """
        lines = []
        
        for party_member in game_session.party_members:
            if not party_member.is_active:
                continue
                
            char = party_member.character
            if not char:
                continue
            
            # Character header
            lines.append(f"\n**{char.name}**")
            
            # Basic D&D info
            if char.is_dnd:
                char_class = char.dnd_class or "Unknown"
                level = char.dnd_level or 1
                species = char.dnd_species or "Unknown"
                lines.append(f"  Class: {char_class} {level}, Species: {species}")
            
            # Combat stats
            current_hp = party_member.current_hp if party_member.current_hp is not None else char.dnd_hit_points_current
            max_hp = party_member.max_hp if party_member.max_hp is not None else char.dnd_hit_points_max
            temp_hp = party_member.temp_hp or char.dnd_temporary_hp or 0
            ac = char.dnd_armor_class or 10
            
            if max_hp:
                lines.append(f"  HP: {current_hp}/{max_hp} (Temp: {temp_hp}) | AC: {ac}")
            
            # Ability scores and modifiers
            if char.dnd_ability_scores:
                scores = char.dnd_ability_scores
                mods = char.dnd_ability_modifiers or {}
                
                str_score = scores.get('strength', 10)
                str_mod = mods.get('strength', 0)
                dex_score = scores.get('dexterity', 10)
                dex_mod = mods.get('dexterity', 0)
                con_score = scores.get('constitution', 10)
                con_mod = mods.get('constitution', 0)
                int_score = scores.get('intelligence', 10)
                int_mod = mods.get('intelligence', 0)
                wis_score = scores.get('wisdom', 10)
                wis_mod = mods.get('wisdom', 0)
                cha_score = scores.get('charisma', 10)
                cha_mod = mods.get('charisma', 0)
                
                lines.append(f"  STR: {str_score} ({str_mod:+d}) | DEX: {dex_score} ({dex_mod:+d}) | CON: {con_score} ({con_mod:+d})")
                lines.append(f"  INT: {int_score} ({int_mod:+d}) | WIS: {wis_score} ({wis_mod:+d}) | CHA: {cha_score} ({cha_mod:+d})")
            
            # Key combat info
            prof_bonus = char.dnd_proficiency_bonus or "+2"
            initiative = char.dnd_initiative or "+0"
            speed = char.dnd_speed or 30
            lines.append(f"  Proficiency: {prof_bonus} | Initiative: {initiative} | Speed: {speed} ft")
            
            # Spellcasting (if applicable)
            if char.dnd_spellcasting:
                spell_info = char.dnd_spellcasting
                spell_ability = spell_info.get('ability', 'Unknown')
                spell_dc = spell_info.get('dc', 10)
                spell_attack = spell_info.get('attack', 0)
                lines.append(f"  Spellcasting: {spell_ability} | DC: {spell_dc} | Attack: +{spell_attack}")
                
                # Spell slots
                if 'slots' in spell_info:
                    slots = spell_info['slots']
                    slot_strs = []
                    for level, slot_info in sorted(slots.items()):
                        if isinstance(slot_info, dict):
                            current = slot_info.get('current', 0)
                            max_slots = slot_info.get('max', 0)
                            if max_slots > 0:
                                slot_strs.append(f"{level}: {current}/{max_slots}")
                    if slot_strs:
                        lines.append(f"  Spell Slots: {', '.join(slot_strs)}")
            
            # Conditions
            conditions = party_member.conditions or char.dnd_conditions or []
            if conditions:
                lines.append(f"  Conditions: {', '.join(conditions)}")
            
            # Skills (only show proficiencies)
            if char.dnd_skills:
                skills_str = ', '.join(char.dnd_skills[:5])  # Limit to first 5
                if len(char.dnd_skills) > 5:
                    skills_str += f" (+{len(char.dnd_skills) - 5} more)"
                lines.append(f"  Skill Proficiencies: {skills_str}")
        
        return lines
    
    def clear_conversation_history(self, session_id: int):
        """Clear conversation history for a session"""
        if session_id in self.conversation_history:
            del self.conversation_history[session_id]
    
    # ============================================================================
    # D&D CONTENT LOOKUP - Phase 4 Integration
    # ============================================================================
    
    async def _lookup_spell(self, spell_name: str) -> str:
        """
        Look up D&D spell details via MCP.
        
        Args:
            spell_name: Name of spell to look up
            
        Returns:
            str: Formatted spell information
        """
        try:
            spell_data = await self.mcp_client.get_spell(spell_name)
            
            if not spell_data or "error" in spell_data:
                return f"❌ Spell '{spell_name}' not found in D&D 5e database."
            
            spell = spell_data.get("spell", {})
            
            # Extract key details
            name = spell.get("name", spell_name)
            level = spell.get("level", 0)
            school = spell.get("school", {}).get("name", "")
            casting_time = spell.get("casting_time", "")
            spell_range = spell.get("range", "")
            components = spell.get("components", [])
            duration = spell.get("duration", "")
            desc = spell.get("desc", [""])
            
            # Format level
            level_str = "Cantrip" if level == 0 else f"Level {level}"
            
            # Format components
            components_str = ", ".join(components) if components else "None"
            
            # Build formatted response
            lines = [
                f"📜 **{name}**",
                f"*{level_str} {school}*",
                "",
                f"**Casting Time:** {casting_time}",
                f"**Range:** {spell_range}",
                f"**Components:** {components_str}",
                f"**Duration:** {duration}",
                "",
            ]
            
            # Add description (first paragraph only)
            if desc and desc[0]:
                description = desc[0]
                if len(description) > 300:
                    description = description[:297] + "..."
                lines.append(f"**Description:** {description}")
            
            # Add damage if available
            if spell.get("damage"):
                damage_type = spell["damage"].get("damage_type", {}).get("name", "")
                damage_at_slot = spell["damage"].get("damage_at_slot_level", {})
                if damage_at_slot:
                    first_level = list(damage_at_slot.values())[0]
                    lines.append(f"**Damage:** {first_level} {damage_type}")
            
            # Add saving throw if available
            if spell.get("dc"):
                save_type = spell["dc"].get("dc_type", {}).get("name", "")
                lines.append(f"**Save:** {save_type} DC")
            
            return "\n".join(lines)
        
        except Exception as e:
            return f"❌ Error looking up spell '{spell_name}': {e}"
    
    async def _lookup_monster(self, monster_name: str) -> str:
        """
        Look up D&D monster stats via MCP.
        
        Args:
            monster_name: Name of monster to look up
            
        Returns:
            str: Formatted monster stat block
        """
        try:
            monster_data = await self.mcp_client.get_monster(monster_name)
            
            if not monster_data or "error" in monster_data:
                return f"❌ Monster '{monster_name}' not found in D&D 5e database."
            
            monster = monster_data.get("monster", {})
            
            # Extract key stats
            name = monster.get("name", monster_name)
            size = monster.get("size", "")
            monster_type = monster.get("type", "")
            alignment = monster.get("alignment", "")
            ac = monster.get("armor_class", [{}])[0].get("value", 10) if monster.get("armor_class") else 10
            hp = monster.get("hit_points", 0)
            hp_dice = monster.get("hit_points_roll", "")
            cr = monster.get("challenge_rating", 0)
            
            # Ability scores
            str_score = monster.get("strength", 10)
            dex_score = monster.get("dexterity", 10)
            con_score = monster.get("constitution", 10)
            int_score = monster.get("intelligence", 10)
            wis_score = monster.get("wisdom", 10)
            cha_score = monster.get("charisma", 10)
            
            # Calculate modifiers
            def mod(score): return (score - 10) // 2
            str_mod = f"+{mod(str_score)}" if mod(str_score) >= 0 else str(mod(str_score))
            dex_mod = f"+{mod(dex_score)}" if mod(dex_score) >= 0 else str(mod(dex_score))
            con_mod = f"+{mod(con_score)}" if mod(con_score) >= 0 else str(mod(con_score))
            
            # Build stat block
            lines = [
                f"⚔️ **{name}**",
                f"*{size} {monster_type}, {alignment}*",
                "",
                f"**AC:** {ac} | **HP:** {hp} ({hp_dice}) | **CR:** {cr}",
                "",
                f"**STR:** {str_score} ({str_mod}) | **DEX:** {dex_score} ({dex_mod}) | **CON:** {con_score} ({con_mod})",
                f"**INT:** {int_score} ({mod(int_score):+d}) | **WIS:** {wis_score} ({mod(wis_score):+d}) | **CHA:** {cha_score} ({mod(cha_score):+d})",
                "",
            ]
            
            # Add speed
            speed = monster.get("speed", {})
            if speed:
                speed_strs = []
                for move_type, distance in speed.items():
                    if isinstance(distance, dict):
                        distance = distance.get("distance", 0)
                    if move_type == "walk":
                        speed_strs.append(f"{distance} ft")
                    else:
                        speed_strs.append(f"{move_type} {distance} ft")
                lines.append(f"**Speed:** {', '.join(speed_strs)}")
            
            # Add actions (first 2 only)
            actions = monster.get("actions", [])
            if actions:
                lines.append("")
                lines.append("**Actions:**")
                for action in actions[:2]:
                    action_name = action.get("name", "Unknown")
                    action_desc = action.get("desc", "")
                    if action_desc:
                        short_desc = action_desc[:150] + "..." if len(action_desc) > 150 else action_desc
                        lines.append(f"• **{action_name}:** {short_desc}")
            
            return "\n".join(lines)
        
        except Exception as e:
            return f"❌ Error looking up monster '{monster_name}': {e}"
    
    async def _lookup_item(self, item_name: str) -> str:
        """
        Look up D&D magic item via MCP.
        
        Args:
            item_name: Name of magic item to look up
            
        Returns:
            str: Formatted item information
        """
        try:
            # Search for item (MCP doesn't have direct get_item, use search_all)
            search_data = await self.mcp_client.search_all(item_name)
            
            if not search_data or "error" in search_data:
                return f"❌ Item '{item_name}' not found in D&D 5e database."
            
            # Find magic items in results
            magic_items = search_data.get("results", {}).get("magic-items", [])
            
            if not magic_items:
                return f"❌ No magic items found matching '{item_name}'."
            
            # Take first match
            item = magic_items[0]
            name = item.get("name", item_name)
            url = item.get("url", "")
            
            # For now, just return basic info
            # Full item details would require another API call
            lines = [
                f"💎 **{name}**",
                "*Magic Item*",
                "",
                "Use `/spell` or `/monster` for full stat blocks.",
                f"Item details: {url}"
            ]
            
            return "\n".join(lines)
        
        except Exception as e:
            return f"❌ Error looking up item '{item_name}': {e}"
    
    async def _detect_spell_cast(self, message: str) -> tuple[bool, str]:
        """
        Detect if message contains spell casting and extract spell name.
        
        Looks for patterns like:
        - "I cast Fireball"
        - "Casting Magic Missile at the goblin"
        - "I use Cure Wounds on the fighter"
        
        Args:
            message: User message
            
        Returns:
            tuple[bool, str]: (detected, spell_name)
        """
        msg_lower = message.lower()
        
        # Spell casting patterns
        cast_patterns = [
            'i cast ',
            'casting ',
            'i use ',
            'using ',
            'i throw ',
            'i shoot ',
        ]
        
        for pattern in cast_patterns:
            if pattern in msg_lower:
                # Extract spell name (next 1-3 words after pattern)
                idx = msg_lower.index(pattern) + len(pattern)
                remaining = message[idx:].strip()
                
                # Take up to 3 words (most spells are 1-3 words)
                words = remaining.split()[:3]
                
                # Try each combination
                for i in range(len(words), 0, -1):
                    potential_spell = ' '.join(words[:i])
                    # Remove trailing punctuation
                    potential_spell = potential_spell.rstrip('.,!?;:')
                    
                    # Return potential spell name
                    return True, potential_spell.title()
        
        return False, ""
    
    async def _detect_monster_mention(self, message: str) -> tuple[bool, str]:
        """
        Detect if message mentions a monster spawn.
        
        Looks for patterns like:
        - "A goblin appears"
        - "Suddenly, an orc attacks"
        - "Three zombies shamble forward"
        
        Args:
            message: User message
            
        Returns:
            tuple[bool, str]: (detected, monster_name)
        """
        msg_lower = message.lower()
        
        # Monster spawn patterns
        spawn_patterns = [
            ' appears',
            ' emerges',
            ' attacks',
            ' jumps out',
            ' approaches',
            ' shambles',
            ' swoops',
            ' charges',
        ]
        
        for pattern in spawn_patterns:
            if pattern in msg_lower:
                # Look for article + noun before pattern
                idx = msg_lower.index(pattern)
                before = message[:idx].strip()
                
                # Extract last 1-3 words
                words = before.split()[-3:]
                
                # Try to find monster name
                for i in range(len(words), 0, -1):
                    potential_monster = ' '.join(words[i-1:])
                    # Remove articles
                    potential_monster = potential_monster.replace('a ', '').replace('an ', '').replace('the ', '')
                    potential_monster = potential_monster.rstrip('.,!?;:')
                    
                    if potential_monster and len(potential_monster) > 2:
                        return True, potential_monster.title()
        
        return False, ""
