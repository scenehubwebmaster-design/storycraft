"""
Utilities for handling structured outputs across different LLM providers.
Converts Pydantic models to provider-specific schema formats.
"""
from typing import Type, Any, Dict
from pydantic import BaseModel
import json
import re
from .audit import write_audit_event


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
    # Defensive parsing:
    # - If the model returned an empty string or only whitespace, raise a clear error
    # - Try a direct json.loads first; if that fails, attempt to extract a JSON
    #   object or array from surrounding text (many LLMs include extra commentary)
    if not response_content or not response_content.strip():
        raise ValueError("Empty response from LLM when structured JSON was expected")

    # Try direct load first
    try:
        data = json.loads(response_content)
    except json.JSONDecodeError:
        # Attempt to extract a JSON object or array lying inside the text
        # Search for the first balanced {...} or [...] block using a simple regex
        # (works for common LLM outputs that wrap the JSON in backticks or prose).
        obj_match = re.search(r"(\{.*\})", response_content, re.S)
        arr_match = re.search(r"(\[.*\])", response_content, re.S)
        candidate = None
        if obj_match:
            candidate = obj_match.group(1)
        elif arr_match:
            candidate = arr_match.group(1)

        if not candidate:
            # Nothing resembling JSON found; re-raise a clearer error
            raise json.JSONDecodeError("No JSON object or array could be located in model output", response_content, 0)

        # Try parsing the extracted candidate
        try:
            data = json.loads(candidate)
        except json.JSONDecodeError as e:
            # If parsing fails due to truncation, attempt a lightweight syntactic repair
            # Check for unbalanced braces/brackets and try to close them.
            repaired = None
            try:
                repaired = _attempt_syntactic_repair(candidate)
                data = json.loads(repaired)
                # If repair succeeded, write an audit event with excerpts
                try:
                    write_audit_event('structured_repair_applied', {
                        'original_excerpt': candidate[:2000],
                        'repaired_excerpt': repaired[:2000],
                        'model': getattr(model, '__name__', None)
                    })
                except Exception:
                    # Best-effort: do not interfere with main flow if auditing fails
                    pass
            except Exception:
                # If this still fails, raise the original JSON error so callers can fallback
                raise e

    return model.model_validate(data)


def _attempt_syntactic_repair(text: str) -> str:
    """
    Attempt minimal deterministic syntactic repairs to truncated JSON-like text.
    - Balance braces and brackets by appending closing tokens if counts are unequal.
    - If the text ends with an unterminated string (unmatched quote), close it.
    - If trailing partial tokens exist after the last complete value, trim them.

    This is intentionally conservative: we only append closers and trim a trailing
    incomplete token. We do not attempt semantic fixes.
    """
    repaired = text

    # Quick heuristic: count braces and brackets
    open_braces = repaired.count('{')
    close_braces = repaired.count('}')
    open_brackets = repaired.count('[')
    close_brackets = repaired.count(']')

    # Close unmatched quotes if odd number of double quotes
    if repaired.count('"') % 2 == 1:
        repaired = repaired + '"'

    # Append missing closing braces/brackets
    if close_braces < open_braces:
        repaired = repaired + ('}' * (open_braces - close_braces))
    if close_brackets < open_brackets:
        repaired = repaired + (']' * (open_brackets - close_brackets))

    # Trim trailing incomplete tokens after the last comma or closing brace/bracket
    # If the text ends with an unfinished word (no closing quote), remove partial tail
    # Find the last occurrence of a closing structure
    last_close = max(repaired.rfind('}'), repaired.rfind(']'))
    if last_close != -1 and last_close < len(repaired) - 1:
        # Keep up to last_close+1
        repaired = repaired[:last_close+1]

    # Final cleanup: strip whitespace
    repaired = repaired.strip()

    return repaired


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

