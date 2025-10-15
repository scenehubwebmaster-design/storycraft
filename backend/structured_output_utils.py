"""
Utilities for handling structured outputs across different LLM providers.
Converts Pydantic models to provider-specific schema formats.
"""
from typing import Type, Any, Dict
from pydantic import BaseModel
import json


def pydantic_to_json_schema(model: Type[BaseModel]) -> Dict[str, Any]:
    """
    Convert a Pydantic model to JSON Schema format.
    Works for all providers as base format.
    """
    schema = model.model_json_schema()
    
    # Remove title if it exists (some providers don't like it at root)
    if "title" in schema:
        del schema["title"]
    
    # Ensure additionalProperties is set to False
    if schema.get("type") == "object":
        schema["additionalProperties"] = False
    
    return schema


def pydantic_to_openai_schema(model: Type[BaseModel]) -> Dict[str, Any]:
    """
    Convert Pydantic model to OpenAI's structured output format.
    OpenAI uses response_format with json_schema type.
    """
    schema = pydantic_to_json_schema(model)
    
    return {
        "type": "json_schema",
        "json_schema": {
            "name": model.__name__,
            "schema": schema,
            "strict": True  # Enforce strict adherence to schema
        }
    }


def pydantic_to_groq_schema(model: Type[BaseModel]) -> Dict[str, Any]:
    """
    Convert Pydantic model to Groq's structured output format.
    Groq uses similar format to OpenAI.
    """
    schema = pydantic_to_json_schema(model)
    
    return {
        "type": "json_schema",
        "json_schema": {
            "name": model.__name__,
            "schema": schema
        }
    }


def pydantic_to_google_schema(model: Type[BaseModel]) -> Dict[str, Any]:
    """
    Convert Pydantic model to Google's structured output format.
    Google uses response_schema directly.
    """
    # Google accepts the Pydantic model directly in their Python SDK
    # But we'll provide the JSON schema for flexibility
    return pydantic_to_json_schema(model)


def get_schema_for_provider(model: Type[BaseModel], provider: str) -> Dict[str, Any]:
    """
    Get the appropriate schema format for a given provider.
    
    Args:
        model: Pydantic model class
        provider: Provider name (openai, groq, google, anthropic)
    
    Returns:
        Schema dict in provider-specific format
    """
    provider = provider.lower()
    
    if provider == "openai":
        return pydantic_to_openai_schema(model)
    elif provider == "groq":
        return pydantic_to_groq_schema(model)
    elif provider == "google" or provider == "gemini":
        return pydantic_to_google_schema(model)
    elif provider == "anthropic":
        # Anthropic doesn't support structured outputs yet
        # Return JSON schema for prompt-based JSON mode
        return pydantic_to_json_schema(model)
    else:
        # Default to JSON schema
        return pydantic_to_json_schema(model)


def parse_structured_response(response_content: str, model: Type[BaseModel]) -> BaseModel:
    """
    Parse a JSON response string into a Pydantic model instance.
    Validates the response against the schema.
    
    Args:
        response_content: JSON string from LLM
        model: Pydantic model class to parse into
    
    Returns:
        Validated Pydantic model instance
    
    Raises:
        ValidationError: If response doesn't match schema
        JSONDecodeError: If response isn't valid JSON
    """
    data = json.loads(response_content)
    return model.model_validate(data)


def supports_structured_outputs(provider: str) -> bool:
    """
    Check if a provider supports native structured outputs.
    
    Args:
        provider: Provider name
    
    Returns:
        True if provider supports structured outputs, False otherwise
    """
    structured_output_providers = ["openai", "groq", "google", "gemini"]
    return provider.lower() in structured_output_providers


def get_structured_output_prompt(model: Type[BaseModel]) -> str:
    """
    Generate a fallback prompt for providers that don't support structured outputs.
    Includes the JSON schema in the prompt.
    
    Args:
        model: Pydantic model class
    
    Returns:
        Prompt string with schema instructions
    """
    schema = pydantic_to_json_schema(model)
    schema_json = json.dumps(schema, indent=2)
    
    return f"""You must respond with valid JSON that exactly matches this schema:

{schema_json}

Important:
- Include all required fields
- Follow the exact structure shown
- Use the correct data types
- Do not include any additional fields
- Respond ONLY with the JSON object, no other text

Your response:"""

