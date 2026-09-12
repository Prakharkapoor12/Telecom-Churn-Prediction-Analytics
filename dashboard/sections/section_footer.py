"""Footer — terminal style."""
from dash import html


def render():
    return html.Footer(
        [
            html.Div(
                [
                    # Brand col
                    html.Div(
                        [
                            html.Div("// PROJECT", className="footer-col-label"),
                            html.Div(
                                "CHURN-01 · Retention Analytics Terminal",
                                className="footer-col-item footer-col-item-strong",
                            ),
                            html.P(
                                "End-to-end machine learning system for telecom customer churn "
                                "prediction. SQL analytics · feature engineering · 8-model "
                                "comparison · Optuna · SHAP · cost-sensitive threshold optimization · "
                                "FastAPI · Dash · Docker.",
                                className="footer-desc",
                            ),
                        ],
                    ),

                    # Components
                    html.Div(
                        [
                            html.Div("// COMPONENTS", className="footer-col-label"),
                            html.Div("10 analysis notebooks", className="footer-col-item"),
                            html.Div("FastAPI prediction service", className="footer-col-item"),
                            html.Div("Dash dashboard (this)", className="footer-col-item"),
                            html.Div("Docker compose stack", className="footer-col-item"),
                            html.Div("12 SQL analytics queries", className="footer-col-item"),
                            html.Div("SHAP explainability layer", className="footer-col-item"),
                        ],
                    ),

                    # Author
                    html.Div(
                        [
                            html.Div("// AUTHOR", className="footer-col-label"),
                            html.Div(
                                "Prakhar Kapoor",
                                className="footer-col-item footer-col-item-strong",
                            ),
                            html.Div("M2 · Data Science & NLP", className="footer-col-item"),
                            html.Div("SRM Institute of Science and Technology",
                                     className="footer-col-item"),
                            html.Div(
                                [
                                    html.A(
                                        [html.I(className="fa-brands fa-github me-1"), "github"],
                                        href="https://github.com/Prakharkapoor12",
                                        target="_blank",
                                        className="footer-link",
                                    ),
                                    html.A(
                                        [html.I(className="fa-solid fa-envelope me-1"), "email"],
                                        href="mailto:prakharhmr2005@gmail.com",
                                        className="footer-link",
                                    ),
                                ],
                                style={"marginTop": "10px"},
                            ),
                        ],
                    ),
                ],
                className="footer-grid",
            ),
            html.Div(
                [
                    html.Span("© 2026 · CHURN-01 · v1.0.0"),
                    html.Span("status: ONLINE · last_trained: 12-09-2029"),
                ],
                className="footer-bottom",
            ),
        ],
        className="footer",
    )
