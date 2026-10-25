# Strict heavy starter adoption evidence

Observed 2026-10-25. Owner: Jeff / tvproductions and the FDAU implementer.
Plan: [strict heavy onboarding](../superpowers/plans/2026-10-25-strict-heavy-starter-onboarding.md).
Spec: [approved design](../superpowers/specs/2026-10-11-skills-first-native-adoption-design.md).

## Scope and source identity

This is brownfield first adoption, not a release or an already-completed template
upgrade. The user explicitly selected heavy and approved the plan. Backplane
remains disabled; FDAU requirements and BACKLOG/HANDOFF remain authoritative.
Cognitive analysis is UNKNOWN pending the external gzkit library extraction and
shared starter contract. No local substitute or acceptance waiver is authorized.

Starting main HEAD: `3a5211bfe3c1ab80e25758fce61356dd6ef7cbef`.
Implementation branch: `chore/strict-heavy-onboarding` in
`.worktrees/strict-heavy-onboarding`. Main already contained the uncommitted
approved specification and new plan; they were copied into the isolated branch,
and the originals remain preserved on main. The separate pre-existing
`chore/dependency-refresh-2026-10-18` worktree is outside this change.

Released starter: v0.6.0 / `c0a6945b2170e1cf5bee3e80738916f5b62d13a5`.
The live latest-release endpoint still identifies v0.6.0. A separate temporary
checkout resolves the annotated tag to that commit. Its own pinned uv 0.13.1 /
Python 3.14.8 environment passed bundle/both-catalog validation and the read-only
backport assessment. This helper environment is separate from FDAU; its unused
legacy cognitive dependency is not installed in FDAU or used for acceptance.

The shared catalog selects SP v7.0.0, gz-skills v0.8.0 and disabled Backplane.
Official releases now include SP v7.0.1 and gz-skills v0.8.3; retain the reviewed
released catalog rather than inventing FDAU-specific component substitutions.
Installed/enabled old-source `gz-skills@gz-skills` is 0.8.3, while FDAU's old
configuration asks for 0.5.0. Other native copies are disabled here. Installation
and loaded-source reconciliation are pending, not inferred from cache presence.

Rollback references are the starting HEAD plus the preserved approved-document
diff and native inventory in the ignored plan workspace. Main's old Superpowers
junction/target remain untouched. No remote push, tag, release or external
repository edit is included in this work.

## Exact environment and candidate tool selection

Initial isolated environment: uv 0.13.5; managed CPython 3.12.15, AMD64, with its
own `.venv` and editable import rooted in this worktree. The original frozen
sync succeeded. The uv_build range still selects the older family and needs
reconciliation. Python's official 3.12.15 release and current uv 0.13.5 release
were checked; the latter also updates managed-Python build trust material.

Official PyPI release metadata was checked for every baseline tool. These are
**candidates**, not compatibility/installation passes. Package metadata admits
Python 3.12.15; actual installation, probes and project checks remain required.

| Tool | Candidate | Selected family / purpose |
| --- | --- | --- |
| uv / uv_build | 0.13.5 | 0.13.x; exact resolver/build inputs |
| Ruff | 0.17.2 | 0.17.x, already entered by existing 0.17.0 lock; strict routine rules |
| ty | 0.0.91 | Current 0.0.x beta; revisit stable release / scoped maintenance |
| pre-commit | 4.7.0 | 4.x routine hook runner |
| Cosmic Ray | 8.7.0 | 8.x bounded mutation |
| Lizard | 1.24.3 | 1.24.x complexity; parser/corpus proof pending |
| cohesion | 1.2.0 | 1.x responsibility review |
| Interrogate | 1.7.0 | 1.x documentation presence |
| Vulture | 2.16 | 2.x dead-code candidates |
| Bandit | 1.9.4 | 1.x security analysis |
| Coverage.py | 7.17.0 | 7.x branch and statement coverage |
| deptry | 0.25.1 | 0.25.x dependency declaration analysis |
| pip-audit | 2.10.1 | 2.x exact-export advisory analysis |
| Import Linter | 2.15 | 2.x project boundary contracts |
| detect-secrets | 1.5.0 | 1.x retained explicit secret controls |
| Cognitive analyzer | Unavailable | External extraction; no fabricated package/pin/API |

This is a scoped onboarding update, not a completed full dependency refresh.
Original documentation/artifact dependencies keep their separate purposes.

## Baseline measurements and known adapter defects

The isolated, unmodified tooling baseline passed **604 unittest tests in
366.153 seconds** on Python 3.12.15. Focused governance/documentation checks
passed 42 tests, the strict backlog audit/next found no findings, ty passed and
strict MkDocs built successfully. These observations establish a baseline,
not acceptance of the revised engineering configuration.

Legacy Xenon C/B/A over `src/xplane_fdau` passes. Diagnostic Ruff C901 at 20
over runtime/tests/tools/project adapters identifies five functions: backlog
`_backlog_link_findings` (24), `_roadmap_findings` (23), `_backlog_findings` (27),
and dependency-refresh `collect_status` (24), `_remaining_constraints` (22).

Diagnostic Lizard 1.24.0 over 93 Python files measured 1,384 functions with an
overall mean about 3.48. Several test/tool/adapter functions exceed 20, and
`tools/dependency_refresh.py`, `tools/runtime_imports.py` and backlog rules
exceed the module-mean ceiling 10. The diagnostic name/line comparison also
reports mismatches requiring investigation with the selected analyzer; it is
not an accepted function-discovery proof. Reports preserve original paths,
hashes and measurements in the ignored workspace; do not compare metric names
as if they were equivalent counts.

The required pre-change dependency status ran but returned nonzero: its
preview uv advisory parser rejects current advisory records, and its bounded
Index reader rejected the coverage response as untrusted or oversized. No
advisory-free or complete-refresh claim is justified. Preserve guards and
diagnose the actual response shapes/size before changing this adapter.

## A01–A18 acceptance matrix

Each row records actual status, applicability, executed scope and remaining
proof. UNKNOWN is not PASS. All required rows must pass for strict acceptance;
Backplane whole-stack readiness is independently deferred.

| ID | Applicability / observed status | Evidence / remaining work |
| --- | --- | --- |
| A01 | PASS for initial identity/scope/rollback capture | Starting HEAD, dirty-document provenance, isolated branch, native inventory and preserved main recorded above; update at candidate closeout |
| A02 | UNKNOWN; library and CLI apply | Existing src layout/import checks; fresh installed candidate required |
| A03 | UNKNOWN; pure Python applies | Existing uv_build; exact selected backend and actual builds pending |
| A04 | UNKNOWN | Effective uv/Ruff/ty precedence and all analyzed scopes pending |
| A05 | UNKNOWN | Managed 3.12.15 execution observed; exact pin/targets/CI reconciliation pending |
| A06 | UNKNOWN | Dated official candidate evidence above; compatibility and final pin verification pending |
| A07 | UNKNOWN | Original frozen sync passed; exact revised group/lock proof pending |
| A08 | UNKNOWN | Strict selected rules, tool provenance and four actual checks pending |
| A09 | UNKNOWN | Installed hook observation and exact-commit remote CI pending; no push authority inferred |
| A10 | UNKNOWN | Runtime empty; original dev/build purposes captured; candidate lock and Requires-Dist proof pending |
| A11 | UNKNOWN | Source-independent sdist-to-wheel build and inventory/input proof pending |
| A12 | UNKNOWN | Fresh external installed candidate behavior pending |
| A13 | UNKNOWN; typed library applies | Existing py.typed; built marker/public typing surface proof pending |
| A14 | UNKNOWN applicability verification | Single distribution, no declared workspace; confirm effective metadata before N/A |
| A15 | UNKNOWN applicability verification | No private/special runtime sources declared; effective override/source inspection pending |
| A16 | UNKNOWN applicability verification | Pure-Python core; no shipped simulator adapter/native/container product observed; record actual triggers |
| A17 | UNKNOWN; audit export/tool consumers apply | Exact dependency-export and isolated-tool execution contracts pending |
| A18 | UNKNOWN; REQUIRED external cognitive dependency | All available deeper tools, findings, code currency and host distinctions pending; cognitive proof cannot pass until shared extraction/integration |

## Ownership and remaining work

Environment/metadata/refresh safeguards: plan Task 2, A04–A08/A10/A18.
Routine composition/hooks/CI: Task 3, A08/A09.
Analysis and affected tool/test/adapter refactoring: Task 4, A18.
Native managed files and packaging: Task 5, A01/A03/A11–A13.
Policy, release/version obligations and current summaries: Task 6.
Candidate measurements, installed artifacts, independent review and native/CI
observations: Task 7. Cognitive extraction belongs to Jeff/upstream maintainers
outside this repository; other tasks can proceed without closing that gap.

Source authority: [starter release](https://github.com/tvproductions/gz-skills-first-starter/releases/tag/v0.6.0),
[Python 3.12.15](https://www.python.org/downloads/release/python-31215/),
[uv 0.13.5](https://github.com/astral-sh/uv/releases/tag/0.13.5),
[Ruff 0.17.2](https://github.com/astral-sh/ruff/releases/tag/0.17.2),
[ty 0.0.91](https://github.com/astral-sh/ty/releases/tag/0.0.91),
and each named package's official PyPI JSON release endpoint. Local raw probe
responses/commands live in the ignored plan workspace and are not portable
proof of future candidate acceptance.

**Overall: onboarding in progress; STRICT acceptance incomplete.**
