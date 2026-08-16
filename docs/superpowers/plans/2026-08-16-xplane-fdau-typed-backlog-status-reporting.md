# xplane-fdau Typed Backlog Status Reporting Implementation Plan

- **Governance:** active
- **Status:** in_progress
- **Date:** 2026-08-16
- **Roadmap child:** `T1.2`
- **Source specification:** `docs/superpowers/specs/2026-08-09-xplane-fdau-backlog-status-skill-design.md`
- **Approval:** 2026-08-16 — Jeff / tvproductions
- **Completion evidence:** —

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the `T1.2` repository-local typed Markdown parser and deterministic human/JSON status reports without implementing later audit, recommendation, mutation, hygiene, or Git-synchronization behavior.

**Architecture:** A repository-local script package under `.codex/skills/backlog-status/scripts/backlog` parses the exact managed structures in `ROADMAP.md`, `BACKLOG.md`, and governance artifacts into frozen standard-library dataclasses. A thin `backlog_status.py` entry point builds a read-only snapshot, observes Git without changing it, and renders either a complete human report or the exact schema-version-1 JSON shape. Parsing enforces Markdown syntax and typed field shape; cross-file adherence, lifecycle proof, cycle detection, next-action selection, and all state changes remain later children.

**Tech Stack:** Python 3.12+, Python standard library only, frozen/slotted dataclasses, `argparse`, `json`, `pathlib`, `re`, `subprocess`, Python `unittest`, uv, Ruff, ty, and Git.

## Global Constraints

- Read `HANDOFF.md`, `ROADMAP.md`, `BACKLOG.md`, the complete parent architecture, the completed identity/FDR migration specification and plan, and the approved T1 design before editing.
- Use Python's `unittest` framework only; pytest is prohibited.
- Keep every `xplane_fdau` runtime module standard-library-only and do not add a runtime or tooling dependency on q4xpcc, xpwebapi, XPPython3, XPLM, a network client, or a Markdown package.
- Keep all backlog-status implementation beneath `.codex/skills/backlog-status`; it must remain excluded from the wheel and source distribution.
- Treat `ROADMAP.md` as node identity/kind/order/dependency authority and `BACKLOG.md` as the only mutable delivery-state authority.
- Parse only the exact managed Markdown structures approved by the T1 design; preserve repository-relative paths with `/` separators and one-based source lines.
- Report facts present in the authorities and derived dependency readiness only; never infer implementation, review, gate satisfaction, or release from file presence or Git history.
- Do not implement `audit`, semantic adherence rules, lifecycle validation, `next`, any mutation command, `repo-hygiene`, Git synchronization, push, tag, publication, or release behavior.
- Use explicit focused Ruff and ty commands for `.codex/skills/backlog-status` because the directory is excluded from ordinary product-source discovery.
- Do not push, tag, publish, create a release, or mark version `0.1.0` released.

---

## Scope boundary

`T1.2` owns syntax-level parsing and reporting. It accepts a repository only when each managed structure can be represented by the approved typed shape. Examples of parser failures in this child are a malformed table separator, an invalid identity token, an invalid status token, a malformed managed link, a malformed task item, a missing required metadata field, or a non-integer gate count.

`T1.2` deliberately does not decide whether identities are duplicated across files, dependencies form a cycle, backlog outcomes drift from the roadmap, a plan covers the wrong child, evidence is eligible, or a lifecycle claim is justified. Those are `T1.3` rules. The status report therefore returns `valid: true` after successful syntax parsing, an empty `findings` array, and `recommendation: null`. A parse failure exits `1` with exact path/line context; schema-version-1 JSON for structurally audited failure states begins with `T1.3`.

---

## File map

| File | Responsibility in this plan |
| --- | --- |
| `.codex/skills/backlog-status/scripts/backlog/__init__.py` | Supported internal imports for the repository-local script package. |
| `.codex/skills/backlog-status/scripts/backlog/model.py` | Frozen typed roadmap, backlog, artifact, report, finding, recommendation, and Git models. |
| `.codex/skills/backlog-status/scripts/backlog/parse.py` | Exact managed-Markdown and governance-metadata parsing with source context. |
| `.codex/skills/backlog-status/scripts/backlog/report.py` | Dependency-readiness derivation, read-only Git observation, human rendering, and exact JSON serialization. |
| `.codex/skills/backlog-status/scripts/backlog_status.py` | Thin `status` / `status --json` command entry point. |
| `tests/fixtures/backlog_status/valid/` | Minimal valid roadmap, backlog, design, and plan fixture repository. |
| `tests/test_backlog_status_model.py` | Frozen-model and value-vocabulary tests. |
| `tests/test_backlog_status_parse.py` | Valid and malformed parser-fixture tests. |
| `tests/test_backlog_status_report.py` | Dependency readiness, human output, Git observation, and schema-v1 JSON tests. |
| `tests/test_backlog_status_cli.py` | Command grammar, exit status, output stream, and current-repository integration tests. |
| `BACKLOG.md` | T1.2 lifecycle, draft/approved plan link, gates, evidence, and review boundary. |
| `HANDOFF.md` | Concise current-plan and lifecycle pointer, not a second state ledger. |
| `.superpowers/sdd/2026-08-16-t1-2-typed-backlog-status-reporting/` | Completion and one evidence artifact per T1.2 gate after implementation verification. |

Do not create `rules.py`, `edit.py`, or `SKILL.md` in this child. `T1.3` owns semantic rules, `T1.5` owns editing, and `T1.6` owns the user-triggering skill and session integration.

---

## Execution precondition

This draft is not executable until written review changes its metadata to `Status: approved`, records `Approval: 2026-08-16 — Jeff / tvproductions` (or the actual approval date), changes the `T1.2` backlog row to `planned`, and changes its plan link label from `[draft plan]` to `[plan]`.

At execution start, update these lifecycle values together:

```markdown
- Active child: `T1.2`.
| `T1.2` | Typed parser, status report, and versioned JSON | `in_progress` | `T1.1` | [design](docs/superpowers/specs/2026-08-09-xplane-fdau-backlog-status-skill-design.md) | [plan](docs/superpowers/plans/2026-08-16-xplane-fdau-typed-backlog-status-reporting.md) | 0/4 | — | — | — |
- **Status:** in_progress
```

Update `HANDOFF.md` to say that `T1.2` is selected and executing its approved plan, then run:

```text
uv run python -m unittest tests.test_backlog_governance -v
git diff --check
git add BACKLOG.md HANDOFF.md docs/superpowers/plans/2026-08-16-xplane-fdau-typed-backlog-status-reporting.md
git diff --cached --check
git commit -m "docs: start typed backlog status reporting"
```

Do not begin Task 1 while the plan remains draft or the child remains merely specified/planned.

---

### Task 1: Define the frozen typed status model

**Files:**

- Create: `.codex/skills/backlog-status/scripts/backlog/__init__.py`
- Create: `.codex/skills/backlog-status/scripts/backlog/model.py`
- Create: `tests/test_backlog_status_model.py`

**Interfaces:**

- Consumes: exact node kinds, lifecycle values, gate states, artifact metadata, finding shape, recommendation shape, and Git shape from the approved T1 design.
- Produces: immutable models `SourceLocation`, `Milestone`, `Epic`, `RoadmapChild`, `ReleaseGate`, `ExternalBoundary`, `Roadmap`, `GateItem`, `GateSummary`, `BacklogChild`, `BacklogReleaseGate`, `Backlog`, `SpecificationArtifact`, `PlanArtifact`, `HistoricalArtifact`, `Artifacts`, `Finding`, `Recommendation`, `RecentCommit`, `GitState`, `RepositorySnapshot`, and `StatusReport`.

- [ ] **Step 1: Write failing immutability and vocabulary tests**

Create `tests/test_backlog_status_model.py`. Insert the script directory without importing `.codex` as a Python package, then assert construction, frozen behavior, tuple preservation, and exact controlled vocabularies:

```python
from __future__ import annotations

from dataclasses import FrozenInstanceError
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / ".codex/skills/backlog-status/scripts"
sys.path.insert(0, str(SCRIPTS))

from backlog.model import (  # noqa: E402
    CHILD_STATUSES,
    GATE_STATES,
    NODE_KINDS,
    BacklogChild,
    GateSummary,
    RoadmapChild,
    SourceLocation,
)


class BacklogStatusModelTests(unittest.TestCase):
    def test_controlled_vocabularies_are_exact(self) -> None:
        self.assertEqual(
            ("milestone", "epic", "local_child", "release_gate", "external_boundary"),
            NODE_KINDS,
        )
        self.assertEqual(
            (
                "queued",
                "designing",
                "specified",
                "planned",
                "in_progress",
                "implemented",
                "reviewed",
                "verified",
                "blocked",
                "deferred",
                "released",
            ),
            CHILD_STATUSES,
        )
        self.assertEqual(("waiting", "ready", "satisfied"), GATE_STATES)

    def test_models_are_frozen_and_preserve_tuple_order(self) -> None:
        location = SourceLocation("ROADMAP.md", 12)
        child = RoadmapChild(
            id="T1.2",
            kind="local_child",
            epic="T1",
            title="Typed parser, status report, and versioned JSON",
            dependencies=("T1.1",),
            external_prerequisite=None,
            source=location,
        )
        backlog_child = BacklogChild(
            id="T1.2",
            status="specified",
            dependencies=("T1.1",),
            specification="docs/superpowers/specs/t1.md",
            plan=None,
            gates=GateSummary(0, 4, ()),
            review_evidence=None,
            resume_state=None,
            reason=None,
            dependency_ready=True,
            source=SourceLocation("BACKLOG.md", 20),
        )
        self.assertEqual(("T1.1",), child.dependencies)
        self.assertTrue(backlog_child.dependency_ready)
        with self.assertRaises(FrozenInstanceError):
            child.title = "changed"  # type: ignore[misc]


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the model test to prove RED**

Run:

```text
uv run python -m unittest tests.test_backlog_status_model -v
```

Expected: import fails because `backlog.model` does not exist.

- [ ] **Step 3: Implement the exact frozen model family**

Create `.codex/skills/backlog-status/scripts/backlog/model.py` with string `TypeAlias` vocabularies and `@dataclass(frozen=True, slots=True)` models. Use these exact primitive aliases and representative definitions:

```python
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal, TypeAlias


NodeKind: TypeAlias = Literal["milestone", "epic", "local_child", "release_gate", "external_boundary"]
ChildStatus: TypeAlias = Literal[
    "queued", "designing", "specified", "planned", "in_progress",
    "implemented", "reviewed", "verified", "blocked", "deferred", "released",
]
GateState: TypeAlias = Literal["waiting", "ready", "satisfied"]
Severity: TypeAlias = Literal["error", "warning"]
Action: TypeAlias = Literal[
    "refine_spec", "request_spec_review", "write_plan", "execute_plan",
    "request_review", "verify", "wait",
]

NODE_KINDS = ("milestone", "epic", "local_child", "release_gate", "external_boundary")
CHILD_STATUSES = (
    "queued", "designing", "specified", "planned", "in_progress",
    "implemented", "reviewed", "verified", "blocked", "deferred", "released",
)
GATE_STATES = ("waiting", "ready", "satisfied")


@dataclass(frozen=True, slots=True)
class SourceLocation:
    path: str
    line: int


@dataclass(frozen=True, slots=True)
class RoadmapChild:
    id: str
    kind: Literal["local_child"]
    epic: str
    title: str
    dependencies: tuple[str, ...]
    external_prerequisite: str | None
    source: SourceLocation


@dataclass(frozen=True, slots=True)
class GateSummary:
    satisfied: int
    total: int
    items: tuple[GateItem, ...]


@dataclass(frozen=True, slots=True)
class BacklogChild:
    id: str
    status: ChildStatus
    dependencies: tuple[str, ...]
    specification: str | None
    plan: str | None
    gates: GateSummary
    review_evidence: str | None
    resume_state: ChildStatus | None
    reason: str | None
    dependency_ready: bool
    source: SourceLocation


@dataclass(frozen=True, slots=True)
class Finding:
    code: str
    severity: Severity
    path: str
    line: int | None
    node: str | None
    gate: int | None
    message: str


@dataclass(frozen=True, slots=True)
class StatusReport:
    schema_version: int
    repository: str
    valid: bool
    roadmap: Roadmap
    backlog: Backlog
    artifacts: Artifacts
    findings: tuple[Finding, ...]
    recommendation: Recommendation | None
    git: GitState
```

Define every model with these exact fields and order; all tuple fields use immutable tuples:

| Model | Fields |
| --- | --- |
| `SourceLocation` | `path: str`, `line: int` |
| `Milestone` | `id: str`, `kind: Literal["milestone"]`, `title: str`, `source: SourceLocation` |
| `Epic` | `id: str`, `kind: Literal["epic"]`, `title: str`, `children: tuple[str, ...]`, `source: SourceLocation` |
| `RoadmapChild` | `id`, `kind`, `epic`, `title`, `dependencies`, `external_prerequisite`, `source` exactly as shown above |
| `ReleaseGate` | `id: str`, `kind: Literal["release_gate"]`, `title: str`, `dependencies: tuple[str, ...]`, `source: SourceLocation` |
| `ExternalBoundary` | `id: str`, `kind: Literal["external_boundary"]`, `title: str`, `owner: str`, `handoff_condition: str`, `source: SourceLocation` |
| `Roadmap` | `milestones: tuple[Milestone, ...]`, `epics: tuple[Epic, ...]`, `local_children: tuple[RoadmapChild, ...]`, `release_gates: tuple[ReleaseGate, ...]`, `external_boundaries: tuple[ExternalBoundary, ...]` |
| `GateItem` | `ordinal: int`, `statement: str`, `satisfied: bool`, `evidence: tuple[str, ...]`, `source: SourceLocation` |
| `GateSummary` | `satisfied: int`, `total: int`, `items: tuple[GateItem, ...]` |
| `BacklogChild` | `id`, `status`, `dependencies`, `specification`, `plan`, `gates`, `review_evidence`, `resume_state`, `reason`, `dependency_ready`, `source` exactly as shown above |
| `BacklogReleaseGate` | `id: str`, `state: GateState`, `evidence: tuple[str, ...]`, `source: SourceLocation` |
| `Backlog` | `active_child: str | None`, `children: tuple[BacklogChild, ...]`, `release_gates: tuple[BacklogReleaseGate, ...]`, `source_path: str` |
| `SpecificationArtifact` | `path: str`, `governance: Literal["active"]`, `status: Literal["draft", "approved", "implemented", "superseded"]`, `epic: str`, `children: tuple[str, ...]`, `approval: str | None`, `source: SourceLocation` |
| `PlanArtifact` | `path: str`, `governance: Literal["active"]`, `status: Literal["draft", "approved", "in_progress", "completed", "superseded"]`, `child: str`, `source_specification: str`, `approval: str | None`, `completion_evidence: str | None`, `source: SourceLocation` |
| `HistoricalArtifact` | `path: str`, `governance: Literal["historical"]`, `status: Literal["completed", "superseded"]`, `disposition: str`, `source: SourceLocation` |
| `Artifacts` | `specifications: tuple[SpecificationArtifact, ...]`, `plans: tuple[PlanArtifact, ...]`, `historical: tuple[HistoricalArtifact, ...]` |
| `Finding` | `code`, `severity`, `path`, `line`, `node`, `gate`, `message` exactly as shown above |
| `Recommendation` | `action: Action`, `child: str | None`, `reason: str`, `command: str | None` |
| `RecentCommit` | `sha: str`, `subject: str` |
| `GitState` | `branch: str`, `dirty: bool`, `recent_commits: tuple[RecentCommit, ...]` |
| `RepositorySnapshot` | `root: Path`, `roadmap: Roadmap`, `backlog: Backlog`, `artifacts: Artifacts` |
| `StatusReport` | fields exactly as shown above |

Because `GateSummary` refers to `GateItem`, rely on `from __future__ import annotations` and define `GateItem` before constructing a summary. Internal-only `source` fields are retained for `T1.3` but are never serialized as report keys.

Create `backlog/__init__.py` with explicit imports of `RepositorySnapshot`, `StatusReport`, and `SourceLocation`, and set `__all__` to those three names. Do not expose a product-package API.

- [ ] **Step 4: Run focused static and model checks**

Run:

```text
uv run python -m unittest tests.test_backlog_status_model -v
uv run ruff check .codex/skills/backlog-status/scripts/backlog/model.py tests/test_backlog_status_model.py
uv run ruff format --check .codex/skills/backlog-status/scripts/backlog/model.py tests/test_backlog_status_model.py
uv run ty check .codex/skills/backlog-status/scripts/backlog/model.py tests/test_backlog_status_model.py
```

Expected: every command exits `0`.

- [ ] **Step 5: Commit the typed model**

```text
git add .codex/skills/backlog-status/scripts/backlog tests/test_backlog_status_model.py
git diff --cached --check
git commit -m "feat: define typed backlog status model"
```

Expected: one local commit; no push.

---

### Task 2: Parse the managed roadmap and backlog Markdown

**Files:**

- Create: `.codex/skills/backlog-status/scripts/backlog/parse.py`
- Create: `tests/fixtures/backlog_status/valid/ROADMAP.md`
- Create: `tests/fixtures/backlog_status/valid/BACKLOG.md`
- Create: `tests/test_backlog_status_parse.py`

**Interfaces:**

- Consumes: `SourceLocation`, roadmap node models, backlog models, exact managed headings/table headers, identity syntax, lifecycle vocabulary, Markdown links, gate task items, and current-position syntax.
- Produces: `MarkdownParseError`, `parse_roadmap(path: Path) -> Roadmap`, and `parse_backlog(path: Path) -> Backlog` with exact one-based source context.

- [ ] **Step 1: Create a minimal valid fixture repository**

Create fixture documents containing `M0`, epic `T1`, children `T1.1` and `T1.2`, release gate `G1`, and external boundary `I1.1`. Use the production table headers verbatim. The backlog fixture must use:

```markdown
- Active child: —.

| Child | Outcome | Status | Depends on | Spec | Plan | Gates | Review | Resume | Reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `T1.1` | Markdown authority contract and explicit inventory normalization | `verified` | `M0` | [design](docs/superpowers/specs/t1-design.md) | [plan](docs/superpowers/plans/t1-1.md) | 1/1 | [review](.superpowers/sdd/t1-1/review.md) | — | — |
| `T1.2` | Typed parser, status report, and versioned JSON | `specified` | `T1.1` | [design](docs/superpowers/specs/t1-design.md) | — | 0/1 | — | — | — |
```

Include one checked T1.1 gate with an evidence link, one open T1.2 gate, and a waiting `G1` dashboard row. Keep the fixture small while preserving every syntax family.

- [ ] **Step 2: Write failing valid and malformed parser tests**

In `tests/test_backlog_status_parse.py`, copy the valid fixture into a temporary directory for mutation cases. Assert:

```python
class ManagedMarkdownParseTests(unittest.TestCase):
    def test_valid_fixture_parses_into_typed_roadmap_and_backlog(self) -> None:
        roadmap = parse_roadmap(FIXTURE / "ROADMAP.md")
        backlog = parse_backlog(FIXTURE / "BACKLOG.md")
        self.assertEqual(("M0",), tuple(node.id for node in roadmap.milestones))
        self.assertEqual(("T1",), tuple(node.id for node in roadmap.epics))
        self.assertEqual(("T1.1", "T1.2"), tuple(node.id for node in roadmap.local_children))
        self.assertIsNone(backlog.active_child)
        self.assertEqual((1, 0), tuple(child.gates.satisfied for child in backlog.children))

    def test_malformed_selection_reports_exact_line(self) -> None:
        path = self.copy_backlog(replace=("- Active child: —.", "- Active child: T1.2."))
        with self.assertRaisesRegex(MarkdownParseError, r"BACKLOG.md:[0-9]+: active child"):
            parse_backlog(path)

    def test_malformed_inventory_cell_count_fails_closed(self) -> None:
        path = self.copy_backlog(replace=("| `T1.2` | Typed parser", "| `T1.2` |"))
        with self.assertRaisesRegex(MarkdownParseError, "inventory row requires 10 cells"):
            parse_backlog(path)

    def test_malformed_status_link_gate_and_identity_fail_with_context(self) -> None:
        replacements = (
            ("`specified`", "`unknown`", "invalid child status"),
            ("[design](docs/", "[design](../", "repository-relative link"),
            ("- [ ] Frozen", "- [?] Frozen", "gate task item"),
            ("`T1.2`", "T1.2", "identity cell"),
        )
        for old, new, message in replacements:
            with self.subTest(new=new):
                path = self.copy_backlog(replace=(old, new))
                with self.assertRaisesRegex(MarkdownParseError, message):
                    parse_backlog(path)
```

Also cover malformed roadmap table separators, standards rows with missing external-prerequisite cells, duplicate managed selection lines as a syntax ambiguity, invalid gate counts, and evidence links on unchecked gates. Duplicate node identities and cross-file drift are intentionally absent because they belong to `T1.3`.

- [ ] **Step 3: Run parser tests to prove RED**

Run:

```text
uv run python -m unittest tests.test_backlog_status_parse -v
```

Expected: import fails because `backlog.parse` does not exist.

- [ ] **Step 4: Implement strict reusable Markdown primitives**

Create `parse.py` with these exact public and internal boundaries:

```python
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

from backlog.model import Backlog, Roadmap, SourceLocation


_IDENTITY = re.compile(r"`([A-Z][0-9]+(?:\.[0-9]+)?)`")
_LINK = re.compile(r"\[([^]]+)]\(([^)]+)\)")
_SEPARATOR = re.compile(r"^\|(?:\s*:?-+:?\s*\|)+$")


class MarkdownParseError(ValueError):
    def __init__(self, path: Path, line: int, message: str) -> None:
        self.path = path
        self.line = line
        self.message = message
        super().__init__(f"{path.as_posix()}:{line}: {message}")


@dataclass(frozen=True, slots=True)
class _Line:
    number: int
    text: str


def _read(path: Path) -> tuple[_Line, ...]:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        raise MarkdownParseError(path, 1, f"cannot read UTF-8 Markdown: {error}") from error
    return tuple(_Line(index, line) for index, line in enumerate(text.splitlines(), start=1))


def _cells(path: Path, line: _Line, expected: int) -> tuple[str, ...]:
    if not line.text.startswith("|") or not line.text.endswith("|"):
        raise MarkdownParseError(path, line.number, "managed table row must begin and end with '|'")
    values = tuple(cell.strip() for cell in line.text.strip("|").split("|"))
    if len(values) != expected:
        raise MarkdownParseError(path, line.number, f"managed table row requires {expected} cells")
    return values


def _identity(path: Path, line: int, value: str) -> str:
    match = _IDENTITY.fullmatch(value)
    if match is None:
        raise MarkdownParseError(path, line, f"invalid identity cell: {value!r}")
    return match.group(1)
```

Add `_find_heading`, `_table`, `_dependencies`, `_optional_link`, `_status`, `_gate_count`, and `_gate_items`. Each helper receives the source path and line, accepts only the exact approved syntax, and raises `MarkdownParseError` rather than silently skipping malformed managed content.

- [ ] **Step 5: Implement roadmap parsing without semantic audit rules**

`parse_roadmap` must:

1. recognize milestone, local-child, standards-child, release-gate, and external-boundary tables only beneath their approved containing headings;
2. derive epic identity/title from exact `##` or `### <ID> — <title> epic` headings and retain children in source order;
3. normalize dependency cells into ordered tuples of exact IDs;
4. preserve an absent standards external prerequisite as `None` only when the cell is exactly `—`; and
5. retain `SourceLocation(path.relative-or-name, line)` for every parsed object.

Do not check duplicates, unknown dependencies, cross-kind collisions, cycles, or membership drift in this task.

- [ ] **Step 6: Implement backlog parsing without lifecycle proof**

`parse_backlog` must:

1. require exactly one managed active-child line and map `—` to `None`;
2. parse the exact ten-column inventory in source order;
3. parse backtick statuses against `CHILD_STATUSES`;
4. parse spec/plan/review/resume/reason cells without deciding whether they are lifecycle-appropriate;
5. join each inventory row with its matching acceptance-gate heading by ID and derive `GateSummary(satisfied, total, items)` from task items, folding indented continuation lines with single spaces while retaining the first task-item line as source context;
6. require the displayed gate count to equal the task-item count as syntax-local consistency, while leaving evidence eligibility to `T1.3`; and
7. parse the release-gate dashboard into typed rows.

Checked gates require one or more repository-relative evidence links after exact ` — Evidence:` text. Open gates contain no evidence suffix. A `Gates` cell of `—` becomes `GateSummary(0, 0, ())` and requires no acceptance section. Store `dependency_ready=False` during parsing; `report.py` derives it from the complete snapshot in Task 4.

- [ ] **Step 7: Run focused parser and static checks**

Run:

```text
uv run python -m unittest tests.test_backlog_status_model tests.test_backlog_status_parse -v
uv run ruff check .codex/skills/backlog-status/scripts/backlog tests/test_backlog_status_model.py tests/test_backlog_status_parse.py
uv run ruff format --check .codex/skills/backlog-status/scripts/backlog tests/test_backlog_status_model.py tests/test_backlog_status_parse.py
uv run ty check .codex/skills/backlog-status/scripts/backlog tests/test_backlog_status_model.py tests/test_backlog_status_parse.py
```

Expected: every command exits `0`.

- [ ] **Step 8: Commit the managed Markdown parser**

```text
git add .codex/skills/backlog-status/scripts/backlog/parse.py tests/fixtures/backlog_status tests/test_backlog_status_parse.py
git diff --cached --check
git commit -m "feat: parse backlog governance markdown"
```

Expected: one local commit; no push.

---

### Task 3: Parse governance specifications and plans

**Files:**

- Modify: `.codex/skills/backlog-status/scripts/backlog/parse.py`
- Create: `tests/fixtures/backlog_status/valid/docs/superpowers/specs/t1-design.md`
- Create: `tests/fixtures/backlog_status/valid/docs/superpowers/plans/t1-1.md`
- Modify: `tests/test_backlog_status_parse.py`

**Interfaces:**

- Consumes: exact active-design, active-plan, and historical metadata families.
- Produces: `parse_artifacts(root: Path) -> Artifacts` and `parse_repository(root: Path) -> RepositorySnapshot` with artifact arrays sorted by repository-relative path.

- [ ] **Step 1: Add valid active and historical artifact fixtures**

Create a valid active design covering `T1.1`, `T1.2` and a valid completed `T1.1` plan using the exact metadata order. Add one historical design and one historical plan with required dispositions. Fixture bodies may be a single explanatory paragraph because `T1.2` parses metadata, not semantic design/plan adherence.

- [ ] **Step 2: Write failing artifact-family tests**

Add tests that assert exact parsed values and path ordering, then table-drive these malformed cases:

```python
malformed = (
    ("missing-governance.md", "missing Governance metadata"),
    ("active-design-missing-owner.md", "active design metadata keys"),
    ("active-plan-multiple-child.md", "Roadmap child requires one identity"),
    ("historical-missing-disposition.md", "historical metadata keys"),
    ("approved-without-approval.md", "approved artifact requires Approval"),
    ("completed-without-evidence.md", "completed plan requires Completion evidence"),
)
```

These are metadata-shape failures. Whether a plan's child is covered by its source design remains `T1.3`.

- [ ] **Step 3: Run the artifact parser tests to prove RED**

Run:

```text
uv run python -m unittest tests.test_backlog_status_parse.ManagedMarkdownParseTests.test_governance_artifacts -v
```

Expected: failure because `parse_artifacts` does not exist.

- [ ] **Step 4: Implement metadata parsing and repository assembly**

Add these public functions:

```python
def parse_artifacts(root: Path) -> Artifacts:
    specifications: list[SpecificationArtifact] = []
    plans: list[PlanArtifact] = []
    historical: list[HistoricalArtifact] = []
    for directory, family in (
        (root / "docs/superpowers/specs", "specification"),
        (root / "docs/superpowers/plans", "plan"),
    ):
        for path in sorted(directory.glob("*.md")):
            parsed = _parse_artifact(root, path, family)
            if isinstance(parsed, HistoricalArtifact):
                historical.append(parsed)
            elif isinstance(parsed, SpecificationArtifact):
                specifications.append(parsed)
            else:
                plans.append(parsed)
    return Artifacts(tuple(specifications), tuple(plans), tuple(historical))


def parse_repository(root: Path) -> RepositorySnapshot:
    resolved = root.resolve()
    return RepositorySnapshot(
        root=resolved,
        roadmap=parse_roadmap(resolved / "ROADMAP.md"),
        backlog=parse_backlog(resolved / "BACKLOG.md"),
        artifacts=parse_artifacts(resolved),
    )
```

`_parse_artifact` must read one contiguous metadata block immediately after the title, require exact key sets and order, enforce controlled governance/status values, and normalize paths relative to `root` with `/`. It must enforce shape-local approval/completion presence but not source-spec existence, child coverage, lifecycle consistency, or evidence eligibility.

- [ ] **Step 5: Run parser, governance, and static checks**

Run:

```text
uv run python -m unittest tests.test_backlog_status_parse tests.test_backlog_governance -v
uv run ruff check .codex/skills/backlog-status/scripts/backlog tests/test_backlog_status_parse.py
uv run ruff format --check .codex/skills/backlog-status/scripts/backlog tests/test_backlog_status_parse.py
uv run ty check .codex/skills/backlog-status/scripts/backlog tests/test_backlog_status_parse.py
```

Expected: every command exits `0`; the existing governance tests still pass.

- [ ] **Step 6: Commit artifact parsing**

```text
git add .codex/skills/backlog-status/scripts/backlog/parse.py tests/fixtures/backlog_status tests/test_backlog_status_parse.py
git diff --cached --check
git commit -m "feat: parse backlog governance artifacts"
```

Expected: one local commit; no push.

---

### Task 4: Build the complete human status report and thin CLI

**Files:**

- Create: `.codex/skills/backlog-status/scripts/backlog/report.py`
- Create: `.codex/skills/backlog-status/scripts/backlog_status.py`
- Create: `tests/test_backlog_status_report.py`
- Create: `tests/test_backlog_status_cli.py`

**Interfaces:**

- Consumes: `RepositorySnapshot`, parsed child statuses/dependencies/gates/artifacts, and read-only Git commands.
- Produces: `with_dependency_readiness(snapshot: RepositorySnapshot) -> RepositorySnapshot`, `observe_git(root: Path, limit: int = 5) -> GitState`, `build_report(snapshot: RepositorySnapshot, git: GitState) -> StatusReport`, `render_human(report: StatusReport) -> str`, and `main(argv: list[str] | None = None, *, root: Path | None = None, stdout: TextIO | None = None, stderr: TextIO | None = None) -> int`.

- [ ] **Step 1: Write failing dependency-readiness and human-report tests**

Build expected output from the valid fixture and assert:

```python
class HumanStatusReportTests(unittest.TestCase):
    def test_dependency_readiness_uses_only_verified_dependencies(self) -> None:
        snapshot = with_dependency_readiness(parse_repository(FIXTURE))
        children = {child.id: child for child in snapshot.backlog.children}
        self.assertTrue(children["T1.2"].dependency_ready)

    def test_human_status_contains_every_node_child_artifact_gate_and_git_fact(self) -> None:
        snapshot = with_dependency_readiness(parse_repository(FIXTURE))
        git = GitState("main", False, (RecentCommit("abc1234", "fixture commit"),))
        output = render_human(build_report(snapshot, git))
        for value in ("M0", "T1", "T1.1", "T1.2", "G1", "I1.1"):
            self.assertIn(value, output)
        self.assertIn("Active child: —", output)
        self.assertIn("T1.2  specified  dependency-ready=yes  gates=0/1", output)
        self.assertIn("docs/superpowers/specs/t1-design.md", output)
        self.assertIn("Git: branch=main dirty=no", output)
        self.assertIn("Findings: none", output)
        self.assertIn("Recommendation: unavailable until T1.4", output)
```

Add a second fixture-state test where a dependency is `reviewed`, `implemented`, or `planned`; `dependency_ready` must remain false. `M0` is ready because it is the verified roadmap milestone named by the approved design, not because of Git history.

- [ ] **Step 2: Write failing CLI grammar and stream tests**

Load `backlog_status.py` with `importlib.util.spec_from_file_location`. In fixture-root CLI tests, patch the module's `observe_git` name to return `GitState("main", False, ())`; only the current-repository integration test uses real Git. Test:

```python
status = self.run_cli(["status"], root=FIXTURE)
self.assertEqual(0, status.code)
self.assertIn("Repository: xplane-fdau", status.stdout)
self.assertEqual("", status.stderr)

invalid = self.run_cli(["audit"], root=FIXTURE)
self.assertEqual(2, invalid.code)
self.assertIn("invalid choice", invalid.stderr)

malformed = self.run_cli(["status"], root=self.malformed_fixture())
self.assertEqual(1, malformed.code)
self.assertEqual("", malformed.stdout)
self.assertRegex(malformed.stderr, r"BACKLOG.md:[0-9]+:")
```

The parser must expose only `status`; `audit`, `next`, `select`, and other future commands remain invalid usage.

- [ ] **Step 3: Run report and CLI tests to prove RED**

Run:

```text
uv run python -m unittest tests.test_backlog_status_report tests.test_backlog_status_cli -v
```

Expected: imports fail because `report.py` and `backlog_status.py` do not exist.

- [ ] **Step 4: Implement dependency readiness and read-only Git observation**

Use `dataclasses.replace` to return a new frozen snapshot. A dependency is ready only when it is `M0` or its referenced backlog child has status `verified` or `released`; do not infer readiness from gate counts, plans, evidence paths, or Git.

Implement Git observation with exact commands and no writes:

```python
def _git(root: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ("git", "-C", str(root), *arguments),
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )
    return completed.stdout


def observe_git(root: Path, limit: int = 5) -> GitState:
    branch = _git(root, "branch", "--show-current").strip()
    dirty = bool(_git(root, "status", "--porcelain").strip())
    log = _git(root, "log", f"-{limit}", "--format=%H%x00%s")
    commits = tuple(
        RecentCommit(sha, subject)
        for line in log.splitlines()
        for sha, subject in (line.split("\x00", 1),)
    )
    return GitState(branch, dirty, commits)
```

Tests patch `subprocess.run` and assert only these read-only invocations occur.

- [ ] **Step 5: Implement complete deterministic human rendering**

`render_human` must include authority paths, active child, all five roadmap-kind inventories, every backlog child with status/readiness/gates/spec/plan/review/reason, release-gate state/evidence, all active and historical artifacts, findings, explicit unavailable recommendation, Git branch/dirty state, and newest-first recent commits. End with exactly one LF and never include a timestamp.

Use fixed labels and source order rather than terminal-width wrapping. Missing optional values render as `—`. This makes the report deterministic and diffable.

- [ ] **Step 6: Implement the thin status CLI**

Use this command boundary for the human form:

```python
def repository_root() -> Path:
    return Path(__file__).resolve().parents[4]


def main(
    argv: list[str] | None = None,
    *,
    root: Path | None = None,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
) -> int:
    output = sys.stdout if stdout is None else stdout
    errors = sys.stderr if stderr is None else stderr
    parser = argparse.ArgumentParser(prog="backlog-status")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("status", help="report repository delivery status")
    parser.parse_args(argv)
    selected_root = repository_root() if root is None else root
    try:
        snapshot = with_dependency_readiness(parse_repository(selected_root))
        report = build_report(snapshot, observe_git(selected_root))
    except (MarkdownParseError, OSError, subprocess.SubprocessError) as error:
        print(error, file=errors)
        return 1
    output.write(render_human(report))
    return 0
```

Task 5 adds the `--json` option and `render_json` import atomically with the serializer, so Task 4 never contains an unimplemented import or branch.

- [ ] **Step 7: Run focused report, CLI, and static checks**

Run:

```text
uv run python -m unittest tests.test_backlog_status_model tests.test_backlog_status_parse tests.test_backlog_status_report tests.test_backlog_status_cli -v
uv run ruff check .codex/skills/backlog-status/scripts tests/test_backlog_status_*.py
uv run ruff format --check .codex/skills/backlog-status/scripts tests/test_backlog_status_*.py
uv run ty check .codex/skills/backlog-status/scripts tests/test_backlog_status_*.py
```

Expected: all human-status tests pass. The JSON-specific test remains scheduled for Task 5; no audit or recommendation command exists.

- [ ] **Step 8: Commit the human status command**

```text
git add .codex/skills/backlog-status/scripts tests/test_backlog_status_report.py tests/test_backlog_status_cli.py
git diff --cached --check
git commit -m "feat: report human backlog status"
```

Expected: one local commit; no push.

---

### Task 5: Serialize exact schema-version-1 JSON and prove current-repository integration

**Files:**

- Modify: `.codex/skills/backlog-status/scripts/backlog/report.py`
- Modify: `.codex/skills/backlog-status/scripts/backlog_status.py`
- Modify: `tests/test_backlog_status_report.py`
- Modify: `tests/test_backlog_status_cli.py`

**Interfaces:**

- Consumes: `StatusReport` and every nested frozen model.
- Produces: `report_dict(report: StatusReport) -> dict[str, object]` and `render_json(report: StatusReport) -> str` with exact key order, two-space indentation, UTF-8-compatible Unicode, finite JSON values, and one final LF.

- [ ] **Step 1: Write the failing exact-JSON contract test**

Construct a small report from the valid fixture and assert the complete top-level key order:

```python
payload = json.loads(render_json(report), object_pairs_hook=dict)
self.assertEqual(
    [
        "schema_version",
        "repository",
        "valid",
        "roadmap",
        "backlog",
        "artifacts",
        "findings",
        "recommendation",
        "git",
    ],
    list(payload),
)
self.assertEqual(1, payload["schema_version"])
self.assertTrue(payload["valid"])
self.assertEqual([], payload["findings"])
self.assertIsNone(payload["recommendation"])
self.assertTrue(render_json(report).endswith("\n"))
self.assertFalse(render_json(report).endswith("\n\n"))
```

Assert the exact nested key order for every object family listed in the approved design. Compare the complete rendered fixture JSON to one inline expected string so extra keys, missing nulls, path separators, array order, escaping, and final-LF drift fail visibly.

- [ ] **Step 2: Write the failing JSON CLI test**

Run `main(["status", "--json"], root=FIXTURE, stdout=StringIO(), stderr=StringIO())`, assert exit `0`, empty stderr, parseable JSON, no timestamp field, and exact schema version. Verify every roadmap ID and backlog child is present in source order.

- [ ] **Step 3: Run the JSON tests to prove RED**

Run:

```text
uv run python -m unittest tests.test_backlog_status_report tests.test_backlog_status_cli -v
```

Expected: failure because `render_json` does not yet return the exact schema-v1 shape.

- [ ] **Step 4: Implement explicit ordered serialization**

Do not use `dataclasses.asdict`, because internal `source` fields and future fields must not leak into the wire contract. Build ordinary dictionaries in the exact insertion order from the design. The top-level implementation is:

```python
def report_dict(report: StatusReport) -> dict[str, object]:
    return {
        "schema_version": report.schema_version,
        "repository": report.repository,
        "valid": report.valid,
        "roadmap": _roadmap_dict(report.roadmap),
        "backlog": _backlog_dict(report.backlog),
        "artifacts": _artifacts_dict(report.artifacts),
        "findings": [_finding_dict(item) for item in report.findings],
        "recommendation": None if report.recommendation is None else _recommendation_dict(report.recommendation),
        "git": _git_dict(report.git),
    }


def render_json(report: StatusReport) -> str:
    return json.dumps(
        report_dict(report),
        ensure_ascii=False,
        allow_nan=False,
        indent=2,
    ) + "\n"
```

Every optional scalar key is emitted with `None`; no key is omitted. Arrays preserve roadmap order except artifacts (path order), findings (approved finding order once `T1.3` supplies them), and recent commits (newest first). Repository paths use `/`.

Add `status.add_argument("--json", action="store_true", dest="as_json")` to the Task 4 parser and change the final write to:

```python
output.write(render_json(report) if arguments.as_json else render_human(report))
```

Import `render_json` from `backlog.report` and restore `arguments = parser.parse_args(argv)` in the same change.

- [ ] **Step 5: Add the current-repository integration test**

In `tests/test_backlog_status_cli.py`, execute both forms against `ROOT`:

```python
human = self.run_cli(["status"], root=ROOT)
self.assertEqual(0, human.code, human.stderr)
self.assertIn("54 local children", human.stdout)

machine = self.run_cli(["status", "--json"], root=ROOT)
self.assertEqual(0, machine.code, machine.stderr)
payload = json.loads(machine.stdout)
self.assertTrue(payload["valid"])
self.assertEqual([], payload["findings"])
self.assertIsNone(payload["recommendation"])
self.assertEqual(54, len(payload["roadmap"]["local_children"]))
self.assertEqual(54, len(payload["backlog"]["children"]))
```

This proves the migrated repository parses and reports. It does not claim that `T1.3` semantic audit has run.

- [ ] **Step 6: Run the complete focused and repository quality set**

Run:

```text
uv run python -m unittest tests.test_backlog_status_model tests.test_backlog_status_parse tests.test_backlog_status_report tests.test_backlog_status_cli tests.test_backlog_governance -v
uv run ruff check .codex/skills/backlog-status/scripts tests/test_backlog_status_*.py
uv run ruff format --check .codex/skills/backlog-status/scripts tests/test_backlog_status_*.py
uv run ty check .codex/skills/backlog-status/scripts tests/test_backlog_status_*.py
uv run python tools/quality.py check
uv run mkdocs build --strict
git diff --check
```

Expected: every command exits `0`. The two documented status commands run successfully from the repository root and neither changes tracked files.

- [ ] **Step 7: Commit schema-v1 reporting**

```text
git add .codex/skills/backlog-status/scripts/backlog/report.py tests/test_backlog_status_report.py tests/test_backlog_status_cli.py
git diff --cached --check
git commit -m "feat: emit versioned backlog status json"
```

Expected: one local commit; no push.

---

### Task 6: Close T1.2 implementation and hand off independent review

**Files:**

- Create: `.superpowers/sdd/2026-08-16-t1-2-typed-backlog-status-reporting/gate-1.md`
- Create: `.superpowers/sdd/2026-08-16-t1-2-typed-backlog-status-reporting/gate-2.md`
- Create: `.superpowers/sdd/2026-08-16-t1-2-typed-backlog-status-reporting/gate-3.md`
- Create: `.superpowers/sdd/2026-08-16-t1-2-typed-backlog-status-reporting/gate-4.md`
- Create: `.superpowers/sdd/2026-08-16-t1-2-typed-backlog-status-reporting/completion.md`
- Modify: `BACKLOG.md`
- Modify: `HANDOFF.md`
- Modify: `docs/superpowers/plans/2026-08-16-xplane-fdau-typed-backlog-status-reporting.md`
- Modify: `tests/test_backlog_governance.py` only if exact lifecycle assertions require the post-closeout state.

**Interfaces:**

- Consumes: passing focused parser/report/CLI tests, explicit governance-tool static checks, complete repository quality, strict documentation, and current-repository status output.
- Produces: four eligible T1.2 gate-evidence files, child-level completion evidence, plan state `completed`, child state `implemented`, and an independent-review handoff. It does not produce review evidence or `verified` state.

- [ ] **Step 1: Run fresh final verification**

From a clean post-Task-5 candidate, run:

```text
uv run python -m unittest tests.test_backlog_status_model tests.test_backlog_status_parse tests.test_backlog_status_report tests.test_backlog_status_cli tests.test_backlog_governance -v
uv run ruff check .codex/skills/backlog-status/scripts tests/test_backlog_status_*.py
uv run ruff format --check .codex/skills/backlog-status/scripts tests/test_backlog_status_*.py
uv run ty check .codex/skills/backlog-status/scripts tests/test_backlog_status_*.py
uv run python .codex/skills/backlog-status/scripts/backlog_status.py status
uv run python .codex/skills/backlog-status/scripts/backlog_status.py status --json
uv run python tools/quality.py check
uv run mkdocs build --strict
git diff --check
```

Expected: every command exits `0`; human output inventories every node and child, JSON has schema version `1`, `valid: true`, empty findings, null recommendation, and neither command changes repository state.

- [ ] **Step 2: Inspect the four acceptance subjects directly**

Run:

```text
git diff --exit-code
git status --short
uv run python -m unittest tests.test_backlog_status_parse -v
uv run python -m unittest tests.test_backlog_status_report.HumanStatusReportTests -v
uv run python -m unittest tests.test_backlog_status_report.JsonStatusReportTests -v
uv run python -m unittest tests.test_backlog_status_cli.CurrentRepositoryStatusTests -v
```

Expected: the pre-closeout tree is clean and each focused acceptance group passes independently.

- [ ] **Step 3: Create exact gate and completion evidence**

Create five evidence files using the approved evidence metadata. Use subjects:

```text
gate-1.md: Frozen typed model and strict Markdown parser fixtures
gate-2.md: Complete human repository status report
gate-3.md: Exact schema-version-1 JSON report
gate-4.md: Current-repository parse and report integration
completion.md: T1.2 implementation-plan completion
```

Each gate file uses its matching positive ordinal, `Kind: verification`, `Result: passed`, the actual verification date, and a body naming the exact commands from Steps 1–2. `completion.md` uses `Gate: —`. Do not create review evidence.

- [ ] **Step 4: Attach evidence without claiming independent review**

In `BACKLOG.md`:

- change only the `T1.2` status from `in_progress` to `implemented`;
- change its gate count from `0/4` to `4/4`;
- leave its approved plan link target unchanged;
- leave `Review` as `—`;
- keep `T1.2` selected for review; and
- check the four T1.2 gates and append their matching evidence links.

In this plan's metadata, set:

```markdown
- **Status:** completed
- **Approval:** 2026-08-16 — Jeff / tvproductions
- **Completion evidence:** `.superpowers/sdd/2026-08-16-t1-2-typed-backlog-status-reporting/completion.md`
```

Update `HANDOFF.md` to state that T1.2 is implemented with four committed gates and awaits independent review. Do not claim `reviewed`, `verified`, or release authorization.

- [ ] **Step 5: Stage and verify evidence eligibility**

Run:

```text
git add BACKLOG.md HANDOFF.md docs/superpowers/plans/2026-08-16-xplane-fdau-typed-backlog-status-reporting.md .superpowers/sdd/2026-08-16-t1-2-typed-backlog-status-reporting tests/test_backlog_governance.py
git diff --cached --check
git diff --cached --name-status
git diff --check
```

Expected: all five evidence files are in the index, none has an unstaged byte change, and only T1.2 closeout/evidence state plus any exact lifecycle assertion is staged.

- [ ] **Step 6: Re-run verification against the staged closeout state**

Repeat every command from Step 1. Expected: every command exits `0`, and the status outputs now report T1.2 as `implemented`, selected, and `4/4` without inventing review or recommendation.

- [ ] **Step 7: Commit the T1.2 implementation closeout**

```text
git commit -m "docs: complete typed backlog status reporting"
git status --short --branch
```

Expected: the commit succeeds, the worktree is clean, and no push occurs. Report T1.2 as implemented and awaiting independent review.

- [ ] **Step 8: Request independent review and verify after accepted fixes**

Use `requesting-code-review` over the T1.2 merge-base-to-HEAD diff. Resolve accepted load-bearing findings through `receiving-code-review`, with `systematic-debugging` and test-first fixes where applicable. Re-run Steps 1–7 after the last accepted fix. Only after accepted review evidence is committed may the backlog move through `reviewed` to `verified` with all four gate evidence files unchanged or deliberately regenerated.

---

## Plan self-review

- **Specification coverage:** Task 1 covers frozen typed models; Tasks 2–3 cover valid/malformed strict parsing for roadmap, backlog, and governance artifacts; Task 4 covers complete human status and read-only Git observation; Task 5 covers exact schema-v1 JSON and current-repository integration; Task 6 supplies one evidence artifact per acceptance gate and preserves independent review.
- **Scope boundary:** No task implements semantic audit/adherence, cycle detection, lifecycle proof, next-action selection, mutation, skill triggers, hygiene integration, Git synchronization, product runtime behavior, network behavior, or release behavior.
- **Type/name consistency:** Parser outputs feed `RepositorySnapshot`; readiness returns a replaced snapshot; `build_report` produces `StatusReport`; both renderers consume only `StatusReport`; the CLI depends only on those public functions.
- **Wire consistency:** Internal `SourceLocation` fields never appear in JSON. Every documented JSON key is explicit, ordered, and present; optional scalar values serialize as null.
- **Incomplete-instruction scan:** Every task names exact files, commands, expected results, interfaces, lifecycle transitions, and verification evidence.
- **Test framework:** Every Python test command uses `unittest`; pytest is neither required nor permitted.
