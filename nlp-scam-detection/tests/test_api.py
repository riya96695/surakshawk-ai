import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

class TestAPIEndpoints(unittest.TestCase):
    def test_home_endpoint(self):
        response = client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "running")

    def test_health_endpoint(self):
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "healthy")

    def test_detect_scam_endpoint(self):
        payload = {"text": "URGENT: Your SBI bank account is blocked today. Share OTP immediately."}
        response = client.post("/detect-scam", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("scam_score", data)
        self.assertIn("risk_level", data)
        self.assertIn("labels", data)
        self.assertIn("reasons", data)

if __name__ == "__main__":
    unittest.main()
