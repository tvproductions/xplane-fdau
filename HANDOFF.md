# Project Handoff

## Start Here

This repository was created to extract the reusable X-Plane Flight Data
Recorder domain from the unreleased `xpwebapi` FDR feature. The user approved
the repository boundary, project identity, capture-neutral architecture,
Python 3.12 floor, and standard-library-only runtime contract.

The next action is **written-spec review**, not implementation. Read the full
design:

- `docs/superpowers/specs/2026-08-08-xplane-fdr-core-design.md`

Present it to the user for review and incorporate any requested changes. After
explicit approval, invoke the Superpowers `writing-plans` workflow. Repository
bootstrap and implementation belong in that plan.

Superpowers v6.2.0 is freshly vendored under `.codex/` from upstream commit
`3dcbd5c4b48e02263fbf4a3c01e3fe4f81d584d9`. Restart Codex in this repository
so its project-local skills are discovered. Do not copy the old project's
custom skills verbatim; establish equivalent project-specific quality,
hygiene, git-sync, documentation, and release capabilities for this package.

## Project Identity

- Repository: `https://github.com/tvproductions/xplane-fdr.git`
- Distribution: `xplane-fdr`
- Import package: `xplane_fdr`
- Python: 3.12 and newer
- Runtime dependencies: none

Description:

> A standard-library-only Python toolkit for reading, writing, recording,
> validating, and converting X-Plane Flight Data Recorder files, independent
> of how flight data is captured.

## Architectural Boundary

`xplane-fdr` owns FDR v3/v4 models and reading, deterministic v4 writing,
push-first recording sessions, profiles, adapter-neutral JSON configuration,
GeoJSON conversion, validation, and offline commands.

It does not own Web API connections, WebSockets, XPLM callbacks, XPPython3
plugin lifecycle, simulator orchestration, landing analysis, or consumer
business logic.

`xpwebapi` and XPPython3 projects such as q4xpcc are adapters and consumers.
They translate their observations into neutral `xplane_fdr` samples. The native
X-Plane FDR v4 artifact is the persistence and interchange boundary.

The recording API must be push-first so an XPPython3 flight-loop callback can
call `FDRRecordingSession.record(sample)` without adopting a blocking iterator,
thread, event loop, or network abstraction. Pull-source recording is an
optional convenience layered on the same session.

## Source Material

The existing implementation and detailed prior specifications remain in:

- Repository: `C:\Users\Jeff\source\repos\xp\xplane-webapi`
- Worktree: `C:\Users\Jeff\source\repos\xp\xplane-webapi\.worktrees\fdr-toolkit`
- Branch: `feature/fdr-toolkit`
- Branch head at handoff: `ca7d621`

Important inputs in that worktree:

- `docs/superpowers/specs/2026-08-07-fdr-toolkit-design.md`
- `docs/superpowers/specs/2026-08-08-fdr-recording-profiles-config-design.md`
- `xpwebapi/fdr/`
- FDR tests, fixtures, documentation, and artifact checks

Those specifications contain detailed accepted behavior. Their old assumption
that the reusable core belongs in `xpwebapi.fdr` is superseded by this design.
The existing configuration's Web API `connection` block must also be separated
from the neutral recording configuration.

## Required Sequence

1. Complete written-spec review in this repository.
2. Write the implementation plan.
3. Bootstrap this repository with the applicable Superpowers workflow and the
   quality structure used by `xplane-webapi`, adjusted for a dependency-free
   library.
4. Move and refactor the neutral implementation and tests here.
5. Verify and publish the initial `xplane-fdr` release.
6. Return to `xpwebapi`, depend on the released package, and retain only its Web
   API adapter and live recording integration.
7. Complete the planned `xpwebapi` minor release.

Do not duplicate the neutral implementation between repositories. Use
`unittest`; never introduce pytest. Preserve MIT attribution and do not copy
GPL implementation from `hotbso/xgs`.
