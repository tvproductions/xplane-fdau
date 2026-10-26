# C1.4 gate 4

- **Child:** `C1.4`
- **Gate:** `4`
- **Kind:** verification
- **Result:** passed
- **Date:** 2026-10-26
- **Subject:** Explicit anchors and optional source/simulator evidence round-trip without invention.

TimingReaderTests covers minimal/full nested round-trips, matching receipt/source IDs, anchor reading/UTC and uncertainty, sequence/cycle/simulator-time boundaries, closed phase/replay values, pause, signed finite speeds, omitted fields and prohibited null. Shape/domain/semantic tiers and nested contextual order have competing-error regressions, including the independently reviewed defect. Private producer-context validation is delivered; integration with an enclosing RawObservation remains C3.1.

Verified candidate: staged tree `e97f887d9e8deab63cf331148b1fbd73dbb9259f`
on Python 3.12.16. The 92 focused tests and full offline hygiene passed.
The external source environment passed 691 unittest tests in 307.496 seconds;
the wheel-only environment passed installed smoke with no development dependencies.
Strict metadata and exact artifact inventories passed. See [completion](completion.md)
for commands, artifact SHA-256 hashes and evidence scope; [review](review.md)
records the independent finding and executor verification. All 130 relevant
input hashes remained unchanged across the complete checks.
