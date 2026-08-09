# Imported architecture documents

This directory contains the cross-project architecture material that caused
the `xplane-fdr` design to be revised into `xplane-fdau`.

The documents were copied byte-for-byte from the q4xpcc repository at commit
`04f606dc1a4d25772a679a5afca49ce3257d985d` on 2026-08-09:

- `xplane12_virtual_fdau_ecosystem_design.md`
  (`sha256:fc0fe7c0c6c37e51f52dec2781ce840dec729365754f9afce3b308306ae54480`)
- `xplane12_foqa_fdr_addon_design_spec_v2.md`
  (`sha256:9333d74bdb2ffeb9a8d21fdf508393289bf1e230f775f55cd36a5ae01dbd23ad`)

The virtual FDAU/FDIU ecosystem design is the authoritative parent
architecture. The older FOQA/FDR illustration is retained only as its
supersession notice directs; it is not normative guidance.

Repository-specific specifications under `docs/superpowers/specs/` refine the
parent architecture into independently reviewable implementation increments.
They may narrow an increment's delivery scope, but they may not contradict the
parent architecture's ownership, dependency, regulatory, or conformance
boundaries.
