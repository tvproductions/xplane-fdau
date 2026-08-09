---
name: documentation
description: Use when creating or updating xplane-fdr user guidance, MkDocs pages, stable API reference, configuration examples, or documentation verification.
---

# Publishing documentation

Document the behavior proved by this repository, not simulator behavior owned
by an adapter. The public import contract is `xplane_fdr.__all__`; the rendered
API reference is `docs/reference/fdr.md` through MkDocstrings.

## Workflow

1. Check the relevant public module, its `unittest` coverage, and the approved
   design before changing a claim or example.
2. Keep user pages in `README.md`, `docs/index.md`, and
   `docs/usage/fdr-toolkit.md`; update `docs/reference/fdr.md` when the stable
   public surface changes.
3. State the format boundary precisely: native X-Plane textual v3/v4 input,
   canonical v4 output, and explicit lossy v3 normalization. Keep capture,
   scheduling, connections, and plugin lifecycle adapter-owned.
4. For recording guidance, explain configured `Output/FDR files`, generated
   UTC filenames, explicit overwrite, and partial-artifact recovery. Link the
   packaged configuration schema instead of copying its rules.
5. Run the documentation contracts, then build the API reference and site:

   ```powershell
   uv run python -m unittest tests.test_public_api tests.test_documentation -v
   uv run mkdocs build --strict
   uv run python tools/quality.py docs
   ```

`mkdocs build --strict` renders the MkDocstrings API reference and fails on
MkDocs navigation or configured link-validation warnings.

## Common mistakes

- Do not imply a bundled capture adapter, live-record CLI, simulator callback,
  connection, or scheduler.
- Do not claim native `.fdr` support applies to ARINC recorder/QAR formats or
  FOQA/FDM analytics.
- Do not put MSL altitude in a third GeoJSON coordinate; use explicit
  properties with the 2D `[longitude, latitude]` geometry.
