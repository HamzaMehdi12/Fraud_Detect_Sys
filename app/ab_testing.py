# File: app/ab_testing.py
import hashlib
import joblib
from fastapi import HTTPException
from prometheus_client import Counter
from typing import Dict, Any

AB_PREDICTION_COUNTER = Counter(
    'ab_predictions_total', 
    'A/B Testing Predictions', 
    ['model_version', 'result']
)

class ABTestRouter:
    def __init__(self):
        self.models = {
            "production": self._load_model("v2.0.0"),
            "candidate": self._load_model("v2.1.0")
        }
        self.weights = {"production": 90, "candidate": 10}
    
    def _load_model(self, version: str) -> Dict[str, Any]:
        try:
            return joblib.load(f"models/registry/model_{version}.pkl")
        except Exception as e:
            raise HTTPException(500, f"Model load failed: {str(e)}")
    
    def _get_model_version(self, transaction_id: str) -> str:
        """Consistent hashing for traffic splitting"""
        hash_val = int(hashlib.md5(transaction_id.encode()).hexdigest(), 16)
        return "candidate" if (hash_val % 100) < self.weights["candidate"] else "production"
    
    def predict(self, features: Dict) -> Dict:
        version = self._get_model_version(features["transaction_id"])
        model = self.models[version]
        
        try:
            prediction = model["pipeline"].predict_proba([features])[0][1]
            is_fraud = prediction > model["threshold"]
            
            AB_PREDICTION_COUNTER.labels(
                model_version=version,
                result="fraud" if is_fraud else "legit"
            ).inc()
            
            return {
                "is_fraud": is_fraud,
                "confidence": float(prediction),
                "model_version": version
            }
        except Exception as e:
            raise HTTPException(500, f"Prediction failed: {str(e)}")