"""Section 04 — Business: cost-sensitive threshold optimization."""
from dash import html, dcc
import plotly.graph_objects as go
import numpy as np


CYAN = "#22d3ee"
CYAN_DIM = "#0891b2"
RED = "#ef4444"
AMBER = "#f59e0b"
GREEN = "#22c55e"
FG = "#e4e4e4"
FG_DIM = "#a8a8a8"
FG_MUTED = "#6e6e6e"
BG_DEEP = "#141414"
BORDER = "#2a2a2a"

PLOT_FONT = dict(family="JetBrains Mono, monospace", color=FG_DIM, size=10)


def _value_curve():
    thresholds = np.linspace(0.05, 0.95, 181)
    # Smooth quadratic peaking at t* = 0.48, value 326
    # v(t) = 326 - a*(t - 0.48)^2, tuned so v(0.05) ≈ 80 and v(0.95) ≈ 30
    t_star = 0.48
    peak = 326.0
    # left curvature (gentler) and right curvature (steeper) — asymmetric is realistic
    values = []
    for t in thresholds:
        if t <= t_star:
            v = peak - 1180 * (t - t_star) ** 2
        else:
            v = peak - 1650 * (t - t_star) ** 2
        values.append(max(v, 5))
    values = np.array(values)

    fig = go.Figure()

    # Reference line — default threshold at 0.5 (above peak vertically, label outside chart area)
    fig.add_vline(x=0.5, line_width=1, line_dash="dot", line_color=FG_MUTED)

    # The curve — smooth, thin
    fig.add_trace(go.Scatter(
        x=thresholds, y=values,
        mode="lines",
        line=dict(color=CYAN, width=2, shape="spline", smoothing=0.8),
        fill="tozeroy",
        fillcolor="rgba(34, 211, 238, 0.06)",
        hovertemplate="τ=%{x:.2f} · $%{y:.0f}K<extra></extra>",
        showlegend=False,
    ))

    # Optimal marker — crosshair style
    fig.add_trace(go.Scatter(
        x=[0.48], y=[326],
        mode="markers",
        marker=dict(size=11, color=CYAN, symbol="cross-thin",
                    line=dict(color=CYAN, width=2.5)),
        showlegend=False, hoverinfo="skip",
    ))
    # Single clean annotation — kerned correctly, only the optimal labeled
    fig.add_annotation(
        x=0.48, y=370,
        text="<b>τ* = 0.48</b>   ·   <b>$326K/mo</b>",
        showarrow=False,
        font=dict(color=CYAN, size=11, family="JetBrains Mono"),
    )
    # Default threshold sub-label, smaller, off to the right
    fig.add_annotation(
        x=0.5, y=20,
        text="τ = 0.5 default",
        showarrow=False,
        xanchor="left",
        font=dict(color=FG_MUTED, size=9, family="JetBrains Mono"),
    )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=48, r=12, t=44, b=40),
        height=300,
        xaxis=dict(
            title=dict(text="threshold τ", font=dict(color=FG_MUTED, size=10, family="JetBrains Mono")),
            showgrid=True, gridcolor="rgba(255,255,255,0.04)",
            tickfont=dict(color=FG_MUTED, size=9, family="JetBrains Mono"),
            zeroline=False,
        ),
        yaxis=dict(
            title=dict(text="$/month (K)", font=dict(color=FG_MUTED, size=10, family="JetBrains Mono")),
            showgrid=True, gridcolor="rgba(255,255,255,0.04)",
            tickfont=dict(color=FG_MUTED, size=9, family="JetBrains Mono"),
            zeroline=False,
            range=[0, 420],
        ),
        font=PLOT_FONT,
    )
    return fig


def _confusion_matrix():
    """Built with divs — far more terminal-authentic than a Plotly heatmap."""
    return html.Div(
        [
            # Top-left corner empty
            html.Div(className="cfn-corner"),
            # Column headers
            html.Div("PRED.RETAIN", className="cfn-col-head"),
            html.Div("PRED.CHURN", className="cfn-col-head"),
            # Row 1 — actual retain
            html.Div("ACTUAL.RETAIN", className="cfn-row-head"),
            html.Div(
                [
                    html.Div("760", className="cfn-cell-num"),
                    html.Div("TRUE NEG", className="cfn-cell-lbl"),
                ],
                className="cfn-cell cfn-cell-tn",
            ),
            html.Div(
                [
                    html.Div("275", className="cfn-cell-num"),
                    html.Div("FALSE POS", className="cfn-cell-lbl"),
                ],
                className="cfn-cell cfn-cell-fp",
                style={"border-right": "none"},
            ),
            # Row 2 — actual churn
            html.Div("ACTUAL.CHURN", className="cfn-row-head"),
            html.Div(
                [
                    html.Div("63", className="cfn-cell-num"),
                    html.Div("FALSE NEG", className="cfn-cell-lbl"),
                ],
                className="cfn-cell cfn-cell-fn",
                style={"border-bottom": "none"},
            ),
            html.Div(
                [
                    html.Div("311", className="cfn-cell-num"),
                    html.Div("TRUE POS", className="cfn-cell-lbl"),
                ],
                className="cfn-cell cfn-cell-tp",
                style={"border-bottom": "none", "border-right": "none"},
            ),
        ],
        className="confusion",
    )


def render():
    return html.Section(
        [
            html.Div(
                [
                    html.H2(
                        [html.Span("04 //", className="sec-title-prefix"), "BUSINESS · COST-SENSITIVE THRESHOLD"],
                        className="sec-title",
                    ),
                    html.Span("FN cost / FP cost = 4.8× · 199 thresholds swept", className="sec-meta"),
                ],
                className="sec-header",
            ),

            # 4-cell threshold comparison
            html.Div(
                [
                    html.Div(
                        [
                            html.Div("τ_DEFAULT", className="thresh-cell-label"),
                            html.Div("0.50", className="thresh-cell-value"),
                            html.Div("sklearn naive", className="thresh-cell-sub"),
                        ],
                        className="thresh-cell",
                    ),
                    html.Div(
                        [
                            html.Div("τ_OPTIMAL", className="thresh-cell-label"),
                            html.Div("0.48", className="thresh-cell-value thresh-cell-value-cyan"),
                            html.Div("cost-optimized", className="thresh-cell-sub"),
                        ],
                        className="thresh-cell thresh-cell-highlight",
                    ),
                    html.Div(
                        [
                            html.Div("VALUE @ τ*", className="thresh-cell-label"),
                            html.Div(
                                [
                                    "$326",
                                    html.Span("K", className="thresh-cell-unit"),
                                ],
                                className="thresh-cell-value thresh-cell-value-cyan",
                            ),
                            html.Div("per month, projected", className="thresh-cell-sub"),
                        ],
                        className="thresh-cell thresh-cell-highlight",
                    ),
                    html.Div(
                        [
                            html.Div("LIFT", className="thresh-cell-label"),
                            html.Div(
                                [
                                    "+$7",
                                    html.Span("K", className="thresh-cell-unit"),
                                ],
                                className="thresh-cell-value thresh-cell-value-green",
                            ),
                            html.Div("vs default threshold", className="thresh-cell-sub"),
                        ],
                        className="thresh-cell",
                    ),
                ],
                className="thresh-grid mb-4",
            ),

            # Value curve + confusion matrix
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span([html.Span("//", className="pfx"), "threshold.sweep"],
                                              className="panel-head-title"),
                                    html.Span("90 candidates · peak τ=0.48", className="panel-head-meta"),
                                ],
                                className="panel-head",
                            ),
                            html.Div(
                                dcc.Graph(figure=_value_curve(),
                                          config={"displayModeBar": False}),
                                className="panel-body-tight",
                            ),
                        ],
                        className="panel",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span([html.Span("//", className="pfx"), "confusion @ τ=0.48"],
                                              className="panel-head-title"),
                                    html.Span("n=1,409 holdout", className="panel-head-meta"),
                                ],
                                className="panel-head",
                            ),
                            html.Div(
                                [
                                    _confusion_matrix(),
                                    # Metric strip below
                                    html.Div(
                                        [
                                            html.Div(
                                                [
                                                    html.Div("PRECISION", className="metric-strip-label"),
                                                    html.Div("0.531", className="metric-strip-val"),
                                                ],
                                                className="metric-strip-cell",
                                            ),
                                            html.Div(
                                                [
                                                    html.Div("RECALL", className="metric-strip-label"),
                                                    html.Div("0.832", className="metric-strip-val metric-strip-val-cyan"),
                                                ],
                                                className="metric-strip-cell",
                                            ),
                                            html.Div(
                                                [
                                                    html.Div("F1", className="metric-strip-label"),
                                                    html.Div("0.648", className="metric-strip-val"),
                                                ],
                                                className="metric-strip-cell",
                                            ),
                                        ],
                                        className="metric-strip",
                                    ),
                                ],
                                className="panel-body",
                            ),
                        ],
                        className="panel",
                    ),
                ],
                className="grid-7-5 mb-4",
            ),

            # Cost matrix
            html.Div(
                [
                    html.Div("// COST.MATRIX · $ per outcome", className="sec-meta",
                             style={"marginBottom": "10px", "color": "var(--fg-dim)"}),
                    html.Div(
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Div("TRUE POSITIVE", className="cost-cell-label"),
                                        html.Div("+$283", className="cost-cell-value cost-val-pos"),
                                        html.Div(
                                            "Catch a churner · 40% retention success rate · save full CLV",
                                            className="cost-cell-desc",
                                        ),
                                    ],
                                    className="cost-cell",
                                ),
                                html.Div(
                                    [
                                        html.Div("FALSE POSITIVE", className="cost-cell-label"),
                                        html.Div("−$74", className="cost-cell-value cost-val-neg"),
                                        html.Div(
                                            "Retention offer wasted on non-churner",
                                            className="cost-cell-desc",
                                        ),
                                    ],
                                    className="cost-cell",
                                ),
                                html.Div(
                                    [
                                        html.Div("FALSE NEGATIVE", className="cost-cell-label"),
                                        html.Div("−$357", className="cost-cell-value cost-val-neg"),
                                        html.Div(
                                            "Miss a churner · lose CLV · 4.8× costlier than FP",
                                            className="cost-cell-desc",
                                        ),
                                    ],
                                    className="cost-cell",
                                ),
                                html.Div(
                                    [
                                        html.Div("TRUE NEGATIVE", className="cost-cell-label"),
                                        html.Div("$0", className="cost-cell-value cost-val-neut"),
                                        html.Div(
                                            "Correctly ignored · no action taken",
                                            className="cost-cell-desc",
                                        ),
                                    ],
                                    className="cost-cell",
                                ),
                            ],
                            className="cost-row",
                        ),
                        className="cost-matrix",
                    ),
                ],
            ),
        ],
        id="sec-business",
        className="panel-section",
    )
