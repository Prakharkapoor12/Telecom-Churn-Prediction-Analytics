"""
Telecom Customer Churn Prediction API
======================================
Run with:
    uvicorn api.main:app --reload --port 8000

Or from the project root:
    cd D:\\VS_code\\customer-churn
    uvicorn api.main:app --reload --port 8000

Then open http://localhost:8000/docs for the interactive Swagger UI.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
import sys
from pathlib import Path
import time

# Add project root to path so we can import src/predict.py
sys.path.insert(0, str(Path(__file__).parent.parent))
from src import predict

# ── App setup ──────────────────────────────────────────────────────────────
app = FastAPI(
    title="Telecom Churn Prediction API",
    description=(
        "Predicts customer churn probability using a tuned LightGBM model "
        "(AUC-ROC = 0.847). Trained on IBM Telco Customer Churn dataset (7,043 customers). "
        "Use /docs for interactive testing."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Preload artifacts at startup so first request isn't slow
@app.on_event("startup")
async def startup_event():
    predict._load_artifacts()
    print("Artifacts loaded successfully.")


# ── Request / Response schemas ─────────────────────────────────────────────

class CustomerRequest(BaseModel):
    """All fields required to make a churn prediction."""
    # Demographics
    gender:         str   = Field(..., example="Male",    description="Male or Female")
    senior_citizen: int   = Field(..., example=0,         description="1 if senior citizen, else 0")
    partner:        str   = Field(..., example="Yes",     description="Yes or No")
    dependents:     str   = Field(..., example="No",      description="Yes or No")

    # Account
    tenure_months:  int   = Field(..., example=2,         description="Months as customer (0-72)")
    contract_type:  str   = Field(..., example="Month-to-month",
                                  description="Month-to-month, One year, or Two year")
    paperless_billing: str = Field(..., example="Yes",   description="Yes or No")
    payment_method: str   = Field(..., example="Electronic check",
                                  description="Electronic check, Mailed check, Bank transfer (automatic), Credit card (automatic)")

    # Services
    phone_service:    str = Field(..., example="Yes",    description="Yes or No")
    multiple_lines:   str = Field(..., example="No",     description="Yes, No, or No phone service")
    internet_service: str = Field(..., example="Fiber optic",
                                  description="DSL, Fiber optic, or No")
    online_security:  str = Field(..., example="No",     description="Yes, No, or No internet service")
    online_backup:    str = Field(..., example="No",     description="Yes, No, or No internet service")
    device_protection:str = Field(..., example="No",     description="Yes, No, or No internet service")
    tech_support:     str = Field(..., example="No",     description="Yes, No, or No internet service")
    streaming_tv:     str = Field(..., example="Yes",    description="Yes, No, or No internet service")
    streaming_movies: str = Field(..., example="No",     description="Yes, No, or No internet service")

    # Billing
    monthly_charges:  float = Field(..., example=79.85,  description="Monthly bill in USD")
    total_charges:    float = Field(..., example=79.85,  description="Total charges to date in USD")

    # Optional override
    threshold: Optional[float] = Field(None, example=0.48,
                                       description="Classification threshold. Defaults to optimal (0.48).")


class PredictionResponse(BaseModel):
    churn_probability: float  = Field(..., description="Probability of churn [0, 1]")
    churn_prediction:  int    = Field(..., description="1 = predicted churn, 0 = retained")
    threshold_used:    float  = Field(..., description="Threshold applied")
    risk_tier:         str    = Field(..., description="high / medium / low")
    top_risk_factors:  list   = Field(..., description="Top 5 SHAP feature names")
    latency_ms:        float  = Field(..., description="Inference latency in milliseconds")


class BatchRequest(BaseModel):
    customers: list[CustomerRequest] = Field(..., description="List of customer records")
    threshold: Optional[float]       = Field(None, description="Shared threshold for all customers")


class HealthResponse(BaseModel):
    status:      str
    model_name:  str
    auc_roc:     float
    uptime_s:    float


# ── Track startup time for uptime ──────────────────────────────────────────
_start_time = time.time()


# ── Endpoints ──────────────────────────────────────────────────────────────

@app.get("/", include_in_schema=False)
def root():
    return {"message": "Telecom Churn API v1.0 — visit /docs for interactive testing"}


@app.get("/health", response_model=HealthResponse, tags=["Monitoring"])
def health():
    """Health check — confirms the model is loaded and the service is alive."""
    info = predict.get_model_info()
    return {
        "status":     "healthy",
        "model_name": info["model_name"],
        "auc_roc":    info["auc_roc"],
        "uptime_s":   round(time.time() - _start_time, 1),
    }


@app.get("/model-info", tags=["Monitoring"])
def model_info():
    """Full model metadata: performance metrics, optimal threshold, top features."""
    return predict.get_model_info()


@app.post("/predict", response_model=PredictionResponse, tags=["Prediction"])
def predict_single_customer(request: CustomerRequest):
    """
    Predict churn probability for a single customer.

    Returns probability, binary prediction, risk tier, and top risk factors.
    Use the Swagger UI (/docs) to test with the pre-filled example.
    """
    t0 = time.time()
    try:
        customer_dict = request.model_dump(exclude={"threshold"})
        result = predict.predict_single(customer_dict, threshold=request.threshold)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

    result["latency_ms"] = round((time.time() - t0) * 1000, 2)
    return result


@app.post("/batch-predict", tags=["Prediction"])
def predict_batch(request: BatchRequest):
    """
    Predict churn for a batch of customers (up to 1000).

    Returns a list of predictions plus aggregate statistics.
    """
    if len(request.customers) > 1000:
        raise HTTPException(status_code=400, detail="Batch size limited to 1000 customers.")

    t0 = time.time()
    try:
        customer_dicts = [c.model_dump(exclude={"threshold"}) for c in request.customers]
        results = predict.predict_batch(customer_dicts, threshold=request.threshold)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch prediction failed: {str(e)}")

    # Aggregate stats
    probs = [r["churn_probability"] for r in results]
    n_predicted_churn = sum(r["churn_prediction"] for r in results)
    risk_counts = {"high": 0, "medium": 0, "low": 0}
    for r in results:
        risk_counts[r["risk_tier"]] += 1

    total_ms = round((time.time() - t0) * 1000, 2)

    return {
        "predictions": results,
        "summary": {
            "n_customers":         len(results),
            "n_predicted_churn":   n_predicted_churn,
            "churn_rate_predicted": round(n_predicted_churn / len(results), 4),
            "avg_churn_probability": round(sum(probs) / len(probs), 4),
            "risk_distribution":   risk_counts,
            "total_latency_ms":    total_ms,
            "avg_latency_ms":      round(total_ms / len(results), 3),
        }
    }
