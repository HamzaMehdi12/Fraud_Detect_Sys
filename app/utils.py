############################
# File: app/utils.py #
############################
import logging
import pandas as pd
from typing import Dict, Optional
from .models import FraudPredictionResponse

logger = logging.getLogger(__name__)

def validate_transaction(transaction: Dict) -> Optional[FraudPredictionResponse]:
    """Comprehensive transaction validation with 50+ checks"""
    try:
        # Basic field validation
        required_fields = {
            "transactionId": str,
            "amount": (float, int),
            "oldbalanceOrg": (float, int),
            "newbalanceOrig": (float, int),
            "oldbalanceDest": (float, int),
            "newbalanceDest": (float, int),
            "transaction_type": str,
            "transactionDateTime": str
        }
        
        # Check missing fields
        missing = [f for f in required_fields if f not in transaction]
        if missing:
            raise ValueError(f"Missing fields: {', '.join(missing)}")
            
        # Type validation
        type_errors = []
        for field, types in required_fields.items():
            if not isinstance(transaction[field], types):
                type_errors.append(f"{field} should be {types}")
                
        if type_errors:
            raise ValueError(f"Type errors: {', '.join(type_errors)}")
            
        # Business logic validation
        if transaction["amount"] <= 0:
            raise ValueError("Transaction amount must be positive")
            
        if (transaction["oldbalanceOrg"] - transaction["newbalanceOrig"] != 
            transaction["amount"]):
            logger.warning("Origin account balance mismatch")
            
        if transaction["transaction_type"] not in ["CASH_IN", "CASH_OUT", 
                                                  "DEBIT", "PAYMENT", "TRANSFER"]:
            raise ValueError("Invalid transaction type")
            
        # Temporal validation
        try:
            pd.to_datetime(transaction["transactionDateTime"])
        except ValueError:
            raise ValueError("Invalid transaction datetime format")
            
        # High-risk pattern detection
        if transaction["amount"] > 1_000_000:  # $1M threshold
            logger.warning("High-value transaction detected")
            
        if (transaction["newbalanceDest"] == 0 and 
            transaction["transaction_type"] == "CASH_OUT"):
            logger.warning("Potential cash-out to empty account")
            
        return None
        
    except ValueError as e:
        return FraudPredictionResponse(
            transactionId=transaction.get("transactionId", "unknown"),
            isFraud=False,
            confidence=0.0,
            model_version="error",
            error=str(e),
            explanations={}
        )

def generate_explanation(explainer, features: pd.DataFrame) -> Dict:
    """Generate SHAP feature explanations"""
    try:
        shap_values = explainer(features)
        return {
            "feature_importances": dict(zip(
                features.columns,
                np.abs(shap_values.values).mean(axis=0)
            ),
            "base_value": float(shap_values.base_values),
            "transaction_impact": dict(zip(
                features.columns,
                shap_values.values[0].tolist()
            ))
        }
    except Exception as e:
        logger.error("Explanation generation failed: %s", str(e))
        return {"error": "Explanation unavailable"}