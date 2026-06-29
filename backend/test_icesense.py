import pytest
import numpy as np
import pandas as pd
from lmip_core.icesense.features import FeatureEngineer
from lmip_core.icesense.model import IceConfidenceModel

def test_feature_engineer():
    fe = FeatureEngineer()
    
    # 10x10 dummy arrays
    dfsar = np.random.rand(10, 10)
    ohrc = np.random.rand(10, 10)
    dem = np.random.rand(10, 10)
    
    features = fe.extract_features(dfsar, ohrc, dem)
    
    assert len(features) == 100
    assert "cpr" in features.columns
    assert "slope" in features.columns

def test_ice_confidence_model():
    model = IceConfidenceModel()
    
    # Generate some dummy training data
    X_train = pd.DataFrame({
        "cpr": np.random.rand(100),
        "slope": np.random.rand(100),
        "shadow_persistence": np.random.rand(100)
    })
    y_train = pd.Series(np.random.randint(0, 2, 100))
    
    # Train
    model.train(X_train, y_train)
    
    # Predict
    X_test = pd.DataFrame({
        "cpr": np.random.rand(10),
        "slope": np.random.rand(10),
        "shadow_persistence": np.random.rand(10)
    })
    
    probs, shap_values = model.predict(X_test)
    
    assert len(probs) == 10
    assert len(shap_values) == 10
    assert max(probs) <= 1.0
    assert min(probs) >= 0.0
