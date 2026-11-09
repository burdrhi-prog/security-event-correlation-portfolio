import json
import tempfile
import unittest
from pathlib import Path
from scripts.correlate_events import correlate, load_events, run

SAMPLE = Path(__file__).resolve().parents[1] / 'examples' / 'synthetic_events.csv'


class CorrelationTests(unittest.TestCase):
    def test_example_and_provenance(self):
        result = run(SAMPLE)
        self.assertEqual((result['event_count'], result['finding_count']), (5, 1))
        finding = result['findings'][0]
        self.assertEqual(finding['event_ids'], ['EV-001', 'EV-002'])
        self.assertEqual(finding['gap_seconds'], 480)
        self.assertTrue(finding['cross_provider'])
        self.assertEqual(finding['source_record_ids'], ['ALPHA-101', 'BETA-201'])

    def test_timezone_required(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'bad.csv'
            path.write_text('event_id,timestamp,account,event_type,client_id,source\nX,2026-01-15T09:00:00,a,login,c,s\n')
            with self.assertRaisesRegex(ValueError, 'timezone'):
                load_events(path)

    def test_same_client_not_flagged(self):
        events, _ = load_events(SAMPLE)
        self.assertEqual(correlate([events[0], events[2]]), [])

    def test_different_accounts_not_flagged(self):
        events, _ = load_events(SAMPLE)
        self.assertEqual(correlate([events[1], events[3]]), [])

    def test_window_configurable(self):
        self.assertEqual(run(SAMPLE, 5)['finding_count'], 0)
        with self.assertRaisesRegex(ValueError, 'window_minutes'):
            run(SAMPLE, 0)

    def test_duplicate_event_ids_deduplicated(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'dup.csv'
            original = SAMPLE.read_text()
            path.write_text(original + original.splitlines()[1] + '\n')
            result = run(path)
            self.assertEqual(result['event_count'], 5)
            self.assertEqual(result['duplicate_event_ids'], ['EV-001'])

    def test_json_input(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'events.json'
            path.write_text(json.dumps([{
                'event_id': 'J1', 'timestamp': '2026-01-01T00:00:00Z',
                'account': 'demo', 'event_type': 'login', 'client_id': 'one', 'source': 'alpha',
            }]))
            self.assertEqual(run(path)['event_count'], 1)

    def test_bad_json_structure(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'bad.json'
            path.write_text('{"not": "an array"}')
            with self.assertRaisesRegex(ValueError, 'array'):
                load_events(path)


if __name__ == '__main__':
    unittest.main()
