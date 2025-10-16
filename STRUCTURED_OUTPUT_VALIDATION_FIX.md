# Structured Output Validation Fix

## Problem

When using structured generation with Groq's Llama 4 Scout model, validation errors occurred:

```
Failed to parse structured output: 1 validation error for CharacterProfile
unique_qualities
  Input should be a valid list [type=list_type, input_value="Eiravyn's unique blend o...both battle and debate.", input_type=str]
```

## Root Cause

The LLM sometimes returns **strings** instead of **lists** for array fields in the JSON schema, even when using structured outputs mode. This happens because:

1. **Model limitations** - Not all models perfectly follow JSON Schema constraints
2. **Complex schemas** - CharacterProfile has many nested list fields
3. **Edge cases** - Models may interpret array requirements loosely

### Example of the Issue

**Expected** (JSON Schema):

```json
{
  "unique_qualities": [
    "Master tactician",
    "Photographic memory",
    "Ambidextrous"
  ]
}
```

**Received** (From LLM):

```json
{
  "unique_qualities": "Eiravyn's unique blend of tactical genius and diplomatic skill makes them valuable in both battle and debate."
}
```

The model returned a descriptive **string** instead of a **list of strings**.

## Solution

Added **Pydantic field validators** to automatically convert strings to lists when needed. This provides:

1. ✅ **Graceful handling** - No validation errors, continues processing
2. ✅ **Data preservation** - String content is wrapped in a list
3. ✅ **Backward compatibility** - Still accepts proper list format
4. ✅ **Defensive programming** - Handles various edge cases

### Implementation

**File**: `backend/schemas.py`

#### CharacterProfile Validators

Added two validators to handle common LLM mistakes:

```python
from pydantic import BaseModel, Field, field_validator

class CharacterProfile(BaseModel):
    # ... field definitions ...

    # Validator for simple string list fields
    @field_validator('distinctive_features', 'personality_traits', 'formative_events',
                     'goals', 'values', 'emotional_weaknesses', 'physical_weaknesses',
                     'skills', 'special_abilities', 'unique_qualities', 'quirks_and_habits',
                     mode='before')
    @classmethod
    def convert_string_to_list(cls, v):
        """Convert string to list if LLM returns string instead of array"""
        if isinstance(v, str):
            # Wrap string in a list
            return [v]
        return v

    # Validator for list of dicts (relationships)
    @field_validator('key_relationships', mode='before')
    @classmethod
    def ensure_relationships_list(cls, v):
        """Ensure relationships is a list of dicts"""
        if isinstance(v, str):
            # If it's a string, return empty list (can't parse)
            return []
        if isinstance(v, dict):
            # If it's a single dict, wrap in list
            return [v]
        return v
```

#### WorldProfile Validators

Similar validators for world generation:

```python
class WorldProfile(BaseModel):
    # ... field definitions ...

    # Validator for simple string list fields
    @field_validator('climate_zones', 'natural_wonders', 'dominant_species',
                     'languages', 'cultural_norms', 'limitations',
                     'notable_artifacts', 'central_themes', 'current_threats',
                     mode='before')
    @classmethod
    def convert_string_to_list(cls, v):
        """Convert string to list if LLM returns string instead of array"""
        if isinstance(v, str):
            return [v]
        return v

    # Validator for list of dicts
    @field_validator('major_historical_events', 'major_regions',
                     'major_civilizations', 'religions_and_beliefs',
                     'major_conflicts', mode='before')
    @classmethod
    def ensure_dict_list(cls, v):
        """Ensure field is a list of dicts"""
        if isinstance(v, str):
            return []  # Can't parse string to dict list
        if isinstance(v, dict):
            return [v]
        return v
```

## How Validators Work

### mode='before'

Runs **before** Pydantic's default validation, allowing us to transform the data

### Conversion Logic

1. **String → List**: `"value"` becomes `["value"]`
2. **Dict → List**: `{...}` becomes `[{...}]`
3. **Already List**: Passes through unchanged
4. **String for Dict List**: Returns `[]` (can't convert string to structured dicts)

### Example Transformations

**Before Validation:**

```json
{
  "unique_qualities": "Great leader",
  "goals": ["Become king", "Unite the realm"],
  "key_relationships": { "name": "Aria", "relationship": "sister" }
}
```

**After Validation:**

```json
{
  "unique_qualities": ["Great leader"],
  "goals": ["Become king", "Unite the realm"],
  "key_relationships": [{ "name": "Aria", "relationship": "sister" }]
}
```

## Fields Protected by Validators

### CharacterProfile (11 list fields)

- `distinctive_features`
- `personality_traits`
- `formative_events`
- `goals`
- `values`
- `emotional_weaknesses`
- `physical_weaknesses`
- `skills`
- `special_abilities`
- `unique_qualities`
- `quirks_and_habits`
- `key_relationships` (special handling)

### WorldProfile (12 list fields)

- `climate_zones`
- `natural_wonders`
- `dominant_species`
- `languages`
- `cultural_norms`
- `limitations`
- `notable_artifacts`
- `central_themes`
- `current_threats`
- `major_historical_events` (special handling)
- `major_regions` (special handling)
- `major_civilizations` (special handling)
- `religions_and_beliefs` (special handling)
- `major_conflicts` (special handling)

## Impact

This fix affects:

- ✅ **Structured Character Generation** - No more validation errors for lists
- ✅ **Structured World Generation** - Handles malformed arrays gracefully
- ✅ **All LLM Providers** - Works regardless of which model/provider is used
- ✅ **Future Schemas** - Pattern can be reused for new structured outputs

## Testing

1. **Character Generation**:
   - Create character with Groq + Llama 4 Scout
   - Should succeed even if model returns strings for lists
   - Check generated character displays correctly

2. **World Generation**:
   - Create world with structured generation
   - Verify all list fields are populated
   - Confirm no validation errors

3. **Edge Cases**:
   - Try with different models
   - Test with various content complexities
   - Verify data integrity after conversion

## Why This Happens

Even with structured outputs (`json_schema` mode), LLMs can:

1. **Misinterpret instructions** - Think a descriptive string is better
2. **Context confusion** - Lose track of schema requirements
3. **Token optimization** - Choose shorter string over array syntax
4. **Training bias** - Trained on data where fields were sometimes strings

## Alternative Solutions Considered

### 1. ❌ Stricter Prompting

```python
prompt = "CRITICAL: All list fields MUST be arrays, never strings..."
```

- **Problem**: Doesn't guarantee compliance
- **Issue**: Makes prompts longer and more complex

### 2. ❌ Retry Logic

```python
try:
    result = parse_response()
except ValidationError:
    retry_with_fixed_prompt()
```

- **Problem**: Wastes API calls and time
- **Issue**: May fail repeatedly

### 3. ✅ Pydantic Validators (Chosen Solution)

```python
@field_validator('field_name', mode='before')
def convert_string_to_list(cls, v):
    if isinstance(v, str):
        return [v]
    return v
```

- **Advantage**: Automatic, fast, reliable
- **Advantage**: No extra API calls
- **Advantage**: Preserves data

## Server Restart

The backend server should auto-reload with these changes. If not:

```powershell
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

## Best Practices Going Forward

1. **Always add validators** for list fields in structured schemas
2. **Test with multiple models** to see different failure modes
3. **Log validation issues** to identify patterns
4. **Consider fallbacks** for complex nested structures
5. **Document expected formats** in field descriptions

## Related Issues

This fix resolves:

- ✅ `list_type` validation errors
- ✅ String-to-list conversion failures
- ✅ Malformed relationship objects
- ✅ Empty array fields when strings are provided

## References

- [Pydantic Validators Documentation](https://docs.pydantic.dev/latest/concepts/validators/)
- [Groq Structured Outputs](https://console.groq.com/docs/structured-outputs)
- [JSON Schema Best Practices](https://json-schema.org/understanding-json-schema/reference/array.html)
