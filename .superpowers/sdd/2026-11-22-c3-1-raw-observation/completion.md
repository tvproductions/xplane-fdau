# C3.1 completed raw observation record and schema

- **Child:** `C3.1`
- **Gate:** —
- **Kind:** verification
- **Result:** passed
- **Date:** 2026-11-22
- **Subject:** C3.1 completed raw observation record and schema

Independent review examined b54bc02b5487c21ba3f8dec496be2840971ee054 (tree c0d10554e5d5201aec81fc3c684c7b430c48601d) against 580ec58e78fadb1ca6de89a57f921a0e80d3541c. The corrected technical candidate is 62563568f175d33c72f32b1841f3a63d005f439b (tree 1282a30530f8a90cffb8cda0be94a719e7a742d2). [Verification manifest](verification.json) records the exact input and artifact hashes. The [approved implementation plan](../../../docs/superpowers/plans/2026-11-22-c3-1-raw-observation.md) governs this evidence.

The four planned tasks delivered the mirrored schema, immutable raw observation and tagged evidence, the four strict public interchange functions, and the executable guide and installed smoke. The four C3.1 acceptance gates have executable receipts.

The Windows Python 3.12.16 check passed the frozen lock check, strict backlog audit, MkDocs build, Ruff lint and format, ty, full unittest suite, and strict wheel/sdist metadata and inventory. A separate external environment installed only the verified wheel and passed the public raw-observation and native FDR smoke checks. The schema is byte-identical across the documentation mirror, source resource and installed wheel. Other platforms were outside this execution.

The published baseline is empty and the pending initial release is 0.1.0. The selected canonical contract kernel through C4.4 now includes completed M0, B1.1, C1.1–C1.5, C2.1–C2.4 and C3.1. C3.2–C3.5 and C4.1–C4.4 remain. Later release bundles cover acquisition, recording and replay, and native projection with G1. The approved design and roadmap govern the selected scope. The change adds unpublished wire behavior. The project metadata, runtime version, lock and changelog agree on 0.1.0. STRICT acceptance and the publication decision remain open.

## Execution rulings

- Update the existing installed-module and synthetic archive inventories. The full hook showed that the new acquisition package invalidated the old fixtures. Updating them preserves the negative checks for missing or changed artifact resources.
- Treat ordered Sequence acceptance as material because the approved constructor declares that input boundary. This relies on normal iteration behavior from supplied Sequence implementations and leaves text, binary buffers, unordered containers and arbitrary iterators outside the input boundary.
