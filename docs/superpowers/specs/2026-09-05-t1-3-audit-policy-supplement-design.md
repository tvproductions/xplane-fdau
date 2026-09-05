# T1.3 Audit Policy Supplement

- **Governance:** active
- **Status:** approved
- **Date:** 2026-09-05
- **Decision owner:** Jeff / tvproductions
- **Roadmap epic:** `T1`
- **Roadmap children:** `T1.3`
- **Approval:** 2026-09-05 — Jeff / tvproductions

## Authority and scope

This is the approved supplement to
`docs/superpowers/specs/2026-08-09-xplane-fdau-backlog-status-skill-design.md`.
It incorporates that design's audit, model, report, lifecycle, and evidence
contracts and defines four precise clarifications for T1.3. Jeff approved the
revised supplement and plan on 2026-09-05 after independent review closed.
This is the focused governing specification for T1.3, with the parent design retained
as its incorporated authority. No other child's governing link changes.

BACKLOG remains the sole mutable delivery ledger. No current state advances
through this document, including D1.1-D1.3's already-recorded verified states.
The frozen migration identities below are admission criteria, not a second
status ledger. The remaining T1.3 acceptance criteria are unchanged.

## Historical plan reconciliation

The three D1 plans were preserved using the historical metadata family. They
have no active-plan Approval or Completion-evidence field. Existing review and
gate artifacts record the completed work; filling in missing historical
metadata would falsely imply that those fields existed during execution.

Approved decision: admit only the following frozen historical plan identities
as a migration case. SHA-256 is over the exact plan file bytes, without newline
normalization. Before implementation, verify these bytes also match the Git
index and HEAD; any mismatch is a blocking policy finding, not a new hash to
accept automatically.

| Child | Historical plan | SHA-256 |
| --- | --- | --- |
| `D1.1` | `docs/superpowers/plans/2026-08-23-d1-1-canonical-design-approval.md` | `c4869782b22736cf5372d93b21b330e85657bcc4c832f041f088bd79caa4780e` |
| `D1.2` | `docs/superpowers/plans/2026-08-23-d1-2-acquisition-recording-projection-pinning-contracts.md` | `9b3c3a2c984f4536730c72c3479577b86707b03e50fca8d3e13f5a50ed80343f` |
| `D1.3` | `docs/superpowers/plans/2026-09-05-d1-3-q4xpcc-handoff.md` | `ec5a0c559ae3d49d412446c538eeb7b4fc34069f9030e973473e8f7e6d08c3b0` |

Admission requires all of the following, with no fallback:

1. The child's effective state is verified (current verified, or blocked/deferred
   with Resume verified), the linked historical plan matches its exact
   row, and that plan has completed status and a disposition naming the child.
2. The current governing specification is approved and covers the child.
3. Dependencies, gate statements, and all other structural rules pass.
4. The current Review link resolves to accepted, child-level review evidence;
   every gate resolves to eligible evidence. Review and all gate evidence
   must match index and HEAD bytes.
5. The historical plan itself matches its pinned digest, index, and HEAD.

Only the active-plan approval/completion-field requirement is replaced by this
admission rule. No completion record or approval date is fabricated. Historical
plans are still reported as historical in version-1 JSON. A failed admission
produces `lifecycle.historical-plan`; it never silently downgrades the child.

Suspension still requires valid Resume/Reason metadata; admission does not
remove the suspension or claim the child is currently available for execution.
Unlisted plans receive no exemption, including a new plan relabeled historical
or a copied D1 plan attached to another child. Reopening work under a historical
plan requires a newly approved active plan; the migration rule does not justify
in-progress, implemented, or reviewed state. Changing the admission table
requires reviewed policy amendment. Implement the table as parsed policy data,
not child-ID conditionals in generic rule functions.

## Specification links by lifecycle

Evaluate blocked/deferred children at their Resume state for evidence
requirements, while separately enforcing suspension metadata.

| Effective state | Link requirement |
| --- | --- |
| queued | Spec may be absent or a contained, existing regular Markdown reference. It supplies context only. |
| designing | Spec must be an active draft design covering the child. |
| specified and later | Spec must be an approved or implemented active design covering the child; normal plan/evidence requirements also apply. |

Queued architectural references do not require active governance metadata or
per-child acceptance subsections. Their existing backlog gates remain open;
checked gates require a governing design and are rejected in the contextual
reference case. Invalid paths and missing referenced files are still errors.
This permits the current F1 architecture references without asserting that F1
is specified. It applies by lifecycle, not by an F1-specific exemption.

Design acceptance matching applies to a linked governing design, not to a
queued contextual reference. Independently discovered active designs always
receive their own metadata checks. A contextual reference cannot authorize
designing, specified, planned, or execution state.

## Deterministic evidence-kind policy

The engine checks evidence eligibility, not the truth of arbitrary prose.
These are the complete slot rules for this version of T1.3:

| Referring slot | Eligible Kind | Required Result | Gate field |
| --- | --- | --- | --- |
| Local-child acceptance gate | verification, artifact | passed | exact positive ordinal |
| Child Review field | review | accepted | absent (`—`) |
| Active-plan Completion evidence | verification, artifact | passed | absent (`—`) |
| Release-dashboard evidence | verification, artifact | passed | absent (`—`), Child equals release-gate ID |

Approval evidence remains a valid evidence artifact family, with accepted
result, but cannot replace any of these slot requirements. A gate concerned
with review or approval uses a verification record describing the reviewed
decision; direct review and approval records are not substitutes for that
gate's verification record. This matches all twenty currently recorded
local-child gate artifacts, whose Kind is verification.

This fixed slot matrix supplies `kinds` to evidence validation. No inference
from gate wording and no mutable per-child override is permitted. A future
requirement for direct approval/review gate evidence needs a reviewed policy
amendment. Use `evidence.kind` or `evidence.result` on mismatch, in addition to
existing path, identity, ordinal, tracking, and byte-eligibility findings.

Release-dashboard evidence uses the existing Child metadata key with the
release-gate identity because it refers to a gate node rather than a local
child. This does not add that node to the local-child inventory. Satisfied
release gates require HEAD-backed evidence and verified prerequisites but
still grant no release or publication authority.

## Release prohibition as an audited contract

The repository currently owns a release-policy statement under BACKLOG's
Current position and a separate approval checkbox under ROADMAP's Version
0.1.0 release gates. T1.3 recognizes the following managed forms after joining
wrapped continuation lines and folding Markdown whitespace:

```text
- Release, tag, and package publication: prohibited pending their separate gates and authorization.
- [ ] A separate release review authorizes publication.
```

There must be exactly one statement beginning `- Release, tag, and package
publication:` in Current position and it must equal the first form. The
roadmap section must contain exactly one task item with the second form's
statement and its checkbox must be open. Missing, duplicate, modified, or
checked forms produce `release.authorization` with the offending file and
line, or the containing section line when missing. Missing sections are parse
errors. Local child released state also produces `release.prohibited-state`.

These managed structures are the recognized authorization surface; unrelated
prose cannot grant authorization. The engine does not claim to interpret or
detect every contradictory sentence elsewhere in the repository. Future
authorized release requires a reviewed change to this policy, not just a
checkbox edit. Ordinary Git-sync policy is a separate surface and is not
rejected merely because it permits an explicitly requested ordinary push.

Test each malformed form through both audit and status --json, including a
case where all child prerequisites are verified and G1 is satisfied: the
publication guard must still block. Negative tests must modify temporary
copies; they never change the working repository's policy.

## Implementation and verification boundaries

The focused plan is
`docs/superpowers/plans/2026-09-05-t1-3-structural-audit.md`. It must add a
policy parser and frozen typed migration entries before lifecycle/evidence
rules consume them. Policy loading requires approved or implemented status,
valid approval metadata, and index/HEAD bytes matching the policy document;
unapproved or unavailable policy produces `policy.unapproved` or
`policy.unavailable`. Commit the approved policy before implementation begins.

The T1.3 implementation knows this repository-owned policy document's path.
Its frozen historical table is parsed with the exact three-column header above;
duplicate children/paths, invalid paths, and non-lowercase 64-digit hashes are
errors. Generic rule modules consume typed policy values. No new report keys,
runtime package files, mutable ledger, external integration, or release
permission is introduced.

Required regression controls include all three current historical-plan cases,
tampered/unlisted plans, missing review/gate evidence, all six queued F1
references, blocked/deferred queued references, every slot/kind/result
combination, malformed release statements, and unavailable/unapproved policy.

## Acceptance criteria

### T1.3 — Structural audit and spec/plan adherence

- Identity, kind, dependency, cycle, lifecycle, gate-count, and link rules fail
  closed with stable finding codes.
- Multi-child governing designs, single-child plans, and historical artifacts
  follow the exact metadata contract.
- Lifecycle prerequisites and eligible evidence are validated without treating
  presence as proof.
- Audit reports all independent findings with file, line, node, and exact
  context and returns a blocking result when required.
