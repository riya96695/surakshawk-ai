# SuraksHawkAI NLP Scam Detection Benchmark Dataset

## Overview
This synthetic dataset contains 30+ curated samples representing common Indian digital payment fraud, social engineering scams, and legitimate banking/personal communications.

## Privacy & Safety Disclaimer
> **IMPORTANT**: All sample telephone numbers (`+919876543210`), bank account numbers (`XX1234`), UPI handles (`paytm@ybl`), URLs, and names in this dataset are strictly synthetic placeholders. No actual personal identifiable information (PII), live OTPs, or active bank credentials are stored or used.

## Schema Column Definitions
- `text`: Raw input message content
- `language`: Primary language (`English`, `Hindi`, `Hinglish`)
- `is_scam`: Binary label (`1` for scam/fraud, `0` for legitimate)
- `scam_type`: Primary scam classification category
- `urgency`: `1` if time panic creates urgency, else `0`
- `authority_impersonation`: `1` if impersonating Bank/Police/Govt, else `0`
- `financial_request`: `1` if requesting money/transfer/fee, else `0`
- `credential_request`: `1` if requesting OTP/PIN/CVV/Password, else `0`
- `threat`: `1` if threatening legal/account block action, else `0`
- `remote_access_request`: `1` if asking for AnyDesk/TeamViewer screen share, else `0`
- `suspicious_link`: `1` if containing unverified domain or APK link, else `0`
- `severity`: Ground-truth risk score decimal (0.0 to 1.0)
- `source_type`: Data acquisition channel (`SMS`, `WhatsApp`, `Chat`, `UPI_App`, `Call_Transcript`)
