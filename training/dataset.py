#############################
# File: training/dataset.py #
#############################
import logging
import pandas as pd
from pathlib import Path
from typing import Tuple, Dict
from sklearn.model_selection import TimeSeriesSplit
from .config import TrainingConfig
from great_expectations.dataset import PandasDataset

logger = logging.getLogger(__name__)

class FraudDataProcessor:
    """Handles end-to-end data processing with quality checks"""
    
    def __init__(self, config: TrainingConfig):
        self.config = config
        self.raw_data = None
        self.processed_data = None
        self._initialize_directories()
        
    def _initialize_directories(self):
        """Ensure required data directories exist"""
        Path(self.config.data_config.raw_data_path).mkdir(parents=True, exist_ok=True)
        Path(self.config.data_config.processed_data_path).parent.mkdir(parents=True, exist_ok=True)
        Path(self.config.data_config.backup_data_path).mkdir(parents=True, exist_ok=True)

    def _validate_raw_data(self, df: pd.DataFrame) -> bool:
        """Perform comprehensive data validation"""
        try:
            ge_df = PandasDataset(df)
            
            # Schema validation
            ge_df.expect_table_columns_to_match_ordered_list(
                ["amount", "oldbalanceOrg", "newbalanceOrig", 
                 "oldbalanceDest", "newbalanceDest", "transaction_type",
                 "isFraud", "transactionDateTime"]
            )
            
            # Data quality expectations
            expectations = {
                "expect_column_values_to_not_be_null": ["amount", "isFraud"],
                "expect_column_values_to_be_between": {
                    "column": "amount", "min_value": 0, "max_value": 1e9
                },
                "expect_column_values_to_be_in_set": {
                    "column": "transaction_type",
                    "value_set": ["CASH_IN", "CASH_OUT", "DEBIT", "PAYMENT", "TRANSFER"]
                },
                "expect_column_values_to_be_unique": "transactionId",
                "expect_column_pair_values_A_to_be_greater_than_B": {
                    "column_A": "oldbalanceOrg",
                    "column_B": "newbalanceOrig",
                    "or_equal": True
                }
            }
            
            validation_result = ge_df.validate(expectations=expectations)
            if not validation_result["success"]:
                logger.error("Data validation failed with %d errors", 
                             len(validation_result["results"]))
                self._log_validation_errors(validation_result)
                return False
            return True
            
        except Exception as e:
            logger.error("Data validation error: %s", str(e))
            return False

    def _engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create derived features and temporal features"""
        try:
            # Temporal features
            df["transactionDateTime"] = pd.to_datetime(df["transactionDateTime"])
            df["hour_of_day"] = df["transactionDateTime"].dt.hour
            df["day_of_week"] = df["transactionDateTime"].dt.dayofweek
            df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)
            
            # Derived features
            for feature, expr in self.config.feature_config.derived_features.items():
                df[feature] = df.eval(expr)
                
            return df
            
        except Exception as e:
            logger.error("Feature engineering failed: %s", str(e))
            raise

    def process_data(self) -> Tuple[pd.DataFrame, Dict]:
        """Main processing pipeline"""
        try:
            # Load raw data
            raw_files = list(Path(self.config.data_config.raw_data_path).glob("*")
            if not raw_files:
                raise FileNotFoundError("No raw data files found")
                
            dfs = []
            for file in raw_files:
                if file.suffix == ".csv":
                    dfs.append(pd.read_csv(file))
                elif file.suffix == ".parquet":
                    dfs.append(pd.read_parquet(file))
                else:
                    logger.warning("Unsupported file format: %s", file.suffix)
                    
            self.raw_data = pd.concat(dfs, ignore_index=True)
            
            # Validate data
            if not self._validate_raw_data(self.raw_data):
                raise ValueError("Raw data validation failed")
                
            # Feature engineering
            processed_data = self._engineer_features(self.raw_data)
            
            # Save processed data
            processed_data.to_parquet(self.config.data_config.processed_data_path)
            logger.info("Processed data saved to %s", 
                        self.config.data_config.processed_data_path)
            
            # Generate data profile
            profile = {
                "start_date": str(processed_data["transactionDateTime"].min()),
                "end_date": str(processed_data["transactionDateTime"].max()),
                "total_transactions": len(processed_data),
                "fraud_percentage": processed_data["isFraud"].mean() * 100,
                "data_quality_score": self._calculate_data_quality_score(processed_data)
            }
            
            return processed_data, profile
            
        except Exception as e:
            logger.critical("Data processing failed: %s", str(e))
            raise