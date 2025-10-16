from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Literal
import os
from dotenv import load_dotenv
import logging
from rate_limiter import rate_limiter
from gemini_models import fetch_available_models
from groq_models import fetch_available_models as fetch_groq_models
from claude_models import fetch_available_models as fetch_claude_models

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
    async def generate_openai(
        prompt: str,
        model: str = "gpt-4",
        max_tokens: int = 1000,
        temperature: float = 0.7,
        response_format: dict = None  # NEW: For structured outputs
    ):
        if not OPENAI_AVAILABLE:
            raise HTTPException(status_code=500, detail="OpenAI client not installed")
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")
        
        client = openai.OpenAI(api_key=api_key)
        
        request_params = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        # Add structured output format if provided
        if response_format:
            request_params["response_format"] = response_format
        
        response = client.chat.completions.create(**request_params)
        
        return response.choices[0].message.content
    
    @staticmethod
    async def generate_anthropic(
        prompt: str,
        model: str = "claude-sonnet-4-5",  # Updated to latest Sonnet 4.5
        max_tokens: int = 1000,
        temperature: float = 0.7,
        system: str = None,
        enable_thinking: bool = False
    ):
        """
        Generate text using Claude (Anthropic) models.
        
        Args:
            prompt: The user prompt
            model: Model ID (e.g., "claude-sonnet-4-5", "claude-haiku-4-5")
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
            system: Optional system prompt for context
            enable_thinking: Enable extended thinking (for supported models)
        
        Returns:
            Generated text content
        """
        if not ANTHROPIC_AVAILABLE:
            raise HTTPException(status_code=500, detail="Anthropic client not installed")
        
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="Anthropic API key not configured")
        
        client = anthropic.Anthropic(api_key=api_key)
        
        # Build request parameters
        request_params = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        # Add system prompt if provided
        if system:
            request_params["system"] = system
        
        # Enable extended thinking if requested and model supports it
        # Thinking-enabled models: Sonnet 4.5, 4, 3.7, Opus 4.1, 4, Haiku 4.5
        if enable_thinking:
            request_params["thinking"] = {
                "type": "enabled",
                "budget_tokens": 2000  # Default thinking budget
            }
        
        message = client.messages.create(**request_params)
        
        # Extract text content from response
        # Claude returns content as a list of blocks
        content = ""
        for block in message.content:
            if hasattr(block, 'type'):
                if block.type == "text":
                    content += block.text
                elif block.type == "thinking":
                    # Optionally include thinking blocks in response
                    # (they're not shown to end users by default)
                    pass
            else:
                # Fallback for direct text
                content += str(block)
        
        return content
    
    @staticmethod
    async def generate_google(
        prompt: str,
        model: str = "gemini-2.0-flash",
        max_tokens: int = 1000,
        temperature: float = 0.7,
        response_schema: dict = None  # NEW: For structured outputs
    ):
        if not GOOGLE_AVAILABLE:
            raise HTTPException(status_code=500, detail="Google AI client not installed")
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="Google API key not configured")
        
        genai.configure(api_key=api_key)
        
        # Configure safety settings to be minimally restrictive for creative content
        # BLOCK_NONE: Show content regardless of probability (recommended for creative storytelling)
        # Note: For gemini-2.0-flash and newer models, BLOCK_NONE is the default for most categories
        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE"  # Was: BLOCK_ONLY_HIGH
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_NONE"  # Was: BLOCK_ONLY_HIGH
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE"  # Was: BLOCK_ONLY_HIGH
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE"  # Was: BLOCK_ONLY_HIGH
            },
        ]
        
        model_instance = genai.GenerativeModel(
            model,
            safety_settings=safety_settings
        )
        
        # Build generation config
        generation_config = {
            "max_output_tokens": max_tokens,
            "temperature": temperature,
        }
        
        # Add structured output if provided
        if response_schema:
            generation_config["response_mime_type"] = "application/json"
            generation_config["response_schema"] = response_schema
        
        response = model_instance.generate_content(
            prompt,
            generation_config=generation_config
        )
        
        # Check if prompt was blocked before generation (prompt_feedback)
        if hasattr(response, 'prompt_feedback') and response.prompt_feedback:
            if hasattr(response.prompt_feedback, 'block_reason'):
                block_reason = response.prompt_feedback.block_reason
                if block_reason and block_reason != 0:  # 0 = BLOCK_REASON_UNSPECIFIED
                    # Extract safety ratings from prompt feedback
                    safety_details = []
                    if hasattr(response.prompt_feedback, 'safety_ratings'):
                        for rating in response.prompt_feedback.safety_ratings:
                            if rating.probability in ['HIGH', 'MEDIUM', 'LOW']:
                                category_name = str(rating.category).replace('HARM_CATEGORY_', '').replace('_', ' ').title()
                                safety_details.append(f"{category_name}: {rating.probability}")
                    
                    block_reason_map = {
                        1: "SAFETY - Prompt content flagged",
                        2: "OTHER - Unknown issue",
                        3: "BLOCKLIST - Contains blocked terms",
                        4: "PROHIBITED_CONTENT - Violates content policy"
                    }
                    reason_name = block_reason_map.get(block_reason, f"Unknown reason (code {block_reason})")
                    
                    detail_msg = f"Your prompt was blocked by Google before generation: {reason_name}."
                    if safety_details:
                        detail_msg += f" Safety ratings: {', '.join(safety_details)}."
                    detail_msg += " This is often too strict for creative fiction. Please use Groq or Anthropic instead, which are better suited for storytelling."
                    
                    logger.warning(f"Google prompt blocked - Reason: {block_reason}, Details: {safety_details}")
                    raise HTTPException(status_code=400, detail=detail_msg)
        
        # Check if response was blocked during generation (no candidates returned)
        if not response.candidates:
            raise HTTPException(
                status_code=400,
                detail="Content generation was blocked by safety filters after prompt was accepted. Try rephrasing your prompt or use a different provider (Groq/Anthropic recommended)."
            )
        
        candidate = response.candidates[0]
        
        # Map finish_reason codes to readable messages
        finish_reason_map = {
            0: "FINISH_REASON_UNSPECIFIED",
            1: "STOP (natural completion)",
            2: "SAFETY (blocked by safety filters)",
            3: "RECITATION (blocked for recitation)",
            4: "OTHER",
            5: "MAX_TOKENS"
        }
        
        # Check finish reason
        if candidate.finish_reason == 2:  # SAFETY
            safety_info = []
            if hasattr(candidate, 'safety_ratings') and candidate.safety_ratings:
                for rating in candidate.safety_ratings:
                    if rating.probability in ['HIGH', 'MEDIUM']:
                        category_name = str(rating.category).replace('HARM_CATEGORY_', '').replace('_', ' ').title()
                        safety_info.append(f"{category_name}: {rating.probability}")
            
            detail_msg = "Content was blocked by Google's safety filters."
            if safety_info:
                detail_msg += f" Triggered categories: {', '.join(safety_info)}."
            detail_msg += " Try rephrasing your prompt or use a different provider (Groq or Anthropic)."
            
            raise HTTPException(status_code=400, detail=detail_msg)
        
        elif candidate.finish_reason == 3:  # RECITATION
            raise HTTPException(
                status_code=400,
                detail="Content was blocked for recitation (too similar to copyrighted material). Try rephrasing or use a different provider."
            )
        
        # Try to get text, with fallback error handling
        try:
            return response.text
        except ValueError:
            # If response.text fails, provide detailed error
            finish_reason_name = finish_reason_map.get(candidate.finish_reason, f"Code {candidate.finish_reason}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate content. Finish reason: {finish_reason_name}. Try using a different provider."
            )
    
    @staticmethod
    async def generate_groq(
        prompt: str,
        model: str = "llama-3.3-70b-versatile",
        max_tokens: int = 1000,
        temperature: float = 0.7,
        response_format: dict = None  # NEW: For structured outputs
    ):
        if not GROQ_AVAILABLE:
            raise HTTPException(status_code=500, detail="Groq client not installed")
        
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="Groq API key not configured")
        
        client = Groq(api_key=api_key)
        
        request_params = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        
        # Add structured output format if provided
        if response_format:
            request_params["response_format"] = response_format
        
        response = client.chat.completions.create(**request_params)
        
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


@router.get("/claude/models")
async def get_claude_models():
    """
    Get list of available Claude (Anthropic) models with their capabilities.
    Returns models with pricing, features, and use case recommendations.
    """
    try:
        models = fetch_claude_models()
        return {
            "models": models,
            "count": len(models),
            "provider": "anthropic",
            "features": {
                "vision": "All Claude 4+ models support vision",
                "thinking": "Extended thinking available on Claude 4.5, 4, 3.7, Opus 4.1, Opus 4, and Haiku 4.5",
                "caching": "Prompt caching available on all models (5-min and 1-hour TTL)",
                "streaming": "All models support streaming responses"
            }
        }
    except Exception as e:
        logger.error(f"Failed to fetch Claude models: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch models: {str(e)}")
