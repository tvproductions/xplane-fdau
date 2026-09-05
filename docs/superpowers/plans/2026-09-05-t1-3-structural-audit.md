# T1.3 Structural Audit and Spec/Plan Adherence Implementation Plan

- **Governance:** active
- **Status:** in_progress
- **Date:** 2026-09-05
- **Roadmap child:** `T1.3`
- **Source specification:** `docs/superpowers/specs/2026-09-05-t1-3-audit-policy-supplement-design.md`
- **Approval:** 2026-09-05 — Jeff / tvproductions
- **Completion evidence:** —

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make repository-local backlog audit reject unsupported structural,
governance, lifecycle, and evidence claims with deterministic contextual findings.

**Architecture:** Extend the existing typed parser with audit-only source facts,
then separate structural rules, artifact adherence, and Git evidence checks.
The thin CLI composes these into the existing schema-version-1 report; parsing
failure in one authority suppresses only rules that depend on that authority.

**Tech Stack:** Python 3.12-compatible standard library, frozen dataclasses,
`pathlib`, `subprocess`, `unittest`, uv, Ruff, ty, Git, and MkDocs.

**Spec:** `docs/superpowers/specs/2026-08-09-xplane-fdau-backlog-status-skill-design.md`.

**Approved supplement:**
`docs/superpowers/specs/2026-09-05-t1-3-audit-policy-supplement-design.md`.
The supplement resolves the four draft-review findings. Jeff approved this
revised plan and supplement on 2026-09-05; the parent specification is unchanged.

## Global constraints

- `ROADMAP.md` is the node-identity, kind, order, and dependency authority.
- `BACKLOG.md` is the only mutable delivery-state authority.
- Use Python's standard-library test framework, `unittest`, exclusively.
- Keep implementation under `.codex/skills/backlog-status/scripts`; runtime
  package, distribution dependencies, canonical contracts, and external clients
  are outside this child.
- Keep Python 3.12 compatibility and verify the repository's supported targets
  without changing runtime metadata or refreshing dependencies in this slice.
- Preserve the exact version-1 JSON keys, ordering, nulls, UTF-8, indentation,
  final LF, and absence of timestamps. Audit-only fields are not serialized.
- Findings have severity `error` or `warning`; every error blocks success.
- Do not infer success from file presence, task checkmarks, or recent commits.
- Production audit performs only filesystem and Git reads; no Git writes,
  network operations, state transitions, recommendation, or automatic repairs.
- T1.4 owns `next`; T1.5 owns mutation and transition requests; T1.6 owns skill,
  session-entry, hygiene, and artifact integration. Do not deliver them here.
- Preserve approved and historical semantic documents. Report any real
  inconsistency before proposing a correction; never suppress it to pass audit.
- Release, tags, and publication remain separately prohibited. An ordinary push
  requires a separate explicit Git-sync request.

## Entry state and execution approval

On 2026-09-05, primary `main` was clean at
`eac980afe5cec66a3ac55cb3774f49bafa4c3466`, with no linked worktree.
`T1.2` and D1.1-D1.3 are verified; T1.3 is selected, specified, and 0/4.
An ignored worktree now exists at `.worktrees/t1-3-structural-audit` on
`t1-3-structural-audit`. Worktree creation required sandbox escalation and
succeeded. This describes the entry state before execution approval.

Jeff approved the policy supplement and this revised plan on 2026-09-05.
Approval is recorded in both artifacts, and this plan's Source specification
and T1.3's Spec link now point to the approved supplement, which incorporates
the parent T1 design. Commit `e082ebd` recorded the approval and planned state
before implementing policy consumers; T1.3 is now in progress.
Use the repository's Superpowers review checkpoints, and use subagents for
independent tasks where their input contracts are already established.

## File responsibilities

All implementation paths in the table are relative to
`.codex/skills/backlog-status/scripts/`.

| File | Responsibility |
| --- | --- |
| `backlog/model.py` | Frozen audit input and evidence types, preserving report types |
| `backlog/parse.py` | Public strict document/evidence parsers and source facts |
| `backlog/parse_sources.py` (new) | Source-fact extraction composed through public APIs |
| `backlog/rules.py` (new) | Identity, inventory, dependency, and release checks |
| `backlog/lifecycle.py` (new) | Lifecycle sufficiency and frozen historical-plan admission |
| `backlog/adherence.py` (new) | Design/plan coverage, metadata, and gate-text agreement |
| `backlog/evidence.py` (new) | Contained regular-file and index/HEAD evidence eligibility |
| `backlog/audit.py` (new) | Independent loading, rule composition, finding sort |
| `backlog/policy.py` (new) | Approved policy loading, historical admission data, evidence slot matrix |
| `backlog/findings.py` (new) | Single shared deterministic finding-order key |
| `backlog/report.py` | Findings and validity in existing human/JSON report |
| `backlog_status.py` | `audit` command and audited status exit behavior |

The parser currently discards backlog outcome text, release-dashboard titles
and prerequisites, and design acceptance text. Retain those as audit input;
do not reconstruct discarded values from rendered reports. Expose public
parsing helpers so new modules never call another module's private functions.

## Task 1: Lossless audit input and isolated parse failures

**Files:** Modify `backlog/model.py`, `backlog/parse.py` under the scripts root;
create `backlog/audit.py` and `backlog/policy.py`; modify `tests/test_backlog_status_model.py` and
`tests/test_backlog_status_parse.py`; create `tests/test_backlog_status_audit.py`.
Create `tests/test_backlog_status_policy.py` for the supplement's loading rules.
Create `backlog/parse_sources.py` for newly added source extraction. This
execution refinement separates about 230 new lines from the existing strict
parser; audit.py consumes its public `parse_roadmap_sources`,
`parse_backlog_sources`, and `parse_artifact_sources` APIs.

**Interfaces:** Retain `parse_repository(root: Path) -> RepositorySnapshot`
and its strict exception behavior for existing callers. Add frozen
`AuditLoad` with `snapshot: RepositorySnapshot`, `findings: tuple[Finding, ...]`,
`invalid_paths: frozenset[str]`, and audit-only source facts. Add
`load_audit(root: Path) -> AuditLoad` and
`parse_artifact(root: Path, path: Path, family: Literal["specification", "plan"])`
returning the existing three artifact types. Add `code`, optional `node`, and
optional `gate` to `MarkdownParseError` without changing its existing text.

Add `HistoricalAdmission(child: str, plan: str, sha256: str)` and
`AuditPolicy(historical: tuple[HistoricalAdmission, ...])` as frozen dataclasses.
`load_policy(root: Path) -> AuditPolicy` reads the exact supplement path,
requires approved/implemented metadata, valid approval, and index/HEAD byte
identity, and parses the historical admission table. A typed
`PolicyError(code: str, path: str, line: int | None, message: str)` carries
`policy.unapproved`, `policy.unavailable`, or `policy.invalid` findings.
`AuditLoad.policy: AuditPolicy | None` preserves failure explicitly; dependent
rules stop when it is absent, while structural parsing/reporting continues.

The policy module defines `EvidenceSlot` as a Literal of `gate`, `review`,
`completion`, and `release`, and exposes
`allowed_kinds(slot: EvidenceSlot) -> frozenset[str]` using the supplement's
fixed slot matrix. It does not inspect gate prose or provide per-child overrides.

- [x] Write failing `unittest` cases for preserved inventory outcome, selected
  line, release-dashboard title/dependencies, approval/date locations, all gate
  headings (including unknown/orphan headings), and each design acceptance
  subsection's child, title, statements, and lines. Use wrapped statements and
  CRLF/LF fixtures; compare whitespace-folded strings, preserving punctuation.

  Add a fixture-copy test with malformed ROADMAP and an independently malformed
  plan. Assert both findings survive, have repository-relative paths and exact
  lines, and no invented missing-child findings come from the failed roadmap.
  Use `TemporaryDirectory` and explicit UTF-8 for every fixture write.
  Add independent policy-loading tests for draft/unapproved policy, missing
  file, uncommitted or edited policy, duplicate admission rows, invalid digest,
  malformed paths, and the approved committed positive control. Compare the
  three real historical plan bytes against the proposed pins before approval;
  do not replace a mismatching pin without review.

  Representative assertions inside the fixture-copy test:

  ```python
  result = load_audit(root)
  paths = {finding.path for finding in result.findings}
  self.assertIn("ROADMAP.md", paths)
  self.assertIn("docs/superpowers/plans/t1-1.md", paths)
  self.assertIn("ROADMAP.md", result.invalid_paths)
  self.assertTrue(all(finding.line is not None for finding in result.findings))
  ```

- [x] Run RED:

  ```powershell
  uv run python -m unittest tests.test_backlog_status_model tests.test_backlog_status_parse tests.test_backlog_status_audit -v
  uv run python -m unittest tests.test_backlog_status_policy -v
  ```

- [x] Implement public parsers that retain the facts above. Load ROADMAP,
  BACKLOG, and each sorted governance artifact independently. Represent an
  unreadable authority with an empty typed value only for report shape and
  mark its path invalid; never treat that value as valid rule input. Convert
  each parse exception to a stable code assigned at its failure site, not by
  matching English exception text. Convert read failures to `input.unreadable`.
  Preserve duplicate rows for later diagnosis instead of overwriting by ID.

  Implement the shared deterministic ordering:

  ```python
  def finding_key(finding: Finding) -> tuple[int, str, int, str, str, int]:
      return (
          0 if finding.severity == "error" else 1,
          finding.path,
          finding.line if finding.line is not None else sys.maxsize,
          finding.code,
          finding.node or "",
          finding.gate if finding.gate is not None else sys.maxsize,
      )
  ```

- [x] Run the same command GREEN and existing report tests to prove source-only
  additions leave JSON shape unchanged. Run the complete pre-commit quality
  commands in Task 5 before committing these explicit files with
  `feat: retain source facts for backlog auditing`.

## Task 2: Structural consistency and dependency rules

**Files:** Create `backlog/rules.py`; create
`tests/test_backlog_status_rules.py` and `tests/backlog_audit_support.py`.

Task 2 supplies the standalone structural rule API. Task 5 composes it in
`backlog/audit.py`; no audit-layer change is required before that integration.

**Interfaces:** Add `structural_findings(loaded: AuditLoad) -> tuple[Finding, ...]`.
Test support exposes `copy_fixture(root: Path) -> None`, which copies the
existing syntax fixture, and `replace_text(root: Path, path: str, old: str,
new: str) -> None`, which requires one exact occurrence and writes UTF-8.
Each test owns its temporary directory and mutations.

- [x] Write parameterized `subTest` cases for this complete rule matrix, with
  valid controls and assertions on code, path, line, node, and gate context:

  | Trigger | Stable code |
  | --- | --- |
  | Repeated same-kind ID / reused cross-kind ID | `roadmap.duplicate-id` / `roadmap.kind-conflict` |
  | Child inconsistent with owning epic | `roadmap.epic-mismatch` |
  | Unknown, duplicate, or nonlocal dependency | `roadmap.unknown-dependency` / `roadmap.duplicate-dependency` / `roadmap.dependency-kind` |
  | Self-cycle / multi-child cycle | `roadmap.dependency-cycle` |
  | Missing / duplicate / nonlocal / unknown backlog child | `backlog.missing-child` / `backlog.duplicate-child` / `backlog.child-kind` / `backlog.unknown-child` |
  | Wrong inventory order | `backlog.child-order` |
  | Outcome / ordered dependency drift | `backlog.outcome-drift` / `backlog.dependency-drift` |
  | Unknown or nonlocal selection | `backlog.invalid-selection` |
  | Count differs from actual task list | `backlog.gate-count` |
  | Unknown gate heading / title disagreement | `backlog.orphan-gates` / `backlog.gate-title` |
  | Missing/duplicate/unknown release dashboard row | `release.inventory` |
  | Dashboard title/prerequisite disagreement | `release.definition-drift` |

  Example using the support functions and current two-child fixture:

  ```python
  replace_text(root, "BACKLOG.md", "1/1", "0/1")
  findings = structural_findings(load_audit(root))
  mismatch = next(item for item in findings if item.code == "backlog.gate-count")
  self.assertEqual("T1.1", mismatch.node)
  self.assertEqual("BACKLOG.md", mismatch.path)
  self.assertIsNotNone(mismatch.line)
  ```

- [x] Run RED: `uv run python -m unittest tests.test_backlog_status_rules -v`.
- [x] Implement rules using multimaps for identity collisions. Traverse only
  validated local edges with a color/stack graph walk; report each cycle
  deterministically without infinite recursion or duplicate cascades. Treat M0
  as a prerequisite only when the milestone exists in valid roadmap input.
  Use roadmap order for inventory checks; compare whitespace-folded titles
  and exact ordered dependency tuples. Skip only cross-file rules whose input
  is invalid or ambiguous, retaining all independent same-file findings.
- [x] Run GREEN plus Task 1 tests, then the Task 5 pre-commit checks. Commit
  explicit files with `feat: audit backlog structure and dependencies`.

## Task 3: Governing artifact and acceptance adherence

**Files:** Create `backlog/adherence.py`; modify `backlog/audit.py` and
`backlog/parse.py`, `backlog/model.py`, and `backlog/parse_sources.py`; create
`tests/test_backlog_status_adherence.py`; extend
`tests/backlog_audit_support.py` with audit-valid design acceptance text.

The model and source-extraction changes retain typed cross-epic declarations
and their source locations, using the source-fact separation introduced in Task 1.
Create `backlog/findings.py` for the shared `finding_key` contract; use it in
audit, adherence, and structural rules while preserving the public audit import.
This review correction avoids duplicated ordering and later composition cycles.

**Interfaces:** Add `adherence_findings(loaded: AuditLoad) -> tuple[Finding, ...]`.
Audit source facts include recognized roadmap cross-epic declarations, tied
to their source lines. Use the current explicit C1-C4 and T2/T3 declarations
as positive fixtures; arbitrary cross-epic lists remain invalid.

When an acceptance subsection contains the exact managed reference
`` `<child>` is complete only when its four earlier acceptance gates pass. ``,
resolve the unique earlier same-child level-two section's explicit
`Its acceptance gates are:` numbered list. Retain the actual statement lines,
require exactly four items, and fail closed on missing or ambiguous targets.
This reads existing declared criteria without treating the reference sentence
as a new gate or introducing child-specific exceptions.

Use the supplement's lifecycle link table before deciding whether Spec is a
contextual reference or a governing design. Blocked/deferred uses Resume for
this determination. An existing regular Markdown context link is valid for
queued work, including the current F1.1-F1.6 references; it cannot justify a
later lifecycle or checked gate. Run gate-text agreement only when the link is
a governing design. Discovered active designs still receive metadata checks.

- [x] Write RED cases for unknown/duplicate/unordered design children, an
  unknown epic, undeclared cross-epic coverage, zero/multiple plan children,
  wrong source family, absent/unapproved/superseded governing design, wrong
  plan child, and a linked design that does not cover the backlog child.
  Validate calendar dates with `date.fromisoformat` after checking the exact
  `YYYY-MM-DD` lexical form. Approval must contain date, em dash, and a nonempty
  owner. Historical dispositions must name a known milestone/child or an
  existing replacement artifact, without becoming active work.

  Add exact gate-text, order, count, and subsection-title comparisons for each
  linked child; wrapped whitespace is accepted, changed punctuation is rejected.
  Add a test proving unlinked approved designs can coexist for the same child:
  D1's contract coverage does not replace the child's explicitly linked design.
  Add positive controls for all six queued F1 architecture links and a suspended
  queued child; reject missing/escaping links, checked gates with context-only
  references, and the same architectural link used at designing or specified.

  ```python
  replace_text(root, "docs/superpowers/specs/t1-design.md",
               "Frozen parser remains open.", "Changed parser condition.")
  findings = adherence_findings(load_audit(root))
  mismatch = next(item for item in findings if item.code == "artifact.gate-drift")
  self.assertEqual("T1.2", mismatch.node)
  self.assertEqual(1, mismatch.gate)
  ```

- [x] Run `uv run python -m unittest tests.test_backlog_status_adherence -v`.
- [x] Implement artifact checks with `artifact.spec.*`, `artifact.plan.*`,
  `artifact.historical.disposition`, `artifact.approval`, and
  `artifact.gate-drift` codes. Preserve the design's example
  `artifact.plan.multiple-children` for that exact error. Validate metadata
  status requirements for every active artifact, but compare backlog gate
  statements against its linked design only. Allow the approved B1 draft-plan
  link while its child remains specified; a draft never proves planned state.
  Do not require a governing approved design for queued children with no link
  or with a valid contextual reference, as specified by the supplement.
- [x] Run GREEN, the earlier audit tests, and Task 5 pre-commit checks. Commit
  explicit files with `feat: audit governing artifacts and acceptance criteria`.

## Task 4: Git-backed evidence and lifecycle sufficiency

**Files:** Create `backlog/evidence.py` and `backlog/lifecycle.py`; modify
`backlog/model.py`, `backlog/parse.py`, `backlog/parse_sources.py`,
`backlog/rules.py`, and `backlog/audit.py`; create
`tests/test_backlog_status_evidence.py` and
`tests/test_backlog_status_lifecycle.py`; extend test support with
`initialize_git(root: Path) -> None` and complete evidence fixture contents.

Keep lifecycle and historical-plan functions in `backlog/lifecycle.py`;
Task 5 imports that module directly, while release rules remain in rules.py.
Retain managed release-section locations in audit source facts and report
missing required sections as parse errors. This does not change the legacy
strict repository parser's syntax-only API.

**Interfaces:** Add frozen `EvidenceArtifact(path, child, gate, kind, result,
date, subject, source)` with `gate: int | None` and other existing lexical
field types. Add `parse_evidence(root: Path, path: Path) -> EvidenceArtifact`.
Add `evidence_findings(root: Path, path: str, child: str, gate: int | None,
*, kinds: frozenset[str], require_head: bool) -> tuple[Finding, ...]` and
`lifecycle_findings(loaded: AuditLoad) -> tuple[Finding, ...]`.
Add `historical_plan_findings(loaded: AuditLoad, child: BacklogChild) ->
tuple[Finding, ...]`, called only for a linked historical plan. It consumes
typed admission data; it contains no D1-specific branching.

- [x] Write failing tests in isolated Git repositories for absent/untracked,
  ignored-untracked, staged-new, committed, unstaged-modified, staged-modified,
  deleted, conflicted, and nonregular evidence. Include spaces and Unicode in
  paths, LF/CRLF, a contained path resolving outside the root, and Git failures.
  Test exact metadata order, kind/result pair, valid date, nonempty subject,
  wrong child, zero/negative/wrong gate, and gate-versus-child-level evidence.

  Establish index/HEAD distinction with real Git fixture commands:

  ```python
  subprocess.run(["git", "-C", str(root), "add", "--", evidence_path], check=True)
  self.assertEqual((), evidence_findings(
      root, evidence_path, "T1.1", 1,
      kinds=frozenset({"verification"}), require_head=False))
  self.assertTrue(evidence_findings(
      root, evidence_path, "T1.1", 1,
      kinds=frozenset({"verification"}), require_head=True))
  ```

  Fixture Git identity uses local `git -c user.name=Fixture -c
  user.email=fixture@example.invalid commit`; never alter global Git config.
  Disable fixture signing/hooks via per-command settings so tests need no
  interactive credentials and cannot execute unrelated user hooks.

- [x] Write lifecycle tests for every status and blocked/deferred resume
  state. For ordinary active plans, apply these stage-specific requirements:
  designing requires a covering draft design; specified requires an approved
  covering design; planned additionally requires an approved plan; in_progress
  requires an in-progress plan and current selection. Implemented requires a
  completed plan with eligible child-level completion evidence, reviewed adds
  accepted child-level review, and verified adds all gates with HEAD-backed
  evidence. The covering design and plan approval remain required in later
  stages, but selection and in-progress plan status do not. Only a currently
  in_progress child must be selected; a suspended child with Resume in_progress
  retains the in-progress plan requirement without requiring current selection.
  Reject released while prohibited, missing
  or extra Resume/Reason, recursive suspended resume states, unsupported
  lifecycle claims, and execution claims before prerequisites are verified.
  Positive controls include specified children whose implementation dependency
  is pending and the four blocked standards children with queued resume state.
  Validate current state only: detecting a historical skipped transition is
  T1.5's expected-state mutation responsibility, not a static-audit inference.

  Add the supplement's historical admission branch: only an effectively verified
  child with the exact pinned historical plan, completed metadata, named
  disposition, approved governing design, verified dependencies, and eligible
  HEAD-backed review/all-gate evidence passes. It replaces only active-plan
  approval/completion-field requirements. No synthetic completion evidence is
  created. Include D1.1-D1.3 positive controls and mutations for wrong child,
  hash, plan path, state, missing evidence, edited evidence, unlisted plan, and
  a new plan relabeled historical. All failures emit `lifecycle.historical-plan`.
  Include blocked/deferred historical children with Resume verified as positive
  controls while still enforcing suspension metadata and preserving suspension.
  Include unselected implemented/reviewed/verified ordinary children, multiple
  simultaneously verified children, and an unselected suspended in-progress
  child to prove stage-specific selection rules.

- [x] Run RED:

  ```powershell
  uv run python -m unittest tests.test_backlog_status_evidence tests.test_backlog_status_lifecycle -v
  ```

- [x] Implement read-only evidence observation using argument-vector Git
  subprocesses (`shell=False`), NUL-delimited index listing, and binary blob
  reads. Require a contained regular Markdown file and normal stage-zero Git
  entry. Compare the file's actual bytes to indexed bytes, and for verified
  claims additionally compare index to HEAD. Do not rely solely on porcelain
  cleanliness or filtered text diffs. Fail closed on unavailable Git evidence.
  Use `evidence.untracked`, `evidence.dirty`, `evidence.not-in-head`,
  `evidence.child-mismatch`, `evidence.gate-mismatch`, `evidence.kind`,
  `evidence.path`, and `evidence.git` codes, with the referring gate context.

  Use `allowed_kinds(slot)` from the fixed supplement matrix: local gates,
  completion, and release slots allow verification/artifact with passed result;
  review allows review with accepted result. Direct approval/review cannot
  substitute for gate verification. Release evidence uses Child equal to the
  release ID and Gate absent; it never creates a local child. Exhaustively test
  all four slots against all four kinds and both results, plus wrong IDs and
  gate ordinals. Emit `evidence.kind` and `evidence.result` distinctly. Check
  lexical evidence ordering and duplicates separately from file eligibility.

  Validate dashboard waiting/ready against roadmap prerequisite states;
  satisfied additionally needs eligible evidence and never grants publication.
  Implement `release_authorization_findings(loaded: AuditLoad) ->
  tuple[Finding, ...]` in rules.py using the supplement's two exact managed
  forms and section boundaries. Missing, duplicated, modified, or checked forms
  produce `release.authorization`; released child state produces
  `release.prohibited-state`. Test every variation through the rule and CLI,
  including a satisfied G1 and verified dependencies. A separately authorized
  ordinary Git-sync statement remains a positive control. Do not interpret
  arbitrary surrounding prose as a grant of release authority.

- [x] Run GREEN and all previous audit tests, then Task 5 pre-commit checks.
  Commit explicit files with `feat: validate lifecycle and committed evidence`.

## Task 5: CLI integration, review, and four-gate closure

**Files:** Modify `backlog_status.py`, `backlog/audit.py`, `backlog/report.py`,
`backlog/parse.py`,
`tests/test_backlog_status_cli.py`, `tests/test_backlog_status_report.py`,
`tests/test_backlog_governance.py`, `tests/backlog_audit_support.py`,
`BACKLOG.md`, `CHANGELOG.md`, and this plan. Create completion/review/gate
records under `.superpowers/sdd/2026-09-05-t1-3-structural-audit/`.

The independently accepted reconciliation in that directory's
`reconciliation-review.md` also authorizes these exact document corrections:

- Align BACKLOG C2.4, C3.3, T2.2, T3.1, and D1.2 statements with their linked
  approved designs. C2.4 becomes 0/5; all previously open gates remain open.
  D1.2 remains verified at 4/4 with unchanged evidence links: independent
  review verified every expanded clause against committed evidence.
- In `docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md`,
  change only the C4.4 acceptance sentence from
  "Version `0.1.0` remains unreleased and no push/tag/publication occurs."
  to "Version `0.1.0` remains unreleased and no release tag or package publication
  occurs; separately authorized routine Git sync does not satisfy or violate
  this release gate." This 2026-09-05 correction implements the existing
  AGENTS/HANDOFF Git-sync policy amendment and approved gz-skills adoption
  authority. Preserve original approval metadata and every other contract
  statement; it does not relabel the historical D1.1 review.
- Append existing authority paths only to the dispositions of
  `docs/superpowers/plans/2026-08-16-xplane-fdau-architecture-propagation.md`,
  `docs/superpowers/plans/2026-08-22-q4xpcc-contract-handoff-readiness-authority.md`,
  `docs/superpowers/plans/2026-09-05-gz-skills-adoption.md`, and
  `docs/superpowers/specs/2026-09-05-gz-skills-adoption-design.md`, using the
  exact mapping in the reconciliation review. Preserve execution bodies and
  all frozen D1 plans/evidence. Update affected governance assertions.

These are corrections to existing intent, not new design approvals or
delivery evidence. Preserve the approved T1.3 policy supplement bytes.

The controller supplies task and whole-branch independent review after the
implementation candidate. Record accepted review and completion evidence only
after those reviews and actual final checks; resume the Task 5 implementer for
that closeout. Do not mark T1.3 verified at the initial code-review checkpoint.

Two confirmed CLI integration regressions also belong here: disable Git's
optional index refresh during observation, and translate oversized BACKLOG
gate-count integer conversion failures into contextual domain findings.
Regression details and exact observations are in `integration-notes.md` beside
the task reports. Preserve Python's integer limits and the accepted count
syntax; malformed input must not abort independent reporting.

**Interfaces:** Add `audit_repository(root: Path) -> AuditLoad`, which loads
and combines all applicable rule families. Extend
`build_report(snapshot: RepositorySnapshot, git: GitState,
findings: tuple[Finding, ...] = ()) -> StatusReport`. Both `status` and `audit`
use that same audited report; `status --json` retains version 1. `audit` is
human output only in this child, matching the specified command surface.

- [x] Write failing CLI tests for valid audit, semantic errors, independently
  malformed inputs, unavailable Git, warnings-only success, invalid arguments,
  and unchanged source/index/HEAD before and after commands. Upgrade CLI
  fixtures to complete audit-valid temporary repositories; keep pure syntax
  fixtures useful without pretending their absent evidence is eligible.
  `status --json` must return valid JSON with `valid: false` and findings even
  on parse failures, using empty typed collections only for invalid authorities.

  ```python
  result = self.run_cli(["status", "--json"], root=root, mock_git=False)
  payload = json.loads(result.stdout)
  self.assertEqual(1, result.code)
  self.assertFalse(payload["valid"])
  self.assertIsNone(payload["recommendation"])
  self.assertIn("backlog.gate-count", [item["code"] for item in payload["findings"]])
  ```

- [x] Run RED with `uv run python -m unittest tests.test_backlog_status_cli
  tests.test_backlog_status_report -v` as one command line.
- [x] Wire the audit into both commands; keep findings on stdout in the report,
  usage diagnostics on stderr, and exit 0/1/2 semantics. On Git observation
  failure add a blocking finding and retain schema shape with an empty Git
  observation; do not report a successful clean observation. Use:

  ```python
  valid = not any(finding.severity == "error" for finding in findings)
  exit_code = 0 if report.valid else 1
  ```

- [x] Run all focused tests GREEN. Run the current repository audit and resolve
  genuine findings through explicit reviewed corrections without rewriting
  completed specs, fabricating approval, or silently widening this child.
  Prove all existing D1 verification and F1 queued references pass through the
  approved supplement's explicit rules. Do not turn a failure into a generic
  exemption or alter their preserved plans/evidence.

- [ ] Use these full pre-commit and final verification commands (each exits 0):

  ```powershell
  uv run python -m unittest discover -v
  uv run ruff check --no-force-exclude .codex/skills/backlog-status/scripts
  uv run ruff format --check --no-force-exclude .codex/skills/backlog-status/scripts
  uv run ty check .codex/skills/backlog-status/scripts
  uv run python tools/quality.py check
  uv run python -m unittest tests.test_public_api tests.test_documentation -v
  uv run mkdocs build --strict
  uv run python tools/quality.py docs
  uv run python .codex/skills/backlog-status/scripts/backlog_status.py audit
  uv run python .codex/skills/backlog-status/scripts/backlog_status.py status --json
  git diff --check
  ```

  Inspect every command's exit status. Before CLI wiring, run available status
  instead of the not-yet-delivered audit; never record that as T1.3 completion.
  Repeat supported-source unittest checks with `uv run --python 3.12`, `3.13`,
  and `3.14` before final closure. Use gzs-cross-platform-python for the
  filesystem/subprocess review and gzs-quality-gate for final verification.

- [ ] Request independent review of the entire branch against the approved
  design and all four T1.3 acceptance criteria. Resolve findings test-first,
  rerun affected and final checks, and commit explicit implementation files
  with `feat: expose strict backlog audit`.
- [ ] Record four evidence files whose subjects match the four existing T1.3
  gates exactly: structural failures; artifact metadata/adherence; lifecycle
  and Git evidence; complete contextual reporting and blocking exit behavior.
  Record commands, test names/counts, reviewed commit, and actual outcomes.
  Record accepted independent review and a child-level completion record.
  The metadata format is the approved six-field evidence contract; no
  checkmark or this plan's test expectations substitute for executed evidence.
- [ ] Stage eligible records with the completed plan and backlog changes, then
  advance implemented/reviewed only when their prerequisites hold. For verified,
  first commit the eligible evidence, then set the four evidence links and
  verified state, commit, and run a fresh clean post-commit audit proving the
  linked evidence bytes are in HEAD. Use `docs: verify T1.3 structural audit`.
  If final audit fails, repair and reverify; do not claim completion.
- [ ] Invoke finishing-a-development-branch and present local integration for
  user selection. After local integration is authorized, merge to main, verify
  the merged result, and remove the clean worktree and temporary branch through
  Git-aware operations. No push or release follows implicitly.

### Task 5 implementation checkpoint — 2026-09-05

The CLI now combines all rule families into one audited report, preserving
version-1 JSON, stdout findings, usage stderr, and blocking exits. Regressions
proved and corrected Git optional index refresh, oversized BACKLOG count
conversion, and Windows executable UTF-8/LF output. The focused CLI, report,
and governance run passed 55 unittest tests. The exact commands and final
candidate verification are recorded in
`.superpowers/sdd/2026-09-05-t1-3-structural-audit/task-5-report.md`.

Applied only the independently accepted `reconciliation-review.md` correction
population: C2.4 is 0/5; C3.3, T2.2, T3.1, and D1.2 now copy their explicitly
linked approved design statements. All previously open gates remain open.
D1.2 retains verified 4/4 and its original evidence links, whose detailed
coverage was independently accepted. Twenty protected files (policy, three
D1 plans, D1.2 detailed design, and fifteen D1 review/gate records) match the
working tree, index, HEAD, and Task 5 base `f92a88f`; all pinned hashes match.

On 2026-09-05, the active canonical design's C4.4 acceptance sentence changed
from "Version `0.1.0` remains unreleased and no push/tag/publication occurs."
to "Version `0.1.0` remains unreleased and no release tag or package publication
occurs; separately authorized routine Git sync does not satisfy or violate
this release gate." Authority is the existing AGENTS.md explicit-only sync
policy, HANDOFF.md's dated amendment, and approved
`docs/superpowers/specs/2026-09-05-gz-skills-adoption-design.md`, as accepted in
`reconciliation-review.md`. Original approval metadata and all other canonical
contract bytes remain unchanged; the historical D1.1 review is not relabeled.
The four accepted historical dispositions append only their exact existing
current-authority paths and preserve their execution bodies.

Task/whole-branch independent review, four-gate evidence, child completion,
HEAD-backed closure, and local integration remain pending. This checkpoint
keeps both plan and T1.3 in_progress with zero T1.3 gates satisfied. It creates
no accepted review or completion record. HANDOFF's current pointer is owned by
the final Task 5 closeout after verified evidence exists.

## Plan audit: intent to scope

| Declared intent | T1.3 scope | Assessment |
| --- | --- | --- |
| Approved T1 design:348 (evidence), :386 (lifecycle), :437 (audit) | BACKLOG.md:427, four T1.3 acceptance gates | Aligned: structural/adherence audit only |
| Approved T1 design:492 (commands), :571 (reporting) | audit plus findings in existing status | Aligned: no next, mutation, or integration hooks |
| Scope amendment and release boundary | Repository-local standard-library tooling | Aligned: no runtime or consumer work |

## Plan audit: scope to execution

| Acceptance requirement | Executable proof | Assessment |
| --- | --- | --- |
| Gate 1: structural and link rules fail closed | Tasks 1, 2, 4; malformed input and graph tests | Aligned |
| Gate 2: designs, plans, historical metadata | Tasks 3-4; lifecycle-specific links and frozen historical admission | Aligned with approved supplement |
| Gate 3: prerequisites and eligible evidence | Tasks 1 and 4; fixed slot matrix, isolated real Git repositories and lifecycle matrix | Aligned with approved supplement |
| Gate 4: all independent contextual findings and blocking result | Tasks 1 and 5; failure isolation, ordering, JSON, exit tests | Aligned |
| Committed evidence and independent review | Task 5 staged/HEAD closure and final review | Aligned |

## Review corrections

| Finding | Concrete correction | Owning section |
| --- | --- | --- |
| Historical D1 plans cannot meet active-plan fields | Frozen identity admission plus HEAD-backed review and all gates; no fabricated metadata | Supplement: Historical plan reconciliation; Tasks 1 and 4 |
| Queued F1 architectural links treated as formal designs | Lifecycle-specific context versus governing link validation | Supplement: Specification links by lifecycle; Task 3 |
| Evidence-kind requirements have no deterministic source | Fixed slot/kind/result/ordinal matrix with exhaustive negative tests | Supplement: Deterministic evidence-kind policy; Tasks 1 and 4 |
| Release prohibition checked only by tests | Production rule on exact managed authorization forms and CLI-negative cases | Supplement: Release prohibition as an audited contract; Tasks 4 and 5 |
| Historical admission rejected allowed suspensions | Apply admission at effective verified while preserving blocked/deferred status | Supplement: Historical plan reconciliation; Task 4 |
| Cumulative rules retained in-progress status and selection after completion | Stage-specific plan status; selection required only for actual in_progress | Task 4 lifecycle matrix and unselected/suspended controls |

The earlier unconditional self-review PASS was withdrawn during draft review.
The revised plan resolves the four original findings and the two independent
lifecycle findings. Independent re-review found no remaining Critical,
Important, or Minor issue. Jeff approved the supplement and revised plan on
2026-09-05; governance approval was recorded in commit e082ebd before execution.
The intent-to-scope and scope-to-plan audit now passes against approved
authority. This approval and plan audit satisfy no T1.3 delivery gate.
