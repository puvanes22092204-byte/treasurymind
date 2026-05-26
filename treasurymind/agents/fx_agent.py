"""FX Conversion Agent - handles currency conversion for reconciliation."""
from typing import Dict, Any, List
from utils.fx_rates import convert_to_myr, get_live_rate


class FXAgent:
    """Converts foreign currency payments to MYR using real-time or historical rates."""

    def convert_payment(self, payment: Dict[str, Any]) -> Dict[str, Any]:
        """Convert a single payment to MYR."""
        amount = payment.get("amount", 0)
        currency = payment.get("currency", "MYR").upper()
        date = payment.get("date", None)

        conversion = convert_to_myr(amount, currency, date)
        payment["myr_amount"] = conversion["myr_amount"]
        payment["fx_rate"] = conversion["rate"]
        payment["fx_source_currency"] = currency
        return payment

    def convert_batch(self, payments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert a batch of payments to MYR."""
        return [self.convert_payment(p) for p in payments]

    def calculate_fx_loss(self, expected_myr: float, received_myr: float) -> Dict[str, Any]:
        """Calculate FX loss between expected and received amounts."""
        difference = round(received_myr - expected_myr, 2)
        return {
            "expected_myr": expected_myr,
            "received_myr": received_myr,
            "difference": difference,
            "is_loss": difference < 0,
            "explanation": self._explain_difference(difference),
        }

    def _explain_difference(self, difference: float) -> str:
        if abs(difference) < 0.50:
            return "Negligible difference — likely rounding."
        elif difference < 0:
            return f"You received RM {abs(difference):.2f} less than expected — likely bank processing fees or unfavorable FX timing."
        else:
            return f"You received RM {difference:.2f} more than expected — favorable FX rate at time of transfer."

    def get_fx_summary(self, payments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate FX loss/gain summary for a batch of payments."""
        total_loss = 0.0
        total_gain = 0.0
        by_currency = {}

        for p in payments:
            expected = p.get("expected_myr", 0)
            received = p.get("myr_amount", 0)
            diff = received - expected
            currency = p.get("fx_source_currency", "USD")

            if diff < 0:
                total_loss += abs(diff)
            else:
                total_gain += diff

            if currency not in by_currency:
                by_currency[currency] = {"loss": 0, "gain": 0, "count": 0}
            by_currency[currency]["count"] += 1
            if diff < 0:
                by_currency[currency]["loss"] += abs(diff)
            else:
                by_currency[currency]["gain"] += diff

        return {
            "total_fx_loss": round(total_loss, 2),
            "total_fx_gain": round(total_gain, 2),
            "net": round(total_gain - total_loss, 2),
            "by_currency": by_currency,
        }

    def check_rate_alert(self, from_currency: str, threshold_pct: float = 2.0) -> Dict[str, Any]:
        """Check if current rate is unusually low compared to average."""
        current_rate = get_live_rate(from_currency, "MYR")
        # Simple heuristic: compare to fallback (average) rate
        from utils.fx_rates import get_fallback_rate
        avg_rate = get_fallback_rate(from_currency, "MYR")
        pct_change = ((current_rate - avg_rate) / avg_rate) * 100

        alert = None
        if pct_change < -threshold_pct:
            alert = f"⚠️ {from_currency}/MYR rate is {abs(pct_change):.1f}% below average — consider delaying conversion"
        elif pct_change > threshold_pct:
            alert = f"✅ {from_currency}/MYR rate is {pct_change:.1f}% above average — good time to convert"

        return {
            "currency": from_currency,
            "current_rate": current_rate,
            "average_rate": avg_rate,
            "pct_change": round(pct_change, 2),
            "alert": alert,
        }
