# Changelog

All notable changes to this project are documented here.

## 0.1.0 (Unreleased)

- Renamed the unreleased project, distribution, import namespace, console
  command, documentation, schemas, workflows, and artifacts to `xplane-fdau`.
- Relocated native X-Plane FDR v3/v4 beneath explicit format and sink boundaries
  as a deliberately lossy replay format and
  recording sink, including reading, canonical v4 writing, configuration, and
  GeoJSON projection.
- Added native offline commands under `xplane-fdau fdr` and non-publishing
  artifact validation across Python 3.12 through 3.14.
- Preserved a standard-library-only runtime and reduced the native reader to the
  enforced complexity ceiling without changing its accepted behavior.
- Publication remains
  prohibited until the canonical vertical slice is complete.
