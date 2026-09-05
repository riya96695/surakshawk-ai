# SuraksHawkAI — NLP & Scam Detection Engine (Member 2 Module)

The **SuraksHawkAI NLP Scam Detection Engine** is a B2B cybersecurity microservice designed for Indian banks, UPI applications (GPay, PhonePe, Paytm), and financial platforms.

It analyzes incoming SMS, chat logs, WhatsApp messages, emails, and speech transcripts to detect social-engineering vectors, payment fraud triggers, and credential theft threats.

---

## 🏗️ Architecture Overview & Pipeline Integration

```
[ Input Signals ] (SMS / Chat / Speech Transcripts)
        ↓
[ services/preprocess.py ] (Unicode Normalization & Entity Extraction: URLs, UPI IDs, Phones)
        ↓
[ services/language_detector.py ] (Fallback Identification: English, Hindi, Hinglish)
        ↓
[ services/pattern_detector.py ] (Indian Scam Taxonomy Rule Engine)
        ↓
[ services/risk_scorer.py ] (Explainable Weighted Risk & Advisory Action Calculation)
        ↓
[ services/scam_detector.py ] (Master Payload Orchestration)
        ↓
[ app.py (FastAPI REST Server) ] ──▶ Payload sent to Member 3 Risk Engine
```

> **🛡️ Safety & Policy Constraint**: As specified in the SuraksHawkAI Strategy, this module **never freezes accounts or blocks payments directly**. It produces explainable, probabilistic risk indicators (`scam_score`, `confidence`, `risk_level`, `labels`, `reasons`, `recommended_action`) for downstream policy engine decision support.

---

## ⚡ Quickstart Guide

### 1. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 2. Run the FastAPI Service
```powershell
python -m uvicorn app:app --reload --port 8000
```

### 3. Test API Endpoint via PowerShell / Curl
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/detect-scam" -Method Post -ContentType "application/json" -Body '{"text": "URGENT: Your SBI account is blocked today due to pending KYC. Click http://sbi-verify.apk to share OTP immediately."}' | ConvertTo-Json
```

### 4. Run Automated Unit Tests
```powershell
python -m unittest discover tests
```

---

## 📑 API Specification

### `POST /detect-scam`
#### Sample Request Body:
```json
{
  "text": "Aapka bank account aaj band ho jayega. Share OTP immediately."
}
```

#### Sample Response Body:
```json
{
  "text": "Aapka bank account aaj band ho jayega. Share OTP immediately.",
  "cleaned_text": "aapka bank account aaj band ho jayega. share otp immediately.",
  "language": "Hinglish (Romanized Hindi)",
  "scam_score": 0.95,
  "confidence": 0.85,
  "risk_level": "critical",
  "labels": [
    "credential_request",
    "threat",
    "authority_impersonation",
    "urgency"
  ],
  "reasons": [
    "[CREDENTIAL_REQUEST]: Requests sensitive authentication credentials (OTP, PIN, CVV, Passwords).",
    "[THREAT]: Employs coercion, legal threats, or account blocking intimidation.",
    "[AUTHORITY_IMPERSONATION]: Impersonates trusted entities like banks, police, RBI, or government departments.",
    "[URGENCY]: Creates artificial time scarcity to impede logical thinking."
  ],
  "recommended_action": "escalate_to_fraud_team",
  "model_version": "surakshawk-nlp-v1.0-hybrid"
}
```
