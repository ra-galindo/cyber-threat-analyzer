from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

from app.model import load_model, predict

app = FastAPI(
    title="Cyber Threat Analyzer API",
    description="BERT-based cyber threat detection for emails/messages.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # later: ["https://your-frontend-domain.com"]
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    text: str

class ThreatPrediction(BaseModel):
    label: str
    score: float

class AnalyzeResponse(BaseModel):
    predictions: List[ThreatPrediction]

@app.on_event("startup")
def _startup():
    load_model()

@app.get("/ping")
def ping():
    return {"status": "ok"}

@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest):
    preds = predict(req.text, top_k=3)
    return AnalyzeResponse(predictions=[ThreatPrediction(**p) for p in preds])
