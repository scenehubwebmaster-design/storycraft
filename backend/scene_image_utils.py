"""Scene Image Generation Utilities

Helpers for extracting visual context from DM responses and generating
scene images using Stable Diffusion.
"""

import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)


def extract_scene_prompt(dm_response: str, max_length: int = 200) -> Optional[str]:
    """
    Extract a visual scene description from DM response text.
    
    Analyzes the DM's narrative to identify:
    - Location/setting descriptions
    - Character appearances and actions
    - Atmospheric elements (lighting, weather, mood)
    - Key visual details
    
    Args:
        dm_response: The DM's narrative text
        max_length: Maximum prompt length (default 200 chars)
        
    Returns:
        A concise image prompt suitable for Stable Diffusion, or None if no visual content
    """
    if not dm_response or len(dm_response.strip()) < 20:
        return None
    
    # Remove common non-visual elements
    text = dm_response
    
    # Remove dice roll syntax
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'\d+d\d+', '', text)
    
    # Remove mechanical notes
    text = re.sub(r'\(DC \d+\)', '', text)
    text = re.sub(r'\(AC \d+\)', '', text)
    text = re.sub(r'\d+\s*HP', '', text)
    
    # Clean up
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Look for descriptive paragraphs (usually contain visual details)
    paragraphs = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 30]
    
    # Prioritize paragraphs with visual keywords
    visual_keywords = [
        'see', 'sees', 'notice', 'notices', 'observe', 'observes',
        'appear', 'appears', 'look', 'looks', 'stand', 'stands',
        'room', 'chamber', 'hall', 'corridor', 'passage', 'area',
        'forest', 'cave', 'dungeon', 'tavern', 'castle', 'ruins',
        'light', 'dark', 'shadow', 'glow', 'shine', 'illuminate',
        'figure', 'creature', 'person', 'humanoid', 'being',
        'door', 'entrance', 'exit', 'portal', 'gate',
        'stone', 'wood', 'metal', 'iron', 'gold', 'silver',
        'red', 'blue', 'green', 'black', 'white', 'grey', 'golden',
        'ancient', 'ruined', 'ornate', 'decorated', 'carved'
    ]
    
    scored_paragraphs = []
    for para in paragraphs:
        para_lower = para.lower()
        score = sum(1 for keyword in visual_keywords if keyword in para_lower)
        if score > 0:
            scored_paragraphs.append((score, para))
    
    # Sort by score (highest first)
    scored_paragraphs.sort(reverse=True, key=lambda x: x[0])
    
    if not scored_paragraphs:
        # No visual paragraphs found, use first paragraph if it exists
        if paragraphs:
            selected_text = paragraphs[0]
        else:
            # Use first sentence
            sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 20]
            if sentences:
                selected_text = sentences[0] + '.'
            else:
                return None
    else:
        # Use highest scoring paragraph
        selected_text = scored_paragraphs[0][1]
    
    # Simplify for SD prompt format
    prompt = simplify_to_prompt(selected_text, max_length)
    
    return prompt


def simplify_to_prompt(text: str, max_length: int = 200) -> str:
    """
    Simplify narrative text into a concise SD-friendly prompt.
    
    Converts:
    "You enter a dimly lit tavern. The air is thick with smoke..."
    To:
    "dimly lit medieval tavern interior, smoke-filled atmosphere, wooden beams"
    """
    # Remove "you" perspective
    text = re.sub(r'\b(you|your)\b', '', text, flags=re.IGNORECASE)
    
    # Remove filler words
    fillers = ['the', 'a', 'an', 'is', 'are', 'was', 'were', 'been', 'being', 
               'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 
               'should', 'could', 'may', 'might', 'must', 'can']
    words = text.split()
    words = [w for w in words if w.lower() not in fillers]
    
    # Join with commas for SD style
    simplified = ' '.join(words[:30])  # Limit to 30 words
    
    # Add genre/style tag
    prompt = f"fantasy RPG scene, {simplified}"
    
    # Add quality tags for better SD output
    prompt += ", detailed, atmospheric, cinematic lighting, professional digital art"
    
    # Truncate if too long
    if len(prompt) > max_length:
        prompt = prompt[:max_length].rsplit(',', 1)[0]  # Cut at last comma
    
    return prompt


def build_scene_negative_prompt() -> str:
    """
    Build a standard negative prompt for D&D scene generation.
    
    Returns:
        Negative prompt string to avoid common SD issues
    """
    return (
        "low quality, blurry, distorted, deformed, ugly, bad anatomy, "
        "watermark, signature, text, words, letters, numbers, "
        "modern, contemporary, realistic photo, photograph, "
        "nsfw, explicit, gore"
    )


def enhance_prompt_for_location(prompt: str, location_type: Optional[str] = None) -> str:
    """
    Enhance prompt with location-specific details.
    
    Args:
        prompt: Base prompt
        location_type: Type hint (e.g., "tavern", "dungeon", "forest")
        
    Returns:
        Enhanced prompt with location-appropriate details
    """
    if not location_type:
        return prompt
    
    location_enhancements = {
        'tavern': 'medieval tavern interior, wooden tables, ale mugs, fireplace',
        'dungeon': 'dark stone dungeon, torch light, ancient walls, shadows',
        'forest': 'dense fantasy forest, mystical trees, dappled sunlight',
        'cave': 'dark cave interior, rocky walls, stalactites, dim light',
        'castle': 'medieval castle interior, stone walls, banners, torches',
        'ruins': 'ancient ruins, crumbling stone, overgrown vegetation',
        'temple': 'fantasy temple interior, ornate pillars, mystical symbols',
        'city': 'medieval fantasy city, cobblestone streets, buildings',
        'battlefield': 'fantasy battlefield, dramatic sky, combat scene',
        'throne_room': 'grand throne room, ornate throne, royal decorations'
    }
    
    enhancement = location_enhancements.get(location_type.lower(), '')
    if enhancement:
        # Insert location details after genre tag
        if 'fantasy RPG scene' in prompt:
            prompt = prompt.replace('fantasy RPG scene', f'fantasy RPG scene, {enhancement}')
        else:
            prompt = f"{enhancement}, {prompt}"
    
    return prompt


def should_generate_scene_image(dm_response: str) -> bool:
    """
    Determine if the DM response warrants a scene image.
    
    Scenes worth generating:
    - Location descriptions
    - Combat encounters starting
    - Significant NPC introductions
    - Dramatic moments
    
    Skip:
    - Pure dialogue
    - Mechanical responses (roll results only)
    - Very short responses
    
    Args:
        dm_response: The DM's response text
        
    Returns:
        True if scene image should be generated
    """
    if not dm_response or len(dm_response.strip()) < 50:
        return False
    
    # Check for scene-worthy keywords
    scene_indicators = [
        'enter', 'enters', 'arrive', 'arrives', 'see', 'sees',
        'room', 'chamber', 'area', 'location', 'place',
        'creature', 'enemy', 'foe', 'monster', 'beast',
        'encounter', 'battle', 'combat', 'fight',
        'appear', 'appears', 'emerge', 'emerges',
        'door opens', 'passage', 'corridor'
    ]
    
    dm_lower = dm_response.lower()
    has_scene_indicator = any(indicator in dm_lower for indicator in scene_indicators)
    
    # Check if it's not just dice rolls or mechanics
    has_narrative = len(re.sub(r'[\[\]0-9d+\-]', '', dm_response)) > 100
    
    return has_scene_indicator and has_narrative
