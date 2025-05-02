# Model Retraining Runbook

## Trigger Conditions
- Daily at 2 AM UTC
- Data drift detected (PSI > 0.2)
- Performance degradation (AUC < 0.85)

## Steps
1. Check data quality:
   ```bash
   python training/validate_data.py --data-path data/processed/latest.parquet