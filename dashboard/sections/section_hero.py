"""Section 01 — Overview: terminal status panel + KPI grid."""
from dash import html, dcc
import plotly.graph_objects as go


def _spark():
    """Tight signal-line — no fill gradient, just a single thin trace."""
    fig = go.Figure(go.Scatter(
        x=list(range(24)),
        y=[28, 27, 28, 29, 30, 29, 31, 33, 32, 34, 36, 38, 41, 44, 47, 49,
           52, 55, 56, 59, 62, 64, 66, 67],
        mode="lines",
        line=dict(color="#22d3ee", width=1.2, shape="linear"),
        hoverinfo="skip",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=0, b=0),
        height=22,
        xaxis=dict(visible=False, fixedrange=True),
        yaxis=dict(visible=False, fixedrange=True),
        showlegend=False,
    )
    return fig


def render():
    return html.Section(
        [
            # Title bar
            html.Div(
                [
                    html.Span("OVERVIEW", className="hero-code"),
                    html.H1(
                        [
                            "telecom.churn.prediction",
                            html.Span(" / ", className="hero-title-sep"),
                            "v1.0",
                        ],
                        className="hero-title",
                    ),
                    html.Div(
                        [
                            html.Span("ML PIPELINE", className="hero-tag hero-tag-on"),
                            html.Span("FASTAPI", className="hero-tag"),
                            html.Span("DASH", className="hero-tag"),
                            html.Span("DOCKER", className="hero-tag"),
                        ],
                        className="hero-tags",
                    ),
                ],
                className="hero-titlebar",
            ),

            # KPI grid — 5 cells
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    "AUC-ROC",
                                    html.Span("HOLDOUT", className="kpi-trend kpi-trend-neut"),
                                ],
                                className="kpi-label",
                            ),
                            html.Div(["0.8471"], className="kpi-value kpi-value-cyan"),
                            html.Div("lgbm.tuned · 80/20 split", className="kpi-sub"),
                        ],
                        className="kpi",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    "MONTHLY VALUE",
                                    html.Span("+$7K vs τ=0.5", className="kpi-trend kpi-trend-up"),
                                ],
                                className="kpi-label",
                            ),
                            html.Div(
                                [
                                    "$326",
                                    html.Span("K", className="kpi-unit"),
                                ],
                                className="kpi-value",
                            ),
                            html.Div("retention.projected", className="kpi-sub"),
                        ],
                        className="kpi",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    "RECALL @ τ=0.48",
                                    html.Span("CHURNERS", className="kpi-trend kpi-trend-neut"),
                                ],
                                className="kpi-label",
                            ),
                            html.Div(
                                [
                                    "83",
                                    html.Span("%", className="kpi-unit"),
                                ],
                                className="kpi-value",
                            ),
                            html.Div("311 / 374 caught", className="kpi-sub"),
                        ],
                        className="kpi",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    "BASELINE CHURN",
                                    html.Span("ANNUAL", className="kpi-trend kpi-trend-down"),
                                ],
                                className="kpi-label",
                            ),
                            html.Div(
                                [
                                    "26.5",
                                    html.Span("%", className="kpi-unit"),
                                ],
                                className="kpi-value",
                            ),
                            html.Div("$1.67M revenue.at_risk", className="kpi-sub"),
                        ],
                        className="kpi",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    "MODELS TESTED",
                                    html.Span("KEPT 1", className="kpi-trend kpi-trend-neut"),
                                ],
                                className="kpi-label",
                            ),
                            html.Div("8", className="kpi-value"),
                            html.Div("Optuna · 50 trials", className="kpi-sub"),
                        ],
                        className="kpi",
                    ),
                ],
                className="kpi-grid",
            ),

            # Lede + model-card metadata strip
            html.Div(
                [
                    # Left: lede paragraph
                    html.P(
                        [
                            "An end-to-end ML system for telecom customer churn — ",
                            html.Strong("SQL analytics"), ", ",
                            html.Strong("feature engineering"), ", ",
                            html.Strong("8-model comparison"), ", ",
                            html.Strong("Optuna Bayesian tuning"), ", ",
                            html.Strong("SHAP explainability"),
                            ", and ",
                            html.Strong("cost-sensitive threshold optimization"),
                            ". Trained on IBM Telco Customer Churn (7,043 customers, "
                            "21 features). Deployed via FastAPI + Docker; explored "
                            "interactively below.",
                        ],
                        className="hero-lede",
                    ),

                    # Right: model-card metadata block
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span("DATASET", className="meta-key"),
                                    html.Span("IBM Telco Customer Churn",
                                              className="meta-val"),
                                ],
                                className="meta-row",
                            ),
                            html.Div(
                                [
                                    html.Span("TRAINING SET", className="meta-key"),
                                    html.Span("5,634 customers · 80%",
                                              className="meta-val"),
                                ],
                                className="meta-row",
                            ),
                            html.Div(
                                [
                                    html.Span("HOLDOUT SET", className="meta-key"),
                                    html.Span("1,409 customers · 20%",
                                              className="meta-val"),
                                ],
                                className="meta-row",
                            ),
                            html.Div(
                                [
                                    html.Span("FEATURES", className="meta-key"),
                                    html.Span("21 raw → 47 encoded",
                                              className="meta-val"),
                                ],
                                className="meta-row",
                            ),
                            html.Div(
                                [
                                    html.Span("LAST TRAINED", className="meta-key"),
                                    html.Span("2026-01-15",
                                              className="meta-val meta-val-cyan"),
                                ],
                                className="meta-row",
                            ),
                        ],
                        className="hero-meta",
                    ),
                ],
                className="hero-lede-row",
            ),

            html.Div(
                [
                    html.Span("// signal", className="spark-strip-key"),
                    html.Div(
                        dcc.Graph(
                            figure=_spark(),
                            config={"displayModeBar": False, "staticPlot": True},
                        ),
                        style={"width": "120px"},
                    ),
                    html.Span("churn.curve(t=24mo)", className="spark-strip-key"),
                    html.Span("· 0–6 mo bucket: ", className="spark-strip-key"),
                    html.Span("52.9% churn", className="spark-strip-val"),
                    html.Span("· 4+ years: ", className="spark-strip-key"),
                    html.Span("9.5% churn", className="spark-strip-val"),
                ],
                className="spark-strip",
            ),
        ],
        id="sec-overview",
        className="hero",
    )
