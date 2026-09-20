# T2.2 implementation verification

- **Child:** `T2.2`
- **Gate:** —
- **Kind:** verification
- **Result:** passed
- **Date:** 2026-09-20
- **Subject:** Guarded Python/uv refresh and three-version compatibility evidence.

Implementation revisions: `d9ad0d9` and accepted review correction `4f30758` on temporary branch `t2-2-dependency-refresh`. The approved lifecycle setup is `a7493e5`. The refresh is limited to the Python/uv dependency surface; the portable `gzs-update-dependencies` workflow owns the separate project-pinned Codex plugin inventory.

## Official status and refresh

Read-only status and guarded apply used the [PyPI Index API](https://docs.pypi.org/api/index-api/), [PyPI release JSON](https://docs.pypi.org/api/json/), and [uv audit](https://docs.astral.sh/uv/reference/cli/#uv-audit). Apply checked the report SHA-256 and exact reviewed dirty paths before mutation. The WinGet-owned uv executable was already at verified current version `0.12.17`, so no global tool update occurred. The exact project `required-version` is `==0.12.17`; both CI setup-uv pins were already `0.12.17`. Python metadata changed from `>=3.12` to `>=3.12,<3.15`; classifiers and the 3.12 selector remain aligned. `packaging>=25` is development-only. Runtime dependencies remain empty.

`uv lock --upgrade`, `uv sync --all-groups --locked`, and `uv lock --check` each exited 0. Of 98 registry packages, the only baseline-to-refreshed version change is `virtualenv` 21.7.16 → 21.9.0. The after-refresh report has zero source blockers, yanks, and advisory findings. Five packages remain below newest stable, each explained by official parent release requirements: `colorlog` and `plotly` by [wily 1.25.0](https://pypi.org/pypi/wily/1.25.0/json), `filelock` by [virtualenv 21.9.0](https://pypi.org/pypi/virtualenv/21.9.0/json), `mando` by [radon 5.1.0](https://pypi.org/pypi/radon/5.1.0/json), and `radon` by wily 1.25.0.

## Verification

The initial targeted `uv run --frozen python -m unittest tests.test_dependency_sources tests.test_dependency_refresh tests.test_dependency_matrix tests.test_project_metadata tests.test_release_tool tests.test_release_workflows tests.test_project_skills -v` passed 76 tests. The project `uv run --offline --frozen python .codex/skills/hygiene/scripts/hygiene.py` exited 0, including the offline lock check, backlog audit, strict MkDocs, all-files pre-commit quality gate, fresh artifacts, strict Twine, and exact `tools/release.py check-dist`. `git diff --check` and `git diff --cached --check` passed on the implementation scope.

The one built wheel/sdist pair passed Twine and the project distribution checker. Its wheel SHA-256 is `08d0e3a55a1ab46b7f5f1911ccdda99926d6f87298bd7b0dc160132627282fcb`; its sdist SHA-256 is `bc1f6ec548aff70c3f850c009633260c80a0222e18e3bcb86de33cc2ca7dedf8`. The wheel and sdist contain no dependency-refresh tooling or governance files. In separate external environments, the full source `unittest` suite passed 511 tests on CPython 3.12.13 (301.113 s), 3.13.14 (266.328 s), and 3.14.4 (320.611 s); each installed-wheel smoke check exited 0. The external matrix directory was removed after successful checked cleanup. Windows was exercised; macOS and Linux remain CI coverage.

The canonical portability static audit reported no findings in new T2.2 Python paths. Its six whole-repository findings are in pre-existing `.gitattributes`, backlog reporting, test, and installed-smoke surfaces and are outside T2.2's implementation scope.

No X-Plane deployment, Git push, tag, package publication, GitHub release, or runtime adoption action occurred. Version `0.1.0` remains unreleased.

After independent review, the corrected targeted suite passed 81 tests; Ruff lint/format and ty passed. The corrected read-only human and JSON status commands each exited 0 against live official sources. The complete active-Python gate on the intermediate `implemented` state reached 516 tests and found only two stale live-state expectations; both were corrected and passed as focused tests. Final full-gate evidence is recorded at T2.2 gate 3 after the lifecycle reaches `verified`.

The final active-version `uv run --frozen python tools/quality.py check` on the reviewed tree exited 0: 516 tests in 257.102 seconds, 43.9% coverage versus 40% minimum, and all other configured checks passed. The four linked gate records give the exact observed scope and limitations.
