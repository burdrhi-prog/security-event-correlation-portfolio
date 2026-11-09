# Portfolio evidence-to-software audit — 2026-11-09

**Status:** Initial inventory and prioritized backlog; not a completed full-workbook audit.

## Source boundaries
- Private master investigation workbook and original provider exports are **not** published.
- Workbook search identified a November 6, 2026 binder/correlation workbook and its merge log. Its notes describe an earlier parent workbook and additions, but this audit has **not** reconciled every workbook sheet or original export.
- Public repositories and their READMEs were reviewed on November 9, 2026.
- Findings below are software requirements inspired by investigation *methods*, not allegations or claims about real people.

## Already implemented here
- CSV/JSON security-event import and UTC normalization.
- Source-scoped event identifiers and duplicate handling.
- Logical-client time-window correlations, without equating logical IDs with people or hardware.
- SIM lifecycle and authentication-event review windows.
- Markdown investigation reports with provenance and uncertainty.
- Evidence-quality checks, including an integrated fail-closed gate for invalid required data.
- Unit tests and a GitHub Actions workflow (hosted status must be checked separately).

## Priority backlog

| Priority | Evidence-handling problem | Synthetic software deliverable | Acceptance test |
|---|---|---|---|
| P0 | Conflicting corrections and superseded conclusions | Typed correction/supersession ledger | Earlier claim remains traceable but never silently appears as current |
| P0 | Missing or conflicting identifier bridges | Explicit relationship graph with provenance and valid-time interval | A SIM association on one day does not imply an earlier continuous association |
| P0 | Multiple provider timestamps and incomplete time zones | Time normalization and uncertainty-aware ordering | Naive timestamps fail validation; overlapping uncertainty windows are not falsely ordered |
| P1 | Authentication, delegated grants and actual control are different | Access-authority state matrix | Historical permission does not automatically become current access |
| P1 | Missing source records | Evidence completeness and gap report | Correlation cannot be labelled confirmed without required source bridge |
| P1 | Provider exports with changing schemas | Import schema/version fixtures | Unknown fields retained and schema drift flagged |
| P2 | Technical findings hard for nontechnical users | Plain-language report output | Each finding states observed, inferred, unknown and next verification step |

## Cross-project ownership
- **Security Event Correlation:** parsers, validation, correlation and report-generation code.
- **Digital Identity Forensics Lab:** methodology, source/evidence ledger, fictional case studies.
- **Identity Fairy:** plain-language, user-facing explanations based on validated synthetic findings.
- **Human–AI Collaboration Lab / Bot Boy:** correction-handling and evidence-grounding evaluation, not forensic source of truth.

## Privacy and claim discipline
Use fictional dates, addresses, account identifiers, network values and provider names in fixtures. Do not copy raw workbook rows, real account data, personal allegations or credentials. Do not claim a physical device, person, unauthorized actor, or current session from logical registration alone.

## Next audit gate
Before implementation of P0 features, inspect the latest authoritative workbook's relevant sheets, identify the exact source-to-claim rules, record any contradictory revisions, and convert only the generalized rules into synthetic tests. Record local test output and verify GitHub Actions before reporting tests as passing.
