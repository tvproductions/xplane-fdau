# Skills-first Native Adoption Design

- **Governance:** active
- **Status:** draft
- **Date:** 2026-10-11
- **Decision owner:** Jeff / tvproductions
- **Roadmap epic:** `T2`
- **Roadmap children:** `T2.1`, `T2.2`
- **Approval:** —

## Intent and scope

Jeff designated `tvproductions/gz-skills-first-starter` as the new baseline for
skills-first projects and approved proceeding with the proposed two-stage
adoption. This design covers the first stage: native upstream plugin sources,
provenance, task routing, and observable discovery. The second stage changes
Python engineering tools and invocation cadence through a separate design and
plan after this stage. The approval of the proposed scope is not recorded as
approval of this subsequently written specification.

This is a crosscutting maintenance amendment to T2.1/T2.2. It does not reopen or
advance their delivery state, select a product child, or change the verified
C1.3 implementation. Existing BACKLOG, ROADMAP, HANDOFF, domain authorities,
architecture, and release gates remain authoritative. The shared starter is the
only additional repository in the proposed adoption
scope. Its own instructions, review, tests and publication authority must be
followed there. No q4xpcc or other application repository, or upstream SP/gz-skills
implementation is changed. This FDAU save point does not edit or publish the
starter repository.

Success means one selected native source for each enabled upstream component,
accurate immutable provenance, direct project instruction routing, and fresh-session
evidence of the selected sources. Configuration presence is not proof of
installation or agent behavior.

## Historical baseline — October 11

- FDAU main: `f4ffb465c1d66633f829ed957886f096df12efb2`, clean before design.
- Starter: `4acc41595b673faabdbe9be8d38b62755048ab93`, publicly resolved and
  inspected in a separate temporary checkout. Its bundle validation passes.
- Starter read-only status: not configured; backport assessment writes nothing.
- Configure preview refuses `.agents/skills/superpowers`; isolated configuration
  validation also refuses enabled `gz-skills@gz-skills` as duplicate discovery.
- Current Superpowers: ignored checkout at v6.4.2,
  `8ca22dba9a94f28898bbce59f2537ff4d87c747d`, exposed by a junction.
- Current gz-skills: installed/enabled `gz-skills@gz-skills`, v0.5.0, selected by
  a release tag in `.codex/config.toml`.
- Another project's native SP v7.0.0 and gz-skills installation exists and is
  disabled here. It is not FDAU's selected source or authority.
- Backlog audit has no findings; no child is selected; next product action is
  drafting the C1.4 plan. This migration does not implement C1.4.

## Current assessment — October 18

FDAU is clean on `main` at `94109c1373953898ce780bc7a94c659d3c6bdc08`.
The strict backlog audit reports no findings and recommends `write_plan C1.4`;
no child is selected. The ledger records C1.3 verified at 4/4 gates. HANDOFF and
the BACKLOG introduction still describe its earlier draft state; reconcile these
current summaries during implementation without altering historical evidence.

The separately maintained starter checkout is clean at
`88928b2c6c663e37f739c80376dae42b5d8e5b4e`. GitHub's commit endpoint resolved
that full SHA and current repository HEAD to the same published commit. Its
declared template version is **0.3.2, unreleased**. The latest published release
is v0.3.0 at `a7550a6e29b88349041e70e3dbba4778be4b8235`; that release still
selects SP v6.4.1, so it is unsuitable for the agreed SP v7 selection. Published
commit availability does not make the 0.3.2 development template a tagged release.

The current starter authors and distributes **zero skills**. Its `bundle.json`,
both native catalogs, adoption/migration guidance and generated instruction
fragment were inspected. `starter.py validate` passes on its existing Python
3.14.8 interpreter. FDAU's Python 3.12 interpreter is not the starter helper's
acceptance runtime. Read-only configuration preview refuses the existing
Superpowers discovery junction; status reports `not configured` and runtime
readiness `unverified`. No adoption files or native installations were changed.

Native inventory reports `gz-skills@gz-skills` installed/enabled at **0.8.0**,
while FDAU configuration still requests **v0.5.0**. Other projects' plugin
identities are installed but disabled here; the shared `skills-first-starter`
identity is absent. This is source drift, not successful adoption.

Official GitHub queries returned SP v7.0.0 and gz-skills v0.8.0 as latest
releases. The latter resolves to `75bcd11ee9371ecff1a7b3432d2af29d4bdbb788`.
Its change from 0.7.0 adds the explicit-only release primitive and router release
guidance; it does not supply a missing stage-one installation capability. This
proposal retains the shared catalog's 0.7.0 selection to avoid a separate starter
publication or a per-project catalog. Revisit that choice when the shared catalog
adopts 0.8.0, or through an explicitly reviewed shared-catalog update. Record the
effective transition from installed 0.8.0 separately from the configured 0.5.0 pin.

Backplane has no published release. Its current upstream HEAD resolves to
`c6f0b4a518e3742053618a613d8d858f0e37e9cd`, newer than the catalog's disabled
pin. Retain the disabled catalog pin; reconsider only with the separate readiness
and FDAU requirements decision. A newer commit does not establish readiness.

## Shared plugin catalog decision

During review Jeff selected one shared starter plugin catalog, rather than an
FDAU-specific catalog. Codex calls a plugin catalog a marketplace; this document
uses that term only for required native command/configuration names. A catalog
lists upstream sources and selected commits; it is not a store or copied skill
implementation.

Configure FDAU through preview/apply from the reviewed published starter commit
`88928b2c6c663e37f739c80376dae42b5d8e5b4e`, with its existing SP v7.0.0 and
gz-skills v0.7.0 selections and Backplane disabled. Record template version 0.3.2
as an unreleased development snapshot, with its exact full SHA. This adoption
does not edit or publish the shared starter. Never use a moving branch,
fabricated SHA, or an old starter SHA with new component pins. The initially
reviewed starter revision remains historical assessment evidence.

FDAU uses the shared `skills-first-starter` catalog and plugin identities. It
creates no project-specific catalog, custom lock extension, installer or status
CLI. The common helper remains the configuration/status surface; native host
verification remains a separate acceptance dimension.

An unmodified older starter would downgrade SP to v6.4.1 and is rejected. A local
FDAU-specific catalog was initially proposed but withdrawn during user review:
it would introduce per-project catalog maintenance instead of the desired shared
baseline. The shared SP v7 candidate is now publicly available at the exact
commit above; FDAU installation remains pending this specification's approval,
an approved implementation plan and native acceptance. An ordinary Git sync of
FDAU does not publish the starter.

## Source selection

| Component | Selected release/revision | Enablement |
| --- | --- | --- |
| Superpowers | v7.0.0 / `bb92a77741419a4ab5f06e711a283343f1ada0c3` | enabled |
| gz-skills | v0.7.0 / `6ebf803e4a2775d3742c84984a03548275b7c926` | enabled |
| Superpowers Backplane | pre-release / `d0eeee829c491da02351e793544aa16ad96461bf` | disabled; not installed by this migration |

SP v7.0.0 was published 2026-10-10. Its release notes, Codex manifest and entry
skill were inspected. It changes brainstorming and fixes Windows/ledger behavior;
the implementation plan must review the remaining workflow differences before
enablement. The Codex manifest declares the skills tree and an empty hooks object.
No upstream bootstrap script is executed or cache edited. gz-skills v0.7.0 adds
project-version-aware Python guidance; the starter's tagged-install receipt
separates installation from fresh-session workflow acceptance. Review the
0.5-to-0.7 workflow changes in the implementation plan, preserving FDAU's
runtime, gate and profile policies. These are selected releases, not a perpetual
claim of latest.

`.codex/config.toml` enables only `superpowers@skills-first-starter` and
`gz-skills@skills-first-starter` among selected upstream sources, explicitly
disables Backplane, and disables `gz-skills@gz-skills` for FDAU. Preserve unrelated
configuration and installations. Inspect the host inventory for other enabled
copies; do not uninstall a shared source to make the inventory pass. Project
enablement may be changed only for the components this migration governs.

## Provenance and routing

`.skills-first/bundle.lock.json` is generated by the shared helper and records
the reviewed published starter revision and its selected component records.
FDAU does not extend its schema or override component sources independently.
The shared bundle, catalogs, selected lock, and observed installation must agree.
Review the helper's generated source URL against the canonical renamed starter
repository; reconcile stale aliases in the shared starter rather than inventing
a local provenance workaround.

Create no starter skill or skill-discovery directory. The current starter
retired `skills-first-start` and moved routing into ordinary instructions;
upstream SP/gz-skills trees are never copied. Generate `AGENTS.skills-first.md`
with FDAU's selected identities and a pointer from AGENTS. Provide
`docs/agents/skills-first.md` for ownership, installation, verification, rollback,
and the Python binding source. Read `docs/engineering/python.md`,
`docs/baseline-policy.md` and `docs/gz-skills-python.md` in the pinned reviewed
starter checkout when needed. Those are policy documents, not discoverable
skills. Reconcile the generated fragment's immediate Python/tool obligations
with FDAU's explicitly deferred second stage: clearly state that the existing
cadence and minor-line Python selector govern until that stage is approved.
Preserve the provenance of any adapted fragment and report the deferred policy
requirements as adoption gaps rather than claiming full engineering parity.

The instructions route project operations to existing project skills, engineering
selection to gzs-router, and feature design/implementation to Superpowers.
It adds no lifecycle, profile selection, autonomous job, or Backplane operation.
No lite/heavy or gzkit profile is inferred.

## Migration and recovery

1. Keep current sources active while preparing and verifying the candidate
   repository configuration in an isolated feature worktree.
2. Inventory host sources and supported manager operations. Register the reviewed
   shared catalog and install the selected SP/gz-skills through the native manager.
   Inspect any user-level changes the manager makes. Keep activation scoped to
   FDAU; if this host cannot do that, report the limitation and stop activation.
3. Reconcile FDAU enablement. Before restarting, detach its old discovery junction
   using a verified nonrecursive link-only operation. Keep the ignored checkout
   as a nondiscoverable rollback source until acceptance; do not delete its target
   through the junction or remove another project's checkout.
4. Start a fresh session in the candidate checkout. Confirm exactly one selected
   source and the expected upstream entry skills (`using-superpowers` and
   `gzs-router`). No starter entry skill is expected. Installation output is not
   enough.
5. Record acceptance evidence, complete repository checks, obtain independent
   review, and use the ordinary finishing choice before integration.

### FDAU requirements and SP-BP boundary

Jeff explicitly reserved FDAU's requirements and backlog approach. This migration
does not adopt SP-BP's requirements technique, rewrite FDAU requirements or
acceptance gates into its records, or migrate BACKLOG/HANDOFF authority. Plugin
installation or later activation alone cannot authorize those changes.

A future reviewed integration may either retain FDAU's approach or deliberately
merge it with SP-BP's. A merger must preserve FDAU's stable identities, acceptance
evidence, traceability and authority, with an explicit source mapping and conflict
resolution. Neither direction is selected by this specification. Backplane stays
disabled and uninstalled by this migration; future integration needs a separate
readiness/design decision, not an implied consequence of starter parity.

Changing host setup cannot rewrite the running session's discovered skill list.
Mark fresh-session acceptance UNKNOWN until observed. Preserve candidate state
and exact resume instructions if continuation needs another session.

Rollback restores the previous project configuration and junction to the retained
v6.4.2 checkout, then verifies discovery in a fresh session. Do not delete native
caches or uninstall sources another project uses. Record any failure and whether
rollback has been observed; a documented procedure is not an executed test.

## Project boundaries retained

- Pure Python and standard-library-only application runtime; no simulator/network
  client dependencies. Python 3.12 minor-line support follows the scope amendment
  and the starter's XPPython3 exception; no exact patch or Python 3.14 application
  runtime is imposed.
- Existing `src`, tools, project skills, architecture, plans, evidence and data
  layout remain. No folders are added merely to mimic the starter diagram.
- BACKLOG remains the only delivery-state authority. Backplane stays expected,
  deferred, disabled, and outside issue operations.
- Existing quality cadence, numeric limits, CI and release checks remain unchanged
  in stage one. Stage two will separately reconcile their invocation policy.
- Git sync, tags, publication and releases remain separately authorized. Local
  implementation commits and the eventual finishing choice do not grant a push.
- The broader weak-test audit remains unresolved. Correct only affected layout
  and installation snapshots in this stage, preserving real policy controls.

## Implementation surfaces and verification

| Surface | Responsibility and acceptance |
| --- | --- |
| Shared starter bundle and both native catalogs; FDAU `.codex/config.toml` and `.skills-first/bundle.lock.json` | Shared source selection; exact SHA agreement; disabled Backplane; preservation of unrelated entries |
| `AGENTS.md`, `AGENTS.skills-first.md`, `docs/agents/skills-first.md` | Current source authority, installation/fresh-session procedure, routing and rollback |
| `docs/architecture/gz_skills_plugin_only_specification.md` | Amend current ID/marketplace contract without rewriting dated evidence |
| Project instructions and skill discovery roots | Direct routing; no starter-owned skill copies, duplicate upstream discovery or retired entry expectations |
| `tests/test_project_skills.py` and focused metadata tests | Reject mismatched pins, duplicate active sources and accidental Backplane enablement using realistic altered fixtures; allow legitimate reviewed version changes |
| `pyproject.toml`, `tools/release.py`, artifact tests | Exclude new governance paths from distributions and reject synthetic archive leakage; preserve installed runtime inventory |
| Stage-one evidence | Exact sources, host version, native registration/install results, fresh-session entry identities, review findings and verification outcomes |

Use the existing starter helper for configuration preview and status, existing
project fixture tests for governing rules, and read-only native manager listings
for host inventory. Record configuration/install/discovery separately as
PASS/FAIL/UNKNOWN. No new project checker or duplicate lifecycle is introduced.
Actual native discovery is operator-observed and cannot be certified by a file
scan. Never print unrelated credentials or user configuration in receipts.

Run focused unittest, Ruff and ty during implementation. Packaging/governance
changes require one stable-candidate complete offline hygiene gate under the
currently approved cadence and a fresh Python 3.12 external installed-wheel
smoke. Add no new runtime dependencies. Preserve failed artifacts. After host
acceptance, independent review and repository verification, the first stage may
be reported complete; Python engineering parity remains pending stage two.

## Next-stage boundary

The separate engineering design will bind routine Ruff check/format, ty, unittest
and pre-commit; move deeper analysis outside hooks/CI; replace Xenon/Radon and
decide Wily's retirement; establish project-pinned on-demand complexity, mutation,
dependency and import-boundary tools; and add branch coverage measurement. It
must preserve existing numeric limits, provide comparable legacy measurements,
prove compatibility on Python 3.12, and avoid broad application refactors. It
cannot inherit a pass from this source-installation migration.

## Acceptance criteria

These sections assign this maintenance amendment to its owning tooling surfaces;
they do not replace the completed BACKLOG gate statements or reopen the children.

### T2.1 — Project repository-hygiene adapter and fresh artifact verification

- The selected lock, catalog, and project enablement agree on all immutable
  sources, with no duplicate active discovery and Backplane disabled.
- Project routing preserves existing operational and domain authorities; fresh
  host acceptance records actual discovery separately from configuration checks.
- Synthetic archive leakage checks and a fresh artifact pair demonstrate that
  the new governance files do not ship with the runtime.
- Negative configuration fixtures reject mismatched pins and duplicate sources,
  and allow a legitimate reviewed revision without a filename inventory snapshot.

### T2.2 — Governed dependency and toolchain refresh

- The provenance record inventories the starter and every selected component;
  native managers retain cache ownership and updates remain explicit.
- The reviewed published shared starter commit selects SP v7.0.0 and gz-skills
  v0.7.0; FDAU records its exact SHA and unreleased template version accurately.
- Installation and recovery preserve sources used by other projects; fresh
  acceptance and unresolved host limitations are reported honestly.
- Application Python support, runtime dependencies, release authority, and the
  separate engineering-policy stage remain unchanged by this migration.

## Sources and design review

- [Starter adoption](https://github.com/tvproductions/gz-skills-first-starter/blob/88928b2c6c663e37f739c80376dae42b5d8e5b4e/docs/adoption.md)
- [Starter migration contract](https://github.com/tvproductions/gz-skills-first-starter/blob/88928b2c6c663e37f739c80376dae42b5d8e5b4e/docs/migration-0.3.md)
- [Starter backport guidance](https://github.com/tvproductions/gz-skills-first-starter/blob/88928b2c6c663e37f739c80376dae42b5d8e5b4e/docs/backport.md)
- [Python binding](https://github.com/tvproductions/gz-skills-first-starter/blob/88928b2c6c663e37f739c80376dae42b5d8e5b4e/docs/engineering/python.md)
- [gz-skills 0.8.0 changes](https://github.com/tvproductions/gz-skills/blob/75bcd11ee9371ecff1a7b3432d2af29d4bdbb788/CHANGELOG.md)
- [SP v7.0.0](https://github.com/obra/superpowers/releases/tag/v7.0.0)
- [Codex marketplace and project enablement](https://developers.openai.com/plugins/build/plugins)

Self-review: the first stage is independently verifiable; no source/gate change
has been implemented or marked approved by this draft. Shared source selection
and the exclusion of starter publication are explicit;
fresh-session discovery is an acceptance gate. The FDAU/SP-BP requirements
exception is explicit. Stage-two tools and cadence are excluded from stage-one
implementation. This draft requires written-spec review before the
implementation plan is created.

Draft verification exposed two pre-existing frozen active-spec inventories in
`GovernanceArtifactTests.test_active_design_epic_assignments_match_roadmap_contract`
and `test_active_artifact_assignments_match_current_roadmap_children`. The strict
backlog consumer audit accepted this draft, but those filename snapshots rejected
its presence. Their redundant snapshot methods were removed during the requested
Git save-point correction. Existing adherence/lifecycle fixtures retain positive
and negative controls for known/unique/ordered children, epic assignments,
cross-epic declarations, plan ownership, required approvals and completion
evidence. The broader weak-test audit remains unresolved. This correction does
not implement native adoption or approve this specification.

October 18 reassessment verification: the strict backlog audit reports no
findings after the revision; 42 focused governance/documentation unittest tests,
strict MkDocs build and `git diff --check` pass. The starter's bundle/both-catalog
validation passes on its existing Python 3.14.8 interpreter. Temporary-directory
access initially prevented two fixture tests in the sandbox; the same focused
suite passed with temporary-directory access. Native installation, candidate
configuration and fresh-session discovery remain pending. No approval, product
child transition, engineering-policy implementation or publication is implied.
