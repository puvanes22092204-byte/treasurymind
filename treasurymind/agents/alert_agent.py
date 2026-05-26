"""Smart Alert Agent - proactive notifications for payment, FX, and cash flow issues."""
from typing import Dict, Any, List
from datetime import datetime, timedelta


class AlertAgent:
    """Generates proactive alerts based on transaction analysis."""

    def generate_all_alerts(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate all applicable alerts from current context."""
        alerts = []
        alerts.extend(self.payment_alerts(context.get("invoices", []), context.get("payments", [])))
        alerts.extend(self.fx_alerts(context.get("fx_data", {})))
        alerts.extend(self.cash_flow_alerts(context.get("cash_flow", {})))
        alerts.extend(self.overdue_alerts(context.get("invoices", [])))
        return sorted(alerts, key=lambda x: x.get("priority", 5))

    def payment_alerts(self, invoices: List[Dict], payments: List[Dict]) -> List[Dict]:
        """Generate payment-related alerts."""
        alerts = []

        # Late payment warnings
        for inv in invoices:
            due_date = inv.get("due_date", "")
            status = inv.get("status", "pending")
            if status == "pending" and due_date:
                try:
                    due = datetime.strptime(due_date, "%Y-%m-%d")
                    days_until = (due - datetime.now()).days
                    if 0 < days_until <= 3:
                        payer = inv.get("payer", "Unknown")
                        ref = inv.get("reference", "N/A")
                        alerts.append({
                            "type": "late_warning",
                            "priority": 1,
                            "icon": "⏰",
                            "message": f"Invoice {ref} is due in {days_until} days — {payer} has a history of paying late",
                            "action": "Send reminder",
                        })
                    elif days_until < 0:
                        alerts.append({
                            "type": "overdue",
                            "priority": 1,
                            "icon": "🚨",
                            "message": f"Invoice {inv.get('reference', 'N/A')} is {abs(days_until)} days overdue — RM {inv.get('amount', 0):,.2f} outstanding",
                            "action": "Send follow-up",
                        })
                except (ValueError, TypeError):
                    continue

        # Partial payment tracker
        for inv in invoices:
            if inv.get("partial_paid", 0) > 0:
                remaining = inv.get("amount", 0) - inv.get("partial_paid", 0)
                alerts.append({
                    "type": "partial_payment",
                    "priority": 2,
                    "icon": "💰",
                    "message": f"{inv.get('payer', 'Client')} still owes RM {remaining:,.2f} from a partial payment on {inv.get('date', 'N/A')}",
                    "action": "Track remaining",
                })

        # Unknown sender detection
        known_payers = {inv.get("payer", "").lower() for inv in invoices if inv.get("payer")}
        for payment in payments:
            payer = payment.get("payer", "")
            if payer and payer.lower() not in known_payers:
                alerts.append({
                    "type": "unknown_sender",
                    "priority": 3,
                    "icon": "❓",
                    "message": f"Received payment from unknown sender '{payer}' not in your client list",
                    "action": "Investigate",
                })

        return alerts

    def fx_alerts(self, fx_data: Dict) -> List[Dict]:
        """Generate FX-related alerts."""
        alerts = []

        total_loss = fx_data.get("total_fx_loss", 0)
        if total_loss > 100:
            alerts.append({
                "type": "fx_loss",
                "priority": 2,
                "icon": "📉",
                "message": f"You lost RM {total_loss:,.2f} to FX fees this month — consider switching to Wise for USD payments",
                "action": "Review FX strategy",
            })

        rate_alert = fx_data.get("rate_alert")
        if rate_alert:
            alerts.append({
                "type": "fx_rate",
                "priority": 3,
                "icon": "💱",
                "message": rate_alert,
                "action": "Check rates",
            })

        return alerts

    def cash_flow_alerts(self, cash_flow: Dict) -> List[Dict]:
        """Generate cash flow alerts."""
        alerts = []

        if cash_flow.get("alert"):
            alerts.append({
                "type": "low_balance",
                "priority": 1,
                "icon": "⚠️",
                "message": cash_flow.get("message", "Cash flow warning"),
                "action": "Review forecast",
            })

        unpaid_total = cash_flow.get("unpaid_total", 0)
        unpaid_count = cash_flow.get("unpaid_count", 0)
        if unpaid_count > 0:
            alerts.append({
                "type": "unpaid_invoices",
                "priority": 2,
                "icon": "📋",
                "message": f"You have {unpaid_count} unpaid invoices totalling RM {unpaid_total:,.2f} — follow up now to protect cash flow",
                "action": "Send reminders",
            })

        return alerts

    def overdue_alerts(self, invoices: List[Dict]) -> List[Dict]:
        """Generate overdue invoice alerts."""
        alerts = []
        overdue = [inv for inv in invoices if inv.get("days_overdue", 0) > 14]

        for inv in overdue[:5]:  # Top 5 most overdue
            alerts.append({
                "type": "overdue_critical",
                "priority": 1,
                "icon": "🔴",
                "message": f"Invoice {inv.get('reference', 'N/A')} is {inv.get('days_overdue', 0)} days overdue — RM {inv.get('amount', 0):,.2f} outstanding from {inv.get('payer', 'Unknown')}",
                "action": "Escalate",
            })

        return alerts
