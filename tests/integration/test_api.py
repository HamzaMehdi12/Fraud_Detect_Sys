from fastapi.testclient import TestClient
from app.app import app

client = TestClient(app)

def test_fraud_prediction():
    payload = {
        "transaction_id": "test_123",
        "amount": 15000.0,
        "oldbalanceOrg": 20000.0,
        "newbalanceOrig": 5000.0,
        "oldbalanceDest": 1000.0,
        "newbalanceDest": 16000.0,
        "transaction_type": "CASH_OUT"
    }
    
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    assert "is_fraud" in response.json()