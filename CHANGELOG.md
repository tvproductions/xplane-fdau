# Changelog

All notable changes to this project are documented here.

## 0.1.0 (Unreleased)

- Added immutable source-binding catalogs, staged public version-1 binary I/O,
  a mirrored normative schema and pure exact-reference, declaration and failure-
  authorization validation against an explicitly supplied measurement catalog.
- Enforce LF checkouts for byte-exact contract resources and provenance evidence;
  preserve native FDR fixture line separators.

- Added immutable source-binding definitions with exact measurement and algorithm
  references, local transform graph validation, explicit failure policies and
  private staged entry interchange. Algorithm execution remains deferred to A1.4.

- Clarify existing release planning: PRDs guide majors, selected work and
  requirements drive minors, and fixes drive patches. Require explicit scope,
  version rationale and acceptance evidence; preserve current release gates.

- Added a strict repository backlog audit to `audit`, `status`, and version-1
  JSON, including contextual structural, artifact, lifecycle, and Git evidence
  findings. Git observation preserves index bytes; command output uses UTF-8
  and LF, including on Windows.
- Bounded native FDR timestamp hour parsing so Python 3.12 through 3.14 reject
  the same malformed hour spellings.
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
