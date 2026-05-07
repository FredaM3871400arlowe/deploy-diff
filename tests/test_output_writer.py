"""Tests for deploy_diff.output_writer."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from deploy_diff.output_writer import (
    OutputConfig,
    build_output_config,
    write_output,
)


CONTENT = "## v1.1.0 -> v1.2.0\n- feat: add thing\n"


def test_write_output_to_stdout(capsys: pytest.CaptureFixture) -> None:
    config = OutputConfig()
    write_output(CONTENT, config)
    captured = capsys.readouterr()
    assert CONTENT in captured.out


def test_write_output_quiet_suppresses_stdout(capsys: pytest.CaptureFixture) -> None:
    config = OutputConfig(quiet=True)
    write_output(CONTENT, config)
    captured = capsys.readouterr()
    assert captured.out == ""


def test_write_output_to_file(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    out_file = tmp_path / "changelog.md"
    config = OutputConfig(output_path=out_file)
    write_output(CONTENT, config)
    assert out_file.read_text(encoding="utf-8") == CONTENT
    captured = capsys.readouterr()
    assert "changelog.md" in captured.err


def test_write_output_appends(tmp_path: Path) -> None:
    out_file = tmp_path / "changelog.md"
    out_file.write_text("# Existing\n", encoding="utf-8")
    config = OutputConfig(output_path=out_file, append=True)
    write_output(CONTENT, config)
    text = out_file.read_text(encoding="utf-8")
    assert text.startswith("# Existing\n")
    assert CONTENT in text


def test_write_output_creates_parent_dirs(tmp_path: Path) -> None:
    out_file = tmp_path / "nested" / "deep" / "changelog.md"
    config = OutputConfig(output_path=out_file)
    write_output(CONTENT, config)
    assert out_file.exists()


def test_write_output_adds_trailing_newline(tmp_path: Path) -> None:
    out_file = tmp_path / "out.md"
    config = OutputConfig(output_path=out_file)
    write_output("no newline at end", config)
    text = out_file.read_text(encoding="utf-8")
    assert text.endswith("\n")


def test_build_output_config_defaults() -> None:
    cfg = build_output_config(None)
    assert cfg.output_path is None
    assert cfg.append is False
    assert cfg.quiet is False


def test_build_output_config_with_path(tmp_path: Path) -> None:
    cfg = build_output_config(str(tmp_path / "out.md"), append=True, quiet=True)
    assert cfg.output_path == tmp_path / "out.md"
    assert cfg.append is True
    assert cfg.quiet is True
