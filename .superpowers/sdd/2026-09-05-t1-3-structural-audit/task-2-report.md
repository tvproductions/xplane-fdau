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
