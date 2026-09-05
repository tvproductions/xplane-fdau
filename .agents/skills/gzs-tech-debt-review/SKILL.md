---
name: gzs-tech-debt-review
description: Survey scoped technical debt using the repository's existing analyzers and render a prioritized, evidence-grounded report without implementing fixes. Use for technical-debt reviews of changed files, a component, a work item, or the whole repository.
compatibility: Uses whichever static analysis, test, documentation, dependency, and repository tools the target project already declares.
metadata:
  govzero-version: "0.1.0"
  govzero-portability: "portable"
  govzero-origin: "gz-skills"
---

# GovZero Technical-Debt Review

Survey debt; do not patch it. Wield existing project probes, preserve their raw
evidence, and recommend a concrete fix shape and route for every retained
finding.

## Workflow

1. Resolve a bounded scope from the user's request: changed files, explicit
   paths, a work item, or the whole repository. Save or report the exact file set
   so the audit can be repeated.
2. Discover available canonical probes. Use only evidenced categories, such as
   complexity and size, lint and types, test gaps, dead code, dependency drift,
   documentation drift, stale TODOs, packaging boundaries, portability, or
   generated-surface coherence. Prefer repository wrappers over rebuilding
   their command sequences.
3. Run every selected probe and retain its command, exit status, and raw output
   location. A missing or broken probe is itself a finding; never silently drop
   a category after selecting it.
4. Convert probe hits into findings with class, severity, location, verbatim
   evidence, recommended fix shape, and route. Remove verified false positives
   with a recorded reason.
5. Grade severity by blast radius and reversibility, not by estimated diff size:

   - Critical: violates a published contract, security boundary, or release gate.
   - High: breaks binding project policy or blocks the next change on the surface.
   - Medium: compounds silently but does not block near-term delivery.
   - Low: local, cosmetic, or safely autotool-fixable drift.

6. Recommend an imperative fix shape, not “review,” “clean up,” or speculative
   new capability. Route through the repository's existing maintenance or issue
   process, but do not create external work items without authorization.
7. Render a severity-sorted summary and cited detail for Critical and High
   findings. End with the smallest useful next action.

## Evidence

Report the scope, probes and failures, severity counts, highest-risk findings,
report path when written, and recommended routes. The review is incomplete when
a selected probe has no recorded outcome.
