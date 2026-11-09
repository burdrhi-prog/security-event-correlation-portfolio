"""Privacy-safe synthetic evidence correction and supersession audit."""
import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

REQUIRED_EVIDENCE = {"evidence_id", "description"}
REQUIRED_CLAIMS = {"claim_id", "statement", "evidence_ids"}
REQUIRED_CORRECTIONS = {"correction_id", "claim_id", "replacement_claim_id", "reason"}


def read_csv(path, required):
    with open(path, newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError(f"{path}: missing columns {sorted(required - set(reader.fieldnames or []))}")
        return list(reader)


def unique_rows(rows, key, label):
    result = {}
    for row in rows:
        identifier = row[key].strip()
        if not identifier or identifier in result:
            raise ValueError(f"{label}: empty or duplicate {key}: {identifier!r}")
        result[identifier] = row
    return result


def audit(evidence_rows, claim_rows, correction_rows):
    evidence = unique_rows(evidence_rows, "evidence_id", "evidence")
    claims = unique_rows(claim_rows, "claim_id", "claims")
    corrections = unique_rows(correction_rows, "correction_id", "corrections")
    issues, successors = [], {}
    for cid, row in corrections.items():
        old, new = row["claim_id"].strip(), row["replacement_claim_id"].strip()
        if old not in claims:
            issues.append(f"{cid}: original claim not found: {old}")
        elif new not in claims:
            issues.append(f"{cid}: replacement claim not found: {new}")
        elif old == new:
            issues.append(f"{cid}: claim cannot supersede itself")
        elif old in successors:
            issues.append(f"{cid}: multiple replacements for {old}")
        else:
            successors[old] = new
    for start in successors:
        visited, cursor = set(), start
        while cursor in successors:
            if cursor in visited:
                issues.append(f"correction cycle involving {cursor}")
                break
            visited.add(cursor)
            cursor = successors[cursor]
    if issues:
        raise ValueError("; ".join(sorted(set(issues))))
    current, history, gaps, contradictions = [], [], [], []
    for claim_id, row in claims.items():
        refs = [x.strip() for x in row["evidence_ids"].split(";") if x.strip()]
        missing = sorted(set(refs) - set(evidence))
        if not refs or missing:
            gaps.append({"claim_id": claim_id, "missing_evidence_ids": missing,
                         "reason": "no evidence cited" if not refs else "referenced evidence not found"})
        item = {"claim_id": claim_id, "statement": row["statement"], "evidence_ids": refs,
                "status": "superseded" if claim_id in successors else "current",
                "evidence_complete": bool(refs) and not missing}
        if claim_id in successors:
            item["superseded_by"] = successors[claim_id]
        history.append(item)
        if claim_id not in successors:
            current.append(item)
    by_subject = defaultdict(list)
    for row in claim_rows:
        if row.get("subject", "").strip() and row["claim_id"] not in successors:
            by_subject[row["subject"].strip()].append(row["claim_id"])
    for subject, ids in by_subject.items():
        if len(ids) > 1:
            contradictions.append({"subject": subject, "current_claim_ids": sorted(ids)})
    return {"current_claims": current, "history": history,
            "corrections": list(corrections.values()), "evidence_gaps": gaps,
            "potential_conflicts": contradictions,
            "summary": {"evidence_count": len(evidence), "claim_count": len(claims),
                        "correction_count": len(corrections), "current_count": len(current),
                        "superseded_count": len(successors)}}


def render_markdown(result):
    lines = ["# Current evidence conclusions", "",
             "> Synthetic demonstration. Current does not mean verified: review evidence gaps and conflicts.", ""]
    for row in result["current_claims"]:
        tag = "supported by listed evidence" if row["evidence_complete"] else "EVIDENCE GAP"
        lines.append(f"- **{row['claim_id']}**: {row['statement']} ({tag}; refs: {', '.join(row['evidence_ids']) or 'none'})")
    lines += ["", "## Evidence gaps"]
    for gap in result["evidence_gaps"]:
        lines.append(f"- {gap['claim_id']}: {gap['reason']}; missing: {', '.join(gap['missing_evidence_ids']) or 'none'}")
    if not result["evidence_gaps"]:
        lines.append("- None detected in cited identifiers (source authenticity not evaluated).")
    lines += ["", "## Potential conflicting current claims"]
    for conflict in result["potential_conflicts"]:
        lines.append(f"- {conflict['subject']}: {', '.join(conflict['current_claim_ids'])}")
    if not result["potential_conflicts"]:
        lines.append("- None detected by shared subject key.")
    lines += ["", "## Supersession history (retained, not current conclusions)"]
    for row in result["history"]:
        if row["status"] == "superseded":
            lines.append(f"- {row['claim_id']} → {row['superseded_by']}: {row['statement']}")
    if not any(row["status"] == "superseded" for row in result["history"]):
        lines.append("- None.")
    lines += ["", "## Correction records"]
    for row in result["corrections"]:
        lines.append(f"- {row['correction_id']}: {row['claim_id']} → {row['replacement_claim_id']}; reason: {row['reason']}")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--output", type=Path, default=Path("current_conclusions.md"))
    parser.add_argument("--json-output", type=Path)
    args = parser.parse_args()
    result = audit(read_csv(args.directory / "evidence.csv", REQUIRED_EVIDENCE),
                   read_csv(args.directory / "claims.csv", REQUIRED_CLAIMS),
                   read_csv(args.directory / "corrections.csv", REQUIRED_CORRECTIONS))
    args.output.write_text(render_markdown(result), encoding="utf-8")
    if args.json_output:
        args.json_output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
