"""Tests for deploy_diff.config_differ module."""

import pytest
from unittest.mock import patch, MagicMock

from deploy_diff.config_differ import (
    _is_config_file,
    get_changed_files,
    collect_config_changes,
    ConfigChange,
)


def make_run_result(stdout: str, returncode: int = 0):
    m = MagicMock()
    m.stdout = stdout
    m.returncode = returncode
    return m


@pytest.mark.parametrize("path,expected", [
    ("config.yaml", True),
    ("settings.yml", True),
    ("app.json", True),
    ("pyproject.toml", True),
    (".env", True),
    (".env.production", True),
    ("main.py", False),
    ("README.md", False),
    ("Dockerfile", False),
])
def test_is_config_file(path, expected):
    assert _is_config_file(path) == expected


@patch("deploy_diff.config_differ.subprocess.run")
def test_get_changed_files(mock_run):
    mock_run.return_value = make_run_result(
        "M\tconfig/settings.yaml\nA\t.env.staging\nD\told.ini\n"
    )
    result = get_changed_files("v1.0.0", "v1.1.0", "/repo")
    assert ("M", "config/settings.yaml") in result
    assert ("A", ".env.staging") in result
    assert ("D", "old.ini") in result


@patch("deploy_diff.config_differ.get_file_diff")
@patch("deploy_diff.config_differ.get_changed_files")
def test_collect_config_changes_filters_non_config(mock_files, mock_diff):
    mock_files.return_value = [
        ("M", "app/settings.yaml"),
        ("M", "app/views.py"),
        ("A", ".env"),
    ]
    mock_diff.return_value = ["+KEY=value"]
    changes = collect_config_changes("v1.0", "v1.1", "/repo")
    paths = [c.path for c in changes]
    assert "app/settings.yaml" in paths
    assert ".env" in paths
    assert "app/views.py" not in paths


@patch("deploy_diff.config_differ.get_file_diff")
@patch("deploy_diff.config_differ.get_changed_files")
def test_collect_config_changes_status_mapping(mock_files, mock_diff):
    mock_files.return_value = [
        ("A", "new.yaml"),
        ("D", "old.yaml"),
        ("M", "changed.yaml"),
    ]
    mock_diff.return_value = []
    changes = collect_config_changes("v1.0", "v1.1", "/repo")
    status_map = {c.path: c.status for c in changes}
    assert status_map["new.yaml"] == "added"
    assert status_map["old.yaml"] == "deleted"
    assert status_map["changed.yaml"] == "modified"
