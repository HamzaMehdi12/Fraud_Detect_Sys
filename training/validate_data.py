import json
import pandas as pd
from pathlib import Path
from great_expectations.dataset import PandasDataset
import logging

logger = logging.getLogger(__name__)

class DataValidator:
    def __init__(self, schema_path: str):
        self.schema = self._load_schema(schema_path)
    
    def _load_schema(self, path: str) -> dict:
        with open(Path(path)) as f:
            return json.load(f)
    
    def validate(self, df: pd.DataFrame) -> bool:
        try:
            ge_df = PandasDataset(df)
            
            # Validate schema
            ge_df.expect_table_columns_to_match_ordered_list(
                self.schema["columns"]
            )
            
            # Validate data types
            for col, dtype in self.schema["dtypes"].items():
                ge_df.expect_column_values_to_be_of_type(col, dtype)
            
            # Business rules
            ge_df.expect_column_values_to_be_between(
                "amount", min_value=0
            )
            ge_df.expect_column_values_to_be_in_set(
                "transaction_type", 
                ["CASH_IN", "CASH_OUT", "DEBIT", "PAYMENT", "TRANSFER"]
            )
            
            return ge_df.validate().success
        except Exception as e:
            logger.error(f"Validation failed: {str(e)}")
            return False