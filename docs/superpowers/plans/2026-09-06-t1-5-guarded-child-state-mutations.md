# T1.5 Guarded Child-State and Gate-Evidence Mutations Implementation Plan

- **Governance:** active
- **Status:** in_progress
- **Date:** 2026-09-06
- **Roadmap child:** `T1.5`
- **Source specification:** `docs/superpowers/specs/2026-08-09-xplane-fdau-backlog-status-skill-design.md`
- **Approval:** 2026-09-06 — Jeff / tvproductions
- **Completion evidence:** —

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add dry-run-first, stale-safe commands that select a local child, move it through the exact lifecycle, suspend or resume it, and record or reopen acceptance-gate evidence by atomically editing only `BACKLOG.md`.

**Architecture:** Add an in-memory backlog override to the existing audit pipeline so every proposed document is fully parsed and audited before publication. A new focused `backlog.edit` module owns typed mutation plans, exact managed-Markdown edits, SHA-256 preconditions, and same-directory atomic replacement; the existing CLI only parses commands and renders the proposed diff plus post-change audit. Existing parser, structural, adherence, lifecycle, evidence, recommendation, and release-prohibition rules remain the semantic authorities.

**Tech Stack:** Python 3.12-compatible standard library, frozen dataclasses, `argparse`, `pathlib`, `hashlib`, `difflib`, `tempfile`, `stat`, `os.replace`, `unittest`, uv, Ruff, ty, Git, and MkDocs.

**Spec:** `docs/superpowers/specs/2026-08-09-xplane-fdau-backlog-status-skill-design.md`.

## Global Constraints

- `ROADMAP.md` remains the node identity, kind, order, and dependency authority; `BACKLOG.md` remains the only mutable delivery-state authority.
- Implement only child `T1.5`; T1.6 skill/session/hygiene/artifact integration, T2/T3 tooling, B1.1, canonical FDAU runtime work, and consumer adoption remain out of scope.
- Use Python's standard-library `unittest` framework exclusively; never add, invoke, or suggest pytest.
- Keep production implementation under `.codex/skills/backlog-status/scripts`; do not edit `xplane_fdau`, package dependencies, canonical contract code, q4xpcc, xpwebapi, XPPython3/XPLM integration, or another repository.
- Mutation commands edit only `BACKLOG.md`; they never edit a specification, plan, evidence artifact, roadmap, handoff, Git index, commit, branch, remote, tag, package, or release surface.
- Every mutation begins from a clean semantic audit, requires an expected selection/state/gate precondition, pins the initial `BACKLOG.md` SHA-256, validates the complete candidate in memory, and writes only with explicit `--apply`.
- Apply rechecks the pinned `BACKLOG.md` bytes and reruns the complete candidate audit against the then-current roadmap, governance artifacts, evidence/Git state, policy, and release prohibitions immediately before replacement; any error refuses publication and cleans up the unpublished partial.
- `--target-sha256`, when supplied, is exactly 64 lowercase hexadecimal characters and must match the bytes read at planning time; apply always rechecks the implicitly or explicitly pinned starting bytes immediately before publication.
- The CLI token `none` represents an empty selection. Stored Markdown continues to use the authoritative `- Active child: —.` form; `none` never enters `BACKLOG.md`.
- Transition options may fill the `Spec`, `Plan`, or `Review` cell needed by the requested target state, but may not alter outcome, dependencies, gates, resume data, or any unrelated cell.
- State changes use only the closed forward/reopen graph. `released` is never a mutation target, and suspended children use only `suspend`/`resume`.
- Gate evidence paths are nonempty, unique, sorted before rendering, repository-relative Markdown paths. Existing audit/evidence policy remains responsible for containment, regular-file, index, metadata, child/gate, kind/result, and optional HEAD eligibility.
- Mutation reasons are explicit command rationale, not a second history ledger. Suspension reasons are stored in `Reason`; reopen/resume reasons are rendered in the mutation summary and belong in the eventual Git review/commit record.
- Read and write UTF-8 strictly. Preserve every byte outside the exact managed selection line, inventory cells, or gate item; retain each edited line's LF/CRLF terminator and the document's final-line state.
- Create a uniquely named sibling temporary file, flush and `os.fsync()` it, close it before `os.replace()` for Windows compatibility, and attempt deterministic cleanup after every pre-publication failure.
- The original remains unchanged on every pre-publication failure. If replacement succeeds but the final audit fails, report that `BACKLOG.md` was published and do not retry or roll it back silently.
- Runtime remains standard-library-only, version `0.1.0` remains unreleased, and no push, tag, publication, GitHub release, or q4xpcc mutation is authorized.

## File Responsibilities

| File | Responsibility |
| --- | --- |
| `.codex/skills/backlog-status/scripts/backlog/parse.py` | Parse `BACKLOG.md` from its path or supplied in-memory UTF-8 text while retaining logical `BACKLOG.md` source locations |
| `.codex/skills/backlog-status/scripts/backlog/parse_sources.py` | Derive inventory, selection, and gate source locations from the same optional in-memory text |
| `.codex/skills/backlog-status/scripts/backlog/audit.py` | Run the existing complete repository audit against current or candidate backlog text |
| `.codex/skills/backlog-status/scripts/backlog/edit.py` (new) | Typed mutation requests/plans, exact byte edits, preconditions, candidate validation, diff rendering, and atomic publication |
| `.codex/skills/backlog-status/scripts/backlog_status.py` | Thin argparse surface and human rendering for six mutation commands |
| `tests/test_backlog_status_audit.py` | Candidate-audit equivalence, source-location, and no-write tests |
| `tests/test_backlog_status_edit.py` (new) | Selection, transitions, suspension, gates, hashes, byte preservation, atomic publication, failure cleanup, and Windows-lock regression tests |
| `tests/test_backlog_status_cli.py` | Exact command grammar, dry-run/apply output, exit status, current-repository integration, and no-Git-write checks |
| `tests/backlog_audit_support.py` | Focused fixture helpers for lifecycle-ready plans, review/completion evidence, and byte/newline cases |
| `tests/test_backlog_governance.py` | Exact T1.5 plan/lifecycle/evidence inventory assertions during closeout |
| `BACKLOG.md` | T1.5 selection, linked approved plan, lifecycle state, five gate links, review link, and final cleared selection |
| `HANDOFF.md` | Concise verified T1.5 result and exact T1.6 next action |
| `.superpowers/sdd/2026-09-06-t1-5-guarded-child-state-mutations/*.md` | Completion, accepted independent review, and five committed gate records |

### Task 1: In-memory candidate audit seam

**Files:** Modify `.codex/skills/backlog-status/scripts/backlog/parse.py`, `.codex/skills/backlog-status/scripts/backlog/parse_sources.py`, `.codex/skills/backlog-status/scripts/backlog/audit.py`, and `tests/test_backlog_status_audit.py`.

**Interfaces:** Extend `parse_backlog(path: Path, *, text: str | None = None) -> Backlog`, `parse_backlog_sources(path: Path, backlog: Backlog, *, text: str | None = None) -> BacklogSources`, `load_audit(root: Path, *, backlog_text: str | None = None) -> AuditLoad`, and `audit_repository(root: Path, *, backlog_text: str | None = None) -> AuditLoad`. Omitted text preserves every current caller and behavior; supplied text is interpreted as the logical `root / "BACKLOG.md"` without reading or writing that file.

- [ ] **Step 1: Write failing candidate-audit tests**

  Add tests that read the valid fixture backlog, pass the unchanged text through `audit_repository(root, backlog_text=text)`, and assert equality of snapshot backlog values, `AuditSources`, findings, and all `BACKLOG.md` source paths/line numbers with the ordinary filesystem audit. Pass a candidate with `T1.2` changed from `specified` to `planned` and assert the expected `lifecycle.plan` finding appears while the real `BACKLOG.md`, Git index, and `HEAD` bytes remain unchanged.

  Add an invalid candidate (`0/x`) and assert `backlog.gate-count` still reports path `BACKLOG.md`, its exact line, and node `T1.1`. The candidate text must not create a temporary file in the repository.

- [ ] **Step 2: Run RED**

  ```powershell
  uv run python -m unittest tests.test_backlog_status_audit -v
  ```

  Expected: FAIL because the four functions do not accept the in-memory keyword.

- [ ] **Step 3: Refactor the two readers without changing grammar**

  Change each private reader to accept optional text:

  ```python
  def _read(path: Path, *, text: str | None = None) -> tuple[_Line, ...]:
      if text is None:
          try:
              text = path.read_text(encoding="utf-8")
          except (OSError, UnicodeError) as error:
              raise MarkdownParseError(
                  path, 1, f"cannot read UTF-8 Markdown: {error}", code="input.unreadable"
              ) from error
      return tuple(_Line(index, line) for index, line in enumerate(text.splitlines(), start=1))
  ```

  Thread `text` only through `parse_backlog` and `parse_backlog_sources`. Continue passing the real logical `root / "BACKLOG.md"` path to every parser so source locations remain `BACKLOG.md`. Do not add text overrides to roadmap, specification, plan, policy, or evidence loading.

- [ ] **Step 4: Thread the override through the audit**

  Give `load_audit` and `audit_repository` keyword-only `backlog_text`. In the backlog branch call:

  ```python
  backlog = parse_backlog(backlog_path, text=backlog_text)
  backlog_sources = parse_backlog_sources(backlog_path, backlog, text=backlog_text)
  ```

  Leave the audit composition and finding order unchanged. The candidate must still use the actual repository's roadmap, governance artifacts, Git evidence, approved audit policy, and release-prohibition sources.

- [ ] **Step 5: Run GREEN and regression checks**

  ```powershell
  uv run python -m unittest tests.test_backlog_status_audit tests.test_backlog_status_parse tests.test_backlog_status_rules tests.test_backlog_status_adherence tests.test_backlog_status_lifecycle -v
  uv run ruff check .codex/skills/backlog-status/scripts/backlog/parse.py .codex/skills/backlog-status/scripts/backlog/parse_sources.py .codex/skills/backlog-status/scripts/backlog/audit.py tests/test_backlog_status_audit.py
  uv run ty check
  ```

  Expected: all pass; ordinary audit output is byte-identical to the pre-task result.

- [ ] **Step 6: Commit the candidate-audit seam**

  ```powershell
  git add .codex/skills/backlog-status/scripts/backlog/parse.py .codex/skills/backlog-status/scripts/backlog/parse_sources.py .codex/skills/backlog-status/scripts/backlog/audit.py tests/test_backlog_status_audit.py
  git commit -m "refactor: audit candidate backlog text"
  ```

### Task 2: Mutation plan and exact selection editing

**Files:** Create `.codex/skills/backlog-status/scripts/backlog/edit.py` and `tests/test_backlog_status_edit.py`; modify `tests/backlog_audit_support.py`.

**Interfaces:** Produce frozen `MutationPlan`, typed `MutationRefusal`, and `plan_selection(root: Path, child: str | None, *, expect_current: str | None, target_sha256: str | None = None) -> MutationPlan`. A plan carries the resolved root/target, exact original/candidate bytes and SHA-256 values, unified diff, semantic summary/rationale, and validated candidate `AuditLoad`; planning performs no write.

- [ ] **Step 1: Write failing model, hash, and selection tests**

  Import `backlog.edit` and assert its models are frozen. On a committed audit fixture, plan `none -> T1.2` and assert:

  ```python
  plan = plan_selection(root, "T1.2", expect_current=None)
  self.assertEqual(hashlib.sha256(original).hexdigest(), plan.original_sha256)
  self.assertEqual(hashlib.sha256(plan.candidate).hexdigest(), plan.candidate_sha256)
  self.assertIn("- Active child: `T1.2`.", plan.candidate.decode("utf-8"))
  self.assertIn("--- a/BACKLOG.md", plan.diff)
  self.assertIn("+++ b/BACKLOG.md", plan.diff)
  self.assertEqual((), plan.audit.findings)
  self.assertEqual(original, (root / "BACKLOG.md").read_bytes())
  ```

  Cover deselection, no-op selection refusal, unknown/nonlocal child, mismatched expected selection, malformed/lowercase hash, a syntactically valid stale hash, and a pre-existing audit error. Prove a warning-only audit remains actionable and the warning survives in the candidate audit. Error assertions use stable codes such as `mutation.expected-selection`, `mutation.target`, `mutation.target-sha256`, `mutation.stale`, and `mutation.audit`.

- [ ] **Step 2: Write failing byte-preservation tests**

  Exercise LF, CRLF, and no-final-newline fixture copies. For each, compare original and candidate byte lines and assert only the managed selection line changed, its original terminator is retained, and every prefix/suffix byte is exact. Add non-ASCII prose to prove strict UTF-8 round-trip. Add invalid UTF-8 and nonregular/symlink `BACKLOG.md` cases and require refusal before a mutation plan exists.

- [ ] **Step 3: Run RED**

  ```powershell
  uv run python -m unittest tests.test_backlog_status_edit -v
  ```

  Expected: FAIL because `backlog.edit` does not exist.

- [ ] **Step 4: Implement the frozen mutation core**

  Use these public shapes:

  ```python
  @dataclass(frozen=True, slots=True)
  class MutationPlan:
      root: Path
      target: Path
      original: bytes
      candidate: bytes
      original_sha256: str
      candidate_sha256: str
      diff: str
      summary: str
      rationale: str | None
      audit: AuditLoad


  class MutationRefusal(ValueError):
      def __init__(self, code: str, message: str) -> None:
          self.code = code
          super().__init__(message)
  ```

  Add private helpers that:

  - resolve only `root.resolve() / "BACKLOG.md"` and require a contained regular non-symlink file;
  - read exact bytes once and decode strict UTF-8;
  - compute lowercase SHA-256 and validate an optional caller pin;
  - reject any existing error finding before editing;
  - address a one-based source line with `splitlines(keepends=True)`;
  - replace line content while retaining its exact `\n`, `\r\n`, or absent terminator;
  - run `audit_repository(root, backlog_text=candidate.decode("utf-8"))` and reject candidate errors; and
  - render `difflib.unified_diff(original_lines, candidate_lines, fromfile="a/BACKLOG.md", tofile="b/BACKLOG.md")` without changing candidate bytes.

  `plan_selection` locates the single `AuditSources.selection` line, compares its typed current value with `expect_current`, validates a non-`None` target against `snapshot.roadmap.local_children`, and renders exactly one of:

  ```text
  - Active child: `T1.2`.
  - Active child: —.
  ```

- [ ] **Step 5: Run GREEN and focused quality**

  ```powershell
  uv run python -m unittest tests.test_backlog_status_edit tests.test_backlog_status_audit -v
  uv run ruff check .codex/skills/backlog-status/scripts/backlog/edit.py tests/test_backlog_status_edit.py tests/backlog_audit_support.py
  uv run ty check
  ```

  Expected: all pass and planning leaves repository and fixture authorities unchanged.

- [ ] **Step 6: Commit the selection planner**

  ```powershell
  git add .codex/skills/backlog-status/scripts/backlog/edit.py tests/test_backlog_status_edit.py tests/backlog_audit_support.py
  git commit -m "feat: plan guarded backlog selection"
  ```

### Task 3: Lifecycle transitions, suspension, and resume

**Files:** Modify `.codex/skills/backlog-status/scripts/backlog/edit.py`, `tests/test_backlog_status_edit.py`, and `tests/backlog_audit_support.py`.

**Interfaces:** Produce `plan_transition`, `plan_suspend`, and `plan_resume` with the exact signatures in Step 5 over the Task 2 mutation-plan pipeline. Optional transition links update only the specification, plan, or review cells; the candidate audit supplies all stage-specific semantic checks.

- [ ] **Step 1: Write the failing closed-graph matrix**

  Assert exactly these `(expected, target)` pairs are allowed:

  ```python
  allowed = {
      ("queued", "designing"),
      ("designing", "specified"),
      ("specified", "planned"),
      ("planned", "in_progress"),
      ("in_progress", "implemented"),
      ("implemented", "reviewed"),
      ("reviewed", "verified"),
      ("specified", "designing"),
      ("planned", "specified"),
      ("in_progress", "planned"),
      ("implemented", "in_progress"),
      ("reviewed", "implemented"),
      ("verified", "reviewed"),
  }
  ```

  Reject every other pair across the nonsuspended lifecycle, every transition from `blocked`/`deferred`, and every target `released` with `mutation.transition`. Refuse an expected status that differs from the parsed current status before candidate construction.

- [ ] **Step 2: Write failing positive transition and cell tests**

  Add fixture helpers that create exact draft/approved/in-progress/completed single-child plans and eligible completion/review evidence. Prove representative forward and reopening transitions pass only when the existing artifact state and dependencies support the candidate.

  For `queued -> designing`, permit `specification="docs/superpowers/specs/t1-design.md"`; for `specified -> planned`, permit `plan="docs/superpowers/plans/t1-2.md"`; for `implemented -> reviewed`, permit `review=".superpowers/sdd/t1-2/review.md"`. Preserve an existing link when its option is omitted. Reject a supplied link on an unrelated target, a pipe/newline-containing link, and simultaneous edits outside the target row. `reviewed -> implemented` clears `Review`; other reopen transitions preserve their still-valid earlier-stage links.

- [ ] **Step 3: Write failing suspend/resume tests**

  Cover every nonsuspended state through both `blocked` and `deferred`. Suspending must set `Status`, store the exact prior state in `Resume`, and store the nonempty reason. Resuming must require `--expect` to match the suspended state and `--resume` to match the stored resume state, then restore `Status` and clear both `Resume` and `Reason`.

  Reject empty, surrounding-whitespace, newline, carriage-return, and pipe-containing reasons. Assert the resume/reopen rationale is present in `MutationPlan.rationale` but is not appended elsewhere in Markdown.

- [ ] **Step 4: Run RED**

  ```powershell
  uv run python -m unittest tests.test_backlog_status_edit -v
  ```

  Expected: FAIL because the three lifecycle planners are absent.

- [ ] **Step 5: Implement exact inventory-cell replacement**

  Use the target child's `InventoryRowSource.source.line` and a helper that splits the already-valid managed row on `|`, replaces only named zero-based cells, and retains each untouched cell plus the edited cell's existing exterior whitespace. Implement:

  ```python
  def plan_transition(
      root: Path,
      child: str,
      target: ChildStatus,
      *,
      expect: ChildStatus,
      specification: str | None = None,
      plan: str | None = None,
      review: str | None = None,
      target_sha256: str | None = None,
  ) -> MutationPlan:
      """Plan one exact nonsuspended lifecycle transition."""


  def plan_suspend(
      root: Path,
      child: str,
      target: Literal["blocked", "deferred"],
      *,
      expect: ChildStatus,
      reason: str,
      target_sha256: str | None = None,
  ) -> MutationPlan:
      """Plan suspension while retaining the exact resume state."""


  def plan_resume(
      root: Path,
      child: str,
      *,
      expect: Literal["blocked", "deferred"],
      resume: ChildStatus,
      reason: str,
      target_sha256: str | None = None,
  ) -> MutationPlan:
      """Plan restoration of one suspended child."""
  ```

  Render link cells as `[design](path)`, `[plan](path)`, and `[review](path)`. Let the existing candidate audit prove artifact coverage, status, approval, completion, review, dependency, selection, gate, and release constraints; do not duplicate those policies in `edit.py`.

- [ ] **Step 6: Run GREEN and focused regression**

  ```powershell
  uv run python -m unittest tests.test_backlog_status_edit tests.test_backlog_status_lifecycle tests.test_backlog_status_adherence tests.test_backlog_status_rules -v
  uv run ruff check .codex/skills/backlog-status/scripts/backlog/edit.py tests/test_backlog_status_edit.py tests/backlog_audit_support.py
  uv run ty check
  ```

  Expected: all pass; exact lifecycle authority remains in `backlog.lifecycle` and the candidate audit.

- [ ] **Step 7: Commit lifecycle planning**

  ```powershell
  git add .codex/skills/backlog-status/scripts/backlog/edit.py tests/test_backlog_status_edit.py tests/backlog_audit_support.py
  git commit -m "feat: guard backlog lifecycle mutations"
  ```

### Task 4: Gate recording and reopening

**Files:** Modify `.codex/skills/backlog-status/scripts/backlog/edit.py`, `tests/test_backlog_status_edit.py`, and `tests/backlog_audit_support.py`.

**Interfaces:** Produce `plan_record_gate` and `plan_reopen_gate` with the exact signatures in Step 4. Both update the task item and the inventory's derived gate count in one candidate.

- [ ] **Step 1: Write failing gate-precondition and evidence tests**

  Prepare a `reviewed` T1.2 fixture with an open gate and staged, eligible gate evidence. Assert record-gate refuses a false `expect_open`, an already closed gate, zero/out-of-range ordinal, missing evidence, duplicate evidence, malformed paths, wrong child/gate/kind/result metadata, untracked evidence, and worktree bytes that differ from the index. Assert supplied evidence is rendered in lexical path order and candidate validation reports the existing evidence finding code without replacing it with a generic error.

- [ ] **Step 2: Write failing exact gate/count edit tests**

  Record the fixture gate and assert `0/1 -> 1/1`, `[ ] -> [x]`, and exact ` — Evidence: [verification](path)` rendering. Reopen it and assert `1/1 -> 0/1`, `[x] -> [ ]`, and complete removal of the evidence suffix while preserving the statement.

  Repeat with a wrapped gate item, LF, CRLF, and no final newline. Compare bytes to prove only the marker, evidence suffix, and gate-count cell changed. Reject reopening a verified child until the caller performs the explicit `verified -> reviewed` transition.

- [ ] **Step 3: Run RED**

  ```powershell
  uv run python -m unittest tests.test_backlog_status_edit -v
  ```

  Expected: FAIL because the gate planners are absent.

- [ ] **Step 4: Implement gate block and count edits**

  Use the parsed `GateItem.source.line` for the first physical line. The block ends immediately before the next task item, Markdown heading, or nonindented content. On record, change only the first marker and append the evidence suffix to the block's last content line. On reopen, remove the exact parsed evidence suffix and restore the open marker. Update inventory cell 6 from the recomputed satisfied/total count; never trust or increment the displayed count independently.

  Use these exact signatures:

  ```python
  def plan_record_gate(
      root: Path,
      child: str,
      ordinal: int,
      *,
      expect_open: bool,
      evidence: tuple[str, ...],
      target_sha256: str | None = None,
  ) -> MutationPlan:
      """Plan closing one open gate with eligible evidence."""


  def plan_reopen_gate(
      root: Path,
      child: str,
      ordinal: int,
      *,
      expect_closed: bool,
      reason: str,
      target_sha256: str | None = None,
  ) -> MutationPlan:
      """Plan reopening one closed gate with explicit rationale."""
  ```

  Sort evidence for deterministic output but reject duplicates. Preserve the current acceptance statement verbatim and let the full candidate audit enforce its match to the governing design.

- [ ] **Step 5: Run GREEN and evidence regressions**

  ```powershell
  uv run python -m unittest tests.test_backlog_status_edit tests.test_backlog_status_evidence tests.test_backlog_status_lifecycle tests.test_backlog_status_adherence -v
  uv run ruff check .codex/skills/backlog-status/scripts/backlog/edit.py tests/test_backlog_status_edit.py tests/backlog_audit_support.py
  uv run ty check
  ```

  Expected: all pass and the mutation layer contains no parallel evidence policy.

- [ ] **Step 6: Commit gate planning**

  ```powershell
  git add .codex/skills/backlog-status/scripts/backlog/edit.py tests/test_backlog_status_edit.py tests/backlog_audit_support.py
  git commit -m "feat: guard backlog gate evidence"
  ```

### Task 5: Atomic apply and mutation CLI

**Files:** Modify `.codex/skills/backlog-status/scripts/backlog/edit.py`, `.codex/skills/backlog-status/scripts/backlog_status.py`, `tests/test_backlog_status_edit.py`, and `tests/test_backlog_status_cli.py`.

**Interfaces:** Produce `publish_mutation(plan: MutationPlan) -> AuditLoad`. Expose `select`, `transition`, `record-gate`, `reopen-gate`, `suspend`, and `resume`; every command accepts `--target-sha256` and `--apply`, while omission of `--apply` renders the same validated dry-run without writing.

- [ ] **Step 1: Write failing publication tests**

  Assert `publish_mutation` re-reads the target and refuses a changed byte with `mutation.stale` before creating a partial. After constructing a valid plan, change a non-target authority so that the same candidate becomes invalid—for example, make its linked evidence bytes differ from the Git index—and assert a fresh candidate audit refuses publication with the original `BACKLOG.md` unchanged and the unpublished partial removed. Patch the write, flush, `os.fsync`, close, mode preservation, target recheck, fresh candidate audit, and `os.replace` seams to prove this order:

  ```text
  capture target mode -> initial target recheck -> create sibling -> write all bytes
  -> flush -> fsync -> close -> preserve mode -> final target recheck
  -> fresh candidate audit -> replace -> final audit
  ```

  Verify the sibling is in `BACKLOG.md.parent`, has a unique `.BACKLOG.md.*.tmp` name, preserves the original permission bits where supported, and no open handle reaches `os.replace`. The successful candidate is exact, the partial is absent, and the returned final audit has no error.

  Inject target-stat, create, short-write, flush, fsync, close, chmod, stale-recheck, fresh-candidate-audit, and replace failures. Before replacement, require original bytes unchanged and cleanup attempted. If cleanup also fails, retain primary-first failure context and report the exact partial path. Inject final-audit failure after a successful replacement and require a distinct published-state error that tells callers not to retry.

- [ ] **Step 2: Write failing CLI grammar tests**

  Require these forms, with `none` mapped to `None` only at the CLI boundary:

  ```powershell
  backlog-status select T1.2 --expect-current none
  backlog-status transition T1.2 planned --expect specified --plan docs/superpowers/plans/t1-2.md
  backlog-status record-gate T1.2 1 --expect-open --evidence .superpowers/sdd/t1-2/gate-1.md --evidence .superpowers/sdd/t1-2/gate-1-artifact.md
  backlog-status reopen-gate T1.2 1 --expect-closed --reason "Evidence contract changed"
  backlog-status suspend T1.2 blocked --expect in_progress --reason "Named prerequisite unavailable"
  backlog-status resume T1.2 --expect blocked --resume in_progress --reason "Prerequisite restored"
  ```

  Configure record-gate `--evidence` with `action="append"`; require one or more occurrences, convert them to the planner's tuple, reject duplicates after normalized repository-path comparison, and let the planner sort accepted paths lexically for deterministic Markdown. Every mutation form also accepts `--target-sha256 <64-lowercase-hex>` and `--apply`. Reject missing evidence, missing expected flags, `--expect-open=false`, `--expect-closed=false`, unknown statuses, invalid ordinals, `released` targets, mutation-only flags on read-only commands, and `--json` on mutations with usage status `2`.

- [ ] **Step 3: Write failing dry-run/apply integration tests**

  For each command, assert a valid dry-run returns `0`, writes UTF-8/LF output, includes mode, target, original/candidate SHA-256, summary/rationale, unified diff, and complete candidate audit, and leaves `BACKLOG.md`, index, `HEAD`, and every other file byte unchanged. Apply a selection in a disposable committed fixture, assert only `BACKLOG.md` changes, rerun ordinary audit, and assert Git index/HEAD are untouched.

  Domain refusals return `1` on stdout with stable `mutation.*` code and no traceback; argparse errors return `2` on stderr. Existing `status`, JSON status, `audit`, and `next` output remains unchanged.

- [ ] **Step 4: Run RED**

  ```powershell
  uv run python -m unittest tests.test_backlog_status_edit tests.test_backlog_status_cli -v
  ```

  Expected: FAIL because publication and mutation subcommands are absent.

- [ ] **Step 5: Implement Windows-safe publication**

  Capture `stat.S_IMODE(target.stat(follow_symlinks=False).st_mode)` after the target has been verified as a regular non-symlink file, then re-read the target and compare it with `plan.original` so an already-stale plan fails before temporary-file creation. Create the partial with `tempfile.mkstemp(prefix=f".{target.name}.", suffix=".tmp", dir=target.parent)`. Write through `os.fdopen(fd, "wb")`, verify the full byte count, flush, call `os.fsync(stream.fileno())`, and leave the context so the handle is closed before replacement. Apply the captured permission bits to the closed partial with `os.chmod`; where a platform cannot represent particular bits, assert preservation of every supported bit rather than silently skipping the operation.

  Re-read `target.read_bytes()` a second time immediately before publication and compare it with `plan.original`, then rerun `audit_repository(plan.root, backlog_text=plan.candidate.decode("utf-8"))` against the current non-target authorities. Any candidate-audit error is a pre-publication refusal. Only a matching target and error-free fresh candidate audit may proceed to `os.replace(partial, target)`.

  Catch pre-publication failures, close any owned descriptor/stream, and unlink only the uniquely owned partial with `Path.unlink()`. Never recursively delete and never touch a caller-supplied path. After replacement, call `audit_repository(plan.root)`; if that final audit contains an error, raise a published-state result without restoring old bytes.

- [ ] **Step 6: Compose the thin CLI**

  Add one helper that gives every mutation parser `--target-sha256` and `--apply`. Parse command-specific values and dispatch to the Task 2-4 plan functions. Add no mutation logic to `backlog_status.py`.

  Render:

  ```text
  Mutation: <summary>
  Mode: dry-run|applied
  Target: BACKLOG.md
  Original SHA-256: <digest>
  Candidate SHA-256: <digest>
  Rationale: <reason>              # only when supplied
  Diff:
  <unified diff>
  Post-change audit:
  <existing render_human report>
  ```

  For dry-run, build the report from `plan.audit`; for apply, use the fresh audit returned by `publish_mutation`. In both cases apply `with_dependency_readiness` to the audit snapshot before `build_report`, exactly as the current read-only path does, so candidate recommendations never use parser-default readiness. Preserve the executable's current UTF-8/LF stdout reconfiguration. Do not add mutation JSON in T1.5.

- [ ] **Step 7: Run GREEN and complete focused verification**

  ```powershell
  uv run python -m unittest tests.test_backlog_status_edit tests.test_backlog_status_cli tests.test_backlog_status_audit tests.test_backlog_status_parse tests.test_backlog_status_rules tests.test_backlog_status_adherence tests.test_backlog_status_lifecycle tests.test_backlog_status_evidence tests.test_backlog_status_next_action tests.test_backlog_status_report -v
  uv run ruff check .codex/skills/backlog-status/scripts tests/test_backlog_status_edit.py tests/test_backlog_status_cli.py tests/test_backlog_status_audit.py tests/backlog_audit_support.py
  uv run ty check
  ```

  Expected: all pass. Record that Windows exercised close-before-replace and cleanup behavior locally; Ubuntu remains unobserved until the configured CI job runs after a separately authorized push.

- [ ] **Step 8: Commit atomic CLI delivery**

  ```powershell
  git add .codex/skills/backlog-status/scripts/backlog/edit.py .codex/skills/backlog-status/scripts/backlog_status.py tests/test_backlog_status_edit.py tests/test_backlog_status_cli.py
  git commit -m "feat: apply guarded backlog mutations"
  ```

### Task 6: T1.5 lifecycle, dogfooding, independent review, and acceptance evidence

**Files:** Modify `BACKLOG.md`, `HANDOFF.md`, this plan, `tests/test_backlog_governance.py`, and current-repository assertions in `tests/test_backlog_status_cli.py`; create `.superpowers/sdd/2026-09-06-t1-5-guarded-child-state-mutations/completion.md`, `review.md`, and `gate-1.md` through `gate-5.md`.

**Interfaces:** The committed final `next` result is `T1.6`/`write_plan`, because T1.5 becomes verified and unselected. No runtime, C/A/R/P/S/F1, release-gate, or external-boundary state changes.

- [ ] **Step 1: Bootstrap the approved plan lifecycle manually through coherent states**

  After Jeff approves this plan, bootstrap it manually because T1.5 is the capability that creates mutation commands. Preserve these exact coherent states and run the existing `audit`, JSON `status`, and `next` after each numbered candidate:

  1. Set this plan to `approved` with the exact approval date/owner; link it from T1.5 and move only T1.5 `specified -> planned`.
  2. Select T1.5 while leaving its status `planned`.
  3. Change this plan to `in_progress` and T1.5 to `in_progress` in the same candidate so neither authority temporarily claims an incompatible stage.

  Do not claim the not-yet-implemented mutation tool performed its own bootstrap, and do not begin implementation until candidate 3 audits cleanly.

- [ ] **Step 2: Complete implementation and dogfood the first transition**

  Run:

  ```powershell
  uv run python -m unittest tests.test_backlog_status_edit tests.test_backlog_status_cli tests.test_backlog_status_audit -v
  uv run python -m unittest discover -v
  uv run python tools/quality.py check
  uv run python .codex/skills/backlog-status/scripts/backlog_status.py audit
  uv run python .codex/skills/backlog-status/scripts/backlog_status.py status --json
  uv run python .codex/skills/backlog-status/scripts/backlog_status.py next
  git diff --check
  ```

  Record commands, counts, coverage, Windows portability evidence, branch, and exact implementation revision in `completion.md`. Mark this plan `completed` with the completion path, stage both files, dry-run `transition T1.5 implemented --expect in_progress` with the printed target hash, then apply the identical pinned command. Audit and commit the implementation transition.

- [ ] **Step 3: Request independent review and close every finding**

  Use `superpowers:requesting-code-review` against the exact merge-base-to-implementation revision and review the complete T1.5 diff against the governing design and this plan. Record Critical, Important, and Minor findings in `review.md`. Apply accepted corrections with `superpowers:receiving-code-review`, `superpowers:systematic-debugging` when a failure is involved, and failing `unittest` first. Rerun affected verification and request rereview until no unresolved finding remains.

  Stage accepted review evidence, dry-run `transition T1.5 reviewed --expect implemented --review .superpowers/sdd/2026-09-06-t1-5-guarded-child-state-mutations/review.md`, apply it with the printed target hash, audit, and commit review plus state together.

- [ ] **Step 4: Create five exact gate records**

  Use the approved evidence metadata contract with these subjects:

  | Gate | Subject | Required proof |
  | --- | --- | --- |
  | 1 | Dry-run and explicit apply authority | Every mutation plans and diffs without writes until `--apply` |
  | 2 | Expected values and stale target rejection | Selection/state/gate expectations and implicit/explicit hashes fail closed |
  | 3 | Selection and lifecycle transition graph | Local-child selection, exact forward/reopen graph, prerequisites, suspend, and resume |
  | 4 | Typed gate evidence mutation | Record/reopen behavior plus existing evidence eligibility and derived counts |
  | 5 | Candidate validation and atomic Markdown publication | Full in-memory audit, byte preservation, Windows-safe replacement, and failure cleanup |

  Each record cites exact tests, commands, reviewed revision, and any platform not directly exercised. Stage all five records before linking them.

- [ ] **Step 5: Dogfood gate recording and commit evidence atomically by intent**

  For each ordinal 1 through 5, run `record-gate T1.5 <ordinal> --expect-open --evidence <gate-path>` first without `--apply`, capture its original SHA-256, and rerun with `--target-sha256 <captured-digest> --apply`. After all five, confirm the row is `5/5`, every link is eligible from the Git index, and unrelated Markdown bytes remain unchanged. Run audit against the staged candidate, then commit all gate files and corresponding backlog changes together.

- [ ] **Step 6: Verify from HEAD, close selection, and update handoff**

  With completion, review, and all five gates committed in `HEAD`, dry-run and apply `transition T1.5 verified --expect reviewed`, then dry-run and apply `select none --expect-current T1.5`. Update the current-repository CLI assertion and handoff to exact `T1.6`/`write_plan`.

  State explicitly that T1.5 changes repository governance only; C1.1-C4.4 remain unimplemented, I1.1/I2.1 runtime adoption remains ineligible, A1.9/I1.2 remain unready, and the dependency path still runs through T1.6, T2.1, T2.2/T3.1, and B1.1 before C1.1.

- [ ] **Step 7: Run the final clean-state quality gate and commit closeout**

  ```powershell
  uv run python .codex/skills/backlog-status/scripts/backlog_status.py audit
  uv run python .codex/skills/backlog-status/scripts/backlog_status.py status --json
  uv run python .codex/skills/backlog-status/scripts/backlog_status.py next
  uv run python tools/quality.py check
  uv run mkdocs build --strict
  uv run python .codex/skills/hygiene/scripts/hygiene.py
  git diff --check
  git status --short --branch
  ```

  Expected: no findings; T1.5 verified at 5/5 and unselected; recommendation `write_plan` for T1.6; all `unittest` and quality/hygiene gates pass; 0.1.0 remains unreleased; no push, tag, publication, release, or external-repository change.

  Commit the final state and handoff. Then use `superpowers:verification-before-completion` and `superpowers:finishing-a-development-branch`; local integration, merged-result verification, worktree removal, and temporary-branch deletion occur only after the user chooses the finishing action.

## Self-Review

- **Spec coverage:** Task 2 covers dry-run planning and selection; Task 3 covers expected state, closed transitions, suspension/resume, and prerequisite enforcement; Task 4 covers typed gate recording/reopening; Task 5 covers explicit apply, stale hashes, repeatable evidence input, complete planning-time and immediately pre-publication candidate validation, permission-preserving atomic publication, cleanup, and Markdown preservation; Task 6 supplies coherent bootstrap states, independent review, and all five committed acceptance records.
- **Scope:** Only repository governance tooling, its tests, T1.5 governance state, and the handoff change. T1.6 integration, product runtime, external clients, dependencies, release machinery, and remote operations remain excluded.
- **Authority reuse:** Structural, adherence, lifecycle, evidence, release, and next-action rules stay in their existing modules. `edit.py` performs mechanical edits and delegates semantic sufficiency to the candidate audit.
- **Type consistency:** Every planner returns the same frozen `MutationPlan`; `publish_mutation` consumes that exact type and returns `AuditLoad`; CLI `none` is translated before calling `plan_selection`.
- **Portability:** `pathlib`, strict UTF-8, exact line terminators, same-directory `mkstemp`, closed handles before `os.replace`, and deterministic cleanup directly implement the cross-platform filesystem requirements. Windows is the local execution platform; configured Ubuntu CI remains separately observable after push.
- **Placeholder scan:** The plan contains no deferred implementation placeholder or undefined production interface.
