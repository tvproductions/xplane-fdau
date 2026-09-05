---
name: gzs-intent-audit
description: Trace declared intent to observed shipped behavior and classify gaps as corrections rather than new design. Use when a capability exists but may not fulfill its specification, during a pre-release integrity review, or when checking whether completed work actually delivered what was decided.
compatibility: Requires a durable source of intent and an observable implemented or shipped surface.
metadata:
  govzero-version: "0.1.0"
  govzero-portability: "portable"
  govzero-origin: "gz-skills"
---

# GovZero Intent Audit

Answer one question per sampled capability: does the observed surface fulfill
the intent that authorized it?

## Workflow

1. Resolve the audit population. For a large corpus, select a bounded sample
   before reading implementation, using risk signals such as incomplete work,
   stale evidence, failing checks, inert mechanisms, high fan-out, or user
   reports. Record why each item entered the sample.
2. Read the authoritative decision, specification, issue, or acceptance record.
   Extract each intent claim verbatim or with an exact citation. Do not inspect
   the implementation until the claims are fixed.
3. Locate the actual delivered surface. Run or exercise it at the user-visible
   seam; a test or documentation claim alone does not prove behavior exists.
4. Compare each claim with observed behavior:

   - **Fulfilled**: the claim is demonstrably met.
   - **Correction**: the delivered surface does not fulfill its owning intent.
   - **Enhancement**: the intent is fulfilled and a genuinely new capability is
     proposed.

5. Route corrections under their owning work item or decision. Do not create a
   new design artifact merely because the original delivery is incomplete.
6. Stop at diagnosis and routing unless the user also requested implementation.

## Evidence

Report the sample and selection signals, cited intent claims, commands or steps
used to observe the delivered surface, per-claim verdicts, and exact correction
routes. Name unavailable evidence and uncertainty; never infer fulfillment from
artifact presence alone.
