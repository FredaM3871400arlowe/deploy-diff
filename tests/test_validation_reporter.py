"""Tests for deploy_diff.validation_reporter."""

import io
from unittest.mock import patch

import pytest

from deploy_diff.tag_validator import ValidationResult
from deploy_diff.validation_reporter import (
    format_validation_report,
    report_and_exit_if_invalid,
)


def _valid() -> ValidationResult:
    return ValidationResult(valid=True, errors=[])


def _invalid(*errors: str) -> ValidationResult:
    return ValidationResult(valid=False, errors=list(errors))


def test_format_validation_report_valid():
    report = format_validation_report(_valid(), "v1.0", "v2.0")
    assert "v1.0" in report
    assert "v2.0" in report
    assert "valid" in report
    assert "✓" in report


def test_format_validation_report_invalid_contains_errors():
    result = _invalid("Tag not found: 'vX'", "Tag not found: 'vY'")
    report = format_validation_report(result, "vX", "vY")
    assert "Tag not found: 'vX'" in report
    assert "Tag not found: 'vY'" in report
    assert "✗" in report


def test_format_validation_report_header_present():
    report = format_validation_report(_valid(), "from-tag", "to-tag")
    assert "from-tag" in report
    assert "to-tag" in report


def test_format_validation_report_invalid_no_checkmark():
    result = _invalid("some error")
    report = format_validation_report(result, "a", "b")
    assert "✓" not in report


def test_report_and_exit_if_invalid_does_nothing_when_valid():
    stream = io.StringIO()
    # Should not raise SystemExit
    report_and_exit_if_invalid(_valid(), "v1", "v2", stream=stream)
    assert stream.getvalue() == ""


def test_report_and_exit_if_invalid_exits_on_invalid():
    stream = io.StringIO()
    with pytest.raises(SystemExit) as exc_info:
        report_and_exit_if_invalid(_invalid("bad tag"), "v1", "v2", stream=stream)
    assert exc_info.value.code == 1


def test_report_and_exit_if_invalid_writes_to_stream():
    stream = io.StringIO()
    with pytest.raises(SystemExit):
        report_and_exit_if_invalid(_invalid("missing tag"), "v1", "v2", stream=stream)
    output = stream.getvalue()
    assert "missing tag" in output


def test_report_and_exit_if_invalid_custom_exit_code():
    stream = io.StringIO()
    with pytest.raises(SystemExit) as exc_info:
        report_and_exit_if_invalid(
            _invalid("err"), "v1", "v2", stream=stream, exit_code=2
        )
    assert exc_info.value.code == 2
