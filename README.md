# Security Event Correlation Lab

**Identity & Access Analysis · Security Event Investigation · Data Quality · Workflow Automation**

An independent portfolio project demonstrating how heterogeneous account and device activity can be organized into traceable, reviewable findings.

> **Project status:** Runnable synthetic example and unit tests committed; execution in a clean checkout remains to be verified.

## Why this matters
Security and fraud teams routinely encounter inconsistent timestamps, different identifier formats, and ambiguous activity across systems. Analysts must preserve evidence provenance and distinguish unusual events from confirmed incidents.

## What this project will demonstrate
- Import and validate CSV/JSON security event records.
- Normalize timestamps while retaining original values.
- Correlate authentication, recovery, session, and device-registration events.
- Flag anomalies for human review without unsupported attribution.
- Produce evidence-linked summaries for technical and nontechnical audiences.
- Validate outputs with repeatable tests.

## Evidence-grounded case study
[How independent workbook methods translate into security and data analysis skills](docs/workbook-methodology-case-study.md). Historical workbook evidence is private; the public-facing case study describes methods and limitations only.

## Relevant roles
Security Operations / SOC · Identity & Access Management · Fraud & Risk Analysis · Technical Data Analysis · Security Automation · Technical Support

## Evidence discipline
**Observation is not interpretation. Correlation is not attribution. Multiple logical registrations do not prove multiple physical devices.**

This project builds on independent research and structured investigation-workbook methods. All examples intended for public sharing will be synthetic; no personal account exports, identifying records, or allegations belong in this repository.

## Try the working example

Requires Python 3.10+; uses only the standard library.

```bash
python scripts/correlate_events.py examples/synthetic_events.csv
python -m unittest discover -s tests -v
```

The five synthetic records are designed to produce **one review signal**: two different logical client IDs on the same example account, eight minutes apart. The tool outputs JSON with event IDs, elapsed time, and explicit interpretation limits.

[View the script](scripts/correlate_events.py) · [Synthetic sample](examples/synthetic_events.csv) · [Tests](tests/test_correlate_events.py)

The repository now contains executable source and tests, but execution in a clean checkout has not yet been independently verified.

## Roadmap
- [x] Establish repository and career-oriented project scope.
- [x] Document workbook-based evidence methodology in the linked case study.
- [ ] Publish a formal machine-readable event schema.
- [x] Create synthetic event data.
- [x] Implement first-pass timestamp normalization and event correlation in Python.
- [x] Add initial automated tests.
- [ ] Run tests in a clean checkout and capture sample output/screenshots.
- [ ] Review privacy and presentation before making repository public.

*Independent learning project; no claim of paid analyst employment, certification, or production deployment.*
