# Backlog

## Required next increment

Before any release, separately reviewed increments must implement:

1. measurement, binding, observation, sample, frame, timing, and quality contracts;
2. acquisition profiles, demand resolution, continuity, and generic fan-out;
3. the canonical archive, manifest, recovery, and deterministic replay; and
4. projection from canonical samples to the native FDR sink with explicit loss
   reporting.

## Later governed work

Capture adapters remain consumer-owned and separately scoped. ARINC profiles and
codecs require edition-pinned standards governance after the canonical contracts
exist. FDM/FOQA analytics remain a later downstream system with separate analysis
and organizational governance. Native X-Plane textual `.fdr` v3/v4 is only a
lossy FDAU projection and sink, not the canonical archive.
