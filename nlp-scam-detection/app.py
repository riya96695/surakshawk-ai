from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from services.scam_detector import detect_scam, MODEL_VERSION

app = FastAPI(
    title="SuraksHawkAI NLP Scam Detection Engine API",
    description="Explainable NLP and Social-Engineering Scam Detection Module for Indian Digital Payment Protection.",
    version="1.0.0"
)

class MessageRequest(BaseModel):
    text: str = Field(..., json_schema_extra={"example": "Your SBI bank account is blocked. Share OTP immediately to verify KYC."})
    source_type: Optional[str] = Field("SMS", json_schema_extra={"example": "SMS"})

@app.get("/")
def home():
    """
    Root endpoint verifying module operation status.
    """
    return {
        "project": "SuraksHawkAI",
        "module": "NLP Scam Detection Engine",
        "status": "running",
        "version": MODEL_VERSION
    }

@app.get("/health")
def health():
    """
    Health check endpoint for B2B system monitoring & load balancers.
    """
    return {
        "status": "healthy",
        "service": "nlp-scam-detection",
        "model_version": MODEL_VERSION
    }

@app.post("/detect-scam")
def detect(request: MessageRequest):
    """
    Main endpoint for analyzing financial text messages, chat logs, and speech transcripts.
    Returns structured explainable risk payload for Risk Engine integration.
    """
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="Input 'text' field cannot be empty.")
        
    try:
        result = detect_scam(request.text)
        return {
            "source_type": request.source_type,
            **result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal NLP detection error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)