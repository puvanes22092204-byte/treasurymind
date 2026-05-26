"""Multi-Bank Statement Parser - handles Maybank, CIMB, RHB, Public Bank formats."""
import pandas as pd
from typing import Dict, Any, List


# Bank-specific column mappings
BANK_FORMATS = {
    "maybank": {
        "date_cols": ["transaction_date", "date", "posting_date"],
        "amount_cols": ["credit", "amount", "credit_amount"],
        "ref_cols": ["reference", "ref_no", "transaction_ref"],
        "desc_cols": ["description", "transaction_description", "particulars"],
        "date_format": "%d/%m/%Y",
    },
    "cimb": {
        "date_cols": ["transaction_date", "date", "value_date"],
        "amount_cols": ["credit", "amount", "deposit"],
        "ref_cols": ["reference_no", "ref", "cheque_no"],
        "desc_cols": ["description", "transaction_description"],
        "date_format": "%d-%m-%Y",
    },
    "rhb": {
        "date_cols": ["date", "transaction_date", "value_date"],
        "amount_cols": ["credit", "amount", "credit_amount"],
        "ref_cols": ["reference", "ref_no"],
        "desc_cols": ["description", "narrative"],
        "date_format": "%d/%m/%Y",
    },
    "public_bank": {
        "date_cols": ["date", "transaction_date"],
        "amount_cols": ["credit", "amount", "deposits"],
        "ref_cols": ["reference", "cheque_no"],
        "desc_cols": ["description", "particulars", "details"],
        "date_format": "%d/%m/%Y",
    },
}


class BankParser:
    """Parses bank statements from multiple Malaysian banks."""

    def detect_bank(self, df: pd.DataFrame) -> str:
        """Auto-detect which bank the statement is from."""
        cols = [c.lower().strip() for c in df.columns]
        col_str = " ".join(cols)

        # Heuristic detection based on column patterns
        if "maybank" in col_str or "m2u" in col_str:
            return "maybank"
        elif "cimb" in col_str or "cimb_clicks" in col_str:
            return "cimb"
        elif "rhb" in col_str or "rhb_now" in col_str:
            return "rhb"
        elif "public_bank" in col_str or "pbe" in col_str:
            return "public_bank"

        # Fallback: try matching column patterns
        for bank, fmt in BANK_FORMATS.items():
            matches = sum(1 for c in cols if any(bc in c for bc in fmt["date_cols"] + fmt["amount_cols"]))
            if matches >= 2:
                return bank

        return "maybank"  # Default fallback

    def parse_statement(self, file, bank: str = None) -> List[Dict[str, Any]]:
        """Parse a bank statement file with auto-detection."""
        try:
            df = pd.read_excel(file)
            df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

            if not bank:
                bank = self.detect_bank(df)

            fmt = BANK_FORMATS.get(bank, BANK_FORMATS["maybank"])
            records = []

            date_col = self._find_column(df.columns, fmt["date_cols"])
            amount_col = self._find_column(df.columns, fmt["amount_cols"])
            ref_col = self._find_column(df.columns, fmt["ref_cols"])
            desc_col = self._find_column(df.columns, fmt["desc_cols"])

            for _, row in df.iterrows():
                amount = self._parse_amount(row.get(amount_col, 0)) if amount_col else 0
                if amount <= 0:
                    continue

                record = {
                    "date": self._parse_date(row.get(date_col, ""), fmt["date_format"]) if date_col else "",
                    "amount": amount,
                    "currency": "MYR",
                    "reference": str(row.get(ref_col, "")) if ref_col else "",
                    "description": str(row.get(desc_col, "")) if desc_col else "",
                    "bank": bank,
                    "payer": self._extract_payer(str(row.get(desc_col, ""))) if desc_col else "",
                }
                records.append(record)

            return records
        except Exception as e:
            return [{"error": str(e), "bank": bank or "unknown"}]

    def _find_column(self, columns, candidates: List[str]) -> str:
        """Find the first matching column from candidates."""
        cols = list(columns)
        for candidate in candidates:
            for col in cols:
                if candidate in col:
                    return col
        return ""

    def _parse_amount(self, value) -> float:
        """Parse amount from various formats."""
        try:
            if isinstance(value, (int, float)):
                return float(value)
            cleaned = str(value).replace(",", "").replace(" ", "").replace("RM", "").strip()
            return float(cleaned) if cleaned else 0.0
        except (ValueError, TypeError):
            return 0.0

    def _parse_date(self, value, date_format: str) -> str:
        """Parse date to standard format."""
        try:
            if pd.isna(value):
                return ""
            from datetime import datetime
            if isinstance(value, str):
                dt = datetime.strptime(value.strip(), date_format)
                return dt.strftime("%Y-%m-%d")
            elif hasattr(value, "strftime"):
                return value.strftime("%Y-%m-%d")
        except (ValueError, TypeError):
            pass
        return str(value)

    def _extract_payer(self, description: str) -> str:
        """Extract payer name from transaction description."""
        # Common patterns in Malaysian bank statements
        prefixes = ["FT FROM ", "IBG FROM ", "TRF FROM ", "INSTANT TRANSFER FROM ",
                   "GIRO FROM ", "DuitNow FROM "]
        desc_upper = description.upper()
        for prefix in prefixes:
            if prefix in desc_upper:
                idx = desc_upper.index(prefix) + len(prefix)
                return description[idx:].split("/")[0].strip()[:50]
        return ""

    def get_supported_banks(self) -> List[str]:
        """Return list of supported banks."""
        return list(BANK_FORMATS.keys())
