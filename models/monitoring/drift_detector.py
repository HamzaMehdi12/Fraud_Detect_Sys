import pandas as pd
from alibi_detect.cd import ChiSquareDrift

class DriftDetector:
    def __init__(self, reference_data: pd.DataFrame):
        self.ref_data = reference_data
        self.detector = ChiSquareDrift(
            x_ref=reference_data.values,
            p_val=0.05
        )
    
    def check_drift(self, current_data: pd.DataFrame):
        return self.detector.predict(current_data.values)