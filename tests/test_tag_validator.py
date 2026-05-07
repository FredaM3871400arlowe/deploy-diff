"""Tests for deploy_diff.tag_validator."""

from unittest.mock import patch

from deploy_diff.tag_validator import (
    ValidationResult,
    _from_precedes_to,
    _tag_exists,
    _tags_are_distinct,
    validate_tag_range,
)

TAGS = ["v1.0.0", "v1.1.0", "v1.2.0", "v2.0.0"]


def test_tag_exists_true():
    assert _tag_exists("v1.0.0", TAGS) is True


def test_tag_exists_false():
    assert _tag_exists("v9.9.9", TAGS) is False


def test_tags_are_distinct_true():
    assert _tags_are_distinct("v1.0.0", "v2.0.0") is True


def test_tags_are_distinct_false():
    assert _tags_are_distinct("v1.0.0", "v1.0.0") is False


def test_from_precedes_to_true():
    assert _from_precedes_to("v1.0.0", "v2.0.0", TAGS) is True


def test_from_precedes_to_false():
    assert _from_precedes_to("v2.0.0", "v1.0.0", TAGS) is False


def test_from_precedes_to_missing_tag_skips_check():
    # Missing tags are handled by existence check; order check should not raise
    assert _from_precedes_to("v9.9.9", "v1.0.0", TAGS) is True


def test_validate_tag_range_valid():
    result = validate_tag_range("v1.0.0", "v2.0.0", known_tags=TAGS)
    assert result.valid is True
    assert result.errors == []
    assert bool(result) is True


def test_validate_tag_range_missing_from():
    result = validate_tag_range("v0.0.1", "v2.0.0", known_tags=TAGS)
    assert result.valid is False
    assert any("v0.0.1" in e for e in result.errors)


def test_validate_tag_range_missing_to():
    result = validate_tag_range("v1.0.0", "v9.9.9", known_tags=TAGS)
    assert result.valid is False
    assert any("v9.9.9" in e for e in result.errors)


def test_validate_tag_range_same_tag():
    result = validate_tag_range("v1.0.0", "v1.0.0", known_tags=TAGS)
    assert result.valid is False
    assert any("must differ" in e for e in result.errors)


def test_validate_tag_range_reversed_order():
    result = validate_tag_range("v2.0.0", "v1.0.0", known_tags=TAGS)
    assert result.valid is False
    assert any("does not precede" in e for e in result.errors)


def test_validate_tag_range_calls_list_tags_when_no_known_tags():
    with patch("deploy_diff.tag_validator.list_tags", return_value=TAGS) as mock_lt:
        result = validate_tag_range("v1.0.0", "v2.0.0", repo_path="/repo")
    mock_lt.assert_called_once_with("/repo")
    assert result.valid is True


def test_validate_tag_range_both_missing_gives_two_errors():
    result = validate_tag_range("vX", "vY", known_tags=TAGS)
    assert len(result.errors) == 2
