"""Tests for deploy_diff.tag_blame."""
from unittest.mock import patch, MagicMock

import pytest

from deploy_diff.tag_blame import (
    TagBlame,
    _get_blame_for_tag,
    blame_tags,
    format_blame_table,
)


def _make_result(stdout="", stderr="", returncode=0):
    r = MagicMock()
    r.stdout = stdout
    r.stderr = stderr
    r.returncode = returncode
    return r


# ---------------------------------------------------------------------------
# TagBlame.short_identity
# ---------------------------------------------------------------------------

def test_short_identity():
    b = TagBlame(tag="v1.0", tagger_name="Alice", tagger_email="a@example.com",
                 date="2024-01-01", message="release")
    assert b.short_identity == "Alice <a@example.com>"


# ---------------------------------------------------------------------------
# _get_blame_for_tag — annotated path
# ---------------------------------------------------------------------------

def test_get_blame_annotated_tag():
    stderr = "tagger Alice Smith <alice@example.com> 1700000000 +0000\n release v1.0"
    with patch("deploy_diff.tag_blame.run_git") as mock_git:
        mock_git.return_value = _make_result(stderr=stderr, returncode=0)
        result = _get_blame_for_tag("v1.0")
    assert result is not None
    assert result.tag == "v1.0"
    assert result.tagger_name == "Alice Smith"
    assert result.tagger_email == "alice@example.com"
    assert result.message == "release v1.0"


def test_get_blame_falls_back_to_log_when_no_tagger_line():
    log_stdout = "Bob\x00bob@example.com\x002024-06-01 10:00:00 +0000\x00chore: tag"
    call_results = [
        _make_result(stderr="", returncode=0),   # tag -v succeeds but no tagger line
        _make_result(stdout=log_stdout, returncode=0),
    ]
    with patch("deploy_diff.tag_blame.run_git", side_effect=call_results):
        result = _get_blame_for_tag("v2.0")
    assert result is not None
    assert result.tagger_name == "Bob"
    assert result.tagger_email == "bob@example.com"
    assert result.message == "chore: tag"


def test_get_blame_returns_none_when_log_fails():
    call_results = [
        _make_result(returncode=1),
        _make_result(returncode=1),
    ]
    with patch("deploy_diff.tag_blame.run_git", side_effect=call_results):
        result = _get_blame_for_tag("bad-tag")
    assert result is None


def test_get_blame_returns_none_when_log_output_malformed():
    call_results = [
        _make_result(returncode=1),
        _make_result(stdout="only-one-field", returncode=0),
    ]
    with patch("deploy_diff.tag_blame.run_git", side_effect=call_results):
        result = _get_blame_for_tag("v3.0")
    assert result is None


# ---------------------------------------------------------------------------
# blame_tags
# ---------------------------------------------------------------------------

def test_blame_tags_skips_unresolvable():
    good = TagBlame(tag="v1.0", tagger_name="X", tagger_email="x@x.com",
                    date="2024-01-01", message="ok")
    with patch("deploy_diff.tag_blame._get_blame_for_tag",
               side_effect=[good, None, good]):
        results = blame_tags(["v1.0", "bad", "v2.0"])
    assert len(results) == 2
    assert all(r is good for r in results)


def test_blame_tags_empty_input():
    assert blame_tags([]) == []


# ---------------------------------------------------------------------------
# format_blame_table
# ---------------------------------------------------------------------------

def test_format_blame_table_empty():
    assert format_blame_table([]) == "No blame information available."


def test_format_blame_table_contains_tag_and_author():
    b = TagBlame(tag="v1.0", tagger_name="Alice", tagger_email="a@a.com",
                 date="2024-01-01 00:00:00 +0000", message="first release")
    table = format_blame_table([b])
    assert "v1.0" in table
    assert "Alice" in table
    assert "first release" in table
