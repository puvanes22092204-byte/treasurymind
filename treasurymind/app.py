"""TreasuryMind - Autonomous SME Financial Intelligence Agent."""
import streamlit as st
import pandas as pd
import io
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.ocr_agent import OCRAgent
from agents.fx_agent import FXAgent
from agents.reconciliation_agent import ReconciliationAgent
from agents.prediction_agent import PredictionAgent
from agents.alert_agent import AlertAgent
from agents.chatbot_agent import ChatbotAgent
from agents.whatsapp_agent import WhatsAppAgent
from agents.email_agent import EmailAgent
from agents.invoice_agent import InvoiceAgent
from agents.bank_parser import BankParser
from agents.tax_agent import TaxAgent
from agents.payment_channel_agent import PaymentChannelAgent
from blockchain.logger import BlockchainLogger
from utils.accounting_export import AccountingExporter
from utils.i18n import get_text, get_language_options
from components.styles import inject_custom_css

st.set_page_config(page_title="TreasuryMind", page_icon="T", layout="wide", initial_sidebar_state="expanded")
inject_custom_css()

# Session state
for key, default in [("logged_in", False), ("language", "en"), ("reconciliation_results", None),
                     ("chat_history", []), ("transactions", []), ("user_name", "")]:
    if key not in st.session_state:
        st.session_state[key] = default


# ============================================================
# LOGIN PAGE
# ============================================================
def show_login():
    st.markdown("""
    <div class="login-container">
        <div class="login-logo"><span>T</span></div>
        <h2>TreasuryMind</h2>
        <p>Autonomous Financial Intelligence for SMEs</p>
    </div>
    """, unsafe_allow_html=True)

    # Center the form
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        with st.form("login_form"):
            name = st.text_input("Full Name", placeholder="e.g. Amara Khan")
            email = st.text_input("Email", placeholder="you@company.com")
            password = st.text_input("Password", type="password", placeholder="Enter password")
            st.markdown("")
            submitted = st.form_submit_button("Sign In", use_container_width=True)

        if submitted:
            if name and email and password:
                st.session_state.logged_in = True
                st.session_state.user_name = name
                st.rerun()
            else:
                st.error("Please fill in all fields.")

        st.markdown("")
        st.markdown("""
        <div style="text-align:center; margin-top:1rem;">
            <p style="color:#7d8590; font-size:0.75rem;">
                Demo credentials: any name, email, and password will work.
            </p>
        </div>
        """, unsafe_allow_html=True)


if not st.session_state.logged_in:
    show_login()
    st.stop()

# ============================================================
# MAIN APP (after login)
# ============================================================
@st.cache_resource
def init_agents():
    return {
        "ocr": OCRAgent(), "fx": FXAgent(), "reconciliation": ReconciliationAgent(),
        "prediction": PredictionAgent(), "alert": AlertAgent(), "chatbot": ChatbotAgent(),
        "whatsapp": WhatsAppAgent(), "email": EmailAgent(), "invoice": InvoiceAgent(),
        "bank_parser": BankParser(), "tax": TaxAgent(),
        "payment_channel": PaymentChannelAgent(),
        "blockchain": BlockchainLogger(), "exporter": AccountingExporter(),
    }

agents = init_agents()
lang = st.session_state.language

# --- SIDEBAR ---
with st.sidebar:
    st.markdown(f"""
    <div style="padding:1.25rem 0; border-bottom:1px solid rgba(255,255,255,0.06); margin-bottom:1rem;">
        <div style="display:flex; align-items:center; gap:0.75rem; padding:0 0.5rem;">
            <div style="width:36px; height:36px; border-radius:9px; background:#06d6a0;
                 display:flex; align-items:center; justify-content:center; flex-shrink:0;">
                <span style="color:#0d1117; font-weight:800; font-size:1rem;">T</span>
            </div>
            <div>
                <p style="margin:0; font-size:0.9rem; font-weight:700; color:#fff;">TreasuryMind</p>
                <p style="margin:0; font-size:0.6rem; color:#7d8590; text-transform:uppercase;
                   letter-spacing:0.1em;">Reconciliation Agent</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio("nav", options=[
        "command_center", "reconciliation", "chatbot", "alerts",
        "invoices", "tax", "channels", "whatsapp", "export", "blockchain"
    ], format_func=lambda x: {
        "command_center": "Command Center",
        "reconciliation": "Document Intake",
        "chatbot": "Treasury Copilot",
        "alerts": "Fraud & Anomaly",
        "invoices": "Invoices",
        "tax": "Analytics",
        "channels": "Payment Channels",
        "whatsapp": "WhatsApp",
        "export": "Export",
        "blockchain": "Audit Log",
    }[x], label_visibility="collapsed")

    st.markdown("")
    st.markdown("")

    # Language selector (small)
    lang_options = get_language_options()
    selected_lang = st.selectbox("Lang", options=list(lang_options.keys()),
        format_func=lambda x: lang_options[x],
        index=list(lang_options.keys()).index(st.session_state.language),
        label_visibility="collapsed")
    if selected_lang != st.session_state.language:
        st.session_state.language = selected_lang
        st.rerun()

    # User info at bottom
    st.markdown(f"""
    <div style="position:fixed; bottom:1rem; padding:0.75rem; border-top:1px solid rgba(255,255,255,0.06);">
        <div style="display:flex; align-items:center; gap:0.6rem;">
            <div style="width:32px; height:32px; border-radius:50%; background:#1f6feb;
                 display:flex; align-items:center; justify-content:center;">
                <span style="color:white; font-weight:600; font-size:0.75rem;">{st.session_state.user_name[:2].upper()}</span>
            </div>
            <div>
                <p style="margin:0; font-size:0.8rem; color:#fff; font-weight:500;">{st.session_state.user_name}</p>
                <p style="margin:0; font-size:0.6rem; color:#7d8590;">Treasury Lead</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# --- HELPERS ---
def mcard(label, value, delta=None, delta_class="d-neutral"):
    d = f'<div class="mc-delta {delta_class}">{delta}</div>' if delta else ""
    return f'<div class="metric-card"><div class="mc-label">{label}</div><div class="mc-value">{value}</div>{d}</div>'

def arow(title, level="a-info", sub=None):
    s = f'<div class="ar-sub">{sub}</div>' if sub else ""
    return f'<div class="alert-row {level}"><div class="ar-title">{title}</div>{s}</div>'


# ============================================================
# COMMAND CENTER
# ============================================================
if page == "command_center":
    from components.command_center import render_command_center
    import streamlit.components.v1 as stc
    data = {
        "summary": (st.session_state.reconciliation_results or {}).get("summary", {}),
        "fx_summary": st.session_state.get("fx_summary", {}),
        "alerts": st.session_state.get("alerts", []),
        "cash_flow": sum(float(t.get("myr_amount", t.get("amount", 0))) for t in st.session_state.get("transactions", [])),
    }
    html_content = render_command_center(st.session_state.user_name, data)
    stc.html(html_content, height=1450, scrolling=True)

# ============================================================
# DOCUMENT INTAKE (Reconciliation)
# ============================================================
elif page == "reconciliation":
    st.markdown('<div class="sec-title">Smart Reconciliation Engine</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">AI matches invoices → payments across currencies</div>', unsafe_allow_html=True)

    # Pipeline indicator
    if st.session_state.reconciliation_results:
        s = st.session_state.reconciliation_results["summary"]
        st.markdown(f"""
        <div class="card">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
                <span style="font-weight:600; color:#fff;">Reconciliation Pipeline</span>
                <span class="badge b-green">COMPLETE</span>
            </div>
            <div style="display:flex; align-items:center; justify-content:space-between; text-align:center;">
                <div><div style="color:#7d8590; font-size:0.65rem; text-transform:uppercase;">Ingest</div><div style="color:#fff; font-size:1.3rem; font-weight:700;">{s['total_invoices']}</div></div>
                <span style="color:#7d8590;">→</span>
                <div><div style="color:#7d8590; font-size:0.65rem; text-transform:uppercase;">OCR + Extract</div><div style="color:#fff; font-size:1.3rem; font-weight:700;">{s['total_invoices']}</div></div>
                <span style="color:#7d8590;">→</span>
                <div><div style="color:#7d8590; font-size:0.65rem; text-transform:uppercase;">FX Normalize</div><div style="color:#fff; font-size:1.3rem; font-weight:700;">{s['total_bank_entries']}</div></div>
                <span style="color:#7d8590;">→</span>
                <div><div style="color:#7d8590; font-size:0.65rem; text-transform:uppercase;">Match</div><div style="color:#fff; font-size:1.3rem; font-weight:700;">{s['matched_count'] + s['partial_count']}</div></div>
                <span style="color:#7d8590;">→</span>
                <div><div style="color:#7d8590; font-size:0.65rem; text-transform:uppercase;">Review</div><div style="color:#fff; font-size:1.3rem; font-weight:700;">{s['partial_count']}</div></div>
                <span style="color:#7d8590;">→</span>
                <div><div style="color:#7d8590; font-size:0.65rem; text-transform:uppercase;">Cleared</div><div style="color:#fff; font-size:1.3rem; font-weight:700;">{s['matched_count']}</div></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Matched transactions table
        st.markdown("")
        results = st.session_state.reconciliation_results
        all_results = results["matched"] + results["partial_matches"]

        if all_results:
            st.markdown("""<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
                <span style="font-weight:600; color:#fff; font-size:1.1rem;">Matched Transactions</span>
            </div>""", unsafe_allow_html=True)

            # Table header
            st.markdown("""
            <div style="display:grid; grid-template-columns: 1.5fr 1fr 1fr 0.8fr 1fr 1fr; gap:0.5rem;
                 padding:0.6rem 1rem; color:#7d8590; font-size:0.7rem; text-transform:uppercase; letter-spacing:0.05em;">
                <span>Invoice</span><span>Expected</span><span>Received</span><span>Δ</span><span>Confidence</span><span>Status</span>
            </div>""", unsafe_allow_html=True)

            for r in all_results[:8]:
                inv = r["invoice"]
                ref = inv.get("reference", "N/A")
                expected = float(inv.get("myr_amount", inv.get("amount", 0)))
                received = float(r["bank_entry"].get("myr_amount", r["bank_entry"].get("amount", 0)))
                diff = r["difference"]
                score = r["match_score"]
                is_match = r["amount_match"]

                # Confidence bar color
                bar_color = "#06d6a0" if score >= 85 else "#d29922" if score >= 60 else "#f85149"
                status_badge = "b-green" if is_match else "b-yellow"
                status_text = "Auto Matched" if is_match else "Partial Match"
                diff_color = "#06d6a0" if abs(diff) < 1 else "#d29922" if abs(diff) < 50 else "#f85149"

                st.markdown(f"""
                <div style="display:grid; grid-template-columns: 1.5fr 1fr 1fr 0.8fr 1fr 1fr; gap:0.5rem;
                     padding:0.75rem 1rem; border-bottom:1px solid rgba(255,255,255,0.04); align-items:center;">
                    <div>
                        <div style="color:#fff; font-weight:600; font-size:0.8rem;">{ref}</div>
                    </div>
                    <span style="color:#e6edf3; font-size:0.85rem;">{expected:,.2f} MYR</span>
                    <span style="color:#e6edf3; font-size:0.85rem;">{received:,.2f} MYR</span>
                    <span style="color:{diff_color}; font-size:0.85rem; font-weight:500;">{diff:+,.2f}</span>
                    <div style="display:flex; align-items:center; gap:0.5rem;">
                        <div style="flex:1; height:4px; background:rgba(255,255,255,0.06); border-radius:2px;">
                            <div style="width:{score}%; height:100%; background:{bar_color}; border-radius:2px;"></div>
                        </div>
                        <span style="color:#b1bac4; font-size:0.75rem;">{score}%</span>
                    </div>
                    <span class="badge {status_badge}">{status_text}</span>
                </div>
                """, unsafe_allow_html=True)

        # AI Reasoning panel
        if all_results:
            st.markdown("")
            first = all_results[0]
            st.markdown(f"""
            <div class="card" style="border-left:3px solid #06d6a0;">
                <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.75rem;">
                    <span style="font-weight:600; color:#fff;">AI Reasoning</span>
                    <span class="badge b-green">Auto Matched</span>
                </div>
                <p style="color:#e6edf3; font-size:0.85rem; line-height:1.6; margin:0 0 1rem;">
                    {first['explanation']}
                </p>
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:1rem; margin-bottom:1rem;">
                    <div><div style="color:#7d8590; font-size:0.65rem; text-transform:uppercase;">FX Rate</div>
                         <div style="color:#fff; font-size:1rem; font-weight:600;">{first['invoice'].get('fx_rate', 4.47):.4f}</div></div>
                    <div><div style="color:#7d8590; font-size:0.65rem; text-transform:uppercase;">Bank Charges</div>
                         <div style="color:#fff; font-size:1rem; font-weight:600;">{abs(first['difference']):.2f} MYR</div></div>
                </div>
                <div style="margin-bottom:0.5rem;">
                    <div style="display:flex; justify-content:space-between; margin-bottom:0.3rem;">
                        <span style="color:#b1bac4; font-size:0.8rem;">Match Confidence</span>
                        <span style="color:#fff; font-size:0.8rem; font-weight:600;">{first['match_score']}%</span>
                    </div>
                    <div style="height:6px; background:rgba(255,255,255,0.06); border-radius:3px;">
                        <div style="width:{first['match_score']}%; height:100%; background:#06d6a0; border-radius:3px;"></div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    else:
        # Upload section
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Receipts / Invoices**")
            receipts = st.file_uploader("r", type=["png","jpg","jpeg","pdf"],
                accept_multiple_files=True, key="receipts", label_visibility="collapsed")
        with col2:
            st.markdown("**Bank Statement**")
            bank_statement = st.file_uploader("b", type=["xlsx","xls","csv"],
                accept_multiple_files=False, key="bank_statement", label_visibility="collapsed")

        col_b, _ = st.columns([1, 2])
        with col_b:
            banks = {"auto":"Auto-detect","maybank":"Maybank","cimb":"CIMB","rhb":"RHB","public_bank":"Public Bank"}
            bank_choice = st.selectbox("Bank", list(banks.keys()), format_func=lambda x: banks[x])
            bank = bank_choice if bank_choice != "auto" else None

        st.markdown("")
        if st.button("Run Reconciliation", type="primary", use_container_width=True):
            if not receipts and not bank_statement:
                st.warning("Upload at least one document.")
            else:
                with st.status("Processing...", expanded=True) as status:
                    st.write("Extracting data...")
                    invoice_data = []
                    for r in (receipts or []):
                        if r.name.lower().endswith(".pdf"):
                            invoice_data.extend(agents["ocr"].extract_from_pdf(r))
                        else:
                            invoice_data.append(agents["ocr"].extract_from_image(r))
                    st.write("Parsing bank statement...")
                    bank_data = agents["bank_parser"].parse_statement(bank_statement, bank) if bank_statement else []
                    st.write("Converting currencies...")
                    invoice_data = agents["fx"].convert_batch(invoice_data)
                    bank_data = agents["fx"].convert_batch(bank_data)
                    st.write("Matching...")
                    results = agents["reconciliation"].reconcile(invoice_data, bank_data)
                    st.write("Alerts...")
                    fx_summary = agents["fx"].get_fx_summary(invoice_data)
                    alerts = agents["alert"].generate_all_alerts({"invoices":invoice_data,"payments":bank_data,"fx_data":fx_summary,"cash_flow":{}})
                    st.write("Blockchain...")
                    blockchain_logs = agents["blockchain"].log_batch(results["matched"]+results["partial_matches"])
                    status.update(label="Complete", state="complete")

                st.session_state.reconciliation_results = results
                st.session_state.transactions = invoice_data + bank_data
                st.session_state.alerts = alerts
                st.session_state.fx_summary = fx_summary
                st.session_state.blockchain_logs = blockchain_logs
                st.rerun()

# ============================================================
# TREASURY COPILOT (Chatbot)
# ============================================================
elif page == "chatbot":
    st.markdown('<div class="sec-title">Treasury Copilot</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">Ask about payments, cash flow, or invoices — in any language.</div>', unsafe_allow_html=True)

    if st.session_state.reconciliation_results:
        agents["chatbot"].set_context({
            "summary": st.session_state.reconciliation_results["summary"],
            "fx_summary": st.session_state.get("fx_summary", {}),
            "alerts": st.session_state.get("alerts", []),
            "unmatched_invoices": st.session_state.reconciliation_results.get("unmatched_invoices", []),
        })

    qc1, qc2, qc3, qc4 = st.columns(4)
    qp = None
    with qc1:
        if st.button("Payment status", use_container_width=True): qp = "Did all my payments come in correctly?"
    with qc2:
        if st.button("Cash flow", use_container_width=True): qp = "Is my cash flow healthy?"
    with qc3:
        if st.button("Who owes me?", use_container_width=True): qp = "Which clients still owe me money?"
    with qc4:
        if st.button("FX losses", use_container_width=True): qp = "How much did I lose to FX fees?"

    st.markdown("")
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("Ask Treasury Copilot...")
    prompt = qp or user_input
    if prompt:
        st.session_state.chat_history.append({"role":"user","content":prompt})
        with st.chat_message("user"): st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                resp = agents["chatbot"].chat(prompt)
            st.markdown(resp)
        st.session_state.chat_history.append({"role":"assistant","content":resp})
        if qp: st.rerun()

# ============================================================
# FRAUD & ANOMALY (Alerts)
# ============================================================
elif page == "alerts":
    st.markdown('<div class="sec-title">Fraud & Anomaly Detection</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">Proactive alerts for suspicious activity, late payments, and FX anomalies.</div>', unsafe_allow_html=True)

    alerts = st.session_state.get("alerts", [])
    if alerts:
        crit = [a for a in alerts if a.get("priority",5)<=1]
        warn = [a for a in alerts if a.get("priority",5)==2]
        info = [a for a in alerts if a.get("priority",5)>=3]

        c1,c2,c3 = st.columns(3)
        with c1: st.markdown(mcard("Critical", str(len(crit)), "Immediate action", "d-down"), unsafe_allow_html=True)
        with c2: st.markdown(mcard("Warnings", str(len(warn)), "Review needed", "d-warn"), unsafe_allow_html=True)
        with c3: st.markdown(mcard("Info", str(len(info)), "For awareness", "d-neutral"), unsafe_allow_html=True)

        st.markdown("")
        if crit:
            st.markdown("**Critical**")
            for a in crit: st.markdown(arow(a["message"], "a-danger", a.get("action")), unsafe_allow_html=True)
        if warn:
            st.markdown("**Warnings**")
            for a in warn: st.markdown(arow(a["message"], "a-warning", a.get("action")), unsafe_allow_html=True)
        if info:
            st.markdown("**Information**")
            for a in info: st.markdown(arow(a["message"], "a-info", a.get("action")), unsafe_allow_html=True)
    else:
        st.markdown(arow("No active alerts. Run reconciliation to generate.", "a-success"), unsafe_allow_html=True)

# ============================================================
# INVOICES
# ============================================================
elif page == "invoices":
    st.markdown('<div class="sec-title">Invoice Generator</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">Create professional invoices in multiple currencies.</div>', unsafe_allow_html=True)

    with st.form("inv_form"):
        c1, c2 = st.columns(2)
        with c1:
            cn = st.text_input("Client Name", "Acme Corp")
            ce = st.text_input("Client Email", "billing@acme.com")
            ca = st.text_input("Client Address", "Singapore")
        with c2:
            cur = st.selectbox("Currency", ["MYR","USD","EUR","GBP","SGD"])
            dd = st.number_input("Payment Terms (days)", value=30, min_value=7)
        st.markdown("**Line Items**")
        items = []
        for i in range(3):
            cols = st.columns([3,1,1])
            d = cols[0].text_input("Description" if i==0 else f"Item {i+1}", key=f"d{i}")
            q = cols[1].number_input("Qty" if i==0 else " ", value=1, min_value=0, key=f"q{i}")
            a = cols[2].number_input("Amount" if i==0 else " ", value=0.0, min_value=0.0, key=f"a{i}")
            if d and a>0: items.append({"description":d,"quantity":q,"amount":a})
        sub = st.form_submit_button("Generate Invoice", use_container_width=True)
    if sub and items:
        inv = agents["invoice"].generate_invoice({"name":cn,"email":ce,"address":ca}, items, cur, dd)
        st.code(agents["invoice"].format_invoice_text(inv), language="text")

# ============================================================
# ANALYTICS (Tax)
# ============================================================
elif page == "tax":
    st.markdown('<div class="sec-title">Treasury Analytics</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">Cash flow, exposure, settlement performance</div>', unsafe_allow_html=True)

    txns = st.session_state.get("transactions", [])
    if txns:
        import plotly.graph_objects as go
        import random

        # Cash flow trend
        st.markdown("""<div class="card"><div style="font-weight:600; color:#fff;">Cash Flow Trend</div>
        <div style="font-size:0.75rem; color:#7d8590;">Last 30 days · MYR equivalent</div></div>""", unsafe_allow_html=True)

        days = list(range(1, 31))
        values = [random.randint(5000, 15000) for _ in days]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=days, y=values, mode="lines", fill="tozeroy",
            line=dict(color="#06d6a0", width=2), fillcolor="rgba(6,214,160,0.1)"))
        fig.update_layout(height=220, margin=dict(t=10,b=30,l=50,r=10),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#7d8590",
            xaxis=dict(gridcolor="rgba(255,255,255,0.04)"), yaxis=dict(gridcolor="rgba(255,255,255,0.04)"))
        st.plotly_chart(fig, use_container_width=True)

        # Currency exposure
        st.markdown("")
        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown("""<div class="card"><div style="font-weight:600; color:#fff;">Currency Exposure</div>
            <div style="font-size:0.75rem; color:#7d8590;">Net USD equivalent</div></div>""", unsafe_allow_html=True)
            currencies = ["USD", "EUR", "MYR", "GBP", "SGD"]
            amounts = [4200, 2100, 980, 620, 410]
            colors = ["#06d6a0", "#58a6ff", "#a855f7", "#f85149", "#d29922"]
            for cur_name, amt, clr in zip(currencies, amounts, colors):
                pct = amt / max(amounts) * 100
                st.markdown(f"""
                <div style="display:flex; align-items:center; gap:0.75rem; margin-bottom:0.6rem;">
                    <span style="color:#fff; font-size:0.8rem; font-weight:500; width:35px;">{cur_name}</span>
                    <div style="flex:1; height:8px; background:rgba(255,255,255,0.06); border-radius:4px;">
                        <div style="width:{pct}%; height:100%; background:{clr}; border-radius:4px;"></div>
                    </div>
                    <span style="color:#e6edf3; font-size:0.8rem; font-weight:600;">${amt:,}k</span>
                </div>""", unsafe_allow_html=True)

        with col_r:
            # Tax summary
            c1, c2 = st.columns(2)
            with c1: rt = st.radio("Period", ["Monthly","Quarterly"], horizontal=True)
            with c2:
                if rt == "Monthly":
                    m = st.number_input("Month", value=5, min_value=1, max_value=12)
                    sm = agents["tax"].generate_monthly_summary(txns, m)
                else:
                    q = st.number_input("Quarter", value=2, min_value=1, max_value=4)
                    sm = agents["tax"].generate_quarterly_summary(txns, q)

            st.markdown(mcard("Total Income", f"RM {sm.get('total_income_myr',0):,.2f}"), unsafe_allow_html=True)
            st.markdown(mcard("SST Payable", f"RM {sm.get('sst_payable', sm.get('total_sst_payable',0)):,.2f}"), unsafe_allow_html=True)
    else:
        st.info("Upload transaction data to see analytics.")

# ============================================================
# PAYMENT CHANNELS
# ============================================================
elif page == "channels":
    st.markdown('<div class="sec-title">Payment Channels</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">Find the cheapest way to receive international payments.</div>', unsafe_allow_html=True)

    c1,c2,c3 = st.columns(3)
    with c1: amt = st.number_input("Amount", value=500.0, min_value=1.0)
    with c2: cur = st.selectbox("Currency", ["USD","EUR","GBP","SGD","AUD"])
    with c3: country = st.text_input("Country", "United States")

    if st.button("Find Best Channel", type="primary", use_container_width=True):
        for i, rec in enumerate(agents["payment_channel"].recommend(amt, cur, country)):
            lvl = "a-success" if rec.get("recommended") else "a-info"
            lbl = "RECOMMENDED" if rec.get("recommended") else f"Option {i+1}"
            st.markdown(arow(f"{lbl}: {rec['channel']} — RM {rec['fee_myr']:.2f}", lvl, rec["speed"]), unsafe_allow_html=True)
            if rec.get("recommended") and "recommendation_text" in rec:
                st.success(rec["recommendation_text"])

# ============================================================
# WHATSAPP
# ============================================================
elif page == "whatsapp":
    st.markdown('<div class="sec-title">WhatsApp Integration</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">Forward receipts via WhatsApp for instant reconciliation.</div>', unsafe_allow_html=True)

    st.markdown("""
    **How it works:**
    1. Send a receipt photo to your TreasuryMind WhatsApp number
    2. Agent extracts payment data automatically
    3. Matches against your invoices
    4. Replies with the result in seconds
    """)
    st.divider()
    sim = st.selectbox("Scenario", ["Receipt Photo", "Text Query (English)", "Text Query (BM)"])
    if st.button("Run Simulation", type="primary", use_container_width=True):
        if sim == "Receipt Photo":
            msgs = agents["whatsapp"].simulate_whatsapp_flow({"status":"Matched","invoice":{"reference":"INV-001"},"difference":-4.70,"explanation":"RM 4.70 less — likely bank fees."})
        elif "BM" in sim:
            r = agents["whatsapp"].process_incoming({"type":"text","text":"Semak status bayaran","sender":"+60123456789"})
            msgs = ["Incoming: 'Semak status bayaran'", f"Reply: {r['reply']}"]
        else:
            r = agents["whatsapp"].process_incoming({"type":"text","text":"Check payment status","sender":"+60123456789"})
            msgs = ["Incoming: 'Check payment status'", f"Reply: {r['reply']}"]
        for m in msgs: st.code(m, language="text")

# ============================================================
# EXPORT
# ============================================================
elif page == "export":
    st.markdown('<div class="sec-title">Accounting Export</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">One-click export to SQL Accounting, QuickBooks, or Wave.</div>', unsafe_allow_html=True)

    txns = st.session_state.get("transactions", [])
    if txns:
        fmts = agents["exporter"].get_supported_formats()
        sel = st.selectbox("Format", [f["id"] for f in fmts], format_func=lambda x: next(f["name"] for f in fmts if f["id"]==x))
        if st.button("Export", type="primary", use_container_width=True):
            buf = agents["exporter"].export_to_excel(txns, sel)
            st.download_button("Download", data=buf, file_name=f"export_{sel}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.info("Run reconciliation first.")

    st.divider()
    st.markdown("**Payment Reminders**")
    if st.session_state.reconciliation_results:
        um = st.session_state.reconciliation_results.get("unmatched_invoices", [])
        if um:
            el = st.selectbox("Language", ["en","ms","zh"], format_func=lambda x: {"en":"English","ms":"BM","zh":"中文"}[x])
            if st.button("Generate Reminders"):
                for r in agents["email"].generate_batch_reminders(um, el):
                    with st.expander(r["subject"]): st.text(r["body"])
        else:
            st.markdown(arow("No overdue invoices.", "a-success"), unsafe_allow_html=True)
    else:
        st.info("Run reconciliation first.")

# ============================================================
# AUDIT LOG (Blockchain)
# ============================================================
elif page == "blockchain":
    st.markdown('<div class="sec-title">Audit Log</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">Immutable on-chain record of every reconciliation decision.</div>', unsafe_allow_html=True)

    logs = st.session_state.get("blockchain_logs", [])
    if logs:
        st.markdown(f'<span style="color:#e6edf3; font-weight:600;">{len(logs)} entries recorded</span>', unsafe_allow_html=True)
        st.markdown("")
        for log in logs:
            oc = log.get("on_chain", False)
            badge_cls = "b-green" if oc else "b-blue"
            badge_txt = "On-chain" if oc else "Local"
            with st.expander(f"{log.get('invoice_ref','N/A')} — {log.get('timestamp','')[:16]}"):
                st.markdown(f'<span class="badge {badge_cls}">{badge_txt}</span>', unsafe_allow_html=True)
                st.json({"Timestamp": log.get("timestamp"), "Invoice": log.get("invoice_ref"),
                    "Score": log.get("match_score"), "Difference": f"RM {log.get('difference',0):.2f}",
                    "Explanation": log.get("explanation"),
                    "Hash": log.get("document_hash","")[:40]+"...", "TX": log.get("tx_hash","Pending")})
        st.divider()
        if st.button("Export Audit Log", use_container_width=True):
            st.download_button("Download JSON", data=agents["blockchain"].export_audit_log(),
                file_name="audit_trail.json", mime="application/json")
    else:
        st.info("Audit trail populates after reconciliation.")


# ============================================================
# FOOTER
# ============================================================
st.markdown('<div class="app-footer"><p>TREASURYMIND · AI MARATHON 2026 · APU AIC · MORPHEUS AI · CHUTES AI</p></div>', unsafe_allow_html=True)
