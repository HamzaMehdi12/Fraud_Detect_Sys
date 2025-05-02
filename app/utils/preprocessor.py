from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
import joblib

def build_preprocessor():
    numeric_features = ['amount', 'oldbalanceOrg', 'newbalanceOrig']
    categorical_features = ['transaction_type']
    
    return ColumnTransformer(
        transformers=[
            ('num', 'passthrough', numeric_features),
            ('cat', OneHotEncoder(), categorical_features)
        ])

def save_preprocessor(preprocessor, path):
    joblib.dump(preprocessor, path)

def load_preprocessor(path):
    return joblib.load(path)