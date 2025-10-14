from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Literal
import os
from dotenv import load_dotenv
import logging
from rate_limiter import rate_limiter
from gemini_models import fetch_available_models
from groq_models import fetch_available_models as fetch_groq_models

load_dotenv()
logger = logging.getLogger(__name__)

router = APIRouter()

# Import LLM clients
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import google.generativeai as genai
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False


class LLMRequest(BaseModel):
    provider: Literal["openai", "anthropic", "google", "groq"]
    prompt: str
    model: str | None = None
    max_tokens: int = 1000
    temperature: float = 0.7


class LLMResponse(BaseModel):
    content: str
    provider: str
    model: str


class LLMProvider:
    """Base class for LLM providers"""
    
    @staticmethod
    async def generate_openai(prompt: str, model: str = "gpt-4", max_tokens: int = 1000, temperature: float = 0.7):
        if not OPENAI_AVAILABLE:
            raise HTTPException(status_code=500, detail="OpenAI client not installed")
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")
        
        client = openai.OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        return response.choices[0].message.content
    
    @staticmethod
    async def generate_anthropic(prompt: str, model: str = "claude-3-5-sonnet-20241022", max_tokens: int = 1000, temperature: float = 0.7):
        if not ANTHROPIC_AVAILABLE:
            raise HTTPException(status_code=500, detail="Anthropic client not installed")
        
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="Anthropic API key not configured")
        
        client = anthropic.Anthropic(api_key=api_key)
        
        message = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return message.content[0].text
    
    @staticmethod
    async def generate_google(prompt: str, model: str = "gemini-2.0-flash", max_tokens: int = 1000, temperature: float = 0.7):
        if not GOOGLE_AVAILABLE:
            raise HTTPException(status_code=500, detail="Google AI client not installed")
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="Google API key not configured")
        
        genai.configure(api_key=api_key)
        model_instance = genai.GenerativeModel(model)
        
        response = model_instance.generate_content(
            prompt,
            generation_config={
                "max_output_tokens": max_tokens,
                "temperature": temperature,
            }
        )
        
        return response.text
    
    @staticmethod
    async def generate_groq(prompt: str, model: str = "llama-3.3-70b-versatile", max_tokens: int = 1000, temperature: float = 0.7):
        if not GROQ_AVAILABLE:
            raise HTTPException(status_code=500, detail="Groq client not installed")
        
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="Groq API key not configured")
        
        client = Groq(api_key=api_key)
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        
        return response.choices[0].message.content


@router.post("/generate", response_model=LLMResponse)
async def generate_content(request: LLMRequest):
    """
    Generate content using the specified LLM provider.
    
    Supports OpenAI, Anthropic (Claude), Google (Gemini), and Groq.
    Includes rate limiting to respect provider quotas.
    """
    try:
        # Estimate tokens (rough estimate: 1 token ≈ 0.75 words ≈ 4 chars)
        estimated_tokens = len(request.prompt) // 4 + request.max_tokens
        
        # Determine model first to use model-specific rate limits
        if request.provider == "openai":
            model = request.model or "gpt-4"
        elif request.provider == "anthropic":
            model = request.model or "claude-3-5-sonnet-20241022"
        elif request.provider == "google":
            model = request.model or "gemini-2.5-flash"
        elif request.provider == "groq":
            model = request.model or "llama-3.3-70b-versatile"
        else:
            model = None
        
        # Check rate limits before making request (with model-specific limits if available)
        rate_limit_error = rate_limiter.check_rate_limit(request.provider, estimated_tokens, model)
        if rate_limit_error:
            logger.warning(f"Rate limit exceeded for {request.provider}/{model}: {rate_limit_error}")
            raise HTTPException(
                status_code=429,
                detail=rate_limit_error
            )
        
        if request.provider == "openai":
            content = await LLMProvider.generate_openai(
                request.prompt, model, request.max_tokens, request.temperature
            )
        elif request.provider == "anthropic":
            content = await LLMProvider.generate_anthropic(
                request.prompt, model, request.max_tokens, request.temperature
            )
        elif request.provider == "google":
            content = await LLMProvider.generate_google(
                request.prompt, model, request.max_tokens, request.temperature
            )
        elif request.provider == "groq":
            content = await LLMProvider.generate_groq(
                request.prompt, model, request.max_tokens, request.temperature
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported provider: {request.provider}")
        
        # Record successful request
        actual_tokens = len(content) // 4  # Rough estimate
        rate_limiter.record_request(request.provider, actual_tokens)
        
        return LLMResponse(
            content=content,
            provider=request.provider,
            model=model
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/providers")
async def get_available_providers():
    """Get list of available LLM providers based on installed clients and API keys"""
    # Fetch Gemini models dynamically
    gemini_models = []
    if GOOGLE_AVAILABLE and bool(os.getenv("GOOGLE_API_KEY")):
        try:
            models_data = await fetch_available_models()
            gemini_models = [m["id"] for m in models_data]
        except Exception as e:
            logger.warning(f"Failed to fetch Gemini models dynamically: {e}")
            gemini_models = ["gemini-2.5-flash", "gemini-2.0-flash"]
    
    # Fetch Groq models dynamically
    groq_models = []
    if GROQ_AVAILABLE and bool(os.getenv("GROQ_API_KEY")):
        try:
            models_data = await fetch_groq_models()
            groq_models = [m["id"] for m in models_data]
        except Exception as e:
            logger.warning(f"Failed to fetch Groq models dynamically: {e}")
            groq_models = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "meta-llama/llama-4-scout-17b-16e-instruct"]
    
    providers = {
        "openai": {
            "available": OPENAI_AVAILABLE and bool(os.getenv("OPENAI_API_KEY")),
            "models": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"]
        },
        "anthropic": {
            "available": ANTHROPIC_AVAILABLE and bool(os.getenv("ANTHROPIC_API_KEY")),
            "models": ["claude-3-5-sonnet-20241022", "claude-3-opus-20240229", "claude-3-sonnet-20240229"]
        },
        "google": {
            "available": GOOGLE_AVAILABLE and bool(os.getenv("GOOGLE_API_KEY")),
            "models": gemini_models
        },
        "groq": {
            "available": GROQ_AVAILABLE and bool(os.getenv("GROQ_API_KEY")),
            "models": groq_models
        }
    }
    return providers


@router.get("/rate-limits/{provider}")
async def get_rate_limit_status(provider: str):
    """Get current rate limit usage for a specific provider."""
    return rate_limiter.get_usage_stats(provider)


@router.get("/rate-limits")
async def get_all_rate_limits():
    """Get rate limit usage for all providers."""
    return {
        "google": rate_limiter.get_usage_stats("google"),
        "openai": rate_limiter.get_usage_stats("openai"),
        "anthropic": rate_limiter.get_usage_stats("anthropic"),
        "groq": rate_limiter.get_usage_stats("groq"),
    }


@router.get("/google/models")
async def get_gemini_models():
    """
    Get list of available Gemini models with their rate limits.
    Fetches from Gemini API or falls back to hardcoded list.
    """
    try:
        models = await fetch_available_models()
        return {
            "models": models,
            "count": len(models)
        }
    except Exception as e:
        logger.error(f"Failed to fetch Gemini models: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch models: {str(e)}")


@router.get("/groq/models")
async def get_groq_models():
    """
    Get list of available Groq models with their rate limits.
    Fetches from Groq API or falls back to hardcoded list.
    """
    try:
        models = await fetch_groq_models()
        return {
            "models": models,
            "count": len(models)
        }
    except Exception as e:
        logger.error(f"Failed to fetch Groq models: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch models: {str(e)}")
