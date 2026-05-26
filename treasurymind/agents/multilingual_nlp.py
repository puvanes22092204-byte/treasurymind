"""Enhanced Multilingual NLP - language detection, translation, and context-aware responses."""
from typing import Dict, Any, Tuple


# Language detection patterns
LANG_PATTERNS = {
    "ms": ["bayaran", "invois", "baki", "akaun", "tunai", "hutang", "terima", "hantar",
           "berapa", "bila", "siapa", "mana", "bagaimana", "adakah", "saya", "anda",
           "ringgit", "bank", "penyata", "laporan", "cukai"],
    "zh": ["付款", "发票", "余额", "账户", "现金", "欠款", "收到", "发送",
           "多少", "什么时候", "谁", "哪里", "怎么", "是否", "我", "你",
           "马币", "银行", "报表", "报告", "税"],
    "ta": ["பணம்", "விலைப்பட்டியல்", "இருப்பு", "கணக்கு", "பணப்புழக்கம்",
           "கடன்", "பெற்றது", "அனுப்பு", "எவ்வளவு", "எப்போது"],
}

# Response templates by language
TEMPLATES = {
    "en": {
        "greeting": "How can I help you with your treasury today?",
        "no_data": "I don't have enough data to answer that. Please upload your bank statement first.",
        "reconciled": "Your reconciliation is complete. {matched} transactions matched, {pending} pending review.",
        "cash_flow": "Your current cash flow is RM {amount}. {trend}",
        "overdue": "You have {count} overdue invoices totalling RM {total}.",
    },
    "ms": {
        "greeting": "Bagaimana saya boleh membantu anda dengan perbendaharaan hari ini?",
        "no_data": "Saya tidak mempunyai data yang mencukupi. Sila muat naik penyata bank anda terlebih dahulu.",
        "reconciled": "Penyesuaian anda selesai. {matched} transaksi sepadan, {pending} menunggu semakan.",
        "cash_flow": "Aliran tunai semasa anda ialah RM {amount}. {trend}",
        "overdue": "Anda mempunyai {count} invois tertunggak berjumlah RM {total}.",
    },
    "zh": {
        "greeting": "今天我能如何帮助您处理财务事务？",
        "no_data": "我没有足够的数据来回答。请先上传您的银行对账单。",
        "reconciled": "对账完成。{matched}笔交易已匹配，{pending}笔待审核。",
        "cash_flow": "您当前的现金流为 RM {amount}。{trend}",
        "overdue": "您有{count}张逾期发票，总计 RM {total}。",
    },
    "ta": {
        "greeting": "இன்று உங்கள் கருவூலத்தில் நான் எவ்வாறு உதவ முடியும்?",
        "no_data": "பதிலளிக்க போதுமான தரவு இல்லை. முதலில் உங்கள் வங்கி அறிக்கையை பதிவேற்றவும்.",
        "reconciled": "சமரசம் முடிந்தது. {matched} பரிவர்த்தனைகள் பொருத்தம், {pending} மதிப்பாய்வு நிலுவையில்.",
        "cash_flow": "உங்கள் தற்போதைய பணப்புழக்கம் RM {amount}. {trend}",
        "overdue": "உங்களிடம் {count} தாமதமான விலைப்பட்டியல்கள் உள்ளன, மொத்தம் RM {total}.",
    },
}


class MultilingualNLP:
    """Language detection and multilingual response generation."""

    def detect_language(self, text: str) -> str:
        """Detect language from text using keyword matching."""
        text_lower = text.lower()
        scores = {"en": 0, "ms": 0, "zh": 0, "ta": 0}

        for lang, patterns in LANG_PATTERNS.items():
            for pattern in patterns:
                if pattern in text_lower:
                    scores[lang] += 1

        # If no non-English detected, default to English
        best = max(scores, key=scores.get)
        return best if scores[best] > 0 else "en"

    def get_template(self, key: str, language: str, **kwargs) -> str:
        """Get a translated template string."""
        lang_templates = TEMPLATES.get(language, TEMPLATES["en"])
        template = lang_templates.get(key, TEMPLATES["en"].get(key, ""))
        try:
            return template.format(**kwargs)
        except (KeyError, IndexError):
            return template

    def translate_status(self, status: str, language: str) -> str:
        """Translate status labels."""
        translations = {
            "ms": {"RECONCILED": "DISESUAIKAN", "PENDING": "MENUNGGU", "SUSPICIOUS": "MENCURIGAKAN", "PROCESSING": "MEMPROSES"},
            "zh": {"RECONCILED": "已对账", "PENDING": "待审核", "SUSPICIOUS": "可疑", "PROCESSING": "处理中"},
            "ta": {"RECONCILED": "சமரசம்", "PENDING": "நிலுவை", "SUSPICIOUS": "சந்தேகம்", "PROCESSING": "செயலாக்கம்"},
        }
        return translations.get(language, {}).get(status, status)

    def format_currency(self, amount: float, currency: str = "MYR", language: str = "en") -> str:
        """Format currency display based on language conventions."""
        if language == "zh":
            return f"{currency} {amount:,.2f}"
        return f"RM {amount:,.2f}" if currency == "MYR" else f"{currency} {amount:,.2f}"
