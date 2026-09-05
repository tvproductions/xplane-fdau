---
name: gzs-router
description: Orient a user to the GovZero portable skill catalog and recommend the smallest useful skill or sequence for their current goal.
compatibility: Works wherever the installed GovZero skills are discoverable by name.
metadata:
  govzero-version: "0.1.0"
  govzero-portability: "portable"
  govzero-origin: "gz-skills"
---

# GovZero Skill Router

Act as the curator for this catalog. Translate the user's goal into the smallest
useful skill or sequence, explain why it fits, and name the exact invocation.
This is a map, not an orchestrator: recommend other user-invoked skills but do
not silently start their workflows.

## Route

1. Identify the user's immediate outcome and whether they want action, an audit,
   maintenance, publication, or orientation.
2. Choose one primary skill from the catalog below. Add another only when it is
   a genuine next phase, not merely related.
3. State prerequisites, mutation or remote effects, and whether explicit user
   invocation is required.
4. Give the exact `$skill-name` invocation and a one-sentence starting prompt.
5. When no skill fits, say so. Recommend ordinary agent work rather than forcing
   a catalog match.

## Catalog

| Goal | Skill | Boundary |
| --- | --- | --- |
| Reduce persistent agent-instruction weight | `gzs-agent-context-diet` | Preserves binding rules while pruning or disclosing context. |
| Review Python for operating-system assumptions | `gzs-cross-platform-python` | Applies to Python portability, not general cross-platform product design. |
| Commit and publish a guarded save point | `gzs-git-sync` | Explicit-only; commits and pushes after repository gates pass. |
| Compare delivered behavior with its owning intent | `gzs-intent-audit` | Diagnoses and routes gaps; does not implement corrections unless separately requested. |
| Check intent, scope, and plan alignment | `gzs-plan-audit` | Runs before implementation and audits existing artifacts. |
| Run the repository's complete verification | `gzs-quality-gate` | Uses project-owned commands and reports unavailable dimensions honestly. |
| Audit or repair repository hygiene | `gzs-repository-hygiene` | Begins read-only; cleanup requires authorization from the request or project workflow. |
| Preserve or resume engineering state | `gzs-session-handoff` | Explicit-only; creates or consumes a durable continuity artifact. |
| Survey and prioritize technical debt | `gzs-tech-debt-review` | Produces an evidenced report without fixing findings. |
| Refresh project dependencies and pinned tools | `gzs-update-dependencies` | Covers project-managed versions, not machine-wide or deployed infrastructure. |

## Common sequences

- Dependency maintenance: `gzs-update-dependencies` → `gzs-git-sync` when the
  verified update should be published.
- Pre-publication confidence: `gzs-quality-gate` → `gzs-git-sync` when no broader
  maintenance workflow already ran the complete gate.
- Plan integrity: `gzs-plan-audit` before implementation; `gzs-intent-audit` after
  delivery when fulfillment is uncertain.
- Repository maintenance: `gzs-repository-hygiene` → `gzs-quality-gate` when the
  hygiene workflow did not already include the full final gate.
- Session continuity: `gzs-session-handoff` at a stopping boundary; invoke it
  again to resume from the artifact.

Avoid redundant sequences. A skill that already requires the complete quality
gate does not need a second quality invocation unless the tree changed afterward.

## Output

Return the primary recommendation, optional sequence, rationale, prerequisites
or side effects, and exact invocation. Keep the answer short enough to function
as a menu rather than reproducing the selected skill's body.
