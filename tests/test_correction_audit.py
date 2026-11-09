import unittest
from scripts.correction_audit import audit, render_markdown

EVIDENCE = [{"evidence_id": "EV-01", "description": "Fictional snapshot"},
            {"evidence_id": "EV-02", "description": "Fictional dated correction"}]
CLAIMS = [
    {"claim_id": "C-01", "subject": "device-association", "statement": "Association applies throughout the year", "evidence_ids": "EV-01"},
    {"claim_id": "C-02", "subject": "device-association", "statement": "Association documented for one date only", "evidence_ids": "EV-01;EV-02"},
]
CORRECTIONS = [{"correction_id": "R-01", "claim_id": "C-01", "replacement_claim_id": "C-02", "reason": "Interval not established"}]


class CorrectionAuditTests(unittest.TestCase):
    def test_superseded_not_current(self):
        result = audit(EVIDENCE, CLAIMS, CORRECTIONS)
        self.assertEqual([c["claim_id"] for c in result["current_claims"]], ["C-02"])
        self.assertEqual(result["history"][0]["superseded_by"], "C-02")

    def test_history_preserved(self):
        result = audit(EVIDENCE, CLAIMS, CORRECTIONS)
        self.assertEqual(len(result["history"]), 2)
        self.assertEqual(len(result["corrections"]), 1)

    def test_markdown_separates_history(self):
        report = render_markdown(audit(EVIDENCE, CLAIMS, CORRECTIONS))
        self.assertNotIn("**C-01**:", report.split("## Evidence gaps")[0])
        self.assertIn("C-01 → C-02", report)

    def test_missing_evidence(self):
        claims = [{"claim_id": "C-03", "subject": "", "statement": "Unsupported", "evidence_ids": "EV-99"}]
        result = audit(EVIDENCE, claims, [])
        self.assertEqual(result["evidence_gaps"][0]["missing_evidence_ids"], ["EV-99"])
        self.assertFalse(result["current_claims"][0]["evidence_complete"])

    def test_no_evidence(self):
        claims = [{"claim_id": "C-03", "subject": "", "statement": "No refs", "evidence_ids": ""}]
        self.assertEqual(audit(EVIDENCE, claims, [])["evidence_gaps"][0]["reason"], "no evidence cited")

    def test_competing_current_claims_flagged(self):
        self.assertEqual(audit(EVIDENCE, CLAIMS, [])["potential_conflicts"][0]["current_claim_ids"], ["C-01", "C-02"])

    def test_duplicate_evidence_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            audit(EVIDENCE + EVIDENCE[:1], CLAIMS, CORRECTIONS)

    def test_duplicate_claim_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            audit(EVIDENCE, CLAIMS + CLAIMS[:1], CORRECTIONS)

    def test_competing_replacements_rejected(self):
        extra = {"claim_id": "C-03", "subject": "", "statement": "Other", "evidence_ids": "EV-02"}
        second = {"correction_id": "R-02", "claim_id": "C-01", "replacement_claim_id": "C-03", "reason": "Other"}
        with self.assertRaisesRegex(ValueError, "multiple replacements"):
            audit(EVIDENCE, CLAIMS + [extra], CORRECTIONS + [second])

    def test_unknown_replacement_rejected(self):
        bad = [{"correction_id": "R-01", "claim_id": "C-01", "replacement_claim_id": "C-99", "reason": "Unknown"}]
        with self.assertRaisesRegex(ValueError, "replacement claim not found"):
            audit(EVIDENCE, CLAIMS, bad)

    def test_cycle_rejected(self):
        reverse = {"correction_id": "R-02", "claim_id": "C-02", "replacement_claim_id": "C-01", "reason": "Cycle"}
        with self.assertRaisesRegex(ValueError, "cycle"):
            audit(EVIDENCE, CLAIMS, CORRECTIONS + [reverse])


if __name__ == "__main__":
    unittest.main()
