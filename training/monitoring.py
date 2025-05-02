# 1. Add model monitoring (training/monitoring.py)
import pandas as pd
from evidently.report import Report
from evidently.metrics import (
    DataDriftTable, 
    ClassificationQualityMetric,
    ConfusionMatrix,
    FeatureDriftTable
)

class ModelMonitor:
    def __init__(self, reference_data: pd.DataFrame, current_data: pd.DataFrame):
        self.reference_data = reference_data
        self.current_data = current_data
        
    def check_data_drift(self) -> dict:
        report = Report(metrics=[
            DataDriftTable(),
            FeatureDriftTable()
        ])
        report.run(
            reference_data=self.reference_data,
            current_data=self.current_data
        )
        return report.as_dict()
    
    def check_model_performance(self, y_true, y_pred) -> dict:
        report = Report(metrics=[
            ClassificationQualityMetric(),
            ConfusionMatrix()
        ])
        report.run(
            reference_data=self.reference_data.assign(label=y_true),
            current_data=self.current_data.assign(label=y_true, prediction=y_pred)
        )
        return report.as_dict()


# 2. Enhanced model versioning (app/models.py)
import datetime
from pydantic import BaseModel

class ModelMetadata(BaseModel):
    version: str
    training_date: datetime.datetime
    features: list
    performance: dict
    data_statistics: dict


# 3. Real-time monitoring (app/monitoring.py)
from prometheus_client import start_http_server, Counter, Gauge

PREDICTION_COUNTER = Counter(
    'fraud_predictions_total', 
    'Total fraud predictions',
    ['model_version', 'result']
)

PREDICTION_CONFIDENCE = Gauge(
    'fraud_prediction_confidence',
    'Prediction confidence score',
    ['model_version']
)

LATENCY_HISTOGRAM = Histogram(
    'fraud_prediction_latency_seconds',
    'Prediction request latency'
)


# 4. Anomaly detection (training/anomaly.py)
from sklearn.ensemble import IsolationForest

class AnomalyDetector:
    def __init__(self, contamination=0.01):
        self.model = IsolationForest(contamination=contamination)
        self.scaler = StandardScaler()
        
    def fit(self, X):
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled)
        
    def predict(self, X):
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)


# 5. Enhanced training pipeline (training/train.py)
class FraudDetectorTrainer:
    # ... existing code ...
    
    def train(self):
        try:
            # Add data validation
            self._validate_training_data(df)
            
            # Add anomaly detection
            self._detect_data_anomalies(df)
            
            # ... rest of training ...
            
            # Add model versioning
            self._create_model_card()
            
            # Add monitoring baseline
            self._save_monitoring_reference_data(df)
            
        except Exception as e:
            logger.error(f"Training failed: {str(e)}")
            raise
    
    def _validate_training_data(self, df):
        from great_expectations import Dataset
        ge_df = Dataset(df)
        
        expectations = {
            "expect_column_values_to_not_be_null": {"column": "amount"},
            "expect_column_values_to_be_between": {
                "column": "amount",
                "min_value": 0
            },
            # ... add 20+ expectations ...
        }
        
        for expectation, params in expectations.items():
            getattr(ge_df, expectation)(**params)
            
        validation = ge_df.validate()
        if not validation["success"]:
            raise ValueError("Data validation failed")
    
    def _detect_data_anomalies(self, df):
        anomaly_detector = AnomalyDetector()
        X = df[self.config.numeric_features]
        anomalies = anomaly_detector.fit_predict(X)
        logger.info(f"Detected {sum(anomalies == -1)} data anomalies")
        
    def _create_model_card(self):
        card = {
            "model_type": "XGBoost",
            "model_version": "1.1.0",
            "training_date": datetime.datetime.now(),
            "metrics": self._calculate_metrics(),
            "data_statistics": self._get_data_stats(),
            "hyperparameters": self.config.model_params
        }
        with open("models/model_card.json", "w") as f:
            json.dump(card, f)
    
    def _save_monitoring_reference_data(self, df):
        df.sample(1000).to_parquet("monitoring/reference_data.parquet")


# 6. Enhanced API with security (app/app.py)
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware

api_key_header = APIKeyHeader(name="X-API-Key")

async def get_api_key(api_key: str = Depends(api_key_header)):
    if api_key != os.getenv("API_KEY"):
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/predict")
@LATENCY_HISTOGRAM.time()
async def predict(
    transaction: TransactionRequest, 
    api_key: str = Depends(get_api_key)
):
    # ... existing code ...
    try:
        start_time = time.time()
        
        # Add anomaly detection
        if self.anomaly_detector.predict(processed_input) == -1:
            logger.warning("Anomalous transaction detected")
            
        # ... prediction logic ...
        
        # Update metrics
        PREDICTION_COUNTER.labels(
            model_version="1.1.0", 
            result="fraud" if prediction else "legit"
        ).inc()
        
        PREDICTION_CONFIDENCE.labels(
            model_version="1.1.0"
        ).set(proba[1])
        
        LATENCY_HISTOGRAM.observe(time.time() - start_time)
        
        return {
            # ... existing response ...,
            "explanation": self._generate_explanation(processed_input)
        }
    except Exception as e:
        # ... error handling ...

    def _generate_explanation(self, processed_input):
        import shap
        explainer = shap.TreeExplainer(self.model)
        shap_values = explainer.shap_values(processed_input)
        return {
            "feature_importance": dict(zip(
                self.config.features, 
                shap_values[0].tolist()
            ))
        }


# 7. Automated retraining (training/retrain.py)
import schedule
import time
from datetime import datetime

class Retrainer:
    def __init__(self):
        self.config = TrainingConfig()
        self.monitor = DataDriftMonitor()
        
    def check_and_retrain(self):
        try:
            current_data = pd.read_parquet("data/processed/latest.parquet")
            ref_data = pd.read_parquet("monitoring/reference_data.parquet")
            
            drift_report = self.monitor.check_data_drift(ref_data, current_data)
            
            if drift_report["data_drift_found"]:
                logger.info("Data drift detected - triggering retraining")
                self.retrain()
                
        except Exception as e:
            logger.error(f"Retraining failed: {str(e)}")
            
    def retrain(self):
        trainer = FraudDetectorTrainer(self.config)
        new_model = trainer.train()
        self._deploy_model(new_model)
        
    def _deploy_model(self, model):
        # Implement canary deployment
        # ... model deployment logic ...
        
if __name__ == "__main__":
    schedule.every().day.at("02:00").do(Retrainer().check_and_retrain)
    while True:
        schedule.run_pending()
        time.sleep(1)