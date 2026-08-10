# xplane-fdau

`xplane-fdau` is a standard library-only virtual Flight Data Acquisition Unit /
Flight Data Interface Unit toolkit for X-Plane. Native X-Plane FDR v3/v4 is
retained as one deliberately lossy replay format and recording sink; it is not
the canonical FDAU archive.

Version `0.1.0` is unreleased. It supports Python 3.12+ with no runtime
dependencies. Native FDR callers import parsing, models, writing, profiles,
configuration, validation errors, and GeoJSON projection from
`xplane_fdau.formats.xplane_fdr`. Recording callers import the native sink from
`xplane_fdau.sinks.xplane_fdr`.

Capture remains adapter-owned: this project does not bundle Web API or XPLM
adapters, connections, cadence scheduling, or plugin lifecycle management.

## Project roadmap

Development toward the canonical FDAU architecture is tracked in the
[roadmap](ROADMAP.md). The [delivery backlog](BACKLOG.md) records stable slice
IDs, dependencies, specification and plan links, status, and measurable
acceptance gates. Version `0.1.0` remains unreleased until the canonical
vertical-slice release gates are independently verified.

See the [documentation site](https://tvproductions.github.io/xplane-fdau/) for
the [native FDR guide](docs/usage/native-fdr.md) and
[native FDR API reference](docs/reference/native-fdr.md).
