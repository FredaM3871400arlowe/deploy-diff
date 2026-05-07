"""Tests for deploy_diff.tag_filter."""

import pytest

from deploy_diff.tag_filter import (
    TagFilterConfig,
    filter_tags,
    latest_tag,
    matches_pattern,
    previous_tag,
)

TAGS = [
    "v1.0.0",
    "v1.1.0",
    "v1.2.0-rc1",
    "v2.0.0",
    "hotfix-2024-01",
    "hotfix-2024-02",
]


def test_matches_pattern_true():
    assert matches_pattern("v1.0.0", r"^v\d+") is True


def test_matches_pattern_false():
    assert matches_pattern("hotfix-2024-01", r"^v\d+") is False


def test_filter_tags_no_config():
    cfg = TagFilterConfig()
    assert filter_tags(TAGS, cfg) == TAGS


def test_filter_tags_prefix():
    cfg = TagFilterConfig(prefix="hotfix")
    assert filter_tags(TAGS, cfg) == ["hotfix-2024-01", "hotfix-2024-02"]


def test_filter_tags_pattern():
    cfg = TagFilterConfig(pattern=r"^v\d+\.\d+\.\d+$")
    assert filter_tags(TAGS, cfg) == ["v1.0.0", "v1.1.0", "v2.0.0"]


def test_filter_tags_exclude():
    cfg = TagFilterConfig(exclude_patterns=[r"rc"])
    result = filter_tags(TAGS, cfg)
    assert "v1.2.0-rc1" not in result
    assert len(result) == len(TAGS) - 1


def test_filter_tags_limit():
    cfg = TagFilterConfig(limit=2)
    assert filter_tags(TAGS, cfg) == ["v1.0.0", "v1.1.0"]


def test_filter_tags_combined():
    cfg = TagFilterConfig(prefix="v", exclude_patterns=[r"rc"], limit=2)
    assert filter_tags(TAGS, cfg) == ["v1.0.0", "v1.1.0"]


def test_latest_tag_returns_last():
    assert latest_tag(TAGS) == "hotfix-2024-02"


def test_latest_tag_empty():
    assert latest_tag([]) is None


def test_previous_tag_found():
    assert previous_tag(TAGS, "v2.0.0") == "v1.2.0-rc1"


def test_previous_tag_first_returns_none():
    assert previous_tag(TAGS, "v1.0.0") is None


def test_previous_tag_unknown_returns_none():
    assert previous_tag(TAGS, "nonexistent") is None
