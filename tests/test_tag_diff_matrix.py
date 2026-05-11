"""Tests for tag_diff_matrix and matrix_renderer."""
import pytest
from unittest.mock import MagicMock
from deploy_diff.tag_diff_matrix import build_matrix, DiffMatrix, MatrixCell
from deploy_diff.matrix_renderer import render_matrix_markdown, render_matrix_plain


def _summary(commits=2, cfg=0, drift=False):
    s = MagicMock()
    s.commit_count = commits
    s.config_change_count = cfg
    s.has_drift = drift
    return s


# --- build_matrix ---

def test_build_matrix_consecutive_pairs():
    tags = ["v1", "v2", "v3"]
    fn = MagicMock(return_value=_summary())
    matrix = build_matrix(tags, fn, consecutive_only=True)
    assert len(matrix.cells) == 2
    assert matrix.cells[0].from_tag == "v1"
    assert matrix.cells[0].to_tag == "v2"
    assert matrix.cells[1].from_tag == "v2"
    assert matrix.cells[1].to_tag == "v3"


def test_build_matrix_all_pairs():
    tags = ["v1", "v2", "v3"]
    fn = MagicMock(return_value=_summary())
    matrix = build_matrix(tags, fn, consecutive_only=False)
    assert len(matrix.cells) == 3  # (v1,v2), (v1,v3), (v2,v3)


def test_build_matrix_captures_errors():
    def bad_fn(a, b):
        raise RuntimeError("git error")

    matrix = build_matrix(["v1", "v2"], bad_fn)
    assert matrix.error_count == 1
    assert matrix.cells[0].error == "git error"
    assert not matrix.cells[0].ok


def test_build_matrix_empty_tags():
    matrix = build_matrix([], MagicMock())
    assert matrix.cells == []
    assert matrix.row_count == 0


def test_matrix_get_returns_correct_cell():
    s = _summary()
    matrix = DiffMatrix(tags=["v1", "v2"])
    matrix.cells.append(MatrixCell(from_tag="v1", to_tag="v2", summary=s))
    cell = matrix.get("v1", "v2")
    assert cell is not None
    assert cell.from_tag == "v1"


def test_matrix_get_returns_none_for_missing():
    matrix = DiffMatrix(tags=["v1", "v2"])
    assert matrix.get("v1", "v3") is None


# --- render_matrix_markdown ---

def test_render_matrix_markdown_empty():
    matrix = DiffMatrix(tags=[])
    result = render_matrix_markdown(matrix)
    assert "No tag pairs" in result


def test_render_matrix_markdown_contains_tags():
    s = _summary(commits=3, cfg=1)
    matrix = DiffMatrix(tags=["v1", "v2"])
    matrix.cells.append(MatrixCell(from_tag="v1", to_tag="v2", summary=s))
    result = render_matrix_markdown(matrix)
    assert "v1" in result
    assert "v2" in result
    assert "3 commit(s)" in result
    assert "1 cfg change(s)" in result


def test_render_matrix_markdown_error_note():
    matrix = DiffMatrix(tags=["v1", "v2"])
    matrix.cells.append(MatrixCell(from_tag="v1", to_tag="v2", summary=None, error="boom"))
    result = render_matrix_markdown(matrix)
    assert "1 pair(s) could not be compared" in result


# --- render_matrix_plain ---

def test_render_matrix_plain_empty():
    matrix = DiffMatrix(tags=[])
    result = render_matrix_plain(matrix)
    assert "No tag pairs" in result


def test_render_matrix_plain_contains_arrow():
    s = _summary(commits=1)
    matrix = DiffMatrix(tags=["v1", "v2"])
    matrix.cells.append(MatrixCell(from_tag="v1", to_tag="v2", summary=s))
    result = render_matrix_plain(matrix)
    assert "v1 -> v2" in result
