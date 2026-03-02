import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_read_health():
    """Health check 엔드포인트가 정상인지 확인"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "up"

def test_predict_endpoint():
    """실제 예측 API가 작동하는지 확인 (Mocking 없이 직접 호출)"""
    payload = {"text": "테스트 문장입니다."}
    response = client.post("/predict", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert "result" in data
    assert "latency_ms" in data