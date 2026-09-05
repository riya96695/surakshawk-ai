import re
import unicodedata

# Common obfuscation replacements (e.g. @ -> a, 0 -> o, $ -> s)
OBFUSCATION_MAP = {
    '@': 'a',
    '0': 'o',
    '$': 's',
    '1': 'i',
    '!': 'i',
    '3': 'e'
}

# Regex patterns for Indian financial & communication entities
URL_PATTERN = r'https?://[^\s]+|www\.[^\s]+|[a-zA-Z0-9-]+\.(?:com|in|org|net|info|co|xyz|top|app|apk|link|site)/[^\s]*'
UPI_PATTERN = r'[a-zA-Z0-9.\-_]+@[a-zA-Z0-9]+'
PHONE_PATTERN = r'(?:\+91[\-\s]?)?[6-9]\d{9}'
CURRENCY_PATTERN = r'(?:₹|rs\.?|inr)\s?\d+(?:,\d+)*(?:\.\d+)?'

def deobfuscate_keywords(text: str) -> str:
    """
    Normalizes spaced-out or symbol-obfuscated scam keywords.
    Example: 'O T P' -> 'otp', 'K-Y-C' -> 'kyc', 'A n y D e s k' -> 'anydesk'
    """
    # Remove dots/hyphens between single characters (e.g., O.T.P -> OTP, K-Y-C -> KYC)
    text = re.sub(r'(?<=\b[a-zA-Z0-9])[\.\-\_](?=[a-zA-Z0-9]\b)', '', text)
    
    # Collapse spaced single letters (e.g., 'O T P' -> 'OTP', 'P I N' -> 'PIN')
    text = re.sub(r'\b([a-zA-Z])\s+([a-zA-Z])\s+([a-zA-Z])\b', r'\1\2\3', text)
    text = re.sub(r'\b([a-zA-Z])\s+([a-zA-Z])\b', r'\1\2', text)
    
    return text

def preprocess_text(text: str) -> dict:
    """
    Comprehensive text preprocessing pipeline for Indian NLP scam detection.
    Preserves critical entities (URLs, UPI IDs, Phone Numbers, Amounts)
    while normalizing unicode, whitespace, and obfuscated text.
    
    Returns a dictionary with raw text, normalized text, and extracted entities.
    """
    if not text or not isinstance(text, str):
        return {
            "cleaned_text": "",
            "normalized_tokens": "",
            "entities": {
                "urls": [],
                "upi_ids": [],
                "phone_numbers": [],
                "currency_amounts": []
            }
        }
    
    # 1. Unicode Normalization (converts full-width, Hindi Devanagari accents safely)
    normalized = unicodedata.normalize('NFKC', text)
    
    # 2. Extract Entities BEFORE destructive cleaning
    urls = re.findall(URL_PATTERN, normalized, flags=re.IGNORECASE)
    upi_ids = re.findall(UPI_PATTERN, normalized, flags=re.IGNORECASE)
    phone_numbers = re.findall(PHONE_PATTERN, normalized)
    currency_amounts = re.findall(CURRENCY_PATTERN, normalized, flags=re.IGNORECASE)
    
    # 3. De-obfuscate words (e.g. O.T.P -> OTP)
    deobfuscated = deobfuscate_keywords(normalized)
    
    # 4. Lowercase conversion
    lowercased = deobfuscated.lower()
    
    # 5. Clean whitespace & special characters (preserve letters, digits, Hindi Devanagari script range \u0900-\u097F, and key symbols)
    cleaned = re.sub(r'[^\w\s\u0900-\u097F₹@\.\-:/]', ' ', lowercased)
    cleaned_text = re.sub(r'\s+', ' ', cleaned).strip()
    
    return {
        "cleaned_text": cleaned_text,
        "entities": {
            "urls": urls,
            "upi_ids": upi_ids,
            "phone_numbers": phone_numbers,
            "currency_amounts": currency_amounts
        }
    }

if __name__ == "__main__":
    # Quick self-test demonstration
    sample = "URGENT: Your SBI Bank Account is blocked! Update K-Y-C now at http://sbi-verify.apk or send Rs 500 to paytm@ybl. Call +919876543210 immediately O.T.P."
    result = preprocess_text(sample)
    print("--- Preprocess Test Output ---")
    print("Cleaned Text:", result["cleaned_text"])
    print("Extracted Entities:", result["entities"])
