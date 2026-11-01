---
name: update-gz-template
description: Check or update a project's adopted gz-skills-first-starter template, explain released policy changes, and reconcile migration guidance. Use for starter-version reviews and template upgrades, rather than general package or plugin updates.
---

# Update the GZ template

Help an existing adopter consume released template policy without replacing its
product. The canonical repository is
`https://github.com/tvproductions/gz-skills-first-starter`. This is a narrow guide
to its maintained adoption instructions, not another dependency updater.

## Establish the request and current adoption

Read the target project's AGENTS and existing authorities. Confirm its root and
dirty state; preserve unrelated work. Read `.skills-first/bundle.lock.json` for
the starter repository, version/full SHA and independent component selections.
Read `.gz-skills/settings.json` for the explicit lite/heavy choice. Absent or
legacy provenance stays unknown; do not infer it from today's version label.
Read the lock's selected native `host`; legacy records without it use Codex.
Use that host's repository-owned settings. For activation-only repair, follow
the reviewed starter's `localize --host` procedure; do not rewrite adoption
provenance or uninstall existing global copies. Installation, version updates
and enablement MUST remain separate. Project commands MUST preserve local scope.

A request to check or explain updates authorizes review only. Do not sync,
resolve, install or modify the adopter in review mode. A request to upgrade
authorizes the scoped template reconciliation and necessary verification; use
that authorization without asking again for routine migration steps. Keep
runtime/tool/plugin refreshes separate unless required by the reviewed target
policy or included in the user's request. With no adoption record, identify
first adoption and follow the starter's greenfield/brownfield entry instead of
pretending this is an upgrade. A gzkit project retains its separate ecosystem.

## Find the released target and its instructions

Query the canonical repository's live stable releases with direct `gh` commands.
Use direct `git` commands for repository operations. Do not wrap routine CLI
calls in Python; substantive Python processing must use the prescribed locked,
uv-managed environment. For example:

```bash
gh api repos/tvproductions/gz-skills-first-starter/releases/latest --jq '{tag_name,html_url,published_at}'
```

Respect an explicitly requested published target. A failed query is UNKNOWN,
not proof of no updates. Distinguish a release from newer main; a version string
alone proves neither source identity nor publication. Use a separate clean
checkout of the selected tag, resolve `TAG^{commit}` to its full SHA, and compare
with HEAD and the target manifest before applying. Never use the adopter's own
HEAD as starter provenance.

Read the selected release notes, intervening changelogs, `docs/versioning.md`,
`docs/baseline-policy.md` and `docs/adoption-workflow.md` at that exact target.
Follow the current runbook linked there; do not freeze a historical filename or
copy its whole procedure into this skill. Release 0.5.0 links
`docs/adoption-0.5.md`; future releases may link a successor. If a tool cannot
fetch the required instructions, report that gap rather than guess the migration.
When present at the target, `docs/updating.md` owns the canonical update and
older-adopter bootstrap method. Reconcile this project skill along with the
other managed content; adding it alone does not upgrade the adopted baseline.

Compare policy changes as well as pins. Enforce the target's latest-tooling
requirement: an old allowed tool family is not proof of currency. Required stale
or unknown freshness blocks strict acceptance; record any explicit owned
compatibility exception as conditional/noncurrent. The adopter retains this
responsibility when composing an upstream maintenance skill. Explain what applies to this product,
what needs reconciliation and what is deferred. If `gzs-update-dependencies`
is actually discovered, compose its template-inventory/review or scoped-update
mode under project policy. Its absence does not prevent reading the release and
following the published runbook; do not claim an undiscovered skill ran.

## Reconcile an authorized upgrade

Follow the target's brownfield-upgrade path. Capture rollback; compare the
original starter-managed content, current project edits and target candidates.
Generate candidates in a disposable directory using the clean target checkout.
Review the actual diff before changing product files. The helper intentionally
refuses different existing records; no force-overwrite or delete-and-reconfigure
shortcut is supplied.

Reconcile the instructions fragment, project policy references, starter
version/full SHA and managed host tables together. Preserve application
dependencies/settings, public behavior, explicit lane and local guidance.
Do not overwrite existing AGENTS with a generated example or hand-edit uv.lock.
Leave native caches to their manager; a template change does not automatically
authorize plugin activation. Backplane remains subject to its readiness rule.

Execute the target's applicable migration, analysis and artifact checks. Keep
lane, configuration, Python acceptance and native discovery as separate results.
Missing/null lane, required failed/unknown/stale evidence or accepted exceptions
cannot become an unqualified strict-conformance claim. Mark unfinished work as
migration pending. Do not alter the product version or manufacture a major PRD
merely because the independent template version changed.

## Report

Give the checked date; old and target starter versions/full SHAs; release link;
policy delta; adopt/defer decision; changed files; observed checks and remaining
migration/readiness gaps; and rollback reference. A review must clearly state
that no update was applied. An applied upgrade must distinguish updated
configuration from completed conformance. Never call the whole stack current
based only on the template. Do not publish releases or notify other adopters
unless the user separately requests those actions.
