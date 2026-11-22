# Preserve receipt and source timing evidence

- **Child:** `C3.1`
- **Gate:** `4`
- **Kind:** verification
- **Result:** passed
- **Date:** 2026-11-22
- **Subject:** Preserve receipt and source timing evidence

Independent review examined b54bc02b5487c21ba3f8dec496be2840971ee054 (tree c0d10554e5d5201aec81fc3c684c7b430c48601d) against 580ec58e78fadb1ca6de89a57f921a0e80d3541c. The corrected technical candidate is 62563568f175d33c72f32b1841f3a63d005f439b (tree 1282a30530f8a90cffb8cda0be94a719e7a742d2). [Verification manifest](verification.json) records the exact input and artifact hashes. The [approved implementation plan](../../../docs/superpowers/plans/2026-11-22-c3-1-raw-observation.md) governs this evidence.

The tests preserve receipt-only timing and independently supplied clocks, anchors, sequences and simulator context. They reject inconsistent producer/reading context and source clock aliasing at the precise path. The installed smoke exercises receipt-only data and a validly rehashed timing violation.
