"""Dark fintech dashboard theme matching TreasuryAI reference."""
import streamlit as st


def inject_custom_css():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

* { font-family: 'Inter', -apple-system, sans-serif; }
#MainMenu, footer, header { visibility: hidden; }

/* === SIDEBAR === */
[data-testid="stSidebar"] {
    background: #0b1120;
    border-right: 1px solid rgba(255,255,255,0.05);
    padding-top: 0;
}

[data-testid="stSidebar"] .stRadio > div { gap: 0; }

[data-testid="stSidebar"] .stRadio > div > label {
    padding: 0.65rem 1.2rem;
    font-size: 0.82rem;
    font-weight: 400;
    color: #8b949e;
    border-radius: 0;
    border-left: 3px solid transparent;
    transition: all 0.15s;
}

[data-testid="stSidebar"] .stRadio > div > label:hover {
    color: #e6edf3;
    background: rgba(6, 214, 160, 0.04);
}

[data-testid="stSidebar"] .stRadio > div > label[data-checked="true"] {
    color: #06d6a0;
    font-weight: 600;
    background: rgba(6, 214, 160, 0.06);
    border-left-color: #06d6a0;
}

/* === CARDS === */
.tm-card {
    background: #131d2f;
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 14px;
    padding: 1.25rem 1.5rem;
}

/* Metric card */
.tm-metric {
    background: #131d2f;
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 14px;
    padding: 1.1rem 1.25rem;
    margin-bottom: 0.75rem;
}
.tm-metric .tm-m-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.6rem;
}
.tm-metric .tm-m-label {
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #8b949e;
    font-weight: 500;
}
.tm-metric .tm-m-icon {
    width: 28px; height: 28px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
}
.tm-metric .tm-m-value {
    font-size: 1.5rem;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 0.2rem;
}
.tm-metric .tm-m-delta {
    font-size: 0.72rem;
    font-weight: 500;
}
.tm-up { color: #06d6a0; }
.tm-down { color: #f85149; }
.tm-warn { color: #d29922; }
.tm-muted { color: #8b949e; }

/* === TABLE === */
.tm-table-header {
    display: grid;
    grid-template-columns: 1.8fr 1fr 1fr 0.7fr 1.2fr 1fr;
    padding: 0.6rem 1.2rem;
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: #8b949e;
    border-bottom: 1px solid rgba(255,255,255,0.05);
}
.tm-table-row {
    display: grid;
    grid-template-columns: 1.8fr 1fr 1fr 0.7fr 1.2fr 1fr;
    padding: 0.85rem 1.2rem;
    align-items: center;
    border-bottom: 1px solid rgba(255,255,255,0.03);
    transition: background 0.1s;
}
.tm-table-row:hover { background: rgba(6,214,160,0.03); }

/* Confidence bar */
.conf-bar {
    display: flex; align-items: center; gap: 0.5rem;
}
.conf-track {
    flex: 1; height: 5px; background: rgba(255,255,255,0.06); border-radius: 3px;
}
.conf-fill { height: 100%; border-radius: 3px; }
.conf-green { background: #06d6a0; }
.conf-yellow { background: #d29922; }
.conf-red { background: #f85149; }

/* Status badges */
.st-badge {
    display: inline-block;
    padding: 0.2rem 0.6rem;
    border-radius: 12px;
    font-size: 0.65rem;
    font-weight: 600;
    text-align: center;
}
.st-auto { background: rgba(6,214,160,0.12); color: #06d6a0; border: 1px solid rgba(6,214,160,0.25); }
.st-partial { background: rgba(210,153,34,0.12); color: #d29922; border: 1px solid rgba(210,153,34,0.25); }
.st-review { background: rgba(248,81,73,0.12); color: #f85149; border: 1px solid rgba(248,81,73,0.25); }
.st-fraud { background: rgba(248,81,73,0.2); color: #ff7b72; border: 1px solid rgba(248,81,73,0.4); }
</style>
""", unsafe_allow_html=True)

    st.markdown("""
<style>
/* === AI PANEL === */
.ai-panel {
    background: #131d2f;
    border: 1px solid rgba(255,255,255,0.05);
    border-left: 3px solid #06d6a0;
    border-radius: 14px;
    padding: 1.5rem;
}
.ai-panel .ai-header {
    display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.75rem;
}
.ai-panel .ai-dot {
    width: 8px; height: 8px; border-radius: 50%; background: #06d6a0;
}
.ai-panel .ai-label { color: #06d6a0; font-size: 0.8rem; font-weight: 600; }
.ai-panel .ai-time { color: #8b949e; font-size: 0.7rem; margin-left: auto; }
.ai-panel .ai-text { color: #e6edf3; font-size: 0.82rem; line-height: 1.65; }
.ai-panel .ai-grid {
    display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; margin-top: 1rem;
}
.ai-panel .ai-stat-label { color: #8b949e; font-size: 0.6rem; text-transform: uppercase; letter-spacing: 0.05em; }
.ai-panel .ai-stat-value { color: #fff; font-size: 1rem; font-weight: 600; margin-top: 0.15rem; }

/* === PIPELINE === */
.pipeline {
    display: flex; align-items: center; justify-content: space-between;
    padding: 1.5rem 0;
}
.pipe-step { text-align: center; }
.pipe-step .pipe-label { font-size: 0.6rem; text-transform: uppercase; color: #8b949e; letter-spacing: 0.05em; }
.pipe-step .pipe-value { font-size: 1.4rem; font-weight: 700; color: #fff; margin-top: 0.2rem; }
.pipe-arrow { color: #8b949e; font-size: 1.2rem; }

/* === ALERT ROWS === */
.alert-row {
    background: #131d2f;
    border: 1px solid rgba(255,255,255,0.05);
    border-left: 3px solid;
    border-radius: 10px;
    padding: 0.85rem 1.2rem;
    margin-bottom: 0.5rem;
}
.ar-success { border-left-color: #06d6a0; }
.ar-danger { border-left-color: #f85149; }
.ar-warning { border-left-color: #d29922; }
.ar-info { border-left-color: #58a6ff; }
.alert-row .ar-title { font-weight: 500; font-size: 0.82rem; color: #e6edf3; }
.alert-row .ar-sub { font-size: 0.72rem; color: #8b949e; margin-top: 0.15rem; }

/* === SECTION HEADERS === */
.sec-title { font-size: 1.35rem; font-weight: 700; color: #fff; margin-bottom: 0.15rem; }
.sec-sub { font-size: 0.82rem; color: #8b949e; margin-bottom: 1.5rem; }

/* === BUTTONS === */
.stButton > button[kind="primary"] {
    background: #06d6a0; color: #0b1120; border: none;
    border-radius: 8px; font-weight: 600;
}
.stButton > button[kind="primary"]:hover {
    background: #05c493; box-shadow: 0 4px 12px rgba(6,214,160,0.25);
}
.stButton > button { border-radius: 8px; font-weight: 500; }

/* File uploader */
[data-testid="stFileUploader"] > div {
    border-radius: 12px;
    border: 2px dashed rgba(6,214,160,0.2);
    background: rgba(6,214,160,0.02);
}

/* Selectbox */
.stSelectbox > div > div { border-radius: 8px; }

/* Expander */
.streamlit-expanderHeader { border-radius: 10px; }

hr { border-color: rgba(255,255,255,0.05); }

/* Footer */
.app-footer { text-align:center; padding:2rem 0 1rem; border-top:1px solid rgba(255,255,255,0.05); margin-top:2rem; }
.app-footer p { color:#8b949e; font-size:0.68rem; letter-spacing:0.06em; }

/* Login */
.login-box {
    max-width: 400px; margin: 10vh auto;
    background: #131d2f; border: 1px solid rgba(255,255,255,0.05);
    border-radius: 18px; padding: 2.5rem 2rem; text-align: center;
}
.login-box h2 { color: #fff; font-size: 1.3rem; font-weight: 700; margin: 0.75rem 0 0.2rem; }
.login-box p { color: #8b949e; font-size: 0.8rem; margin-bottom: 1.5rem; }
</style>
""", unsafe_allow_html=True)
