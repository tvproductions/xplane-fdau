# C3.1 independent review and disposition

- **Child:** `C3.1`
- **Gate:** —
- **Kind:** review
- **Result:** accepted
- **Date:** 2026-11-22
- **Subject:** C3.1 independent review and disposition

Independent review examined b54bc02b5487c21ba3f8dec496be2840971ee054 (tree c0d10554e5d5201aec81fc3c684c7b430c48601d) against 580ec58e78fadb1ca6de89a57f921a0e80d3541c. The corrected technical candidate is 62563568f175d33c72f32b1841f3a63d005f439b (tree 1282a30530f8a90cffb8cda0be94a719e7a742d2). [Verification manifest](verification.json) records the exact input and artifact hashes. The [approved implementation plan](../../../docs/superpowers/plans/2026-11-22-c3-1-raw-observation.md) governs this evidence.

The fresh-context reviewer examined all 22 changed files, passed 22 selected unittest tests on Python 3.12.16, and independently signed and checked 90 evidence/status/diagnostic combinations. The reviewer requested corrections on four Important findings and flagged ordered Sequence acceptance as Minor. The approved public API makes the Sequence finding material. The native execution fix pass reproduced and resolved all five findings.

| Finding | Regression test |
| --- | --- |
| The projection escaped with KeyError for impossible inline shapes under a null discriminant | test_null_inline_tags_still_require_possible_value_shapes |
| Later nested fields could outrank earlier evidence or applicability rules | test_competing_nested_semantics_follow_property_order |
| Source and receipt clocks could alias one domain UUID despite incompatible definitions | test_source_domain_cannot_alias_receipt_domain |
| The constructor ran wire dispatch before shape and canonical-domain checks | test_constructor_envelope_follows_shape_and_domain_checks |
| Valid ordered inputs were limited to built-in lists and tuples | test_ordered_sequences_are_defensively_copied |

Each test reproduced its finding before the fix and passed afterward. The complete Windows offline hygiene pass included unittest and exact artifact validation. An independently installed wheel passed the public installed smoke. This receipt accepts the review disposition and resulting verification evidence.
