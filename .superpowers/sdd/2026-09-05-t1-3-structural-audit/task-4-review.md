# Task 4 independent spec and quality review

## Spec compliance

**Issues found.** The implementation covers the requested Git evidence, lifecycle,
historical admission, and release-rule APIs, but two failure-handling and managed-form
requirements need correction. Review range: `1e00bdd..676d52e`.

## Strengths

- `backlog/evidence.py:45` observes actual worktree bytes, stage-zero regular
  entries, binary index blobs, and optional regular HEAD content. Literal
  argument-vector Git calls, NUL delimiters, and explicit path containment
  avoid porcelain and text-filter shortcuts.
- `backlog/lifecycle.py:130` separates ordinary plan requirements by effective
  stage; `backlog/lifecycle.py:160` restricts selection to current in-progress
  children. Completed and suspended states retain their respective evidence
  requirements without requiring current selection.
- `backlog/lifecycle.py:92` consumes typed historical pins, verifies exact
  bytes and digest, and requires accepted review, all gates, governing design,
  dependencies, and relevant structural/adherence checks without D1 branching
  or fabricated completion evidence.
- `tests/test_backlog_status_evidence.py:96` exercises all slot/kind/result
  combinations using real indexed evidence. The Git-state tests also exercise
  spaces, Unicode, raw newline changes, conflicts, and nonregular index modes.
- `tests/test_backlog_status_lifecycle.py:166` keeps D1.2 normalization confined
  to an isolated positive-control copy. The reported real historical-admission
  failure is the appropriate outcome until Task 5's reviewed reconciliation.

## Important findings

1. **An oversized Gate ordinal escapes as an exception and aborts findings.**
   `.codex/skills/backlog-status/scripts/backlog/parse.py:480` converts the
   unbounded digit match with `int()` outside error translation. On supported
   Python versions, an otherwise valid committed evidence record containing a
   4,301-digit positive Gate raises `ValueError: Exceeds the limit (4300 digits)
   for integer string conversion`. `evidence_findings` catches only
   `MarkdownParseError` around this call, so the failure escapes instead of
   producing `evidence.gate-mismatch` with the referring child/gate context;
   lifecycle aggregation cannot retain independent findings. Translate the
   conversion failure into the domain parse error, or reject an appropriately
   defined ordinal range before conversion. Add a regression that confirms
   both the stable finding and continued reporting of an independent error.

2. **Release-form discovery precedes whitespace folding, rejecting valid forms
   and missing folded duplicates.**
   `.codex/skills/backlog-status/scripts/backlog/rules.py:402` consumes the
   prefix-filtered source collection, whose extractor at
   `.codex/skills/backlog-status/scripts/backlog/parse_sources.py:182` checks the
   raw first line against the entire literal prefix. The approved supplement
   recognizes these forms after joining continuations and folding whitespace.
   A sole prohibition with two spaces after `Release,`, or a line break between
   `package` and `publication:`, incorrectly yields `release.authorization`.
   More seriously, a canonical prohibition followed by a second copy with two
   spaces after `Release,` yields no authorization finding: the duplicate is
   never counted. Collect complete candidate list statements and normalize
   before prefix recognition, then enforce exact count and normalized value.
   Preserve the original source line and section boundary. Test both valid
   whitespace variants and their duplicate combinations.

## Critical and Minor findings

None within Task 4's reviewed scope.

## Checks and limits

- Read the supplied diff once in sequential bounded chunks. Checked the task
  brief, global constraints, implementer report, and approved policy supplement.
- Named outside-diff risk: malformed evidence may escape shared parser error
  handling. Inspected the unchanged `_read` / `_relative_path` helpers and
  reproduced the oversized ordinal in an isolated committed Git fixture on
  Python 3.13. Result: uncaught `ValueError`.
- Named outside-diff risk: release candidate extraction may discard equivalent
  whitespace forms before the new rule sees them. Inspected the unchanged
  `_prefixed_statements` / `_task_statements` helpers and ran isolated direct-rule
  probes. Results: both valid whitespace variants failed; a folded duplicate
  passed. BACKLOG parsing remained valid. These deliberately minimal fixtures
  lack the policy document; the independent release rule does not consume that
  policy-loading result.
- No suite reruns, checkout/index/HEAD changes, or subagents. Only the review
  report was written in the project; reproductions used temporary repositories.
- Cannot verify from this diff: CLI aggregation and malformed-release controls
  through `audit` / `status --json`; Task 5 explicitly owns that integration.
- Recorded evidence reports 20 focused tests, the full Python 3.12 quality gate
  with 354 tests and 94% configured coverage, and 354 passing Python 3.13 tests.
  Hidden-tooling coverage is not represented by that runtime coverage figure.
  Python 3.14's two independently reproduced baseline reader failures are
  separately routed by the controller, outside this review. Linux/macOS runs
  are unobserved. The report also records the existing nonblocking MkDocs
  Material advisory; this is not pristine documentation output.

## Assessment

**Task quality: Needs fixes.** The module boundaries and most contract controls
are sound. Correct the uncaught ordinal conversion and normalization-before-
recognition defect before accepting this task; retain the reported D1.2 and
cross-task integration limits.
