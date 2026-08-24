# D1.2 Acquisition, Recording, Projection, and Pinning Contract Design Implementation Plan

- **Governance:** historical
- **Status:** completed
- **Disposition:** D1.2 acquisition, recording, projection, and pinning contract design completed with accepted independent review and four committed verification gates; preserved as the contract-only execution record without A1/R1/P1 implementation, artifact, adoption, or release activity.

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` to execute this plan task-by-task.
> Use `superpowers:requesting-code-review` for the independent whole-design and
> final branch reviews. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Independently review and verify the approved D1.2 contract-only design as binding future A1/R1/P1 architecture input without implementing or delivering those contracts.

**Architecture:** Treat the approved D1.2 specification as the only new semantic artifact. Review it against the parent architecture, scope amendment, approved canonical contracts, D1 readiness contract, ROADMAP ordering, and all four D1.2 acceptance gates; then atomically record accepted review evidence, four verification gates, the verified backlog transition, and a resumable D1.3 handoff.

**Tech Stack:** Markdown, Python 3.12+ standard library, Python `unittest`, repository governance/status tooling, MkDocs, repository quality tooling, and Git.

**Spec:** `docs/superpowers/specs/2026-08-23-xplane-fdau-acquisition-recording-projection-pinning-contracts-design.md`

## Global Constraints

- Read `HANDOFF.md`, `ROADMAP.md`, `BACKLOG.md`, the complete parent architecture, the repository scope amendment, the completed migration specification and plan, the approved canonical-contract specification, the approved D1 readiness design, and the complete D1.2 design before editing.
- Change only the D1.2 design when resolving an accepted review finding, D1.2/D1.3 governance and handoff Markdown, this plan, D1.2 review/gate evidence, and focused governance/status tests that encode the D1 lifecycle.
- Do not change runtime code, package metadata, schemas, fixtures, conformance resources, generated artifacts, q4xpcc files, or create any A1/R1/P1 implementation plan.
- Use Python's `unittest` framework only. Never add, invoke, or suggest pytest.
- Keep runtime standard-library-only and preserve external ownership of XPPython3/XPLM, `xplane-webapi`, simulator I/O, q4xpcc policy, and q4xpcc operational findings.
- Keep native X-Plane textual FDR v3/v4 a deliberately lossy projection and sink, not the canonical FDAU archive. Do not define native-FDR-to-canonical mapping.
- D1.2 may become `verified` only after accepted independent review and all four gate files are committed. Every A1/R1/P1/S/F1 child retains zero gates and no plan, review, schema, fixture, artifact, implementation, or adoption evidence. A1/R1/P1/S1.1/F1 remain `queued`; the pre-existing S2.1/S2.2/S3.1/S4.1 licensed-source blocks and `queued` resume states remain truthful and unchanged.
- After D1.2 verifies, select only `D1.3`. Keep `I1.0` ineligible until D1.3 verifies; keep `I1.1`, `I1.2`, `G1`, release, push, tag, and publication authorization unchanged.
- Do not emit the D1.3 q4xpcc brief, invent a source revision pin or artifact hash, push, tag, publish, or release.

---

### Task 1: Independently review the complete D1.2 design

**Files:**

- Modify only if required by accepted findings: `docs/superpowers/specs/2026-08-23-xplane-fdau-acquisition-recording-projection-pinning-contracts-design.md`
- Create: `.superpowers/sdd/2026-08-23-d1-2-acquisition-recording-projection-pinning-contracts/review.md`

**Interfaces:**

- Consumes: the approved D1.2 design at the branch's approval commit and the complete authority chain named in Global Constraints.
- Produces: accepted independent review evidence with no unresolved Critical, Important, or otherwise load-bearing ambiguity.

- [x] **Step 1: Run deterministic candidate scans**

  ```powershell
  rg -n -i "TBD|TODO|FIXME|to be decided|implementation-defined|may choose|normally|optional.*when applicable" docs/superpowers/specs/2026-08-23-xplane-fdau-acquisition-recording-projection-pinning-contracts-design.md
  rg -n "pytest|xpwebapi|xplane-webapi|XPPython3|XPLM|q4xpcc|ARINC|FOQA|native FDR|release|push|tag|publish" docs/superpowers/specs/2026-08-23-xplane-fdau-acquisition-recording-projection-pinning-contracts-design.md
  git diff --check
  ```

  Expected: no unresolved placeholder or implementation-choice wording; every provider, consumer, standards, native-format, adoption, and publication mention preserves the approved boundary; whitespace passes. Contextual examples and policy words are acceptable only when their normative choice is already closed.

- [x] **Step 2: Request independent whole-design review**

  Use `superpowers:requesting-code-review` with a clean-context reviewer. Supply the approved design, parent architecture, scope amendment, completed migration specification, approved canonical design, D1 readiness design, ROADMAP A1/R1/P1 ordering, BACKLOG D1.2 gates, and this plan. Require line-specific Critical/Important/Minor findings and `ACCEPTED` or `NOT ACCEPTED`.

  Require explicit audits of:

  - all acquisition-profile, demand, resolution, transform, session, continuity, fan-out, recording, archive, checkpoint, recovery, replay, projection, loss-report, deployment, pinning, and conformance families;
  - identity/version boundaries, exact fields and variants, reference closure, closed codes, validation order, causal precedence, lifecycle state, artifact identity/content identity, and future schema/conformance paths;
  - q4xpcc Slice 2A–2D coverage and complete A1.1–A1.9, R1.1–R1.7, and P1.1–P1.6 ownership mapping;
  - canonical/native-FDR, ARINC, FDM/FOQA, provider/client, q4xpcc policy/finding, adoption, and release boundaries; and
  - reproducible installed-wheel/bundled deployment, exact source and release-artifact pins, delivered-file hashes, conformance, and closed-world no-divergent-subset proof without fabricated current artifacts.

- [x] **Step 3: Resolve every load-bearing finding and obtain re-review**

  Use `superpowers:receiving-code-review` before acting on findings. Fix every Critical and Important/load-bearing finding in the design, run the Step 1 scans, commit a correction wave with an imperative `docs:` subject, and request complete re-review. Continue until the reviewer reports `ACCEPTED`. Do not weaken scope, identity, determinism, evidence, or release boundaries to satisfy a finding.

- [x] **Step 4: Record accepted review evidence**

  Create `review.md` with exactly this metadata family:

  ```markdown
  # D1.2 Acquisition, Recording, Projection, and Pinning Contract Design Review

  - **Child:** `D1.2`
  - **Gate:** —
  - **Kind:** review
  - **Result:** accepted
  - **Date:** 2026-08-23
  - **Subject:** Independent acquisition, recording, projection, and pinning contract design review
  ```

  Record every reviewed revision, finding and resolution, the final assessment, exact scope, and the explicit absence of implementation, schema, fixture, artifact, adoption, release, push, tag, and publication claims.

- [x] **Step 5: Verify and commit Task 1**

  ```powershell
  uv run python -m unittest tests.test_backlog_governance tests.test_documentation -v
  git diff --check
  git add docs/superpowers/specs/2026-08-23-xplane-fdau-acquisition-recording-projection-pinning-contracts-design.md
  git add -f .superpowers/sdd/2026-08-23-d1-2-acquisition-recording-projection-pinning-contracts/review.md
  git diff --cached --check
  git commit -m "docs: record D1.2 contract review"
  ```

### Task 2: Close D1.2 governance test-first and hand off to D1.3

**Files:**

- Modify: `tests/test_backlog_governance.py`
- Modify: `tests/test_backlog_status_cli.py`
- Modify: `BACKLOG.md`
- Modify: `HANDOFF.md`
- Modify: `docs/superpowers/plans/2026-08-23-d1-2-acquisition-recording-projection-pinning-contracts.md`
- Create: `.superpowers/sdd/2026-08-23-d1-2-acquisition-recording-projection-pinning-contracts/gate-1.md`
- Create: `.superpowers/sdd/2026-08-23-d1-2-acquisition-recording-projection-pinning-contracts/gate-2.md`
- Create: `.superpowers/sdd/2026-08-23-d1-2-acquisition-recording-projection-pinning-contracts/gate-3.md`
- Create: `.superpowers/sdd/2026-08-23-d1-2-acquisition-recording-projection-pinning-contracts/gate-4.md`

**Interfaces:**

- Consumes: the accepted Task 1 review and exact four D1.2 acceptance statements.
- Produces: verified D1.2 at `4/4`, selected dependency-ready D1.3 at `0/4`, exact committed evidence, and no downstream delivery claim.

- [x] **Step 0: Resolve capped Task 1 carryover and obtain accepted whole-design review**

  Apply the four load-bearing rulings recorded in the SDD ledger after whole-design re-review 7: map recording-orchestrator-only failure to exact acquisition `internal_failure` propagation; add an exact recording-descriptor `RecordRef` to every projection report; remove every schema-v1 offline-projection operation or promise while retaining in-session deterministic projection; and keep preserved-partial byte-root content sidecars tied to sealed candidate bytes while later sink/final-manifest evidence owns failure, preserved state, and ledger head. Run all Task 1 scans and focused documentation checks, commit only the corrected design, then request another complete independent whole-design review. Do not proceed until that review reports `ACCEPTED` with no unresolved load-bearing finding.

  After acceptance, create `review.md` with the exact metadata and complete revision/finding/resolution history specified by Task 1 Step 4, including every whole-design pass and the final accepted revision. Commit the corrected design and accepted review evidence before writing final-state governance tests.

- [x] **Step 1: Write final-state governance tests first**

  Read `superpowers:test-driven-development` and `writing-good-tests.md`. Update `tests/test_backlog_governance.py` so the sole selection is `D1.3`; `D1.2` has the new design/plan/review links, `verified`, `4/4`, and four evidence files; `D1.3` remains `specified`, `0/4`, and dependency-ready; and A1/R1/P1/S/F1 retain zero gates and no delivery evidence. Preserve the truthful licensed-source blocks and queued resume states for S2.1/S2.2/S3.1/S4.1; every other downstream child remains queued. Add a D1.2 evidence-metadata test with these exact gate subjects:

  ```python
  subjects = (
      "Complete A1/R1/P1 contract and q4xpcc Slice 2 coverage",
      "Exact versioned families, invariants, outcomes, and future resources",
      "Reproducible deployment pinning and no-divergent-subset proof",
      "Accepted review and preserved implementation and release boundaries",
  )
  ```

  Update `tests/test_backlog_status_cli.py` so D1.1 and D1.2 are verified and dependency-ready, D1.3 is specified and dependency-ready, D1.2 exposes its exact design/plan/review/evidence paths, and D1.3 exposes no plan/review/evidence.

- [x] **Step 2: Run the focused tests and verify RED**

  ```powershell
  uv run python -m unittest tests.test_backlog_governance tests.test_backlog_status_cli -v
  ```

  Expected: failures name the still-active `D1.2` selection, its `specified`/`0/4` row, missing D1.2 review/gate evidence, and D1.3 dependency readiness. Fix test errors until failures are solely caused by the not-yet-recorded final governance state.

- [x] **Step 3: Record the four D1.2 gates and backlog transition**

  Create four gate files with `Child: D1.2`, ordinal `Gate`, `Kind: verification`, `Result: passed`, `Date: 2026-08-23`, and the exact subjects from Step 1. Gate 1 maps the design to all four q4xpcc Slice 2 plans and all A1/R1/P1 children. Gate 2 inventories every family and exact identity/version, ownership, invariant, reference, outcome, error, schema, and conformance boundary. Gate 3 records installed-wheel and reproducibly bundled modes, exact source/release-artifact/delivered-file hashes, conformance execution, and closed-world no-divergent-subset proof without claiming a current artifact. Gate 4 cites accepted review and proves every A1/R1/P1/S/F1 child retains zero gates and no delivery evidence, with the pre-existing licensed-source standards blocks unchanged, while all implementation/adoption/release boundaries remain closed.

  In `BACKLOG.md`, set D1.2 to `verified`, link the new approved design, this plan, `4/4`, and `review.md`; check exactly its four acceptance statements with matching gate links. Select `D1.3`. Leave D1.3 `specified` at `0/4` with no plan/review/evidence and do not emit its brief.

- [x] **Step 4: Update the resumable handoff and finalize plan metadata**

  Update `HANDOFF.md` to record D1.2's approved design, accepted review, four gates, and contract-only outcome. State the exact next sequence: execute selected D1.3, then report I1.0 planning reconciliation eligibility only after D1.3 verification. Preserve the separate I1.1/C4.4 and I1.2/A1.9 thresholds and all release prohibitions.

  After all checks in Step 5 exist, replace this plan's active metadata with:

  ```markdown
  - **Governance:** historical
  - **Status:** completed
  - **Disposition:** D1.2 acquisition, recording, projection, and pinning contract design completed with accepted independent review and four committed verification gates; preserved as the contract-only execution record without A1/R1/P1 implementation, artifact, adoption, or release activity.
  ```

  Check only steps whose commands and evidence actually exist.

- [x] **Step 5: Run GREEN and complete verification**

  Use `superpowers:verification-before-completion`, then run:

  ```powershell
  uv run python -m unittest tests.test_backlog_governance tests.test_backlog_status_parse tests.test_backlog_status_report tests.test_backlog_status_cli -v
  uv run python .codex/skills/backlog-status/scripts/backlog_status.py status
  uv run python .codex/skills/backlog-status/scripts/backlog_status.py status --json
  uv run python -m unittest discover -v
  uv run python tools/quality.py check
  uv run python -m unittest tests.test_public_api tests.test_documentation -v
  uv run mkdocs build --strict
  uv run python tools/quality.py docs
  git diff --check
  ```

  Expected: every command exits 0; the suite remains at or above the 278-test baseline; status reports D1.2 verified at `4/4`, D1.3 selected and dependency-ready at `0/4`, and no finding or inferred recommendation; repository quality and strict documentation pass; no runtime, package, schema, fixture, artifact, q4xpcc, A1/R1/P1-plan, release, push, tag, or publication file appears in scope.

  Completion evidence: the test-first focused run established a genuine RED
  with 36 tests, 12 assertion failures, and no errors before governance
  implementation. Final verification passed 72 focused governance/status
  tests, valid human and JSON status with no finding or recommendation, 280
  full `unittest` tests, the complete quality gate at 94% statement coverage,
  15 public-API/documentation tests, strict MkDocs, documentation quality at
  43.6%, and `git diff --check`. Accepted independent review is committed at
  `.superpowers/sdd/2026-08-23-d1-2-acquisition-recording-projection-pinning-contracts/review.md`;
  the four exact completion records are `gate-1.md` through `gate-4.md` in
  that same directory.

- [x] **Step 6: Inspect, commit, and verify the local checkpoint**

  ```powershell
  git diff --name-only 01aa223..HEAD
  git status --short
  git diff --check
  git add BACKLOG.md HANDOFF.md tests/test_backlog_governance.py tests/test_backlog_status_cli.py docs/superpowers/plans/2026-08-23-d1-2-acquisition-recording-projection-pinning-contracts.md
  git add -f .superpowers/sdd/2026-08-23-d1-2-acquisition-recording-projection-pinning-contracts/review.md .superpowers/sdd/2026-08-23-d1-2-acquisition-recording-projection-pinning-contracts/gate-1.md .superpowers/sdd/2026-08-23-d1-2-acquisition-recording-projection-pinning-contracts/gate-2.md .superpowers/sdd/2026-08-23-d1-2-acquisition-recording-projection-pinning-contracts/gate-3.md .superpowers/sdd/2026-08-23-d1-2-acquisition-recording-projection-pinning-contracts/gate-4.md
  git diff --cached --check
  git commit -m "docs: verify D1.2 contract design"
  git status --short --branch
  git log -6 --oneline
  ```

  Expected scope: the approved D1.2 design metadata/corrections, this plan, BACKLOG, HANDOFF, two focused test files, D1.2 review evidence, and four D1.2 gate files. The branch is clean; no push, tag, publication, release, artifact, or q4xpcc brief occurs.
