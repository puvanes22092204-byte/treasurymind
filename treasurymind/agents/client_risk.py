"""AI Client Risk Profiling - scoring and behavioral analysis."""
from typing import Dict, Any, List
from datetime import datetime


class ClientRiskProfiler:
    """Builds and maintains risk profiles for each client/counterparty."""

    def __init__(self):
        self.profiles = {}

    def build_profile(self, client_name: str, transactions: List[Dict]) -> Dict[str, Any]:
        """Build or update a client risk profile from transaction history."""
        client_txns = [t for t in transactions if t.get("payer", "").lower() == client_name.lower()]

        if not client_txns:
            return self._default_profile(client_name)

        # Calculate metrics
        total_volume = sum(float(t.get("myr_amount", t.get("amount", 0))) for t in client_txns)
        avg_amount = total_volume / len(client_txns)
        late_count = sum(1 for t in client_txns if t.get("days_overdue", 0) > 0)
        late_ratio = late_count / len(client_txns) if client_txns else 0

        # Risk scoring model (0-100, higher = riskier)
        risk_score = self._calculate_risk_score(client_txns, late_ratio, avg_amount)

        profile = {
            "client_name": client_name,
            "total_transactions": len(client_txns),
            "total_volume": round(total_volume, 2),
            "avg_transaction": round(avg_amount, 2),
            "late_payment_count": late_count,
            "late_payment_ratio": round(late_ratio, 3),
            "risk_score": risk_score,
            "risk_level": self._risk_level(risk_score),
            "late_payment_risk": round(late_ratio, 2),
            "recommended_terms": self._recommend_terms(risk_score),
            "last_updated": datetime.now().isoformat(),
            "insights": self._generate_insights(client_name, client_txns, risk_score, late_ratio),
        }

        self.profiles[client_name.lower()] = profile
        return profile

    def _calculate_risk_score(self, txns: List[Dict], late_ratio: float, avg_amount: float) -> int:
        """Multi-factor risk scoring model."""
        score = 0

        # Late payment factor (0-40 points)
        score += int(late_ratio * 40)

        # Transaction consistency (0-20 points) - irregular amounts = higher risk
        amounts = [float(t.get("myr_amount", t.get("amount", 0))) for t in txns]
        if amounts and max(amounts) > 0:
            variance = (max(amounts) - min(amounts)) / max(amounts)
            score += int(variance * 20)

        # Volume factor (0-15 points) - very small volumes = higher risk
        if avg_amount < 100:
            score += 15
        elif avg_amount < 500:
            score += 8

        # Frequency factor (0-15 points) - few transactions = less data = higher uncertainty
        if len(txns) < 3:
            score += 15
        elif len(txns) < 5:
            score += 8

        # FX complexity (0-10 points)
        currencies = set(t.get("currency", "MYR") for t in txns)
        if len(currencies) > 2:
            score += 10

        return min(score, 100)

    def _risk_level(self, score: int) -> str:
        if score >= 70: return "HIGH"
        elif score >= 40: return "MEDIUM"
        else: return "LOW"

    def _recommend_terms(self, score: int) -> Dict:
        if score >= 70:
            return {"payment_terms": "Prepayment or COD", "credit_limit": 0, "follow_up": "immediate"}
        elif score >= 40:
            return {"payment_terms": "Net 15", "credit_limit": 5000, "follow_up": "weekly"}
        else:
            return {"payment_terms": "Net 30", "credit_limit": 50000, "follow_up": "monthly"}

    def _generate_insights(self, name: str, txns: List[Dict], score: int, late_ratio: float) -> List[str]:
        insights = []
        if late_ratio > 0.5:
            insights.append(f"{name} pays late {late_ratio*100:.0f}% of the time. Consider stricter terms.")
        if score >= 70:
            insights.append(f"High risk client. Recommend prepayment or reduced credit limit.")
        if len(txns) > 10 and late_ratio < 0.1:
            insights.append(f"Reliable client with consistent payment history. Safe for extended terms.")
        return insights

    def _default_profile(self, name: str) -> Dict:
        return {
            "client_name": name, "total_transactions": 0, "total_volume": 0,
            "risk_score": 50, "risk_level": "UNKNOWN", "late_payment_risk": 0.5,
            "recommended_terms": {"payment_terms": "Net 15", "credit_limit": 5000},
            "insights": ["New client — insufficient data for risk assessment."],
        }

    def get_all_profiles(self) -> List[Dict]:
        return list(self.profiles.values())

    def get_profile(self, client_name: str) -> Dict:
        return self.profiles.get(client_name.lower(), self._default_profile(client_name))
