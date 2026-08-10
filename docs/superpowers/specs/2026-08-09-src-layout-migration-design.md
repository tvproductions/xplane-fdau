# xplane-fdau Source-Layout Migration Design

- **Governance:** active
- **Status:** draft
- **Date:** 2026-08-09
- **Decision owner:** Jeff / tvproductions
- **Roadmap epic:** `B1`
- **Roadmap children:** `B1.1`
- **Approval:** —

## Context

The original xplane-fdr bootstrap copied the flat package layout inherited by
xplane-webapi and configured `uv_build` with `module-root = ""`. The later
xplane-fdau identity migration preserved that structure without making a new
layout decision.

xplane-fdau is an independent, distributable library. Its source package should
be isolated from the repository root so development and verification exercise
the installed project rather than succeeding through the current working
directory. No simulator, XPPython3, runtime-dependency, or artifact-format
constraint requires the flat layout.

## Decision

Move the import package from `xplane_fdau/` to `src/xplane_fdau/` before
canonical-contract implementation begins. Configure `uv_build` with
`module-root = "src"` and update every repository tool that addresses source
files by path.

The distribution name, import name, public API, console command, runtime
dependency boundary, and installed wheel paths do not change.

## Scope

`B1.1` performs one mechanical and independently reviewable migration:

1. move the complete tracked `xplane_fdau` tree to `src/xplane_fdau` while
   preserving bytes and Git history;
2. set `[tool.uv.build-backend].module-root` to `"src"`;
3. retarget source-aware quality, coverage, documentation, release, and import
   boundary checks to `src/xplane_fdau`;
4. preserve installed imports and wheel members under `xplane_fdau/`;
5. update source-distribution expectations to
   `xplane_fdau-0.1.0/src/xplane_fdau/`;
6. prove repository-root imports resolve through the installed project rather
   than a top-level package directory; and
7. update active documentation and workflow guidance that names a physical
   source path.

The migration does not change native FDR behavior, canonical contracts,
schemas, CLI semantics, public exports, or release authorization.

## Repository layout

The resulting source structure is:

```text
src/
└── xplane_fdau/
    ├── __init__.py
    ├── cli.py
    ├── formats/
    ├── sinks/
    └── py.typed
```

`tests/`, `tools/`, `docs/`, and repository-governance tooling remain at the
repository root. No compatibility package or root-level forwarding module is
created.

## Import and execution contract

All supported development commands run through the synchronized project
environment. Imports continue to use `xplane_fdau`; callers never import
`src.xplane_fdau`.

Tests that inspect physical source files derive the repository source root as
`ROOT / "src" / "xplane_fdau"`. Tests that inspect wheel members continue to
expect `xplane_fdau/...`. Tests that inspect source-archive members expect the
additional `src/` component.

A focused isolation test runs an interpreter from the repository root with the
project installed and proves:

- `xplane_fdau.__file__` resolves beneath `src/xplane_fdau` in the development
  environment;
- no root-level `xplane_fdau` directory exists; and
- built-wheel smoke testing imports from the installed wheel outside the
  checkout.

## Tooling changes

`tools/quality.py` uses `src/xplane_fdau` for Ruff, Bandit, documentation
coverage, complexity, cohesion, and maintainability paths. Coverage continues
to identify the import package as `xplane_fdau` unless a failing test proves a
physical path is required.

`tools/runtime_imports.py` keeps `xplane_fdau` as the allowed import root; only
callers that enumerate source files change their physical path.

`tools/release.py` keeps wheel-member expectations package-relative and changes
only checkout or source-archive paths. Release verification must still reject
unexpected native code, modules, package data, duplicate members, links, and
unsafe archive paths.

The console entry point remains:

```toml
xplane-fdau = "xplane_fdau.cli:main"
```

## Test-first migration sequence

Implementation begins with failing `unittest` contracts for the new physical
layout, build-backend root, quality-tool targets, source enumeration, and
source-archive members. The package tree then moves once, followed by the
minimal configuration and path updates needed to satisfy those contracts.

After focused tests pass, verification runs the complete repository quality
gate, strict documentation build, distribution build/check, and installed-wheel
smoke test. Generated artifacts are not committed.

## Failure handling

The migration stops if:

- tracked package files exist at both old and new roots;
- any active tool still enumerates the old physical source root;
- repository tests pass only because the checkout root is importable;
- wheel members gain an unintended `src/` prefix;
- source-archive validation omits the required `src/` prefix;
- installed smoke testing resolves into the checkout; or
- public API, runtime dependency, or artifact contents change unexpectedly.

## Acceptance criteria

### B1.1 — Source-layout migration and installed-import isolation

- The complete runtime package exists only under `src/xplane_fdau` and
  `uv_build` uses `module-root = "src"`.
- Quality, coverage, import-boundary, documentation, and release tooling address
  the new physical source root without weakening existing checks.
- Repository-root and installed-wheel tests prove imports resolve through the
  installed project rather than a top-level checkout package.
- Wheel members and public imports remain unchanged while source-archive members
  use the required `src/xplane_fdau` path.
- The full quality, strict documentation, distribution, and installed-artifact
  gates pass with no release, tag, or package publication.

## Delivery boundary

This design covers exactly `B1.1`. After written approval it receives one
focused implementation plan. Canonical-contract work remains behind `B1.1`,
and repository-governance tooling remains a separate `T1` epic.
