import pandas as pd
import numpy as np
import joblib
import json
from pathlib import Path

_ARTIFACTS_DIR = Path(__file__).parent.parent / "artifacts"

_model = None
_preprocessor = None
_config = None
_feature_meta = None


def _load_artifacts():
    global _model, _preprocessor, _config, _feature_meta
    if _model is None:
        _model        = joblib.load(_ARTIFACTS_DIR / "champion.joblib")
        _preprocessor = joblib.load(_ARTIFACTS_DIR / "preprocessor.joblib")
        with open(_ARTIFACTS_DIR / "production_config.json") as f:
            _config = json.load(f)
        with open(_ARTIFACTS_DIR / "feature_metadata.json") as f:
            _feature_meta = json.load(f)


def predict_single(customer: dict, threshold: float = None) -> dict:
    """
    Predict churn probability for a single customer.

    Parameters
    ----------
    customer : dict
        Raw customer attributes. Required keys match the training schema.
    threshold : float, optional
        Classification threshold. Defaults to production_config optimal.

    Returns
    -------
    dict with keys:
        churn_probability : float
        churn_prediction  : int (0 or 1)
        threshold_used    : float
        risk_tier         : str  ('high' / 'medium' / 'low')
        top_risk_factors  : list[str]
    """
    _load_artifacts()

    if threshold is None:
        threshold = _config.get("optimal_threshold_business_value", 0.5)

    all_features = (
        _feature_meta["numeric_features"] +
        _feature_meta["binary_features"] +
        _feature_meta["categorical_features"]
    )
    row = pd.DataFrame([{k: customer.get(k, np.nan) for k in all_features}])

    # Engineered features (mirrors NTB-02)
    months = row["tenure_months"].iloc[0]
    if months <= 6:    row["tenure_phase"] = "phase1_0to6"
    elif months <= 12: row["tenure_phase"] = "phase2_7to12"
    elif months <= 24: row["tenure_phase"] = "phase3_13to24"
    elif months <= 48: row["tenure_phase"] = "phase4_25to48"
    else:              row["tenure_phase"] = "phase5_49plus"

    row["is_new_customer"]    = int(months <= 6)
    row["has_internet"]       = int(row["internet_service"].iloc[0] != "No")
    addon_cols = ["online_security", "online_backup", "device_protection",
                  "tech_support", "streaming_tv", "streaming_movies"]
    row["num_addons"]         = sum(1 for c in addon_cols if customer.get(c) == "Yes")
    row["risky_payment"]      = int(row["payment_method"].iloc[0] == "Electronic check")
    row["auto_payment"]       = int(row["payment_method"].iloc[0] in
                                    ["Bank transfer (automatic)", "Credit card (automatic)"])
    row["charges_per_tenure"] = row["monthly_charges"].iloc[0] / (months + 1)
    row["high_value_customer"] = int(row["monthly_charges"].iloc[0] > 79.65)

    row_aligned = row.reindex(columns=all_features)
    X_processed = _preprocessor.transform(row_aligned)

    proba = float(_model.predict_proba(X_processed)[:, 1][0])
    prediction = int(proba >= threshold)

    if proba >= 0.7:   risk_tier = "high"
    elif proba >= 0.35: risk_tier = "medium"
    else:               risk_tier = "low"

    return {
        "churn_probability": round(proba, 4),
        "churn_prediction":  prediction,
        "threshold_used":    threshold,
        "risk_tier":         risk_tier,
        "top_risk_factors":  _config.get("top_features_shap", [])[:5],
    }


def predict_batch(customers: list, threshold: float = None) -> list:
    """Predict churn for a list of customer dicts."""
    return [predict_single(c, threshold) for c in customers]


def get_model_info() -> dict:
    """Return production config metadata."""
    _load_artifacts()
    return {
        "model_name":        _config.get("model_name"),
        "auc_roc":           _config.get("test_auc_roc"),
        "pr_auc":            _config.get("test_pr_auc"),
        "optimal_threshold": _config.get("optimal_threshold_business_value"),
        "monthly_value_usd": _config.get("optimal_monthly_value_usd"),
        "top_features":      _config.get("top_features_shap", [])[:5],
        "created_at":        _config.get("created_at"),
    }
