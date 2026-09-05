# Task 2 report: structural consistency and dependency rules

## Changes

Implemented `backlog.rules.structural_findings(loaded)`. It independently
checks roadmap identity multimaps, epic membership, local dependency identity
and kind, deterministic local cycles, inventory reconciliation and ordering,
outcome/dependency drift, selection validity, displayed gate counts, gate
headings, and release-dashboard reconciliation. Invalid authorities suppress
only the rules that require that authority; same-file checks continue where
their parsed input remains available.

`tests/backlog_audit_support.py` copies the syntax fixture into each
`TemporaryDirectory` and applies exactly one UTF-8 replacement with explicit
LF output. `tests/test_backlog_status_rules.py` uses parameterized `subTest`
cases for the complete Task 2 rule matrix, asserts finding code, path, line
presence or absence, node, and null gate context, and retains a valid-fixture
control.

## TDD evidence

RED was observed before `backlog/rules.py` existed:

```text
uv run python -m unittest tests.test_backlog_status_rules -v
exit 1
ModuleNotFoundError: No module named 'backlog.rules'
```

The first implementation run exposed test assertion defects rather than a
production-rule defect: it treated an unspecified expected line as `None`,
and the unknown-child fixture mutation left its required gate heading behind.
Those test fixtures were corrected before the GREEN run.

GREEN:

```text
uv run python -m unittest tests.test_backlog_status_rules -v
Ran 6 tests — OK

uv run python -m unittest tests.test_backlog_status_model tests.test_backlog_status_parse tests.test_backlog_status_audit tests.test_backlog_status_policy tests.test_backlog_status_rules -v
Ran 53 tests — OK
```

## Final verification

```text
uv run ruff check --no-force-exclude .codex/skills/backlog-status/scripts
All checks passed

uv run ruff format --check --no-force-exclude .codex/skills/backlog-status/scripts
9 files already formatted

uv run ty check .codex/skills/backlog-status/scripts
All checks passed

uv run python tools/quality.py check
exit 0; Ruff, format, ty, unittest/coverage, Bandit, detect-secrets,
Interrogate, Vulture, and Xenon passed

uv run mkdocs build --strict
exit 0; documentation built successfully

git diff --check
exit 0
```

## Self-review

- Rules use `Path`-based test fixtures, explicit UTF-8, deterministic
  `TemporaryDirectory` cleanup, and no subprocesses or mutable production
  operations.
- The cycle walker includes only unique, validated local-child edges. It uses
  white/gray/black colors, emits the closing edge deterministically, and
  cannot recurse forever or generate a cascade from unknown, duplicate, or
  nonlocal dependencies.
- `M0` is accepted only when its sole roadmap identity is a milestone.
- Cross-file inventory, drift, selection, heading, and dashboard comparisons
  are skipped when their required authority is invalid or ambiguous, while
  gate-count and roadmap-local checks remain independent.
- The policy supplement and parent specification were read but not modified.
  No lifecycle, evidence, adherence, report wiring, CLI, or mutable-ledger
  behavior was added.

No unresolved concern remains for Task 2.

## Review fix round 1/5

The structural review found four root causes. Epic validation inferred an ID
prefix instead of trusting the parsed epic membership. Dependency-cycle input
was gated by one flag for an entire dependency row. Backlog and release joins
collapsed ambiguous roadmap identities into dictionaries, and collision
classification inspected all kinds at once instead of comparing each later
entry to preceding entries. The controller ruled that audit composition belongs
to Task 5, so this round does not change `audit.py`.

The focused RED command and output were:

```text
uv run python -m unittest tests.test_backlog_status_rules.StructuralRulesTests.test_standards_epic_owns_canonical_s_children tests.test_backlog_status_rules.StructuralRulesTests.test_cycle_retains_valid_edge_when_a_sibling_dependency_is_invalid tests.test_backlog_status_rules.StructuralRulesTests.test_combined_identity_collision_retains_same_kind_and_cross_kind_codes tests.test_backlog_status_rules.StructuralRulesTests.test_invalid_or_ambiguous_roadmap_does_not_cascade_cross_file_findings -v
exit 1; S1.1/S2.1/S2.2/S3.1/S4.1 incorrectly reported epic mismatches,
the valid cycle was omitted when paired with T9.9, combined collisions omitted
duplicate-id, and the corrected invalid-roadmap fixture reported the expected
backlog.unknown-child and backlog.invalid-selection cascades.
```

The first RED attempt exposed an unambiguous test-fixture issue: a separator
substring occurred in three tables, violating the support helper's intentional
exactly-one replacement contract. The test was narrowed to the milestone table
separator, then failed for the intended production cascades.

The fixes retain individually valid local edges, derive epic consistency from
the parsed owning epic's child list, maintain identity multimaps for every
cross-file comparison, skip only an ambiguous comparison unit, and classify
collisions against prior entries. The ambiguity regression covers both local
inventory joins and an ambiguous release-gate definition. The valid repository
check now returns zero loader and structural findings.

```text
uv run python -m unittest tests.test_backlog_status_rules -v
Ran 10 tests — OK

uv run python -m unittest tests.test_backlog_status_model tests.test_backlog_status_parse tests.test_backlog_status_audit tests.test_backlog_status_policy tests.test_backlog_status_rules -v
Ran 57 tests — OK

uv run python -c "... load_audit(Path('.')); structural_findings(loaded) ..."
load_findings=0 structural_findings=0

uv run ruff check --no-force-exclude .codex/skills/backlog-status/scripts
All checks passed

uv run ruff format --check --no-force-exclude .codex/skills/backlog-status/scripts
9 files already formatted

uv run ty check .codex/skills/backlog-status/scripts
All checks passed

uv run python tools/quality.py check
exit 0

uv run mkdocs build --strict
exit 0; documentation built successfully

git diff --check
exit 0
```

The installed Python 3.12 target ran all listed commands. The controller owns
the supported-target matrix confirmation for Task 5, so no unsupported Python
target is claimed here.

The final direct `unittest discover -q` confirmation ran 308 tests in 5.809
seconds with 94% repository coverage (1,527 statements, 98 missed). The
current-worktree audit confirmation was `load_findings=0 structural_findings=0`.
