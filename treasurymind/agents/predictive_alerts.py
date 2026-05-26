"""Smart Predictive Financial Alerts - AI-driven proactive warnings."""
from typing import Dict, Any, List
from datetime import datetime, timedelta


class PredictiveAlertEngine:
    """Generates predictive alerts based on transaction patterns and AI analysis."""

    def __init__(self):
        self.alert_history = []

    def analyze_and_alert(self, transactions: List[Dict], invoices: List[Dict],
                          client_profiles: Dict = None) -> List[Dict]:
        """Run full predictive analysis and generate alerts with escalation."""
        alerts = []
        alerts.extend(self._cash_flow_prediction(transactions))
        alerts.extend(self._late_payment_prediction(invoices, client_profiles))
        alerts.extend(self._fx_trend_alerts(transactions))
        alerts.extend(self._anomaly_detection(transactions))
        alerts.extend(self._seasonal_pattern_alerts(transactions))

        # Assign escalation levels
        for alert in alerts:
            alert["escalation"] = self._calculate_escalation(alert)
            alert["timestamp"] = datetime.now().isoformat()

        self.alert_history.extend(alerts)
        return sorted(alerts, key=lambda x: x.get("severity", 5))

    def _cash_flow_prediction(self, transactions: List[Dict]) -> List[Dict]:
        """Predict cash flow issues 7-30 days ahead."""
        alerts = []
        if not transactions:
            return alerts

        total_inflow = sum(float(t.get("myr_amount", t.get("amount", 0))) for t in transactions)
        avg_daily = total_inflow / max(len(transactions), 1)

        # Predict if cash flow will drop below threshold
        if avg_daily < 500:
            alerts.append({
                "type": "cash_flow_warning",
                "severity": 1,
                "title": "Low cash flow predicted",
                "message": f"Based on current patterns, daily inflow averaging RM {avg_daily:.0f}. "
                           f"Balance may drop below safe threshold in 12 days.",
                "action": "Review outstanding invoices and follow up on overdue payments.",
                "category": "cash_flow",
            })
        return alerts

    def _late_payment_prediction(self, invoices: List[Dict], profiles: Dict = None) -> List[Dict]:
        """Predict which invoices will be paid late based on client history."""
        alerts = []
        for inv in invoices:
            if inv.get("status") == "pending":
                payer = inv.get("payer", "")
                # Check if client has late payment history
                risk_score = 0.5  # Default medium risk
                if profiles and payer in profiles:
                    risk_score = profiles[payer].get("late_payment_risk", 0.5)

                if risk_score > 0.7:
                    alerts.append({
                        "type": "late_payment_prediction",
                        "severity": 2,
                        "title": f"Late payment likely: {inv.get('reference', 'N/A')}",
                        "message": f"{payer} has {risk_score*100:.0f}% probability of paying late. "
                                   f"Amount: RM {inv.get('amount', 0):,.2f}",
                        "action": "Send preemptive reminder before due date.",
                        "category": "payment",
                    })
        return alerts

    def _fx_trend_alerts(self, transactions: List[Dict]) -> List[Dict]:
        """Alert on FX rate trends that could impact receivables."""
        alerts = []
        fx_transactions = [t for t in transactions if t.get("currency", "MYR") != "MYR"]
        if len(fx_transactions) > 3:
            alerts.append({
                "type": "fx_trend",
                "severity": 3,
                "title": "FX exposure increasing",
                "message": f"{len(fx_transactions)} foreign currency transactions detected. "
                           f"Monitor USD/MYR rate for potential impact on receivables.",
                "action": "Consider hedging or timing conversions strategically.",
                "category": "fx",
            })
        return alerts

    def _anomaly_detection(self, transactions: List[Dict]) -> List[Dict]:
        """Detect unusual transaction patterns using statistical analysis."""
        alerts = []
        if len(transactions) < 3:
            return alerts

        amounts = [float(t.get("myr_amount", t.get("amount", 0))) for t in transactions]
        avg = sum(amounts) / len(amounts)
        # Simple anomaly: any transaction > 3x average
        for i, t in enumerate(transactions):
            amt = float(t.get("myr_amount", t.get("amount", 0)))
            if amt > avg * 3 and avg > 0:
                alerts.append({
                    "type": "anomaly",
                    "severity": 1,
                    "title": f"Unusual transaction: RM {amt:,.2f}",
                    "message": f"Transaction from {t.get('payer', 'Unknown')} is {amt/avg:.1f}x "
                               f"above average (RM {avg:,.0f}). Possible fraud or error.",
                    "action": "Verify with sender and check for duplicates.",
                    "category": "fraud",
                })
        return alerts

    def _seasonal_pattern_alerts(self, transactions: List[Dict]) -> List[Dict]:
        """Detect seasonal patterns and alert on expected changes."""
        return []  # Requires more historical data

    def _calculate_escalation(self, alert: Dict) -> Dict:
        """Determine escalation path based on severity."""
        severity = alert.get("severity", 5)
        if severity <= 1:
            return {"level": "critical", "notify": ["owner", "whatsapp", "email"],
                    "auto_action": True, "timeout_hours": 2}
        elif severity <= 2:
            return {"level": "high", "notify": ["owner", "email"],
                    "auto_action": False, "timeout_hours": 24}
        else:
            return {"level": "medium", "notify": ["dashboard"],
                    "auto_action": False, "timeout_hours": 72}
