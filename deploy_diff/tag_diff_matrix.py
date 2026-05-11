"""Builds a matrix comparing multiple tag pairs across dimensions."""
from dataclasses import dataclass, field
from typing import List, Optional
from deploy_diff.tag_diff_summary import TagDiffSummary


@dataclass
class MatrixCell:
    from_tag: str
    to_tag: str
    summary: Optional[TagDiffSummary]
    error: Optional[str] = None

    @property
    def ok(self) -> bool:
        return self.error is None and self.summary is not None


@dataclass
class DiffMatrix:
    tags: List[str]
    cells: List[MatrixCell] = field(default_factory=list)

    def get(self, from_tag: str, to_tag: str) -> Optional[MatrixCell]:
        for cell in self.cells:
            if cell.from_tag == from_tag and cell.to_tag == to_tag:
                return cell
        return None

    @property
    def row_count(self) -> int:
        return len(self.tags)

    @property
    def error_count(self) -> int:
        return sum(1 for c in self.cells if not c.ok)


def build_matrix(
    tags: List[str],
    build_summary_fn,
    consecutive_only: bool = True,
) -> DiffMatrix:
    """Build a DiffMatrix from a list of tags.

    Args:
        tags: Ordered list of tag names.
        build_summary_fn: Callable[[str, str], TagDiffSummary] that may raise.
        consecutive_only: If True, only compare adjacent pairs; otherwise all pairs.
    """
    matrix = DiffMatrix(tags=list(tags))
    pairs = _pairs(tags, consecutive_only)
    for from_tag, to_tag in pairs:
        try:
            summary = build_summary_fn(from_tag, to_tag)
            matrix.cells.append(MatrixCell(from_tag=from_tag, to_tag=to_tag, summary=summary))
        except Exception as exc:  # noqa: BLE001
            matrix.cells.append(MatrixCell(from_tag=from_tag, to_tag=to_tag, summary=None, error=str(exc)))
    return matrix


def _pairs(tags: List[str], consecutive_only: bool):
    if consecutive_only:
        return [(tags[i], tags[i + 1]) for i in range(len(tags) - 1)]
    return [
        (tags[i], tags[j])
        for i in range(len(tags))
        for j in range(i + 1, len(tags))
    ]
