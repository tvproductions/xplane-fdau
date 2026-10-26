# C1.4 gate 2

- **Child:** `C1.4`
- **Gate:** `2`
- **Kind:** verification
- **Result:** passed
- **Date:** 2026-10-26
- **Subject:** UTC retains exact nanoseconds and explicit uppercase Z.

UtcAnchorTests and the canonical scalar test cover nine-digit text, Gregorian years 0001–9999, leap-day/calendar failures, exact canonical bytes, UTC-aware microsecond conversion, and rejection of precision loss. Installed smoke checks exact nine-digit output and conversion rejection; its altered-digit negative control fails as intended.

Verified candidate: staged tree `e97f887d9e8deab63cf331148b1fbd73dbb9259f`
on Python 3.12.16. The 92 focused tests and full offline hygiene passed.
The external source environment passed 691 unittest tests in 307.496 seconds;
the wheel-only environment passed installed smoke with no development dependencies.
Strict metadata and exact artifact inventories passed. See [completion](completion.md)
for commands, artifact SHA-256 hashes and evidence scope; [review](review.md)
records the independent finding and executor verification. All 130 relevant
input hashes remained unchanged across the complete checks.
