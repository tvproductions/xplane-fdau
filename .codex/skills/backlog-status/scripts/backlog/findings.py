from __future__ import annotations

import sys

from backlog.model import Finding


def finding_key(finding: Finding) -> tuple[int, str, int, str, str, int]:
    """Return the canonical stable ordering key for audit findings."""
    return (
        0 if finding.severity == "error" else 1,
        finding.path,
        finding.line if finding.line is not None else sys.maxsize,
        finding.code,
        finding.node or "",
        finding.gate if finding.gate is not None else sys.maxsize,
    )
