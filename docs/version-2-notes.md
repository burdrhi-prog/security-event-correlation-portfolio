# Version 2 — implementation and verification

This project implements methods inspired by a private investigation workbook's documented v137 methodology. The workbook itself was not accessible for direct reinspection during this update. No real case records are used.

## Features
- CSV and JSON event ingestion with required-field validation.
- UTC timestamp normalization with explicit rejection of timezone-naive values.
- Logical-client overlap within a configurable 1–1440 minute window.
- Account-scoped comparison; events from different accounts are never paired.
- Source provenance (provider, source record ID, event ID, UTC timestamps) in each finding.
- Repeated event IDs counted and excluded from event correlation.
- Human-review classifications rather than assertions of compromise or operator identity.

## Known limitations
- Duplicate detection uses event_id only within a file; cross-provider ID collisions require compound identifiers.
- IP and device fields are ingested but not used for attribution or correlation.
- The tool is a teaching/demo implementation, not a forensic determination engine.
- No raw private workbook data is stored here.

## Reproduce
From the repository root:

```bash
python -m unittest discover -s tests -v
python scripts/correlate_events.py examples/synthetic_events.csv
python scripts/correlate_events.py examples/synthetic_events.csv --window-minutes 5
```

## Verification
Locally executed eight unittest cases successfully on 2026-11-09. The five-event synthetic sample yielded one finding at the default 15-minute window, with an eight-minute gap. At five minutes, it yielded zero findings.
