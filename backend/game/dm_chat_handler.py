"""
DM Chat Handler - Natural Language Interface for AI Dungeon Master

This module provides a chat-based interface that connects all game systems
(dice, combat, narrative) through natural language processing powered by LM Studio.

Architecture:
1. Process player messages through intent classification (exploration/combat/dialogue/command)
2. Route to appropriate game system based on intent
3. Generate contextual DM responses using LLM
4. Maintain conversation history and game state consistency
5. Log all interactions for narrative continuity

LM Studio Integration:
- Uses local LLM at http://100.120.44.114:1234
- OpenAI-compatible API
- Async HTTP client with retry logic
- JSON-mode responses for structured parsing
"""

import json
import asyncio
import aiohttp
from typing import List, Dict, Any
from dataclasses import dataclass
from enum import Enum

from sqlalchemy.orm import Session
from backend.models import GameSession
from backend.game.dice_roller import DiceRoller
from backend.game.combat_engine import CombatEngine
from backend.game.narrative_engine import NarrativeEngine


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


class AsyncLMStudioClient:
    """Async LM Studio client for AI DM chat"""
    
    def __init__(self, base_url: str = "http://100.120.44.114:1234/v1", timeout: int = 120):
        self.base_url = base_url.rstrip('/')
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.max_retries = 5
        
    async def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        max_tokens: int = 512,
        temperature: float = 0.2,
        json_mode: bool = False
    ) -> Dict[str, Any]:
        """Send chat completion request with retry logic"""
        url = f"{self.base_url}/chat/completions"
        
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        
        if json_mode:
            payload["response_format"] = {"type": "json_object"}
        
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                async with aiohttp.ClientSession(timeout=self.timeout) as session:
                    async with session.post(url, json=payload) as response:
                        response.raise_for_status()
                        return await response.json()
                        
            except Exception as e:
                last_error = e
                sleep_duration = min(10, 1 + attempt * 2)
                print(f"LM Studio request failed (attempt {attempt + 1}/{self.max_retries}): {e}")
                print(f"Retrying in {sleep_duration}s...")
                await asyncio.sleep(sleep_duration)
        
        raise last_error


class DMChatHandler:
    """
    Main AI DM chat interface that orchestrates all game systems.
    
    This handler acts as the "brain" of the AI DM, processing natural language
    player input and coordinating responses across dice rolling, combat, narrative,
    and dialogue systems.
    """
    
    def __init__(
        self,
        db: Session,
        lm_studio_url: str = "http://100.120.44.114:1234/v1",
        model: str = "local-model"
    ):
        """
        Initialize DM chat handler with all game system dependencies.
        
        Args:
            db: Database session for state persistence
            lm_studio_url: URL to LM Studio server
            model: Model identifier for LM Studio
        """
        self.db = db
        self.lm_client = AsyncLMStudioClient(base_url=lm_studio_url)
        self.model = model
        
        # Initialize game system components
        self.dice_roller = DiceRoller()
        self.combat_engine = CombatEngine(db)
        self.narrative_engine = NarrativeEngine(db)
        
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
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Game context:\n{game_context}\n\nPlayer message: {user_message}"}
        ]
        
        try:
            response = await self.lm_client.chat(
                model=self.model,
                messages=messages,
                max_tokens=256,
                temperature=0.1,
                json_mode=True
            )
            
            content = response['choices'][0]['message']['content']
            parsed = json.loads(content)
            
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
        
        else:
            message = f"Unknown command: {command}\nAvailable: /roll, /hp, /status"
        
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
            
            # Check for combat trigger
            if scene.detected_events:
                for event in scene.detected_events:
                    if event.get('type') == 'combat':
                        combat_started = True
                        message += "\n\n⚔️ **Combat Started!**"
                        events.append(event)
            
            # Add available choices
            if scene.choices:
                message += "\n\n**What do you do?**"
                for i, c in enumerate(scene.choices, 1):
                    message += f"\n{i}. {c}"
            
        except Exception as e:
            message = f"Error processing exploration: {e}"
            combat_started = False
            events = []
        
        return DMResponse(
            message=message,
            game_state_changed=True,
            scene_changed=True,
            combat_started=combat_started,
            combat_ended=False,
            events=events
        )
    
    async def _handle_unknown(self, game_session: GameSession, user_message: str) -> DMResponse:
        """Handle unknown intents with general DM response"""
        # Generate contextual response using LLM
        game_context = self._build_game_context(game_session)
        
        system_prompt = """You are a D&D Dungeon Master. Generate a helpful response to the player's message.
Keep it concise (2-3 sentences). Stay in character as the DM. Guide the player on what they can do."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Game context:\n{game_context}\n\nPlayer: {user_message}"}
        ]
        
        try:
            response = await self.lm_client.chat(
                model=self.model,
                messages=messages,
                max_tokens=256,
                temperature=0.7
            )
            
            message = response['choices'][0]['message']['content']
            
        except Exception:
            message = "I'm not sure what you mean. Try /help for available commands, or describe what you'd like to do in more detail."
        
        return DMResponse(
            message=message,
            game_state_changed=False,
            scene_changed=False,
            combat_started=False,
            combat_ended=False,
            events=[]
        )
    
    def _build_game_context(self, game_session: GameSession) -> str:
        """Build concise game context for LLM prompts"""
        lines = []
        
        # Current scene
        current_scene = game_session.game_state.get('current_scene')
        if current_scene:
            lines.append(f"Location: {current_scene.get('location', 'Unknown')}")
            lines.append(f"Scene: {current_scene.get('description', '')[:200]}...")
        
        # Combat status
        combat_state = game_session.game_state.get('combat_state')
        if combat_state and combat_state.get('active'):
            lines.append(f"Combat: Active (Round {combat_state.get('round', 1)})")
            combatants = combat_state.get('combatants', [])
            if combatants:
                lines.append(f"Combatants: {', '.join(c.get('name', 'Unknown') for c in combatants)}")
        
        # Party status
        party_status = game_session.game_state.get('party_status', {})
        if party_status:
            lines.append(f"Party: {', '.join(party_status.keys())}")
        
        return "\n".join(lines) if lines else "New game session"
    
    def clear_conversation_history(self, session_id: int):
        """Clear conversation history for a session"""
        if session_id in self.conversation_history:
            del self.conversation_history[session_id]
