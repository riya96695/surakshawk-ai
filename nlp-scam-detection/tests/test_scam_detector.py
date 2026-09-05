import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.scam_detector import detect_scam

class TestScamDetector(unittest.TestCase):
    def test_bank_otp_scam(self):
        """TEST 1 - Bank OTP Scam"""
        sample = "Your SBI bank account is blocked. Share OTP immediately to verify KYC"
        res = detect_scam(sample)
        
        self.assertGreaterEqual(res["scam_score"], 0.80)
        self.assertIn("credential_request", res["labels"])
        self.assertIn("urgency", res["labels"])

    def test_prize_lottery_scam(self):
        """TEST 2 - Prize Scam"""
        sample = "Congratulations! You won ₹50,000. Click this link immediately to claim your prize."
        res = detect_scam(sample)
        
        self.assertGreaterEqual(res["scam_score"], 0.80)
        self.assertEqual(res["risk_level"], "high")
        self.assertIn("prize_scam", res["labels"])
        self.assertIn("financial_lure", res["labels"])
        self.assertIn("link_request", res["labels"])
        self.assertIn("urgency", res["labels"])

    def test_normal_message(self):
        """TEST 3 - Normal Message"""
        sample = "Hi, how are you? Let's meet tomorrow."
        res = detect_scam(sample)
        
        self.assertEqual(res["scam_score"], 0.0)
        self.assertEqual(res["risk_level"], "low")
        self.assertEqual(res["labels"], [])
        self.assertEqual(res["recommended_action"], "allow")

    def test_legitimate_bank_transaction(self):
        sample = "Rs 500 debited from A/C XX1234 on 04-Sep-26 at SBI ATM. Available balance Rs 12500."
        res = detect_scam(sample)
        
        self.assertLess(res["scam_score"], 0.30)
        self.assertEqual(res["risk_level"], "low")

    def test_hinglish_scam_detection(self):
        sample = "Aapka bank account aaj band ho jayega OTP share karo turant."
        res = detect_scam(sample)
        
        self.assertGreaterEqual(res["scam_score"], 0.70)
        self.assertIn("Hinglish", res["language"])

if __name__ == "__main__":
    unittest.main()
