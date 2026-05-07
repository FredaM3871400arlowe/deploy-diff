"""Tests for deploy_diff.tag_sorter."""

import pytest
from deploy_diff.tag_sorter import SortConfig, sort_tags


def test_sort_tags_semver_order():
    tags = ["v1.10.0", "v1.2.0", "v2.0.0", "v1.2.1"]
    assert sort_tags(tags) == ["v1.2.0", "v1.2.1", "v1.10.0", "v2.0.0"]


def test_sort_tags_semver_reverse():
    tags = ["v1.0.0", "v2.0.0", "v1.5.3"]
    result = sort_tags(tags, SortConfig(reverse=True))
    assert result == ["v2.0.0", "v1.5.3", "v1.0.0"]


def test_sort_tags_date_order():
    tags = ["rel-2024.03.01", "rel-2023.12.15", "rel-2024.01.20"]
    assert sort_tags(tags) == ["rel-2023.12.15", "rel-2024.01.20", "rel-2024.03.01"]


def test_sort_tags_date_reverse():
    tags = ["2024.01.01", "2023.06.15", "2024.06.01"]
    result = sort_tags(tags, SortConfig(reverse=True))
    assert result[0] == "2024.06.01"


def test_sort_tags_lexicographic_fallback():
    tags = ["beta", "alpha", "gamma"]
    assert sort_tags(tags) == ["alpha", "beta", "gamma"]


def test_sort_tags_mixed_semver_and_date():
    """Semver tags should sort before date-style tags."""
    tags = ["2024.01.01", "1.0.0"]
    result = sort_tags(tags)
    assert result == ["1.0.0", "2024.01.01"]


def test_sort_tags_ignore_prefix():
    tags = ["release/1.10.0", "release/1.2.0", "release/2.0.0"]
    config = SortConfig(ignore_prefixes=["release/"])
    assert sort_tags(tags, config) == ["release/1.2.0", "release/1.10.0", "release/2.0.0"]


def test_sort_tags_empty():
    assert sort_tags([]) == []


def test_sort_tags_single():
    assert sort_tags(["v1.0.0"]) == ["v1.0.0"]


def test_sort_tags_no_config_uses_defaults():
    tags = ["v0.9.0", "v1.0.0", "v0.10.0"]
    result = sort_tags(tags)
    assert result == ["v0.9.0", "v0.10.0", "v1.0.0"]
