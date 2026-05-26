"""AI Financial Chatbot Agent - multilingual CFO in your pocket via Chutes AI (DeepSeek V3)."""
import os
from typing import Dict, Any, List
from dotenv import load_dotenv

load_dotenv()

CHUTES_API_KEY = os.getenv("CHUTES_API_KEY", "")
CHUTES_API_BASE = os.getenv("CHUTES_API_BASE", "https://llm.chutes.ai/v1")

SUPPORTED_LANGUAGES = {
    "en": "English",
    "ms": "Bahasa Malaysia",
    "zh": "中文 (Mandarin)",
    "ta": "தமிழ் (Tamil)",
}

SYSTEM_PROMPT = """You are TreasuryMind, an AI financial assistant for Malaysian SMEs.
You help business owners understand their payment reconciliation, cash flow, and finances.

Rules:
- Always respond in the same language the user writes to you in
- Be concise and actionable
- Reference real transaction data when available
- Explain financial concepts simply
- If asked about specific invoices or payments, use the context provided
- Support Bahasa Malaysia, English, Mandarin, and Tamil
- When discussing amounts, use RM (Malaysian Ringgit) as default
- Be proactive — suggest actions the owner should take

You have access to the business's full transaction history and reconciliation data."""


class ChatbotAgent:
    """Multilingual AI chatbot powered by DeepSeek V3 via Chutes AI."""

    def __init__(self):
        self.conversation_history: List[Dict[str, str]] = []
        self.business_context: Dict[str, Any] = {}
        self.client = self._init_client()

    def _init_client(self):
        """Initialize OpenAI-compatible client for Chutes AI."""
        try:
            from openai import OpenAI
            if CHUTES_API_KEY:
                return OpenAI(api_key=CHUTES_API_KEY, base_url=CHUTES_API_BASE)
        except ImportError:
            pass
        return None

    def set_context(self, context: Dict[str, Any]):
        """Update business context for informed responses."""
        self.business_context = context

    def chat(self, user_message: str, language: str = "auto") -> str:
        """Send a message and get a response."""
        # Build context message
        context_msg = self._build_context_message()

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT + "\n\n" + context_msg},
        ]
        messages.extend(self.conversation_history[-10:])  # Last 10 messages for memory
        messages.append({"role": "user", "content": user_message})

        # Try Chutes AI
        if self.client:
            try:
                response = self.client.chat.completions.create(
                    model="deepseek-ai/DeepSeek-V3",
                    messages=messages,
                    max_tokens=1024,
                    temperature=0.7,
                )
                reply = response.choices[0].message.content
            except Exception as e:
                reply = self._fallback_response(user_message)
        else:
            reply = self._fallback_response(user_message)

        # Update history
        self.conversation_history.append({"role": "user", "content": user_message})
        self.conversation_history.append({"role": "assistant", "content": reply})

        return reply

    def _build_context_message(self) -> str:
        """Build context string from business data."""
        if not self.business_context:
            return "No transaction data loaded yet."

        ctx = self.business_context
        parts = []

        if "summary" in ctx:
            s = ctx["summary"]
            parts.append(f"Reconciliation: {s.get('matched_count', 0)} matched, "
                        f"{s.get('unmatched_invoice_count', 0)} unmatched invoices")

        if "fx_summary" in ctx:
            fx = ctx["fx_summary"]
            parts.append(f"FX losses this period: RM {fx.get('total_fx_loss', 0):,.2f}")

        if "alerts" in ctx:
            parts.append(f"Active alerts: {len(ctx['alerts'])}")

        if "forecast" in ctx:
            parts.append(f"Cash flow forecast: {ctx['forecast']}")

        return "Current business data:\n" + "\n".join(parts)

    def _fallback_response(self, message: str) -> str:
        """Provide intelligent fallback when API unavailable."""
        msg_lower = message.lower()

        # Detect language and respond accordingly
        if any(w in msg_lower for w in ["adakah", "berapa", "bagaimana", "saya", "bayaran"]):
            return self._fallback_bm(msg_lower)
        elif any(w in msg_lower for w in ["付款", "发票", "多少", "客户"]):
            return self._fallback_zh(msg_lower)

        # English fallback
        if "payment" in msg_lower or "paid" in msg_lower:
            return self._answer_payment_query()
        elif "cash flow" in msg_lower or "forecast" in msg_lower:
            return self._answer_cashflow_query()
        elif "owe" in msg_lower or "outstanding" in msg_lower:
            return self._answer_outstanding_query()
        elif "fx" in msg_lower or "exchange" in msg_lower or "currency" in msg_lower:
            return self._answer_fx_query()
        else:
            return ("I can help you with payment reconciliation, cash flow forecasts, "
                    "outstanding invoices, and FX analysis. What would you like to know?")

    def _fallback_bm(self, msg: str) -> str:
        """Bahasa Malaysia fallback responses."""
        if "bayaran" in msg or "dibayar" in msg:
            return "Berdasarkan rekod anda, saya boleh semak status bayaran. Sila muat naik penyata bank terkini untuk analisis penuh."
        return "Saya boleh membantu anda dengan penyesuaian bayaran, ramalan aliran tunai, dan analisis FX. Apa yang anda ingin tahu?"

    def _fallback_zh(self, msg: str) -> str:
        """Mandarin fallback responses."""
        if "付款" in msg:
            return "根据您的记录，我可以检查付款状态。请上传最新的银行对账单进行完整分析。"
        return "我可以帮助您进行付款对账、现金流预测和外汇分析。您想了解什么？"

    def _answer_payment_query(self) -> str:
        ctx = self.business_context
        if "summary" in ctx:
            s = ctx["summary"]
            return (f"Based on your latest reconciliation: {s.get('matched_count', 0)} payments matched, "
                    f"{s.get('partial_count', 0)} partial matches, and "
                    f"{s.get('unmatched_payment_count', 0)} unmatched payments.")
        return "Upload your bank statement and receipts so I can check your payment status."

    def _answer_cashflow_query(self) -> str:
        ctx = self.business_context
        if "forecast" in ctx:
            return f"Cash flow forecast: {ctx['forecast']}"
        return "I need your transaction history to generate a cash flow forecast. Upload your bank statement to get started."

    def _answer_outstanding_query(self) -> str:
        ctx = self.business_context
        if "unmatched_invoices" in ctx:
            count = len(ctx["unmatched_invoices"])
            return f"You have {count} outstanding invoices that haven't been matched to payments yet."
        return "Upload your invoices and bank statement so I can identify outstanding payments."

    def _answer_fx_query(self) -> str:
        ctx = self.business_context
        if "fx_summary" in ctx:
            fx = ctx["fx_summary"]
            return (f"FX Summary: Total loss RM {fx.get('total_fx_loss', 0):,.2f}, "
                    f"Total gain RM {fx.get('total_fx_gain', 0):,.2f}, "
                    f"Net: RM {fx.get('net', 0):,.2f}")
        return "I can analyze your FX exposure once you upload transaction data with foreign currencies."

    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []
