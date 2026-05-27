"""Treasury Intelligence Agent - data consistency, fraud detection, alert generation."""
from typing import Dict, Any, List
from datetime import datetime


class TreasuryIntelligenceAgent:
    """Elite Treasury Intelligence Agent for fraud detection and data validation."""

    def analyze(self, transactions: List[Dict], results: Dict, fx_summary: Dict) -> Dict[str, Any]:
        """Run full treasury intelligence analysis."""
        dashboard_health = self._check_data_consistency(transactions, results)
        fraud_signals = self._detect_fraud(transactions)
        alerts = self._generate_alerts(transactions, results, fraud_signals)
        insights = self._generate_insights(transactions, results, fx_summary)
        actions = self._recommend_actions(fraud_signals, dashboard_health)

        return {
            "dashboard_health": dashboard_health,
            "alerts": alerts[:5],  # Max 5 alerts
            "fraud_signals": fraud_signals,
            "insights": insights,
            "actions": actions,
        }

    # === 1. DATA CONSISTENCY ENGINE ===
    def _check_data_consistency(self, transactions: List[Dict], results: Dict) -> Dict:
        """Validate KPI consistency: total = matched + unmatched + pending + flagged."""
        s = results.get("summary", {})
        total = s.get("total_transactions", 0)
        reconciled = s.get("reconciled_count", 0)
        pending = s.get("pending_count", 0)
        suspicious = s.get("suspicious_count", 0)
        processing = s.get("processing_count", 0)

        computed_total = reconciled + pending + suspicious + processing
        is_consistent = (total == computed_total) or total == 0

        issues = []
        if not is_consistent:
            issues.append(f"Total ({total}) != Reconciled({reconciled}) + Pending({pending}) + Suspicious({suspicious}) + Processing({processing}) = {computed_total}")

        # Check match rate consistency
        if total > 0:
            expected_rate = round(reconciled / total * 100, 1)
            reported_rate = s.get("match_rate", 0)
            if abs(expected_rate - reported_rate) > 0.5:
                issues.append(f"Match rate mismatch: reported {reported_rate}% vs computed {expected_rate}%")

        return {
            "status": "OK" if not issues else "Issues found",
            "consistent": is_consistent,
            "issues": issues,
            "validated_totals": {
                "total": total,
                "reconciled": reconciled,
                "pending": pending,
                "suspicious": suspicious,
                "processing": processing,
            }
        }

    # === 2. FRAUD & ANOMALY DETECTION ===
    def _detect_fraud(self, transactions: List[Dict]) -> List[Dict]:
        """Detect fraud patterns using multi-signal scoring."""
        signals = []

        if not transactions:
            return signals

        amounts = [float(t.get("myr_amount", t.get("amount", 0))) for t in transactions]
        avg_amount = sum(amounts) / len(amounts) if amounts else 0
        payers = [t.get("payer", "") for t in transactions]
        unique_payers = set(payers)

        for i, txn in enumerate(transactions):
            score = 0
            reasons = []
            amount = float(txn.get("myr_amount", txn.get("amount", 0)))
            payer = txn.get("payer", "Unknown")
            ref = txn.get("reference", f"TXN-{i}")

            # A. Statistical anomaly: amount > 3x average
            if avg_amount > 0 and amount > avg_amount * 3:
                score += 30
                reasons.append(f"Abnormal amount: RM {amount:,.2f} is {amount/avg_amount:.1f}x above average")

            # B. Behavioral: new/unseen counterparty with large amount
            payer_count = payers.count(payer)
            if payer_count <= 1 and amount > avg_amount * 1.5:
                score += 20
                reasons.append(f"New counterparty '{payer}' with above-average transaction")

            # C. Structuring: near-identical amounts (within 0.1%)
            similar_count = sum(1 for a in amounts if abs(a - amount) < amount * 0.001 and a == amount)
            if similar_count > 1:
                score += 25
                reasons.append(f"Repeated amount pattern: RM {amount:,.2f} appears {similar_count} times")

            # D. Reconciliation failure
            status = txn.get("status", "")
            if status in ("SUSPICIOUS", "PROCESSING"):
                score += 20
                reasons.append(f"Reconciliation status: {status}")

            # E. Unknown sender (no matching invoice reference)
            if "unknown" in payer.lower() or "offshore" in payer.lower():
                score += 20
                reasons.append(f"Unknown/offshore entity: {payer}")

            # F. Unusual currency
            currency = txn.get("currency", "MYR")
            if currency not in ("MYR", "USD", "EUR", "SGD"):
                score += 15
                reasons.append(f"Unusual currency: {currency}")

            # Only flag if score > 30
            if score > 30:
                risk_level = "High Risk" if score > 60 else "Review"
                signals.append({
                    "reference": ref,
                    "payer": payer,
                    "amount": amount,
                    "score": min(score, 100),
                    "risk_level": risk_level,
                    "reasons": reasons,
                    "icon": "🚨" if score > 60 else "⚠",
                })

        return sorted(signals, key=lambda x: x["score"], reverse=True)

    # === 3. ALERT GENERATION ===
    def _generate_alerts(self, transactions: List[Dict], results: Dict,
                        fraud_signals: List[Dict]) -> List[Dict]:
        """Generate prioritized alerts (max 5)."""
        alerts = []
        s = results.get("summary", {})

        # High risk fraud alerts
        high_risk = [f for f in fraud_signals if f["score"] > 60]
        if high_risk:
            alerts.append({
                "priority": 1,
                "icon": "🚨",
                "type": "High Risk",
                "message": f"{len(high_risk)} transactions flagged — {high_risk[0]['reasons'][0]}",
            })

        # Structuring detection
        structuring = [f for f in fraud_signals if any("Repeated amount" in r for r in f["reasons"])]
        if structuring:
            alerts.append({
                "priority": 1,
                "icon": "🚨",
                "type": "High Risk",
                "message": f"Structuring pattern detected: {len(structuring)} transactions with near-identical amounts",
            })

        # Unmatched ratio warning
        total = s.get("total_transactions", 0)
        unmatched = s.get("processing_count", 0) + s.get("suspicious_count", 0)
        if total > 0 and (unmatched / total) > 0.2:
            alerts.append({
                "priority": 2,
                "icon": "⚠",
                "type": "Warning",
                "message": f"Unmatched ratio at {unmatched/total*100:.0f}% — exceeds 20% threshold",
            })

        # FX variance alert
        fx_var = s.get("fx_variance_total", 0)
        if abs(fx_var) > 100:
            alerts.append({
                "priority": 3,
                "icon": "⚠",
                "type": "Warning",
                "message": f"Total FX variance: RM {abs(fx_var):,.2f} — review rate discrepancies",
            })

        # Insight: currency distribution
        currencies = {}
        for t in transactions:
            c = t.get("currency", "MYR")
            currencies[c] = currencies.get(c, 0) + 1
        if currencies:
            dominant = max(currencies, key=currencies.get)
            pct = currencies[dominant] / len(transactions) * 100
            alerts.append({
                "priority": 4,
                "icon": "📊",
                "type": "Insight",
                "message": f"{dominant} accounts for {pct:.0f}% of transaction volume",
            })

        return sorted(alerts, key=lambda x: x["priority"])[:5]

    # === 4. INSIGHTS ===
    def _generate_insights(self, transactions: List[Dict], results: Dict, fx: Dict) -> List[str]:
        """Generate key insights."""
        insights = []
        s = results.get("summary", {})

        if s.get("match_rate", 0) > 0:
            insights.append(f"Reconciliation rate: {s['match_rate']}%")

        if s.get("reconciled_count", 0) > 0:
            insights.append(f"{s['reconciled_count']} transactions auto-reconciled successfully")

        if fx.get("total_fx_loss", 0) > 0:
            insights.append(f"FX losses this period: RM {fx['total_fx_loss']:,.2f}")

        if len(transactions) > 0:
            total_value = sum(float(t.get("myr_amount", t.get("amount", 0))) for t in transactions)
            insights.append(f"Total processed value: RM {total_value:,.2f}")

        return insights

    # === 5. RECOMMENDED ACTIONS ===
    def _recommend_actions(self, fraud_signals: List[Dict], health: Dict) -> List[str]:
        """Generate concrete next steps."""
        actions = []

        high_risk = [f for f in fraud_signals if f["score"] > 60]
        if high_risk:
            refs = ", ".join(f["reference"] for f in high_risk[:3])
            actions.append(f"Investigate flagged transactions: {refs}")

        structuring = [f for f in fraud_signals if any("Repeated" in r for r in f["reasons"])]
        if structuring:
            actions.append("Review structuring pattern — possible money laundering attempt")

        unknown = [f for f in fraud_signals if any("Unknown" in r or "offshore" in r for r in f["reasons"])]
        if unknown:
            actions.append(f"Verify identity of unknown senders: {', '.join(f['payer'] for f in unknown[:3])}")

        if health.get("issues"):
            actions.append("Resolve data consistency issues in KPI calculations")

        if not actions:
            actions.append("No immediate actions required — system operating normally")

        return actions
