# Security Event Correlation Lab — Version 2

**Identity & Access Analysis · Security Event Investigation · Data Quality · Workflow Automation**

A privacy-safe Python portfolio demonstration inspired by independent multi-provider security investigation workbook methods. **Synthetic data only.** No real account exports, identifying details, or accusations are included.

## What it does

- Imports CSV or JSON security event data.
- Normalizes timezone-aware timestamps to UTC.
- Detects repeated event IDs and preserves the duplicate count.
- Finds different logical client IDs on the same account within a configurable time window.
- Outputs review signals with event IDs, source references, and explicit interpretation limits.

**Correlation is not attribution.** Different logical client identifiers do not establish separate physical devices, users, or unauthorized access.

## Run

Python 3.10+; standard library only.

```bash
python scripts/correlate_events.py examples/synthetic_events.csv
python scripts/correlate_events.py examples/synthetic_events.csv --window-minutes 5
python -m unittest discover -s tests -v
```

Expected sample result: 5 unique events, 0 duplicate event IDs, 1 finding with an 8-minute gap. All 8 tests passed in local execution on 2026-11-09.

See [Version 2 notes](docs/version-2-notes.md), [sample JSON output](examples/expected_output.json), and the [privacy-safe workbook methodology case study](docs/workbook-methodology-case-study.md).

## Status and limitations

This is an independent learning project, not a production security product or evidence of a specific real-world incident. Workbook v137 is the methodological reference described in earlier documentation; it was not re-opened for this release. IP and device fields are retained but not interpreted. No claims of paid professional experience or certification are made.
