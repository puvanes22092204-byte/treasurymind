"""Accounting Export - one-click export to SQL Accounting, QuickBooks, and Wave formats."""
import pandas as pd
from typing import Dict, Any, List
from datetime import datetime
import json
import io


class AccountingExporter:
    """Exports reconciliation data to popular accounting software formats."""

    def export_quickbooks(self, transactions: List[Dict]) -> pd.DataFrame:
        """Export in QuickBooks-compatible CSV format."""
        rows = []
        for t in transactions:
            rows.append({
                "Date": t.get("date", ""),
                "Transaction Type": "Payment",
                "Num": t.get("reference", ""),
                "Name": t.get("payer", ""),
                "Memo": t.get("description", ""),
                "Account": "Accounts Receivable",
                "Amount": float(t.get("myr_amount", t.get("amount", 0))),
                "Currency": t.get("currency", "MYR"),
            })
        return pd.DataFrame(rows)

    def export_sql_accounting(self, transactions: List[Dict]) -> pd.DataFrame:
        """Export in SQL Accounting (Malaysian) compatible format."""
        rows = []
        for t in transactions:
            rows.append({
                "DocNo": t.get("reference", ""),
                "DocDate": t.get("date", ""),
                "PostDate": t.get("date", ""),
                "Description": t.get("description", t.get("payer", "")),
                "DocAmt": float(t.get("myr_amount", t.get("amount", 0))),
                "Currency": t.get("currency", "MYR"),
                "CurrencyRate": float(t.get("fx_rate", 1.0)),
                "DebitAcc": "300-000",  # Trade Receivables
                "CreditAcc": "500-000",  # Revenue
                "Tax": "SR-0",
                "TaxAmt": 0,
            })
        return pd.DataFrame(rows)

    def export_wave(self, transactions: List[Dict]) -> pd.DataFrame:
        """Export in Wave Accounting compatible CSV format."""
        rows = []
        for t in transactions:
            rows.append({
                "Transaction Date": t.get("date", ""),
                "Transaction ID": t.get("reference", ""),
                "Account Name": "Sales Revenue",
                "Transaction Type": "Income",
                "Description": f"Payment from {t.get('payer', 'Client')}",
                "Amount (One column)": float(t.get("myr_amount", t.get("amount", 0))),
                "Currency": t.get("currency", "MYR"),
                "Customer": t.get("payer", ""),
            })
        return pd.DataFrame(rows)

    def export_to_excel(self, transactions: List[Dict], format_type: str = "quickbooks") -> io.BytesIO:
        """Export to Excel file in specified format."""
        exporters = {
            "quickbooks": self.export_quickbooks,
            "sql_accounting": self.export_sql_accounting,
            "wave": self.export_wave,
        }

        exporter = exporters.get(format_type, self.export_quickbooks)
        df = exporter(transactions)

        output = io.BytesIO()
        df.to_excel(output, index=False, engine="openpyxl")
        output.seek(0)
        return output

    def get_supported_formats(self) -> List[Dict[str, str]]:
        """Return list of supported export formats."""
        return [
            {"id": "quickbooks", "name": "QuickBooks", "description": "QuickBooks Online/Desktop compatible CSV"},
            {"id": "sql_accounting", "name": "SQL Accounting", "description": "SQL Accounting (Malaysia) import format"},
            {"id": "wave", "name": "Wave", "description": "Wave Accounting compatible format"},
        ]
