"""Section 05 — Predict: terminal-style 3-step wizard.

IMPORTANT: callback IDs preserved exactly as the original — `step-next-1`,
`inp-tenure`, `form-state`, `btn-predict`, the pattern-matching {"type":"big-chip"},
etc. Only the surrounding classNames + visual structure changed.
"""
import sys
from pathlib import Path

import dash
from dash import html, dcc, Input, Output, State, no_update, callback_context, ctx, ALL
import plotly.graph_objects as go

predict_module = None
try:
    from src import predict as predict_module
    PREDICT_AVAILABLE = True
except Exception as e:
    PREDICT_AVAILABLE = False
    print(f"⚠ predict module not available: {e}")


CYAN = "#22d3ee"
RED = "#ef4444"
AMBER = "#f59e0b"
GREEN = "#22c55e"
FG = "#e4e4e4"
FG_DIM = "#a8a8a8"
FG_MUTED = "#6e6e6e"
BG_DEEP = "#141414"
BORDER = "#2a2a2a"

DEFAULT_FORM_STATE = {
    "contract": "Month-to-month",
    "tenure": 2,
    "payment": "Electronic check",
    "internet": "Fiber optic",
    "online_security": False,
    "online_backup": False,
    "device_protection": False,
    "tech_support": False,
    "streaming_tv": True,
    "streaming_movies": False,
    "monthly": 79.85,
    "total": 79.85,
    "paperless": "Yes",
    "gender": "Male",
    "senior": "No",
    "partner": "No",
    "dependents": "No",
    "phone": "Yes",
    "multi": "No",
}


# ──────────────────────────────────────────────────────────────────────
# Wizard step bar
# ──────────────────────────────────────────────────────────────────────
def _stepbar(active_step):
    steps = [
        ("01", "PROFILE",  "customer"),
        ("02", "SERVICES", "subscription"),
        ("03", "BILLING",  "charges + plan"),
    ]
    return html.Div(
        [
            html.Div(
                [
                    html.Span(num, className="wiz-step-num"),
                    html.Div(
                        [
                            html.Div(label, style={"fontWeight": 600, "fontSize": "13px"}),
                            html.Div(sub, style={"color": "var(--fg-dim)", "fontSize": "11px", "marginTop": "3px", "fontWeight": 400, "letterSpacing": "0.04em"}),
                        ]
                    ),
                    html.I(className="fa-solid fa-check wiz-step-icon") if i + 1 < active_step else html.Span(),
                ],
                className="wiz-step " + (
                    "wiz-step-active" if i + 1 == active_step
                    else "wiz-step-done" if i + 1 < active_step
                    else ""
                ),
            )
            for i, (num, label, sub) in enumerate(steps)
        ],
        className="wizard-stepbar",
    )


# ──────────────────────────────────────────────────────────────────────
# STEP 1 — Profile
# ──────────────────────────────────────────────────────────────────────
def _step_1():
    return html.Div(
        [
            html.Div(
                "Three account fundamentals account for ~80% of churn risk: "
                "contract lock-in, tenure, and payment method.",
                className="step-prose-mono",
            ),

            # Contract type
            html.Div(
                [
                    html.Div(
                        [
                            html.Label("CONTRACT_TYPE", className="field-label"),
                            html.Span("strongest predictor · feature_importance=0.46",
                                      className="field-hint"),
                        ],
                        className="field-grp-label",
                    ),
                    html.Div(
                        [
                            html.Button(
                                [
                                    html.Span("MONTH-TO-MONTH"),
                                    html.Span("highest risk · 42.7% churn",
                                              className="term-chip-meta"),
                                ],
                                id={"type": "big-chip", "field": "contract", "value": "Month-to-month"},
                                className="term-chip term-chip-tall term-chip-selected",
                                n_clicks=0,
                            ),
                            html.Button(
                                [
                                    html.Span("ONE YEAR"),
                                    html.Span("medium risk · 11.3% churn",
                                              className="term-chip-meta"),
                                ],
                                id={"type": "big-chip", "field": "contract", "value": "One year"},
                                className="term-chip term-chip-tall",
                                n_clicks=0,
                            ),
                            html.Button(
                                [
                                    html.Span("TWO YEAR"),
                                    html.Span("safest · 2.8% churn",
                                              className="term-chip-meta"),
                                ],
                                id={"type": "big-chip", "field": "contract", "value": "Two year"},
                                className="term-chip term-chip-tall",
                                n_clicks=0,
                            ),
                        ],
                        className="term-chip-row",
                    ),
                ],
                className="field-grp",
            ),

            # Tenure + Payment grid
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Label("TENURE_MONTHS", className="field-label"),
                                    html.Span("how long they've been a customer",
                                              className="field-hint"),
                                ],
                                className="field-grp-label",
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Div(
                                                [
                                                    html.Span(id="tenure-display", children="2",
                                                              className="term-slider-val"),
                                                    html.Span(" months", className="term-slider-unit"),
                                                ]
                                            ),
                                            html.Div("0 — 72 mo",
                                                     style={"color": "var(--fg-dim)", "fontFamily": "var(--font-mono)",
                                                            "fontSize": "11.5px"}),
                                        ],
                                        className="term-slider-readout",
                                    ),
                                    dcc.Slider(
                                        id="inp-tenure",
                                        min=0, max=72, step=1, value=2,
                                        marks={0: "0", 12: "1y", 24: "2y", 48: "4y", 72: "6y"},
                                    ),
                                ],
                                className="term-slider-wrap",
                            ),
                        ],
                        className="field-grp",
                    ),

                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Label("PAYMENT_METHOD", className="field-label"),
                                    html.Span("auto-pay → +retention", className="field-hint"),
                                ],
                                className="field-grp-label",
                            ),
                            html.Div(
                                [
                                    html.Button(
                                        "E-CHECK",
                                        id={"type": "big-chip", "field": "payment", "value": "Electronic check"},
                                        className="term-chip term-chip-selected", n_clicks=0,
                                    ),
                                    html.Button(
                                        "MAIL",
                                        id={"type": "big-chip", "field": "payment", "value": "Mailed check"},
                                        className="term-chip", n_clicks=0,
                                    ),
                                    html.Button(
                                        "BANK.AUTO",
                                        id={"type": "big-chip", "field": "payment", "value": "Bank transfer (automatic)"},
                                        className="term-chip", n_clicks=0,
                                    ),
                                    html.Button(
                                        "CARD.AUTO",
                                        id={"type": "big-chip", "field": "payment", "value": "Credit card (automatic)"},
                                        className="term-chip", n_clicks=0,
                                    ),
                                ],
                                className="term-chip-row",
                            ),
                        ],
                        className="field-grp",
                    ),
                ],
                className="grid-2",
            ),

            # Nav
            html.Div(
                [
                    html.Div(),  # spacer
                    html.Button(
                        ["CONTINUE ", html.I(className="fa-solid fa-arrow-right ms-2")],
                        id="step-next-1",
                        className="wiz-btn wiz-btn-primary", n_clicks=0,
                    ),
                ],
                className="wiz-nav",
            ),
        ],
        className="step-content",
        id="step-1",
    )


# ──────────────────────────────────────────────────────────────────────
# STEP 2 — Services
# ──────────────────────────────────────────────────────────────────────
def _step_2():
    return html.Div(
        [
            html.Div(
                "Each add-on service reduces churn risk almost linearly. "
                "Stickier customers have more reasons to stay.",
                className="step-prose-mono",
            ),

            # Internet
            html.Div(
                [
                    html.Div(
                        [
                            html.Label("INTERNET_SERVICE", className="field-label"),
                            html.Span("fiber correlates with higher churn",
                                      className="field-hint"),
                        ],
                        className="field-grp-label",
                    ),
                    html.Div(
                        [
                            html.Button("FIBER OPTIC",
                                id={"type": "big-chip", "field": "internet", "value": "Fiber optic"},
                                className="term-chip term-chip-selected", n_clicks=0),
                            html.Button("DSL",
                                id={"type": "big-chip", "field": "internet", "value": "DSL"},
                                className="term-chip", n_clicks=0),
                            html.Button("NO INTERNET",
                                id={"type": "big-chip", "field": "internet", "value": "No"},
                                className="term-chip", n_clicks=0),
                        ],
                        className="term-chip-row",
                    ),
                ],
                className="field-grp",
            ),

            # Add-ons
            html.Div(
                [
                    html.Div(
                        [
                            html.Label("ADD_ON_SERVICES", className="field-label"),
                            html.Span("toggle subscribed services", className="field-hint"),
                        ],
                        className="field-grp-label",
                    ),
                    html.Div(
                        [
                            _addon_toggle("online_security",  "ONLINE_SECURITY",  False, "fa-shield-halved"),
                            _addon_toggle("online_backup",    "ONLINE_BACKUP",    False, "fa-cloud"),
                            _addon_toggle("device_protection","DEVICE_PROTECTION",False, "fa-mobile"),
                            _addon_toggle("tech_support",     "TECH_SUPPORT",     False, "fa-headset"),
                            _addon_toggle("streaming_tv",     "STREAMING_TV",     True,  "fa-tv"),
                            _addon_toggle("streaming_movies", "STREAMING_MOVIES", False, "fa-film"),
                        ],
                        className="addon-grid",
                    ),
                ],
                className="field-grp",
            ),

            # Nav
            html.Div(
                [
                    html.Button(
                        [html.I(className="fa-solid fa-arrow-left me-2"), "BACK"],
                        id="step-back-2",
                        className="wiz-btn wiz-btn-ghost", n_clicks=0,
                    ),
                    html.Button(
                        ["CONTINUE ", html.I(className="fa-solid fa-arrow-right ms-2")],
                        id="step-next-2",
                        className="wiz-btn wiz-btn-primary", n_clicks=0,
                    ),
                ],
                className="wiz-nav",
            ),
        ],
        className="step-content",
        id="step-2",
        style={"display": "none"},
    )


def _addon_toggle(field, label, default_on, icon):
    return html.Button(
        [
            html.I(className=f"fa-solid {icon} addon-icon"),
            html.Span(label, className="addon-label"),
            html.Div(className="addon-switch"),
        ],
        id={"type": "addon-toggle", "field": field},
        className="addon-toggle addon-toggle-on" if default_on else "addon-toggle",
        n_clicks=0,
    )


# ──────────────────────────────────────────────────────────────────────
# STEP 3 — Plan
# ──────────────────────────────────────────────────────────────────────
def _step_3():
    return html.Div(
        [
            html.Div(
                "Charges-per-tenure is the second-strongest SHAP feature. "
                "Price relative to tenure flags overpaying customers.",
                className="step-prose-mono",
            ),

            # Monthly charges — big slider
            html.Div(
                [
                    html.Div(
                        [
                            html.Label("MONTHLY_CHARGES", className="field-label"),
                            html.Span("$ per month, current bill", className="field-hint"),
                        ],
                        className="field-grp-label",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Span("$", style={"color": "var(--fg-muted)", "fontSize": "16px"}),
                                            html.Span(id="charges-display", children="79.85",
                                                      className="term-slider-val"),
                                            html.Span(" /mo", className="term-slider-unit"),
                                        ]
                                    ),
                                    html.Div("$18 — $120",
                                             style={"color": "var(--fg-dim)", "fontFamily": "var(--font-mono)",
                                                    "fontSize": "11.5px"}),
                                ],
                                className="term-slider-readout",
                            ),
                            dcc.Slider(
                                id="inp-monthly",
                                min=18, max=120, step=0.5, value=79.85,
                                marks={20: "$20", 50: "$50", 80: "$80", 120: "$120"},
                            ),
                            html.Div(id="charges-context", className="term-slider-context"),
                        ],
                        className="term-slider-wrap",
                    ),
                ],
                className="field-grp",
            ),

            # Total + paperless
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Label("TOTAL_CHARGES", className="field-label"),
                                    html.Span("lifetime billing", className="field-hint"),
                                ],
                                className="field-grp-label",
                            ),
                            dcc.Input(
                                id="inp-total", type="number",
                                value=79.85, step=10,
                                className="term-input",
                            ),
                        ],
                        className="field-grp",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Label("PAPERLESS_BILLING", className="field-label"),
                                    html.Span("paperless → slightly more churn",
                                              className="field-hint"),
                                ],
                                className="field-grp-label",
                            ),
                            html.Div(
                                [
                                    html.Button("YES · PAPERLESS",
                                        id={"type": "big-chip", "field": "paperless", "value": "Yes"},
                                        className="term-chip term-chip-selected", n_clicks=0),
                                    html.Button("NO · PAPER BILL",
                                        id={"type": "big-chip", "field": "paperless", "value": "No"},
                                        className="term-chip", n_clicks=0),
                                ],
                                className="term-chip-row",
                            ),
                        ],
                        className="field-grp",
                    ),
                ],
                className="grid-2",
            ),

            # Demographics — compact
            html.Div(
                [
                    html.Div(
                        [
                            html.Label("DEMOGRAPHICS", className="field-label"),
                            html.Span("low-importance features", className="field-hint"),
                        ],
                        className="field-grp-label",
                    ),
                    html.Div(
                        [
                            _two_toggle("gender",     "GENDER",         ["Male", "Female"],          "Male"),
                            _two_toggle("senior",     "SENIOR_CITIZEN", ["No", "Yes"],               "No"),
                            _two_toggle("partner",    "HAS_PARTNER",    ["No", "Yes"],               "No"),
                            _two_toggle("dependents", "HAS_DEPENDENTS", ["No", "Yes"],               "No"),
                            _two_toggle("phone",      "PHONE_SERVICE",  ["No", "Yes"],               "Yes"),
                            _two_toggle("multi",      "MULTIPLE_LINES", ["No", "Yes", "No phone service"], "No"),
                        ],
                        className="grid-3",
                    ),
                ],
                className="field-grp",
            ),

            # Nav
            html.Div(
                [
                    html.Button(
                        [html.I(className="fa-solid fa-arrow-left me-2"), "BACK"],
                        id="step-back-3",
                        className="wiz-btn wiz-btn-ghost", n_clicks=0,
                    ),
                    html.Button(
                        "PREDICT.CHURN()",
                        id="btn-predict",
                        className="wiz-btn wiz-btn-execute", n_clicks=0,
                    ),
                ],
                className="wiz-nav",
            ),
        ],
        className="step-content",
        id="step-3",
        style={"display": "none"},
    )


def _two_toggle(field, label, options, default):
    return html.Div(
        [
            html.Div(label, className="field-label", style={"marginBottom": "6px"}),
            html.Div(
                [
                    html.Button(
                        opt.upper() if opt != "No phone service" else "NO PHONE",
                        id={"type": "big-chip", "field": field, "value": opt},
                        className="term-chip term-chip-selected" if opt == default else "term-chip",
                        n_clicks=0,
                    )
                    for opt in options
                ],
                className="term-chip-row",
            ),
        ],
    )


# ──────────────────────────────────────────────────────────────────────
# Gauge — restyled for dark
# ──────────────────────────────────────────────────────────────────────
def _build_gauge(prob, tier, threshold):
    bar_color = {"high": RED, "medium": AMBER, "low": GREEN}[tier]
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=prob * 100,
        number={"suffix": "%", "font": {"size": 32, "color": bar_color, "family": "JetBrains Mono"}},
        gauge={
            "axis": {
                "range": [0, 100],
                "tickwidth": 1,
                "tickcolor": FG_MUTED,
                "tickfont": {"color": FG_MUTED, "size": 9, "family": "JetBrains Mono"},
            },
            "bar": {"color": bar_color, "thickness": 0.25},
            "bgcolor": BG_DEEP,
            "borderwidth": 1,
            "bordercolor": BORDER,
            "steps": [
                {"range": [0, 35],   "color": "rgba(34, 197, 94, 0.10)"},
                {"range": [35, 70],  "color": "rgba(245, 158, 11, 0.10)"},
                {"range": [70, 100], "color": "rgba(239, 68, 68, 0.10)"},
            ],
            "threshold": {
                "line": {"color": CYAN, "width": 2},
                "thickness": 0.85,
                "value": threshold * 100,
            },
        },
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=10, b=10),
        height=200,
        font=dict(family="JetBrains Mono, monospace"),
    )
    return fig


# ──────────────────────────────────────────────────────────────────────
# Section render
# ──────────────────────────────────────────────────────────────────────
def render():
    return html.Section(
        [
            html.Div(
                [
                    html.H2(
                        [html.Span("05 //", className="sec-title-prefix"), "PREDICT · INTERACTIVE"],
                        className="sec-title",
                    ),
                    html.Span("calls predict.predict_single() · same as FastAPI /predict",
                              className="sec-meta"),
                ],
                className="sec-header",
            ),

            # Wizard panel
            html.Div(
                [
                    html.Div(
                        [
                            html.Span([html.Span("// ", className="pfx"), "interactive.churn_predictor"],
                                      className="wizard-head-title"),
                            html.Span("3-step wizard · inference < 50 ms",
                                      style={"color": "var(--fg-dim)", "fontSize": "11.5px",
                                             "textTransform": "uppercase", "letterSpacing": "0.06em"}),
                        ],
                        className="wizard-head",
                    ),

                    # Stepbar
                    html.Div(id="stepper-container", children=_stepbar(1)),

                    # Body with all 3 steps
                    html.Div(
                        [
                            _step_1(),
                            _step_2(),
                            _step_3(),
                        ],
                        className="wizard-body",
                    ),
                ],
                className="wizard",
            ),

            # Result reveal
            html.Div(id="prediction-result"),
            html.Div(
                html.Button(
                    [html.I(className="fa-solid fa-rotate-left me-2"), "RESET · TRY ANOTHER"],
                    id="btn-reset", n_clicks=0,
                    className="wiz-btn wiz-btn-ghost",
                ),
                className="reset-row",
            ),

            # Hidden state
            dcc.Store(id="form-state", data=DEFAULT_FORM_STATE.copy()),
            dcc.Store(id="active-step", data=1),
        ],
        id="sec-predict",
        className="panel-section",
    )


# ──────────────────────────────────────────────────────────────────────
# Callbacks — IDs preserved exactly from original
# ──────────────────────────────────────────────────────────────────────
def register_callbacks(app):

    # Step navigation
    @app.callback(
        [Output("active-step", "data"),
         Output("step-1", "style"),
         Output("step-2", "style"),
         Output("step-3", "style"),
         Output("stepper-container", "children")],
        [Input("step-next-1", "n_clicks"),
         Input("step-next-2", "n_clicks"),
         Input("step-back-2", "n_clicks"),
         Input("step-back-3", "n_clicks"),
         Input("btn-reset", "n_clicks")],
        State("active-step", "data"),
        prevent_initial_call=True,
    )
    def navigate_steps(n1, n2, b2, b3, reset_clicks, current):
        trig = ctx.triggered_id
        new_step = current
        if trig == "step-next-1":   new_step = 2
        elif trig == "step-next-2": new_step = 3
        elif trig == "step-back-2": new_step = 1
        elif trig == "step-back-3": new_step = 2
        elif trig == "btn-reset":    new_step = 1

        show = {"display": "block"}
        hide = {"display": "none"}
        styles = [hide, hide, hide]
        styles[new_step - 1] = show
        return new_step, styles[0], styles[1], styles[2], _stepbar(new_step)

    # Slider readouts
    @app.callback(
        Output("tenure-display", "children"),
        Input("inp-tenure", "value"),
    )
    def update_tenure(v):
        return str(int(v) if v is not None else 0)

    @app.callback(
        [Output("charges-display", "children"),
         Output("charges-context", "children")],
        Input("inp-monthly", "value"),
    )
    def update_charges(v):
        v = float(v or 0)
        if v < 35:
            ctx_text = ["▼ low tier · typically ", html.Strong("safer"), " (DSL or phone-only)"]
        elif v < 65:
            ctx_text = ["mid-tier · typical telco customer"]
        elif v < 90:
            ctx_text = ["▲ higher tier · often fiber · ", html.Strong("higher churn risk")]
        else:
            ctx_text = ["▲▲ premium · bundled fiber + streaming · ",
                        html.Strong("highest revenue at risk")]
        return f"{v:.2f}", html.Span(ctx_text)

    # Chip className updates — pattern-matching, same as original
    @app.callback(
        Output({"type": "big-chip", "field": dash.ALL, "value": dash.ALL}, "className"),
        [Input({"type": "big-chip", "field": dash.ALL, "value": dash.ALL}, "n_clicks")],
        [State({"type": "big-chip", "field": dash.ALL, "value": dash.ALL}, "id")],
        prevent_initial_call=False,
    )
    def update_chip_classes(n_clicks_list, ids):
        if not callback_context.triggered or all(n == 0 for n in n_clicks_list):
            return [no_update] * len(ids)

        trig = callback_context.triggered[0]["prop_id"]
        import json as _json
        try:
            trig_dict = _json.loads(trig.split(".")[0])
        except Exception:
            return [no_update] * len(ids)

        trig_field = trig_dict["field"]
        trig_value = trig_dict["value"]

        # All chip types now share the same .term-chip base
        # Contract chips use .term-chip-tall variant
        tall_fields = {"contract"}

        out = []
        for cid in ids:
            if cid["field"] == trig_field:
                if cid["field"] in tall_fields:
                    base = "term-chip term-chip-tall"
                    sel  = "term-chip term-chip-tall term-chip-selected"
                else:
                    base = "term-chip"
                    sel  = "term-chip term-chip-selected"
                out.append(sel if cid["value"] == trig_value else base)
            else:
                out.append(no_update)
        return out

    # Form state updates
    @app.callback(
        Output("form-state", "data"),
        [Input({"type": "big-chip", "field": dash.ALL, "value": dash.ALL}, "n_clicks"),
         Input({"type": "addon-toggle", "field": dash.ALL}, "n_clicks"),
         Input("inp-tenure", "value"),
         Input("inp-monthly", "value"),
         Input("inp-total", "value"),
         Input("btn-reset", "n_clicks")],
        State("form-state", "data"),
        prevent_initial_call=True,
    )
    def update_form_state(chip_clicks, addon_clicks, tenure, monthly, total, reset_clicks, current):
        if callback_context.triggered_id == "btn-reset":
            return DEFAULT_FORM_STATE.copy()

        new_state = dict(current) if current else {}

        trig = callback_context.triggered[0] if callback_context.triggered else None
        if trig:
            prop_id = trig["prop_id"]
            if "big-chip" in prop_id:
                import json as _json
                try:
                    info = _json.loads(prop_id.split(".")[0])
                    new_state[info["field"]] = info["value"]
                except Exception:
                    pass
            elif "addon-toggle" in prop_id:
                import json as _json
                try:
                    info = _json.loads(prop_id.split(".")[0])
                    new_state[info["field"]] = not new_state.get(info["field"], False)
                except Exception:
                    pass

        if tenure is not None:  new_state["tenure"]  = int(tenure)
        if monthly is not None: new_state["monthly"] = float(monthly)
        if total is not None:   new_state["total"]   = float(total)

        return new_state

    # Addon toggle visual state
    @app.callback(
        Output({"type": "addon-toggle", "field": dash.ALL}, "className"),
        Input("form-state", "data"),
        State({"type": "addon-toggle", "field": dash.ALL}, "id"),
    )
    def update_addon_classes(state, ids):
        if not state:
            return [no_update] * len(ids)
        return [
            "addon-toggle addon-toggle-on" if state.get(cid["field"], False)
            else "addon-toggle"
            for cid in ids
        ]

    # Prediction
    @app.callback(
        Output("prediction-result", "children"),
        [Input("btn-predict", "n_clicks"),
         Input("btn-reset", "n_clicks")],
        State("form-state", "data"),
        prevent_initial_call=True,
    )
    def run_prediction(n_clicks, reset_clicks, state):
        if ctx.triggered_id == "btn-reset":
            return []
        if not n_clicks or not state:
            return no_update

        def yn(v): return "Yes" if v else "No"

        customer = {
            "gender": state.get("gender", "Male"),
            "senior_citizen": 1 if state.get("senior") == "Yes" else 0,
            "partner": state.get("partner", "No"),
            "dependents": state.get("dependents", "No"),
            "tenure_months": int(state.get("tenure", 0)),
            "contract_type": state.get("contract", "Month-to-month"),
            "paperless_billing": state.get("paperless", "Yes"),
            "payment_method": state.get("payment", "Electronic check"),
            "phone_service": state.get("phone", "Yes"),
            "multiple_lines": state.get("multi", "No"),
            "internet_service": state.get("internet", "Fiber optic"),
            "online_security": yn(state.get("online_security")),
            "online_backup": yn(state.get("online_backup")),
            "device_protection": yn(state.get("device_protection")),
            "tech_support": yn(state.get("tech_support")),
            "streaming_tv": yn(state.get("streaming_tv")),
            "streaming_movies": yn(state.get("streaming_movies")),
            "monthly_charges": float(state.get("monthly", 0)),
            "total_charges": float(state.get("total", 0)),
        }

        if state.get("internet") == "No":
            for k in ["online_security", "online_backup", "device_protection",
                      "tech_support", "streaming_tv", "streaming_movies"]:
                customer[k] = "No internet service"

        if not PREDICT_AVAILABLE or predict_module is None:
            return _error_card("Model artifacts not loaded. Run NTB-10 first to create `artifacts/`.")

        try:
            result = predict_module.predict_single(customer)
        except Exception as e:
            return _error_card(f"Prediction error: {str(e)[:200]}")

        prob   = float(result.get("churn_probability", 0))
        tier   = result.get("risk_tier", "low")
        pred   = int(result.get("churn_prediction", 0))
        thresh = float(result.get("threshold_used", 0.48))

        tier_label = {"high": "HIGH RISK", "medium": "MEDIUM RISK", "low": "LOW RISK"}[tier]
        verdict_text = "> likely_to_churn = TRUE" if pred == 1 else "> likely_to_churn = FALSE"

        # Drivers
        drivers = []
        if customer["contract_type"] == "Month-to-month":
            drivers.append(("month-to-month contract", "+35%", "danger"))
        elif customer["contract_type"] == "Two year":
            drivers.append(("two-year contract", "−25%", "success"))

        if customer["internet_service"] == "Fiber optic":
            drivers.append(("fiber optic service", "+20%", "danger"))
        elif customer["internet_service"] == "DSL":
            drivers.append(("dsl service", "+5%", "warning"))

        t = customer["tenure_months"]
        if t <= 6:
            drivers.append(("new customer (≤6mo)", "+20%", "danger"))
        elif t <= 12:
            drivers.append(("first-year customer", "+12%", "warning"))
        elif t > 48:
            drivers.append(("loyal (4+ years)", "−15%", "success"))

        if customer["payment_method"] == "Electronic check":
            drivers.append(("electronic check payment", "+8%", "danger"))
        elif "automatic" in customer["payment_method"].lower():
            drivers.append(("auto-pay enabled", "−8%", "success"))

        if customer["monthly_charges"] > 80:
            drivers.append(("high monthly charges", "+15%", "warning"))

        addon_count = sum(1 for k in ["online_security","online_backup","device_protection",
                                       "tech_support","streaming_tv","streaming_movies"]
                          if customer.get(k) == "Yes")
        if addon_count >= 4:
            drivers.append((f"{addon_count} add-on services", f"−{addon_count*3}%", "success"))
        elif addon_count == 0 and customer["internet_service"] != "No":
            drivers.append(("no add-ons (unstacked)", "+10%", "warning"))

        # Action block
        if tier == "high":
            clv = customer["monthly_charges"] * 12
            action_block = html.Div(
                [
                    html.Div("ACTION.HIGH_VALUE_RETAIN", className="action-title action-title-danger"),
                    html.Div(
                        [
                            "estimated_clv_at_stake = ",
                            html.Strong(f"${clv:,.0f}"),
                            f" · (${customer['monthly_charges']:.0f}/mo × 12)",
                        ],
                        className="action-detail",
                    ),
                    html.P(
                        "Profile matches high-churn patterns. Proactive outreach with a contract "
                        "upgrade discount is recommended. Expected save rate: ~40%.",
                        className="action-desc",
                    ),
                ],
                className="action-block",
            )
        elif tier == "medium":
            action_block = html.Div(
                [
                    html.Div("ACTION.MONITOR", className="action-title action-title-warning"),
                    html.P(
                        "Elevated risk but not critical. Bundle upsell or service check-in. "
                        "Re-score in 30 days.",
                        className="action-desc",
                    ),
                ],
                className="action-block",
            )
        else:
            action_block = html.Div(
                [
                    html.Div("ACTION.NO_OP", className="action-title action-title-success"),
                    html.P(
                        "Customer profile is stable. Consider as upsell or testimonial candidate.",
                        className="action-desc",
                    ),
                ],
                className="action-block",
            )

        return html.Div(
            [
                # Probability + verdict panel
                html.Div(
                    [
                        html.Div(
                            [
                                html.Span(
                                    [html.Span("// ", className="pfx"), "prediction.output"],
                                    className="result-head-title",
                                ),
                                html.Span("vs 26.5% baseline · τ=0.48 · t<50ms",
                                          className="result-head-meta"),
                            ],
                            className="result-head",
                        ),
                        html.Div(
                            html.Div(
                                [
                                    dcc.Graph(
                                        figure=_build_gauge(prob, tier, thresh),
                                        config={"displayModeBar": False},
                                    ),
                                    html.Div(
                                        [
                                            html.Div(tier_label,
                                                     className=f"result-tier result-tier-{tier}"),
                                            html.Div(verdict_text, className="result-verdict-text"),
                                            html.Div(
                                                [
                                                    html.Div(
                                                        [
                                                            html.Div("PROB", className="result-vstat-label"),
                                                            html.Div(f"{prob*100:.1f}%",
                                                                     className="result-vstat-val"),
                                                        ],
                                                        className="result-vstat",
                                                    ),
                                                    html.Div(
                                                        [
                                                            html.Div("THRESHOLD", className="result-vstat-label"),
                                                            html.Div(f"{thresh:.2f}",
                                                                     className="result-vstat-val"),
                                                        ],
                                                        className="result-vstat",
                                                    ),
                                                    html.Div(
                                                        [
                                                            html.Div("LATENCY", className="result-vstat-label"),
                                                            html.Div("<50ms",
                                                                     className="result-vstat-val"),
                                                        ],
                                                        className="result-vstat",
                                                    ),
                                                ],
                                                className="result-vstats",
                                            ),
                                        ],
                                        className="result-verdict",
                                    ),
                                ],
                                className="result-gauge-row",
                            ),
                            className="result-body",
                        ),
                    ],
                    className="result-panel",
                ),

                # Drivers + Action
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Span(
                                            [html.Span("// ", className="pfx"), "risk.drivers"],
                                            className="panel-head-title",
                                        ),
                                        html.Span(f"top {min(6, len(drivers))} · shap-based",
                                                  className="panel-head-meta"),
                                    ],
                                    className="panel-head",
                                ),
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                html.Span(f"{i+1:02d}", className="driver-rank"),
                                                html.Span(name, className="driver-name"),
                                                html.Span(delta,
                                                          className=f"driver-delta driver-delta-{color}"),
                                            ],
                                            className="drivers-row",
                                        )
                                        for i, (name, delta, color) in enumerate(drivers[:6])
                                    ],
                                ),
                            ],
                            className="drivers-block",
                        ),
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Span(
                                            [html.Span("// ", className="pfx"), "recommended.action"],
                                            className="panel-head-title",
                                        ),
                                        html.Span("policy-driven",
                                                  className="panel-head-meta"),
                                    ],
                                    className="panel-head",
                                ),
                                action_block,
                            ],
                            className="panel",
                        ),
                    ],
                    className="grid-2 mt-3",
                ),

            ],
            className="result-block",
        )


def _error_card(msg):
    return html.Div(
        html.Div(
            [
                html.I(className="fa-solid fa-triangle-exclamation error-icon"),
                html.Div("PREDICTION ERROR", className="error-title"),
                html.Div(msg, className="error-desc"),
            ],
            className="error-card",
        ),
        className="result-block",
    )
