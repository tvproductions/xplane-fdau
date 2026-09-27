# C1.1 gate 2 — Int64 and binary64 lexical vectors

- **Child:** `C1.1`
- **Gate:** `2`
- **Kind:** verification
- **Result:** passed
- **Date:** 2026-09-27
- **Subject:** Signed 64-bit integers and finite binary64 canonical spelling.

`tests.test_contract_json_parse` checks Int64 boundaries, negative zero, overflow, and nonzero underflow. `tests.test_contract_binary64` checks RFC 8785 Appendix B finite vectors, project real/integer lexical distinctions, negative zero, ECMAScript plain/exponent thresholds, and a frozen independent oracle of 4,096 unique finite bit patterns covering every finite exponent field 0–2046. Oracle source: Node/V8 v24.19.0 `JSON.stringify(Number)`; fixture SHA-256: `669cf361937c1fccc4a87dcc89047fdaa34cf0ac5d0b7f0916a996c2b01dd1ac`. Full offline hygiene exited 0 with 554 `unittest` tests.
