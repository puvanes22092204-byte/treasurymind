"""Tax Summary Report Agent - generates GST/SST-ready summaries."""
import pandas as pd
from typing import Dict, Any, List
from datetime import datetime


class TaxAgent:
    """Generates tax-ready summaries for Malaysian SMEs."""

    SST_RATE = 0.06  # 6% Service Tax

    def generate_monthly_summary(self, transactions: List[Dict], month: int = None,
                                  year: int = None) -> Dict[str, Any]:
        """Generate monthly tax summary."""
        now = datetime.now()
        month = month or now.month
        year = year or now.year

        # Filter transactions for the specified month
        monthly = []
        for t in transactions:
            try:
                date = datetime.strptime(t.get("date", ""), "%Y-%m-%d")
                if date.month == month and date.year == year:
                    monthly.append(t)
            except (ValueError, TypeError):
                continue

        total_income = sum(float(t.get("myr_amount", t.get("amount", 0))) for t in monthly)
        foreign_income = sum(
            float(t.get("myr_amount", t.get("amount", 0)))
            for t in monthly if t.get("currency", "MYR") != "MYR"
        )
        domestic_income = total_income - foreign_income

        # SST calculation (service tax on domestic services)
        sst_payable = round(domestic_income * self.SST_RATE, 2)

        by_currency = {}
        for t in monthly:
            cur = t.get("currency", "MYR")
            if cur not in by_currency:
                by_currency[cur] = {"count": 0, "total_original": 0, "total_myr": 0}
            by_currency[cur]["count"] += 1
            by_currency[cur]["total_original"] += float(t.get("amount", 0))
            by_currency[cur]["total_myr"] += float(t.get("myr_amount", t.get("amount", 0)))

        by_client = {}
        for t in monthly:
            client = t.get("payer", "Unknown")
            if client not in by_client:
                by_client[client] = {"count": 0, "total_myr": 0}
            by_client[client]["count"] += 1
            by_client[client]["total_myr"] += float(t.get("myr_amount", t.get("amount", 0)))

        return {
            "period": f"{year}-{month:02d}",
            "total_income_myr": round(total_income, 2),
            "domestic_income": round(domestic_income, 2),
            "foreign_income": round(foreign_income, 2),
            "sst_payable": sst_payable,
            "transaction_count": len(monthly),
            "by_currency": by_currency,
            "by_client": by_client,
        }

    def generate_quarterly_summary(self, transactions: List[Dict], quarter: int = None,
                                    year: int = None) -> Dict[str, Any]:
        """Generate quarterly tax summary (SST filing period)."""
        now = datetime.now()
        year = year or now.year
        quarter = quarter or ((now.month - 1) // 3 + 1)

        months = [(quarter - 1) * 3 + i + 1 for i in range(3)]
        monthly_summaries = [self.generate_monthly_summary(transactions, m, year) for m in months]

        total_income = sum(s["total_income_myr"] for s in monthly_summaries)
        total_sst = sum(s["sst_payable"] for s in monthly_summaries)
        total_foreign = sum(s["foreign_income"] for s in monthly_summaries)

        return {
            "period": f"Q{quarter} {year}",
            "months": monthly_summaries,
            "total_income_myr": round(total_income, 2),
            "total_foreign_income": round(total_foreign, 2),
            "total_sst_payable": round(total_sst, 2),
            "filing_deadline": self._get_filing_deadline(quarter, year),
        }

    def _get_filing_deadline(self, quarter: int, year: int) -> str:
        """Get SST filing deadline for a quarter."""
        # SST due last day of month following quarter end
        deadline_months = {1: 4, 2: 7, 3: 10, 4: 1}
        month = deadline_months[quarter]
        yr = year + 1 if quarter == 4 else year
        return f"{yr}-{month:02d}-28"

    def export_tax_report(self, summary: Dict[str, Any]) -> pd.DataFrame:
        """Export tax summary as DataFrame for Excel download."""
        rows = [
            {"Category": "Total Income (MYR)", "Amount": summary["total_income_myr"]},
            {"Category": "Domestic Income", "Amount": summary.get("domestic_income", 0)},
            {"Category": "Foreign Income", "Amount": summary.get("foreign_income", 0)},
            {"Category": "SST Payable (6%)", "Amount": summary.get("sst_payable", 0)},
            {"Category": "Transaction Count", "Amount": summary.get("transaction_count", 0)},
        ]

        # Add currency breakdown
        for cur, data in summary.get("by_currency", {}).items():
            rows.append({"Category": f"Income ({cur})", "Amount": data["total_myr"]})

        return pd.DataFrame(rows)
