# File: training/config.py
from dataclasses import dataclass

@dataclass
class TrainingConfig:
    data_path: str = "data/processed/transactions.parquet"
    test_size: float = 0.2
    model_params: dict = {
        "n_estimators": 300,
        "max_depth": 8,
        "learning_rate": 0.1,
        "subsample": 0.8,
        "scale_pos_weight": 50,
        "random_state": 42
    }
    threshold: float = 0.35
    feature_columns: list = [
        "amount", "oldbalanceOrg", "newbalanceOrig",
        "oldbalanceDest", "newbalanceDest", "transaction_type"
    ]
    target_column: str = "isFraud"
    validation_window: str = "7D"  # 7 days for temporal validation