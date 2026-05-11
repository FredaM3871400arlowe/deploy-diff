"""Renders a DiffMatrix as markdown or plain text."""
from deploy_diff.tag_diff_matrix import DiffMatrix, MatrixCell

_TICK = "\u2713"
_CROSS = "\u2717"


def _cell_summary(cell: MatrixCell) -> str:
    if not cell.ok:
        return f"{_CROSS} error"
    s = cell.summary
    parts = [f"{s.commit_count} commit(s)"]
    if s.config_change_count:
        parts.append(f"{s.config_change_count} cfg change(s)")
    if s.has_drift:
        parts.append("drift")
    return f"{_TICK} " + ", ".join(parts)


def render_matrix_markdown(matrix: DiffMatrix) -> str:
    if not matrix.cells:
        return "_No tag pairs to compare._\n"
    lines = ["## Tag Diff Matrix\n"]
    lines.append("| From | To | Summary |")
    lines.append("|------|----|---------|")
    for cell in matrix.cells:
        lines.append(f"| `{cell.from_tag}` | `{cell.to_tag}` | {_cell_summary(cell)} |")
    lines.append("")
    if matrix.error_count:
        lines.append(f"> {_CROSS} {matrix.error_count} pair(s) could not be compared.\n")
    return "\n".join(lines)


def render_matrix_plain(matrix: DiffMatrix) -> str:
    if not matrix.cells:
        return "No tag pairs to compare.\n"
    lines = ["Tag Diff Matrix", "=" * 40]
    for cell in matrix.cells:
        lines.append(f"  {cell.from_tag} -> {cell.to_tag}: {_cell_summary(cell)}")
    lines.append("")
    if matrix.error_count:
        lines.append(f"{matrix.error_count} pair(s) could not be compared.")
    return "\n".join(lines)
