import re

# Lexicon of common Romanized Hindi (Hinglish) words used in Indian social engineering
HINGLISH_KEYWORDS = {
    'aaj', 'abhi', 'karo', 'karein', 'hoga', 'hai', 'bhejo', 'jaega', 'jayega',
    'paise', 'rupaye', 'khata', 'turant', 'kya', 'nahi', 'dijiye', 'dijiye',
    'milega', 'jeeta', 'lottery', 'bhej', 'kisi', 'ko', 'mat', 'do', 'batao',
    'bhai', 'sir', 'madam', 'band', 'hoke', 'pe'
}

def detect_language(text: str) -> dict:
    """
    Lightweight heuristic-based language detector for Indian scam messages.
    Supports English, Hindi (Devanagari), Hinglish (Romanized Hindi),
    Bengali, Tamil, Telugu, Kannada, and Malayalam.
    
    Provides offline fallback when large ML NLP models are unavailable.
    """
    if not text or not isinstance(text, str):
        return {"language": "Unknown", "confidence": 0.0, "is_romanized": False}
    
    # 1. Script-based Unicode checks
    if re.search(r'[\u0900-\u097F]', text):
        return {"language": "Hindi (Devanagari)", "confidence": 0.95, "is_romanized": False}
    elif re.search(r'[\u0980-\u09FF]', text):
        return {"language": "Bengali", "confidence": 0.95, "is_romanized": False}
    elif re.search(r'[\u0B80-\u0BFF]', text):
        return {"language": "Tamil", "confidence": 0.95, "is_romanized": False}
    elif re.search(r'[\u0C00-\u0C7F]', text):
        return {"language": "Telugu", "confidence": 0.95, "is_romanized": False}
    elif re.search(r'[\u0C80-\u0CFF]', text):
        return {"language": "Kannada", "confidence": 0.95, "is_romanized": False}
    elif re.search(r'[\u0D00-\u0D7F]', text):
        return {"language": "Malayalam", "confidence": 0.95, "is_romanized": False}

    # 2. Hinglish (Romanized Hindi) keyword match ratio
    tokens = set(re.findall(r'\b[a-zA-Z]+\b', text.lower()))
    if not tokens:
        return {"language": "Unknown", "confidence": 0.3, "is_romanized": False}
        
    hinglish_matches = tokens.intersection(HINGLISH_KEYWORDS)
    hinglish_ratio = len(hinglish_matches) / max(1, len(tokens))
    
    if len(hinglish_matches) >= 2 or hinglish_ratio > 0.2:
        return {
            "language": "Hinglish (Romanized Hindi)",
            "confidence": min(0.9, 0.5 + hinglish_ratio),
            "is_romanized": True
        }
        
    # 3. Default Fallback to English
    return {"language": "English", "confidence": 0.85, "is_romanized": False}

if __name__ == "__main__":
    import sys
    if sys.stdout.encoding.lower() != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
        
    test_samples = [
        "Your bank account will be blocked today.",
        "आपका खाता आज बंद कर दिया जाएगा।",
        "Aapka bank account aaj band ho jayega OTP share karo turant.",
        "உங்கள் வங்கி கணக்கு முடக்கப்பட்டுள்ளது"
    ]
    print("--- Language Detector Test Output ---")
    for sample in test_samples:
        print(f"Text: '{sample[:40]}...' -> {detect_language(sample)}")
