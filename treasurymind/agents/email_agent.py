"""Auto Follow-Up Email Generator Agent - drafts payment reminder emails."""
from typing import Dict, Any, List
from datetime import datetime

TEMPLATES = {
    "en": {
        "subject": "Friendly Reminder: Invoice {ref} — Payment Due",
        "body": """Dear {client},

I hope this message finds you well.

This is a friendly reminder that Invoice {ref} for {currency} {amount} was due on {due_date}. As of today, the payment is {days} days overdue.

Could you kindly confirm the payment status or let me know if there are any issues?

Payment details:
- Invoice: {ref}
- Amount: {currency} {amount}
- Due date: {due_date}

Thank you for your prompt attention to this matter.

Best regards,
{owner_name}""",
    },
    "ms": {
        "subject": "Peringatan Mesra: Invois {ref} — Bayaran Tertunggak",
        "body": """Yang dihormati {client},

Saya harap mesej ini sampai dalam keadaan baik.

Ini adalah peringatan mesra bahawa Invois {ref} berjumlah {currency} {amount} telah tamat tempoh pada {due_date}. Sehingga hari ini, bayaran telah tertunggak selama {days} hari.

Bolehkah anda mengesahkan status bayaran atau maklumkan jika terdapat sebarang isu?

Butiran bayaran:
- Invois: {ref}
- Jumlah: {currency} {amount}
- Tarikh tamat: {due_date}

Terima kasih atas perhatian segera anda.

Yang benar,
{owner_name}""",
    },
    "zh": {
        "subject": "友好提醒：发票 {ref} — 付款到期",
        "body": """尊敬的 {client}，

希望您一切安好。

这是一封友好提醒，发票 {ref} 金额为 {currency} {amount}，到期日为 {due_date}。截至今日，付款已逾期 {days} 天。

请确认付款状态或告知是否有任何问题。

付款详情：
- 发票：{ref}
- 金额：{currency} {amount}
- 到期日：{due_date}

感谢您的及时关注。

此致，
{owner_name}""",
    },
}


class EmailAgent:
    """Generates polite payment reminder emails in multiple languages."""

    def __init__(self, owner_name: str = "Business Owner"):
        self.owner_name = owner_name

    def generate_reminder(self, invoice: Dict[str, Any], language: str = "en") -> Dict[str, str]:
        """Generate a payment reminder email for an overdue invoice."""
        template = TEMPLATES.get(language, TEMPLATES["en"])

        ref = invoice.get("reference", "N/A")
        client = invoice.get("payer", "Valued Client")
        amount = f"{invoice.get('amount', 0):,.2f}"
        currency = invoice.get("currency", "RM")
        due_date = invoice.get("due_date", "N/A")

        # Calculate days overdue
        try:
            due = datetime.strptime(due_date, "%Y-%m-%d")
            days = (datetime.now() - due).days
        except (ValueError, TypeError):
            days = 0

        subject = template["subject"].format(ref=ref)
        body = template["body"].format(
            client=client,
            ref=ref,
            amount=amount,
            currency=currency,
            due_date=due_date,
            days=days,
            owner_name=self.owner_name,
        )

        return {"subject": subject, "body": body, "to": invoice.get("email", ""), "language": language}

    def generate_batch_reminders(self, invoices: List[Dict], language: str = "en") -> List[Dict[str, str]]:
        """Generate reminders for all overdue invoices."""
        reminders = []
        for inv in invoices:
            if inv.get("status") in ["overdue", "pending"]:
                reminders.append(self.generate_reminder(inv, language))
        return reminders

    def generate_thank_you(self, payment: Dict[str, Any], language: str = "en") -> Dict[str, str]:
        """Generate a thank-you email when payment is received."""
        client = payment.get("payer", "Valued Client")
        ref = payment.get("reference", "N/A")
        amount = f"{payment.get('amount', 0):,.2f}"

        if language == "ms":
            subject = f"Terima Kasih — Bayaran untuk {ref} Diterima"
            body = f"Yang dihormati {client},\n\nTerima kasih atas bayaran RM {amount} untuk invois {ref}. Bayaran telah diterima dan direkodkan.\n\nYang benar,\n{self.owner_name}"
        elif language == "zh":
            subject = f"感谢 — 已收到 {ref} 的付款"
            body = f"尊敬的 {client}，\n\n感谢您支付发票 {ref} 的 RM {amount}。付款已收到并记录。\n\n此致，\n{self.owner_name}"
        else:
            subject = f"Thank You — Payment for {ref} Received"
            body = f"Dear {client},\n\nThank you for your payment of RM {amount} for invoice {ref}. Payment has been received and recorded.\n\nBest regards,\n{self.owner_name}"

        return {"subject": subject, "body": body, "to": payment.get("email", ""), "language": language}
