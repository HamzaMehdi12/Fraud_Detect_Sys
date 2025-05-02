# File: app/models.py
from pydantic import BaseModel
from typing import Dict, Any
import datetime

class ModelMetadata(BaseModel):
    model_version: str = "1.0.0"
    training_date: datetime.datetime
    features_used: list
    model_metrics: Dict[str, Any]
    data_statistics: Dict[str, Any]

class FraudPredictionResponse(BaseModel):
    is_fraud: bool
    confidence: float
    model_version: str
    feature_contributions: Dict[str, float]