import unittest
from pathlib import Path
from scripts.investigation_report import build_report,safe
SAMPLE=Path(__file__).resolve().parents[1]/'examples'/'synthetic_sim_auth_events.csv'
class ReportTests(unittest.TestCase):
    def test_counts(self):
        r=build_report(SAMPLE)
        self.assertIn('8 unique source-scoped events',r)
        self.assertIn('1 duplicate row(s) excluded',r)
        self.assertIn('2 SIM-anchor groups',r)
    def test_sources(self):
        r=build_report(SAMPLE)
        self.assertIn('| carrier-demo | 2 |',r)
        self.assertIn('| identity-demo | 6 |',r)
    def test_provenance(self):
        r=build_report(SAMPLE)
        self.assertIn('CAR-101',r)
        self.assertIn('ID-201',r)
    def test_chronology(self):
        r=build_report(SAMPLE)
        self.assertLess(r.index('ID-201'),r.index('CAR-101'))
    def test_other_account_not_in_findings(self):
        r=build_report(SAMPLE).split('## Grouped correlation findings')[1].split('## Evidence gaps')[0]
        self.assertNotIn('ID-205',r)
    def test_zero_window(self):
        self.assertIn('No SIM-anchor groups met',build_report(SAMPLE,0,0))
    def test_escape(self):
        self.assertEqual(safe('x|y\nz'),'x\\|y z')
    def test_invalid_window(self):
        with self.assertRaisesRegex(ValueError,'window'):
            build_report(SAMPLE,-1,1)
    def test_quality_section_embedded(self):
        r=build_report(SAMPLE)
        self.assertIn('## Automated evidence-quality assessment',r)
        self.assertIn('**Quality issues:** 7 across 9 input rows.',r)
        self.assertIn('duplicate_source_event_id',r)
        self.assertIn('authorization_unresolved',r)
    def test_quality_error_blocks_report(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'invalid.csv'
            p.write_text('event_id,timestamp,account,event_type,source,source_record_id\nS,2026-01-01T10:00:00,demo,sim_swap,carrier,CAR-1\n')
            with self.assertRaisesRegex(ValueError,'evidence quality check failed'):
                build_report(p)
if __name__=='__main__':
    unittest.main()
