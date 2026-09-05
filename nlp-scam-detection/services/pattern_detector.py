import re

# Comprehensive Indian Social Engineering Scam Taxonomy Rules
INDIAN_SCAM_TAXONOMY = {
    "credential_request": {
        "severity": 1.0,
        "explanation": "Requests sensitive authentication credentials (OTP, PIN, CVV, Passwords).",
        "patterns": [
            r"\b(?:share|tell|send|enter|provide|verify)\b.*\b(?:otp|one time password|pin|cvv|password|passcode)\b",
            r"\b(?:otp|pin|cvv)\b.*\b(?:bhejo|share karo|dijiye|batao)\b",
            r"\b(?:aadhaar|pan)\s?(?:number|card|details)\b",
            r"\botp\s?batao\b"
        ]
    },
    "remote_access_request": {
        "severity": 0.95,
        "explanation": "Requests user to install remote desktop control software or share screen.",
        "patterns": [
            r"\b(?:install|download)\b.*\b(?:anydesk|teamviewer|quicksupport|rustdesk|screen share)\b",
            r"\b(?:anydesk|teamviewer|quicksupport)\b.*\b(?:app|apk|install)\b",
            r"\b(?:screen\s?share|remote\s?access)\b"
        ]
    },
    "threat": {
        "severity": 0.9,
        "explanation": "Employs coercion, legal threats, or account blocking intimidation.",
        "patterns": [
            r"\b(?:account|card|sim|service)\b.*\b(?:blocked|suspended|deactivated|terminated|closed)\b",
            r"\b(?:account|sim)\b.*\b(?:band\s?ho|block\s?ho|band\s?ho\s?jayega)\b",
            r"\b(?:legal\s?action|police|arrest|cbi|court|income\s?tax|electricity\s?cut)\b",
            r"\b(?:bhejo|otherwise|varupil)\b.*\b(?:arrest|jail|case)\b"
        ]
    },
    "kyc_scam": {
        "severity": 0.85,
        "explanation": "Uses fake KYC verification or document expiration panic.",
        "patterns": [
            r"\b(?:update|complete|verify)\b.*\b(?:kyc|aadhaar|pan|bank account)\b",
            r"\b(?:kyc)\b.*\b(?:expire|pending|update|mandatory)\b",
            r"\b(?:kyc\s?update\s?karo|kyc\s?pending\s?hai)\b"
        ]
    },
    "authority_impersonation": {
        "severity": 0.8,
        "explanation": "Impersonates trusted entities like banks, police, RBI, or government departments.",
        "patterns": [
            r"\b(?:from\s?your\s?bank|sbi|hdfc|icici|axis|rbi|police|customs|income\s?tax|telecom|trai)\b",
            r"\b(?:bank\s?officer|customer\s?care|manager|police\s?officer)\b",
            r"\b(?:sbi\s?se|bank\s?se|police\s?se)\b"
        ]
    },
    "prize_scam": {
        "severity": 0.85,
        "explanation": "Detected prize/lottery claim language.",
        "patterns": [
            r"\b(?:congratulations|congrats|lucky\s?winner|winner)\b",
            r"\b(?:you\s?won|won|jeet\s?gaye)\b.*\b(?:prize|lottery|lakh|cash|reward|iphone|₹|rs)\b",
            r"\b(?:claim\s?your\s?prize|claim\s?reward|claim\s?now|prize\s?claim)\b"
        ]
    },
    "financial_lure": {
        "severity": 0.8,
        "explanation": "Detected monetary reward lure or suspicious payment claim.",
        "patterns": [
            r"\b(?:won|got|received|claim)\b.*\b(?:₹|rs\.?|inr)\s?\d+(?:,\d+)*\b",
            r"\b(?:cashback|guaranteed\s?return|double\s?money|free\s?recharge)\b"
        ]
    },
    "link_request": {
        "severity": 0.8,
        "explanation": "Detected call-to-action link prompt or suspicious URL request.",
        "patterns": [
            r"\b(?:click|open|visit|follow)\b.*\b(?:this\s?link|the\s?link|link|here|below|url)\b",
            r"\b(?:link\s?kholo|link\s?pe\s?click\s?karo)\b"
        ]
    },
    "suspicious_link": {
        "severity": 0.85,
        "explanation": "Contains unverified domain link or executable APK payload file.",
        "patterns": [
            r"\bhttps?://[^\s]+\.(?:apk|xyz|top|site|app|link)\b",
            r"\bbit\.ly/[^\s]+|tinyurl\.com/[^\s]+\b",
            r"\b[a-zA-Z0-9-]+\.(?:apk|xyz|site)\b"
        ]
    },
    "financial_request": {
        "severity": 0.75,
        "explanation": "Demands immediate payment, UPI collect, or processing fee transfer.",
        "patterns": [
            r"\b(?:send|transfer|pay|deposit)\b.*\b(?:money|rs|inr|amount|fee|tax)\b",
            r"\b(?:processing\s?fee|registration\s?fee|advance\s?charge)\b",
            r"\b(?:upi\s?pin|upi\s?collect|gpay|phonepe|paytm)\b.*\b(?:pay|send)\b",
            r"\b(?:paise\s?bhejo|transfer\s?karo)\b"
        ]
    },
    "urgency": {
        "severity": 0.7,
        "explanation": "Creates artificial time scarcity to impede logical thinking.",
        "patterns": [
            r"\b(?:immediately|urgent|today|within\s?\d+\s?(?:min|mins|minutes|hours)|last\s?date)\b",
            r"\b(?:turant|aaj\s?hi|abhi)\b"
        ]
    },
    "fake_job_investment": {
        "severity": 0.7,
        "explanation": "Offers unrealistic part-time earning or guaranteed investment returns.",
        "patterns": [
            r"\b(?:part-time|work\s?from\s?home)\b.*\b(?:earn|daily|income|salary)\b",
            r"\b(?:investment|guaranteed\s?return|double\s?money)\b",
            r"\b(?:ghar\s?baithe\s?paise\s?kamaye)\b"
        ]
    }
}

def detect_scam_patterns(text: str, entities: dict) -> dict:
    """
    Scans normalized text against Indian Scam Taxonomy regex rules and entity signals.
    Returns matched categories, severity scores, matched patterns, and explanation reasons.
    """
    matched_labels = []
    matched_patterns = []
    reasons = []
    category_severities = []
    
    text_lower = text.lower()
    
    # 1. Rule-based Regex Matching
    for label, info in INDIAN_SCAM_TAXONOMY.items():
        for pattern in info["patterns"]:
            match = re.search(pattern, text_lower, flags=re.IGNORECASE)
            if match:
                matched_str = match.group(0)
                matched_labels.append(label)
                matched_patterns.append(matched_str)
                reasons.append(f"[{label.upper()}]: {info['explanation']} (Matched: '{matched_str}')")
                category_severities.append(info["severity"])
                break  # Matched one pattern for this label, move to next label

    # 2. Entity-based Pattern Augmentation
    if entities.get("currency_amounts"):
        for amt in entities["currency_amounts"]:
            if any(w in text_lower for w in ["won", "claim", "prize", "lottery", "congratulations"]):
                if "financial_lure" not in matched_labels:
                    matched_labels.append("financial_lure")
                    matched_patterns.append(amt)
                    reasons.append(f"[FINANCIAL_LURE]: Detected financial reward amount '{amt}'")
                    category_severities.append(0.80)

    if entities.get("urls"):
        for url in entities["urls"]:
            if ".apk" in url.lower() or any(x in url.lower() for x in [".xyz", ".top", "bit.ly", "tinyurl"]):
                if "suspicious_link" not in matched_labels:
                    matched_labels.append("suspicious_link")
                    matched_patterns.append(url)
                    reasons.append(f"[SUSPICIOUS_LINK]: Found potentially untrusted URL or APK payload '{url}'")
                    category_severities.append(0.85)

    return {
        "labels": matched_labels,
        "matched_patterns": matched_patterns,
        "reasons": reasons,
        "category_severities": category_severities
    }

if __name__ == "__main__":
    import sys
    if sys.stdout.encoding.lower() != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')

    sample = "Congratulations! You won ₹50,000. Click this link immediately to claim your prize."
    sample_entities = {"urls": [], "upi_ids": [], "phone_numbers": [], "currency_amounts": ["₹50,000"]}
    res = detect_scam_patterns(sample, sample_entities)
    print("--- Pattern Detector Test Output ---")
    print("Labels:", res["labels"])
    print("Matched Patterns:", res["matched_patterns"])
    print("Reasons:", res["reasons"])
