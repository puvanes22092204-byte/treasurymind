"""Cash Flow Prediction Agent - forecasts future cash flow using historical data."""
import pandas as pd
from typing import Dict, Any, List
from datetime import datetime, timedelta


class PredictionAgent:
    """Predicts future cash flow based on historical transaction patterns."""

    def predict_cash_flow(self, transactions: List[Dict], days_ahead: int = 30) -> Dict[str, Any]:
        """Predict cash flow for the next N days."""
        if not transactions:
            return {"error": "No transaction history available"}

        try:
            df = self._prepare_dataframe(transactions)
            forecast = self._simple_forecast(df, days_ahead)
            late_payers = self._identify_late_payers(transactions)
            return {
                "forecast": forecast,
                "late_payer_risk": late_payers,
                "summary": self._generate_summary(forecast, late_payers),
            }
        except Exception as e:
            return {"error": str(e)}

    def _prepare_dataframe(self, transactions: List[Dict]) -> pd.DataFrame:
        """Convert transactions to time-series DataFrame."""
        records = []
        for t in transactions:
            try:
                date = pd.to_datetime(t.get("date", ""))
                amount = float(t.get("myr_amount", t.get("amount", 0)))
                records.append({"ds": date, "y": amount})
            except (ValueError, TypeError):
                continue
        df = pd.DataFrame(records)
        if not df.empty:
            df = df.groupby("ds").sum().reset_index()
            df = df.sort_values("ds")
        return df

    def _simple_forecast(self, df: pd.DataFrame, days_ahead: int) -> List[Dict]:
        """Simple moving average forecast (fallback when Prophet unavailable)."""
        if df.empty:
            return []

        # Calculate daily average from historical data
        total = df["y"].sum()
        date_range = (df["ds"].max() - df["ds"].min()).days or 1
        daily_avg = total / date_range

        forecast = []
        start_date = datetime.now()
        for i in range(days_ahead):
            date = start_date + timedelta(days=i)
            # Add some variance based on day of week
            multiplier = 1.2 if date.weekday() < 5 else 0.5
            predicted = round(daily_avg * multiplier, 2)
            forecast.append({
                "date": date.strftime("%Y-%m-%d"),
                "predicted_amount": predicted,
                "confidence": "medium",
            })

        return forecast

    def _identify_late_payers(self, transactions: List[Dict]) -> List[Dict]:
        """Identify clients with a pattern of late payments."""
        payer_history = {}
        for t in transactions:
            payer = t.get("payer", "Unknown")
            if payer not in payer_history:
                payer_history[payer] = {"count": 0, "late_count": 0}
            payer_history[payer]["count"] += 1
            if t.get("days_overdue", 0) > 0:
                payer_history[payer]["late_count"] += 1

        late_payers = []
        for payer, stats in payer_history.items():
            if stats["count"] > 0:
                late_ratio = stats["late_count"] / stats["count"]
                if late_ratio > 0.3:
                    late_payers.append({
                        "payer": payer,
                        "total_transactions": stats["count"],
                        "late_payments": stats["late_count"],
                        "late_ratio": round(late_ratio * 100, 1),
                        "risk": "HIGH" if late_ratio > 0.5 else "MEDIUM",
                    })

        return sorted(late_payers, key=lambda x: x["late_ratio"], reverse=True)

    def _generate_summary(self, forecast: List[Dict], late_payers: List[Dict]) -> str:
        """Generate human-readable cash flow summary."""
        if not forecast:
            return "Insufficient data for prediction."

        total_expected = sum(f["predicted_amount"] for f in forecast)
        summary = f"Expected incoming: RM {total_expected:,.2f} over the next {len(forecast)} days."

        if late_payers:
            risky = [p["payer"] for p in late_payers[:3]]
            summary += f" Watch out for: {', '.join(risky)} — history of late payments."

        return summary

    def predict_low_balance(self, current_balance: float, forecast: List[Dict],
                           threshold: float = 5000.0) -> Dict[str, Any]:
        """Predict when balance might drop below threshold."""
        running_balance = current_balance
        # Assume average daily expenses
        daily_expense = sum(f["predicted_amount"] for f in forecast) / max(len(forecast), 1) * 0.7

        for i, day in enumerate(forecast):
            running_balance += day["predicted_amount"] - daily_expense
            if running_balance < threshold:
                return {
                    "alert": True,
                    "days_until_low": i + 1,
                    "predicted_date": day["date"],
                    "predicted_balance": round(running_balance, 2),
                    "message": f"⚠️ Your balance will likely drop below RM {threshold:,.0f} in {i+1} days.",
                }

        return {"alert": False, "message": "✅ Cash flow looks healthy for the forecast period."}
