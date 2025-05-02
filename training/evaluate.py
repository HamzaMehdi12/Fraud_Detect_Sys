# File: training/evaluate.py
import logging
import joblib
import pandas as pd
from sklearn.metrics import (
    classification_report, 
    roc_auc_score,
    precision_recall_curve,
    average_precision_score
)
import matplotlib.pyplot as plt
from .config import TrainingConfig

logger = logging.getLogger(__name__)

class ModelEvaluator:
    def __init__(self, config: TrainingConfig):
        self.config = config
        self.artifacts = joblib.load(config.model_save_path)
        self.model = self.artifacts["model"]
        self.preprocessor = self.artifacts["preprocessor"]
        
    def evaluate(self):
        try:
            df = pd.read_csv(self.config.data_path)
            X = df[self.config.features]
            y = df[self.config.target]
            
            X_processed = self.preprocessor.transform(X)
            
            y_pred = self.model.predict(X_processed)
            y_proba = self.model.predict_proba(X_processed)[:, 1]
            
            self._generate_metrics(y, y_pred, y_proba)
            self._plot_curves(y, y_proba)
            
        except Exception as e:
            logger.error(f"Evaluation failed: {str(e)}")
            raise
            
    def _generate_metrics(self, y_true, y_pred, y_proba):
        logger.info("\nClassification Report:\n%s", classification_report(y_true, y_pred))
        logger.info("ROC AUC Score: %.3f", roc_auc_score(y_true, y_proba))
        logger.info("Average Precision Score: %.3f", 
                   average_precision_score(y_true, y_proba))
        
    def _plot_curves(self, y_true, y_proba):
        plt.figure(figsize=(12, 6))
        
        # ROC Curve
        fpr, tpr, _ = roc_curve(y_true, y_proba)
        plt.subplot(121)
        plt.plot(fpr, tpr)
        plt.title('ROC Curve')
        
        # Precision-Recall Curve
        precision, recall, _ = precision_recall_curve(y_true, y_proba)
        plt.subplot(122)
        plt.plot(recall, precision)
        plt.title('Precision-Recall Curve')
        
        plt.savefig("reports/performance_curves.png")
        plt.close()