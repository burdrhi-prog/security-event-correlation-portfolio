import tempfile
import unittest
from pathlib import Path
from scripts.evidence_quality import check
SAMPLE=Path(__file__).resolve().parents[1]/'examples'/'synthetic_sim_auth_events.csv'
class QualityTests(unittest.TestCase):
    def test_sample_duplicate(self):
        r=check(SAMPLE)
        self.assertEqual(r['input_rows'],9)
        self.assertEqual(sum(i['code']=='duplicate_source_event_id' for i in r['issues']),1)
    def test_naive_and_missing_authorization(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'a.csv'
            p.write_text('event_id,timestamp,account,event_type,source,source_record_id,authorization_status\nA,2026-01-01T00:00:00,demo,login,alpha,ref,\n')
            codes=[i['code'] for i in check(p)['issues']]
            self.assertIn('missing_timezone',codes)
            self.assertIn('authorization_unresolved',codes)
    def test_invalid_timestamp(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'a.csv'
            p.write_text('event_id,timestamp,account,event_type,source,source_record_id\nA,invalid,demo,login,alpha,ref\n')
            self.assertIn('invalid_timestamp',[i['code'] for i in check(p)['issues']])
    def test_missing_required_value(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'a.csv'
            p.write_text('event_id,timestamp,account,event_type,source,source_record_id\nA,2026-01-01T00:00:00Z,demo,login,alpha,\n')
            self.assertIn('missing_required_value',[i['code'] for i in check(p)['issues']])
    def test_missing_column(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'a.csv'
            p.write_text('event_id,timestamp\nA,2026-01-01T00:00:00Z\n')
            with self.assertRaisesRegex(ValueError,'missing required columns'):
                check(p)
    def test_same_id_different_source(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'a.csv'
            p.write_text('event_id,timestamp,account,event_type,source,source_record_id\nA,2026-01-01T00:00:00Z,demo,login,alpha,ref\nA,2026-01-01T00:01:00Z,demo,login,beta,ref\n')
            self.assertFalse(any(i['code']=='duplicate_source_event_id' for i in check(p)['issues']))
    def test_mixed_offsets(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'a.csv'
            p.write_text('event_id,timestamp,account,event_type,source,source_record_id\nA,2026-01-01T00:00:00Z,demo,login,alpha,ref1\nB,2026-01-01T00:00:00-07:00,demo,login,alpha,ref2\n')
            self.assertIn('mixed_source_offsets',[i['code'] for i in check(p)['issues']])
if __name__=='__main__':
    unittest.main()
