# 🧠 TreasuryMind — Autonomous SME Financial Intelligence Agent

**AI Marathon 2026: LLM Everywhere | APU AIC × Morpheus AI × Chutes AI**

TreasuryMind gives the smallest Malaysian SME the financial intelligence of a Fortune 500 company — automatically, intelligently, and transparently.

## Features

- 🔄 **Automated Payment Reconciliation** — OCR + fuzzy matching + FX conversion
- 💬 **Multilingual AI Chatbot** — BM, English, Mandarin, Tamil (DeepSeek V3 via Chutes AI)
- 📊 **Financial Health Dashboard** — Real-time metrics, charts, health score
- 🔔 **Smart Alerts** — Late payments, duplicates, FX warnings, cash flow alerts
- 📈 **Cash Flow Prediction** — 30-day forecast with late payer risk
- 🔗 **Blockchain Audit Trail** — Immutable on-chain logging (Polygon testnet)
- 📱 **WhatsApp Integration** — Send receipt photos, get instant reconciliation
- ✉️ **Auto Follow-Up Emails** — Multilingual payment reminders
- 🧾 **Invoice Generator** — Multi-currency professional invoices
- 🏦 **Multi-Bank Support** — Maybank, CIMB, RHB, Public Bank
- 📋 **Tax Summary** — GST/SST-ready monthly/quarterly reports
- 🌍 **Payment Channel Recommendations** — Cheapest way to receive payments
- 📤 **Accounting Export** — SQL Accounting, QuickBooks, Wave

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Copy environment file and add your API keys
cp .env.example .env

# 3. Generate sample data for demo
python generate_sample_data.py

# 4. Run the app
streamlit run app.py
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| AI Brain | Chutes AI (DeepSeek V3) |
| Frontend | Streamlit |
| OCR | Tesseract / Pillow |
| PDF | pdfplumber |
| FX Rates | ExchangeRate-API |
| Prediction | pandas (Prophet-ready) |
| Blockchain | Web3.py + Polygon Amoy |
| Charts | Plotly |

## SDG Alignment

- **SDG 1** — No Poverty (prevents SME financial collapse)
- **SDG 8** — Decent Work & Economic Growth (saves hours monthly)
- **SDG 10** — Reduced Inequalities (Fortune 500 tools for micro-SMEs)
- **SDG 17** — Partnerships for the Goals (enables cross-border trade)
