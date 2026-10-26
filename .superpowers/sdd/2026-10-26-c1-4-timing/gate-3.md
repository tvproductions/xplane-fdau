# C1.4 gate 3

- **Child:** `C1.4`
- **Gate:** `3`
- **Kind:** verification
- **Result:** passed
- **Date:** 2026-10-26
- **Subject:** Checked arithmetic accepts related domains and rejects unrelated domains.

ClockArithmeticTests covers signed comparisons, exact nanosecond/unit scaling independent of resolution, rational tick periods, fractional rejection, both Int64 endpoints and overflow, and cancellation through large intermediate integers. Installed smoke checks a 1/3-tick difference and unrelated-domain rejection; its incorrect-difference negative control fails as intended.

Verified candidate: staged tree `e97f887d9e8deab63cf331148b1fbd73dbb9259f`
on Python 3.12.16. The 92 focused tests and full offline hygiene passed.
The external source environment passed 691 unittest tests in 307.496 seconds;
the wheel-only environment passed installed smoke with no development dependencies.
Strict metadata and exact artifact inventories passed. See [completion](completion.md)
for commands, artifact SHA-256 hashes and evidence scope; [review](review.md)
records the independent finding and executor verification. All 130 relevant
input hashes remained unchanged across the complete checks.
