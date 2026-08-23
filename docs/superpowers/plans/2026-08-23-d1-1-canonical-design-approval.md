# D1.1 Canonical C1–C4 Design Approval Implementation Plan

- **Governance:** historical
- **Status:** completed
- **Disposition:** D1.1 canonical C1-C4 design approval completed with accepted independent review and four committed verification gates; preserved as the design-only execution record without C implementation, artifact, adoption, or release activity.

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:executing-plans` to execute the sequential design/governance
> tasks and `superpowers:requesting-code-review` for the independent review.
> Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Review, make exact, independently approve, and record the canonical C1–C4 design as implementation authority without delivering any C1–C4 runtime behavior or evidence.

**Architecture:** Treat the canonical-contract specification as the sole cross-epic semantic authority for C1.1–C4.4, with the scope amendment governing ownership and dependency direction. Resolve every language-neutral wire, identity, timing, quality, schema, fixture, validation, and Python/native conformance decision in the specification; then record D1.1 verification separately from the still-undelivered C1–C4 children.

**Tech Stack:** Markdown, JSON/URI contract notation, Python 3.12+ standard library, Python `unittest`, repository governance/status tooling, MkDocs, repository quality tooling, and Git.

**Spec:** `docs/superpowers/specs/2026-08-22-q4xpcc-contract-handoff-readiness-design.md`

## Global Constraints

- Read `HANDOFF.md`, `ROADMAP.md`, `BACKLOG.md`, the complete parent architecture, the repository scope amendment, the completed identity/native-FDR migration specification and plan, the D1 readiness design, and the complete canonical-contract draft before editing.
- Change design, governance, handoff, plan/evidence Markdown, and only the focused governance/status test expectations that encode the D1 lifecycle. Do not change runtime code, package metadata, JSON schemas, fixtures, generated artifacts, production tooling, C1–C4 implementation plans, or q4xpcc files.
- Use Python's `unittest` framework only. Never add, invoke, or suggest pytest.
- Keep the runtime dependency boundary standard-library-only and preserve external ownership of XPPython3/XPLM, `xplane-webapi`, simulator I/O, q4xpcc policy, and q4xpcc operational findings.
- Keep native X-Plane textual FDR v3/v4 a deliberately lossy projection and sink, not the canonical FDAU archive or canonical measurement model.
- Approving the cross-epic design advances `C1.1` through `C4.4` only to `specified`; every C delivery gate remains unchecked and at `0/4` or `0/5`, every C Plan/Review/Resume field remains `—`, and no C implementation or artifact evidence is created.
- `D1.1` may become `verified` only after all four D1.1 gate files and accepted independent-review evidence are committed. `D1.2` then becomes the selected dependency-ready batch; `D1.3`, `I1.0`, `I1.1`, `I1.2`, G1, and release authorization remain unmet.
- Do not push, tag, publish, create a GitHub release, create a PyPI release, or issue the future D1.3 q4xpcc consumer brief.

---

### Task 1: Make the canonical design exact and self-consistent

**Files:**

- Modify: `docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md`

**Interfaces:**

- Consumes: the parent architecture, scope amendment, D1.1 acceptance gates, and the existing draft.
- Produces: one still-unapproved candidate specification with exact version-1 wire and semantic decisions and no placeholder, contradiction, or ambiguous implementation choice.

- [x] **Step 1: Freeze governance and version vocabulary without approving the document**

  Keep `Status: draft` and `Approval: —` during editing. Define exact family names, family URIs, schema IDs, media type, `$schema` URI, `schema_version` lexical type/value, the relationship between family URI and schema version, and the five allowed top-level document keys/field order rules where field order is semantically relevant.

- [x] **Step 2: Freeze canonical JSON and hashing**

  Specify parse-domain versus typed-model-domain numbers, duplicate-key rejection, Unicode scalar/NFC validation, escaping, UTF-8/LF bytes, exact signed-64-bit integer handling, exact RFC 8785/ECMAScript binary64 token production plus the integral-real adaptation, negative zero, exponent thresholds/sign/casing, canonical key ordering, SHA-256 spelling, and self-hash preimages. State whether schema documents themselves are canonical-hashed (they are not) and require golden vectors to pin every lexical boundary.

- [x] **Step 3: Freeze identity, provenance, reference, and typed-value wire shapes**

  Define exact JSON objects, required/optional properties, enum values, syntax/ranges, and invariants for semantic IDs, revisions, UUIDs, sequences/generations, `Authority`, `ProvenanceSource`, `ProducerIdentity`, `DefinitionRef`, `RecordRef`, `AlgorithmRef`, typed inline values, enumeration members/values, vectors/arrays, and `PayloadReference`. Make null/absence and caller-supplied self-hash behavior explicit.

- [x] **Step 4: Freeze measurement and binding catalog shapes**

  Define exact field inventories and invariants for `MeasurementCatalog`, `MeasurementDefinition`, axes, ranges, shapes, enumerations, applicability selectors, freshness/interpolation/discontinuity policy, `SourceBindingCatalog`, source dependencies and companions, transform steps, failure dispositions, phases, replay policy, canonical ordering, hashes, and pure cross-catalog validation. Distinguish binding-declared source shape from observation-reported shape and prohibit executable transform content.

- [x] **Step 5: Freeze timing and evidence-record shapes**

  Define exact fields and matrices for `ClockDomain`, `ClockReading`, `UtcInstant`, `ClockAnchor`, `ObservationTiming`, `RawObservation`, `MeasurementSample`, and `MeasurementFrame`. Pin UTC nanosecond grammar, clock-domain comparability, signed/unsigned ranges, cycle/simulator-time/time-speed rules, raw value-state encoding, status/value compatibility, normalized-value compatibility, status-to-quality implications, lineage reference types, derivation closure/cycle scope, sample/frame ordering, and frame timing/reference closure.

- [x] **Step 6: Freeze errors, schemas, fixtures, and conformance**

  Define JSON property paths as RFC 6901 JSON Pointers, exact error-class precedence, bounded diagnostic behavior, schema dialect/IDs/resource inventory, byte-parity rules, fixture manifest version and case fields, accepted/rejected/canonical dispositions, exact canonical-hash evidence, Python/native runner input/output and exit classification, and the distinction between schema validation and semantic validation.

- [x] **Step 7: Run the specification self-review**

  Run:

  ```powershell
  rg -n -i "TBD|TODO|FIXME|placeholder|to be decided|implementation-defined|may choose|for example|such as|normally|optional.*when applicable" docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md
  rg -n "pytest|xpwebapi|xplane-webapi|XPPython3|XPLM|q4xpcc|ARINC|FOQA|FDR" docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md
  git diff --check
  ```

  Expected: no unresolved placeholder or implementation-choice wording; every provider/consumer/standards/native-format mention preserves the approved ownership boundary; whitespace checks pass. Contextual non-normative uses of “for example” or “such as” must be rewritten or explicitly labeled non-normative.

- [x] **Step 8: Commit the review candidate**

  ```powershell
  git add docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md
  git commit -m "docs: make canonical contracts exact"
  ```

  The plan remains untracked during execution because current governance tests
  enumerate active plans exactly. Its presence creates one known temporary
  local RED, while the committed candidate tree contains only the draft
  specification. Task 4 records the plan only after its metadata truthfully
  becomes historical/completed, matching the repository's bootstrap-plan
  precedent.

### Task 2: Obtain independent design review and resolve every load-bearing finding

**Files:**

- Create: `.superpowers/sdd/2026-08-23-d1-1-canonical-design-approval/review.md`
- Modify: `docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md`
- Modify: files explicitly identified by an accepted review finding, limited by the global constraints

**Interfaces:**

- Consumes: the committed Task 1 candidate and D1.1's first three acceptance gates.
- Produces: accepted independent review evidence with no unresolved Critical or Important/load-bearing finding.

- [x] **Step 1: Request an independent whole-design review**

  Use `superpowers:requesting-code-review` with a clean-context reviewer. Give the reviewer the Task 1 base/head range, the D1.1 plan, the canonical draft, the parent architecture, scope amendment, readiness design, ROADMAP C1–C4 order, and BACKLOG C/D gates. Require line-specific findings ranked Critical, Important, or Minor and a final `ACCEPTED`/`NOT ACCEPTED` assessment. Require explicit audits of canonical JSON/numbers/hashing, identity/provenance/references, typed values, timing, status/quality matrices, catalog and record closure, schema/fixture parity, error determinism, Python/native conformance, ownership, dependency order, and scope exclusions.

- [x] **Step 2: Resolve findings with technical evidence**

  Use `superpowers:receiving-code-review`. Fix every Critical and Important/load-bearing finding. Resolve a Minor finding when it removes ambiguity or contradiction; otherwise record why it is non-load-bearing. Do not approve the specification while the reviewer reports `NOT ACCEPTED`.

- [x] **Step 3: Request re-review after any correction wave**

  Re-run the Step 1 audit against the corrected head. Continue until the reviewer reports `ACCEPTED` with no unresolved load-bearing finding.

- [x] **Step 4: Record exact review evidence and commit corrections**

  Create `review.md` with `Child: D1.1`, `Gate: —`, `Kind: review`, `Result: accepted`, date, reviewed revisions, reviewer findings, resolutions, and the accepted final assessment. Commit the corrected specification and review evidence:

  ```powershell
  git add docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md .superpowers/sdd/2026-08-23-d1-1-canonical-design-approval/review.md
  git commit -m "docs: resolve canonical design review"
  ```

### Task 3: Approve the design and record D1.1/C1–C4 governance truth

**Files:**

- Modify: `docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md`
- Modify: `BACKLOG.md`
- Modify: `tests/test_backlog_governance.py`
- Modify: `tests/test_backlog_status_cli.py`
- Create: `.superpowers/sdd/2026-08-23-d1-1-canonical-design-approval/gate-1.md`
- Create: `.superpowers/sdd/2026-08-23-d1-1-canonical-design-approval/gate-2.md`
- Create: `.superpowers/sdd/2026-08-23-d1-1-canonical-design-approval/gate-3.md`
- Create: `.superpowers/sdd/2026-08-23-d1-1-canonical-design-approval/gate-4.md`

**Interfaces:**

- Consumes: the accepted independent review and exact D1.1 acceptance gates.
- Produces: approved canonical design authority, verified D1.1 evidence, and specified-but-undelivered C1.1–C4.4 children.

- [x] **Step 1: Mark only the canonical cross-epic design approved**

  Set the canonical design metadata to `Status: approved` and `Approval: 2026-08-23 — Jeff / tvproductions`. Do not mark any C child implemented, reviewed, verified, or released.

- [x] **Step 2: Advance the C inventory only to specified**

  In `BACKLOG.md`, set `C1.1` through `C4.4` to `specified`, keep the approved canonical design link in every Spec cell, preserve every dependency and outcome, keep Plan/Review/Resume/Reason as `—`, and keep all gate counts at zero. Do not check any C acceptance checkbox.

- [x] **Step 3: Record D1.1's four gate files**

  Each gate file uses the repository evidence metadata family with `Child: D1.1`, its exact gate number, `Kind: verification`, `Result: passed`, and date. Gate 1 cites approved metadata, placeholder/contradiction scans, and accepted review. Gate 2 maps each exact contract-decision family to specification sections. Gate 3 maps scope-amendment ownership/dependency direction and the acquisition-quality/operational-finding distinction. Gate 4 records the exact C1.1–C4.4 inventory transition, all-zero delivery gates, absent C plans/reviews/evidence, and unchanged release/adoption boundaries.

- [x] **Step 4: Close the D1.1 backlog row and acceptance checkboxes atomically**

  Set D1.1 to `verified`, link this plan, show `4/4`, link `review.md`, and keep its governing D1 design link. Check exactly the four D1.1 acceptance gates and attach the matching gate evidence links. Select `D1.2`; leave D1.2/D1.3 `specified` at `0/4` with no plan/review/evidence.

- [x] **Step 5: Update exact final-state governance expectations**

  In `tests/test_backlog_governance.py`, replace only the D1.1 initial-row and
  active-selection expectations with the verified row, plan/review links,
  4/4 evidence, active D1.2, accepted-review metadata, and exact C1.1–C4.4
  `specified`/zero-gate/no-plan/no-review assertions. Preserve D1.2/D1.3
  specified/0-of-4 expectations. In `tests/test_backlog_status_cli.py`, update
  only current-repository human/JSON expectations to D1.1 verified and
  dependency-complete, D1.2 specified/dependency-ready and selected, D1.3
  specified/not-ready, with the same 64-child inventory and gate statements.

- [x] **Step 6: Run focused governance and status checks**

  ```powershell
  uv run python -m unittest tests.test_backlog_governance tests.test_backlog_status_parse tests.test_backlog_status_report tests.test_backlog_status_cli -v
  uv run python .codex/skills/backlog-status/scripts/backlog_status.py status
  uv run python .codex/skills/backlog-status/scripts/backlog_status.py status --json
  git diff --check
  ```

  Expected: D1.1 is verified at 4/4 with plan/review/evidence; D1.2 is the sole active and dependency-ready child at 0/4; D1.3 is not dependency-ready; C1.1–C4.4 are specified with unchanged zero delivery gates; no output claims C implementation, adoption, artifact, or release readiness.

- [x] **Step 7: Commit approval and evidence**

  ```powershell
  git add docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md BACKLOG.md tests/test_backlog_governance.py tests/test_backlog_status_cli.py .superpowers/sdd/2026-08-23-d1-1-canonical-design-approval
  git commit -m "docs: approve canonical contract design"
  ```

### Task 4: Update the resumable handoff and verify D1.1 completely

**Files:**

- Modify: `HANDOFF.md`
- Modify: `docs/superpowers/plans/2026-08-23-d1-1-canonical-design-approval.md`

**Interfaces:**

- Consumes: committed D1.1 approval/evidence and unchanged release boundaries.
- Produces: a clean committed D1.1 checkpoint whose next batch is exactly D1.2.

- [x] **Step 1: Update the sole current handoff**

  Record D1.1's approved specification, accepted review, four committed gates, and C1.1–C4.4 `specified`/zero-gate state. Name D1.2 as the next selected batch, followed by D1.3; state that I1.0 planning reconciliation remains ineligible until D1.3 verifies and I1.1/I1.2/G1/release remain unchanged.

- [x] **Step 2: Finalize this plan's execution metadata**

  After all prior steps pass, set `Governance: historical`, `Status: completed`, and a disposition stating that D1.1 design approval completed with accepted independent review and four committed gates, without C implementation or release activity. Check only steps whose commands/evidence exist.

- [x] **Step 3: Run fresh complete verification**

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

  Expected: every command exits 0; the full suite remains at or above the 276-test baseline; repository quality, strict documentation, and documentation quality pass; status is truthful; no runtime/distribution/schema/fixture/artifact/C-plan file changed.

- [x] **Step 4: Inspect scope and commit the final handoff**

  ```powershell
  git diff --name-only d0c1359..HEAD
  git status --short
  git diff --check
  ```

  Expected scope: only the canonical design, this D1.1 plan, BACKLOG, HANDOFF,
  the two focused governance/status tests, D1.1 review evidence, and four D1.1
  gate files. Commit:

  ```powershell
  git add HANDOFF.md docs/superpowers/plans/2026-08-23-d1-1-canonical-design-approval.md
  git commit -m "docs: record D1.1 canonical approval handoff"
  ```

- [x] **Step 5: Verify the clean local checkpoint without publishing**

  ```powershell
  git status --short --branch
  git log -6 --oneline
  ```

  Expected: clean local `main`, D1.1 closing commits visible, and no push, tag, publication, release, artifact, or q4xpcc handoff brief.
