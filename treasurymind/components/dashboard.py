"""Financial Health Dashboard - live visual dashboard with charts and metrics."""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Dict, Any, List


def render_dashboard(data: Dict[str, Any]):
    """Render the full financial health dashboard."""
    st.markdown("## 📊 Financial Health Dashboard")

    # Top metrics row
    col1, col2, col3, col4 = st.columns(4)
    summary = data.get("summary", {})

    with col1:
        st.metric("Match Rate", f"{summary.get('match_rate', 0)}%",
                 delta=f"{summary.get('matched_count', 0)} matched")
    with col2:
        fx = data.get("fx_summary", {})
        st.metric("FX Loss", f"RM {fx.get('total_fx_loss', 0):,.2f}",
                 delta=f"-RM {fx.get('total_fx_loss', 0):,.2f}", delta_color="inverse")
    with col3:
        st.metric("Unmatched", f"{summary.get('unmatched_invoice_count', 0)}",
                 delta="Needs attention" if summary.get('unmatched_invoice_count', 0) > 0 else "All clear")
    with col4:
        health_score = _calculate_health_score(data)
        st.metric("Health Score", f"{health_score}/100",
                 delta="Healthy" if health_score > 70 else "Needs attention")

    st.divider()

    # Charts row
    col_left, col_right = st.columns(2)

    with col_left:
        _render_match_chart(summary)
    with col_right:
        _render_fx_chart(data.get("fx_summary", {}))

    st.divider()

    # Revenue trend and forecast
    _render_revenue_trend(data.get("transactions", []))

    # Outstanding invoices heatmap
    _render_outstanding_heatmap(data.get("unmatched_invoices", []))


def _calculate_health_score(data: Dict[str, Any]) -> int:
    """Calculate overall financial health score (0-100)."""
    score = 100
    summary = data.get("summary", {})

    # Deduct for unmatched invoices
    unmatched = summary.get("unmatched_invoice_count", 0)
    score -= min(unmatched * 10, 30)

    # Deduct for FX losses
    fx_loss = data.get("fx_summary", {}).get("total_fx_loss", 0)
    if fx_loss > 500:
        score -= 20
    elif fx_loss > 100:
        score -= 10

    # Deduct for low match rate
    match_rate = summary.get("match_rate", 100)
    if match_rate < 50:
        score -= 20
    elif match_rate < 80:
        score -= 10

    # Deduct for alerts
    alerts = data.get("alerts", [])
    critical_alerts = [a for a in alerts if a.get("priority", 5) <= 1]
    score -= min(len(critical_alerts) * 5, 20)

    return max(score, 0)


def _render_match_chart(summary: Dict[str, Any]):
    """Render matched vs unmatched pie chart."""
    st.markdown("### Payment Matching")
    labels = ["Matched ✅", "Partial ⚠️", "Unmatched ❌"]
    values = [
        summary.get("matched_count", 0),
        summary.get("partial_count", 0),
        summary.get("unmatched_invoice_count", 0),
    ]

    if sum(values) > 0:
        fig = go.Figure(data=[go.Pie(
            labels=labels, values=values,
            marker_colors=["#2ecc71", "#f39c12", "#e74c3c"],
            hole=0.4,
        )])
        fig.update_layout(height=300, margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Upload data to see matching results")


def _render_fx_chart(fx_data: Dict[str, Any]):
    """Render FX loss/gain by currency."""
    st.markdown("### FX Impact by Currency")
    by_currency = fx_data.get("by_currency", {})

    if by_currency:
        currencies = list(by_currency.keys())
        losses = [by_currency[c].get("loss", 0) for c in currencies]
        gains = [by_currency[c].get("gain", 0) for c in currencies]

        fig = go.Figure()
        fig.add_trace(go.Bar(name="Loss", x=currencies, y=losses, marker_color="#e74c3c"))
        fig.add_trace(go.Bar(name="Gain", x=currencies, y=gains, marker_color="#2ecc71"))
        fig.update_layout(barmode="group", height=300, margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("FX data will appear after reconciliation")


def _render_revenue_trend(transactions: List[Dict]):
    """Render revenue trend over time."""
    st.markdown("### 📈 Revenue Trend")
    if not transactions:
        st.info("Upload transaction data to see revenue trends")
        return

    df = pd.DataFrame(transactions)
    if "date" in df.columns and "myr_amount" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.dropna(subset=["date"])
        daily = df.groupby("date")["myr_amount"].sum().reset_index()
        fig = px.line(daily, x="date", y="myr_amount", title="Daily Revenue (MYR)")
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)


def _render_outstanding_heatmap(unmatched: List[Dict]):
    """Render outstanding invoices as a visual list."""
    st.markdown("### 🔥 Outstanding Invoices")
    if not unmatched:
        st.success("All invoices matched! No outstanding payments.")
        return

    for inv in unmatched[:10]:
        days = inv.get("days_overdue", 0)
        color = "🔴" if days > 14 else "🟡" if days > 7 else "🟢"
        amount = float(inv.get("amount", 0))
        st.markdown(
            f"{color} **{inv.get('reference', 'N/A')}** — "
            f"RM {amount:,.2f} from {inv.get('payer', 'Unknown')} "
            f"({'overdue ' + str(days) + ' days' if days > 0 else 'pending'})"
        )
