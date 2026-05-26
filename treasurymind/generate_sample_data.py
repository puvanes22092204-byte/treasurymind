"""Generate sample data for TreasuryMind demo."""
import pandas as pd
from datetime import datetime, timedelta
import random
import os


def generate_sample_bank_statement():
    """Generate a sample Maybank bank statement."""
    entries = []
    base_date = datetime(2026, 5, 1)

    clients = [
        ("Acme Corp", "USD", "INV-001"),
        ("TechFlow Pte Ltd", "SGD", "INV-002"),
        ("Global Trade Co", "USD", "INV-003"),
        ("Sakura Industries", "JPY", "INV-004"),
        ("EuroDesign GmbH", "EUR", "INV-005"),
        ("Dragon Logistics", "CNY", "INV-006"),
        ("Smith & Partners", "GBP", "INV-007"),
        ("KL Solutions", "MYR", "INV-008"),
    ]

    for i, (client, currency, ref) in enumerate(clients):
        date = base_date + timedelta(days=random.randint(1, 25))
        # Simulate amounts with slight FX differences
        amounts = {
            "USD": random.uniform(200, 2000),
            "SGD": random.uniform(300, 1500),
            "JPY": random.uniform(20000, 100000),
            "EUR": random.uniform(150, 1800),
            "CNY": random.uniform(1000, 8000),
            "GBP": random.uniform(100, 1500),
            "MYR": random.uniform(500, 5000),
        }
        amount = round(amounts[currency], 2)

        entries.append({
            "Transaction Date": date.strftime("%d/%m/%Y"),
            "Description": f"IBG FROM {client} {ref}",
            "Reference": ref.replace("INV", "TXN") + f"-{random.randint(100,999)}",
            "Credit": round(amount * random.uniform(0.95, 1.02), 2),  # Slight variance
            "Currency": "MYR",
            "Balance": round(random.uniform(10000, 50000), 2),
        })

    df = pd.DataFrame(entries)
    output_path = os.path.join("sample_data", "bank_statement_maybank.xlsx")
    df.to_excel(output_path, index=False, engine="openpyxl")
    print(f"✅ Generated: {output_path}")
    return df


def generate_sample_invoices():
    """Generate sample invoices Excel file."""
    invoices = [
        {"reference": "INV-001", "payer": "Acme Corp", "amount": 500.00, "currency": "USD",
         "date": "2026-05-03", "due_date": "2026-06-03", "status": "pending"},
        {"reference": "INV-002", "payer": "TechFlow Pte Ltd", "amount": 800.00, "currency": "SGD",
         "date": "2026-05-05", "due_date": "2026-06-05", "status": "pending"},
        {"reference": "INV-003", "payer": "Global Trade Co", "amount": 1200.00, "currency": "USD",
         "date": "2026-05-08", "due_date": "2026-06-08", "status": "pending"},
        {"reference": "INV-004", "payer": "Sakura Industries", "amount": 50000.00, "currency": "JPY",
         "date": "2026-05-10", "due_date": "2026-06-10", "status": "pending"},
        {"reference": "INV-005", "payer": "EuroDesign GmbH", "amount": 750.00, "currency": "EUR",
         "date": "2026-05-12", "due_date": "2026-05-20", "status": "overdue", "days_overdue": 6},
        {"reference": "INV-006", "payer": "Dragon Logistics", "amount": 3500.00, "currency": "CNY",
         "date": "2026-05-14", "due_date": "2026-06-14", "status": "pending"},
        {"reference": "INV-007", "payer": "Smith & Partners", "amount": 950.00, "currency": "GBP",
         "date": "2026-05-16", "due_date": "2026-05-25", "status": "overdue", "days_overdue": 1},
        {"reference": "INV-008", "payer": "KL Solutions", "amount": 2500.00, "currency": "MYR",
         "date": "2026-05-18", "due_date": "2026-06-18", "status": "pending"},
    ]

    df = pd.DataFrame(invoices)
    output_path = os.path.join("sample_data", "invoices.xlsx")
    df.to_excel(output_path, index=False, engine="openpyxl")
    print(f"✅ Generated: {output_path}")
    return df


if __name__ == "__main__":
    os.makedirs("sample_data", exist_ok=True)
    print("🧠 TreasuryMind — Generating sample data for demo...")
    generate_sample_bank_statement()
    generate_sample_invoices()
    print("\n✅ All sample data generated! Run the app with: streamlit run app.py")
