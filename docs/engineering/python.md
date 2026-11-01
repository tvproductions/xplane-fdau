# FDAU Python engineering policy

The approved starter baseline requires strict applicable Astral alignment.
FDAU keeps the supported family `>=3.12,<3.13` under its core scope amendment;
`.python-version` selects the exact reviewed managed execution patch. Ruff and
ty target 3.12. This is the baseline's documented 3.12 lane, not evidence of an
embedded simulator runtime. The core remains pure Python and standard-library-only;
external simulator adapters prove their own host compatibility.

Select the latest stable host-compatible patch and tools within reviewed release
families using dated official evidence. Preserve exact uv/uv_build/tool pins and
the committed lock. Review family changes separately. Effective configuration,
executable origins, lock contents, installed metadata and source-independent
artifacts must agree; a locked command alone proves none of those observations.
ty remains a beta tool family and its diagnostics are treated as errors.

The November 1, 2026 refresh retains Python 3.12.16 and selects uv/uv_build
0.13.6, Ruff 0.17.3 and ty 0.0.95. uv 0.13.6 includes the selected Python
patch in its built-in catalog, replacing the October 26 immutable download
catalog override. Keep the exact Python pin aligned between `.python-version`
and CI; do not upgrade the shared minor-version alias or an embedded XPPython3
runtime as part of this project refresh. The
[coordinated refresh review](../reviews/2026-11-01-coordinated-refresh.md)
records verification and remaining acceptance gaps.

Run focused unittest, Ruff and ty while editing. The routine gate is exactly
Ruff check, Ruff format --check, ty and unittest, in that order:

```powershell
uv sync --locked --all-groups
uv run --locked --all-groups python tools/quality.py check
```

Ruff selects E4/E7/E9/F/I/UP/B/SIM/RUF over runtime, tests, tools and project
adapters. Installed pre-commit uses these same four checks; ty and unittest also
run when no Python file is staged. Routine CI invokes the aggregate once.
For metadata/build/artifact changes, run the offline hygiene adapter at stable
closeout: it supplies all-files hooks and their single routine suite, alongside
lock, backlog, docs and fresh artifact validation. Do not additionally repeat
the standalone aggregate on an unchanged candidate.

Deeper acceptance is required at adoption/release and on demand. Keep it outside
routine hooks and routine CI:

```powershell
uv run --locked --all-groups python tools/quality.py analysis --output analysis.json
uv run --locked --all-groups python tools/quality.py coverage
uv run --locked --all-groups python tools/quality.py vulnerabilities
uv run --locked --all-groups python tools/quality.py mutation --output mutation.json
```

Use new report paths; analysis and mutation preserve existing files. The offline
analysis command runs independent available dimensions even after findings.
Coverage, network audit and mutation are separate acceptance observations.
Do not commit generated reports/caches in the package; retain dated evidence
through the existing review authority.

| Dimension | Scope and interpretation |
| --- | --- |
| Cyclomatic complexity | Ruff C901, 20 per function, runtime/tests/tools/adapters |
| Function/module/project complexity | Native Lizard scores on original UTF-8 source; 20/10/5 ceilings; exact hashes, AST/function-discovery reconciliation, unrounded weighted aggregates; function-free modules have null values |
| Cognitive complexity | UNKNOWN until the shared library is extracted from gzkit and integrated into the reviewed starter; no complexipy substitute, copied code, local analyzer or invented equivalent threshold |
| Security | Bandit on runtime/tools/adapters and detect-secrets on tracked files; investigate actual findings without blanket ignores or baseline regeneration |
| Documentation | Interrogate runtime floor 40%, plus review of usefulness and correctness |
| Dead code | Vulture runtime/tests/tools/adapters, confidence 80%; trace consumers before deletion |
| Cohesion | Standalone cohesion runtime class scores, reviewed against actual responsibilities; no invented universal score floor |
| Coverage | Statement and branch measurement through unittest, retained 40% floor |
| Dependencies | deptry on shipped source against pyproject; exact hashed all-group lock export audited by pip-audit with no second resolver |
| Architecture | Real Import Linter forbidden direct/indirect edges: contracts cannot reach formats/sinks/CLI; formats cannot reach sinks/CLI; sinks cannot reach CLI; retained runtime import checks prohibit third-party, network and host imports |
| Mutation | Native Cosmic Ray on values, canonical JSON and identity validation; disposable source copy, verified import origin, green focused baseline, 30-second mutant timeout; review survivors and incomplete/abnormal execution |

An unsupported original definition is a measurement error, never an excluded
denominator. Lizard currently misses inline suites in four project files; keep
that gap visible and resolve it through the shared analyzer contract. Required
cognitive UNKNOWN likewise prevents analysis exit 0. Do not rewrite sound source
only to accommodate parser omissions, suppress required findings, raise limits,
or call configured tooling executed acceptance. Xenon/Wily remain available as
legacy diagnostic support until the replacement proof is complete.

Assess relevant Python 3.12 idioms and deprecations during design, review and
scoped maintenance using versioned official documentation. The onboarding review
adopts annotation-only PEP 695 aliases where no runtime reflection consumes them,
clear tuple unpacking and equivalent context-manager composition. Existing tests
prove behavior and exception causes. Runtime-reflected aliases and host-specific
changes require their own consumer evidence; Python 3.13/3.14 features remain
outside the supported family. An interpreter upgrade does not establish code
currency. OS seams use explicit UTF-8, pathlib, closed temporary resources and
argument-vector subprocesses; Windows evidence does not establish macOS/Linux
execution.

For release acceptance, bind all applicable A01–A18 evidence to the actual
candidate and exact artifact hashes, including a wheel rebuilt from the sdist,
external installed behavior and the typed public surface. Changed inputs stale
their affected proof. Required FAIL/UNKNOWN/stale results or conditional exceptions
cannot establish STRICT compliance. Publication remains separately gated.
