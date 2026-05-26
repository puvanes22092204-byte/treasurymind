"""File Upload Component - handles receipt and bank statement uploads."""
import streamlit as st
from typing import Tuple, List, Any


def render_upload_section() -> Tuple[List[Any], Any]:
    """Render the file upload section and return uploaded files."""
    st.markdown("## 📤 Upload Documents")
    st.markdown("Upload your receipts and bank statement for automatic reconciliation.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🧾 Receipts / Invoices")
        st.caption("Supported: PNG, JPG, PDF")
        receipts = st.file_uploader(
            "Upload receipts or invoices",
            type=["png", "jpg", "jpeg", "pdf"],
            accept_multiple_files=True,
            key="receipts",
            help="Upload payment receipts or PDF invoices to extract payment data",
        )

    with col2:
        st.markdown("### 🏦 Bank Statement")
        st.caption("Supported: XLSX, XLS, CSV")
        bank_statement = st.file_uploader(
            "Upload bank statement",
            type=["xlsx", "xls", "csv"],
            accept_multiple_files=False,
            key="bank_statement",
            help="Upload your bank statement (Maybank, CIMB, RHB, or Public Bank)",
        )

    return receipts or [], bank_statement


def render_bank_selector() -> str:
    """Render bank selection dropdown."""
    banks = {
        "auto": "🔍 Auto-detect",
        "maybank": "🏦 Maybank",
        "cimb": "🏦 CIMB",
        "rhb": "🏦 RHB",
        "public_bank": "🏦 Public Bank",
    }
    selected = st.selectbox("Select your bank (or auto-detect)", options=list(banks.keys()),
                           format_func=lambda x: banks[x])
    return selected if selected != "auto" else None


def render_processing_status(steps: List[str], current_step: int):
    """Render live processing status."""
    for i, step in enumerate(steps):
        if i < current_step:
            st.markdown(f"✅ {step}")
        elif i == current_step:
            st.markdown(f"⏳ {step}...")
        else:
            st.markdown(f"⬜ {step}")
