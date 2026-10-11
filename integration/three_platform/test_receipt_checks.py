import json, unittest
from pathlib import Path
from receipt_checks import load_and_check, check_receipt
class ReceiptTests(unittest.TestCase):
  def test_fixtures(self): self.assertEqual(load_and_check(),{'dev':6,'heldout':4,'adversarial':2})
  def test_unexecuted_template(self):
    d=json.loads((Path(__file__).parent/'sample_integration_receipt.json').read_text())
    self.assertTrue(check_receipt(d))
  def test_prevent_false_e2e_pass(self):
    d=json.loads((Path(__file__).parent/'sample_integration_receipt.json').read_text())
    d['status']='PASS_E2E'
    with self.assertRaises(AssertionError): check_receipt(d)
  def test_prevent_wrong_project(self):
    d=json.loads((Path(__file__).parent/'sample_integration_receipt.json').read_text())
    d['project_id']='not_official'
    with self.assertRaises(AssertionError): check_receipt(d)
  def test_prevent_nonfixture_case(self):
    d=json.loads((Path(__file__).parent/'sample_integration_receipt.json').read_text())
    d['case_id']='RDF-SYN-999'
    with self.assertRaises(AssertionError): check_receipt(d)
if __name__=='__main__': unittest.main(verbosity=2)
