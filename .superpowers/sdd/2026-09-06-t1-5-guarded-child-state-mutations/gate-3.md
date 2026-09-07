# T1.5 gate-3 evidence

- **Child:** `T1.5`
- **Gate:** `3`
- **Kind:** verification
- **Result:** passed
- **Date:** 2026-09-06
- **Subject:** Selection and lifecycle transition graph

Selection is limited to eligible local children, and lifecycle mutation follows
the closed transition graph with stage-specific links and prerequisites.
Coverage includes `test_transition_allows_exact_closed_graph_only`,
`test_every_allowed_forward_and_reopen_edge_produces_a_clean_candidate`,
`test_transition_accepts_stage_specific_specification_and_review_links`, and
`test_suspend_and_resume_round_trip_all_nonsuspended_states`. The accepted
ruling admits exact adjacent lifecycle handoffs and clears the obsolete Plan
link on `specified -> designing` while retaining completed-plan handoff safety.

Reviewed implementation: `3cef7da35378bfce855565b618adf6d34c7a80db`.
[review.md](review.md) records an accepted rereview with zero unresolved
findings. The correction quality run passed 449 discovery and 449 coverage
tests at 94%; the accepted rereview passed 106 focused tests.

The standard-library implementation and Windows tests make no downstream
delivery or release claim. Ubuntu and Python 3.12 through 3.14 CI remain
unobserved pending a separately authorized push.
