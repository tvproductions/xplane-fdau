# D1.1 Canonical C1-C4 Design Review

- **Child:** `D1.1`
- **Gate:** —
- **Kind:** review
- **Result:** accepted
- **Date:** 2026-08-23
- **Subject:** Independent canonical C1-C4 design review

## Reviewed revisions

The independent read-only review covered the complete canonical design at
accepted head `5417a3e`, beginning with candidate `0f6bc18` and reviewing each
correction wave at `acc79e7`, `c232a77`, `96ada92`, and `5417a3e`. The reviewer
also re-audited the complete resulting specification after every wave rather
than limiting review to the changed paragraphs.

The reviewed implementation scope was one design document only:

- `docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md`.

No runtime code, schema, fixture, conformance corpus, package artifact,
implementation plan, adapter, q4xpcc file, release, push, tag, or publication
was reviewed or delivered.

## Findings and resolutions

The initial review reported no Critical finding, 11 Important findings, and
three Minor findings. Correction waves made schema ordering independent from
semantic error order; closed enumeration-array, elementwise numeric,
referenced-payload, applicability, failure/normalization, validity/quality,
freshness, anchor, derivation, public-API, media-type, conformance-result, and
nested-error-order contracts; aligned the normative module tree; and made UTC
interval arithmetic cross-language exact.

Subsequent whole-design reviews found and resolved remaining interactions:

- raw enumeration evidence is preserved without a measurement catalog while
  normalized values resolve against the measurement enumeration;
- direct, transformed, raw, and normalized referenced payloads obey exact
  payload-spec compatibility and membership rules;
- C3 distinguishes closure-corroborated facts from producer assertions whose
  later algorithm or continuity contracts provide corroboration;
- primary freshness age is persisted separately from all-input staleness;
- measurement quality/validity authorization is cross-validated against every
  sample-producing binding failure disposition; and
- any derived `reject` condition is globally dominant, eliminating
  multi-condition policy bypass.

The fifth review found no Critical, Important, or Minor finding. It confirmed
that global rejection, absent-normalization selection, quality/validity
authorization, all-input staleness, payload closure, canonical-disposition
parity, cross-contract tests, and C2.4 acceptance criteria are mutually
consistent. `git diff --check` passed for every reviewed correction range.

## Result

Accepted. The canonical design at `5417a3e` has no unresolved load-bearing
finding and is suitable for D1.1 approval as cross-epic C1-C4 implementation
authority. This review does not claim any C1-C4 delivery gate, runtime
implementation, schema, fixture, corpus, artifact, adoption, release, push,
tag, or publication.
