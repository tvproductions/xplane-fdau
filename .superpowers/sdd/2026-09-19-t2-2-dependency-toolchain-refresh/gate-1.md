# T2.2 gate 1 — Read-only official dependency status

- **Child:** `T2.2`
- **Gate:** `1`
- **Kind:** verification
- **Result:** passed
- **Date:** 2026-09-20
- **Subject:** Human and deterministic JSON status over the complete Python/uv dependency surface.

`uv run --frozen python tools/dependency_refresh.py status --json` and `uv run --frozen python tools/dependency_refresh.py status` each exited 0 against live official sources after the accepted review correction `4f30758`. The human report contained 122 lines, including installed/repository/newest uv, Python 3.12/3.13/3.14, build/development constraints, each of 98 locked registry packages and its newest/outdated classification, findings, blockers, reviewed paths, proposed files/commands, and plan digest. The JSON report had zero source blockers, yanks, or vulnerability findings and reported the same 98 packages. Five versions are below newest stable: `colorlog`, `filelock`, `mando`, `plotly`, and `radon`.

The command uses the [PyPI Index API](https://docs.pypi.org/api/index-api/), exact locked artifact SHA-256 matches, uv universal locked tree/workspace metadata, and [uv audit](https://docs.astral.sh/uv/reference/cli/#uv-audit) with OSV. Bounded official-source parsing, malformed-schema blockers, yanks/advisories as remediation findings, deterministic JSON/digest, and human field completeness passed focused `unittest`. A live separate conditional-lock repro confirmed that this uv 0.12.17 audit implementation reported a vulnerable Windows-only package even when targeting Linux. The status invocations performed no tracked-file mutation.
