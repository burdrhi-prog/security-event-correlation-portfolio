# SIM-change and authentication correlation (Phase 3)

## Goal
Group account-security activity around a carrier SIM lifecycle event, retaining exact source identifiers, timestamp provenance, and interpretation boundaries.

## Source methodology
Inspired by the private investigation workbook v137's documented event-correlation approach. The workbook was not reopened for this release. All examples are synthetic; dates, providers, and account labels are fictional.

## Inputs
CSV with required fields: `event_id,timestamp,account,event_type,source,source_record_id`. Optional fields: `client_id,authorization_status`.

Recognized SIM anchors: `sim_change`, `sim_swap`, `sim_activation`, `sim_deactivation`.
Recognized security events: `login`, `recovery`, `password_reset`, `mfa_change`, `device_registration`, `session_refresh`, `recovery_contact_change`.

## Run
```bash
python scripts/sim_change_correlation.py examples/synthetic_sim_auth_events.csv
python scripts/sim_change_correlation.py examples/synthetic_sim_auth_events.csv --before-minutes 10 --after-minutes 10
python -m unittest discover -s tests -v
```

## Expected behavior
The sample has nine input rows, eight distinct source-scoped events, one duplicate, two grouped findings, and four related security events across the two SIM anchors. Original and normalized UTC timestamps, offsets, source record IDs, and reported authorization status are retained.

## Boundaries
- A carrier-confirmed event is not necessarily an authorized event.
- Account activity near a SIM event is not evidence that the SIM event caused it.
- Distinct client registrations do not prove distinct physical devices or operators.
- Authorization status is a reported data field, not independently validated.
- Duplicate keys use (source, event_id), not a globally unique event ID.
- One account event may appear in two SIM-anchor findings if windows overlap; this is intentional, not an extra source event.
- No private workbook records, IP addresses, phone numbers, or identifying allegations are published.

## Local verification
The Phase 3 implementation was exercised against 12 automated tests locally on 2026-11-09. GitHub Actions execution has not yet been configured.
