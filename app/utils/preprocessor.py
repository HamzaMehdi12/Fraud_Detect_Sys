from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
import joblib

def build_preprocessor():
    """
    Creates a preprocessing pipeline to transform raw transaction data into a format suitable for machine learning models. ML models require numeric input. 
    Preserves numeric features while encoding categorical ones.
    
    Numeric Features (amount, oldbalanceOrg, newbalanceOrig):
    Passed through unchanged (passthrough).
    Example: amount=1000.0 → remains 1000.0.
    
    Categorical Feature (transaction_type):
    Encoded using OneHotEncoder to convert categories to binary vectors.
    Example: transaction_type="TRANSFER" → [1, 0, 0, 0, 0].
    """
    numeric_features = ['amount', 'oldbalanceOrg', 'newbalanceOrig']
    categorical_features = ['transaction_type']
    
    return ColumnTransformer(
        transformers=[
            ('num', 'passthrough', numeric_features),
            ('cat', OneHotEncoder(), categorical_features)
        ])

def save_preprocessor(preprocessor, path):
    """
    Serializes and saves the preprocessing pipeline to disk for reuse.Ensures consistent preprocessing during training and inference.
    Critical for reproducibility in production.

    Uses joblib (optimized for numpy/scikit-learn objects).
    Saves the ColumnTransformer configuration and learned states (e.g., OneHotEncoder categories).
    """
    joblib.dump(preprocessor, path)

def load_preprocessor(path):
    """
    Loads a saved preprocessing pipeline from disk. Guarantees identical preprocessing for new data. Avoids data leakage or mismatched transformations.

    Reconstructs the ColumnTransformer with all learned transformations.
    Retains mappings (e.g., TRANSFER → [1, 0, 0, 0, 0]).
    """
    return joblib.load(path)
