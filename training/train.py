# File: training/train.py
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import TimeSeriesSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
import joblib
import logging
from datetime import datetime
from .config import TrainingConfig

logger = logging.getLogger(__name__)

class FraudModelTrainer:
    def __init__(self, config: TrainingConfig):
        self.config = config
        self.pipeline = None
        self.feature_processor = None
    
    def _process_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Feature engineering and validation"""
        df = df[self.config.feature_columns + [self.config.target_column]]
        
        # Temporal validation split
        df["transaction_date"] = pd.to_datetime(df["transaction_date"])
        df = df.sort_values("transaction_date")
        return df
    
    def _build_pipeline(self):
        numeric_features = [
            "amount", "oldbalanceOrg", "newbalanceOrig",
            "oldbalanceDest", "newbalanceDest"
        ]
        categorical_features = ["transaction_type"]
        
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', 'passthrough', numeric_features),
                ('cat', OneHotEncoder(), categorical_features)
            ]
        )
        
        return Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('classifier', xgb.XGBClassifier(**self.config.model_params))
        ])
    
    def train(self):
        try:
            df = pd.read_parquet(self.config.data_path)
            df = self._process_features(df)
            
            # Temporal split
            cutoff = df["transaction_date"].max() - pd.Timedelta(self.config.validation_window)
            train = df[df["transaction_date"] < cutoff]
            test = df[df["transaction_date"] >= cutoff]
            
            if len(test) == 0:
                raise ValueError("Test set is empty - check validation window")
            
            self.pipeline = self._build_pipeline()
            self.pipeline.fit(
                train[self.config.feature_columns],
                train[self.config.target_column]
            )
            
            # Save model with versioning
            version = datetime.now().strftime("%Y%m%d%H%M%S")
            artifact = {
                "pipeline": self.pipeline,
                "threshold": self.config.threshold,
                "version": version,
                "training_date": str(datetime.now()),
                "features": self.config.feature_columns
            }
            
            joblib.dump(artifact, f"models/registry/model_v{version}.pkl")
            logger.info(f"Model v{version} saved successfully")
            
            return artifact
        except Exception as e:
            logger.error(f"Training failed: {str(e)}")
            raise