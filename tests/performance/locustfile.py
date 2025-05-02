from locust import HttpUser, task, between

class FraudDetectionUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def predict_fraud(self):
        payload = {
            "transaction_id": "test_123",
            "amount": 15000.0,
            "oldbalanceOrg": 20000.0,
            "newbalanceOrig": 5000.0,
            "oldbalanceDest": 1000.0,
            "newbalanceDest": 16000.0,
            "transaction_type": "CASH_OUT"
        }
        self.client.post("/predict", json=payload)