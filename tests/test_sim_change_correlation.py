import tempfile
import unittest
from pathlib import Path
from scripts.sim_change_correlation import load_events, correlate, run, parse_timestamp

SAMPLE = Path(__file__).resolve().parents[1] / 'examples' / 'synthetic_sim_auth_events.csv'


class SimCorrelationTests(unittest.TestCase):
    def test_two_grouped_findings(self):
        result = run(SAMPLE)
        self.assertEqual(result['finding_count'], 2)
        self.assertEqual([f['related_count'] for f in result['findings']], [3, 1])

    def test_duplicate_record_not_double_counted(self):
        result = run(SAMPLE)
        self.assertEqual(result['duplicate_count'], 1)
        self.assertEqual(result['event_count'], 8)

    def test_before_after_offsets(self):
        finding = run(SAMPLE)['findings'][0]
        self.assertEqual([x['seconds_from_sim_event'] for x in finding['related_events']], [-900, 300, 18000])

    def test_cross_provider(self):
        self.assertTrue(all(f['cross_provider'] for f in run(SAMPLE)['findings']))

    def test_other_account_excluded(self):
        self.assertNotIn('A-005', [x['event_id'] for f in run(SAMPLE)['findings'] for x in f['related_events']])

    def test_outside_window_excluded(self):
        self.assertNotIn('A-004', [x['event_id'] for f in run(SAMPLE)['findings'] for x in f['related_events']])

    def test_custom_window(self):
        self.assertEqual([f['related_count'] for f in run(SAMPLE, 10, 10)['findings']], [1])

    def test_zero_window(self):
        self.assertEqual(run(SAMPLE, 0, 0)['finding_count'], 0)

    def test_timezone_naive_rejected(self):
        with self.assertRaisesRegex(ValueError, 'UTC offset'):
            parse_timestamp('2026-01-01T10:00:00')

    def test_invalid_window_rejected(self):
        with self.assertRaisesRegex(ValueError, 'window'):
            run(SAMPLE, -1, 10)

    def test_missing_required_column_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'bad.csv'
            p.write_text('event_id,timestamp\nX,2026-01-01T00:00:00Z\n')
            with self.assertRaisesRegex(ValueError, 'missing columns'):
                load_events(p)

    def test_distinct_providers_can_share_event_id(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'same-id.csv'
            p.write_text('event_id,timestamp,account,event_type,source,source_record_id\nX,2026-01-01T00:00:00Z,a,sim_swap,carrier,c1\nX,2026-01-01T00:01:00Z,a,login,identity,i1\n')
            events, duplicates = load_events(p)
            self.assertEqual((len(events), len(duplicates)), (2, 0))
            self.assertEqual(len(correlate(events)), 1)


if __name__ == '__main__':
    unittest.main()
