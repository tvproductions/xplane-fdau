# Task 3 real-repository reconciliation

Command:

```powershell
uv run python -c "from pathlib import Path; import sys; sys.path.insert(0, str(Path('.codex/skills/backlog-status/scripts').resolve())); from backlog.audit import load_audit; from backlog.rules import structural_findings; from backlog.adherence import adherence_findings; loaded=load_audit(Path('.')); print('load',len(loaded.findings),'structural',len(structural_findings(loaded)),'adherence',len(adherence_findings(loaded))); [print(f'{f.code}|{f.path}:{f.line}|{f.node}|{f.gate}') for f in adherence_findings(loaded)]"
```

Initial result before assigning historical-plan admission to Task 4: load 0,
structural 0, adherence 15. The three `artifact.plan.governing` findings for
the linked D1.1-D1.3 historical plans were Task 3 false positives. The approved
supplement assigns their frozen admission to Task 4, while Task 3 continues to
validate their historical metadata and dispositions.

After that scope correction, Task 3 initially reported 12 potential
governing-artifact mismatches. Inspection showed that D1.1 and D1.3 use the
approved generic reference form: each managed acceptance subsection refers to
the exact four numbered acceptance gates in its unique earlier same-child
level-two section. Resolving that form from the retained source lines removed
those two extraction false positives. Task 3 now reports the following 10
genuine governing-artifact mismatches. No authority document was changed.

## Historical dispositions

- `artifact.historical.disposition` |
  `docs/superpowers/plans/2026-08-16-xplane-fdau-architecture-propagation.md:5`
  | node none | gate none
- `artifact.historical.disposition` |
  `docs/superpowers/plans/2026-08-22-q4xpcc-contract-handoff-readiness-authority.md:5`
  | node none | gate none
- `artifact.historical.disposition` |
  `docs/superpowers/plans/2026-09-05-gz-skills-adoption.md:5` | node none |
  gate none
- `artifact.historical.disposition` |
  `docs/superpowers/specs/2026-09-05-gz-skills-adoption-design.md:5` | node
  none | gate none

Each disposition lacks a known milestone/local-child identity and an existing
replacement-artifact path under the approved adherence rule.

## Acceptance-gate drift

### C2.4

Finding: `artifact.gate-drift` |
`docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md:1872`
| node `C2.4` | gate 3.

Backlog:

1. Binding catalog identity, ordering, uniqueness, schema, and hashes pass.
2. Missing or mismatched measurement references fail.
3. Direct bindings enforce unit/representation/shape/applicability parity.
4. Transformed bindings validate declarations without executing or claiming algorithm conformance.

Design:

1. Binding catalog identity, ordering, uniqueness, schema, and hashes pass.
2. Missing or mismatched measurement references fail.
3. Direct bindings enforce unit/representation/shape/payload/applicability parity.
4. Failure dispositions incompatible with measurement quality or validity authorization fail during cross-catalog validation.
5. Transformed bindings validate declarations without executing or claiming algorithm conformance.

### C3.3

Finding: `artifact.gate-drift` |
`docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md:1896`
| node `C3.3` | gate 1.

Backlog:

1. Every sample reaches one complete observation or immutable record reference.
2. Ordered derivation-parent references remain intact and cycle-free within the supplied validation closure.
3. Catalog-resolved sample representation, unit, range, binding, status, and quality validation passes.
4. Missing, mismatched, or stale lineage fails with exact context.

Design:

1. Every sample reaches every consumed observation through a complete record or immutable record reference.
2. Ordered derivation algorithm inputs remain intact and cycle-free within the supplied validation closure.
3. Catalog-resolved sample representation, unit, payload, range, binding, status, and quality validation passes.
4. Missing, mismatched, or stale lineage fails with exact context.

### C4.4

Finding: `artifact.gate-drift` |
`docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md:1954`
| node `C4.4` | gate 5.

Backlog gate 5: Version `0.1.0` remains unreleased and no release tag or
package publication occurs; separately authorized routine Git sync does not
satisfy or violate this release gate.

Design gate 5: Version `0.1.0` remains unreleased and no push/tag/publication
occurs.

### T2.2

Finding: `artifact.gate-drift` |
`docs/superpowers/specs/2026-08-15-xplane-fdau-local-workflow-skills-design.md:360`
| node `T2.2` | gate 1.

Backlog:

1. Read-only human and JSON status discover the newest stable `uv`, Python 3.12-3.14 policy, lock freshness, outdated releases, yanks, vulnerabilities, and constraints from official sources.
2. Apply pins the exact verified stable `uv`, aligns package metadata to `>=3.12,<3.15`, retains compatible ordinary development constraints, refreshes the complete lock, and fails closed on dirty, stale, incompatible, or unexplained security state.
3. Targeted `unittest`, full repo hygiene, Python 3.12-3.14 source and installed-wheel verification, and wheel/sdist inventory pass.
4. Superpowers comparison/update, X-Plane deployment, staging, commit, push, tag, publication, and release behavior is absent.

Design:

1. Read-only human and JSON status discover the newest stable `uv`, supported Python matrix, locked graph, outdated releases, yanks, vulnerabilities, and constraints from official sources without mutation.
2. Apply pins the exact verified stable `uv`, aligns package metadata to `>=3.12,<3.15`, retains compatible ordinary development constraints, refreshes the complete lock, and fails closed on stale scope, incompatible resolution, or unexplained security findings.
3. Targeted `unittest`, full repo hygiene, Python 3.12-3.14 source and installed-wheel verification, and exact wheel/sdist inventory all pass.
4. Superpowers, X-Plane deployment, staging, commit, push, tag, publication, and release behavior is absent from the skill and implementation.

### T3.1

Finding: `artifact.gate-drift` |
`docs/superpowers/specs/2026-08-15-xplane-fdau-local-workflow-skills-design.md:376`
| node `T3.1` | gate 2.

Backlog:

1. Dry-run and JSON reports deterministically expose branch, remote, scope, ahead/behind/divergence, actions, warnings, blockers, and expected state.
2. Apply revalidates pinned state, performs reviewed auto-add, full hygiene, intentional commit, fast-forward pull or rebase of unpublished commits, and final verification without rewriting published or merge-head history.
3. Detached, conflicting, stale, unexpected, missing-remote, failed-fetch, failed-hygiene, merge-head, ambiguous-divergence, push-failure, and alignment-failure states fail closed without unsafe continuation.
4. An explicitly authorized ordinary push is followed by a fresh fetch and proof that local and remote are `ahead=0`, `behind=0`; no tag, publication, release, force, destructive reset, or verification-bypass path exists.
5. Temporary-repository tests, current-repository dry-run, complete quality gates, and independent review pass without changing release authorization.

Design:

1. Dry-run and JSON reports deterministically expose branch, remote, scope, ahead/behind/divergence, actions, warnings, blockers, and expected state.
2. Apply revalidates pinned state, performs reviewed auto-add, full hygiene, intentional commit, fast-forward pull or rebase of unpublished commits, an explicitly authorized ordinary push, and a fresh final fetch/alignment check.
3. Detached, conflicting, stale, unexpected, missing-remote, failed-fetch, failed-hygiene, merge-head, published-history-rewrite, failed-push, and failed-alignment states fail closed without partial unsafe continuation.
4. An explicitly authorized ordinary push finishes only after proof that local and remote are `ahead=0`, `behind=0`; no tag, publication, release, force, destructive-reset, or verification-bypass path exists.
5. Temporary-repository tests, current-repository dry-run, complete quality gates, and independent review pass without changing release authorization.

### D1.2

Finding: `artifact.gate-drift` |
`docs/superpowers/specs/2026-08-23-xplane-fdau-acquisition-recording-projection-pinning-contracts-design.md:3972`
| node `D1.2` | gate 1.

Backlog:

1. one approved design fixes every A1/R1/P1 contract shape and policy needed by the four q4xpcc Phase 24A Slice 2 plans;
2. every family has an exact identity/version boundary, owned fields, invariants, references, error outcomes, and intended future schema/fixture path;
3. deployment, revision pinning, release-artifact hashes, delivered-file hashes, conformance, and no-divergent-subset proof are explicit without requiring a current release artifact; and
4. independent review finds no unresolved load-bearing ambiguity, the approved contract-only design is recorded as binding architecture input for future A1, R1, and P1 specifications, and those implementation children remain `queued` with zero delivery gates satisfied and no implementation, artifact, or release claim.

Design:

1. this one approved design fixes the A1/R1/P1 contract shapes and policies needed by all four q4xpcc Phase 24A Slice 2 plans, including acquisition, continuity, fan-out, recording, recovery, replay, native-FDR projection, deployment, and conformance planning surfaces;
2. every family has an exact identity/version boundary, fields, invariants, references, runtime outcomes, error boundary, delivery ownership boundary, and future schema/conformance path, with closed failure codes and deterministic validation/causal precedence;
3. installed-wheel and reproducibly bundled deployment, independently trusted expected version/revision/artifact/conformance pins, mode-specific metadata evidence, delivered-file hashes, conformance, and closed-world no-divergent-subset proof are explicit without requiring or fabricating a current release; and
4. independent review reports no unresolved load-bearing ambiguity; native FDR, ARINC, FDM/FOQA, q4xpcc, and external-client boundaries remain consistent with the approved scope amendment; the approved contract-only design is recorded as binding input for later A1/R1/P1 specifications; and every implementation, schema, fixture, artifact, adoption, release, push, tag, and publication gate remains unsatisfied without advancing any A1, R1, P1, S, or F1 child.
