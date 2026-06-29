import logging
import numpy as np
import pandas as pd
import xgboost as xgb
import shap
from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)

class IceConfidenceModel:
    """
    XGBoost model to predict subsurface ice probability (Ice Confidence).
    Includes SHAP-based explainability logic.
    """
    
    def __init__(self, model_path: str = None):
        self.model_path = model_path
        self.model = None
        self.explainer = None
        
    def train(self, X_train: pd.DataFrame, y_train: pd.Series, **kwargs):
        """Trains the XGBoost classification model."""
        logger.info("Training Ice Confidence XGBoost Model...")
        self.model = xgb.XGBClassifier(
            objective="binary:logistic",
            eval_metric="logloss",
            use_label_encoder=False,
            **kwargs
        )
        self.model.fit(X_train, y_train)
        
        # Initialize SHAP explainer
        self.explainer = shap.TreeExplainer(self.model)
        logger.info("Model training and explainer initialization complete.")
        
    def predict(self, X: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Predicts ice confidence (probability) and returns SHAP values for explainability.
        
        Returns:
            Tuple of (probabilities, shap_values)
        """
        if self.model is None:
            raise ValueError("Model is not trained. Call train() first.")
            
        logger.info(f"Predicting ice confidence for {len(X)} pixels...")
        probabilities = self.model.predict_proba(X)[:, 1]
        
        # Calculate SHAP values
        shap_values = self.explainer.shap_values(X)
        
        return probabilities, shap_values
        
    def generate_confidence_map(self, probabilities: np.ndarray, original_shape: tuple) -> np.ndarray:
        """Reshapes flat predictions back into a 2D spatial array map."""
        return probabilities.reshape(original_shape)
