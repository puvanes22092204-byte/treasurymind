"""Invoice Generator Agent - creates professional invoices in multiple currencies."""
from typing import Dict, Any, List
from datetime import datetime, timedelta


class InvoiceAgent:
    """Generates professional invoices connected to the reconciliation system."""

    def __init__(self, business_info: Dict[str, str] = None):
        self.business_info = business_info or {
            "name": "My Business Sdn Bhd",
            "address": "Kuala Lumpur, Malaysia",
            "phone": "+60 12-345 6789",
            "email": "billing@mybusiness.com",
            "bank": "Maybank",
            "account": "1234-5678-9012",
        }
        self.invoice_counter = 1

    def generate_invoice(self, client: Dict[str, str], items: List[Dict],
                        currency: str = "MYR", due_days: int = 30) -> Dict[str, Any]:
        """Generate a professional invoice."""
        ref = f"INV-{self.invoice_counter:04d}"
        self.invoice_counter += 1

        subtotal = sum(item.get("amount", 0) * item.get("quantity", 1) for item in items)
        tax_rate = 0.06  # SST 6%
        tax = round(subtotal * tax_rate, 2)
        total = round(subtotal + tax, 2)

        invoice = {
            "reference": ref,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "due_date": (datetime.now() + timedelta(days=due_days)).strftime("%Y-%m-%d"),
            "business": self.business_info,
            "client": client,
            "items": items,
            "subtotal": subtotal,
            "tax_rate": tax_rate,
            "tax_amount": tax,
            "total": total,
            "currency": currency,
            "status": "pending",
            "notes": f"Payment due within {due_days} days. Thank you for your business.",
        }
        return invoice

    def format_invoice_text(self, invoice: Dict[str, Any]) -> str:
        """Format invoice as readable text (for display/export)."""
        biz = invoice["business"]
        client = invoice["client"]
        currency = invoice["currency"]

        text = f"""
{'='*50}
                    INVOICE
{'='*50}
From: {biz['name']}
      {biz['address']}
      {biz['email']}

To:   {client.get('name', 'N/A')}
      {client.get('address', '')}
      {client.get('email', '')}

Invoice #: {invoice['reference']}
Date:      {invoice['date']}
Due Date:  {invoice['due_date']}
{'─'*50}
"""
        for item in invoice["items"]:
            qty = item.get("quantity", 1)
            amt = item.get("amount", 0)
            desc = item.get("description", "Item")
            line_total = qty * amt
            text += f"  {desc:<30} {qty} x {currency} {amt:>10,.2f} = {currency} {line_total:>10,.2f}\n"

        text += f"""{'─'*50}
  Subtotal:    {currency} {invoice['subtotal']:>10,.2f}
  Tax ({invoice['tax_rate']*100:.0f}%):     {currency} {invoice['tax_amount']:>10,.2f}
  {'─'*30}
  TOTAL:       {currency} {invoice['total']:>10,.2f}
{'='*50}
  {invoice.get('notes', '')}
"""
        return text

    def get_overdue_invoices(self, invoices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter invoices that are overdue."""
        overdue = []
        today = datetime.now()
        for inv in invoices:
            if inv.get("status") == "pending":
                try:
                    due = datetime.strptime(inv["due_date"], "%Y-%m-%d")
                    if today > due:
                        inv["days_overdue"] = (today - due).days
                        overdue.append(inv)
                except (ValueError, KeyError):
                    continue
        return sorted(overdue, key=lambda x: x.get("days_overdue", 0), reverse=True)
