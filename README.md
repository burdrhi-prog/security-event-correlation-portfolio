# Security Event Correlation Lab

[![Python tests](https://github.com/burdrhi-prog/security-event-correlation-portfolio/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/burdrhi-prog/security-event-correlation-portfolio/actions/workflows/tests.yml)

**Python · Security event correlation · Identity and access analysis · Evidence quality · GitHub Actions**

A privacy-safe, independently developed Python project demonstrating how to normalize, correlate, and document security events across fictional providers. It translates methods from an independently maintained investigation workbook into reproducible software and automated tests.

**All example events are synthetic.** This is a learning and portfolio project, not a production monitoring system or evidence of an actual compromise.

## At a glance

| Capability | Demonstration |
| --- | --- |
| Event ingestion | Read structured CSV/JSON event inputs |
| Timestamp handling | Normalize timezone-aware times to UTC while retaining source context |
| Correlation | Flag nearby events involving distinct logical clients; group authentication events around fictional SIM lifecycle anchors |
| Evidence provenance | Retain source references, record IDs, and authorization-status labels |
| Data quality | Identify duplicate source events, missing values, timezone problems, and unresolved labels |
| Reporting | Generate a Markdown investigation report and a JSON evidence-quality assessment |
| Automated validation | Run Python unit tests, report generation, and quality checks through GitHub Actions |

## Example findings (fictional data)

The [basic synthetic event example](examples/expected_output.json) illustrates a review signal:

- **5 unique events**, **0 duplicate event IDs**, and **1 correlation finding** using a 15-minute window.
- Two fictional providers report different logical client IDs for the same demonstration account **8 minutes apart**.
- The finding retains event IDs, source record IDs, UTC timestamps, and an explicit interpretation limit.

The [SIM/authentication sample](examples/synthetic_sim_auth_events.csv) illustrates **8 unique events, 1 duplicate record, and 2 grouped findings**. Its integrated evidence-quality review identifies **7 issues**: 5 unresolved authorization labels, 1 duplicate source-event record, and 1 mixed UTC-offset informational finding.

**Interpretation matters:** Time proximity is a reason to review records, not proof of a shared physical device, another person, unauthorized access, or causation.

## Try it

Requires **Python 3.10+**; uses the standard library only.

```bash
# Basic event correlation
python scripts/correlate_events.py examples/synthetic_events.csv

# SIM-change/authentication review
python scripts/sim_change_correlation.py examples/synthetic_sim_auth_events.csv

# Human-readable investigation report
python scripts/investigation_report.py examples/synthetic_sim_auth_events.csv --output investigation_report.md

# Machine-readable evidence-quality assessment
python scripts/evidence_quality.py examples/synthetic_sim_auth_events.csv --output evidence_quality.json

# All unit tests
python -m unittest discover -s tests -v
```

**Explore the results:** [Sample correlation JSON](examples/expected_output.json) · [Report generator](scripts/investigation_report.py) · [Evidence-quality checker](scripts/evidence_quality.py) · [GitHub Actions runs](https://github.com/burdrhi-prog/security-event-correlation-portfolio/actions)

## Investigation techniques demonstrated

1. **Preserve provenance:** Carry original event identifiers, source records, and timestamps into review outputs.
2. **Normalize carefully:** Compare events in UTC without conflating different identifier namespaces or discarding original timing context.
3. **Correlate without overclaiming:** Apply explicit time windows and SIM-event anchors as review heuristics, not causal proof.
4. **Assess input reliability:** Surface missing values, duplicates, uncertain authorization, and inconsistent timezone representations.
5. **Document uncertainty:** Separate observed records, correlated patterns, evidence gaps, and unresolved attribution.
6. **Automate repeatable checks:** Use Python unit tests and continuous integration to catch regressions before presenting results.

These skills are relevant to entry-level security operations, identity and access review, fraud/risk analysis, data-quality work, and technical documentation.

## Testing and project status

The badge above reflects the **current `main` branch** workflow. The [Python tests workflow](.github/workflows/tests.yml) runs on pushes and pull requests and performs unit testing, synthetic report generation, and evidence-quality checks.

On **November 10, 2026**, GitHub Actions runs **#16 and #17 passed** after an outdated report-test expectation was corrected from 6 to 7 quality issues and the documentation was updated. The earlier failed runs remain visible in the repository history. See the [Actions history](https://github.com/burdrhi-prog/security-event-correlation-portfolio/actions) for the current result.

## Documentation and methods

- [Privacy-safe workbook methodology case study](docs/workbook-methodology-case-study.md)
- [SIM-change correlation: methods and limitations](docs/sim-change-correlation.md)
- [Version 2 development notes](docs/version-2-notes.md)
- [Synthetic sample data](examples/synthetic_sim_auth_events.csv)

## Scope, privacy, and limitations

No private account exports, real-world identifiers, or accusations are published in this demonstration. Different logical registrations do **not** automatically mean different physical devices or operators. Correlations are investigative leads, not proof of compromise. Data-quality flags do not by themselves establish tampering.

This repository demonstrates independently developed methods and tested code; it does not claim paid professional security experience, certification, or production readiness.
