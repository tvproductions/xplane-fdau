# Coordinated toolchain and starter refresh

- **Governance:** active
- **Status:** approved
- **Date:** 2026-11-01
- **Decision owner:** Jeff / tvproductions
- **Roadmap epic:** `T2`
- **Roadmap children:** `T2.1`, `T2.2`
- **Approval:** 2026-11-01 — Jeff explicitly requested application and verification of the reviewed coordinated refresh in chat.

## Scope and authority

Apply the November 1 freshness review to the existing Python 3.12 toolchain and
skills-first adoption. This is crosscutting maintenance, not a new product child
or completion of the outstanding STRICT onboarding acceptance. Preserve runtime
behavior, empty runtime dependencies, unittest, four routine hooks, FDAU-owned
roadmap/backlog/release gates, and the selected heavy profile. Backplane stays
disabled. No shared user settings, unrelated worktree, release, push or local
integration is authorized by this refresh.

## Reviewed targets

- Retain Python 3.12.16 and `requires-python = ">=3.12,<3.13"`.
- Adopt uv/uv_build 0.13.6, Ruff 0.17.3, ty 0.0.95 and setup-uv 10.3.3.
- Adopt starter 0.8.0 at `e0b752fcc13b87ec7868fe0b0f85badefdb6bf52`.
- Adopt its Superpowers 7.0.1 at `2ce8aa15d05bd57213e6f746f953aafb7ded7a8b`
  and gz-skills 0.8.3 at `d6acc26e28ca1c4f43e5bb46d8973021d7d006c3`.
- Retain disabled Backplane at `d0eeee829c491da02351e793544aa16ad96461bf`.
- Resolve transitive updates with uv; retain justified parent constraints.
  Review major transitive releases against their actual consumers and checks.

Reconcile old/current/target managed content using the released starter helper
in a separate clean checkout. Preserve local guidance and operational skills.
Generate target candidates before changing adopter files. Use only project-owned
Codex configuration and native scope-preserving resolution; never edit caches
or use `plugin add` to widen user activation. Record configured, installed and
fresh-session discovered sources separately. If native resolution cannot preserve
scope, retain the reviewable migration and name the remaining native limitation.

## Verification and acceptance

Use the existing guarded dependency-refresh adapter after reviewed bootstrap of
the resolver/backend and manifest pins. Status and digest-protected apply must
agree on dirty scope. Do not hand-edit uv.lock. Run focused unittest/static checks,
complete offline hygiene, exact source-independent artifacts, supported Python
3.12 source and external installed-wheel smoke, advisory status, and independent
whole-change review. Repair update-caused failures without weakening safeguards.
Retain original failures in evidence. Unknown cognitive analysis and existing
Lizard acceptance limitations remain explicit; no STRICT or host-certification
claim follows from routine checks. Record exact revisions, diffs and rollback
HEAD `7438a125e8a2bd5bc2453fe5f73d87b407585c69`.

## Acceptance criteria

These criteria qualify this crosscutting maintenance change, without reopening
or replacing the completed T2 delivery records.

### T2.1 — Project repository-hygiene adapter and fresh artifact verification

- Complete offline hygiene passes with unchanged quality rules and hooks.
- Fresh wheel/sdist metadata and inventory pass; a wheel rebuilt from the sdist
  matches the original wheel, with supported-Python installed smoke evidence.
- The released managed files, actual native sources and fresh-session discovery
  agree, with user settings preserved and any upstream helper limitation explicit.

### T2.2 — Governed dependency and toolchain refresh

- Guarded status/apply scope agrees; the final lock check has no churn.
- Selected Python, resolver/backend, tools and CI pins agree with reviewed targets.
- Every retained outdated dependency has an evidenced parent constraint; the
  final advisory result and major-transitive consumer checks are recorded.
- Independent review closes material findings; existing STRICT gaps remain open.
