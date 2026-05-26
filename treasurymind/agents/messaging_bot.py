"""WhatsApp & Telegram Finance Assistant - messaging platform integration."""
from typing import Dict, Any, List


class MessagingBot:
    """Unified messaging bot for WhatsApp and Telegram treasury interactions."""

    def __init__(self, chatbot_agent=None):
        self.chatbot = chatbot_agent
        self.sessions = {}  # phone -> session state

    def handle_message(self, platform: str, sender: str, message: Dict) -> Dict[str, Any]:
        """Process incoming message from WhatsApp or Telegram."""
        msg_type = message.get("type", "text")
        text = message.get("text", "")

        if msg_type == "image":
            return self._handle_receipt_image(platform, sender, message)
        elif msg_type == "document":
            return self._handle_document(platform, sender, message)
        else:
            return self._handle_text(platform, sender, text)

    def _handle_text(self, platform: str, sender: str, text: str) -> Dict:
        """Handle text queries via messaging."""
        text_lower = text.lower()

        # Quick commands
        if text_lower in ["/status", "status", "semak"]:
            return {"reply": self._get_status_summary(), "type": "text"}
        elif text_lower in ["/balance", "baki", "balance"]:
            return {"reply": self._get_balance(), "type": "text"}
        elif text_lower in ["/help", "help", "bantuan"]:
            return {"reply": self._get_help_text(platform), "type": "text"}
        elif text_lower in ["/report", "report", "laporan"]:
            return {"reply": "Generating your reconciliation report...", "type": "text",
                    "action": "generate_report"}

        # AI chat
        if self.chatbot:
            response = self.chatbot.chat(text)
            return {"reply": response, "type": "text"}

        return {"reply": "Send a receipt photo for instant reconciliation, or type /help for commands.", "type": "text"}

    def _handle_receipt_image(self, platform: str, sender: str, message: Dict) -> Dict:
        """Process receipt image sent via messaging."""
        return {
            "reply": "Receipt received! Processing with AI...\n\n"
                     "I'll match it against your invoices and reply with the result.",
            "type": "text",
            "action": "process_receipt",
            "status": "processing",
        }

    def _handle_document(self, platform: str, sender: str, message: Dict) -> Dict:
        """Process document (PDF invoice, bank statement) via messaging."""
        return {
            "reply": "Document received! I'll extract the data and run reconciliation.",
            "type": "text",
            "action": "process_document",
        }

    def _get_status_summary(self) -> str:
        return ("Treasury Status:\n"
                "• Reconciled: 1,089 (87%)\n"
                "• Pending Review: 124\n"
                "• Suspicious: 14\n"
                "• Cash Flow: RM 8.4M\n\n"
                "Type /report for full details.")

    def _get_balance(self) -> str:
        return ("Current Balance Summary:\n"
                "• MYR: RM 2,450,000\n"
                "• USD: $180,000\n"
                "• EUR: €95,000\n\n"
                "Net position: RM 3,200,000 equivalent")

    def _get_help_text(self, platform: str) -> str:
        return ("TreasuryMind Commands:\n\n"
                "/status - View reconciliation status\n"
                "/balance - Check current balances\n"
                "/report - Generate reconciliation report\n"
                "/help - Show this help\n\n"
                "Or simply:\n"
                "• Send a receipt photo for instant matching\n"
                "• Send a PDF invoice for processing\n"
                "• Ask any finance question in BM, EN, ZH, or TA")

    def format_reconciliation_result(self, result: Dict) -> str:
        """Format a reconciliation result for messaging."""
        status = result.get("status", "PROCESSING")
        ref = result.get("invoice", {}).get("reference", "N/A")
        conf = result.get("confidence", 0)
        variance = result.get("fx_variance", 0)

        icon = "✅" if status == "RECONCILED" else "⚠️" if status == "PENDING" else "🚨"
        return (f"{icon} {status}\n\n"
                f"Invoice: {ref}\n"
                f"Confidence: {conf*100:.0f}%\n"
                f"FX Variance: RM {variance:+.2f}\n\n"
                f"Type /status for full overview.")
