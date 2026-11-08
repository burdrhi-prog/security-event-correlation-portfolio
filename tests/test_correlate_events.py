import tempfile
import unittest
from pathlib import Path
from scripts.correlate_events import correlate, load_events, run


class CorrelationTests(unittest.TestCase):
    def test_example_has_one_review_signal(self):
        result = run("examples/synthetic_events.csv")
        self.assertEqual(result["event_count"], 5)
        self.assertEqual(result["finding_count"], 1)
        self.assertEqual(result["findings"][0]["event_ids"], ["EV-001", "EV-002"])

    def test_missing_timezone_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "bad.csv"
            path.write_text(
                "event_id,timestamp,account,event_type,client_id,source\n"
                "X,2026-01-15T09:00:00,a,login,c,s\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "timezone"):
                load_events(path)

    def test_same_client_not_flagged(self):
        rows = load_events("examples/synthetic_events.csv")
        self.assertEqual(correlate([rows[0], rows[2]]), [])


if __name__ == "__main__":
    unittest.main()
