"""
D&D MCP Client - Python wrapper for Node.js MCP server

This service communicates with the D&D MCP proxy server to fetch official
D&D 5e content and format it for use in our AI DM system.

Architecture:
- Node.js MCP proxy server runs on port 3001
- Python client sends HTTP requests to proxy endpoints
- Results cached in memory for performance (1 hour TTL)
- Fallback to existing RAG system if MCP unavailable

Usage:
    client = DndMcpClient()
    spell = await client.get_spell("fireball")
    monsters = await client.find_monsters_by_cr(0, 5)
"""

import aiohttp
import asyncio
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from functools import wraps
import logging

logger = logging.getLogger(__name__)


class DndMcpClientError(Exception):
    """Base exception for MCP client errors"""
    pass


class DndMcpConnectionError(DndMcpClientError):
    """Raised when unable to connect to MCP proxy"""
    pass


class DndMcpTimeoutError(DndMcpClientError):
    """Raised when request times out"""
    pass


def cache_result(ttl_minutes: int = 60):
    """Decorator to cache async function results"""
    def decorator(func):
        cache = {}
        cache_times = {}
        
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Check if cached and not expired
            if cache_key in cache:
                cache_time = cache_times.get(cache_key)
                if cache_time and datetime.now() - cache_time < timedelta(minutes=ttl_minutes):
                    logger.debug(f"Cache hit for {cache_key}")
                    return cache[cache_key]
            
            # Call function and cache result
            result = await func(self, *args, **kwargs)
            cache[cache_key] = result
            cache_times[cache_key] = datetime.now()
            logger.debug(f"Cached result for {cache_key}")
            
            return result
        
        return wrapper
    return decorator


class DndMcpClient:
    """
    Client for interacting with D&D MCP proxy server.
    
    Provides async methods to query official D&D 5e content including
    spells, monsters, equipment, magic items, and more.
    """
    
    def __init__(
        self,
        base_url: str = "http://localhost:3001",
        timeout: int = 30,
        max_retries: int = 3
    ):
        """
        Initialize DnD MCP client.
        
        Args:
            base_url: Base URL of MCP proxy server
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.max_retries = max_retries
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(timeout=self.timeout)
        return self.session
    
    async def close(self):
        """Close the client session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request to MCP proxy with retry logic.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            json_data: JSON body data for POST requests
            params: Query parameters for GET requests
            
        Returns:
            Response data as dictionary
            
        Raises:
            DndMcpConnectionError: If unable to connect
            DndMcpTimeoutError: If request times out
        """
        url = f"{self.base_url}{endpoint}"
        session = await self._get_session()
        
        for attempt in range(self.max_retries):
            try:
                async with session.request(
                    method,
                    url,
                    json=json_data,
                    params=params
                ) as response:
                    if response.status == 503:
                        error_data = await response.json()
                        raise DndMcpConnectionError(
                            f"MCP proxy not connected: {error_data.get('detail', 'Unknown error')}"
                        )
                    
                    response.raise_for_status()
                    data = await response.json()
                    
                    # Extract content from MCP response format
                    if 'content' in data and isinstance(data['content'], list):
                        if len(data['content']) > 0 and 'text' in data['content'][0]:
                            # Parse the text content as JSON
                            try:
                                return json.loads(data['content'][0]['text'])
                            except json.JSONDecodeError:
                                return data
                    
                    return data
                    
            except asyncio.TimeoutError:
                if attempt == self.max_retries - 1:
                    raise DndMcpTimeoutError(f"Request to {endpoint} timed out after {self.max_retries} attempts")
                logger.warning(f"Request timeout, attempt {attempt + 1}/{self.max_retries}")
                await asyncio.sleep(1 * (attempt + 1))  # Exponential backoff
                
            except aiohttp.ClientError as e:
                if attempt == self.max_retries - 1:
                    raise DndMcpConnectionError(f"Failed to connect to MCP proxy: {str(e)}")
                logger.warning(f"Connection error, attempt {attempt + 1}/{self.max_retries}: {e}")
                await asyncio.sleep(1 * (attempt + 1))
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check MCP proxy server health.
        
        Returns:
            Health status dictionary
        """
        return await self._make_request('GET', '/health')
    
    async def check_api_health(self) -> Dict[str, Any]:
        """
        Check D&D 5e API health.
        
        Returns:
            API health information
        """
        return await self._make_request('GET', '/api/health')
    
    @cache_result(ttl_minutes=60)
    async def search_all(self, query: str) -> Dict[str, Any]:
        """
        Search across all D&D categories.
        
        Args:
            query: Search query string
            
        Returns:
            Dictionary with search results organized by category
            
        Example:
            results = await client.search_all("fireball")
            spells = results.get('spells', [])
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        
        return await self._make_request(
            'POST',
            '/api/search',
            json_data={'query': query}
        )
    
    @cache_result(ttl_minutes=120)
    async def get_spell(self, spell_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed spell information.
        
        Args:
            spell_name: Name of the spell
            
        Returns:
            Spell details dictionary or None if not found
            
        Example:
            spell = await client.get_spell("fireball")
            if spell:
                print(f"Level: {spell['level']}, School: {spell['school']}")
        """
        results = await self._make_request('GET', f'/api/spell/{spell_name}')
        
        # Extract spell from search results
        if 'spells' in results and len(results['spells']) > 0:
            return results['spells'][0]
        
        return None
    
    @cache_result(ttl_minutes=120)
    async def get_monster(self, monster_name: str) -> Optional[Dict[str, Any]]:
        """
        Get monster stat block.
        
        Args:
            monster_name: Name of the monster
            
        Returns:
            Monster details dictionary or None if not found
            
        Example:
            monster = await client.get_monster("goblin")
            if monster:
                print(f"CR: {monster['challenge_rating']}, AC: {monster['armor_class']}")
        """
        results = await self._make_request('GET', f'/api/monster/{monster_name}')
        
        # Extract monster from search results
        if 'monsters' in results and len(results['monsters']) > 0:
            return results['monsters'][0]
        
        return None
    
    @cache_result(ttl_minutes=60)
    async def filter_spells_by_level(
        self,
        min_level: int = 0,
        max_level: int = 9,
        school: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Filter spells by level and optionally by school.
        
        Args:
            min_level: Minimum spell level (0-9)
            max_level: Maximum spell level (0-9)
            school: Magic school (abjuration, conjuration, etc.)
            
        Returns:
            List of spell dictionaries
            
        Example:
            cantrips = await client.filter_spells_by_level(0, 0)
            evocation_spells = await client.filter_spells_by_level(1, 5, "evocation")
        """
        params = {
            'min_level': min_level,
            'max_level': max_level
        }
        
        if school:
            params['school'] = school
        
        results = await self._make_request('GET', '/api/spells', params=params)
        
        # Extract spells list from results
        if 'spells' in results:
            return results['spells']
        
        return []
    
    @cache_result(ttl_minutes=60)
    async def find_monsters_by_cr(
        self,
        min_cr: float = 0,
        max_cr: float = 30
    ) -> List[Dict[str, Any]]:
        """
        Find monsters within a challenge rating range.
        
        Args:
            min_cr: Minimum challenge rating
            max_cr: Maximum challenge rating
            
        Returns:
            List of monster dictionaries
            
        Example:
            easy_monsters = await client.find_monsters_by_cr(0, 2)
            boss_monsters = await client.find_monsters_by_cr(10, 15)
        """
        params = {
            'min_cr': min_cr,
            'max_cr': max_cr
        }
        
        results = await self._make_request('GET', '/api/monsters', params=params)
        
        # Extract monsters list from results
        if 'monsters' in results:
            return results['monsters']
        
        return []
    
    @cache_result(ttl_minutes=120)
    async def search_equipment_by_cost(
        self,
        max_cost: float = 100,
        cost_unit: str = 'gp'
    ) -> List[Dict[str, Any]]:
        """
        Search for equipment within a cost limit.
        
        Args:
            max_cost: Maximum cost value
            cost_unit: Currency unit (gp, sp, cp)
            
        Returns:
            List of equipment dictionaries
            
        Example:
            cheap_items = await client.search_equipment_by_cost(10, 'gp')
        """
        params = {
            'max_cost': max_cost,
            'cost_unit': cost_unit
        }
        
        results = await self._make_request('GET', '/api/equipment', params=params)
        
        # Extract equipment list from results
        if 'equipment' in results:
            return results['equipment']
        
        return []
    
    async def verify_statement(
        self,
        statement: str,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Verify a D&D statement against official content.
        
        Args:
            statement: Statement to verify
            category: Optional category to focus search
            
        Returns:
            Verification results with confidence level
            
        Example:
            result = await client.verify_statement("Fireball is a 3rd-level evocation spell")
            print(f"Verified: {result['verified']}, Confidence: {result['confidence']}")
        """
        json_data = {
            'statement': statement
        }
        
        if category:
            json_data['category'] = category
        
        return await self._make_request('POST', '/api/verify', json_data=json_data)
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()


# Singleton instance for global use
_client_instance: Optional[DndMcpClient] = None


def get_dnd_mcp_client() -> DndMcpClient:
    """
    Get singleton DnD MCP client instance.
    
    Returns:
        Shared DndMcpClient instance
    """
    global _client_instance
    if _client_instance is None:
        _client_instance = DndMcpClient()
    return _client_instance


# Example usage
if __name__ == "__main__":
    async def test_client():
        """Test the MCP client"""
        async with DndMcpClient() as client:
            # Check health
            print("Checking health...")
            health = await client.health_check()
            print(f"Health: {health}")
            
            # Search for fireball
            print("\nSearching for 'fireball'...")
            results = await client.search_all("fireball")
            print(f"Found {len(results.get('spells', []))} spells")
            
            # Get spell details
            print("\nGetting spell details...")
            spell = await client.get_spell("fireball")
            if spell:
                print(f"Fireball: Level {spell.get('level')}, School: {spell.get('school')}")
            
            # Find low-level monsters
            print("\nFinding CR 0-2 monsters...")
            monsters = await client.find_monsters_by_cr(0, 2)
            print(f"Found {len(monsters)} monsters")
            
            # Get cantrips
            print("\nGetting cantrips...")
            cantrips = await client.filter_spells_by_level(0, 0)
            print(f"Found {len(cantrips)} cantrips")
    
    asyncio.run(test_client())
