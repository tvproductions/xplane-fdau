# xplane-fdau Backlog Authority and Inventory Normalization Implementation Plan

- **Governance:** active
- **Status:** in_progress
- **Date:** 2026-08-15
- **Roadmap child:** `T1.1`
- **Source specification:** `docs/superpowers/specs/2026-08-09-xplane-fdau-backlog-status-skill-design.md`
- **Approval:** 2026-08-15 — Jeff / tvproductions
- **Completion evidence:** —

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Establish the exact Markdown authority, inventory, and governance-metadata contracts required by `T1.1` without implementing the later backlog parser, audit command, mutation engine, or workflow skills.

**Architecture:** Keep `ROADMAP.md` authoritative for node identity, kind, order, and dependencies, and consolidate all mutable local-child delivery state into one exact table in `BACKLOG.md`. Protect this hand-authored contract with focused standard-library tests that inspect only the current repository documents; production parsing and reporting remain reserved for `T1.2`. Normalize every existing specification and plan to either the active or historical metadata family, then close the four `T1.1` gates with committed Markdown evidence.

**Tech Stack:** Markdown, Python 3.12+ standard library, Python `unittest`, `uv`, Ruff, ty, coverage, Bandit, detect-secrets, MkDocs, and Git.

## Global Constraints

- Read `HANDOFF.md`, `ROADMAP.md`, `BACKLOG.md`, the parent architecture, the completed migration specification and plan, and the approved T1 design before editing.
- Use Python's `unittest` framework only; pytest is prohibited.
- Keep the distributed `xplane_fdau` runtime standard-library-only and do not add a runtime or tooling dependency on q4xpcc, xpwebapi, XPPython3, XPLM, or a network client.
- Treat q4xpcc only as recorded design input; do not copy its backlog implementation.
- Modify only Markdown governance documents, focused repository tests, and `.superpowers/sdd/` evidence in this child.
- Do not implement a production parser, status command, audit command, next-action selector, mutation command, `repo-hygiene`, or guarded Git synchronization in `T1.1`.
- Do not push, tag, publish, create a release, or mark version `0.1.0` released.
- Preserve the approved T1.1 gate text byte-for-byte apart from Markdown line wrapping before attaching evidence.

---

## File map

| File | Responsibility in this plan |
| --- | --- |
| `ROADMAP.md` | Exact, nonoverlapping node-kind tables; explicit dependency identities; no mutable status. |
| `BACKLOG.md` | The one active-child selection, one complete local-child inventory, acceptance gates, release-gate dashboard, and release prohibition. |
| `tests/test_backlog_governance.py` | Focused current-repository contract tests; test-only Markdown helpers, not the T1.2 production parser. |
| `docs/superpowers/specs/*.md` | Active-design or historical-design metadata normalization. |
| `docs/superpowers/plans/*.md` | Active-plan or historical-plan metadata normalization, including this T1.1 plan. |
| `.superpowers/sdd/2026-08-15-t1-1-backlog-authority-normalization/*.md` | One evidence file per T1.1 gate plus child-level completion evidence. |
| `HANDOFF.md` | Concise pointer to the approved plan and eventual implemented-awaiting-review state; never a second status ledger. |

The test module intentionally has no reusable production API. `T1.2` will create the typed parser from its own approved plan instead of promoting these narrow test helpers by accident.

---

## Execution precondition

This draft is not executable until written review records `Status: approved`, an
approval value in `YYYY-MM-DD — Jeff / tvproductions` form, and the linked
`T1.1` backlog state `planned`. At execution start, change the plan and `T1.1`
inventory row together to `in_progress`, update the concise `HANDOFF.md`
pointer, run `git diff --check`, and commit only those lifecycle fields with:

```text
git add BACKLOG.md HANDOFF.md docs/superpowers/plans/2026-08-15-xplane-fdau-backlog-authority-normalization.md
git diff --cached --check
git commit -m "docs: start backlog authority normalization"
```

Do not begin Task 1 from a draft or merely specified state.

---

### Task 1: Make roadmap node kinds and dependencies exact

**Files:**

- Create: `tests/test_backlog_governance.py`
- Modify: `ROADMAP.md`

**Interfaces:**

- Consumes: the approved roadmap table headers and node taxonomy in `docs/superpowers/specs/2026-08-09-xplane-fdau-backlog-status-skill-design.md`.
- Produces: `roadmap_rows(header: tuple[str, ...]) -> list[tuple[str, ...]]` and `roadmap_child_rows() -> list[tuple[str, ...]]`, test-only extractors used by Task 2; exact roadmap child ordering and dependency cells with no ranges.

- [ ] **Step 1: Add the failing roadmap contract tests**

Create `tests/test_backlog_governance.py` with the following complete initial content:

```python
"""Contract tests for the hand-authored roadmap and backlog authorities."""

from __future__ import annotations

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
ROADMAP = ROOT / "ROADMAP.md"
BACKLOG = ROOT / "BACKLOG.md"

MILESTONE_HEADER = ("Milestone", "Outcome")
CHILD_HEADER = ("Child", "Outcome", "Depends on")
STANDARDS_HEADER = ("Child", "Outcome", "Depends on", "External prerequisite")
GATE_HEADER = ("Gate", "Outcome", "Depends on")
BOUNDARY_HEADER = ("Boundary", "Owner", "xplane-fdau handoff condition")
INVENTORY_HEADER = (
    "Child",
    "Outcome",
    "Status",
    "Depends on",
    "Spec",
    "Plan",
    "Gates",
    "Review",
    "Resume",
    "Reason",
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def table_rows(text: str, header: tuple[str, ...]) -> list[tuple[str, ...]]:
    lines = text.splitlines()
    expected = tuple(header)
    rows: list[tuple[str, ...]] = []
    for index, line in enumerate(lines):
        cells = tuple(cell.strip() for cell in line.strip().strip("|").split("|"))
        if cells != expected:
            continue
        for row in lines[index + 2 :]:
            if not row.startswith("|"):
                break
            values = tuple(cell.strip() for cell in row.strip().strip("|").split("|"))
            if len(values) != len(expected):
                break
            rows.append(values)
    return rows


def identity(cell: str) -> str:
    match = re.fullmatch(r"`([A-Z][0-9]+(?:\.[0-9]+)?)`", cell)
    if match is None:
        raise AssertionError(f"not an exact identity cell: {cell!r}")
    return match.group(1)


def roadmap_rows(header: tuple[str, ...]) -> list[tuple[str, ...]]:
    return table_rows(read_text(ROADMAP), header)


def roadmap_child_rows() -> list[tuple[str, ...]]:
    lines = read_text(ROADMAP).splitlines()
    rows: list[tuple[str, ...]] = []
    index = 0
    while index < len(lines):
        cells = tuple(cell.strip() for cell in lines[index].strip().strip("|").split("|"))
        if cells not in {CHILD_HEADER, STANDARDS_HEADER}:
            index += 1
            continue
        index += 2
        while index < len(lines) and lines[index].startswith("|"):
            values = tuple(cell.strip() for cell in lines[index].strip().strip("|").split("|"))
            rows.append(values)
            index += 1
    return rows


class RoadmapAuthorityTests(unittest.TestCase):
    def test_node_kinds_are_explicit_complete_and_nonoverlapping(self) -> None:
        milestones = [identity(row[0]) for row in roadmap_rows(MILESTONE_HEADER)]
        children = [identity(row[0]) for row in roadmap_child_rows()]
        gates = [identity(row[0]) for row in roadmap_rows(GATE_HEADER)]
        boundaries = [identity(row[0]) for row in roadmap_rows(BOUNDARY_HEADER)]

        self.assertEqual(["M0"], milestones)
        self.assertEqual(["G1"], gates)
        self.assertEqual(["I1.1", "I1.2", "I2.1", "F1.1", "F2.1"], boundaries)
        self.assertEqual(54, len(children))
        self.assertEqual(54, len(set(children)))
        kinds = [set(milestones), set(children), set(gates), set(boundaries)]
        for index, current in enumerate(kinds):
            for other in kinds[index + 1 :]:
                self.assertFalse(current & other)

    def test_authoritative_dependency_cells_use_exact_identities(self) -> None:
        rows = roadmap_child_rows()
        for row in rows:
            dependency_cell = row[2]
            self.assertNotRegex(dependency_cell, r"[–—-]`[A-Z]")
            for dependency in dependency_cell.split(", "):
                self.assertRegex(dependency, r"^`(?:M0|[A-Z][0-9]+\.[0-9]+)`$")

        by_child = {identity(row[0]): row[2] for row in rows}
        self.assertEqual("`C1.3`, `C1.4`, `C1.5`, `C2.4`", by_child["C3.1"])
        self.assertEqual("`A1.4`, `A1.5`, `A1.6`, `A1.7`, `A1.8`", by_child["A1.9"])
        self.assertEqual("`P1.2`, `P1.3`, `P1.4`", by_child["P1.5"])

    def test_roadmap_has_no_mutable_child_status_column(self) -> None:
        roadmap = read_text(ROADMAP)
        self.assertNotIn("| Child | Outcome | Status |", roadmap)
        self.assertIn("`BACKLOG.md` is the durable Superpowers entry point", roadmap)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the focused tests and confirm the range failure**

Run:

```text
uv run python -m unittest tests.test_backlog_governance.RoadmapAuthorityTests -v
```

Expected: `test_authoritative_dependency_cells_use_exact_identities` fails on the `C3.1`, `A1.9`, and `P1.5` range cells. The other two tests pass.

- [ ] **Step 3: Expand the three authoritative dependency ranges**

In `ROADMAP.md`, make these exact replacements:

```markdown
| `C3.1` | Raw-observation record and schema | `C1.3`, `C1.4`, `C1.5`, `C2.4` |
| `A1.9` | Acquisition-session orchestration and installed closure | `A1.4`, `A1.5`, `A1.6`, `A1.7`, `A1.8` |
| `P1.5` | Omission, default, conversion, and precision-loss report | `P1.2`, `P1.3`, `P1.4` |
```

Do not add status to a roadmap table and do not change the release-path or external-boundary meaning.

- [ ] **Step 4: Run the focused roadmap tests**

Run:

```text
uv run python -m unittest tests.test_backlog_governance.RoadmapAuthorityTests -v
```

Expected: all three roadmap tests pass.

- [ ] **Step 5: Commit the roadmap contract**

```text
git add ROADMAP.md tests/test_backlog_governance.py
git diff --cached --check
git commit -m "test: define roadmap authority contract"
```

Expected: one local commit; no push.

---

### Task 2: Consolidate every local child into the authoritative backlog inventory

**Files:**

- Modify: `tests/test_backlog_governance.py`
- Modify: `BACKLOG.md`

**Interfaces:**

- Consumes: `roadmap_rows(header)` and the exact node rows established in Task 1.
- Produces: exactly one `## Local child inventory` table with `INVENTORY_HEADER`, exact roadmap order/outcomes/dependencies, and all mutable delivery fields.

- [ ] **Step 1: Add failing selection and inventory tests**

Insert this class after `RoadmapAuthorityTests` and before the module's `if __name__ == "__main__"` block:

```python
class BacklogAuthorityTests(unittest.TestCase):
    def test_current_position_has_one_exact_selection_line(self) -> None:
        backlog = read_text(BACKLOG)
        selection_lines = [
            line for line in backlog.splitlines() if line.startswith("- Active child:")
        ]
        self.assertEqual(["- Active child: `T1.1`."], selection_lines)
        self.assertNotIn("Active child slice:", backlog)

    def test_inventory_matches_every_roadmap_child_once_in_order(self) -> None:
        roadmap = roadmap_child_rows()
        inventory = table_rows(read_text(BACKLOG), INVENTORY_HEADER)
        self.assertEqual(54, len(inventory))
        self.assertEqual(
            [(identity(row[0]), row[1], row[2]) for row in roadmap],
            [(identity(row[0]), row[1], row[3]) for row in inventory],
        )

    def test_inventory_excludes_nonchildren_and_range_rows(self) -> None:
        inventory = table_rows(read_text(BACKLOG), INVENTORY_HEADER)
        inventory_ids = [identity(row[0]) for row in inventory]
        excluded = {"M0", "G1", "I1.1", "I1.2", "I2.1", "F1.1", "F2.1"}
        self.assertFalse(set(inventory_ids) & excluded)
        self.assertEqual(len(inventory_ids), len(set(inventory_ids)))
        self.assertNotRegex("\n".join(row[0] for row in inventory), r"[–—]")

    def test_inventory_owns_complete_mutable_state_cells(self) -> None:
        inventory = table_rows(read_text(BACKLOG), INVENTORY_HEADER)
        allowed_statuses = {
            "`queued`",
            "`designing`",
            "`specified`",
            "`planned`",
            "`in_progress`",
            "`implemented`",
            "`reviewed`",
            "`verified`",
            "`blocked`",
            "`deferred`",
            "`released`",
        }
        for row in inventory:
            child, _outcome, status, dependencies, spec, plan, gates, review, resume, reason = row
            self.assertIn(status, allowed_statuses, child)
            self.assertRegex(dependencies, r"^`(?:M0|[A-Z][0-9]+\.[0-9]+)`(?:, `(?:M0|[A-Z][0-9]+\.[0-9]+)`)*$")
            self.assertTrue(spec == "—" or spec.startswith("[design](docs/superpowers/specs/"), child)
            self.assertTrue(
                plan == "—"
                or plan.startswith("[draft plan](docs/superpowers/plans/")
                or plan.startswith("[plan](docs/superpowers/plans/"),
                child,
            )
            self.assertRegex(gates, r"^(?:—|[0-9]+/[0-9]+)$")
            self.assertEqual("—", review)
            if status == "`blocked`":
                self.assertEqual("`queued`", resume)
                self.assertNotEqual("—", reason)
            else:
                self.assertEqual("—", resume)
                self.assertEqual("—", reason)

    def test_no_second_child_status_dashboard_remains(self) -> None:
        backlog = read_text(BACKLOG)
        self.assertEqual(1, backlog.count("| Child | Outcome | Status |"))
        for obsolete_heading in (
            "## Build-foundation child dashboard",
            "## Canonical-contract child dashboard",
            "## Future release-path child dashboard",
            "## Standards child dashboard",
            "## Repository governance tooling",
        ):
            self.assertNotIn(obsolete_heading, backlog)
        self.assertIn("## Release-gate dashboard", backlog)
        self.assertIn("## External consumer and downstream boundaries", backlog)
```

- [ ] **Step 2: Run the backlog tests and confirm the legacy-dashboard failures**

Run:

```text
uv run python -m unittest tests.test_backlog_governance.BacklogAuthorityTests -v
```

Expected: all five tests fail because the selection line is legacy text, there is no exact unified inventory, and several status dashboards still exist.

- [ ] **Step 3: Replace the status dashboards with one exact inventory**

In `BACKLOG.md`:

1. Replace the managed selection with exactly `- Active child: `T1.1`.`.
2. Add one `## Local child inventory` table immediately after the canonical release boundary.
3. Use the exact ten-column header from the approved design.
4. Add all 54 local children in the same order and with the same full outcome text as `ROADMAP.md`.
5. Expand the `C3.1`, `A1.9`, and `P1.5` dependency ranges to exact ordered IDs.
6. Remove the five legacy status dashboards while preserving every child acceptance-gate section under a single `## Local-child acceptance gates` heading.
7. Preserve the release-gate dashboard, external-boundary table, backlog rules, and release prohibition as report-only/non-child structures.

Populate mutable cells with this exact policy:

| Children | Status | Spec | Plan | Gates | Resume/Reason |
| --- | --- | --- | --- | --- | --- |
| `B1.1` | `specified` | source-layout design | existing draft source-layout plan | `0/5` | `—` / `—` |
| `C1.1` | `designing` | canonical-contract design | `—` | `0/4` | `—` / `—` |
| `C1.2`–`C4.3` | `queued` | canonical-contract design | `—` | `0/4` | `—` / `—` |
| `C4.4` | `queued` | canonical-contract design | `—` | `0/5` | `—` / `—` |
| `A1.1`–`A1.9`, `R1.1`–`R1.7`, `P1.1`–`P1.6`, `S1.1` | `queued` | `—` | `—` | `—` | `—` / `—` |
| `S2.1`, `S2.2`, `S3.1` | `blocked` | `—` | `—` | `—` | `queued` / `Licensed edition-pinned source is unavailable.` |
| `S4.1` | `blocked` | `—` | `—` | `—` | `queued` / `A licensed source and concrete use case are unavailable.` |
| `T1.1` | `specified` | backlog-status design | this draft plan | `0/4` | `—` / `—` |
| `T1.2`–`T1.4` | `specified` | backlog-status design | `—` | `0/4` | `—` / `—` |
| `T1.5`, `T1.6` | `specified` | backlog-status design | `—` | `0/5` | `—` / `—` |
| `T2.1`, `T3.1` | `specified` | local-workflow-skills design | `—` | `0/5` | `—` / `—` |

Use these exact link targets and labels:

```markdown
[design](docs/superpowers/specs/2026-08-09-src-layout-migration-design.md)
[draft plan](docs/superpowers/plans/2026-08-09-src-layout-migration.md)
[design](docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md)
[design](docs/superpowers/specs/2026-08-09-xplane-fdau-backlog-status-skill-design.md)
[draft plan](docs/superpowers/plans/2026-08-15-xplane-fdau-backlog-authority-normalization.md)
[design](docs/superpowers/specs/2026-08-15-xplane-fdau-local-workflow-skills-design.md)
```

Set `Review` to `—` for every row. Do not invent acceptance gates for children whose designs do not define them.

- [ ] **Step 4: Run the focused governance tests**

Run:

```text
uv run python -m unittest tests.test_backlog_governance -v
```

Expected: all eight tests from Tasks 1 and 2 pass.

- [ ] **Step 5: Inspect the authority diff and commit it**

Run:

```text
git diff -- ROADMAP.md BACKLOG.md tests/test_backlog_governance.py
git diff --check
```

Confirm that every local child appears exactly once in the inventory, every external boundary remains outside it, and no gate checkbox changed.

Then run:

```text
git add BACKLOG.md tests/test_backlog_governance.py
git diff --cached --check
git commit -m "docs: normalize backlog child inventory"
```

Expected: one local commit; no push.

---

### Task 3: Normalize every existing specification and plan metadata header

**Files:**

- Modify: `tests/test_backlog_governance.py`
- Modify: `docs/superpowers/specs/2026-08-08-xplane-fdr-core-design.md`
- Modify: `docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md`
- Modify: `docs/superpowers/specs/2026-08-09-xplane-fdau-identity-fdr-kernel-migration-design.md`
- Modify: `docs/superpowers/plans/2026-08-08-xplane-fdr-core.md`
- Modify: `docs/superpowers/plans/2026-08-09-xplane-fdau-identity-fdr-kernel-migration.md`

**Interfaces:**

- Consumes: active and historical metadata families from the approved T1 design.
- Produces: a deterministic metadata block at the start of every existing spec and plan; active artifacts compete for current governance, historical artifacts are preserved but excluded.

- [ ] **Step 1: Add failing governance-artifact tests**

Add these helpers after `roadmap_rows`:

```python
def metadata(path: Path) -> dict[str, str]:
    lines = read_text(path).splitlines()
    result: dict[str, str] = {}
    started = False
    for line in lines[1:]:
        if not started and not line:
            continue
        match = re.fullmatch(r"- \*\*([^*]+):\*\* (.+)", line)
        if match is None:
            if started:
                break
            continue
        started = True
        key, value = match.groups()
        result[key] = value
    return result
```

Add this class after `BacklogAuthorityTests`:

```python
class GovernanceArtifactTests(unittest.TestCase):
    def test_every_spec_uses_one_complete_governance_family(self) -> None:
        for path in sorted((ROOT / "docs/superpowers/specs").glob("*.md")):
            values = metadata(path)
            self.assertIn(values.get("Governance"), {"active", "historical"}, path)
            if values["Governance"] == "active":
                self.assertEqual(
                    {
                        "Governance",
                        "Status",
                        "Date",
                        "Decision owner",
                        "Roadmap epic",
                        "Roadmap children",
                        "Approval",
                    },
                    set(values),
                    path,
                )
                self.assertIn(values["Status"], {"draft", "approved", "implemented", "superseded"}, path)
            else:
                self.assertEqual({"Governance", "Status", "Disposition"}, set(values), path)
                self.assertIn(values["Status"], {"completed", "superseded"}, path)

    def test_every_plan_uses_one_complete_governance_family(self) -> None:
        for path in sorted((ROOT / "docs/superpowers/plans").glob("*.md")):
            values = metadata(path)
            self.assertIn(values.get("Governance"), {"active", "historical"}, path)
            if values["Governance"] == "active":
                self.assertEqual(
                    {
                        "Governance",
                        "Status",
                        "Date",
                        "Roadmap child",
                        "Source specification",
                        "Approval",
                        "Completion evidence",
                    },
                    set(values),
                    path,
                )
                self.assertIn(values["Status"], {"draft", "approved", "in_progress", "completed", "superseded"}, path)
            else:
                self.assertEqual({"Governance", "Status", "Disposition"}, set(values), path)
                self.assertIn(values["Status"], {"completed", "superseded"}, path)

    def test_active_artifact_assignments_match_current_roadmap_children(self) -> None:
        active_specs = {
            path.name: metadata(path)
            for path in sorted((ROOT / "docs/superpowers/specs").glob("*.md"))
            if metadata(path).get("Governance") == "active"
        }
        active_plans = {
            path.name: metadata(path)
            for path in sorted((ROOT / "docs/superpowers/plans").glob("*.md"))
            if metadata(path).get("Governance") == "active"
        }
        self.assertEqual(
            {
                "2026-08-09-src-layout-migration-design.md",
                "2026-08-09-xplane-fdau-backlog-status-skill-design.md",
                "2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md",
                "2026-08-15-xplane-fdau-local-workflow-skills-design.md",
            },
            set(active_specs),
        )
        self.assertEqual(
            {
                "2026-08-09-src-layout-migration.md",
                "2026-08-15-xplane-fdau-backlog-authority-normalization.md",
            },
            set(active_plans),
        )
        self.assertEqual("`T1.1`", active_plans["2026-08-15-xplane-fdau-backlog-authority-normalization.md"]["Roadmap child"])

    def test_historical_artifacts_name_their_disposition(self) -> None:
        historical_paths = (
            ROOT / "docs/superpowers/specs/2026-08-08-xplane-fdr-core-design.md",
            ROOT / "docs/superpowers/specs/2026-08-09-xplane-fdau-identity-fdr-kernel-migration-design.md",
            ROOT / "docs/superpowers/plans/2026-08-08-xplane-fdr-core.md",
            ROOT / "docs/superpowers/plans/2026-08-09-xplane-fdau-identity-fdr-kernel-migration.md",
        )
        for path in historical_paths:
            self.assertIn(metadata(path)["Status"], {"completed", "superseded"})
            self.assertNotEqual("—", metadata(path)["Disposition"])
```

- [ ] **Step 2: Run the artifact tests and confirm the legacy-header failures**

Run:

```text
uv run python -m unittest tests.test_backlog_governance.GovernanceArtifactTests -v
```

Expected: the tests fail for the two legacy core artifacts, the two completed migration artifacts, and the draft canonical-contract design because they do not yet use an exact governance family.

- [ ] **Step 3: Apply exact historical metadata to superseded core artifacts**

Immediately after the title in `docs/superpowers/specs/2026-08-08-xplane-fdr-core-design.md`, add:

```markdown
- **Governance:** historical
- **Status:** superseded
- **Disposition:** Replaced by `docs/superpowers/specs/2026-08-09-xplane-fdau-identity-fdr-kernel-migration-design.md` under `M0`.
```

Immediately after the title in `docs/superpowers/plans/2026-08-08-xplane-fdr-core.md`, add:

```markdown
- **Governance:** historical
- **Status:** superseded
- **Disposition:** Replaced by `docs/superpowers/plans/2026-08-09-xplane-fdau-identity-fdr-kernel-migration.md` under `M0`.
```

Keep both existing superseded/non-executable notices below the metadata.

- [ ] **Step 4: Apply exact historical metadata to completed migration artifacts**

Replace the legacy status/date/owner header in `docs/superpowers/specs/2026-08-09-xplane-fdau-identity-fdr-kernel-migration-design.md` with:

```markdown
- **Governance:** historical
- **Status:** completed
- **Disposition:** Completed under `M0`.
```

Immediately below that block, add:

```markdown
> **Historical completion:** Implemented and verified under `M0`, but version
> `0.1.0` remains unreleased.
```

Immediately after the title in `docs/superpowers/plans/2026-08-09-xplane-fdau-identity-fdr-kernel-migration.md`, add the same three-line historical metadata block and historical-completion notice. Preserve its completed task marks and execution history.

- [ ] **Step 5: Apply exact active metadata to the canonical-contract design**

Replace the existing short header in `docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md` with:

```markdown
- **Governance:** active
- **Status:** draft
- **Date:** 2026-08-09
- **Decision owner:** Jeff / tvproductions
- **Roadmap epic:** `C`
- **Roadmap children:** `C1.1`, `C1.2`, `C1.3`, `C1.4`, `C1.5`, `C2.1`, `C2.2`, `C2.3`, `C2.4`, `C3.1`, `C3.2`, `C3.3`, `C3.4`, `C3.5`, `C4.1`, `C4.2`, `C4.3`, `C4.4`
- **Approval:** —
```

Do not approve the canonical-contract design or change its technical content.

- [ ] **Step 6: Run focused governance and existing documentation tests**

Run:

```text
uv run python -m unittest tests.test_backlog_governance tests.test_documentation -v
```

Expected: the new governance tests pass. Update the existing migration-status assertion to require `- **Governance:** historical`, `- **Status:** completed`, `- **Disposition:** Completed under `M0`.`, and the exact historical-completion notice instead of the removed legacy status line. Keep the assertion that no draft status appears and do not weaken the unreleased boundary.

- [ ] **Step 7: Review and commit metadata normalization**

Run:

```text
git diff -- docs/superpowers/specs docs/superpowers/plans tests/test_backlog_governance.py tests/test_documentation.py
git diff --check
git add docs/superpowers/specs docs/superpowers/plans tests/test_backlog_governance.py tests/test_documentation.py
git diff --cached --check
git commit -m "docs: normalize governance artifact metadata"
```

Expected: one local commit. Confirm the draft T1.1 plan remains `draft`, the canonical design remains `draft`, completed/superseded content remains historical, and no product code changed.

---

### Task 4: Verify T1.1, attach gate evidence, and hand off independent review

**Files:**

- Create: `.superpowers/sdd/2026-08-15-t1-1-backlog-authority-normalization/gate-1.md`
- Create: `.superpowers/sdd/2026-08-15-t1-1-backlog-authority-normalization/gate-2.md`
- Create: `.superpowers/sdd/2026-08-15-t1-1-backlog-authority-normalization/gate-3.md`
- Create: `.superpowers/sdd/2026-08-15-t1-1-backlog-authority-normalization/gate-4.md`
- Create: `.superpowers/sdd/2026-08-15-t1-1-backlog-authority-normalization/completion.md`
- Modify: `BACKLOG.md`
- Modify: `HANDOFF.md`
- Modify: `docs/superpowers/plans/2026-08-15-xplane-fdau-backlog-authority-normalization.md`

**Interfaces:**

- Consumes: the passing T1.1 contract tests and clean full quality/documentation builds from Tasks 1–3.
- Produces: four eligible gate-evidence files, one child-level completion-evidence file, plan state `completed`, child state `implemented`, and an explicit independent-review handoff. It does not produce review evidence or `verified` state.

- [ ] **Step 1: Run the complete focused and repository verification set**

Run each command from the repository root:

```text
uv run python -m unittest tests.test_backlog_governance -v
uv run python tools/quality.py check
uv run mkdocs build --strict
git diff --check
```

Expected: every command exits `0`; the full quality command uses `unittest`, and no generated build artifact is staged.

- [ ] **Step 2: Inspect the four gate subjects directly**

Run:

```text
git grep -n "| Milestone | Outcome |\|| Child | Outcome | Depends on |\|| Gate | Outcome | Depends on |\|| Boundary | Owner | xplane-fdau handoff condition |" -- ROADMAP.md
git grep -n "^- Active child:\|^## Local child inventory\|^| Child | Outcome | Status |" -- BACKLOG.md
git grep -n "I1.1\|I1.2\|I2.1\|F1.1\|F2.1" -- BACKLOG.md
git grep -n "Governance:\|Disposition:" -- docs/superpowers/specs docs/superpowers/plans
```

Expected: roadmap kind headers are distinct; there is one exact selection and one exact inventory header; external boundaries occur only in the report-only boundary section; every spec and plan has a governance marker and every historical artifact has a disposition.

- [ ] **Step 3: Create exact gate and completion evidence**

Create the five files with the bodies below. The verification statements are assertions made only after Steps 1 and 2 pass.

`gate-1.md`:

```markdown
# Verification Evidence

- **Child:** `T1.1`
- **Gate:** `1`
- **Kind:** verification
- **Result:** passed
- **Date:** 2026-08-15
- **Subject:** Exact nonoverlapping roadmap node contracts

The focused governance tests, full quality gate, strict documentation build,
and direct roadmap-table inspection passed. Milestones, local children, release
gates, and external boundaries use distinct explicit table contracts and exact
dependency identities.
```

`gate-2.md`:

```markdown
# Verification Evidence

- **Child:** `T1.1`
- **Gate:** `2`
- **Kind:** verification
- **Result:** passed
- **Date:** 2026-08-15
- **Subject:** Single mutable delivery-state authority

The focused governance tests and direct Markdown inspection passed.
`BACKLOG.md` contains the only local-child delivery-state table; `ROADMAP.md`
retains identity, kind, order, and dependency authority without mutable status.
```

`gate-3.md`:

```markdown
# Verification Evidence

- **Child:** `T1.1`
- **Gate:** `3`
- **Kind:** verification
- **Result:** passed
- **Date:** 2026-08-15
- **Subject:** Complete explicit local-child inventory

The focused governance tests passed for all 54 roadmap local children in exact
roadmap order. Every child has one inventory row and the five external
boundaries remain report-only without local delivery status.
```

`gate-4.md`:

```markdown
# Verification Evidence

- **Child:** `T1.1`
- **Gate:** `4`
- **Kind:** verification
- **Result:** passed
- **Date:** 2026-08-15
- **Subject:** Complete governance metadata migration

The focused governance and documentation tests passed. Every existing design
and implementation plan uses the exact active metadata family or an explicit
historical completed/superseded disposition.
```

`completion.md`:

```markdown
# Verification Evidence

- **Child:** `T1.1`
- **Gate:** —
- **Kind:** verification
- **Result:** passed
- **Date:** 2026-08-15
- **Subject:** T1.1 plan completion

All approved implementation-plan tasks completed. The focused governance tests,
full repository quality gate, strict documentation build, and Markdown diff
checks passed. Independent review remains a separate lifecycle transition.
```

- [ ] **Step 4: Attach evidence without claiming independent review**

In `BACKLOG.md`:

- change only the `T1.1` inventory status from `specified` to `implemented`;
- change its gate count from `0/4` to `4/4`;
- change its plan link label from `[draft plan]` to `[plan]` without changing the target;
- leave `Review` as `—`;
- check the four `T1.1` gates and append one matching evidence link per ordinal, in order:

```markdown
[verification](.superpowers/sdd/2026-08-15-t1-1-backlog-authority-normalization/gate-1.md)
[verification](.superpowers/sdd/2026-08-15-t1-1-backlog-authority-normalization/gate-2.md)
[verification](.superpowers/sdd/2026-08-15-t1-1-backlog-authority-normalization/gate-3.md)
[verification](.superpowers/sdd/2026-08-15-t1-1-backlog-authority-normalization/gate-4.md)
```

Preserve each approved gate statement exactly before ` — Evidence:`. Leave the active child as `T1.1` so review resumes against the implemented child.

In this plan's metadata, set:

```markdown
- **Status:** completed
- **Approval:** 2026-08-15 — Jeff / tvproductions
- **Completion evidence:** [.superpowers/sdd/2026-08-15-t1-1-backlog-authority-normalization/completion.md](../../../.superpowers/sdd/2026-08-15-t1-1-backlog-authority-normalization/completion.md)
```

In `HANDOFF.md`, replace the T1.1 planning sentence with a concise statement that the plan is completed, the child is `implemented`, all four gates have committed evidence, and independent review is the next required action. Do not reproduce the full inventory.

- [ ] **Step 5: Stage and verify evidence eligibility**

Run:

```text
git add BACKLOG.md HANDOFF.md docs/superpowers/plans/2026-08-15-xplane-fdau-backlog-authority-normalization.md .superpowers/sdd/2026-08-15-t1-1-backlog-authority-normalization
git diff --cached --check
git diff --cached --name-status
git diff --check
```

Expected: all five evidence files are in the index, none has an unstaged byte change, and only T1.1 closeout/evidence documents are staged.

- [ ] **Step 6: Re-run verification against the staged closeout state**

Run:

```text
uv run python -m unittest tests.test_backlog_governance -v
uv run python tools/quality.py check
uv run mkdocs build --strict
```

Expected: every command exits `0`. If an exact contract test now expects the pre-closeout `specified`/`0/4` values, update it to assert the lifecycle-valid `implemented`/`4/4` state while retaining `Review = —`, then rerun the same commands.

- [ ] **Step 7: Commit the T1.1 implementation closeout**

```text
git add BACKLOG.md HANDOFF.md docs/superpowers/plans/2026-08-15-xplane-fdau-backlog-authority-normalization.md tests/test_backlog_governance.py .superpowers/sdd/2026-08-15-t1-1-backlog-authority-normalization
git diff --cached --check
git commit -m "docs: complete backlog authority normalization"
git status --short --branch
```

Expected: the commit succeeds, the worktree is clean, the branch is only locally ahead, and no push occurs. Report `T1.1` as implemented and awaiting independent review—not reviewed, verified, released, or authorized for publication.

---

## Plan self-review

- **Specification coverage:** Task 1 covers exact nonoverlapping roadmap kinds; Task 2 makes `BACKLOG.md` the single complete mutable child-state authority; Task 3 migrates every current governance artifact; Task 4 supplies one eligible evidence artifact per T1.1 gate and preserves the independent-review boundary.
- **Scope boundary:** The plan introduces no production parser, command, mutation engine, skill, runtime code, runtime dependency, network behavior, or release behavior. Those remain with `T1.2` and later children.
- **Type/name consistency:** The test-only helpers are consistently named `read_text`, `table_rows`, `identity`, `roadmap_rows`, and `metadata`; later tasks consume only those definitions.
- **Placeholder scan:** Every file, command, expected result, metadata value, link target, lifecycle transition, and evidence body needed for execution is explicit.
- **Test framework:** Every Python test command uses `unittest`; pytest is neither required nor permitted.
