"""
Settings Router - Manage application settings and API keys
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import os
from pathlib import Path
from importlib.util import find_spec
from dotenv import load_dotenv, set_key, find_dotenv

router = APIRouter(prefix="/api/settings", tags=["settings"])

# Load environment variables
load_dotenv()

class APIKeysModel(BaseModel):
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None

class APIKeysResponse(BaseModel):
    openai_configured: bool
    anthropic_configured: bool
    google_configured: bool
    groq_configured: bool
    openai_api_key_preview: Optional[str] = None
    anthropic_api_key_preview: Optional[str] = None
    google_api_key_preview: Optional[str] = None
    groq_api_key_preview: Optional[str] = None


def mask_api_key(key: str) -> str:
    """Mask API key for display (show first 8 and last 4 characters)"""
    if not key or len(key) < 12:
        return None
    return f"{key[:8]}...{key[-4:]}"


@router.get("/api-keys", response_model=APIKeysResponse)
async def get_api_keys():
    """Get current API key configuration status"""
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    google_key = os.getenv("GOOGLE_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")
    
    return APIKeysResponse(
        openai_configured=bool(openai_key),
        anthropic_configured=bool(anthropic_key),
        google_configured=bool(google_key),
        groq_configured=bool(groq_key),
        openai_api_key_preview=mask_api_key(openai_key) if openai_key else None,
        anthropic_api_key_preview=mask_api_key(anthropic_key) if anthropic_key else None,
        google_api_key_preview=mask_api_key(google_key) if google_key else None,
        groq_api_key_preview=mask_api_key(groq_key) if groq_key else None
    )


@router.post("/api-keys")
async def update_api_keys(keys: APIKeysModel):
    """Update API keys in .env file"""
    try:
        # Find or create .env file
        env_file = find_dotenv()
        if not env_file:
            # Create .env file in backend directory
            backend_dir = Path(__file__).parent.parent
            env_file = backend_dir / ".env"
            env_file.touch()
        
        env_path = str(env_file)
        
        # Update keys if provided
        updated_keys = []
        if keys.openai_api_key:
            set_key(env_path, "OPENAI_API_KEY", keys.openai_api_key)
            os.environ["OPENAI_API_KEY"] = keys.openai_api_key
            updated_keys.append("OpenAI")
        
        if keys.anthropic_api_key:
            set_key(env_path, "ANTHROPIC_API_KEY", keys.anthropic_api_key)
            os.environ["ANTHROPIC_API_KEY"] = keys.anthropic_api_key
            updated_keys.append("Anthropic")
        
        if keys.google_api_key:
            set_key(env_path, "GOOGLE_API_KEY", keys.google_api_key)
            os.environ["GOOGLE_API_KEY"] = keys.google_api_key
            updated_keys.append("Google")
        
        if keys.groq_api_key:
            set_key(env_path, "GROQ_API_KEY", keys.groq_api_key)
            os.environ["GROQ_API_KEY"] = keys.groq_api_key
            updated_keys.append("Groq")
        
        if not updated_keys:
            raise HTTPException(status_code=400, detail="No API keys provided")
        
        return {
            "message": f"Successfully updated API keys: {', '.join(updated_keys)}",
            "updated_providers": updated_keys
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update API keys: {str(e)}")


@router.delete("/api-keys/{provider}")
async def delete_api_key(provider: str):
    """Remove an API key from .env file"""
    provider = provider.lower()
    valid_providers = ["openai", "anthropic", "google", "groq"]
    
    if provider not in valid_providers:
        raise HTTPException(status_code=400, detail=f"Invalid provider. Must be one of: {', '.join(valid_providers)}")
    
    try:
        env_file = find_dotenv()
        if not env_file:
            raise HTTPException(status_code=404, detail=".env file not found")
        
        env_path = str(env_file)
        key_name = f"{provider.upper()}_API_KEY"
        
        # Set to empty string to remove
        set_key(env_path, key_name, "")
        if key_name in os.environ:
            del os.environ[key_name]
        
        return {"message": f"Successfully removed {provider} API key"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove API key: {str(e)}")


@router.get("/providers")
async def get_provider_status():
    """Get the availability status of all LLM providers"""
    # Check if packages are installed using importlib
    openai_installed = find_spec("openai") is not None
    anthropic_installed = find_spec("anthropic") is not None
    google_installed = find_spec("google.generativeai") is not None
    groq_installed = find_spec("groq") is not None
    
    return {
        "openai": {
            "installed": openai_installed,
            "configured": bool(os.getenv("OPENAI_API_KEY")),
            "available": openai_installed and bool(os.getenv("OPENAI_API_KEY"))
        },
        "anthropic": {
            "installed": anthropic_installed,
            "configured": bool(os.getenv("ANTHROPIC_API_KEY")),
            "available": anthropic_installed and bool(os.getenv("ANTHROPIC_API_KEY"))
        },
        "google": {
            "installed": google_installed,
            "configured": bool(os.getenv("GOOGLE_API_KEY")),
            "available": google_installed and bool(os.getenv("GOOGLE_API_KEY"))
        },
        "groq": {
            "installed": groq_installed,
            "configured": bool(os.getenv("GROQ_API_KEY")),
            "available": groq_installed and bool(os.getenv("GROQ_API_KEY"))
        }
    }
