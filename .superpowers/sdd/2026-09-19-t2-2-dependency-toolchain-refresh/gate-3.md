# T2.2 gate 3 — Tests, hygiene, matrix, and exact artifacts

- **Child:** `T2.2`
- **Gate:** `3`
- **Kind:** verification
- **Result:** passed
- **Date:** 2026-09-20
- **Subject:** Active-version full gate, one hygiene pass, three Python source/installed-wheel checks, and exact distributions.

The original targeted T2.2 `unittest` command passed 76 tests. After accepted review correction `4f30758`, the same focused module set passed 81 tests, and the two changed live-state backlog assertions passed directly. The final `uv run --frozen python tools/quality.py check` exited 0 on the reviewed tree: 516 tests in 257.102 seconds, 43.9% coverage versus 40% minimum, with Ruff lint/format, ty, Bandit, detect-secrets, Interrogate, Vulture, and Xenon passing. This final gate also exercised the corrected status/tests. The initial full-gate attempt exposed two stale lifecycle expectations; both were fixed before this successful run.

The T2.2 apply ran one `uv run --offline --frozen python .codex/skills/hygiene/scripts/hygiene.py` pass before the matrix. It exited 0, including lock check, backlog audit, strict MkDocs, all-files pre-commit quality, strict Twine, fresh artifacts, and `tools/release.py check-dist`. The matrix built one external wheel/sdist pair and ran full source `unittest` successfully under CPython 3.12.13 (511 tests, 301.113 s), 3.13.14 (511 tests, 266.328 s), and 3.14.4 (511 tests, 320.611 s). Each version passed an installed-wheel smoke check from an external environment. The matrix removed only its verified temporary directory after success.

The exact wheel `xplane_fdau-0.1.0-py3-none-any.whl` SHA-256 is `08d0e3a55a1ab46b7f5f1911ccdda99926d6f87298bd7b0dc160132627282fcb`; the exact source archive `xplane_fdau-0.1.0.tar.gz` SHA-256 is `bc1f6ec548aff70c3f850c009633260c80a0222e18e3bcb86de33cc2ca7dedf8`. The artifact validator and payload inventory excluded repository tooling from both. Windows was directly exercised; macOS and Linux remain CI-host coverage. Review changes affected only development status tooling/tests and live-state assertions; they did not change package payload, lock, or matrix runner, so hygiene and the three-version matrix were not repeated.
