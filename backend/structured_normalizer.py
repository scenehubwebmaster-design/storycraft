"""
Server-side normalization helpers for structured LLM outputs.

Provides a conservative, auditable set of heuristics to coerce JSON-like
objects into shapes that Pydantic schemas expect. This is intentionally
protective: we only perform low-risk transformations (type coercion for
numbers, wrapping single values into lists for array fields, trimming
strings, and case-insensitive enum matching) and always audit when a
repair/normalization is applied.
"""
from typing import Any, Type
import json
from pydantic import BaseModel
from .structured_output_utils import pydantic_to_json_schema
from .audit import write_audit_event
import logging

logger = logging.getLogger(__name__)


def _coerce_number(value: Any, target_type: str):
    try:
        if target_type == 'integer':
            if isinstance(value, str) and value.isdigit():
                return int(value)
            if isinstance(value, float):
                return int(value)
        if target_type == 'number':
            if isinstance(value, str):
                return float(value)
        return value
    except Exception:
        return value


def _match_enum(value: Any, enum_list: list):
    if not isinstance(value, str):
        return value
    for option in enum_list:
        if isinstance(option, str) and option.lower() == value.lower():
            return option
    return value


def normalize_and_validate(data_or_text: Any, model: Type[BaseModel], *, provider: str | None = None, model_name: str | None = None):
    """
    Attempt to normalize a JSON-like dict/list and validate it against the
    provided Pydantic model. Returns a validated model instance on success
    or raises the underlying ValidationError on final failure.

    Audit events are written when normalization heuristics are applied.
    """
    if isinstance(data_or_text, str):
        try:
            data = json.loads(data_or_text)
        except Exception:
            raise
    else:
        data = data_or_text

    # If it's already a Pydantic instance, return it
    if hasattr(data, 'model_dump'):
        return data

    # Fast path: try direct validation first
    try:
        validated = model.model_validate(data)
        return validated
    except Exception as first_err:
        # We'll attempt conservative, auditable repairs guided by the JSON Schema
        try:
            schema = pydantic_to_json_schema(model)
        except Exception:
            schema = {}
        # Build a deep copy to mutate
        data_copy = json.loads(json.dumps(data)) if isinstance(data, (dict, list)) else data
        repaired = False

        def _normalize_by_schema(node, schema_node):
            nonlocal repaired
            # If schema_node is a dict describing type
            if not isinstance(schema_node, dict):
                return node

            typ = schema_node.get('type')

            # Object: normalize properties recursively
            if typ == 'object' and isinstance(node, dict):
                props = schema_node.get('properties', {})
                for k, prop_schema in props.items():
                    if k not in node:
                        continue
                    node[k] = _normalize_by_schema(node[k], prop_schema)
                return node

            # Array: ensure node is a list and normalize items
            if typ == 'array':
                items_schema = schema_node.get('items', {})
                if not isinstance(node, list):
                    # wrap singleton into list
                    node = [node]
                    repaired = True
                return [ _normalize_by_schema(elem, items_schema) for elem in node ]

            # String expected but got list with single element -> unwrap
            if typ == 'string' and isinstance(node, list):
                if len(node) == 1 and isinstance(node[0], (str, int, float)):
                    repaired = True
                    return str(node[0])
                # else leave as-is (will fail validation)

            # Numbers: attempt coercion
            if typ in ('integer', 'number'):
                coerced = _coerce_number(node, typ)
                if coerced != node:
                    repaired = True
                    return coerced

            # Enum matching for strings
            if 'enum' in schema_node and isinstance(schema_node['enum'], list):
                matched = _match_enum(node, schema_node['enum'])
                if matched != node:
                    repaired = True
                    return matched

            # Default: return node unchanged
            return node

        # Apply normalization guided by top-level schema
        try:
            schema = pydantic_to_json_schema(model)
            top_schema = schema if isinstance(schema, dict) else {}
            normalized = _normalize_by_schema(data_copy, top_schema.get('schema') if 'schema' in top_schema else top_schema)
        except Exception:
            normalized = data_copy

        # If we made modifications, audit & revalidate
        if repaired:
            try:
                validated = model.model_validate(normalized)
                try:
                    write_audit_event('structured_normalization_applied', {
                        'provider': provider,
                        'model': model_name,
                        'original_excerpt': json.dumps(data)[:2000],
                        'normalized_excerpt': json.dumps(normalized)[:2000]
                    })
                except Exception:
                    logger.debug('Failed to write audit event for structured_normalization_applied')
                return validated
            except Exception:
                # Fall through to raise original error
                pass

        # No successful normalization; re-raise the original validation error
        raise first_err
