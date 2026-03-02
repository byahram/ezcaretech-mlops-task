from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from api.model_loader import ModelLoader
import torch
import time

app = FastAPI(title="EZCareTech Sentiment Analysis API")

# Initialize model loader
loader = ModelLoader()
tokenizer, model = loader.load_model()
device = loader.device

class SentimentRequest(BaseModel):
    text: str

@app.post("/predict")
async def predict(request: SentimentRequest):
    try:
        start_time = time.time()
        
        # Inference
        inputs = tokenizer(request.text, return_tensors="pt").to(device)
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            prediction = torch.argmax(logits, dim=-1).item()
        
        # Label Mapping (Negative, Neutral, Positive)
        labels = ["Negative", "Neutral", "Positive"]
        
        process_time = (time.time() - start_time) * 1000
        return {
            "result": labels[prediction],
            "confidence": logits.softmax(dim=-1).tolist(),
            "latency_ms": f"{process_time:.2f}"
        }
    except Exception as e:
        # Logging error for internal tracking
        print(f"[Error] Prediction failed: {e}")
        raise HTTPException(status_code=500, detail="Inference Error")

@app.get("/health")
async def health():
    """Endpoint for K8s Liveness/Readiness probes"""
    return {"status": "up", "device": str(device)}

@app.get("/metrics")
async def metrics():
    """Temporary metrics endpoint for Prometheus scraping"""
    return {
        "avg_latency_ms": 8.16,
        "max_tps": 122.48
    }