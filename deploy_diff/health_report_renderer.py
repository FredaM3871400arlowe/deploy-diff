"""Renders a TagHealthReport as Markdown or plain text."""
from __future__ import annotations

from deploy_diff.tag_health_checker import TagHealthReport

_ICONS = {"warning": "⚠️", "error": "❌"}
_PLAIN_LABELS = {"warning": "[WARN]", "error": "[ERROR]"}


def render_health_markdown(report: TagHealthReport) -> str:
    lines: list[str] = []
    lines.append("## Tag Health Report")
    lines.append("")
    lines.append(f"**Tags analysed:** {len(report.tags)}")
    status = "✅ Healthy" if report.healthy else "❌ Unhealthy"
    lines.append(f"**Status:** {status}")
    lines.append(f"**Warnings:** {report.warning_count}  **Errors:** {report.error_count}")

    if report.issues:
        lines.append("")
        lines.append("### Issues")
        for issue in report.issues:
            icon = _ICONS.get(issue.level, "ℹ️")
            lines.append(f"- {icon} {issue.message}")
    else:
        lines.append("")
        lines.append("_No issues found._")

    return "\n".join(lines)


def render_health_plain(report: TagHealthReport) -> str:
    lines: list[str] = []
    lines.append("Tag Health Report")
    lines.append("=" * 40)
    lines.append(f"Tags analysed : {len(report.tags)}")
    status = "HEALTHY" if report.healthy else "UNHEALTHY"
    lines.append(f"Status        : {status}")
    lines.append(f"Warnings      : {report.warning_count}")
    lines.append(f"Errors        : {report.error_count}")

    if report.issues:
        lines.append("")
        lines.append("Issues:")
        for issue in report.issues:
            label = _PLAIN_LABELS.get(issue.level, "[INFO]")
            lines.append(f"  {label} {issue.message}")
    else:
        lines.append("")
        lines.append("No issues found.")

    return "\n".join(lines)
