# xplane-fdr

`xplane-fdr` is a pure-Python toolkit using only the Python standard library for native
X-Plane textual Flight Data Recorder files. It accepts FDR v3 and v4 input and
always writes deterministic canonical v4 output. Python 3.12 or newer is
required.

The library is deliberately capture-neutral. An adapter reads simulator or
external values, decides cadence scheduling, manages connections and plugin
lifecycle, and submits semantic samples; capture adapters are not bundled.
This package does not import a Web API client, XPPython3, `xp`, or XPLM.

## What it includes

- Incremental v3/v4 reading and strict validation.
- Deterministic v4 writing, including partial-artifact recovery.
- Push-first recording sessions, stock profiles, and strict JSON configuration.
- JSON-compatible GeoJSON conversion and offline commands.

## What it does not include

The command line does not include a live-record command. Capture sources,
connections, scheduling, and simulator plugin lifecycle belong to the adapter
that calls `session.record(sample)`.

Native X-Plane textual `.fdr` v3/v4 files are not real-aircraft ARINC
recorder/QAR formats. This project also does not provide FOQA/FDM analytics or
program thresholds.

Continue with the [FDR toolkit guide](usage/fdr-toolkit.md) or the
[stable API reference](reference/fdr.md).
