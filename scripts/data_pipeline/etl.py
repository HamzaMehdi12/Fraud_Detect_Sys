import pandas as pd
from pathlib import Path
from training.validate_data import DataValidator
import logging

def run_etl(raw_dir: str, processed_dir: str, schema_path: str):
    raw_path = Path(raw_dir)
    processed_path = Path(processed_dir)
    processed_path.mkdir(exist_ok=True)
    
    validator = DataValidator(schema_path)
    
    for file in raw_path.glob("*.csv"):
        try:
            df = pd.read_csv(file)
            if validator.validate(df):
                df["transaction_date"] = pd.to_datetime(df["transaction_date"])
                df.to_parquet(processed_path / f"{file.stem}.parquet")
                logging.info(f"Processed {file.name}")
            else:
                logging.warning(f"Validation failed for {file.name}")
        except Exception as e:
            logging.error(f"Error processing {file.name}: {str(e)}")