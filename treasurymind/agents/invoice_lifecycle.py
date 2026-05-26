"""AI Invoice Lifecycle Manager - creation, tracking, matching, and closure."""
from typing import Dict, Any, List
from datetime import datetime, timedelta


class InvoiceLifecycleManager:
    """Manages the full invoice lifecycle from creation to reconciliation."""

    STATUSES = ["DRAFT", "SENT", "VIEWED", "PARTIAL_PAID", "PAID", "OVERDUE", "DISPUTED", "CLOSED"]

    def __init__(self):
        self.invoices = []
        self.counter = 1

    def create_invoice(self, client: Dict, items: List[Dict], currency: str = "MYR",
                      due_days: int = 30, language: str = "en") -> Dict[str, Any]:
        """Create a new invoice with AI-suggested terms."""
        ref = f"INV-{datetime.now().strftime('%Y')}-{self.counter:04d}"
        self.counter += 1

        subtotal = sum(item.get("amount", 0) * item.get("quantity", 1) for item in items)
        tax_rate = 0.06  # SST
        tax = round(subtotal * tax_rate, 2)
        total = round(subtotal + tax, 2)

        invoice = {
            "reference": ref,
            "status": "DRAFT",
            "client": client,
            "items": items,
            "subtotal": subtotal,
            "tax_rate": tax_rate,
            "tax_amount": tax,
            "total": total,
            "currency": currency,
            "language": language,
            "created_at": datetime.now().isoformat(),
            "due_date": (datetime.now() + timedelta(days=due_days)).strftime("%Y-%m-%d"),
            "sent_at": None,
            "paid_at": None,
            "paid_amount": 0,
            "history": [{"action": "created", "timestamp": datetime.now().isoformat()}],
        }

        self.invoices.append(invoice)
        return invoice

    def update_status(self, ref: str, new_status: str, metadata: Dict = None) -> Dict:
        """Update invoice status with audit trail."""
        inv = self._find(ref)
        if not inv:
            return {"error": f"Invoice {ref} not found"}

        old_status = inv["status"]
        inv["status"] = new_status
        inv["history"].append({
            "action": f"status_change: {old_status} → {new_status}",
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {},
        })

        if new_status == "SENT":
            inv["sent_at"] = datetime.now().isoformat()
        elif new_status == "PAID":
            inv["paid_at"] = datetime.now().isoformat()
            inv["paid_amount"] = inv["total"]

        return inv

    def record_payment(self, ref: str, amount: float, currency: str = "MYR") -> Dict:
        """Record a payment against an invoice."""
        inv = self._find(ref)
        if not inv:
            return {"error": f"Invoice {ref} not found"}

        inv["paid_amount"] += amount
        inv["history"].append({
            "action": f"payment_received: {currency} {amount:.2f}",
            "timestamp": datetime.now().isoformat(),
        })

        if inv["paid_amount"] >= inv["total"]:
            inv["status"] = "PAID"
            inv["paid_at"] = datetime.now().isoformat()
        elif inv["paid_amount"] > 0:
            inv["status"] = "PARTIAL_PAID"

        return inv

    def check_overdue(self) -> List[Dict]:
        """Find all overdue invoices."""
        overdue = []
        today = datetime.now()
        for inv in self.invoices:
            if inv["status"] in ("SENT", "VIEWED", "PARTIAL_PAID"):
                due = datetime.strptime(inv["due_date"], "%Y-%m-%d")
                if today > due:
                    days_overdue = (today - due).days
                    inv["status"] = "OVERDUE"
                    inv["days_overdue"] = days_overdue
                    overdue.append(inv)
        return overdue

    def get_aging_report(self) -> Dict[str, Any]:
        """Generate aging report (0-30, 31-60, 61-90, 90+ days)."""
        buckets = {"0-30": [], "31-60": [], "61-90": [], "90+": []}
        today = datetime.now()

        for inv in self.invoices:
            if inv["status"] not in ("PAID", "CLOSED"):
                due = datetime.strptime(inv["due_date"], "%Y-%m-%d")
                days = (today - due).days
                if days <= 30:
                    buckets["0-30"].append(inv)
                elif days <= 60:
                    buckets["31-60"].append(inv)
                elif days <= 90:
                    buckets["61-90"].append(inv)
                else:
                    buckets["90+"].append(inv)

        return {
            bucket: {"count": len(invs), "total": sum(i["total"] - i["paid_amount"] for i in invs)}
            for bucket, invs in buckets.items()
        }

    def get_lifecycle_stats(self) -> Dict[str, Any]:
        """Get overall invoice lifecycle statistics."""
        by_status = {}
        for inv in self.invoices:
            s = inv["status"]
            by_status[s] = by_status.get(s, 0) + 1

        total_outstanding = sum(inv["total"] - inv["paid_amount"]
                               for inv in self.invoices if inv["status"] not in ("PAID", "CLOSED"))

        return {
            "total_invoices": len(self.invoices),
            "by_status": by_status,
            "total_outstanding": round(total_outstanding, 2),
            "overdue_count": len(self.check_overdue()),
        }

    def _find(self, ref: str) -> Dict:
        for inv in self.invoices:
            if inv["reference"] == ref:
                return inv
        return None
