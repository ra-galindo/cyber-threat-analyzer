from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI(
    title="Cyber Threat Analyzer API",
    description="BERT-based cyber threat detection for emails/messages.",
    version="0.1.0",
)

class AnalyzeRequest(BaseModel):
    text: str


class ThreatPrediction(BaseModel):
    label: str
    score: float


class AnalyzeResponse(BaseModel):
    predictions: List[ThreatPrediction]


@app.get("/ping")
def ping():
    return {"status": "ok"}



@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest):
    """
    Analyze text and return predicted threat type.
    """
    text = req.text.lower()

    # (just to test the API):
    if "password" in text or "account" in text:
        label = "phishing"
        score = 0.92
    elif "bitcoin" in text or "crypto" in text:
        label = "scam"
        score = 0.85
    else:
        label = "safe"
        score = 0.80

    return AnalyzeResponse(
        predictions=[ThreatPrediction(label=label, score=score)]
    )
