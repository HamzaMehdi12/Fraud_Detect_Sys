import requests
import json
from typing import Dict

GRAFANA_URL = "http://grafana:3000"
API_KEY = "YOUR_API_KEY"

def create_alert(alert_config: Dict):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        f"{GRAFANA_URL}/api/v1/provisioning/alert-rules",
        headers=headers,
        json=alert_config
    )
    
    if response.status_code != 201:
        raise Exception(f"Alert creation failed: {response.text}")

HIGH_RISK_ALERT = {
    "name": "High Fraud Probability Alert",
    "condition": "B",
    "for": "5m",
    "annotations": {
        "summary": "High fraud risk detected",
        "description": "Transaction {{ $labels.transaction_id }} has {{ $value }}% fraud probability"
    },
    "rules": [{
        "expr": "fraud_prediction_confidence > 0.85",
        "labels": {"severity": "critical"}
    }]
}