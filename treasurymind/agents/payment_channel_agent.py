"""Payment Channel Recommendation Agent - suggests cheapest payment methods."""
from typing import Dict, Any, List


# Payment channel data for Malaysian SMEs
PAYMENT_CHANNELS = {
    "wise": {
        "name": "Wise (TransferWise)",
        "fee_pct": 0.5,
        "flat_fee_myr": 5.0,
        "min_amount_usd": 0,
        "max_amount_usd": 1000000,
        "speed": "1-2 business days",
        "currencies": ["USD", "EUR", "GBP", "AUD", "SGD", "JPY", "CNY"],
        "best_for": "Regular international transfers over USD 200",
    },
    "paypal": {
        "name": "PayPal",
        "fee_pct": 3.9,
        "flat_fee_myr": 2.0,
        "min_amount_usd": 0,
        "max_amount_usd": 10000,
        "speed": "Instant to 3 days",
        "currencies": ["USD", "EUR", "GBP", "AUD", "SGD"],
        "best_for": "Small amounts under USD 100, quick payments",
    },
    "bank_wire": {
        "name": "Bank Wire Transfer",
        "fee_pct": 0.2,
        "flat_fee_myr": 30.0,
        "min_amount_usd": 500,
        "max_amount_usd": 10000000,
        "speed": "2-5 business days",
        "currencies": ["USD", "EUR", "GBP", "AUD", "SGD", "JPY", "CNY", "INR"],
        "best_for": "Large transfers over USD 5,000",
    },
    "duitnow": {
        "name": "DuitNow (Domestic)",
        "fee_pct": 0,
        "flat_fee_myr": 0,
        "min_amount_usd": 0,
        "max_amount_usd": 50000,
        "speed": "Instant",
        "currencies": ["MYR"],
        "best_for": "Domestic Malaysian payments",
    },
    "stripe": {
        "name": "Stripe",
        "fee_pct": 2.9,
        "flat_fee_myr": 1.30,
        "min_amount_usd": 0,
        "max_amount_usd": 100000,
        "speed": "2-7 business days",
        "currencies": ["USD", "EUR", "GBP", "AUD", "SGD"],
        "best_for": "Online business payments, recurring billing",
    },
}


class PaymentChannelAgent:
    """Recommends optimal payment channels based on amount, currency, and country."""

    def recommend(self, amount: float, currency: str, country: str = "") -> List[Dict[str, Any]]:
        """Recommend payment channels sorted by cost."""
        recommendations = []

        for key, channel in PAYMENT_CHANNELS.items():
            if currency.upper() not in channel["currencies"]:
                continue

            fee = self._calculate_fee(amount, channel)
            savings_vs_bank = self._calculate_savings(amount, channel)

            recommendations.append({
                "channel": channel["name"],
                "fee_myr": round(fee, 2),
                "fee_pct_effective": round((fee / max(amount * 4.47, 1)) * 100, 2),
                "speed": channel["speed"],
                "best_for": channel["best_for"],
                "savings_vs_bank_wire": round(savings_vs_bank, 2),
            })

        # Sort by fee (cheapest first)
        recommendations.sort(key=lambda x: x["fee_myr"])

        # Add recommendation text
        if recommendations:
            best = recommendations[0]
            best["recommended"] = True
            best["recommendation_text"] = (
                f"For {currency} {amount:,.2f} from {country or 'international'}, "
                f"{best['channel']} saves you RM {best['savings_vs_bank_wire']:.2f} "
                f"compared to bank wire transfer."
            )

        return recommendations

    def _calculate_fee(self, amount: float, channel: Dict) -> float:
        """Calculate total fee in MYR for a transaction."""
        myr_amount = amount * 4.47  # Approximate USD to MYR
        fee = (myr_amount * channel["fee_pct"] / 100) + channel["flat_fee_myr"]
        return fee

    def _calculate_savings(self, amount: float, channel: Dict) -> float:
        """Calculate savings compared to standard bank wire."""
        bank_wire = PAYMENT_CHANNELS["bank_wire"]
        bank_fee = self._calculate_fee(amount, bank_wire)
        channel_fee = self._calculate_fee(amount, channel)
        return max(bank_fee - channel_fee, 0)

    def get_recommendation_summary(self, transactions: List[Dict]) -> Dict[str, Any]:
        """Analyze past transactions and suggest optimal channels."""
        total_fees_paid = 0
        potential_savings = 0
        suggestions = []

        for t in transactions:
            amount = float(t.get("amount", 0))
            currency = t.get("currency", "USD")
            if currency == "MYR" or amount == 0:
                continue

            recs = self.recommend(amount, currency)
            if recs:
                best = recs[0]
                # Estimate what they paid (assume bank wire)
                bank_fee = self._calculate_fee(amount, PAYMENT_CHANNELS["bank_wire"])
                total_fees_paid += bank_fee
                potential_savings += best.get("savings_vs_bank_wire", 0)

        if potential_savings > 0:
            suggestions.append(
                f"💡 You could save approximately RM {potential_savings:,.2f} per month "
                f"by switching to optimal payment channels for each transaction."
            )

        return {
            "estimated_fees_paid": round(total_fees_paid, 2),
            "potential_savings": round(potential_savings, 2),
            "suggestions": suggestions,
        }
