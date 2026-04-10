from db import parse_tags


def test_parse_tags_handles_json():
    assert parse_tags('["a", "b"]') == ["a", "b"]


def test_parse_tags_handles_python_literal_and_invalid_values():
    assert parse_tags("['x', 'y']") == ["x", "y"]
    assert parse_tags("{'a': 1}") == []
    assert parse_tags("invalid") == []
    assert parse_tags(None) == []
