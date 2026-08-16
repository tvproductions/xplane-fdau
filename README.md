# xplane-fdau

`xplane-fdau` is the standard-library-only, transport-free flight-data kernel
for X-Plane. It defines the shared FDAU/FDIU domain contracts and processing
used by external XPPython3/XPLM and `xplane-webapi` clients, but never connects
to X-Plane itself. It is X-Plane-specific, not simulator-neutral.

Version `0.1.0` is unreleased. It has no runtime dependencies and uses only the
Python standard library. It is tested on Python 3.12, 3.13, and 3.14. Python
3.12 is the compatibility floor for code composed into an XPPython3 client,
not an exact project-wide `3.12.x` pin.

The core is the home for canonical flight-data acquisition semantics,
recording, recovery, replay, native X-Plane FDR support, edition-pinned ARINC
standards implementations, and X-Plane FDM/FOQA-oriented analysis. Those
capabilities are delivered incrementally; the current native FDR surface is
available from `xplane_fdau.formats.xplane_fdr` and
`xplane_fdau.sinks.xplane_fdr`.

All simulator I/O remains client-owned. This project does not bundle Web API
or XPLM adapters, connections, cadence scheduling, or plugin lifecycle
management. Native X-Plane textual FDR v3/v4 is one deliberately lossy replay
format and recording sink; it is neither the canonical FDAU archive nor an
ARINC recorder format.

## Project roadmap

Development toward the canonical FDAU architecture is tracked in the
[roadmap](ROADMAP.md). The [delivery backlog](BACKLOG.md) records stable slice
IDs, dependencies, specification and plan links, status, and measurable
acceptance gates. Version `0.1.0` remains unreleased until the canonical
vertical-slice release gates are independently verified.

See the [documentation site](https://tvproductions.github.io/xplane-fdau/) for
the [native FDR guide](docs/usage/native-fdr.md) and
[native FDR API reference](docs/reference/native-fdr.md). The
[core-scope amendment](docs/architecture/xplane_fdau_core_scope_amendment.md)
defines the governing ecosystem boundary.
