# Task 3 report: governing artifact and acceptance adherence

Status: DONE_WITH_CONCERNS

Implementation commits:

- `a51186d` (`feat: audit governing artifacts and acceptance criteria`)
- `4f824c9` (`fix: close task 3 adherence review findings`)

## Changes

- Added `adherence_findings(loaded: AuditLoad) -> tuple[Finding, ...]` in
  `backlog/adherence.py`.
- Added active design identity, order, epic, declared cross-epic, metadata date,
  approval, active-plan relationship, lifecycle link, contextual reference,
  historical disposition, and acceptance drift checks.
- Added stable `artifact.plan.zero-children`,
  `artifact.plan.multiple-children`, `artifact.plan.wrong-family`, and
  `artifact.spec.wrong-family` parse findings.
- Added typed, source-located ROADMAP cross-epic declarations for the current
  C1-C4 and T2/T3 forms without changing version-1 serialization.
- Added exact generic resolution of the approved four-earlier-gates reference
  form. Resolution requires one earlier same-child level-two section, one exact
  `Its acceptance gates are:` marker, and exactly four sequential numbered
  items. Missing and ambiguous sources fail closed through gate drift.
- Added audit-valid acceptance text through `tests/backlog_audit_support.py` so
  the shared parser fixture bytes remain unchanged.
- Kept frozen historical-plan admission in Task 4. Task 3 accepts a parsed
  historical plan link as historical input while still checking historical
  metadata and disposition.

## TDD evidence

Initial RED:

```text
uv run python -m unittest tests.test_backlog_status_adherence -v
Ran 18 tests in 0.211s
FAILED (failures=26, errors=2)
```

The missing `backlog.adherence` interface caused the assertion failures and the
missing typed `cross_epic_designs` fact caused the attribute error. One initial
test replacement was also ambiguous and was corrected before implementation.

Focused RED for the approved generic earlier-gate reference:

```text
uv run python -m unittest tests.test_backlog_status_adherence.AdherenceTests.test_exact_four_gate_reference_resolves_a_unique_earlier_child_section -v
Ran 1 test in 0.054s
FAILED (failures=1)
```

Focused GREEN:

```text
uv run python -m unittest tests.test_backlog_status_adherence.AdherenceTests.test_exact_four_gate_reference_resolves_a_unique_earlier_child_section -v
Ran 1 test in 0.054s
OK
```

Focused RED for dependent-finding isolation:

```text
uv run python -m unittest tests.test_backlog_status_adherence.AdherenceTests.test_invalid_authority_or_linked_artifact_does_not_cascade_adherence -v
Ran 1 test in 0.040s
FAILED (failures=1)
```

Focused GREEN:

```text
uv run python -m unittest tests.test_backlog_status_adherence.AdherenceTests.test_invalid_authority_or_linked_artifact_does_not_cascade_adherence -v
Ran 1 test in 0.037s
OK
```

Final focused suite:

```text
uv run python -m unittest tests.test_backlog_status_adherence -v
Ran 21 tests in 0.996s
OK
```

Earlier audit regression suites:

```text
uv run python -m unittest tests.test_backlog_status_audit tests.test_backlog_status_rules tests.test_backlog_status_parse -q
Ran 46 tests in 2.006s
OK
```

## Complete verification

```text
uv run python tools/quality.py check
exit 0
Ruff, Ruff format, ty, unittest discovery, coverage, Bandit,
detect-secrets, Interrogate, Vulture, and Xenon passed.
```

```text
uv run ruff check --no-force-exclude .codex/skills/backlog-status/scripts
All checks passed!

uv run ruff format --check --no-force-exclude .codex/skills/backlog-status/scripts
10 files already formatted

uv run ty check .codex/skills/backlog-status/scripts
All checks passed!

uv run mkdocs build --strict
Documentation built successfully

git diff --check
exit 0, no output
```

The tests use `TemporaryDirectory`, `pathlib.Path`, explicit UTF-8, and explicit
LF writes where fixture text is changed. Windows ran all checks. macOS and Linux
were not locally exercised; the repository CI matrix remains the independent
cross-platform verification surface.

## Real-repository audit

Exact command:

```powershell
uv run python -c "from pathlib import Path; import sys; sys.path.insert(0, str(Path('.codex/skills/backlog-status/scripts').resolve())); from backlog.audit import load_audit; from backlog.rules import structural_findings; from backlog.adherence import adherence_findings; loaded=load_audit(Path('.')); print('load',len(loaded.findings),'structural',len(structural_findings(loaded)),'adherence',len(adherence_findings(loaded))); [print(f'{f.code}|{f.path}:{f.line}|{f.node}|{f.gate}') for f in adherence_findings(loaded)]"
```

Result:

```text
load 0 structural 0 adherence 22
artifact.historical.disposition|docs/superpowers/plans/2026-08-16-xplane-fdau-architecture-propagation.md:5|None|None
artifact.historical.disposition|docs/superpowers/plans/2026-08-22-q4xpcc-contract-handoff-readiness-authority.md:5|None|None
artifact.historical.disposition|docs/superpowers/plans/2026-09-05-gz-skills-adoption.md:5|None|None
artifact.gate-drift|docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md:1868|C2.4|None
artifact.gate-drift|docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md:1872|C2.4|3
artifact.gate-drift|docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md:1873|C2.4|4
artifact.gate-drift|docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md:1896|C3.3|1
artifact.gate-drift|docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md:1898|C3.3|2
artifact.gate-drift|docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md:1900|C3.3|3
artifact.gate-drift|docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md:1954|C4.4|5
artifact.gate-drift|docs/superpowers/specs/2026-08-15-xplane-fdau-local-workflow-skills-design.md:360|T2.2|1
artifact.gate-drift|docs/superpowers/specs/2026-08-15-xplane-fdau-local-workflow-skills-design.md:363|T2.2|2
artifact.gate-drift|docs/superpowers/specs/2026-08-15-xplane-fdau-local-workflow-skills-design.md:367|T2.2|3
artifact.gate-drift|docs/superpowers/specs/2026-08-15-xplane-fdau-local-workflow-skills-design.md:369|T2.2|4
artifact.gate-drift|docs/superpowers/specs/2026-08-15-xplane-fdau-local-workflow-skills-design.md:376|T3.1|2
artifact.gate-drift|docs/superpowers/specs/2026-08-15-xplane-fdau-local-workflow-skills-design.md:379|T3.1|3
artifact.gate-drift|docs/superpowers/specs/2026-08-15-xplane-fdau-local-workflow-skills-design.md:382|T3.1|4
artifact.gate-drift|docs/superpowers/specs/2026-08-23-xplane-fdau-acquisition-recording-projection-pinning-contracts-design.md:3972|D1.2|1
artifact.gate-drift|docs/superpowers/specs/2026-08-23-xplane-fdau-acquisition-recording-projection-pinning-contracts-design.md:3976|D1.2|2
artifact.gate-drift|docs/superpowers/specs/2026-08-23-xplane-fdau-acquisition-recording-projection-pinning-contracts-design.md:3980|D1.2|3
artifact.gate-drift|docs/superpowers/specs/2026-08-23-xplane-fdau-acquisition-recording-projection-pinning-contracts-design.md:3985|D1.2|4
artifact.historical.disposition|docs/superpowers/specs/2026-09-05-gz-skills-adoption-design.md:5|None|None
```

All exact source/backlog comparisons and the two corrected extraction findings
are recorded in `task-3-reconciliation.md`. The 22 genuine preserved-document
findings are routed to Task 5 reconciliation. No roadmap, backlog, design, plan,
or other governing authority bytes were changed.

## Self-review

- Confirmed finding order matches the shared severity/path/line/code/node/gate
  contract.
- Confirmed malformed ROADMAP or linked artifacts do not create dependent
  adherence cascades.
- Confirmed an unlinked approved design cannot replace the backlog child's
  explicit design link.
- Confirmed all six real F1 links remain queued contextual references and a
  suspended queued fixture uses Resume for the same determination.
- Confirmed the current C1-C4 and T2/T3 cross-epic declarations are source
  located and arbitrary undeclared cross-epic metadata remains invalid.
- Confirmed Task 3 introduces no lifecycle evidence validation, CLI
  integration, runtime dependency, network operation, state transition, or
  serialized version-1 field.

## Concerns

The 22 real-repository findings are genuine under the approved exact-text and
historical-disposition rules. They intentionally remain visible and block a
future integrated audit until reviewed reconciliation. Task 3 did not alter the
preserved documents to make the audit pass.

## Review fix round 1

Review commit baseline: `580469e`; reviewed Task 3 head: `6a9886f`.

RED:

```text
uv run python -m unittest tests.test_backlog_status_adherence.AdherenceTests.test_unresolved_managed_reference_is_never_treated_as_literal_gate_text tests.test_backlog_status_adherence.AdherenceTests.test_gate_drift_reports_title_each_ordinal_and_count_independently -v
Ran 2 tests in 0.145s
FAILED (failures=5)

uv run python -m unittest tests.test_backlog_status_audit.AuditLoadingTests.test_finding_key_is_reexported_from_neutral_module -v
Ran 1 test in 0.000s
FAILED (failures=1)
```

GREEN before the final full gate:

```text
uv run python -m unittest tests.test_backlog_status_adherence -v
Ran 23 tests in 1.098s
OK

uv run python -m unittest tests.test_backlog_status_audit tests.test_backlog_status_rules tests.test_backlog_status_model tests.test_backlog_status_parse -q
Ran 50 tests in 1.834s
OK
```

Additional fail-closed reference RED:

```text
uv run python -m unittest tests.test_backlog_status_adherence.AdherenceTests.test_managed_reference_must_be_the_only_acceptance_statement -v
test_managed_reference_must_be_the_only_acceptance_statement ... ERROR
StopIteration
Ran 1 test in 0.033s
FAILED (errors=1)
```

The exact managed reference plus a sibling acceptance statement was incorrectly
treated as ordinary literal text. The resolver now treats any occurrence of the
managed form as managed and requires it to be the subsection's sole statement.

Final targeted GREEN:

```text
uv run python -m unittest tests.test_backlog_status_adherence.AdherenceTests.test_managed_reference_must_be_the_only_acceptance_statement tests.test_backlog_status_adherence.AdherenceTests.test_unresolved_managed_reference_is_never_treated_as_literal_gate_text tests.test_backlog_status_adherence.AdherenceTests.test_gate_drift_reports_title_each_ordinal_and_count_independently -v
Ran 3 tests in 0.167s
OK
```

Final focused regression:

```text
uv run python -m unittest tests.test_backlog_status_adherence tests.test_backlog_status_audit tests.test_backlog_status_rules tests.test_backlog_status_model tests.test_backlog_status_parse -q
Ran 74 tests in 2.375s
OK
```

Final complete gate:

```text
uv run python tools/quality.py check
Ran 333 tests in 6.530s
Ran 333 tests under coverage in 7.049s
TOTAL 1527 statements, 98 missed, 94% coverage
Interrogate: 43.6% (minimum 40.0%)
exit 0
```

Final hidden-source and documentation controls:

```text
uv run ruff check --no-force-exclude .codex/skills/backlog-status/scripts
All checks passed!

uv run ruff format --check --no-force-exclude .codex/skills/backlog-status/scripts
11 files already formatted

uv run ty check .codex/skills/backlog-status/scripts
All checks passed!

uv run mkdocs build --strict
Documentation built in 1.31 seconds

git diff --check
exit 0, no output
```

The review fixes add a source-located managed-reference resolution problem,
report title drift, every differing ordinal, and count drift independently,
and centralize `finding_key` in neutral `backlog/findings.py`. `backlog.audit`
continues to re-export the public import, while adherence and structural rules
consume the same function.
