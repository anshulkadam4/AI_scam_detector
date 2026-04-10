import logging

import streamlit as st

from detector import SAFETY_RECOMMENDATIONS, predict_message, train_model

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
            }
            .block-container {
                max-width: 1140px;
                padding-top: 1.6rem;
                padding-bottom: 2.5rem;
            }
            h1, h2, h3 {
                font-family: Georgia, "Times New Roman", serif;
                letter-spacing: -0.02em;
            }
            .shell,
            .hero-card,
            .glass-card,
            .result-card,
            .signal-card,
            .footer-card {
                background: rgba(255, 255, 255, 0.76);
                border: 1px solid rgba(21, 38, 63, 0.08);
                border-radius: 24px;
                box-shadow: 0 18px 55px rgba(37, 54, 82, 0.08);
                backdrop-filter: blur(12px);
            }
            .hero-card {
                padding: 1.8rem;
                margin-bottom: 1rem;
            }
            .kicker {
                display: inline-block;
                padding: 0.36rem 0.75rem;
                border-radius: 999px;
                background: #15263f;
                color: #f8efe1;
                font-size: 0.74rem;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.08em;
            }
            .hero-grid {
                display: grid;
                grid-template-columns: 1.45fr 0.8fr;
                gap: 1rem;
                align-items: end;
                margin-top: 1rem;
            }
            .hero-title {
                margin: 0.7rem 0 0.75rem 0;
                font-size: 3.15rem;
                line-height: 0.95;
            }
            .hero-copy {
                margin: 0;
                max-width: 42rem;
                color: #45607d;
                font-size: 1rem;
            }
            .hero-alert {
                padding: 1rem 1.1rem;
                border-radius: 20px;
                background: linear-gradient(135deg, #142743, #34567e);
                color: #f5f8fc;
            }
            .hero-alert strong {
                display: block;
                font-size: 1.05rem;
                margin-bottom: 0.2rem;
            }
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(4, minmax(0, 1fr));
                gap: 0.9rem;
                margin-top: 1rem;
            }
            .signals-grid {
                display: grid;
                grid-template-columns: repeat(3, minmax(0, 1fr));
                gap: 0.9rem;
            }
            .breakdown-grid {
                display: grid;
                grid-template-columns: repeat(2, minmax(0, 1fr));
                gap: 0.9rem;
            }
            .stat-chip {
                padding: 1rem 1.1rem;
                border-radius: 18px;
                background: linear-gradient(180deg, rgba(21, 38, 63, 0.97), rgba(57, 91, 132, 0.93));
                color: #f8fbff;
            }
            .stat-chip span {
                font-size: 0.76rem;
                text-transform: uppercase;
                letter-spacing: 0.08em;
                font-weight: 700;
            }
            .stat-chip strong {
                display: block;
                margin-top: 0.15rem;
                font-size: 1.25rem;
            }
            .signal-card {
                padding: 1rem 1.1rem;
            }
            .signal-card span {
                font-size: 0.76rem;
                text-transform: uppercase;
                letter-spacing: 0.08em;
                font-weight: 700;
            }
            .eyebrow {
                font-size: 0.76rem;
                text-transform: uppercase;
                letter-spacing: 0.08em;
                font-weight: 700;
            }
            .section-title {
                margin: 0.2rem 0 0.4rem 0;
                font-size: 1.5rem;
            }
            .section-copy {
                margin: 0;
                color: #526781;
            }
            .result-card {
                padding: 1.25rem;
                color: #fff;
            }
            .risk-high {
                background: linear-gradient(135deg, #4c1219, #a02e3d);
            }
            .risk-low {
                background: linear-gradient(135deg, #143f31, #2f7d63);
            }
            .risk-value {
                font-size: 3.2rem;
                line-height: 1;
                margin: 0.3rem 0 0.4rem 0;
                font-weight: 700;
            }
            .meter-wrap {
                margin-top: 0.9rem;
                border-radius: 999px;
                overflow: hidden;
                height: 0.8rem;
                background: rgba(255, 255, 255, 0.18);
            }
            .meter-bar {
                height: 100%;
                border-radius: 999px;
                background: linear-gradient(90deg, #ffd6b0, #fff5ea);
            }
            .pill-row {
                display: flex;
                flex-wrap: wrap;
                gap: 0.45rem;
                margin-top: 0.5rem;
            }
            .pill {
                padding: 0.36rem 0.72rem;
                border-radius: 999px;
                background: rgba(21, 38, 63, 0.08);
                color: #183251;
                font-size: 0.88rem;
                font-weight: 600;
            }
            .footer-card {
                margin-top: 1rem;
                color: #4d637b;
                padding: 1rem 1.1rem;
            }
            .footer-card strong {
                color: #15263f;
            }
            .glass-card {
                padding: 1rem 1.1rem;
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
    selected_example = st.selectbox(
        "Quick examples",
        options=["Custom message"] + EXAMPLE_MESSAGES,
        index=0,
    )
    default_message = "" if selected_example == "Custom message" else selected_example
    user_input = st.text_area(
        "Enter message",
        value=default_message,
        height=230,
        placeholder="Example: Your account has been suspended. Click here to verify now.",
        label_visibility="collapsed",
    )
    run_check = st.button("Analyze Message", type="primary", use_container_width=True)

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

if run_check:
    if not user_input.strip():
        st.warning("Enter a message before running detection.")
    else:
        try:
            result = predict_message(
                user_input,
                artifacts["model"],
                artifacts["vectorizer"],
            )
            risk_percent = round(result["scam_probability"] * 100)
            risk_class = "risk-high" if result["is_scam"] else "risk-low"
            risk_title = (
                "High risk message" if result["is_scam"] else "Low risk message"
            )
            risk_text = (
                "The message matches scam-like patterns or contains risky trigger words."
                if result["is_scam"]
                else "The message does not strongly resemble common scam messages in this model."
            )

            result_col, detail_col = st.columns([0.9, 1.1], gap="large")

            with result_col:
                st.markdown(
                    f"""
                    <section class="result-card {risk_class}">
                        <span class="eyebrow">Detection Result</span>
                        <div class="risk-value">{risk_percent}%</div>
                        <h2 style="margin: 0 0 0.45rem 0;">{risk_title}</h2>
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
                            <span class="eyebrow">Probability</span>
                            <h3 class="section-title" style="margin-top: 0.25rem;">{risk_percent}% risk</h3>
                            <p class="section-copy">Estimated chance that the message fits spam or scam behavior.</p>
                        </section>
                        <section class="signal-card">
                            <span class="eyebrow">Model verdict</span>
                            <h3 class="section-title" style="margin-top: 0.25rem;">{"Scam-like" if result["model_prediction"] == 1 else "Safe-like"}</h3>
                            <p class="section-copy">Raw classifier output before keyword-based risk adjustment.</p>
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
