# T1.5 gate-2 evidence

- **Child:** `T1.5`
- **Gate:** `2`
- **Kind:** verification
- **Result:** passed
- **Date:** 2026-09-06
- **Subject:** Expected values and stale target rejection

Expected selection, lifecycle status, and gate state are validated before a
candidate is accepted. A normalized lowercase SHA-256 pins apply authority;
initial and final byte checks refuse stale targets. Coverage includes
`test_plan_refuses_malformed_or_uppercase_target_hashes`,
`test_plan_refuses_a_stale_well_formed_target_hash`,
`test_transition_refuses_stale_expected_status_before_candidate`,
`test_record_gate_refuses_stale_gate_preconditions_and_invalid_ordinals`, and
`test_target_changed_during_fresh_candidate_audit_is_not_overwritten`.

Reviewed implementation: `3cef7da35378bfce855565b618adf6d34c7a80db`.
[review.md](review.md) records an accepted rereview with zero unresolved
findings. The correction quality run passed 449 discovery and 449 coverage
tests at 94%; the accepted rereview passed 106 focused tests.

Windows directly exercised stale-target refusal and owned-partial cleanup.
Ubuntu and Python 3.12 through 3.14 CI remain unobserved pending a separately
authorized push. This evidence authorizes no release or publication.
