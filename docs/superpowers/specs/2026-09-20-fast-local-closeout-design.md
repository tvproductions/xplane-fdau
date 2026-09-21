# Fast local closeout and merge verification design

- **Governance:** historical
- **Status:** completed
- **Disposition:** Jeff approved this crosscutting local-workflow revision on 2026-09-20 after B1.1 integration exposed repeated five-minute full gates. It amends the completed local quality cadence design without changing roadmap child state, CI, quality thresholds, or release authority.

## Context and decision

The earlier local quality-cadence correction removed the full suite from intermediate commits and selected one complete gate at stable closeout. B1.1 still needed repeated full gates after late failures and another full gate after local fast-forward integration. The green coverage-backed suites took 314.236 seconds in the feature worktree and 292.904 seconds on main. A stale live backlog assertion and a secrets-baseline rewrite surfaced after entering the expensive gate. The main checkout also retained ignored bytecode under the old package root, which a focused import-layout test would have caught before another full run.

Keep isolated worktrees and one complete offline quality or hygiene gate on the stable branch candidate. Move fast, state-sensitive checks ahead of coverage. For an exact local fast-forward to main, run focused merged-checkout verification in place of a second complete suite. The explicit user approval for this design overrides only the upstream Superpowers finishing step that otherwise reruns the full suite after local merge. All other finishing safeguards remain in force.

## Branch closeout

- During each implementation task, run affected unittest cases, Ruff, and ty as required by the existing cadence. Intermediate commits retain the fast staged-file hook.
- Before coverage in the complete quality gate, run Ruff, ty, Bandit, detect-secrets, Interrogate, Vulture, and Xenon. Run a small live-state preflight containing the current-repository backlog status test and the repository-root import-layout test. These focused tests are repeated inside the complete suite but are cheap relative to a failed full run.
- Full offline hygiene runs the offline lock check and strict backlog audit first, then strict MkDocs and all-files pre-commit before the complete quality gate. A hook that updates the secrets baseline stops the gate before coverage. After the complete gate passes, hygiene continues to build and validate one exact external wheel/sdist pair, preserving its current cleanup safeguards.
- The branch closeout record identifies the full-gate candidate and any later documentation or governance-only edits checked with their focused gates. Any later source, build, package, lock, or artifact-validator edit requires a new complete gate on the changed candidate.

## Local fast-forward integration

After the user selects local integration, record the reviewed branch HEAD, the last green full-gate commit, and its tracked passing receipt. Ensure both checkouts are clean, and fast-forward main without a remote pull. The merged HEAD must equal the recorded branch commit. The project-owned command accepts these three exact inputs: expected branch HEAD, full-gate commit, and receipt path. It checks that the receipt is a tracked passing verification artifact in HEAD, that the full-gate commit is an ancestor of HEAD, and that every intervening tracked edit is limited to Markdown under docs or .superpowers/sdd, BACKLOG.md, or HANDOFF.md. It then checks:

1. the exact expected main commit and clean tracked worktree;
2. offline frozen environment synchronization and lock consistency;
3. strict backlog audit and the live-state status and repository-root import tests;
4. a fresh offline wheel/sdist pair with strict metadata and exact release inventory validation; and
5. an installed-wheel smoke test from an external temporary environment.

The command reports the exact commit, Python version, test count, artifact hashes, and installed import path. It uses one safely owned temporary directory, removes it after success, and preserves it with its path on failure. It performs no remote, tag, publication, or release action.

A non-fast-forward merge, differing HEAD, failed branch closeout, missing or non-passing evidence, tracked change after the branch gate outside the exact allowed paths, or failed focused merge verification requires investigation and the complete gate on the resulting main candidate. The temporary worktree and branch remain until main verification passes; cleanup follows the existing Superpowers ownership and untracked-file rules.

## Surfaces and limits

- tools/quality.py and its unittest contracts: fail-fast ordering and the two focused live-state preflight tests.
- The repository hygiene adapter and its unittest contracts: documentation and all-files hook before coverage, preserving one full quality invocation and one exact artifact pair.
- A small project-owned merge-verification command with unittest contracts: exact commit, offline focused checks, external artifacts, safe cleanup, and fail-closed conditions.
- AGENTS.md, project quality and hygiene adapters, HANDOFF.md, and their guidance tests: state the branch and local-integration cadence and the narrow explicit exception to the upstream finishing instruction.

The complete suite, 40% coverage floor, security thresholds, standard-library-only runtime, supported Python versions, CI matrix, independent review, release-readiness checks, and remote Git-sync safeguards do not change. Version-sensitive changes and explicit release-readiness work retain their broader compatibility requirements. Pull requests and non-fast-forward merges continue to use their existing gates. This workflow is a crosscutting local-process amendment; it does not change B1.1 or C1.1 delivery evidence.

## Acceptance

- An all-files hook, strict docs, live-state mismatch, or secrets-baseline rewrite fails before the coverage suite starts.
- The complete branch quality gate still runs exactly once on a stable candidate and retains all current blocking checks.
- An exact fast-forward runs focused main verification without a second full unittest suite; a differing merged tree cannot use this shortcut.
- A stale flat-package cache on main is detected by focused verification before cleanup.
- Offline artifact and installed-import proofs remain external to the checkout, with safe success cleanup and failure preservation.
- No CI, release, runtime dependency, remote sync, tag, or publication behavior changes.
