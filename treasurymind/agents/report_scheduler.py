"""Automated Email & Report Scheduler - scheduled financial reports."""
from typing import Dict, Any, List
from datetime import datetime, timedelta


class ReportScheduler:
    """Generates and schedules automated financial reports."""

    def __init__(self):
        self.schedules = []

    def create_schedule(self, report_type: str, frequency: str, recipients: List[str],
                       language: str = "en") -> Dict:
        """Create a new report schedule."""
        schedule = {
            "id": f"sched_{len(self.schedules)+1:04d}",
            "report_type": report_type,
            "frequency": frequency,  # daily, weekly, monthly
            "recipients": recipients,
            "language": language,
            "active": True,
            "created": datetime.now().isoformat(),
            "next_run": self._calculate_next_run(frequency),
        }
        self.schedules.append(schedule)
        return schedule

    def generate_report(self, report_type: str, data: Dict, language: str = "en") -> Dict:
        """Generate a report based on type and data."""
        generators = {
            "daily_reconciliation": self._daily_recon_report,
            "weekly_summary": self._weekly_summary,
            "monthly_tax": self._monthly_tax_report,
            "cash_flow_forecast": self._cash_flow_report,
            "fx_exposure": self._fx_exposure_report,
            "client_aging": self._client_aging_report,
        }
        generator = generators.get(report_type, self._daily_recon_report)
        return generator(data, language)

    def _daily_recon_report(self, data: Dict, lang: str) -> Dict:
        s = data.get("summary", {})
        return {
            "title": "Daily Reconciliation Report",
            "generated": datetime.now().isoformat(),
            "sections": [
                {"heading": "KPI Summary", "content": {
                    "Transactions": s.get("total_transactions", 0),
                    "Reconciled": s.get("reconciled_count", 0),
                    "Pending": s.get("pending_count", 0),
                    "Suspicious": s.get("suspicious_count", 0),
                    "Match Rate": f"{s.get('match_rate', 0)}%",
                    "FX Variance": f"RM {s.get('fx_variance_total', 0):,.2f}",
                    "Cash Flow": f"RM {s.get('cash_flow_total', 0):,.2f}",
                }},
                {"heading": "Action Items", "content": [
                    f"{s.get('pending_count', 0)} transactions need manual review",
                    f"{s.get('suspicious_count', 0)} flagged for investigation",
                ]},
            ],
        }

    def _weekly_summary(self, data: Dict, lang: str) -> Dict:
        return {"title": "Weekly Treasury Summary", "generated": datetime.now().isoformat(),
                "sections": [{"heading": "Overview", "content": "Weekly aggregated metrics"}]}

    def _monthly_tax_report(self, data: Dict, lang: str) -> Dict:
        return {"title": "Monthly Tax Summary (SST)", "generated": datetime.now().isoformat(),
                "sections": [{"heading": "Tax Obligations", "content": "SST calculation pending"}]}

    def _cash_flow_report(self, data: Dict, lang: str) -> Dict:
        return {"title": "Cash Flow Forecast", "generated": datetime.now().isoformat(),
                "sections": [{"heading": "30-Day Forecast", "content": "Projection based on patterns"}]}

    def _fx_exposure_report(self, data: Dict, lang: str) -> Dict:
        return {"title": "FX Exposure Report", "generated": datetime.now().isoformat(),
                "sections": [{"heading": "Currency Positions", "content": "Multi-currency breakdown"}]}

    def _client_aging_report(self, data: Dict, lang: str) -> Dict:
        return {"title": "Client Aging Report", "generated": datetime.now().isoformat(),
                "sections": [{"heading": "Outstanding by Client", "content": "Aging analysis"}]}

    def _calculate_next_run(self, frequency: str) -> str:
        now = datetime.now()
        if frequency == "daily":
            return (now + timedelta(days=1)).replace(hour=8, minute=0).isoformat()
        elif frequency == "weekly":
            return (now + timedelta(weeks=1)).replace(hour=8, minute=0).isoformat()
        else:
            return (now + timedelta(days=30)).replace(hour=8, minute=0).isoformat()

    def get_available_reports(self) -> List[Dict]:
        return [
            {"id": "daily_reconciliation", "name": "Daily Reconciliation", "desc": "KPIs, matches, alerts"},
            {"id": "weekly_summary", "name": "Weekly Summary", "desc": "Aggregated weekly metrics"},
            {"id": "monthly_tax", "name": "Monthly Tax (SST)", "desc": "Tax obligations summary"},
            {"id": "cash_flow_forecast", "name": "Cash Flow Forecast", "desc": "30-day projection"},
            {"id": "fx_exposure", "name": "FX Exposure", "desc": "Currency position analysis"},
            {"id": "client_aging", "name": "Client Aging", "desc": "Outstanding by client"},
        ]
