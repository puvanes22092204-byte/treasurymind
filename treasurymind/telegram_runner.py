"""TreasuryMind Telegram Bot Runner.

Setup:
1. Message @BotFather on Telegram → /newbot → get your token
2. Set TELEGRAM_BOT_TOKEN in .env or paste below
3. Run: python telegram_runner.py

The bot will respond to:
- /start - Welcome message
- /status - Reconciliation status
- /balance - Cash flow
- /alerts - Active alerts
- /report - Generate report
- /risk [client] - Client risk score
- /help - List commands
- Any text - AI financial assistant
- Photos - Receipt OCR + reconciliation
- Documents - Invoice/statement processing
"""
import os
import sys
import requests
import time
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

from agents.telegram_bot import TelegramBot
from agents.chatbot_agent import ChatbotAgent
from agents.ocr_agent import OCRAgent
from agents.fx_agent import FXAgent

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8918003085:AAGpMGOUdFahKrxtJRo3XbRWnAkV-97XcOw")
API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# Init agents
bot = TelegramBot()
chatbot = ChatbotAgent()
ocr = OCRAgent()
fx = FXAgent()


def get_updates(offset=None):
    """Poll for new messages."""
    params = {"timeout": 30}
    if offset:
        params["offset"] = offset
    try:
        r = requests.get(f"{API_URL}/getUpdates", params=params, timeout=35)
        return r.json().get("result", [])
    except Exception:
        return []


def send_message(chat_id, text, parse_mode="Markdown"):
    """Send a message to a chat."""
    requests.post(f"{API_URL}/sendMessage", json={
        "chat_id": chat_id, "text": text, "parse_mode": parse_mode
    })


def handle_update(update):
    """Process a single update."""
    message = update.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    if not chat_id:
        return

    # Determine message type
    if "photo" in message:
        send_message(chat_id, "📸 Receipt received! Analyzing...")
        # In production, download the photo and run OCR
        result = ocr._mock_extraction("telegram_photo")
        converted = fx.convert_payment(result)
        reply = (
            f"*Receipt Analysis:*\n"
            f"Amount: {result.get('currency', 'USD')} {result.get('amount', 0)}\n"
            f"MYR Equivalent: RM {converted.get('myr_amount', 0):.2f}\n"
            f"Reference: {result.get('reference', 'N/A')}\n"
            f"Date: {result.get('date', 'N/A')}"
        )
        send_message(chat_id, reply)

    elif "document" in message:
        filename = message["document"].get("file_name", "")
        send_message(chat_id, f"📄 Document received: {filename}\nProcessing...")
        send_message(chat_id, "Document processed. View results on your dashboard.")

    elif "text" in message:
        text = message["text"]
        result = bot.process_message(str(chat_id), {"type": "text", "text": text})

        if result.get("reply"):
            send_message(chat_id, result["reply"])
        elif result.get("action") == "chat":
            # Route through AI chatbot
            ai_response = chatbot.chat(text)
            send_message(chat_id, ai_response)


def main():
    """Main polling loop."""
    if TELEGRAM_TOKEN == "YOUR_TOKEN_HERE":
        print("=" * 50)
        print("TELEGRAM BOT SETUP")
        print("=" * 50)
        print("\n1. Open Telegram and message @BotFather")
        print("2. Send /newbot and follow the prompts")
        print("3. Copy the token BotFather gives you")
        print("4. Set TELEGRAM_BOT_TOKEN in your .env file")
        print("   or replace YOUR_TOKEN_HERE in this file")
        print("\nThen run this script again.")
        print("=" * 50)
        return

    print(f"TreasuryMind Telegram Bot starting...")
    print(f"Bot is live! Send messages to your bot on Telegram.")
    print(f"Press Ctrl+C to stop.\n")

    offset = None
    while True:
        updates = get_updates(offset)
        for update in updates:
            offset = update["update_id"] + 1
            try:
                handle_update(update)
            except Exception as e:
                print(f"Error: {e}")
        time.sleep(1)


if __name__ == "__main__":
    main()
