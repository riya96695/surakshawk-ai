import math

def calculate_risk_score(labels: list, category_severities: list, entities: dict, language_info: dict) -> dict:
    """
    Computes an explainable scam_score (0.0 - 1.0), confidence metric, risk_level,
    and advisory recommended action for downstream Risk Engine consumption.
    
    Formula design:
    - Uses highest severity category as base anchor.
    - Diminishing returns formula for multiple compound scam indicators.
    - Boosts score for high-risk combinations (Credential theft, Prize lures + Link prompts).
    """
    if not labels or not category_severities:
        return {
            "scam_score": 0.0,
            "confidence": 0.95,
            "risk_level": "low",
            "recommended_action": "allow"
        }
        
    # Sort severities descending
    sorted_severities = sorted(category_severities, reverse=True)
    max_sev = sorted_severities[0]
    remaining_sum = sum(sorted_severities[1:])
    
    # 1. Base Score calculation with diminishing returns
    # False-Positive Mitigation:
    # If ONLY authority_impersonation or financial_request is present without threats/credentials/urgency/links,
    # dampen the score as it is likely a legitimate transactional notification (e.g. "Rs 500 debited at SBI ATM").
    coercive_signals = {"credential_request", "threat", "urgency", "kyc_scam", "suspicious_link", "remote_access_request", "fake_lottery_reward", "prize_scam", "financial_lure", "link_request", "fake_job_investment"}
    has_coercion = any(lbl in coercive_signals for lbl in labels)
    
    if not has_coercion:
        # Standalone bank name or financial reference in ordinary notification
        score = min(0.25, max_sev * 0.25)
    else:
        score = max_sev + (1.0 - max_sev) * (1.0 - math.exp(-0.4 * remaining_sum))
    
    # 2. Critical Threat & Lure Combo Boosts
    # Combo A: Prize / Lottery scam + Financial Lure + Link Prompt + Urgency
    if ("prize_scam" in labels or "fake_lottery_reward" in labels) and ("link_request" in labels or "suspicious_link" in labels) and "urgency" in labels:
        score = 0.85

    # Combo B: OTP/Credential request combined with Threat, Urgency, or Impersonation
    if "credential_request" in labels and any(x in labels for x in ["threat", "urgency", "authority_impersonation", "kyc_scam"]):
        score = max(score, 0.85)
        
    # Combo C: Remote access request combined with financial request or bank impersonation
    if "remote_access_request" in labels and any(x in labels for x in ["financial_request", "authority_impersonation"]):
        score = max(score, 0.95)
        
    # Combo D: Unverified APK link payload present
    if any(".apk" in str(u).lower() for u in entities.get("urls", [])):
        score = min(1.0, score + 0.10)
        
    scam_score = round(min(1.0, max(0.0, score)), 2)
    
    # 3. Calculate Signal Confidence
    match_count = len(labels)
    lang_conf = language_info.get("confidence", 0.85)
    
    entity_bonus = 0.05 if (entities.get("urls") or entities.get("upi_ids") or entities.get("currency_amounts")) else 0.0
    base_conf = 0.70 + (0.05 * min(4, match_count)) + entity_bonus
    confidence = round(min(0.98, base_conf * lang_conf), 2)
    
    # 4. Map Risk Level & Advisory Recommended Action
    if scam_score >= 0.90:
        risk_level = "critical"
        recommended_action = "escalate_to_fraud_team"
    elif scam_score >= 0.60:
        risk_level = "high"
        recommended_action = "step_up_warning" if scam_score < 0.80 else "step_up_confirmation"
    elif scam_score >= 0.30:
        risk_level = "medium"
        recommended_action = "show_warning"
    else:
        risk_level = "low"
        recommended_action = "allow"
        
    return {
        "scam_score": scam_score,
        "confidence": confidence,
        "risk_level": risk_level,
        "recommended_action": recommended_action
    }

if __name__ == "__main__":
    test_labels = ["prize_scam", "financial_lure", "link_request", "urgency"]
    test_sevs = [0.85, 0.8, 0.8, 0.7]
    test_entities = {"currency_amounts": ["₹50,000"]}
    test_lang = {"language": "English", "confidence": 0.95}
    
    res = calculate_risk_score(test_labels, test_sevs, test_entities, test_lang)
    print("--- Risk Scorer Test Output ---")
    print("Calculated Payload:", res)
