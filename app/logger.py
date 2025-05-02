# File: app/logger.py
import logging
import sys
from pathlib import Path

def setup_logging():
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(logs_dir / "fraud_detection.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    logging.captureWarnings(True)