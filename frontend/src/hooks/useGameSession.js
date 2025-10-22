/**
 * useGameSession Hook - Manages AI DM Game Session State
 * 
 * Provides centralized state management for:
 * - Game session lifecycle (create, load, update)
 * - Chat messages and DM responses
 * - Combat state tracking
 * - Party member status
 * - Scene progression
 * - Event history
 */

import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

export function useGameSession(initialGameSessionId = null) {
  // Core game state
  const [gameSessionId, setGameSessionId] = useState(initialGameSessionId);
  const [chatSessionId, setChatSessionId] = useState(null);
  const [gameState, setGameState] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Chat state
  const [messages, setMessages] = useState([]);
  const [isGenerating, setIsGenerating] = useState(false);

  // Game-specific state
  const [currentScene, setCurrentScene] = useState(null);
  const [combatState, setCombatState] = useState(null);
  const [partyStatus, setPartyStatus] = useState({});
  const [eventLog, setEventLog] = useState([]);

  /**
   * Create a new game session
   */
  const createGameSession = useCallback(async (title = 'New Adventure', partyMembers = []) => {
    setLoading(true);
    setError(null);

    try {
      // Create game session
      const gameRes = await axios.post(`${API_BASE}/game/sessions`, {
        title,
        game_state: {
          party_status: partyMembers.reduce((acc, member) => ({
            ...acc,
            [member.name]: {
              character_id: member.id,
              current_hp: member.max_hp || 20,
              max_hp: member.max_hp || 20,
              conditions: []
            }
          }), {})
        }
      });

      const newGameSessionId = gameRes.data.id;
      setGameSessionId(newGameSessionId);
      setGameState(gameRes.data.game_state);
      setPartyStatus(gameRes.data.game_state?.party_status || {});

      // Create associated chat session
      const chatRes = await axios.post(`${API_BASE}/chat/sessions`, {
        title: `${title} - DM Chat`,
        provider: 'http://100.120.44.114:1234/v1',
        model: 'local-model',
        include_context: false
      });

      setChatSessionId(chatRes.data.id);

      return { gameSessionId: newGameSessionId, chatSessionId: chatRes.data.id };
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Load existing game session
   */
  const loadGameSession = useCallback(async (gameId, chatId) => {
    setLoading(true);
    setError(null);

    try {
      // Load game session
      const gameRes = await axios.get(`${API_BASE}/game/sessions/${gameId}`);
      setGameSessionId(gameId);
      setGameState(gameRes.data.game_state);
      setCurrentScene(gameRes.data.game_state?.current_scene);
      setCombatState(gameRes.data.game_state?.combat_state);
      setPartyStatus(gameRes.data.game_state?.party_status || {});

      // Load chat session and messages
      if (chatId) {
        const chatRes = await axios.get(`${API_BASE}/chat/sessions/${chatId}`);
        setChatSessionId(chatId);
        setMessages(chatRes.data.messages || []);
      }

      // Load event log
      const eventsRes = await axios.get(`${API_BASE}/game/sessions/${gameId}/events`);
      setEventLog(eventsRes.data.events || []);

      return gameRes.data;
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Send message to DM and get response
   */
  const sendMessage = useCallback(async (content) => {
    if (!gameSessionId || !chatSessionId) {
      throw new Error('Game and chat sessions must be initialized');
    }

    setIsGenerating(true);
    setError(null);

    try {
      // Add user message
      const userMsgRes = await axios.post(
        `${API_BASE}/chat/sessions/${chatSessionId}/messages`,
        { role: 'user', content }
      );

      setMessages(prev => [...prev, userMsgRes.data]);

      // Generate DM response
      const dmRes = await axios.post(
        `${API_BASE}/chat/sessions/${chatSessionId}/game-chat?game_session_id=${gameSessionId}`
      );

      // Update messages
      setMessages(prev => [...prev, dmRes.data.assistant_message]);

      // Update game state
      setGameState(dmRes.data.game_state);
      setCurrentScene(dmRes.data.game_state?.current_scene);
      setCombatState(dmRes.data.game_state?.combat_state);
      setPartyStatus(dmRes.data.game_state?.party_status || {});

      // Add events to log
      if (dmRes.data.dm_response?.events) {
        setEventLog(prev => [...prev, ...dmRes.data.dm_response.events]);
      }

      return dmRes.data;
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
      throw err;
    } finally {
      setIsGenerating(false);
    }
  }, [gameSessionId, chatSessionId]);

  /**
   * Roll dice
   */
  const rollDice = useCallback(async (notation) => {
    if (!gameSessionId) {
      throw new Error('Game session must be initialized');
    }

    try {
      const res = await axios.post(
        `${API_BASE}/game/sessions/${gameSessionId}/roll`,
        { notation }
      );

      // Add roll to event log
      setEventLog(prev => [...prev, {
        type: 'dice_roll',
        notation,
        result: res.data,
        timestamp: new Date().toISOString()
      }]);

      return res.data;
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
      throw err;
    }
  }, [gameSessionId]);

  /**
   * Start combat
   */
  const startCombat = useCallback(async (combatants) => {
    if (!gameSessionId) {
      throw new Error('Game session must be initialized');
    }

    try {
      const res = await axios.post(
        `${API_BASE}/game/sessions/${gameSessionId}/combat`,
        { combatants }
      );

      setCombatState(res.data);
      return res.data;
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
      throw err;
    }
  }, [gameSessionId]);

  /**
   * Process attack in combat
   */
  const processAttack = useCallback(async (attackerName, targetName, attackBonus, damageDice) => {
    if (!gameSessionId) {
      throw new Error('Game session must be initialized');
    }

    try {
      const res = await axios.post(
        `${API_BASE}/game/sessions/${gameSessionId}/combat/attack`,
        {
          attacker_name: attackerName,
          target_name: targetName,
          attack_bonus: attackBonus,
          damage_dice: damageDice
        }
      );

      // Refresh combat state
      const combatRes = await axios.get(
        `${API_BASE}/game/sessions/${gameSessionId}/combat`
      );
      setCombatState(combatRes.data);

      return res.data;
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
      throw err;
    }
  }, [gameSessionId]);

  /**
   * Next turn in combat
   */
  const nextTurn = useCallback(async () => {
    if (!gameSessionId) {
      throw new Error('Game session must be initialized');
    }

    try {
      const res = await axios.post(
        `${API_BASE}/game/sessions/${gameSessionId}/combat/next-turn`
      );

      setCombatState(res.data);
      return res.data;
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
      throw err;
    }
  }, [gameSessionId]);

  /**
   * End combat
   */
  const endCombat = useCallback(async () => {
    if (!gameSessionId) {
      throw new Error('Game session must be initialized');
    }

    try {
      const res = await axios.post(
        `${API_BASE}/game/sessions/${gameSessionId}/combat/end`
      );

      setCombatState(null);
      return res.data;
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
      throw err;
    }
  }, [gameSessionId]);

  /**
   * Start new scene
   */
  const startScene = useCallback(async (adventureType, location) => {
    if (!gameSessionId) {
      throw new Error('Game session must be initialized');
    }

    try {
      const res = await axios.post(
        `${API_BASE}/game/sessions/${gameSessionId}/scene/start`,
        { adventure_type: adventureType, location }
      );

      setCurrentScene(res.data.scene);
      return res.data;
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
      throw err;
    }
  }, [gameSessionId]);

  return {
    // State
    gameSessionId,
    chatSessionId,
    gameState,
    messages,
    currentScene,
    combatState,
    partyStatus,
    eventLog,
    loading,
    error,
    isGenerating,

    // Actions
    createGameSession,
    loadGameSession,
    sendMessage,
    rollDice,
    startCombat,
    processAttack,
    nextTurn,
    endCombat,
    startScene,

    // Helpers
    isInCombat: combatState?.active === true,
    currentTurnCombatant: combatState?.active 
      ? combatState.combatants?.[combatState.current_turn]
      : null,
  };
}
