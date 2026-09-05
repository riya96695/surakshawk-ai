"""
SuraksHawkAI - Master NLP Scam Detection Service
Orchestrates text preprocessing, language detection, Indian scam taxonomy rules,
weighted severity risk calculation, and explainable payload formatting.
"""

import sys
import os

# Ensure parent directory is in sys.path for direct script execution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.preprocess import preprocess_text
from services.language_detector import detect_language
from services.pattern_detector import detect_scam_patterns
from services.risk_scorer import calculate_risk_score

MODEL_VERSION = "surakshawk-nlp-v1.0-hybrid"

def detect_scam(text: str) -> dict:
    """
    Analyzes an input message (SMS, WhatsApp, Chat, Speech transcript)
    and returns a structured explainable risk payload for SuraksHawkAI Risk Engine.
    
    Args:
        text (str): Raw input message
        
    Returns:
        dict: Complete explainable risk payload
    """
    if not text or not isinstance(text, str):
        return {
            "text": text or "",
            "cleaned_text": "",
            "language": "Unknown",
            "scam_score": 0.0,
            "confidence": 1.0,
            "risk_level": "low",
            "labels": [],
            "reasons": ["Empty or invalid message string provided."],
            "matched_patterns": [],
            "entities": {"urls": [], "upi_ids": [], "phone_numbers": [], "currency_amounts": []},
            "recommended_action": "allow",
            "model_version": MODEL_VERSION
        }
        
    original_text = text
    
    # 1. Preprocessing & Entity Extraction
    preprocess_res = preprocess_text(original_text)
    cleaned_text = preprocess_res["cleaned_text"]
    entities = preprocess_res["entities"]
    
    # 2. Language Detection Fallback
    lang_res = detect_language(original_text)
    
    # 3. Pattern Matching against Indian Scam Taxonomy
    pattern_res = detect_scam_patterns(cleaned_text, entities)
    
    # 4. Risk Scoring & Advisory Recommended Action
    risk_res = calculate_risk_score(
        labels=pattern_res["labels"],
        category_severities=pattern_res["category_severities"],
        entities=entities,
        language_info=lang_res
    )
    
    # 5. Format Explainable Response Payload
    return {
        "text": original_text,
        "cleaned_text": cleaned_text,
        "language": lang_res["language"],
        "scam_score": risk_res["scam_score"],
        "confidence": risk_res["confidence"],
        "risk_level": risk_res["risk_level"],
        "labels": pattern_res["labels"],
        "reasons": pattern_res["reasons"],
        "matched_patterns": pattern_res["matched_patterns"],
        "entities": entities,
        "recommended_action": risk_res["recommended_action"],
        "model_version": MODEL_VERSION
    }

if __name__ == "__main__":
    import sys
    if sys.stdout.encoding.lower() != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')

    sample_scam = "URGENT: Your SBI account is blocked today due to pending KYC. Click http://sbi-verify.apk to share OTP immediately."
    result = detect_scam(sample_scam)
    print("--- Master Scam Detector Test Output ---")
    print(f"Text: '{result['text']}'")
    print(f"Language: {result['language']}")
    print(f"Scam Score: {result['scam_score']} | Confidence: {result['confidence']} | Risk Level: {result['risk_level']}")
    print(f"Labels: {result['labels']}")
    print(f"Recommended Action: {result['recommended_action']}")
    print(f"Reasons: {result['reasons']}")