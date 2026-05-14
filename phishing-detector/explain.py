import pickle
from pathlib import Path

import pandas as pd
import shap

_model = None
_explainer = None


def _load():
    global _model, _explainer
    if _model is None or _explainer is None:
        model_path = Path(__file__).parent / "model.pkl"
        _model = pickle.load(open(model_path, "rb"))
        _explainer = shap.TreeExplainer(_model)


def explain(features: dict) -> dict:
    """
    Returns {feature_name: shap_value} sorted by absolute impact.
    Positive values push toward phishing, negative toward legitimate.
    """
    _load()
    X = pd.DataFrame([features]).fillna(-1)
    shap_values = _explainer.shap_values(X)
    # Binary LightGBM returns list [class0_vals, class1_vals]
    values = shap_values[1][0] if isinstance(shap_values, list) else shap_values[0]
    result = dict(zip(features.keys(), values))
    return dict(sorted(result.items(), key=lambda x: abs(x[1]), reverse=True))
