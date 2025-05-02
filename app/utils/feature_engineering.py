from datetime import datetime
import pandas as pd

def create_features(df: pd.DataFrame) -> pd.DataFrame:
    """Generate time-based and transaction features"""
    df['transaction_date'] = pd.to_datetime(df['transaction_date'])
    
    # Time features
    df['hour'] = df['transaction_date'].dt.hour
    df['is_weekend'] = df['transaction_date'].dt.weekday >= 5
    
    # Transaction features
    df['balance_change_orig'] = df['oldbalanceOrg'] - df['newbalanceOrig']
    df['balance_change_dest'] = df['newbalanceDest'] - df['oldbalanceDest']
    df['amount_to_balance_ratio'] = df['amount'] / (df['oldbalanceOrg'] + 1e-6)
    
    return df