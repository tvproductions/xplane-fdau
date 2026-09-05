# D1.3 Reviewed q4xpcc Phase 24A Handoff Implementation Plan

- **Governance:** historical
- **Status:** completed
- **Disposition:** D1.3 reviewed q4xpcc Phase 24A consumer handoff completed with accepted independent review and four committed verification gates; preserved as the planning-only execution record without canonical-contract implementation, artifact, consumer adoption, or release activity.

> **For agentic workers:** Use `superpowers:subagent-driven-development` for
> the tasks below, with independent task and final branch review.

**Goal:** Deliver a reviewed, revision-pinned q4xpcc planning brief and verify D1.3's four gates.

**Architecture:** The brief summarizes approved D1.1/D1.2 inputs without new semantics. BACKLOG remains the delivery ledger; I1.0 becomes reportable only after D1.3 verifies. The clean emission revision travels with the brief as a delivery envelope, avoiding a document that claims to contain its own enclosing commit hash.

**Tech Stack:** Markdown, Python standard-library `unittest`, existing backlog status CLI, MkDocs, Git, and repository quality tooling.

**Spec:** `docs/superpowers/specs/2026-08-22-q4xpcc-contract-handoff-readiness-design.md`

## Global Constraints

- One primary child: `D1.3`. Preserve D1.1 and D1.2 verified evidence.
- No runtime, metadata, schema, fixture, conformance corpus, provider, consumer-repository, or approved contract-design changes.
- Use Python's `unittest` only; runtime remains standard-library-only.
- The brief permits planning reconciliation only after D1.3 verification. I1.1 still requires C4.4, I1.2 still requires A1.9, and G1 remains waiting.
- No push, tag, publication, release, external message, or q4xpcc file mutation.
- Preserve all C/A/R/P/S/F delivery states, licensed-source blocks, and gates.
- Use the existing approved D1 design as authority; no new handoff workflow, CLI, or state authority.
- Final local selection is T1.3, specified at 0/4 with no new plan or evidence. I1.0 is a statusless external next action and never a selectable local child.
- Tests of human prose are unnecessary. Update the existing governance/status contracts for the lifecycle transition; independently review the brief against approved source documents.

## Task 1: Commit the concise consumer brief and obtain independent review

**Files:**

- Create: `docs/architecture/q4xpcc_phase_24a_contract_handoff.md`.
- Modify: this plan's task checkboxes only.
- Create ignored working report: `.superpowers/sdd/2026-09-05-d1-3-q4xpcc-handoff/task-1-report.md`.

**Interfaces:**

- Consumes the clean source snapshot `f86c6f939f1fdbfd354660c432363b9aa7f8444d`, approved canonical and D1.2 designs, D1 readiness design, scope amendment, ROADMAP, and D1.1/D1.2 committed review/gates.
- Produces a committed, reviewable human brief. D1.3 remains specified/0-of-4 until Task 2. The controller supplies independent review and its exact revision to Task 2.

- [x] Read the brief's governing sources. Focus canonical sections Package and dependency boundaries, Contract families and versions, Schema and conformance corpus; D1.2 sections New family inventory and future resources, Deployment policy and portable receipt, Public modules and dependency direction, and q4xpcc Phase 24A reconciliation. Read the D1 readiness design completely.
- [x] Write a concise brief (target 100–150 lines). Include a source-snapshot field naming the exact clean base above; clarify this is an input-document pin, not a release pin or a claim that the brief existed at that revision. The delivery envelope reports the actual emission HEAD separately. State readiness is conditional on D1.3 verified evidence in BACKLOG.
- [x] Include links to parent architecture, scope amendment, approved canonical design, approved D1.2 design, D1 readiness design, and committed D1.1/D1.2 review/gates. Record approval dates from source metadata, repository/distribution/import identity, and current 0.1.0 unreleased status. Distinguish approved Python policy `>=3.12,<3.15` from current metadata `>=3.12` pending T2.2.
- [x] State FDAU owns generic measurements, binding contracts, normalization/acquisition, timing/quality/continuity, fan-out, recording/recovery/replay, and native projection. External clients own simulator I/O, XPLM/XPPython3/Web API adapters; q4xpcc owns cards, missions, findings, guidance, authorization, application orchestration, and its specific definitions. ARINC and FDM/FOQA mechanics are later local work with their existing boundaries.
- [x] Map the four exact Phase 24A plan filenames from parent section 22 to their reconciliation actions. Preserve the distinction between acquisition sufficiency and operational findings.
- [x] List future canonical semantic package roots, schema roots `xplane_fdau/schemas/` and `docs/schemas/`, the five canonical family stems, the D1.2 inventory link for all 32 additional families and their owning children, and all three conformance roots. Mark every target as intended, undelivered. Show the future runner `python -m xplane_fdau.conformance --manifest PATH --output PATH` as a future verification command, with exit 0/1/2 semantics and packaged-manifest resolution. Deployment families and their runner spelling belong to A1.9; C4.4 does not imply acquisition deployment receipt delivery.
- [x] Summarize independently trusted expected release pins, exact wheel/source/version and hashes, whole namespace inventory, single verified import root, empty runtime dependencies, and installed-wheel versus exact bundled-package metadata rules. No fabricated wheel/hash/receipt. Native FDR is lossy; current schema-v1 projection is live/in-session and offline canonical-archive projection requires a later reviewed contract.
- [x] Verify with `uv run python -m unittest tests.test_public_api tests.test_documentation -q`, `uv run mkdocs build --strict`, and `git diff --check`. Run full quality before the brief commit. The active untracked plan creates the one known inventory-bootstrap failure until Task 2 finalizes it; record that exact failure without changing the production parser or relaxing tests. To keep the brief commit independently green, temporarily stage this plan in its ignored SDD directory while validating/committing Task 1, then restore it to its canonical path for Task 2.
- [x] Commit only the brief using `docs: add q4xpcc Phase 24A planning brief`. Report its SHA, focused/documentation/full-quality results, source facts, and concerns to the report path. Do not mark independent review accepted yourself.

## Task 2: Verify the handoff and close D1.3 test-first

**Files:**

- Modify: `tests/test_backlog_governance.py`, `tests/test_backlog_status_cli.py`, `BACKLOG.md`, `HANDOFF.md`, this plan.
- Create: `.superpowers/sdd/2026-09-05-d1-3-q4xpcc-handoff/review.md`, `gate-1.md`, `gate-2.md`, `gate-3.md`, `gate-4.md`.
- Create ignored working report: `.superpowers/sdd/2026-09-05-d1-3-q4xpcc-handoff/task-2-report.md`.

**Interfaces:**

- Consumes the committed brief and the controller's actual accepted independent Task 1 review.
- Produces D1.3 verified 4/4, local selection T1.3 specified 0/4, a historical completed plan, four evidence records, and a reviewed source-pinned consumer brief ready for clean-HEAD emission.

- [x] Before edits, verify the brief commit is clean (the plan may be temporarily held in its ignored SDD directory), capture `git rev-parse HEAD`, emit that exact revision followed by `git show HEAD:docs/architecture/q4xpcc_phase_24a_contract_handoff.md`, and record the brief SHA-256. This is the gate-3 clean delivery envelope; source-snapshot and emission revisions are explicitly different identities. Restore the plan afterward.
- [x] Update the existing final-state governance expectations first: D1.3 inventory becomes verified, its plan links to this plan, gates are 4/4, review points to this task's review.md; sole active child becomes T1.3. All D1 acceptance statements stay exact, and all three D1 children have four checked gates. Update handoff-order expectations for completed D1.3 and I1.0 eligibility. Keep all downstream and external-boundary tests intact.
- [x] Update the real status CLI integration test so all three D1 children report verified/dependency-ready/4-of-4 with exact existing/new plan and evidence paths; T1.3 is selected and dependency-ready. Assert `recommendation` is still null and I1.0 remains outside the local-child inventories; this task does not implement the future next-action CLI.

  Expected D1.3 output values:

  ```python
  self.assertEqual("verified", child["status"])
  self.assertEqual(4, child["gates"]["satisfied"])
  self.assertEqual(4, child["gates"]["total"])
  self.assertTrue(child["dependency_ready"])
  self.assertEqual(
      "docs/superpowers/plans/2026-09-05-d1-3-q4xpcc-handoff.md",
      child["plan"],
  )
  ```

- [x] Run `uv run python -m unittest tests.test_backlog_governance tests.test_backlog_status_cli -q` and record genuine failing assertions against the still-unmodified BACKLOG/HANDOFF. Do not add prose-presence tests or weaken parser rules.
- [x] Record accepted review metadata with Child `D1.3`, Gate em dash, Kind review, Result accepted, Date 2026-09-05, Subject `Independent q4xpcc Phase 24A consumer handoff review`. Cite the actual reviewer verdict and reviewed brief SHA; do not invent an assessment.
- [x] Write four gate records with Child `D1.3`, ordinal Gate, Kind verification, Result passed, Date 2026-09-05, and these subjects: `Verified prerequisite designs and committed review evidence`; `Reviewed consumer brief and repository handoff agreement`; `Clean committed emission and exact revision identity`; `Planning reconciliation eligibility and preserved delivery boundaries`. Include exact evidence, inspected paths and revisions, command results, and limitations. Gate 3 records the clean delivery envelope captured before edits and the pinned brief hash, without claiming an enclosing commit can contain its own SHA.
- [x] Update BACKLOG current position and exactly D1.3's row and four checkbox/evidence pairs. Select T1.3 only. Report I1.0 eligibility in prose, preserving its statusless external record and all stronger thresholds. Update HANDOFF to link the brief, plan, accepted review and gates, state D1.3 complete, I1.0 eligible, T1.3 next local work, and no delivered canonical/runtime/artifact or release readiness. Keep historical checkpoints explicitly historical.
- [x] Finalize this plan with historical/completed/Disposition metadata and checked steps only when done, following the D1.2 completed-plan precedent.
- [x] Run focused governance/status tests; `uv run python -m unittest tests.test_public_api tests.test_documentation -q`; human/JSON status (no finding, no recommendation); full `uv run python tools/quality.py check`; `uv run mkdocs build --strict`; and `git diff --check`. Record actual counts and results. Existing environment setup may print a uv-build version-range warning; do not change dependencies for this documentation slice.
- [x] Inspect the exact scope. Commit only the listed files (force-add only the five intended evidence files under ignored .superpowers) using `docs: verify D1.3 q4xpcc planning handoff`. Report commit and real verification evidence. Controller performs task and whole-branch review, resolves findings, then follows the user's established local integration/cleanup preference and emits the final clean HEAD with the brief link.
