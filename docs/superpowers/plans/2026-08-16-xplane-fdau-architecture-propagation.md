# xplane-fdau Architecture Propagation Implementation Plan

- **Governance:** historical
- **Status:** completed
- **Disposition:** Approved architecture propagation completed on the temporary design branch; preserved as the execution record for the 2026-08-16 scope amendment.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make every active xplane-fdau design and governance surface express the approved X-Plane-specific, transport-free core; local ARINC and FDM/FOQA ownership; external client adapters; multi-version Python policy; and governed dependency-refresh parity.

**Architecture:** Preserve the two imported q4xpcc architecture documents byte-for-byte and make a repository-owned amendment authoritative for the clarified scope. Propagate that authority into active specifications, roadmap/backlog state, handoff, public documentation, and historical design headers without rewriting historical execution facts. Treat FDM as the deterministic technical analysis subsystem and FOQA as the externally governed program context supported by core ports and records.

**Tech Stack:** Markdown, MkDocs, Python 3.12-3.14, Python `unittest`, repository backlog parsers, Git.

**Spec:** `docs/architecture/xplane_fdau_core_scope_amendment.md`

## Global Constraints

- Keep `docs/architecture/xplane12_virtual_fdau_ecosystem_design.md` and `docs/architecture/xplane12_foqa_fdr_addon_design_spec_v2.md` byte-for-byte unchanged.
- Keep the distributed runtime pure Python and standard-library-only.
- `xplane-fdau` never imports or communicates through q4xpcc, `xplane-webapi`, XPPython3, `xp`, XPLM, or a network client.
- Python compatibility is `>=3.12,<3.15`; 3.12, 3.13, and 3.14 remain mandatory source and installed-wheel verification targets.
- An exact embedded-Python pin belongs to the concrete XPPython3 client; the core is not pinned to `3.12.x`.
- ARINC implementations are local, edition-pinned, requirements-traced, standard-library capabilities; concrete transport and device I/O remain external.
- FDM and FOQA-support mechanics are local capabilities; approved-program governance, identity custody, corrective-action authority, and regulatory claims remain external.
- Keep native X-Plane `.fdr`, canonical FDAU archives, and ARINC representations distinct.
- Add dependency-refresh parity without comparing or vendoring Superpowers.
- Do not push, tag, publish, or create a release.

---

### Task 1: Finalize the governing architecture and public boundary

**Files:**
- Create: `docs/architecture/xplane_fdau_core_scope_amendment.md`
- Modify: `docs/architecture/README.md`
- Modify: `README.md`
- Modify: `docs/index.md`
- Modify: `mkdocs.yml`

**Interfaces:**
- Consumes: the provenance-locked parent architecture, FAA AC 120-82, and the approved conversation decisions.
- Produces: the current scope authority referenced by every later task.

- [ ] **Step 1: Write the architecture amendment**

  Record the mission, X-Plane bounded context, client/adapter dependency direction, local domain ownership, native-FDR/ARINC separation, mandatory FDM/FOQA pipeline, AC 120-82 mapping, Python policy, roadmap consequences, and acceptance criteria. Link the official FAA PDF directly and distinguish technical FDM/FOQA support from organizational approval and legal protections.

- [ ] **Step 2: Link the amendment from the architecture index**

  State that the imported hashes remain authoritative evidence of provenance while the amendment supersedes their simulator-neutral and downstream-FDM/FOQA interpretations.

- [ ] **Step 3: Align public overview language**

  In `README.md` and `docs/index.md`, use “X-Plane-specific, transport-free kernel,” name external XPPython3/XPLM and `xplane-webapi` clients, state the tested 3.12-3.14 range, describe ARINC and FDM/FOQA as roadmap-owned capabilities, and avoid claiming incomplete features are shipped.

- [ ] **Step 4: Expose the amendment in MkDocs navigation**

  Add `Architecture -> Core scope` without exposing either provenance-locked imported document as current standalone guidance.

- [ ] **Step 5: Check document mechanics**

  Run: `git diff --check`

  Expected: exit 0 with no whitespace errors.

- [ ] **Step 6: Commit the governing design**

  ```powershell
  git add README.md docs/architecture/README.md docs/architecture/xplane_fdau_core_scope_amendment.md docs/index.md mkdocs.yml docs/superpowers/plans/2026-08-16-xplane-fdau-architecture-propagation.md
  git commit -m "docs: define the X-Plane FDAU core boundary"
  ```

### Task 2: Propagate the authority through design specifications and plans

**Files:**
- Modify: `AGENTS.md`
- Modify: `docs/superpowers/specs/2026-08-08-xplane-fdr-core-design.md`
- Modify: `docs/superpowers/specs/2026-08-09-src-layout-migration-design.md`
- Modify: `docs/superpowers/specs/2026-08-09-xplane-fdau-backlog-status-skill-design.md`
- Modify: `docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md`
- Modify: `docs/superpowers/specs/2026-08-09-xplane-fdau-identity-fdr-kernel-migration-design.md`
- Modify: `docs/superpowers/specs/2026-08-15-xplane-fdau-local-workflow-skills-design.md`
- Modify: every existing file under `docs/superpowers/plans/`

**Interfaces:**
- Consumes: `docs/architecture/xplane_fdau_core_scope_amendment.md`.
- Produces: one unambiguous authority chain for active work and explicit context on historical records.

- [ ] **Step 1: Make the amendment mandatory session-entry reading**

  Add it immediately after the parent architecture in `AGENTS.md`, explain that it governs core purpose and FDM/FOQA ownership, and retain the existing migration and active-contract reading order.

- [ ] **Step 2: Amend historical design records without rewriting them**

  Add a dated blockquote to the superseded xplane-fdr design and completed identity-migration design. State that their increment scope and executed facts remain historical, while current product ownership and Python policy come from the amendment.

- [ ] **Step 3: Align active structural and governance designs**

  Link the amendment from the source-layout and backlog-governance specifications. Clarify that an external boundary can represent client adoption or organizational FOQA governance, but reusable FDM/FOQA code is a local roadmap child.

- [ ] **Step 4: Align the canonical-contract design**

  Make provider neutrality explicitly mean neutrality among X-Plane access paths. Change FDM/FOQA and ARINC exclusions to increment-only exclusions, add an FDM/FOQA extension boundary grounded in evidence qualification and provenance, and replace “downstream FDM/FOQA” with later local analysis work.

- [ ] **Step 5: Add dependency-refresh workflow design**

  Expand the local-workflow specification to cover `T2.2 refresh-dependencies`: discover the newest stable `uv`, retain an exact repository `uv` pin, refresh toward stable releases through review, use compatible constraints plus the lock for ordinary development dependencies, reject prereleases unless explicitly approved, run lock/quality/artifact validation, and make no Superpowers comparison.

- [ ] **Step 6: Contextualize existing plans**

  Add a concise current-architecture note to every historical/completed plan rather than changing commands that document what was executed. Update the active source-layout plan to reference the amendment and the new `B1.1` prerequisites while retaining its 3.12-3.14 verification matrix.

- [ ] **Step 7: Commit design propagation**

  ```powershell
  git add AGENTS.md docs/superpowers/specs docs/superpowers/plans
  git commit -m "docs: propagate the amended FDAU architecture"
  ```

### Task 3: Reconcile roadmap, backlog, and handoff contracts

**Files:**
- Modify: `tests/test_backlog_governance.py`
- Modify: `tests/test_backlog_status_cli.py`
- Modify: `ROADMAP.md`
- Modify: `BACKLOG.md`
- Modify: `HANDOFF.md`

**Interfaces:**
- Consumes: the amended architecture and the active Markdown-governance schema.
- Produces: selectable local `F1.*` and `T2.2` work with exact dependencies and acceptance evidence.

- [ ] **Step 1: Write failing roadmap-contract expectations**

  Add epic `F` with children `F1.1` through `F1.6`, add `T2.2` to epic `T2`, update the external-boundary titles to retain only client adoption and approved-program governance, and increase the parsed local-child count from 54 to 61.

- [ ] **Step 2: Verify the expectations fail before authority changes**

  Run: `uv run python -m unittest tests.test_backlog_governance tests.test_backlog_status_cli -v`

  Expected: failures identify the missing `F1.1`-`F1.6` and `T2.2` roadmap entries.

- [ ] **Step 3: Add the local FDM/FOQA-support epic**

  Add these dependency-ordered roadmap children after standards work:

  - `F1.1`: AC 120-82 terminology, analysis ports, profile, evidence, and finding contracts; depends on `C4.4`, `R1.7`.
  - `F1.2`: evidence qualification, flight/phase segmentation, and derived-parameter provenance; depends on `F1.1`, `A1.7`.
  - `F1.3`: versioned event sets, prerequisites, detection, and severity; depends on `F1.2`.
  - `F1.4`: candidate/validated finding lifecycle and auditable review records; depends on `F1.3`.
  - `F1.5`: comparable-profile aggregation, trend analysis, and report projections; depends on `F1.4`.
  - `F1.6`: de-identification/security/retention policy ports and end-to-end analysis conformance; depends on `F1.5`.

  Keep these children outside release gate `G1` and state that the technical implementation is local while program authority remains external.

- [ ] **Step 4: Add dependency-refresh parity and ordering**

  Add `T2.2` after `T2.1`, dependent on `T2.1`. Keep `T3.1` dependent on `T2.1`. Change `B1.1` to depend on both `T2.2` and `T3.1`, and record newest-stable `uv` discovery plus lock/quality verification in the `T2.2` acceptance gates.

- [ ] **Step 5: Mirror all local children in BACKLOG.md**

  Add the seven new rows once, in roadmap order, with `queued` state and exact dependencies. Add measurable acceptance headings for every new child, replace the downstream-FDM statement, and retain external `F2.1` only as approved FOQA program governance and claims.

- [ ] **Step 6: Update current position and handoff**

  Record the amendment as governing architecture, state that ARINC and FDM/FOQA are later local capabilities, document the `>=3.12,<3.15` policy separately from the XPPython3 client pin, and identify `T2.2` as a required peer prerequisite of `T3.1` before `B1.1`.

- [ ] **Step 7: Verify roadmap/backlog contracts pass**

  Run: `uv run python -m unittest tests.test_backlog_governance tests.test_backlog_status_cli -v`

  Expected: all tests pass.

- [ ] **Step 8: Commit governance reconciliation**

  ```powershell
  git add ROADMAP.md BACKLOG.md HANDOFF.md tests/test_backlog_governance.py tests/test_backlog_status_cli.py
  git commit -m "docs: schedule local standards analysis and refresh work"
  ```

### Task 4: Verify the complete documentation change

**Files:**
- Verify: all files changed by Tasks 1-3

**Interfaces:**
- Consumes: the complete documentation and governance diff.
- Produces: evidence that documentation, authority parsing, imported provenance, and repository quality remain intact.

- [ ] **Step 1: Scan for unresolved architecture contradictions**

  Search repository-owned Markdown for exact-3.12 core pins, simulator-neutral claims, downstream FDM/FOQA ownership, bundled adapters, and native-FDR/ARINC conflation. Historical text is acceptable only when its header marks it historical and links the current amendment.

- [ ] **Step 2: Run documentation and governance contracts**

  Run: `uv run python -m unittest tests.test_public_api tests.test_documentation tests.test_backlog_governance tests.test_backlog_status_cli -v`

  Expected: all tests pass, including the imported-document hashes.

- [ ] **Step 3: Build the documentation site**

  Run: `uv run mkdocs build --strict`

  Expected: exit 0 with no warnings.

- [ ] **Step 4: Run documentation quality**

  Run: `uv run python tools/quality.py docs`

  Expected: all documentation checks pass.

- [ ] **Step 5: Run the full repository hygiene gate**

  Run: `uv run python tools/hygiene.py`

  Expected: all `unittest`, coverage, quality, pre-commit, artifact, and hygiene checks pass.

- [ ] **Step 6: Inspect final scope**

  Run: `git status --short` and `git diff --check HEAD~3..HEAD`.

  Expected: only the planned architecture, design, governance, documentation, and contract-test files changed; no imported architecture bytes changed.
