"""Tests for deploy_diff.tag_comparator."""

from deploy_diff.tag_comparator import (
    ComparisonResult,
    _config_file_set,
    _commit_hashes,
    compare_deployments,
)
from deploy_diff.changelog_formatter import ChangelogEntry
from deploy_diff.config_differ import ConfigChange
from deploy_diff.diff_stats import DiffStats


def _change(path: str, status: str = "M") -> ConfigChange:
    return ConfigChange(path=path, status=status, diff="")


def _entry(
    commits=None,
    config_changes=None,
    from_tag="v1.0",
    to_tag="v1.1",
) -> ChangelogEntry:
    return ChangelogEntry(
        from_tag=from_tag,
        to_tag=to_tag,
        commits=commits or [],
        config_changes=config_changes or [],
    )


def test_config_file_set_empty():
    assert _config_file_set([]) == set()


def test_config_file_set_collects_paths():
    entry = _entry(config_changes=[_change("config/app.yaml"), _change("config/db.yaml")])
    result = _config_file_set([entry])
    assert result == {"config/app.yaml", "config/db.yaml"}


def test_config_file_set_deduplicates_across_entries():
    e1 = _entry(config_changes=[_change("config/app.yaml")])
    e2 = _entry(config_changes=[_change("config/app.yaml"), _change("config/db.yaml")])
    result = _config_file_set([e1, e2])
    assert result == {"config/app.yaml", "config/db.yaml"}


def test_commit_hashes_empty():
    assert _commit_hashes([]) == set()


def test_commit_hashes_collects_all():
    e1 = _entry(commits=["abc Fix bug", "def Add feature"])
    e2 = _entry(commits=["ghi Refactor"])
    result = _commit_hashes([e1, e2])
    assert result == {"abc Fix bug", "def Add feature", "ghi Refactor"}


def test_compare_deployments_no_overlap():
    baseline = [_entry(commits=["aaa old commit"], config_changes=[_change("cfg/old.yaml")])]
    candidate = [_entry(commits=["bbb new commit"], config_changes=[_change("cfg/new.yaml")])]

    result = compare_deployments("v1.0", "v2.0", baseline, candidate)

    assert result.baseline_tag == "v1.0"
    assert result.candidate_tag == "v2.0"
    assert result.new_commits == 1
    assert result.dropped_commits == 1
    assert result.new_config_files == ["cfg/new.yaml"]
    assert result.dropped_config_files == ["cfg/old.yaml"]
    assert result.common_config_files == []


def test_compare_deployments_full_overlap():
    entries = [_entry(commits=["aaa shared"], config_changes=[_change("cfg/shared.yaml")])]
    result = compare_deployments("v1.0", "v1.1", entries, entries)

    assert result.new_commits == 0
    assert result.dropped_commits == 0
    assert result.common_config_files == ["cfg/shared.yaml"]
    assert not result.has_config_drift


def test_net_commit_delta_positive():
    baseline = [_entry(commits=["aaa old"])]
    candidate = [_entry(commits=["aaa old", "bbb extra", "ccc more"])]
    result = compare_deployments("v1", "v2", baseline, candidate)
    assert result.net_commit_delta == 2


def test_net_commit_delta_negative():
    baseline = [_entry(commits=["aaa", "bbb", "ccc"])]
    candidate = [_entry(commits=["aaa"])]
    result = compare_deployments("v1", "v2", baseline, candidate)
    assert result.net_commit_delta == -2


def test_has_config_drift_false():
    result = ComparisonResult(
        baseline_tag="v1",
        candidate_tag="v2",
        baseline_stats=DiffStats(0, 0, {}),
        candidate_stats=DiffStats(0, 0, {}),
        new_commits=0,
        dropped_commits=0,
    )
    assert not result.has_config_drift


def test_has_config_drift_true_on_new_files():
    result = ComparisonResult(
        baseline_tag="v1",
        candidate_tag="v2",
        baseline_stats=DiffStats(0, 0, {}),
        candidate_stats=DiffStats(0, 0, {}),
        new_commits=0,
        dropped_commits=0,
        new_config_files=["cfg/new.yaml"],
    )
    assert result.has_config_drift
