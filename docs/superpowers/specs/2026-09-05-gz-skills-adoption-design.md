# Canonical gz-skills adoption design

- **Governance:** historical
- **Status:** completed
- **Disposition:** Jeff / tvproductions approved and completed the 2026-09-05 cross-cutting canonical gz-skills adoption without a roadmap-child completion, Git push, tag, publication, or release claim.

## Approved intent

Jeff requested adoption of all skills from https://github.com/tvproductions/gz-skills,
explicitly sunset the localized version, and named gz-skills canonical. This
approves replacing the local-only Git-sync policy, not executing a push now.

## Integration

Install all eleven unmodified upstream skills under .agents/skills/ using the
upstream Python installer and commit its gz-skills.lock.json. Pin full revision
e925081362eec2517ab429517e250ecca6877cdc, verified as upstream HEAD and clean
local checkout on 2026-09-05. No global installation, duplicate managed plugin,
upstream mutation, or runtime dependency is introduced. Use the supported
vendored-snapshot contract for repository-owned, reviewable provenance.
Preserve raw installed bytes through Git attributes so lock hashes survive
Windows checkouts. All bundled metadata and references travel with each skill.

Remove .codex/skills/git-sync/SKILL.md, with no local alias. Retain project
quality/hygiene helpers and domain-specific documentation/release guidance as
adapters subordinate to the portable invariants; they supply exact commands and
project constraints, not competing workflow definitions. Existing Superpowers
discovery remains external and ignored. The eleven portable skills are available
for their documented triggers; installing them does not execute every workflow.

## Authority reconciliation

AGENTS.md routes to the canonical catalog and project command adapters. Explicit
git sync authorizes ordinary commit/reconciliation/push and requires fresh remote
verification at ahead=0, behind=0; an ahead branch is not synchronized. Failed
gates, fetches, conflicts, unknown scope, or unsafe history changes block sync.
No automatic push follows installation, ordinary coding, local merge, or handoff.
No force push, destructive reset, hook bypass, or unrelated cleanup is authorized.

Separate routine Git publication from release: tags, package publication and
releases remain prohibited until the reviewed canonical vertical slice and
separate release authorization. Amend current ROADMAP/BACKLOG/HANDOFF and the
active local-workflow design accordingly. T2.1/T2.2/T3.1 remain unimplemented
specified children at their existing gate counts; their future helpers adapt
portable workflows rather than create competing local skills. T1.3 remains
selected. Do not rewrite provenance-locked architecture, accepted D1 designs,
historical completed plans or committed D1 gate/review evidence.

## Verification

Reproduce baseline agent refusal first (done), update installation-integrity
unittest contracts before installation, and prove RED then GREEN. Test all eleven
installed trees against their lock hashes, complete catalog, source pin, safe
relative paths and discovery. Do not add prose-presence tests. Run a fresh
agent behavior scenario against the installed canonical instructions: explicit
sync includes push and final remote proof; installation alone never pushes;
failed quality blocks; no safety bypass.

Run full repository quality, strict docs, pre-commit, upstream installer status,
and a fresh wheel/sdist boundary check. Independent review must find no blocking
issue. Finish with established local integration, merged verification and
temporary worktree/branch cleanup. No push/tag/publication/release in this task.

## Completion verification

Implementation reproduced the missing-installation RED before running the
pinned upstream installer, then passed the five focused project-skill tests and
the combined 80-test project-skill/governance/status set. The pinned upstream
status command reported all eleven installations current. Independent
consuming-agent scenarios in
`.superpowers/sdd/2026-09-05-gz-skills-adoption/behavior-review.md` proved the
explicit-sync, adoption-only, failed-gate, and future-adapter boundaries. The
same review records that all 23 installed files match their raw upstream Git
blobs at the pinned revision and that Git attributes disable text conversion.

The final offline/frozen project quality gate passed 281 `unittest` tests with
94% statement coverage and all configured static, security, documentation, dead
code, and complexity checks. Strict MkDocs and all four pre-commit hooks passed.
A fresh wheel/sdist pair passed `tools/release.py check-dist`; explicit member
inspection found zero `.agents/`, `.codex/`, or `gz-skills.lock.json` entries.
The preserved artifacts and exact hashes are recorded in the ignored task
report. This completion does not claim the Python 3.12-3.14 installed matrix,
release readiness, local integration, push, tag, publication, or release.

Post-commit verification exposed the generated lock to the quality tool's
tracked-path secret scan for the first time. Its one public upstream revision
and eleven independently verified public tree hashes are individually recorded
in `.secrets.baseline` as `is_secret: false`. No file exclusion, detector
change, lock edit, or other baseline entry changed; focused and full security
verification was rerun on the tracked candidate.
