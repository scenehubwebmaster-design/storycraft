import pytest
from backend.name_generation_utils import extract_json_from_text


def test_plain_object():
    s = '{"skin": "pale", "eyes": "green", "hair": "black"}'
    parsed = extract_json_from_text(s)
    assert isinstance(parsed, dict)
    assert parsed['skin'] == 'pale'


def test_wrapped_object():
    s = "Here is the JSON:\n```json\n{\"skin\": \"olive\", \"eyes\": \"brown\", \"hair\": \"curly\"}\n```\nThanks"
    parsed = extract_json_from_text(s)
    assert parsed['eyes'] == 'brown'


def test_array_fallback():
    s = "Some text before [ {\"first\": \"A\"}, {\"first\": \"B\"} ] end"
    parsed = extract_json_from_text(s)
    assert isinstance(parsed, list)
    assert parsed[0]['first'] == 'A'


def test_malformed_raises():
    s = "No json here: just text"
    with pytest.raises(ValueError):
        extract_json_from_text(s)
