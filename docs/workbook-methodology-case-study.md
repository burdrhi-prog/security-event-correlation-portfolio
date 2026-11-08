# Independent Workbook Analysis — Privacy-Safe Case Study

## Context
An independently maintained, multi-provider investigation workbook was used to organize provider records, event timelines, identifier crosswalks, device/session lineage, and evidence references. This project demonstrates **analytical methods**, not findings about particular people.

## Inspected historical source
A locally provided historical workbook named `Master_Investigation_Timeline_Updated_2026-10-04_v137_Meta_DeviceID_IP_Possession_Boundary.xlsx` contains **158 worksheets**. Inspected sections include Master Timeline, Evidence Index, Identifier Crosswalk, History2 Overlap, Operator Workflow Analysis, and Attribution Workflow. The user referenced a newer v140 but it was not available; **v137 is a provisional historical reference, not the authoritative latest record**.

## Methods represented
1. Preserve source event IDs and original timestamps.
2. Normalize time zones for comparison, without overwriting source times.
3. Keep provider/client/device identifier namespaces distinct.
4. Cross-reference events by time windows and exact identifiers.
5. Separate source observation, user confirmation, technical correlation, disputed attribution, and unresolved hypotheses.
6. Keep an evidence index and document missing bridges before drawing conclusions.

## Engineering translation
The repository's Python example currently imports synthetic CSV events, normalizes timezone-aware timestamps, and flags two different logical client IDs within 15 minutes on the same account. It **does not** prove compromise or identify physical devices or operators. Further work: JSON support, configurable windows, source provenance in outputs, deduplication, and richer tests.

## Employer relevance
Security event triage; identity and access analysis; fraud/risk operations; data-quality checking; audit-ready technical documentation; automation opportunity identification.

## Privacy
No real workbook rows, names, account identifiers, network addresses, or allegations are included here. Numbers describing workbook scope are not incident counts or evidence of unique actors.
