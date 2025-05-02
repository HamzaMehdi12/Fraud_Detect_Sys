##############################
# File: app/app.py #
##############################
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, ValidationError
from typing import Dict, Any
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
import logging
from prometheus_client import Counter, Histogram
from .models import FraudPredictionResponse
from .utils import validate_transaction, generate_explanation
from .logger import setup_logging

# Initialize application
app = FastAPI(
    title="Fraud Detection API",
    version="2.0.0",
    description="Real-time fraud detection system for financial transactions",
    docs_url="/docs",
    redoc_url=None
)#creating API

# Metrics setup
PREDICTION_COUNTER = Counter(
    'fraud_predictions_total',
    'Total number of fraud predictions',
    ['model_version', 'result']
)

PREDICTION_LATENCY = Histogram(
    'fraud_prediction_latency_seconds',
    'Prediction request latency'
)

# Model loading
MODEL_REGISTRY = Path("models/registry")
MODEL_VERSION = "2.0.0"

def load_model():
    try:
        model_path = MODEL_REGISTRY / f"model_v{MODEL_VERSION}.pkl"
        artifacts = joblib.load(model_path)
        return artifacts
    except FileNotFoundError:
        logging.error("Model file not found")
        raise HTTPException(status_code=500, detail="Model not deployed")
    except Exception as e:
        logging.error("Model loading failed: %s", str(e))
        raise HTTPException(status_code=500, detail="Model initialization failed")

@app.on_event("startup")
async def startup_event():#FAST API development
    setup_logging()
    app.state.model = load_model()
    logging.info("API startup completed")

class TransactionRequest(BaseModel):
    transactionId: str
    amount: float
    oldbalanceOrg: float
    newbalanceOrig: float
    oldbalanceDest: float
    newbalanceDest: float
    transaction_type: str
    transactionDateTime: str

@app.post("/predict", response_model=FraudPredictionResponse) #To submit a request at a specified source.
@PREDICTION_LATENCY.time()#from the above function
async def predict(request: TransactionRequest):
    """Real-time fraud prediction endpoint"""
    try:
        # Input validation
        validation_error = validate_transaction(request.dict())
        if validation_error:
            return validation_error
            
        # Feature engineering
        features = pd.DataFrame([request.dict()])
        features = self._apply_feature_engineering(features)
        
        # Model prediction
        dmatrix = xgb.DMatrix(features[self.app.state.model["feature_names"]])
        proba = self.app.state.model["model"].predict(dmatrix)
        prediction = proba > self.app.state.model["config"].model_config.threshold
        
        # Generate explanation
        explanation = generate_explanation(
            self.app.state.model["explainer"],
            features
        )
        
        # Update metrics
        PREDICTION_COUNTER.labels(
            model_version=MODEL_VERSION,
            result="fraud" if prediction else "legit"
        ).inc()
        
        return {
            "transactionId": request.transactionId,
            "isFraud": bool(prediction),
            "confidence": float(proba),
            "model_version": MODEL_VERSION,
            "explanations": explanation,
            "anomaly_score": self._calculate_anomaly_score(features)
        }
        
    except ValidationError as e:
        logging.error("Input validation error: %s", str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logging.error("Prediction failed: %s", str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/model-info")
async def model_info():
    """Get current model information"""
    return {
        "version": MODEL_VERSION,
        "features": self.app.state.model["feature_names"],
        "training_date": str(self.app.state.model["training_timestamp"]),
        "performance": self.app.state.model.get("metrics", {})
    }

@app.get("/health")
async def health_check():
    """System health check"""
    return {
        "status": "healthy",
        "model_loaded": self.app.state.model is not None,
        "version": MODEL_VERSION
    }