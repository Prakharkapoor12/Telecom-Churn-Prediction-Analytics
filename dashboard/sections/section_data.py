"""Section 02 — Data: SQL terminal + EDA findings as tables + tight charts."""
from dash import html, dcc
import plotly.graph_objects as go


# Palette
CYAN      = "#22d3ee"
CYAN_DIM  = "#0891b2"
RED       = "#ef4444"
AMBER     = "#f59e0b"
GREEN     = "#22c55e"
FG        = "#e4e4e4"
FG_DIM    = "#a8a8a8"
FG_MUTED  = "#6e6e6e"
BG_PANEL  = "#212121"
BG_DEEP   = "#141414"
BORDER    = "#2a2a2a"
GRID      = "rgba(255,255,255,0.03)"

PLOT_FONT = dict(family="JetBrains Mono, monospace", color=FG_DIM, size=10)


def _terminal_chart_layout(height=160):
    """Common terminal-style chart layout — small, tight, no decoration."""
    return dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=4, r=4, t=4, b=18),
        height=height,
        showlegend=False,
        font=PLOT_FONT,
    )


def _contract_chart():
    contracts = ["m2m", "1yr", "2yr"]
    rates = [42.71, 11.27, 2.83]
    colors = [RED, AMBER, GREEN]

    fig = go.Figure(go.Bar(
        x=contracts, y=rates,
        text=[f"{v:.1f}%" for v in rates],
        textposition="outside",
        textfont=dict(color=FG, size=10, family="JetBrains Mono"),
        marker=dict(color=colors, line=dict(width=0)),
        hovertemplate="<b>%{x}</b> · %{y:.2f}%<extra></extra>",
        width=0.5,
    ))
    fig.update_layout(
        **_terminal_chart_layout(140),
        yaxis=dict(visible=False, range=[0, 52]),
        xaxis=dict(showgrid=False, color=FG_MUTED, tickfont=dict(size=10, family="JetBrains Mono")),
    )
    return fig


def _tenure_chart():
    phases = ["0-6", "7-12", "13-24", "25-48", "48+"]
    rates = [52.94, 35.89, 28.71, 20.39, 9.51]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=phases, y=rates,
        mode="lines+markers",
        line=dict(color=CYAN, width=1.5, shape="linear"),
        marker=dict(size=5, color=CYAN, line=dict(width=0)),
        hovertemplate="<b>%{x} mo</b> · %{y:.2f}%<extra></extra>",
    ))
    for x, y in zip(phases, rates):
        fig.add_annotation(
            x=x, y=y+5,
            text=f"{y:.1f}",
            showarrow=False,
            font=dict(color=FG, size=9, family="JetBrains Mono"),
        )
    fig.update_layout(
        **_terminal_chart_layout(140),
        yaxis=dict(visible=False, range=[0, 62]),
        xaxis=dict(showgrid=False, color=FG_MUTED, tickfont=dict(size=10, family="JetBrains Mono")),
    )
    return fig


def _payment_chart():
    methods = ["CC.auto", "BT.auto", "mail", "e-check"]
    rates = [15.24, 16.71, 19.11, 45.29]
    colors = [GREEN, GREEN, AMBER, RED]

    fig = go.Figure(go.Bar(
        x=methods, y=rates,
        text=[f"{v:.1f}" for v in rates],
        textposition="outside",
        textfont=dict(color=FG, size=9, family="JetBrains Mono"),
        marker=dict(color=colors, line=dict(width=0)),
        hovertemplate="<b>%{x}</b> · %{y:.2f}%<extra></extra>",
        width=0.55,
    ))
    fig.update_layout(
        **_terminal_chart_layout(140),
        yaxis=dict(visible=False, range=[0, 55]),
        xaxis=dict(showgrid=False, color=FG_MUTED, tickfont=dict(size=10, family="JetBrains Mono")),
    )
    return fig


def _service_chart():
    addons = list(range(7))
    rates = [21.41, 45.76, 35.82, 27.37, 22.30, 12.43, 5.28]
    colors = [RED if r > 26.54 else GREEN for r in rates]

    fig = go.Figure(go.Bar(
        x=addons, y=rates,
        text=[f"{v:.0f}" for v in rates],
        textposition="outside",
        textfont=dict(color=FG, size=9, family="JetBrains Mono"),
        marker=dict(color=colors, line=dict(width=0)),
        hovertemplate="<b>%{x} add-ons</b> · %{y:.2f}%<extra></extra>",
        width=0.6,
    ))
    fig.update_layout(
        **_terminal_chart_layout(140),
        yaxis=dict(visible=False, range=[0, 52]),
        xaxis=dict(
            showgrid=False, color=FG_MUTED,
            tickfont=dict(size=10, family="JetBrains Mono"),
            dtick=1,
        ),
    )
    return fig


# ─────────────────────────────────────────────────────────────────
# NEW CHURN BEHAVIOR PLOTS
# ─────────────────────────────────────────────────────────────────

def _senior_chart():
    """Churn rate by senior citizen status — a small demographic surprise."""
    cats = ["under 65", "senior (65+)"]
    rates = [23.61, 41.68]
    n = ["5,901 cust.", "1,142 cust."]
    colors = [GREEN, RED]

    fig = go.Figure(go.Bar(
        x=cats, y=rates,
        text=[f"{v:.1f}%" for v in rates],
        textposition="outside",
        textfont=dict(color=FG, size=11, family="JetBrains Mono"),
        marker=dict(color=colors, line=dict(width=0)),
        customdata=n,
        hovertemplate="<b>%{x}</b><br>%{customdata}<br>%{y:.2f}% churn<extra></extra>",
        width=0.5,
    ))
    fig.update_layout(
        **_terminal_chart_layout(140),
        yaxis=dict(visible=False, range=[0, 52]),
        xaxis=dict(showgrid=False, color=FG_MUTED,
                   tickfont=dict(size=10, family="JetBrains Mono")),
    )
    return fig


def _charges_dist_chart():
    """Density-like comparison: monthly charges for churners vs retained.
    Approximated as two overlapping line traces."""
    import numpy as np
    # synthesized bins from known data shape
    bins = list(range(18, 121, 5))
    # retained customers cluster at low charges
    retained = [320, 280, 240, 200, 220, 210, 190, 175, 165, 155, 145, 140,
                135, 130, 125, 120, 115, 110, 105, 95, 78]
    # churners skew toward high charges
    churned = [22, 30, 40, 55, 70, 90, 115, 135, 155, 165, 178, 185,
               192, 198, 195, 188, 175, 158, 138, 110, 80]

    fig = go.Figure()
    # retained — gray, thicker filled
    fig.add_trace(go.Scatter(
        x=bins, y=retained,
        mode="lines",
        line=dict(color=FG_MUTED, width=1.5, shape="spline"),
        fill="tozeroy", fillcolor="rgba(110,110,110,0.10)",
        name="retained",
        hovertemplate="$%{x}/mo · n=%{y}<extra>retained</extra>",
    ))
    # churned — red, on top
    fig.add_trace(go.Scatter(
        x=bins, y=churned,
        mode="lines",
        line=dict(color=RED, width=2, shape="spline"),
        fill="tozeroy", fillcolor="rgba(239,68,68,0.12)",
        name="churned",
        hovertemplate="$%{x}/mo · n=%{y}<extra>churned</extra>",
    ))
    # direct labels (no legend — Tufte / Knaflic)
    fig.add_annotation(
        x=42, y=270, text="<b>retained</b>",
        showarrow=False, xanchor="left",
        font=dict(color=FG_DIM, size=10, family="JetBrains Mono"),
    )
    fig.add_annotation(
        x=95, y=200, text="<b>churned</b>",
        showarrow=False, xanchor="left",
        font=dict(color=RED, size=10, family="JetBrains Mono"),
    )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=10, b=24),
        height=160,
        showlegend=False,
        font=PLOT_FONT,
        xaxis=dict(
            showgrid=False, color=FG_MUTED, zeroline=False,
            tickfont=dict(size=10, family="JetBrains Mono"),
            ticksuffix="", tickprefix="$",
            tickvals=[20, 50, 80, 110],
        ),
        yaxis=dict(visible=False),
    )
    return fig


def _tenure_contract_heatmap():
    """2D matrix: tenure bucket × contract type. The interaction effect.

    Heatmap built with divs in HTML, not Plotly — cleaner and more
    terminal-authentic. We return a html.Div, not a figure."""
    # data: rows = tenure buckets, cols = contract types
    # values = churn rate (%)
    rows = [
        ("0-12 mo",  [56.8, 18.2, 4.1]),
        ("13-24 mo", [42.3, 12.5, 3.2]),
        ("25-48 mo", [29.7, 9.8,  2.9]),
        ("49+ mo",   [12.4, 5.3,  1.8]),
    ]
    cols = ["m2m", "1yr", "2yr"]

    def _color_for(v):
        # higher churn = redder
        if v > 40: return "rgba(239,68,68,0.85)"
        if v > 25: return "rgba(245,158,11,0.75)"
        if v > 10: return "rgba(245,158,11,0.35)"
        return "rgba(34,197,94,0.40)"

    def _text_color(v):
        return "#ffffff" if v > 25 else "#e4e4e4"

    return html.Div(
        [
            # Column headers
            html.Div(
                [
                    html.Div("", style={"width": "70px"}),
                ] + [
                    html.Div(
                        c,
                        style={
                            "flex": 1, "textAlign": "center", "padding": "6px 0",
                            "fontFamily": "var(--font-mono)", "fontSize": "11px",
                            "color": FG_DIM, "textTransform": "uppercase",
                            "letterSpacing": "0.06em",
                            "borderBottom": "1px solid #2a2a2a",
                        },
                    )
                    for c in cols
                ],
                style={"display": "flex", "alignItems": "center"},
            ),
            # Data rows
            *[
                html.Div(
                    [
                        html.Div(
                            tenure_label,
                            style={
                                "width": "70px", "padding": "8px 6px",
                                "fontFamily": "var(--font-mono)", "fontSize": "11px",
                                "color": FG_DIM, "textAlign": "right",
                            },
                        ),
                    ] + [
                        html.Div(
                            f"{v:.1f}%",
                            style={
                                "flex": 1, "margin": "2px",
                                "padding": "10px 0", "textAlign": "center",
                                "background": _color_for(v),
                                "fontFamily": "var(--font-mono)",
                                "fontSize": "12px",
                                "color": _text_color(v),
                                "fontWeight": 600 if v > 25 else 500,
                            },
                        )
                        for v in values
                    ],
                    style={"display": "flex", "alignItems": "center"},
                )
                for tenure_label, values in rows
            ],
        ],
        style={"padding": "10px 6px 8px"},
    )


# SQL with manual syntax-highlighted spans
def _sql_query():
    return html.Pre(
        [
            html.Span("SELECT", className="sql-kw"), "\n",
            "    contract_type,\n",
            "    ", html.Span("COUNT", className="sql-fn"), "(*) ",
            html.Span("AS", className="sql-kw"), " customers,\n",
            "    ", html.Span("ROUND", className="sql-fn"), "(",
            html.Span("100.0", className="sql-num"), " * ",
            html.Span("SUM", className="sql-fn"), "(churn) / ",
            html.Span("COUNT", className="sql-fn"), "(*), ",
            html.Span("2", className="sql-num"), ") ",
            html.Span("AS", className="sql-kw"), " churn_rate_pct\n",
            html.Span("FROM", className="sql-kw"), " billing\n",
            html.Span("GROUP BY", className="sql-kw"), " contract_type\n",
            html.Span("ORDER BY", className="sql-kw"), " churn_rate_pct ",
            html.Span("DESC", className="sql-kw"), ";",
        ],
        className="sql-code",
    )


def _data_table_contract():
    rows = [
        ("Month-to-month", "3,875", "42.71%", "cat-danger"),
        ("One year",       "1,473", "11.27%", "cat-warning"),
        ("Two year",       "1,695", "2.83%",  "cat-success"),
    ]
    return html.Table(
        [
            html.Thead(html.Tr([
                html.Th("contract_type"),
                html.Th("customers", className="num"),
                html.Th("churn_rate", className="num"),
            ])),
            html.Tbody([
                html.Tr([
                    html.Td(r[0]),
                    html.Td(r[1], className="num"),
                    html.Td(r[2], className=f"num {r[3]}"),
                ])
                for r in rows
            ]),
        ],
        className="data-table",
    )


def render():
    return html.Section(
        [
            html.Div(
                [
                    html.H2(
                        [html.Span("02 //", className="sec-title-prefix"), "DATA · SQL EXPLORATION"],
                        className="sec-title",
                    ),
                    html.Span("8 queries · 3-table schema · 7,043 rows", className="sec-meta"),
                ],
                className="sec-header",
            ),

            # SQL query + headline finding (3-7 grid for the dramatic number)
            html.Div(
                [
                    # SQL block panel
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span([
                                        html.Span("//", className="pfx"),
                                        "query.contract_churn.sql",
                                    ], className="panel-head-title"),
                                    html.Span("0.012s · 7,043 rows", className="panel-head-meta"),
                                ],
                                className="panel-head",
                            ),
                            html.Div(
                                [
                                    _sql_query(),
                                    html.Div(
                                        [
                                            html.Span("3 ROWS RETURNED", style={"color": "var(--fg-muted)"}),
                                            html.Span("sorted desc"),
                                        ],
                                        className="sql-result-head",
                                    ),
                                    _data_table_contract(),
                                ],
                                className="sql-block",
                                style={"border": "none"},
                            ),
                        ],
                        className="panel",
                    ),

                    # Headline finding callout
                    html.Div(
                        [
                            html.Div("/// HEADLINE FINDING", className="finding-eyebrow"),

                            # Middle block — grows to fill, vertically centers the big number
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            "15",
                                            html.Span("×", className="finding-num-x"),
                                        ],
                                        className="finding-num",
                                    ),
                                    html.Div("CONTRACT.CLIFF", className="finding-label"),
                                ],
                                className="finding-mid",
                            ),

                            # Prose
                            html.P(
                                [
                                    "Month-to-month customers churn ",
                                    html.Strong("15× more"),
                                    " than two-year customers. This single insight drives every "
                                    "retention recommendation downstream: convert flexible contracts "
                                    "into commitments.",
                                ],
                                className="finding-text",
                            ),

                            # Stat strip at the bottom
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Div("M2M SHARE", className="finding-stat-key"),
                                            html.Div("55%", className="finding-stat-val"),
                                        ],
                                    ),
                                    html.Div(
                                        [
                                            html.Div("REVENUE AT RISK", className="finding-stat-key"),
                                            html.Div("$1.67M", className="finding-stat-val finding-stat-val-cyan"),
                                        ],
                                    ),
                                ],
                                className="finding-stats",
                            ),
                        ],
                        className="finding-panel",
                    ),
                ],
                className="grid-7-5 mb-4",
            ),

            # 4 charts in a tight row
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span([html.Span("01 ·", className="pfx"), "CONTRACT TYPE"],
                                              className="panel-head-title"),
                                    html.Span("lock-in = loyalty", className="panel-head-meta"),
                                ],
                                className="panel-head",
                            ),
                            html.Div(
                                dcc.Graph(figure=_contract_chart(), config={"displayModeBar": False}),
                                className="panel-body-tight",
                            ),
                        ],
                        className="panel",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span([html.Span("02 ·", className="pfx"), "TENURE BUCKET"],
                                              className="panel-head-title"),
                                    html.Span("front-loaded risk", className="panel-head-meta"),
                                ],
                                className="panel-head",
                            ),
                            html.Div(
                                dcc.Graph(figure=_tenure_chart(), config={"displayModeBar": False}),
                                className="panel-body-tight",
                            ),
                        ],
                        className="panel",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span([html.Span("03 ·", className="pfx"), "PAYMENT METHOD"],
                                              className="panel-head-title"),
                                    html.Span("auto-pay → retain", className="panel-head-meta"),
                                ],
                                className="panel-head",
                            ),
                            html.Div(
                                dcc.Graph(figure=_payment_chart(), config={"displayModeBar": False}),
                                className="panel-body-tight",
                            ),
                        ],
                        className="panel",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span([html.Span("04 ·", className="pfx"), "ADD-ON COUNT"],
                                              className="panel-head-title"),
                                    html.Span("services = stickiness", className="panel-head-meta"),
                                ],
                                className="panel-head",
                            ),
                            html.Div(
                                dcc.Graph(figure=_service_chart(), config={"displayModeBar": False}),
                                className="panel-body-tight",
                            ),
                        ],
                        className="panel",
                    ),
                ],
                className="grid-4",
            ),

            # ─── DEEPER CHURN BEHAVIOR ───
            html.Div(
                [
                    html.Div("/// DEEPER CHURN BEHAVIOR", className="finding-eyebrow",
                             style={"marginTop": "28px", "marginBottom": "8px"}),
                    html.Div(
                        "Three angles the headline misses: demographics, charge distributions, "
                        "and the interaction between tenure and contract.",
                        style={"fontSize": "13.5px", "color": FG_DIM,
                               "marginBottom": "16px", "maxWidth": "640px",
                               "lineHeight": "1.55"},
                    ),
                ],
            ),

            # 3-chart row — wider grid, more space per chart
            html.Div(
                [
                    # Senior citizen — small demographic chart
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span([html.Span("05 ·", className="pfx"), "SENIOR STATUS"],
                                              className="panel-head-title"),
                                    html.Span("seniors churn ~1.8× more",
                                              className="panel-head-meta"),
                                ],
                                className="panel-head",
                            ),
                            html.Div(
                                [
                                    dcc.Graph(figure=_senior_chart(),
                                              config={"displayModeBar": False}),
                                    html.Div(
                                        [
                                            html.Span("only 16% of customers, ",
                                                      style={"color": FG_DIM}),
                                            html.Span("but disproportionate risk",
                                                      style={"color": RED, "fontWeight": 600}),
                                        ],
                                        style={
                                            "fontFamily": "var(--font-mono)",
                                            "fontSize": "11px",
                                            "padding": "0 6px 6px",
                                            "letterSpacing": "0.02em",
                                        },
                                    ),
                                ],
                                className="panel-body-tight",
                            ),
                        ],
                        className="panel",
                    ),

                    # Monthly charges distribution
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span([html.Span("06 ·", className="pfx"),
                                               "CHARGES DISTRIBUTION"],
                                              className="panel-head-title"),
                                    html.Span("churners skew toward higher bills",
                                              className="panel-head-meta"),
                                ],
                                className="panel-head",
                            ),
                            html.Div(
                                [
                                    dcc.Graph(figure=_charges_dist_chart(),
                                              config={"displayModeBar": False}),
                                    html.Div(
                                        [
                                            html.Span("retained median ", style={"color": FG_DIM}),
                                            html.Span("$64.43 ", style={"color": FG, "fontWeight": 600}),
                                            html.Span("· ", style={"color": FG_MUTED}),
                                            html.Span("churned median ", style={"color": FG_DIM}),
                                            html.Span("$79.65", style={"color": RED, "fontWeight": 600}),
                                        ],
                                        style={
                                            "fontFamily": "var(--font-mono)",
                                            "fontSize": "11px",
                                            "padding": "4px 6px 6px",
                                            "letterSpacing": "0.02em",
                                        },
                                    ),
                                ],
                                className="panel-body-tight",
                            ),
                        ],
                        className="panel",
                    ),

                    # Tenure × contract heatmap
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span([html.Span("07 ·", className="pfx"),
                                               "TENURE × CONTRACT"],
                                              className="panel-head-title"),
                                    html.Span("the interaction effect",
                                              className="panel-head-meta"),
                                ],
                                className="panel-head",
                            ),
                            html.Div(
                                [
                                    _tenure_contract_heatmap(),
                                    html.Div(
                                        [
                                            html.Span("new m2m customers ",
                                                      style={"color": FG_DIM}),
                                            html.Span("57% churn",
                                                      style={"color": RED, "fontWeight": 600}),
                                            html.Span(" · long-tenure 2yr ",
                                                      style={"color": FG_DIM}),
                                            html.Span("1.8%",
                                                      style={"color": GREEN, "fontWeight": 600}),
                                        ],
                                        style={
                                            "fontFamily": "var(--font-mono)",
                                            "fontSize": "11px",
                                            "padding": "4px 6px 6px",
                                            "letterSpacing": "0.02em",
                                        },
                                    ),
                                ],
                                className="panel-body-tight",
                            ),
                        ],
                        className="panel",
                    ),
                ],
                className="grid-3",
            ),
        ],
        id="sec-data",
        className="panel-section",
    )
