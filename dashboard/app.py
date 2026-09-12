"""
CHURN-01 · Retention Analytics Terminal
========================================
Charcoal + cyan terminal aesthetic · dense data-first layout · v1.0

Run from project root:
    python dashboard/app.py
"""

import sys
from pathlib import Path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from datetime import datetime

from dash import Dash, html, dcc
import dash_bootstrap_components as dbc

from sections import (
    section_hero,
    section_data,
    section_models,
    section_business,
    section_predict,
    section_footer,
)

app = Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://use.fontawesome.com/releases/v6.4.0/css/all.css",
    ],
    suppress_callback_exceptions=True,
    title="CHURN-01 · Retention Analytics",
)
app.title = "CHURN-01 · Retention Analytics"
server = app.server


# ── Top status bar (the Bloomberg header) ────────────────────────────────
def status_bar():
    return html.Header(
        [
            html.Div(
                [
                    # Identity
                    html.Div(
                        [
                            html.Span("CHURN-01", className="sb-val sb-val-cyan"),
                            html.Span("·", style={"color": "var(--fg-faint)"}),
                            html.Span("retention.analytics", className="sb-val"),
                        ],
                        className="sb-section",
                    ),
                    # Status indicator
                    html.Div(
                        [
                            html.Span(className="sb-dot"),
                            html.Span("ONLINE", className="sb-val sb-val-green"),
                        ],
                        className="sb-section",
                    ),
                    # Model
                    html.Div(
                        [
                            html.Span("MODEL", className="sb-key"),
                            html.Span("lgbm.tuned.v1", className="sb-val"),
                        ],
                        className="sb-section",
                    ),
                    # AUC
                    html.Div(
                        [
                            html.Span("AUC", className="sb-key"),
                            html.Span("0.8471", className="sb-val sb-val-cyan"),
                        ],
                        className="sb-section",
                    ),
                    # Threshold
                    html.Div(
                        [
                            html.Span("τ", className="sb-key"),
                            html.Span("0.48", className="sb-val"),
                        ],
                        className="sb-section",
                    ),
                    # Spacer
                    html.Div(className="sb-section sb-section-flex"),
                    # Nav
                    html.Nav(
                        [
                            html.A("OVERVIEW", href="#sec-overview", className="sb-nav-link"),
                            html.A("DATA",     href="#sec-data",     className="sb-nav-link"),
                            html.A("MODELS",   href="#sec-models",   className="sb-nav-link"),
                            html.A("BUSINESS", href="#sec-business", className="sb-nav-link"),
                            html.A("PREDICT",  href="#sec-predict",  className="sb-nav-link sb-nav-link-cta"),
                        ],
                        className="sb-nav",
                    ),
                ],
                className="statusbar-inner",
            ),
        ],
        className="statusbar",
    )


app.layout = html.Div(
    [
        status_bar(),
        html.Main(
            [
                section_hero.render(),
                section_data.render(),
                section_models.render(),
                section_business.render(),
                section_predict.render(),
            ],
            className="main",
        ),
        section_footer.render(),
    ],
    className="shell",
)

section_predict.register_callbacks(app)


if __name__ == "__main__":
    app.run(debug=True, port=8050)
