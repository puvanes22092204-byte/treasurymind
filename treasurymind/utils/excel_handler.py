"""Excel/bank statement parsing utility."""
import pandas as pd
from typing import List, Dict, Any


def parse_bank_statement(file) -> List[Dict[str, Any]]:
    """Parse uploaded bank statement Excel file into structured records."""
    try:
        df = pd.read_excel(file)
        df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]
        column_map = _detect_columns(df)
        records = []
        for _, row in df.iterrows():
            record = {
                "date": str(row.get(column_map.get("date", ""), "")),
                "amount": _parse_amount(row.get(column_map.get("amount", ""), 0)),
                "currency": str(row.get(column_map.get("currency", ""), "MYR")).upper(),
                "reference": str(row.get(column_map.get("reference", ""), "")),
                "description": str(row.get(column_map.get("description", ""), "")),
                "payer": str(row.get(column_map.get("payer", ""), "")),
            }
            if record["amount"] != 0:
                records.append(record)
        return records
    except Exception as e:
        return [{"error": str(e)}]


def _detect_columns(df: pd.DataFrame) -> Dict[str, str]:
    """Auto-detect column mappings from various bank statement formats."""
    mapping = {}
    cols = list(df.columns)
    date_keywords = ["date", "transaction_date", "value_date", "posting_date"]
    amount_keywords = ["amount", "credit", "debit", "value", "sum", "total"]
    ref_keywords = ["reference", "ref", "ref_no", "transaction_id", "id"]
    desc_keywords = ["description", "desc", "narrative", "details", "particulars"]
    payer_keywords = ["payer", "sender", "from", "remitter", "name"]
    currency_keywords = ["currency", "ccy", "cur"]

    for col in cols:
        if any(k in col for k in date_keywords) and "date" not in mapping:
            mapping["date"] = col
        elif any(k in col for k in amount_keywords) and "amount" not in mapping:
            mapping["amount"] = col
        elif any(k in col for k in ref_keywords) and "reference" not in mapping:
            mapping["reference"] = col
        elif any(k in col for k in desc_keywords) and "description" not in mapping:
            mapping["description"] = col
        elif any(k in col for k in payer_keywords) and "payer" not in mapping:
            mapping["payer"] = col
        elif any(k in col for k in currency_keywords) and "currency" not in mapping:
            mapping["currency"] = col

    # Fallback: use first columns if not detected
    if "date" not in mapping and len(cols) > 0:
        mapping["date"] = cols[0]
    if "amount" not in mapping and len(cols) > 1:
        mapping["amount"] = cols[1]
    if "reference" not in mapping and len(cols) > 2:
        mapping["reference"] = cols[2]

    return mapping


def _parse_amount(value) -> float:
    """Parse amount from various formats."""
    try:
        if isinstance(value, (int, float)):
            return float(value)
        cleaned = str(value).replace(",", "").replace(" ", "").strip()
        return float(cleaned)
    except (ValueError, TypeError):
        return 0.0


def generate_reconciliation_report(results: List[Dict[str, Any]], output_path: str = None) -> pd.DataFrame:
    """Generate a downloadable reconciliation report as DataFrame."""
    df = pd.DataFrame(results)
    if output_path:
        df.to_excel(output_path, index=False, engine="openpyxl")
    return df
