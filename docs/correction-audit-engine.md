# Evidence correction and supersession engine

**Synthetic demonstration only.** This feature imports three fictional CSV tables, preserves correction history, excludes superseded claims from the current-conclusions section, and flags missing evidence or potentially competing current claims.

## Run

```bash
python -m unittest discover -s tests -v
python scripts/correction_audit.py examples/correction_audit --output /tmp/current_conclusions.md --json-output /tmp/correction_audit.json
```

CSV schemas: `evidence.csv` uses `evidence_id,description`; `claims.csv` uses `claim_id,subject,statement,evidence_ids` (semicolon-separated IDs); `corrections.csv` uses `correction_id,claim_id,replacement_claim_id,reason`.

A current claim is **not superseded**, which does not imply it is true or independently verified. Missing references are flagged; shared subject labels indicate *potential* conflicts, not proven contradictions. The tool rejects correction cycles, unknown replacements and competing replacements.

No real workbook rows, account records, identifiers or allegations are published. This is not an immutable forensic store or a validated production system. Input CSVs are assumed trusted; source authenticity, authorization, schema evolution and adversarial-input handling are future work.

The existing GitHub Actions Python workflow discovers `tests/test_correction_audit.py` alongside the other unit tests. Hosted workflow outcomes must be verified separately in the Actions tab.
