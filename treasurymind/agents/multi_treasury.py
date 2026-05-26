"""Multi-Business & Multi-Currency Treasury View - aggregated portfolio management."""
from typing import Dict, Any, List


class MultiTreasuryManager:
    """Manages multiple business entities and currencies in a unified view."""

    def __init__(self):
        self.businesses = {}
        self.exchange_rates = {
            "USD": 4.47, "EUR": 4.85, "GBP": 5.65, "SGD": 3.35,
            "AUD": 2.95, "JPY": 0.030, "CNY": 0.62, "THB": 0.13,
            "IDR": 0.00028, "INR": 0.053,
        }

    def add_business(self, business_id: str, name: str, base_currency: str = "MYR",
                    country: str = "MY") -> Dict:
        """Register a new business entity."""
        biz = {
            "id": business_id,
            "name": name,
            "base_currency": base_currency,
            "country": country,
            "accounts": [],
            "transactions": [],
            "created": True,
        }
        self.businesses[business_id] = biz
        return biz

    def get_consolidated_view(self) -> Dict[str, Any]:
        """Get aggregated treasury view across all businesses."""
        total_myr = 0
        by_currency = {}
        by_business = {}

        for biz_id, biz in self.businesses.items():
            biz_total = 0
            for txn in biz.get("transactions", []):
                amount = float(txn.get("amount", 0))
                currency = txn.get("currency", "MYR")
                rate = self.exchange_rates.get(currency, 1.0) if currency != "MYR" else 1.0
                myr_amount = amount * rate

                total_myr += myr_amount
                biz_total += myr_amount
                by_currency[currency] = by_currency.get(currency, 0) + amount

            by_business[biz_id] = {
                "name": biz["name"],
                "total_myr": round(biz_total, 2),
                "transaction_count": len(biz.get("transactions", [])),
            }

        return {
            "total_portfolio_myr": round(total_myr, 2),
            "business_count": len(self.businesses),
            "by_currency": {k: round(v, 2) for k, v in by_currency.items()},
            "by_business": by_business,
            "base_currency": "MYR",
        }

    def get_currency_exposure(self) -> List[Dict]:
        """Calculate net currency exposure across all businesses."""
        exposure = {}
        for biz in self.businesses.values():
            for txn in biz.get("transactions", []):
                cur = txn.get("currency", "MYR")
                amt = float(txn.get("amount", 0))
                exposure[cur] = exposure.get(cur, 0) + amt

        result = []
        for cur, amount in sorted(exposure.items(), key=lambda x: -x[1]):
            rate = self.exchange_rates.get(cur, 1.0) if cur != "MYR" else 1.0
            result.append({
                "currency": cur,
                "amount": round(amount, 2),
                "myr_equivalent": round(amount * rate, 2),
                "rate": rate,
                "pct_of_total": 0,  # Calculated after
            })

        total = sum(r["myr_equivalent"] for r in result) or 1
        for r in result:
            r["pct_of_total"] = round(r["myr_equivalent"] / total * 100, 1)

        return result
