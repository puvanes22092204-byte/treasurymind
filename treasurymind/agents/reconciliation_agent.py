"""Reconciliation & Matching Agent - fuzzy matches payments to invoices."""
from typing import Dict, Any, List
from thefuzz import fuzz


class ReconciliationAgent:
    """Matches bank statement entries to invoices/receipts using fuzzy logic."""

    MATCH_THRESHOLD = 70
    FX_TOLERANCE = 5.0  # RM tolerance for FX variance

    def reconcile(self, invoices: List[Dict], bank_entries: List[Dict]) -> Dict[str, Any]:
        """Run full reconciliation using formula-based classification.

        Status rules:
        - RECONCILED: confidence >= 0.90 AND fxVariance within tolerance
        - PENDING REVIEW: confidence between 0.70 - 0.89
        - SUSPICIOUS: large fxVariance OR duplicate detected
        - PROCESSING: everything else
        """
        results = []
        used_entries = set()

        for inv in invoices:
            best_match = None
            best_score = 0

            for i, entry in enumerate(bank_entries):
                if i in used_entries:
                    continue
                score = self._calculate_match_score(inv, entry)
                if score > best_score:
                    best_score = score
                    best_match = (i, entry)

            if best_match and best_score >= self.MATCH_THRESHOLD:
                idx, entry = best_match
                used_entries.add(idx)
                result = self._build_match_result(inv, entry, best_score)
                results.append(result)
            else:
                # No match found — PROCESSING
                results.append({
                    "invoice": inv,
                    "bank_entry": {},
                    "match_score": best_score,
                    "confidence": best_score / 100.0,
                    "amount_match": False,
                    "fx_variance": 0,
                    "difference": 0,
                    "status": "PROCESSING",
                    "explanation": f"No matching bank entry found for invoice {inv.get('reference', 'N/A')}.",
                })

        # Unmatched bank entries
        unmatched_payments = []
        for i, entry in enumerate(bank_entries):
            if i not in used_entries:
                unmatched_payments.append(entry)

        # Classify results using formulas
        reconciled = [r for r in results if r["status"] == "RECONCILED"]
        pending = [r for r in results if r["status"] == "PENDING"]
        suspicious = [r for r in results if r["status"] == "SUSPICIOUS"]
        processing = [r for r in results if r["status"] == "PROCESSING"]

        # Detect duplicates and mark as suspicious
        duplicates = self.detect_duplicates(bank_entries)
        for dup in duplicates:
            for r in results:
                if r["status"] != "SUSPICIOUS" and r.get("bank_entry") == dup.get("payment_1"):
                    r["status"] = "SUSPICIOUS"
                    r["explanation"] += " Possible duplicate detected."

        # Recalculate after duplicate detection
        reconciled = [r for r in results if r["status"] == "RECONCILED"]
        pending = [r for r in results if r["status"] == "PENDING"]
        suspicious = [r for r in results if r["status"] == "SUSPICIOUS"]
        processing = [r for r in results if r["status"] == "PROCESSING"]

        # KPI calculations
        total_transactions = len(results) + len(unmatched_payments)
        total_fx_variance = sum(abs(r.get("fx_variance", 0)) for r in results)
        total_cash_flow = sum(float(r.get("bank_entry", {}).get("myr_amount",
                             r.get("bank_entry", {}).get("amount", 0))) for r in results if r.get("bank_entry"))

        return {
            "all_results": results,
            "matched": reconciled,
            "partial_matches": pending,
            "unmatched_invoices": processing,
            "unmatched_payments": unmatched_payments,
            "suspicious": suspicious,
            "summary": {
                "total_transactions": total_transactions,
                "total_invoices": len(invoices),
                "total_bank_entries": len(bank_entries),
                "reconciled_count": len(reconciled),
                "pending_count": len(pending),
                "suspicious_count": len(suspicious),
                "processing_count": len(processing),
                "matched_count": len(reconciled),
                "partial_count": len(pending),
                "unmatched_invoice_count": len(processing),
                "unmatched_payment_count": len(unmatched_payments),
                "match_rate": round(len(reconciled) / max(len(invoices), 1) * 100, 1),
                "fx_variance_total": round(total_fx_variance, 2),
                "cash_flow_total": round(total_cash_flow, 2),
            },
        }

    def _calculate_match_score(self, invoice: Dict, entry: Dict) -> int:
        """Calculate fuzzy match score between invoice and bank entry."""
        score = 0

        # Reference number matching (highest weight)
        inv_ref = str(invoice.get("reference", "")).strip()
        entry_ref = str(entry.get("reference", "")).strip()
        if inv_ref and entry_ref:
            ref_score = fuzz.ratio(inv_ref.lower(), entry_ref.lower())
            score += ref_score * 0.4

        # Amount matching
        inv_amount = float(invoice.get("myr_amount", invoice.get("amount", 0)))
        entry_amount = float(entry.get("myr_amount", entry.get("amount", 0)))
        if inv_amount > 0 and entry_amount > 0:
            amount_ratio = min(inv_amount, entry_amount) / max(inv_amount, entry_amount)
            score += amount_ratio * 100 * 0.35

        # Payer/description matching
        inv_payer = str(invoice.get("payer", ""))
        entry_desc = str(entry.get("description", entry.get("payer", "")))
        if inv_payer and entry_desc:
            payer_score = fuzz.partial_ratio(inv_payer.lower(), entry_desc.lower())
            score += payer_score * 0.15

        # Date proximity
        score += 10 * 0.1  # Base date score

        return int(score)

    def _build_match_result(self, invoice: Dict, entry: Dict, score: int) -> Dict[str, Any]:
        """Build detailed match result with formula-based status classification.

        Formulas:
        - expectedAmount = invoiceAmount * fxRate
        - fxVariance = receivedAmount - expectedAmount
        - confidence = match_score / 100

        Classification:
        - confidence >= 0.90 AND fxVariance within tolerance → RECONCILED
        - confidence between 0.70 - 0.89 → PENDING
        - fxVariance large OR duplicate → SUSPICIOUS
        - else → PROCESSING
        """
        # Calculate expected and received amounts
        inv_amount = float(invoice.get("myr_amount", invoice.get("amount", 0)))
        received_amount = float(entry.get("myr_amount", entry.get("amount", 0)))

        # fxVariance = receivedAmount - expectedAmount
        fx_variance = round(received_amount - inv_amount, 2)

        # confidence = score / 100
        confidence = score / 100.0

        # Classify status using rules
        if confidence >= 0.90 and abs(fx_variance) <= self.FX_TOLERANCE:
            status = "RECONCILED"
        elif 0.70 <= confidence < 0.90:
            status = "PENDING"
        elif abs(fx_variance) > self.FX_TOLERANCE * 10:  # Large variance
            status = "SUSPICIOUS"
        else:
            status = "PROCESSING"

        amount_match = status == "RECONCILED"
        explanation = self._generate_explanation(invoice, entry, fx_variance, status, confidence)

        return {
            "invoice": invoice,
            "bank_entry": entry,
            "match_score": score,
            "confidence": confidence,
            "amount_match": amount_match,
            "fx_variance": fx_variance,
            "difference": fx_variance,
            "status": status,
            "explanation": explanation,
        }

    def _generate_explanation(self, inv: Dict, entry: Dict, fx_variance: float,
                              status: str, confidence: float) -> str:
        """Generate plain English explanation of the match."""
        ref = inv.get('reference', 'N/A')

        if status == "RECONCILED":
            if abs(fx_variance) < 0.50:
                return f"Invoice {ref} matched exactly. Confidence {confidence:.0%}."
            return (f"Invoice {ref} reconciled. FX variance of RM {abs(fx_variance):.2f} "
                    f"within tolerance. Confidence {confidence:.0%}.")
        elif status == "PENDING":
            return (f"Invoice {ref} likely matches but confidence is {confidence:.0%}. "
                    f"FX variance: RM {fx_variance:+.2f}. Manual review recommended.")
        elif status == "SUSPICIOUS":
            return (f"Invoice {ref} flagged as suspicious. Large FX variance of "
                    f"RM {fx_variance:+.2f} detected. Possible fraud or duplicate.")
        else:
            return f"Invoice {ref} still processing. Confidence too low ({confidence:.0%})."

    def detect_duplicates(self, payments: List[Dict]) -> List[Dict[str, Any]]:
        """Detect potential duplicate payments."""
        duplicates = []
        for i, p1 in enumerate(payments):
            for j, p2 in enumerate(payments):
                if j <= i:
                    continue
                if (abs(float(p1.get("amount", 0)) - float(p2.get("amount", 0))) < 0.01
                    and fuzz.ratio(str(p1.get("payer", "")), str(p2.get("payer", ""))) > 80):
                    duplicates.append({
                        "payment_1": p1,
                        "payment_2": p2,
                        "alert": "⚠️ Possible duplicate payment detected",
                    })
        return duplicates
