from __future__ import annotations

import json
from pathlib import Path
from typing import List, Dict, Any, Optional

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

MODEL_DIR = Path(__file__).resolve().parents[1] / "models" / "cyber-bert-v1"

_tokenizer: Optional[Any] = None
_model: Optional[Any] = None
_label_map: Optional[Dict[str, str]] = None
_device: Optional[torch.device] = None


def load_model() -> None:
    """Load model/tokenizer once (cached in module globals)."""
    global _tokenizer, _model, _label_map, _device

    if _tokenizer is not None and _model is not None and _label_map is not None and _device is not None:
        return

    if not MODEL_DIR.exists():
        raise FileNotFoundError(f"Model folder not found: {MODEL_DIR}")

    label_map_path = MODEL_DIR / "label_map.json"
    if not label_map_path.exists():
        raise FileNotFoundError(f"label_map.json not found in: {MODEL_DIR}")

    with open(label_map_path, "r", encoding="utf-8") as f:
        raw_map = json.load(f)

    # Support both {"0": "label"} and {0: "label"} just in case
    _label_map = {str(k): str(v) for k, v in raw_map.items()}

    _device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Ensure deploy loads from local folder only (no accidental internet fetch)
    _tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR, use_fast=True, local_files_only=True)
    _model = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR, local_files_only=True)
    _model.to(_device)
    _model.eval()


@torch.inference_mode()
def predict(text: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """Return top-k predictions as [{label, score}, ...]."""
    if _tokenizer is None or _model is None or _label_map is None or _device is None:
        load_model()

    text = (text or "").strip()
    if not text:
        return [{"label": "empty", "score": 1.0}]

    inputs = _tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=256,
    )
    inputs = {k: v.to(_device) for k, v in inputs.items()}

    outputs = _model(**inputs)
    probs = torch.softmax(outputs.logits, dim=1)[0]

    k = max(1, min(int(top_k), int(probs.shape[0])))
    top_vals, top_idx = torch.topk(probs, k=k)

    results: List[Dict[str, Any]] = []
    for score, idx in zip(top_vals.tolist(), top_idx.tolist()):
        label = _label_map.get(str(idx), f"label_{idx}")
        results.append({"label": label, "score": float(score)})

    return results
