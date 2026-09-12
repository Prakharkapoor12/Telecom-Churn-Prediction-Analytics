"""Section 03 — Models: leaderboard table + SHAP table + pipeline strip."""
from dash import html, dcc
import plotly.graph_objects as go


CYAN = "#22d3ee"
FG = "#e4e4e4"
FG_DIM = "#a8a8a8"
FG_MUTED = "#6e6e6e"


LEADERBOARD = [
    {"rank": 1, "model": "LightGBM",          "variant": "tuned",   "auc": 0.8471, "is_champ": True,  "params": "1024",  "time": "2m 14s"},
    {"rank": 2, "model": "LogisticRegression","variant": "default", "auc": 0.8465, "is_champ": False, "params": "47",    "time": "0.8s"},
    {"rank": 3, "model": "LogisticRegression","variant": "weighted","auc": 0.8465, "is_champ": False, "params": "47",    "time": "0.9s"},
    {"rank": 4, "model": "LogisticRegression","variant": "tuned",   "auc": 0.8454, "is_champ": False, "params": "47",    "time": "12s"},
    {"rank": 5, "model": "XGBoost",           "variant": "tuned",   "auc": 0.8454, "is_champ": False, "params": "843",   "time": "1m 47s"},
    {"rank": 6, "model": "RandomForest",      "variant": "default", "auc": 0.8429, "is_champ": False, "params": "100",   "time": "3.2s"},
    {"rank": 7, "model": "XGBoost",           "variant": "default", "auc": 0.8380, "is_champ": False, "params": "100",   "time": "1.8s"},
    {"rank": 8, "model": "LightGBM",          "variant": "default", "auc": 0.8303, "is_champ": False, "params": "100",   "time": "0.9s"},
]


SHAP_FEATURES = [
    ("contract_two_year",       0.4632, "categorical"),
    ("charges_per_tenure",      0.4583, "engineered"),
    ("internet_fiber_optic",    0.2599, "categorical"),
    ("contract_one_year",       0.1734, "categorical"),
    ("tenure_months",           0.1550, "numeric"),
    ("paperless_billing",       0.1130, "boolean"),
    ("online_security",         0.1128, "categorical"),
    ("payment_electronic_check",0.1124, "categorical"),
]


def _leaderboard_table():
    """Real table, not a bar chart. Far more terminal-authentic."""
    return html.Table(
        [
            html.Thead(html.Tr([
                html.Th("#"),
                html.Th("model"),
                html.Th("variant"),
                html.Th("auc_roc", className="num"),
                html.Th("Δ_champ", className="num"),
                html.Th("params", className="num"),
                html.Th("fit_time", className="num"),
            ])),
            html.Tbody([
                html.Tr(
                    [
                        html.Td(f"{r['rank']:02d}"),
                        html.Td(r['model']),
                        html.Td(r['variant'], style={"color": FG_MUTED}),
                        html.Td(f"{r['auc']:.4f}", className="num"),
                        html.Td(
                            html.Span(
                                "—" if r['is_champ'] else f"−{0.8471 - r['auc']:.4f}",
                                className="delta-down" if not r['is_champ'] else "",
                                style={"color": CYAN} if r['is_champ'] else {},
                            ),
                            className="num",
                        ),
                        html.Td(r['params'], className="num"),
                        html.Td(r['time'], className="num"),
                    ],
                    className="row-champ" if r['is_champ'] else "",
                )
                for r in LEADERBOARD
            ]),
        ],
        className="data-table",
    )


def _shap_bar_inline(value, max_value):
    """Inline ASCII-ish bar representation."""
    pct = value / max_value
    width = int(pct * 100)
    return html.Div(
        html.Div(style={
            "width": f"{width}%",
            "height": "6px",
            "background": CYAN,
            "opacity": 0.4 + 0.6 * pct,
        }),
        style={
            "width": "100%",
            "height": "6px",
            "background": "rgba(255,255,255,0.04)",
        }
    )


def _shap_table():
    max_val = max(v for _, v, _ in SHAP_FEATURES)
    return html.Table(
        [
            html.Thead(html.Tr([
                html.Th("rank"),
                html.Th("feature"),
                html.Th("|shap|", className="num"),
                html.Th("magnitude"),
            ])),
            html.Tbody([
                html.Tr([
                    html.Td(f"{i+1:02d}"),
                    html.Td(name),
                    html.Td(f"{val:.4f}", className="num", style={"color": CYAN}),
                    html.Td(_shap_bar_inline(val, max_val), style={"width": "120px"}),
                ])
                for i, (name, val, _) in enumerate(SHAP_FEATURES)
            ]),
        ],
        className="data-table",
    )


def _pipeline_strip():
    stages = [
        ("01", "SOURCE",   "SQLite · 7K rows"),
        ("02", "FEATURES", "encode · derive · scale"),
        ("03", "TRAIN",    "8 models compared"),
        ("04", "TUNE",     "Optuna · 50 trials"),
        ("05", "EXPLAIN",  "SHAP TreeExplainer"),
        ("06", "DECIDE",   "threshold sweep · cost-opt"),
        ("07", "DEPLOY",   "FastAPI + Docker"),
    ]
    return html.Div(
        [
            html.Div(
                [
                    html.Div(f"{num} · {step}", className="pipeline-step-num"),
                    html.Div(meta.split(" · ")[0], className="pipeline-step-name"),
                    html.Div(meta, className="pipeline-step-meta"),
                ],
                className="pipeline-step",
            )
            for num, step, meta in stages
        ],
        className="pipeline-strip",
    )


def render():
    return html.Section(
        [
            html.Div(
                [
                    html.H2(
                        [html.Span("03 //", className="sec-title-prefix"), "MODELS · 8 TRAINED · 1 KEPT"],
                        className="sec-title",
                    ),
                    html.Span("80/20 stratified · seed=42 · roc-auc primary", className="sec-meta"),
                ],
                className="sec-header",
            ),

            # Pipeline strip
            html.Div(_pipeline_strip(), className="mb-4"),

            # Leaderboard + SHAP side by side
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span([html.Span("//", className="pfx"), "leaderboard.holdout"],
                                              className="panel-head-title"),
                                    html.Span("auc-roc · same split", className="panel-head-meta"),
                                ],
                                className="panel-head",
                            ),
                            html.Div(_leaderboard_table(), className="panel-body-flush"),
                        ],
                        className="panel",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span([html.Span("//", className="pfx"), "shap.top_features"],
                                              className="panel-head-title"),
                                    html.Span("mean |shap| · lgbm.tuned", className="panel-head-meta"),
                                ],
                                className="panel-head",
                            ),
                            html.Div(_shap_table(), className="panel-body-flush"),
                        ],
                        className="panel",
                    ),
                ],
                className="grid-7-5 mb-4",
            ),

            # 3 takeaway panels
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                html.Span([html.Span("//", className="pfx"), "FINDING.01"],
                                          className="panel-head-title"),
                                className="panel-head",
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        "Tuned LightGBM won — barely.",
                                        className="finding-title",
                                    ),
                                    html.Div(
                                        "After 50 Optuna trials, beat the LR baseline by 0.0006 AUC. "
                                        "Bayesian search converged ~3× faster than grid search.",
                                        className="finding-body",
                                    ),
                                ],
                                className="panel-body finding-body-wrap",
                            ),
                        ],
                        className="panel",
                    ),
                    html.Div(
                        [
                            html.Div(
                                html.Span([html.Span("//", className="pfx"), "FINDING.02"],
                                          className="panel-head-title"),
                                className="panel-head",
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        "LR almost won.",
                                        className="finding-title",
                                    ),
                                    html.Div(
                                        "Strong feature engineering pushed logistic regression to AUC 0.8465 "
                                        "— within 0.0006 of state-of-the-art ensemble. Linear, interpretable, "
                                        "100× faster to fit. Always start here.",
                                        className="finding-body",
                                    ),
                                ],
                                className="panel-body finding-body-wrap",
                            ),
                        ],
                        className="panel",
                    ),
                    html.Div(
                        [
                            html.Div(
                                html.Span([html.Span("//", className="pfx"), "FINDING.03"],
                                          className="panel-head-title"),
                                className="panel-head",
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        "Calibration kept.",
                                        className="finding-title",
                                    ),
                                    html.Div(
                                        "Tested SMOTE, undersampling, class weights. SMOTE broke calibration "
                                        "without raising AUC. Chose class weights to keep predicted probabilities "
                                        "meaningful for threshold optimization.",
                                        className="finding-body",
                                    ),
                                ],
                                className="panel-body finding-body-wrap",
                            ),
                        ],
                        className="panel",
                    ),
                ],
                className="grid-3",
            ),
        ],
        id="sec-models",
        className="panel-section",
    )
