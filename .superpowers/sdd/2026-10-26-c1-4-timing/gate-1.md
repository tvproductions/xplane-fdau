# C1.4 gate 1

- **Child:** `C1.4`
- **Gate:** `1`
- **Kind:** verification
- **Result:** passed
- **Date:** 2026-10-26
- **Subject:** Clock domains and readings retain identity and unit metadata.

ClockModelTests covers all kinds and units, positive resolution, origin/scope and producer identity, UUID/text/integer boundaries, frozen keyword-only models, and a defensively copied immutable reduced tick mapping. Literal canonical projection and the external installed smoke verify delivery.

Verified candidate: staged tree `e97f887d9e8deab63cf331148b1fbd73dbb9259f`
on Python 3.12.16. The 92 focused tests and full offline hygiene passed.
The external source environment passed 691 unittest tests in 307.496 seconds;
the wheel-only environment passed installed smoke with no development dependencies.
Strict metadata and exact artifact inventories passed. See [completion](completion.md)
for commands, artifact SHA-256 hashes and evidence scope; [review](review.md)
records the independent finding and executor verification. All 130 relevant
input hashes remained unchanged across the complete checks.
