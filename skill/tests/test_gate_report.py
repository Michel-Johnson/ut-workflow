"""Behavior tests for rule aggregation; not a test of agent decision quality."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/gate_report.py'
spec = importlib.util.spec_from_file_location('gate_report', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class GateTests(unittest.TestCase):
    def run_gate(self, required, checks):
        return module.summarize({'required_rules': required, 'checks': checks})

    def test_evidence_pass_is_ready_for_selected_scope(self):
        result = self.run_gate(['UT-14'], [{'rule_id':'UT-14','status':'PASS','evidence':'run.log: found 3; exit 0'}])
        self.assertEqual(result['gate'], 'READY')
        self.assertEqual(result['evidence_authenticity'], 'not_verified')

    def test_missing_required_check_blocks(self):
        self.assertEqual(self.run_gate(['UT-14'], [])['gate'], 'BLOCKED')

    def test_failure_remains_not_ready_even_with_unknown(self):
        result = self.run_gate(['UT-14','UT-19'], [{'rule_id':'UT-14','status':'FAIL','evidence':'exit 1'}])
        self.assertEqual(result['gate'], 'NOT_READY')
        self.assertEqual(result['unknown_rules'], ['UT-19'])

    def test_unknown_is_not_pass(self):
        self.assertEqual(self.run_gate(['UT-14'], [{'rule_id':'UT-14','status':'UNKNOWN','reason':'tool unavailable'}])['gate'], 'BLOCKED')

    def test_pass_requires_evidence(self):
        with self.assertRaises(ValueError):
            self.run_gate(['UT-14'], [{'rule_id':'UT-14','status':'PASS'}])

    def test_not_applicable_requires_reason(self):
        with self.assertRaises(ValueError):
            self.run_gate(['UT-18'], [{'rule_id':'UT-18','status':'NOT_APPLICABLE'}])

    def test_empty_requirement_set_is_not_ready(self):
        with self.assertRaises(ValueError): self.run_gate([], [])

    def test_all_not_applicable_is_not_automatic_ready(self):
        self.assertEqual(self.run_gate(['UT-18'], [{'rule_id':'UT-18','status':'NOT_APPLICABLE','reason':'no coverage requirement'}])['gate'], 'BLOCKED')

    def test_omitted_scope_cannot_have_hidden_extra_pass(self):
        with self.assertRaises(ValueError):
            self.run_gate(['UT-14'], [{'rule_id':'UT-19','status':'PASS','evidence':'coverage 1.0'}])

    def test_duplicate_checks_rejected(self):
        row={'rule_id':'UT-14','status':'PASS','evidence':'run.log'}
        with self.assertRaises(ValueError): self.run_gate(['UT-14'], [row,row])

    def test_waiver_cannot_automatically_approve(self):
        with self.assertRaises(ValueError):
            module.summarize({'required_rules':['UT-14'],'checks':[], 'exceptions':[{'approved':True}]})

    def test_cli_exit_codes_and_json(self):
        cases=[
            ({'required_rules':['UT-14'],'checks':[{'rule_id':'UT-14','status':'PASS','evidence':'log'}]},0,'READY'),
            ({'required_rules':['UT-14'],'checks':[{'rule_id':'UT-14','status':'FAIL','evidence':'log'}]},1,'NOT_READY'),
            ({'required_rules':['UT-14'],'checks':[]},2,'BLOCKED'),
            ({'required_rules':[],'checks':[]},3,'INVALID')]
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'input.json'
            for value,code,gate in cases:
                with self.subTest(gate=gate):
                    p.write_text(json.dumps(value))
                    run=subprocess.run([sys.executable,str(SCRIPT),str(p)],capture_output=True,text=True)
                    self.assertEqual(run.returncode,code)
                    self.assertEqual(json.loads(run.stdout)['gate'],gate)
            p.write_text('{"required_rules":[],"required_rules":["UT-14"],"checks":[]}')
            run=subprocess.run([sys.executable,str(SCRIPT),str(p)],capture_output=True,text=True)
            self.assertEqual(run.returncode,3)
            self.assertIn('duplicate JSON key',json.loads(run.stdout)['error'])

if __name__=='__main__': unittest.main(verbosity=2)
