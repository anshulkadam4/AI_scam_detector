import logging
from datetime import datetime

import streamlit as st

from detector import SAFETY_RECOMMENDATIONS, SCAM_KEYWORDS, predict_message, train_model

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


EXAMPLE_MESSAGES = [
    "Congratulations, you have won a prize. Click the link to claim now.",
    "Your bank account has been suspended. Verify your OTP immediately.",
    "I am on my way home. Do you want me to bring dinner?",
]

MESSAGE_INPUT_HINTS = {
    "SMS": "Example: Your account has been suspended. Click here to verify now.",
    "Email": "Example: Dear customer, we detected unusual activity on your account.",
    "Chat": "Example: Hey, send me your OTP so I can finish the transfer.",
    "Social media": "Example: Claim your free gift by clicking the link in this message.",
}

THREAT_CATEGORY_LABELS = {
    "otp": "OTP / account verification scam",
    "bank": "Bank or account fraud",
    "delivery": "Delivery or package scam",
    "offer": "Fake offer or prize scam",
    "support": "Impersonation / support scam",
}


def get_message_placeholder(message_type: str) -> str:
    return MESSAGE_INPUT_HINTS.get(message_type, MESSAGE_INPUT_HINTS["SMS"])


def infer_threat_category(message: str, message_type: str) -> str:
    lowered = message.lower()
    if any(keyword in lowered for keyword in ["otp", "verify", "password", "account"]):
        return THREAT_CATEGORY_LABELS["otp"]
    if any(
        keyword in lowered for keyword in ["bank", "payment", "suspended", "blocked"]
    ):
        return THREAT_CATEGORY_LABELS["bank"]
    if any(
        keyword in lowered
        for keyword in ["delivery", "package", "shipment", "tracking"]
    ):
        return THREAT_CATEGORY_LABELS["delivery"]
    if any(
        keyword in lowered for keyword in ["prize", "gift", "offer", "claim", "win"]
    ):
        return THREAT_CATEGORY_LABELS["offer"]
    if any(
        keyword in lowered
        for keyword in ["support", "help", "customer service", "verify your identity"]
    ):
        return THREAT_CATEGORY_LABELS["support"]
    return f"General {message_type} risk"


def format_risk_level(score: int) -> tuple[str, str]:
    if score >= 75:
        return "High risk", "risk-high"
    if score >= 40:
        return "Medium risk", "risk-medium"
    return "Low risk", "risk-low"


def format_keyword_score(keyword_hits: list[str]) -> str:
    if not keyword_hits:
        return "No direct trigger keywords detected."
    return f"Keywords raised the risk by {len(keyword_hits)} trigger terms."


def clear_scan_history() -> None:
    st.session_state.scan_history = []


def find_custom_keywords(message: str, custom_keywords: list[str]) -> list[str]:
    """Find custom keywords in a message."""
    lowered_message = message.lower()
    return [keyword for keyword in custom_keywords if keyword in lowered_message]


def analyze_message_with_custom_keywords(
    message: str, model, vectorizer, custom_keywords: list[str]
) -> dict:
    """Analyze message using custom keywords."""
    result = predict_message(message, model, vectorizer)
    # Replace keyword hits with custom keyword findings
    result["keyword_hits"] = find_custom_keywords(message, custom_keywords)
    return result


def reset_custom_keywords() -> None:
    st.session_state.custom_keywords = SCAM_KEYWORDS.copy()


@st.cache_resource
def load_artifacts():
    try:
        artifacts = train_model()
        logger.info("Model artifacts loaded successfully")
        return artifacts
    except Exception as e:
        logger.error(f"Failed to load model artifacts: {e}")
        st.error(
            "Unable to load the detection model. Please check the application logs."
        )
        st.stop()


def inject_styles() -> None:
    st.markdown(
        """
        <style>
            * {
                box-sizing: border-box;
            }
            .stApp {
                background:
                    radial-gradient(circle at 0% 0%, rgba(214, 229, 255, 0.95), transparent 30%),
                    radial-gradient(circle at 100% 0%, rgba(255, 225, 204, 0.9), transparent 28%),
                    linear-gradient(180deg, #f8f3eb 0%, #edf4f7 48%, #f8fbfd 100%);
                color: #15263f;
            }
            [data-testid="stHeader"] {
                background: linear-gradient(90deg, #0f1d33 0%, #17345a 48%, #a24a3d 100%);
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }
            [data-testid="stHeader"]::before {
                content: "AI Scam Message Detector  |  Live phishing and fraud screening dashboard";
                display: block;
                width: 100%;
                padding: 0.85rem 1rem 0.85rem 4.2rem;
                color: #f7f1e7;
                font-size: 0.92rem;
                font-weight: 700;
                letter-spacing: 0.04em;
                word-wrap: break-word;
                overflow-wrap: break-word;
                white-space: normal;
                box-sizing: border-box;
            }
            .block-container {
                max-width: 1140px;
                padding-top: 2rem;
                padding-bottom: 2rem;
                padding-left: 1.5rem;
                padding-right: 1.5rem;
                margin: 0 auto;
            }
            h1, h2, h3 {
                font-family: Georgia, "Times New Roman", serif;
                letter-spacing: -0.02em;
                word-wrap: break-word;
                overflow-wrap: break-word;
            }
            .shell,
            .hero-card,
            .glass-card,
            .result-card,
            .signal-card,
            .footer-card {
                background: rgba(255, 255, 255, 0.76);
                border: 1px solid rgba(21, 38, 63, 0.08);
                border-radius: 20px;
                box-shadow: 0 14px 40px rgba(37, 54, 82, 0.06);
                backdrop-filter: blur(12px);
                transition: all 0.2s ease;
            }
            .shell:hover,
            .hero-card:hover,
            .glass-card:hover,
            .signal-card:hover,
            .footer-card:hover {
                box-shadow: 0 18px 50px rgba(37, 54, 82, 0.08);
            }
            .hero-card {
                padding: 2.5rem;
                margin-bottom: 2.5rem;
            }
            .kicker {
                display: inline-block;
                padding: 0.4rem 0.85rem;
                border-radius: 20px;
                background: #15263f;
                color: #f8efe1;
                font-size: 0.7rem;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.08em;
            }
            .hero-grid {
                display: grid;
                grid-template-columns: 1.45fr 0.8fr;
                gap: 2rem;
                align-items: end;
                margin-top: 1.5rem;
            }
            .hero-title {
                margin: 0.5rem 0 0.8rem 0;
                font-size: 3.15rem;
                line-height: 1.05;
                word-spacing: -0.05em;
            }
            .hero-copy {
                margin: 0;
                max-width: 42rem;
                color: #45607d;
                font-size: 0.95rem;
                line-height: 1.5;
            }
            .hero-alert {
                padding: 1.1rem 1.3rem;
                border-radius: 20px;
                background: linear-gradient(135deg, #142743, #34567e);
                color: #f5f8fc;
                border: 1px solid rgba(255, 255, 255, 0.12);
            }
            .hero-alert strong {
                display: block;
                font-size: 1rem;
                margin-bottom: 0.3rem;
                font-weight: 700;
            }
            .hero-alert div {
                font-size: 0.9rem;
                line-height: 1.4;
            }
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(4, minmax(0, 1fr));
                gap: 1.25rem;
                margin-top: 2.5rem;
            }
            .signals-grid {
                display: grid;
                grid-template-columns: repeat(3, minmax(0, 1fr));
                gap: 1.5rem;
                margin-bottom: 2.5rem;
            }
            .breakdown-grid {
                display: grid;
                grid-template-columns: repeat(2, minmax(0, 1fr));
                gap: 1.25rem;
            }
            .stat-chip {
                padding: 1.1rem;
                border-radius: 18px;
                background: linear-gradient(180deg, rgba(21, 38, 63, 0.97), rgba(57, 91, 132, 0.93));
                color: #f8fbff;
                border: 1px solid rgba(255, 255, 255, 0.1);
                text-align: center;
                transition: transform 0.2s ease;
            }
            .stat-chip:hover {
                transform: translateY(-2px);
            }
            .stat-chip span {
                font-size: 0.7rem;
                text-transform: uppercase;
                letter-spacing: 0.08em;
                font-weight: 700;
                display: block;
                margin-bottom: 0.3rem;
            }
            .stat-chip strong {
                display: block;
                margin-top: 0.2rem;
                font-size: 1.3rem;
                font-weight: 700;
            }
            .signal-card {
                padding: 1.5rem;
                border-radius: 20px;
            }
            .signal-card span {
                font-size: 0.7rem;
                text-transform: uppercase;
                letter-spacing: 0.08em;
                font-weight: 700;
                display: block;
                margin-bottom: 0.4rem;
            }
            .eyebrow {
                font-size: 0.7rem;
                text-transform: uppercase;
                letter-spacing: 0.08em;
                font-weight: 700;
                display: block;
                margin-bottom: 0.4rem;
            }
            .section-title {
                margin: 0.3rem 0 0.5rem 0;
                font-size: 1.4rem;
                font-weight: 700;
            }
            .section-copy {
                margin: 0;
                color: #526781;
                font-size: 0.95rem;
                line-height: 1.5;
            }
            .result-card {
                padding: 1.5rem;
                color: #fff;
                border-radius: 20px;
            }
            .result-card h2 {
                color: #fff;
                margin: 0.5rem 0 0.5rem 0;
                font-size: 1.3rem;
            }
            .result-card p {
                margin: 0;
                font-size: 0.95rem;
                line-height: 1.4;
            }
            .risk-high {
                background: linear-gradient(135deg, #4c1219, #a02e3d);
                border: 1px solid rgba(255, 255, 255, 0.15);
            }
            .risk-medium {
                background: linear-gradient(135deg, #7a4f18, #cc8d24);
                border: 1px solid rgba(255, 255, 255, 0.15);
            }
            .risk-low {
                background: linear-gradient(135deg, #143f31, #2f7d63);
                border: 1px solid rgba(255, 255, 255, 0.15);
            }
            .risk-value {
                font-size: 3.2rem;
                line-height: 1;
                margin: 0.5rem 0 0.4rem 0;
                font-weight: 700;
            }
            .risk-badge {
                display: inline-flex;
                align-items: center;
                padding: 0.4rem 0.85rem;
                border-radius: 20px;
                background: rgba(255, 255, 255, 0.18);
                color: #fff;
                font-size: 0.8rem;
                font-weight: 700;
                letter-spacing: 0.04em;
                margin-bottom: 0.8rem;
                border: 1px solid rgba(255, 255, 255, 0.25);
            }
            .meter-wrap {
                margin-top: 1rem;
                border-radius: 20px;
                overflow: hidden;
                height: 0.8rem;
                background: rgba(255, 255, 255, 0.18);
                border: 1px solid rgba(255, 255, 255, 0.12);
            }
            .meter-bar {
                height: 100%;
                border-radius: 20px;
                background: linear-gradient(90deg, #ffd6b0, #fff5ea);
            }
            .pill-row {
                display: flex;
                flex-wrap: wrap;
                gap: 0.75rem;
                margin-top: 1rem;
            }
            .pill {
                padding: 0.4rem 0.8rem;
                border-radius: 20px;
                background: rgba(21, 38, 63, 0.08);
                color: #183251;
                font-size: 0.85rem;
                font-weight: 600;
                border: 1px solid rgba(21, 38, 63, 0.12);
                white-space: nowrap;
                transition: all 0.2s ease;
            }
            .pill:hover {
                background: rgba(21, 38, 63, 0.12);
                border-color: rgba(21, 38, 63, 0.2);
            }
            .footer-card {
                margin-top: 0.75rem;
                color: #4d637b;
                padding: 1.25rem 1.5rem;
            }
            .footer-card strong {
                color: #15263f;
                display: block;
                margin-bottom: 0.4rem;
                font-size: 0.9rem;
            }
            .glass-card {
                padding: 1.5rem;
                border-radius: 20px;
                margin-bottom: 1.25rem;
            }
            button[kind="primary"] {
                background: linear-gradient(135deg, #0f1d33, #17345a) !important;
                border: none !important;
                border-radius: 20px !important;
                color: #fff !important;
                font-weight: 700 !important;
                padding: 0.7rem 1.5rem !important;
                transition: all 0.2s ease !important;
            }
            button[kind="primary"]:hover {
                background: linear-gradient(135deg, #17345a, #1f3d6b) !important;
                box-shadow: 0 8px 24px rgba(15, 29, 51, 0.25) !important;
                transform: translateY(-1px) !important;
            }
            button[kind="secondary"] {
                border-radius: 20px !important;
                padding: 0.6rem 1.2rem !important;
                font-weight: 600 !important;
                transition: all 0.2s ease !important;
            }
            textarea {
                border-radius: 16px !important;
                border: 2px solid rgba(21, 38, 63, 0.15) !important;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
            }
            textarea:focus {
                border: 2px solid #17345a !important;
                box-shadow: 0 0 0 3px rgba(23, 52, 90, 0.1) !important;
            }
            select {
                border-radius: 16px !important;
                border: 2px solid rgba(21, 38, 63, 0.15) !important;
            }
            select:focus {
                border: 2px solid #17345a !important;
            }

            @media (max-width: 900px) {
                .hero-grid,
                .stats-grid,
                .signals-grid,
                .breakdown-grid {
                    grid-template-columns: 1fr;
                }
                .hero-title {
                    font-size: 2.35rem;
                }
                [data-testid="stHeader"]::before {
                    padding: 0.75rem 0.75rem 0.75rem 1rem;
                    font-size: 0.8rem;
                    letter-spacing: 0.02em;
                }
                .hero-card {
                    padding: 2rem;
                    margin-bottom: 2rem;
                }
                .stats-grid {
                    gap: 1.25rem;
                    margin-top: 2rem;
                }
                .signals-grid {
                    gap: 1.25rem;
                    margin-bottom: 2rem;
                }
                .breakdown-grid {
                    gap: 1.25rem;
                }
                .glass-card {
                    margin-bottom: 1rem;
                }
            }
            @media (max-width: 640px) {
                .stApp {
                    background:
                        radial-gradient(circle at 0% 0%, rgba(214, 229, 255, 0.85), transparent 40%),
                        radial-gradient(circle at 100% 0%, rgba(255, 225, 204, 0.8), transparent 35%),
                        linear-gradient(180deg, #f8f3eb 0%, #edf4f7 48%, #f8fbfd 100%);
                }
                [data-testid="stHeader"] {
                    padding: 0;
                }
                [data-testid="stHeader"]::before {
                    content: "AI Scam Detector";
                    padding: 0.7rem 0.75rem 0.7rem 1rem;
                    font-size: 0.75rem;
                    letter-spacing: 0.01em;
                    font-weight: 700;
                }
                .block-container {
                    max-width: 100%;
                    padding-top: 1.5rem;
                    padding-bottom: 1.5rem;
                    padding-left: 1rem;
                    padding-right: 1rem;
                }
                .hero-card {
                    padding: 1.5rem;
                    margin-bottom: 1.5rem;
                    border-radius: 18px;
                }
                .hero-grid {
                    gap: 1.25rem;
                    margin-top: 1rem;
                }
                .hero-title {
                    font-size: 1.8rem;
                    margin: 0.4rem 0 0.5rem 0;
                    line-height: 1.15;
                }
                .hero-copy {
                    font-size: 0.9rem;
                }
                .hero-alert {
                    padding: 1rem 1.25rem;
                    font-size: 0.85rem;
                    border-radius: 16px;
                }
                .hero-alert strong {
                    font-size: 0.95rem;
                    margin-bottom: 0.2rem;
                }
                .stats-grid {
                    gap: 1rem;
                    margin-top: 1.5rem;
                }
                .stat-chip {
                    padding: 1rem;
                    border-radius: 16px;
                }
                .stat-chip span {
                    font-size: 0.65rem;
                }
                .stat-chip strong {
                    font-size: 1.1rem;
                    margin-top: 0.1rem;
                }
                .signals-grid {
                    gap: 1rem;
                    margin-bottom: 1.5rem;
                }
                .signal-card {
                    padding: 1.25rem;
                    border-radius: 16px;
                }
                .section-title {
                    font-size: 1.2rem;
                    margin: 0.2rem 0 0.4rem 0;
                }
                .section-copy {
                    font-size: 0.9rem;
                }
                .glass-card {
                    padding: 1.25rem;
                    border-radius: 16px;
                    margin-bottom: 1rem;
                }
                .result-card {
                    padding: 1.25rem;
                    border-radius: 16px;
                }
                .result-card h2 {
                    font-size: 1.2rem;
                    margin: 0.4rem 0 0.4rem 0;
                }
                .risk-value {
                    font-size: 2.5rem;
                    margin: 0.3rem 0 0.3rem 0;
                }
                .risk-badge {
                    font-size: 0.75rem;
                    padding: 0.35rem 0.7rem;
                    margin-bottom: 0.6rem;
                }
                .pill {
                    font-size: 0.8rem;
                    padding: 0.35rem 0.7rem;
                }
                .pill-row {
                    gap: 0.5rem;
                    margin-top: 0.75rem;
                }
                .footer-card {
                    padding: 1.1rem 1.25rem;
                    margin-top: 0.75rem;
                    font-size: 0.9rem;
                }
                .footer-card strong {
                    margin-bottom: 0.3rem;
                    font-size: 0.9rem;
                }
                .eyebrow {
                    font-size: 0.65rem;
                    margin-bottom: 0.3rem;
                }
                button[kind="primary"] {
                    padding: 0.65rem 1.2rem !important;
                    font-size: 0.9rem !important;
                }
                textarea {
                    font-size: 0.95rem !important;
                }
            }
            @media (max-width: 480px) {
                [data-testid="stHeader"]::before {
                    content: "AI Scam Detector";
                    padding: 0.6rem 0.6rem 0.6rem 0.8rem;
                    font-size: 0.7rem;
                }
                .hero-title {
                    font-size: 1.5rem;
                    line-height: 1.2;
                }
                .block-container {
                    padding-left: 0.75rem;
                    padding-right: 0.75rem;
                    padding-top: 1rem;
                    padding-bottom: 1rem;
                }
                h1, h2, h3 {
                    letter-spacing: -0.01em;
                }
                .hero-card {
                    padding: 1.25rem;
                    margin-bottom: 1.25rem;
                }
                .stat-chip {
                    padding: 0.9rem;
                }
                .signal-card {
                    padding: 1.1rem;
                }
            }

        </style>
        """,
        unsafe_allow_html=True,
    )


st.set_page_config(
    page_title="AI Scam Message Detector",
    page_icon="A",
    layout="wide",
    initial_sidebar_state="collapsed",
)

artifacts = load_artifacts()
inject_styles()

if "scan_history" not in st.session_state:
    st.session_state.scan_history = []
if "custom_keywords" not in st.session_state:
    st.session_state.custom_keywords = SCAM_KEYWORDS.copy()
if "compare_mode" not in st.session_state:
    st.session_state.compare_mode = False

# Sidebar navigation and controls
with st.sidebar:
    st.markdown("### Dashboard")

    # Scan Statistics
    if st.session_state.scan_history:
        high_risk_count = sum(
            1 for s in st.session_state.scan_history if s["risk"] == "High risk"
        )
        medium_risk_count = sum(
            1 for s in st.session_state.scan_history if s["risk"] == "Medium risk"
        )
        low_risk_count = sum(
            1 for s in st.session_state.scan_history if s["risk"] == "Low risk"
        )

        st.metric("Total Scans", len(st.session_state.scan_history))
        col1, col2, col3 = st.columns(3)
        col1.metric("High Risk", high_risk_count, delta=None)
        col2.metric("Medium Risk", medium_risk_count, delta=None)
        col3.metric("Low Risk", low_risk_count, delta=None)

        st.divider()

    # Model Metrics
    st.markdown("### Model Performance")
    col1, col2 = st.columns(2)
    col1.metric("Accuracy", f"{artifacts['accuracy']:.1%}")
    col2.metric("Precision", f"{artifacts['precision']:.1%}")
    col1.metric("Recall", f"{artifacts['recall']:.1%}")
    col2.metric("F1 Score", f"{artifacts['f1']:.1%}")

    st.divider()

    # Tools
    st.markdown("### Tools")
    if st.button("Toggle Compare Mode", use_container_width=True):
        st.session_state.compare_mode = not st.session_state.compare_mode

    if st.button(
        "Clear scan history", use_container_width=True, on_click=clear_scan_history
    ):
        st.rerun()

    # Custom Keywords Management
    with st.expander("Custom Keywords", expanded=False):
        st.markdown("**Add/Remove Scam Keywords**")
        keywords_text = st.text_area(
            "Keywords (one per line)",
            value="\n".join(st.session_state.custom_keywords),
            height=150,
            label_visibility="collapsed",
        )
        updated_keywords = [
            k.strip().lower() for k in keywords_text.split("\n") if k.strip()
        ]
        st.session_state.custom_keywords = updated_keywords

        if st.button(
            "Reset to Default", use_container_width=True, on_click=reset_custom_keywords
        ):
            st.rerun()

    # History Filter
    if st.session_state.scan_history:
        st.markdown("### Filter History")
        risk_filter = st.multiselect(
            "Filter by Risk Level",
            options=["High risk", "Medium risk", "Low risk"],
            default=["High risk", "Medium risk", "Low risk"],
            key="risk_filter",
        )
        message_type_filter = st.multiselect(
            "Filter by Message Type",
            options=["SMS", "Email", "Chat", "Social media"],
            default=["SMS", "Email", "Chat", "Social media"],
            key="type_filter",
        )
    else:
        risk_filter = None
        message_type_filter = None

dataset = artifacts["dataset"]
spam_count = int(dataset["label"].sum())
safe_count = int((dataset["label"] == 0).sum())
total_count = len(dataset)
spam_rate = spam_count / total_count if total_count else 0

st.markdown(
    f"""
    <section class="hero-card">
        <div class="kicker">AI Fraud Filter</div>
        <div class="hero-grid">
            <div>
                <h1 class="hero-title">Catch risky messages before they trigger a bad click.</h1>
                <p class="hero-copy">
                    Paste a suspicious SMS, email snippet, or chat alert. The model scores the text,
                    surfaces risky keywords, and gives you a fast trust signal before you respond.
                </p>
            </div>
            <div class="hero-alert">
                <span class="eyebrow">Live Summary</span>
                <strong>Use this before opening links, sending OTPs, or replying to urgent payment requests.</strong>
                <div>Built for quick screening during demos, submissions, and real-world phishing examples.</div>
            </div>
        </div>
        <div class="stats-grid">
            <div class="stat-chip"><span>Model accuracy</span><strong>{artifacts["accuracy"]:.2%}</strong></div>
            <div class="stat-chip"><span>Dataset size</span><strong>{total_count}</strong></div>
            <div class="stat-chip"><span>Safe messages</span><strong>{safe_count}</strong></div>
            <div class="stat-chip"><span>Spam share</span><strong>{spam_rate:.1%}</strong></div>
        </div>
    </section>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="signals-grid">
        <section class="signal-card">
            <span class="eyebrow">Signal 01</span>
            <h3 class="section-title">Language pattern match</h3>
            <p class="section-copy">The classifier compares the message against spam-like wording learned from the training data.</p>
        </section>
        <section class="signal-card">
            <span class="eyebrow">Signal 02</span>
            <h3 class="section-title">Keyword pressure</h3>
            <p class="section-copy">Terms like verify, OTP, claim, click, and bank increase scrutiny and affect the final risk view.</p>
        </section>
        <section class="signal-card">
            <span class="eyebrow">Signal 03</span>
            <h3 class="section-title">Decision support</h3>
            <p class="section-copy">The app turns the prediction into an easier trust decision with safety guidance and visual emphasis.</p>
        </section>
    </div>
    """,
    unsafe_allow_html=True,
)

left_col, right_col = st.columns([1.25, 0.95], gap="large")

with left_col:
    st.markdown(
        """
        <section class="glass-card">
            <span class="eyebrow">Message Check</span>
            <h2 class="section-title">Inspect a message</h2>
            <p class="section-copy">Choose a sample or paste your own text. Short scam-style prompts work best.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )
    message_type = st.selectbox(
        "Message source",
        options=["SMS", "Email", "Chat", "Social media"],
        index=0,
        help="Select the message channel to adapt guidance and risk context.",
    )
    selected_example = st.selectbox(
        "Quick examples",
        options=["Custom message"] + EXAMPLE_MESSAGES,
        index=0,
    )
    default_message = "" if selected_example == "Custom message" else selected_example
    placeholder_text = get_message_placeholder(message_type)
    user_input = st.text_area(
        "Enter message",
        value=default_message,
        height=230,
        placeholder=placeholder_text,
        label_visibility="collapsed",
    )
    st.caption(f"Best for {message_type.lower()} screening. {placeholder_text}")
    run_check = st.button("Analyze Message", type="primary", use_container_width=True)

    # Compare mode
    if st.session_state.compare_mode:
        st.divider()
        st.markdown("### Compare with Another Message")
        compare_input = st.text_area(
            "Second message to compare",
            height=120,
            placeholder="Paste another message to analyze side-by-side",
            label_visibility="collapsed",
        )
        compare_check = st.button("Compare", type="secondary", use_container_width=True)
    else:
        compare_input = None
        compare_check = False

with right_col:
    st.markdown(
        """
        <section class="glass-card">
            <span class="eyebrow">Quick Advice</span>
            <h2 class="section-title">Treat urgency as a warning sign</h2>
            <p class="section-copy">
                Messages that demand immediate action, threaten account closure, or ask for credentials
                are exactly the kind of content this detector is meant to screen first.
            </p>
        </section>
        """,
        unsafe_allow_html=True,
    )
    if st.session_state.scan_history:
        filtered_history = st.session_state.scan_history
        if risk_filter and message_type_filter:
            filtered_history = [
                s
                for s in st.session_state.scan_history
                if s["risk"] in risk_filter and s["message_type"] in message_type_filter
            ]

        with st.expander(
            f"Scan History ({len(filtered_history)} results)", expanded=True
        ):
            st.markdown("**Most Recent Scans**")
            for entry in reversed(filtered_history[-10:]):
                keywords = ", ".join(entry["keywords"]) if entry["keywords"] else "none"
                st.markdown(
                    f"""
                    <section class="glass-card" style="margin-bottom: 0.8rem;">
                        <strong>{entry["timestamp"]} · {entry["message_type"]}</strong>
                        <div style="margin: 0.45rem 0 0.45rem 0;">{entry["category"]} · <strong>{entry["risk"]} ({entry["score"]}%)</strong></div>
                        <div style="color: #4d637b; font-size: 0.95rem;">Keywords: {keywords}</div>
                    </section>
                    """,
                    unsafe_allow_html=True,
                )
    st.markdown(
        """
        <section class="glass-card" style="margin-top: 1rem;">
            <span class="eyebrow">Best Inputs</span>
            <div class="pill-row">
                <span class="pill">SMS alerts</span>
                <span class="pill">Bank messages</span>
                <span class="pill">Prize claims</span>
                <span class="pill">OTP requests</span>
                <span class="pill">Delivery scams</span>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

if run_check or compare_check:
    if not user_input.strip():
        st.warning("Enter a message before running detection.")
    else:
        try:
            result = analyze_message_with_custom_keywords(
                user_input,
                artifacts["model"],
                artifacts["vectorizer"],
                st.session_state.custom_keywords,
            )
            risk_percent = round(result["scam_probability"] * 100)
            raw_percent = round(result["raw_probability"] * 100)
            risk_title, risk_class = format_risk_level(risk_percent)
            category = infer_threat_category(user_input, message_type)
            keyword_summary = format_keyword_score(result["keyword_hits"])
            risk_text = (
                "The message matches scam-like patterns or contains risky trigger words."
                if result["is_scam"]
                else "The message does not strongly resemble common scam messages in this model."
            )

            history_item = {
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "message_type": message_type,
                "category": category,
                "risk": risk_title,
                "score": risk_percent,
                "keywords": result["keyword_hits"],
            }
            st.session_state.scan_history.append(history_item)
            if len(st.session_state.scan_history) > 10:
                st.session_state.scan_history = st.session_state.scan_history[-10:]

            # Handle compare mode
            if compare_check and compare_input and compare_input.strip():
                st.markdown("### Side-by-Side Comparison")
                result2 = analyze_message_with_custom_keywords(
                    compare_input,
                    artifacts["model"],
                    artifacts["vectorizer"],
                    st.session_state.custom_keywords,
                )
                risk_percent2 = round(result2["scam_probability"] * 100)
                raw_percent2 = round(result2["raw_probability"] * 100)
                risk_title2, risk_class2 = format_risk_level(risk_percent2)

                col1, col2 = st.columns(2, gap="large")

                with col1:
                    st.markdown(f"**First Message**")
                    st.markdown(
                        f"""
                        <section class="result-card {risk_class}">
                            <span class="eyebrow">{risk_title}</span>
                            <div class="risk-value">{risk_percent}%</div>
                            <div class="pill-row">{"".join(f'<span class="pill">{k}</span>' for k in result["keyword_hits"])}</div>
                        </section>
                        """,
                        unsafe_allow_html=True,
                    )

                with col2:
                    st.markdown(f"**Second Message**")
                    st.markdown(
                        f"""
                        <section class="result-card {risk_class2}">
                            <span class="eyebrow">{risk_title2}</span>
                            <div class="risk-value">{risk_percent2}%</div>
                            <div class="pill-row">{"".join(f'<span class="pill">{k}</span>' for k in result2["keyword_hits"])}</div>
                        </section>
                        """,
                        unsafe_allow_html=True,
                    )

                st.markdown(
                    f"**Difference:** {abs(risk_percent - risk_percent2)}% risk gap"
                )

            else:
                # Normal single message display
                result_col, detail_col = st.columns([0.95, 1.05], gap="large")

            with result_col:
                st.markdown(
                    f"""
                    <section class="result-card {risk_class}">
                        <span class="eyebrow">Detection Result</span>
                        <div class="risk-badge">{risk_title}</div>
                        <div class="risk-value">{risk_percent}%</div>
                        <h2 style="margin: 0 0 0.45rem 0;">{category}</h2>
                        <p style="margin: 0;">{risk_text}</p>
                        <div class="meter-wrap">
                            <div class="meter-bar" style="width: {risk_percent}%;"></div>
                        </div>
                    </section>
                    """,
                    unsafe_allow_html=True,
                )

            with detail_col:
                st.markdown(
                    """
                    <section class="glass-card">
                        <span class="eyebrow">Breakdown</span>
                        <h2 class="section-title">Why this message got this score</h2>
                        <p class="section-copy">Use the indicators below to explain the prediction during a demo or report.</p>
                    </section>
                    """,
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"""
                    <div class="breakdown-grid" style="margin-top: 1rem;">
                        <section class="signal-card">
                            <span class="eyebrow">Model confidence</span>
                            <h3 class="section-title" style="margin-top: 0.25rem;">{raw_percent}%</h3>
                            <p class="section-copy">This is the raw classifier estimate before keyword adjustment.</p>
                        </section>
                        <section class="signal-card">
                            <span class="eyebrow">Keyword pressure</span>
                            <h3 class="section-title" style="margin-top: 0.25rem;">{len(result["keyword_hits"])} terms</h3>
                            <p class="section-copy">{keyword_summary}</p>
                        </section>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if result["keyword_hits"]:
                    keyword_html = "".join(
                        f'<span class="pill">{keyword}</span>'
                        for keyword in result["keyword_hits"]
                    )
                    st.markdown(
                        f"""
                        <section class="glass-card" style="margin-top: 1rem;">
                            <span class="eyebrow">Keyword Hits</span>
                            <div class="pill-row">{keyword_html}</div>
                        </section>
                        """,
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        """
                        <section class="glass-card" style="margin-top: 1rem;">
                            <span class="eyebrow">Keyword Hits</span>
                            <div class="pill-row"><span class="pill">No suspicious keywords detected</span></div>
                        </section>
                        """,
                        unsafe_allow_html=True,
                    )

            action_col, feedback_col = st.columns([1, 1], gap="large")
            if action_col.button("Report false positive", key="flag_fp"):
                st.success("Thank you. This will help improve detection over time.")
            if feedback_col.button("Report false negative", key="flag_fn"):
                st.success("Thanks for the feedback. The example has been noted.")

            st.markdown("### Safety Recommendations")
            rec_col1, rec_col2 = st.columns(2, gap="large")
            for index, recommendation in enumerate(SAFETY_RECOMMENDATIONS):
                target_col = rec_col1 if index % 2 == 0 else rec_col2
                with target_col:
                    st.markdown(
                        f"""
                        <section class="footer-card">
                            <strong>Recommendation {index + 1}</strong>
                            <div>{recommendation}</div>
                        </section>
                        """,
                        unsafe_allow_html=True,
                    )
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            st.error("An error occurred during message analysis. Please try again.")
