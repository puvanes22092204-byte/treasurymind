"""WhatsApp Integration Agent - receive receipts and get reconciliation via WhatsApp."""
from typing import Dict, Any, List


class WhatsAppAgent:
    """Handles WhatsApp-based receipt processing and responses."""

    def __init__(self):
        self.pending_messages: List[Dict[str, Any]] = []

    def process_incoming(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process an incoming WhatsApp message (text or image)."""
        msg_type = message.get("type", "text")
        sender = message.get("sender", "Unknown")

        if msg_type == "image":
            return {
                "action": "process_receipt",
                "sender": sender,
                "status": "processing",
                "reply": f"📸 Got your receipt! Processing now... I'll reply with the reconciliation result shortly.",
            }
        elif msg_type == "text":
            text = message.get("text", "")
            return self._handle_text_query(text, sender)
        else:
            return {
                "action": "unknown",
                "reply": "Send me a receipt photo or ask a question about your payments!",
            }

    def _handle_text_query(self, text: str, sender: str) -> Dict[str, Any]:
        """Handle text-based queries via WhatsApp."""
        text_lower = text.lower()

        if any(w in text_lower for w in ["status", "check", "semak"]):
            return {
                "action": "check_status",
                "sender": sender,
                "reply": "🔍 Checking your latest reconciliation status...",
            }
        elif any(w in text_lower for w in ["balance", "baki", "cash"]):
            return {
                "action": "check_balance",
                "sender": sender,
                "reply": "💰 Let me check your current cash flow...",
            }
        elif any(w in text_lower for w in ["invoice", "invois", "bil"]):
            return {
                "action": "check_invoices",
                "sender": sender,
                "reply": "📋 Pulling up your invoice status...",
            }
        else:
            return {
                "action": "chat",
                "sender": sender,
                "reply": "I can help with: 📸 Receipt reconciliation (send photo), "
                         "📊 Payment status, 💰 Cash flow, 📋 Invoice tracking",
            }

    def format_reconciliation_reply(self, result: Dict[str, Any]) -> str:
        """Format reconciliation result as WhatsApp-friendly message."""
        status = result.get("status", "Unknown")
        ref = result.get("invoice", {}).get("reference", "N/A")
        diff = result.get("difference", 0)
        explanation = result.get("explanation", "")

        reply = f"{'✅' if 'Matched' in status else '⚠️'} *{status}*\n\n"
        reply += f"📄 Invoice: {ref}\n"

        if diff != 0:
            reply += f"💰 Difference: RM {abs(diff):.2f} {'less' if diff < 0 else 'more'}\n"

        reply += f"\n💡 {explanation}"
        return reply

    def format_summary_reply(self, summary: Dict[str, Any]) -> str:
        """Format reconciliation summary for WhatsApp."""
        matched = summary.get("matched_count", 0)
        total = summary.get("total_invoices", 0)
        unmatched = summary.get("unmatched_invoice_count", 0)

        reply = "📊 *Reconciliation Summary*\n\n"
        reply += f"✅ Matched: {matched}/{total}\n"
        reply += f"⚠️ Unmatched: {unmatched}\n"
        reply += f"📈 Match rate: {summary.get('match_rate', 0)}%\n"

        if unmatched > 0:
            reply += f"\n⚡ {unmatched} invoices need attention. Open the dashboard for details."

        return reply

    def simulate_whatsapp_flow(self, receipt_data: Dict[str, Any]) -> List[str]:
        """Simulate a complete WhatsApp interaction flow for demo."""
        messages = [
            "📱 *Message received from +60 12-345 6789*",
            "📸 Receipt image received — processing...",
            "⏳ Running OCR extraction...",
            "💱 Converting USD → MYR at today's rate...",
            "🔍 Matching against your invoices...",
            self.format_reconciliation_reply(receipt_data) if receipt_data else "✅ Payment matched successfully!",
        ]
        return messages
