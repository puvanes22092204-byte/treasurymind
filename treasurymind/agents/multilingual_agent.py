"""Multilingual AI Support - NLP translation and language detection for SEA SMEs."""
from typing import Dict, Any

LANG_MAP = {
    "en": "English", "ms": "Bahasa Malaysia", "zh": "Mandarin",
    "ta": "Tamil", "id": "Bahasa Indonesia", "th": "Thai",
}

# Common financial terms in each language
FINANCIAL_TERMS = {
    "ms": {"invoice": "invois", "payment": "bayaran", "overdue": "tertunggak",
            "balance": "baki", "receipt": "resit", "tax": "cukai"},
    "zh": {"invoice": "发票", "payment": "付款", "overdue": "逾期",
            "balance": "余额", "receipt": "收据", "tax": "税"},
    "ta": {"invoice": "விலைப்பட்டியல்", "payment": "கட்டணம்", "overdue": "தாமதம்",
            "balance": "இருப்பு", "receipt": "ரசீது", "tax": "வரி"},
}


class MultilingualAgent:
    """Handles language detection, translation, and multilingual responses."""

    def detect_language(self, text: str) -> str:
        """Detect language from text using keyword heuristics."""
        text_lower = text.lower()
        if any(w in text_lower for w in ["adakah", "berapa", "bayaran", "saya", "invois"]):
            return "ms"
        elif any(ord(c) > 0x4E00 and ord(c) < 0x9FFF for c in text):
            return "zh"
        elif any(ord(c) > 0x0B80 and ord(c) < 0x0BFF for c in text):
            return "ta"
        return "en"

    def translate_status(self, status: str, lang: str) -> str:
        """Translate reconciliation status to target language."""
        translations = {
            "ms": {"RECONCILED": "Diselaraskan", "PENDING": "Menunggu Semakan",
                   "SUSPICIOUS": "Mencurigakan", "PROCESSING": "Memproses"},
            "zh": {"RECONCILED": "已对账", "PENDING": "待审核",
                   "SUSPICIOUS": "可疑", "PROCESSING": "处理中"},
            "ta": {"RECONCILED": "சரிசெய்யப்பட்டது", "PENDING": "நிலுவையில்",
                   "SUSPICIOUS": "சந்தேகம்", "PROCESSING": "செயலாக்கம்"},
        }
        return translations.get(lang, {}).get(status, status)

    def localize_amount(self, amount: float, currency: str, lang: str) -> str:
        """Format amount in locale-appropriate way."""
        if lang == "ms":
            return f"RM {amount:,.2f}" if currency == "MYR" else f"{currency} {amount:,.2f}"
        return f"{currency} {amount:,.2f}"

    def get_greeting(self, lang: str, user_name: str) -> str:
        """Get localized greeting."""
        greetings = {
            "en": f"Hello {user_name}, how can I help with your treasury today?",
            "ms": f"Hai {user_name}, bagaimana saya boleh bantu kewangan anda hari ini?",
            "zh": f"你好 {user_name}，今天我能帮您处理什么财务事务？",
            "ta": f"வணக்கம் {user_name}, இன்று உங்கள் நிதி விஷயத்தில் எப்படி உதவ முடியும்?",
        }
        return greetings.get(lang, greetings["en"])
