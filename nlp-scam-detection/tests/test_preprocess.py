import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.preprocess import preprocess_text

class TestPreprocess(unittest.TestCase):
    def test_preprocess_entity_extraction(self):
        sample = "URGENT: SBI Bank account update at http://sbi-verify.apk or pay Rs 500 to paytm@ybl call 9876543210 O.T.P."
        res = preprocess_text(sample)
        
        self.assertIn("http://sbi-verify.apk", res["entities"]["urls"])
        self.assertIn("paytm@ybl", res["entities"]["upi_ids"])
        self.assertIn("Rs 500", res["entities"]["currency_amounts"])
        self.assertIn("otp", res["cleaned_text"])

    def test_preprocess_empty_input(self):
        res = preprocess_text("")
        self.assertEqual(res["cleaned_text"], "")
        self.assertEqual(res["entities"]["urls"], [])

if __name__ == "__main__":
    unittest.main()
