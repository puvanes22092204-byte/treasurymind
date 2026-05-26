"""Telegram Finance Assistant - mirrors WhatsApp functionality for Telegram users."""
from typing import Dict, Any, List


class TelegramBot:
    """Handles Telegram-based receipt processing and financial queries."""

    def __init__(self):
        self.sessions = {}

    def process_message(self, chat_id: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming Telegram message."""
        msg_type = message.get("type", "text")
        text = message.get("text", "")

        if msg_type == "photo":
            return {
                "action": "process_receipt",
                "reply": "Processing your receipt image... I'll analyze and match it against your invoices.",
                "chat_id": chat_id,
            }
        elif msg_type == "document":
            filename = message.get("filename", "")
            if filename.endswith((".xlsx", ".xls", ".csv")):
                return {
                    "action": "process_statement",
                    "reply": "Bank statement received. Running reconciliation...",
                    "chat_id": chat_id,
                }
            elif filename.endswith(".pdf"):
                return {
                    "action": "process_invoice",
                    "reply": "PDF invoice received. Extracting data...",
                    "chat_id": chat_id,
                }
        elif msg_type == "text":
            return self._handle_text(chat_id, text)

        return {"action": "unknown", "reply": "Send me a receipt photo, bank statement, or ask a question."}

    def _handle_text(self, chat_id: str, text: str) -> Dict[str, Any]:
        """Route text commands."""
        t = text.lower().strip()

        commands = {
            "/start": "Welcome to TreasuryMind! I'm your AI treasury assistant.\n\nSend me:\n- Receipt photos for instant reconciliation\n- Bank statements (Excel) for batch processing\n- Questions about your finances in any language",
            "/status": "Checking your reconciliation status...",
            "/balance": "Fetching your current cash flow...",
            "/alerts": "Loading your active alerts...",
            "/report": "Generating your daily report...",
            "/help": "Commands:\n/status - Reconciliation status\n/balance - Cash flow\n/alerts - Active alerts\n/report - Generate report\n/risk [client] - Client risk score",
        }

        if t in commands:
            return {"action": t.replace("/", ""), "reply": commands[t], "chat_id": chat_id}

        if t.startswith("/risk"):
            client = t.replace("/risk", "").strip()
            return {"action": "client_risk", "client": client,
                    "reply": f"Analyzing risk profile for {client}...", "chat_id": chat_id}

        # Natural language query
        return {"action": "chat", "reply": None, "query": text, "chat_id": chat_id}

    def format_reconciliation_result(self, result: Dict) -> str:
        """Format result for Telegram (supports markdown)."""
        status = result.get("status", "PROCESSING")
        ref = result.get("invoice_ref", "N/A")
        conf = result.get("confidence", 0)
        variance = result.get("fx_variance", 0)

        emoji = {"RECONCILED": "✅", "PENDING": "⚠️", "SUSPICIOUS": "🚨", "PROCESSING": "⏳"}
        icon = emoji.get(status, "📋")

        return (
            f"{icon} *{status}*\n\n"
            f"Invoice: `{ref}`\n"
            f"Confidence: {conf*100:.0f}%\n"
            f"FX Variance: RM {variance:+.2f}\n"
            f"_{result.get('explanation', '')}_"
        )

    def format_alert(self, alert: Dict) -> str:
        """Format alert for Telegram."""
        severity_icon = {"critical": "🔴", "high": "🟠", "medium": "🟡"}
        level = alert.get("escalation", {}).get("level", "medium")
        return f"{severity_icon.get(level, '🔵')} *{alert.get('title', '')}*\n{alert.get('message', '')}"
