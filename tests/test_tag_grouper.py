"""Tests for deploy_diff.tag_grouper."""

from deploy_diff.tag_grouper import (
    GroupConfig,
    TagGroup,
    group_tags,
    environment_pairs,
)


# ---------------------------------------------------------------------------
# TagGroup helpers
# ---------------------------------------------------------------------------

def test_tag_group_latest_empty():
    g = TagGroup(name="prod", tags=[])
    assert g.latest() is None


def test_tag_group_latest_single():
    g = TagGroup(name="prod", tags=["v1.0.0"])
    assert g.latest() == "v1.0.0"


def test_tag_group_previous_requires_two():
    g = TagGroup(name="prod", tags=["v1.0.0"])
    assert g.previous() is None


def test_tag_group_previous_returns_second_to_last():
    g = TagGroup(name="prod", tags=["v1.0.0", "v1.1.0", "v1.2.0"])
    assert g.previous() == "v1.1.0"
    assert g.latest() == "v1.2.0"


# ---------------------------------------------------------------------------
# group_tags
# ---------------------------------------------------------------------------

def test_group_tags_no_patterns_all_default():
    config = GroupConfig(patterns={}, default_group="other")
    tags = ["v1.0.0", "v2.0.0"]
    groups = group_tags(tags, config)
    assert set(groups["other"].tags) == {"v1.0.0", "v2.0.0"}


def test_group_tags_prefix_patterns():
    config = GroupConfig(
        patterns={"prod": r"^prod-", "staging": r"^staging-"},
        default_group="other",
    )
    tags = ["prod-1.0", "staging-1.0", "hotfix-1.0"]
    groups = group_tags(tags, config)
    assert groups["prod"].tags == ["prod-1.0"]
    assert groups["staging"].tags == ["staging-1.0"]
    assert groups["other"].tags == ["hotfix-1.0"]


def test_group_tags_first_match_wins():
    config = GroupConfig(
        patterns={"prod": r"prod", "all": r".*"},
        default_group="other",
    )
    tags = ["prod-1.0"]
    groups = group_tags(tags, config)
    assert groups["prod"].tags == ["prod-1.0"]
    assert groups["all"].tags == []


def test_group_tags_empty_input():
    config = GroupConfig(patterns={"prod": r"^prod-"}, default_group="other")
    groups = group_tags([], config)
    assert groups["prod"].tags == []
    assert groups["other"].tags == []


# ---------------------------------------------------------------------------
# environment_pairs
# ---------------------------------------------------------------------------

def test_environment_pairs_omits_empty_groups():
    groups = {
        "prod": TagGroup("prod", []),
        "staging": TagGroup("staging", ["s-1", "s-2"]),
    }
    pairs = environment_pairs(groups)
    assert "prod" not in pairs
    assert pairs["staging"] == ("s-1", "s-2")


def test_environment_pairs_single_tag_no_previous():
    groups = {"prod": TagGroup("prod", ["v1.0.0"])}
    pairs = environment_pairs(groups)
    assert pairs["prod"] == (None, "v1.0.0")
