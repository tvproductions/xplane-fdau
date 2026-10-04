# C1.2 gate 3 — Pinned references

- **Child:** `C1.2`
- **Gate:** `3`
- **Kind:** verification
- **Result:** passed
- **Date:** 2026-10-04
- **Subject:** Definition and record references pin identity, revision/version, and hash.

`tests.test_contract_identity.ReferenceTests` checks exact DefinitionRef identity/revision/hash fields and all five RecordRef family URIs with integer schema version 1. Invalid hashes, families, versions, and Boolean versions fail at exact paths. Keyword-only frozen/slotted values and private wire converters preserve their property inventories. AlgorithmRef copies nested mappings and arrays into immutable storage, preserves Boolean/integer/real distinctions in equality, and round-trips plain wire object/array shapes. Caller mutation cannot change stored parameters. Cyclic and excessive-depth input raises bounded CanonicalJSONError, with canonical key order and escaped paths retained.

Public-export and installed-module tests confirm the staged C1.2 namespace; later model factories and public model hash dispatch remain assigned to their eligible-model children. The final focused run passed 41 tests. The installed-wheel reference assertion and artifact validation passed on Python 3.12.14; full gate details appear in `completion.md`.
