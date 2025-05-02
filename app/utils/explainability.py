import shap
import numpy as np

class ShapExplainer: #Class for machine learning model ecplanations using Shap values
    def __init__(self, model, preprocessor):
        self.explainer = shap.TreeExplainer(model)
        self.preprocessor = preprocessor
        
    def explain(self, input_data):
        processed_data = self.preprocessor.transform(input_data)
        shap_values = self.explainer.shap_values(processed_data)
        return {
            "base_value": float(self.explainer.expected_value),
            "shap_values": shap_values[0].tolist(),
            "feature_names": self.preprocessor.get_feature_names_out().tolist()
        }