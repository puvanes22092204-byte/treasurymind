# TreasuryMind — Autonomous SME Financial Intelligence Agent

**AI Marathon 2026: LLM Everywhere | APU AIC × Morpheus AI × Chutes AI**

> An AI CFO + treasury assistant built specifically for Southeast Asian SMEs.

**Live Demo:** [treasurymind-production.up.railway.app](https://treasurymind-production.up.railway.app)
**Telegram Bot:** [@treasurymind_ai_bot](https://t.me/treasurymind_ai_bot)

---

## What It Does

TreasuryMind gives the smallest Malaysian SME the financial intelligence of a Fortune 500 company. It automatically reconciles cross-border payments, detects fraud, predicts cash flow problems, and records every decision on a blockchain audit trail.

**Core Problem:** 98.5% of Malaysian businesses are SMEs. None can afford a CFO. Manual payment reconciliation wastes hours monthly and leads to costly errors.

**Solution:** A fully autonomous multi-agent AI system that handles everything from OCR extraction to fraud detection to multilingual chatbot support.

---

## Features

| Module | Description |
|--------|-------------|
| Smart Reconciliation Engine | Fuzzy-matches payments to invoices with FX conversion and confidence scoring |
| Treasury Intelligence Agent | Real-time fraud detection, anomaly scoring (0-100), data consistency validation |
| AI Treasury Copilot | Multilingual chatbot (EN/BM/ZH/TA) with file upload analysis |
| Invoice Generator | Create professional invoices with SST calculation and lifecycle tracking |
| Predictive Alerts | Cash flow warnings, late payment predictions, FX trend alerts |
| Client Risk Profiling | AI-scored risk assessment (0-100) per counterparty |
| Multi-Business Treasury | Consolidated portfolio view across entities and currencies |
| Document Vault | SHA-256 encrypted storage with tamper detection |
| Blockchain Audit Trail | Immutable on-chain logging (Polygon testnet) |
| WhatsApp & Telegram | Send receipt photos via messaging for instant reconciliation |
| Automated Reports | Daily/weekly/monthly report generation (6 report types) |
| Multi-Bank Support | Maybank, CIMB, RHB, Public Bank statement parsing |
| Accounting Export | SQL Accounting, QuickBooks, Wave compatible formats |

---

## KPI Formulas

```
Transactions     = count(all transactions)
Reconciled       = count(status === "RECONCILED")
Pending Review   = count(status === "PENDING")
Suspicious       = count(status === "SUSPICIOUS")
Processing       = count(status === "PROCESSING")
FX Variance      = sum(all fxVariance)

expectedAmount   = invoiceAmount × fxRate
fxVariance       = receivedAmount - expectedAmount
confidence       = matchScore / 100
```

**Classification Rules:**
- confidence ≥ 0.90 AND fxVariance within tolerance → RECONCILED
- confidence 0.70–0.89 → PENDING REVIEW
- large fxVariance OR duplicate detected → SUSPICIOUS
- else → PROCESSING

---

## Fraud Detection

**Fraud Risk Score (0–100):**
- +30 → abnormal amount (>3x average)
- +20 → new/unseen counterparty
- +25 → structuring (repeated near-identical amounts)
- +20 → unknown/offshore entity
- +20 → reconciliation failure
- +15 → unusual currency

**Classification:**
- 0–30 → Normal ✅
- 31–60 → Review ⚠
- 61–100 → High Risk 🚨

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Flask (Python 3.12) |
| AI/LLM | DeepSeek V3 via Chutes AI |
| Frontend | HTML/CSS/JS + Chart.js |
| OCR | Tesseract + Pillow |
| PDF Parsing | pdfplumber |
| Excel | pandas + openpyxl |
| FX Rates | ExchangeRate-API (with fallback) |
| Blockchain | Web3.py + Polygon Amoy Testnet |
| Messaging | Telegram Bot API |
| NLP | Custom multilingual detection (4 languages) |
| Deployment | Railway.app |

---

## Quick Start

### Local Development

```bash
# Clone
git clone https://github.com/puvanes22092204-byte/treasurymind.git
cd treasurymind

# Setup Python environment
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run web dashboard
python server.py
# Open http://127.0.0.1:5000

# Run Telegram bot (separate terminal)
python telegram_runner.py
```

### Demo Data

Upload these files from `sample_data/` to test fraud detection:
- **invoices.xlsx** → Upload as "Receipts/Invoices" (left side)
- **bank_statement_demo.xlsx** → Upload as "Bank Statement" (right side)

The demo data includes:
- 10 legitimate invoices (USD, EUR, SGD, CNY, JPY, MYR)
- 15 bank entries including fraud scenarios:
  - Duplicate payments
  - Unknown senders
  - Structuring patterns (~RM 9,999 repeated)
  - Offshore entity transfers
  - Large FX variances

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/kpis` | GET | Current KPI state (0s if no data) |
| `/api/reconcile` | POST | Upload files and run reconciliation |
| `/api/results` | GET | Last reconciliation results |
| `/api/intelligence` | GET | Treasury Intelligence analysis |
| `/api/chat` | POST | AI chatbot query |
| `/api/chat-with-file` | POST | Chat with file attachment |
| `/api/invoices` | GET/POST | List or create invoices |
| `/api/client-risk` | GET | All client risk profiles |
| `/api/predictive-alerts` | POST | Run predictive alert analysis |
| `/api/reports/generate` | POST | Generate a report |
| `/api/reports/available` | GET | List report types |
| `/api/treasury/consolidated` | GET | Multi-business view |
| `/api/vault/stats` | GET | Document vault statistics |
| `/api/telegram` | POST | Telegram webhook |
| `/api/download-report` | GET | Download Excel report |
| `/api/detect-language` | POST | Detect input language |

---

## Project Structure

```
treasurymind/
├── server.py                    # Flask backend (main entry point)
├── telegram_runner.py           # Telegram bot runner
├── requirements.txt             # Python dependencies
├── Procfile                     # Railway deployment
├── ARCHITECTURE.md              # System architecture docs
├── agents/
│   ├── ocr_agent.py             # OCR + document extraction
│   ├── fx_agent.py              # FX conversion
│   ├── reconciliation_agent.py  # Matching engine (formula-based)
│   ├── treasury_intelligence.py # Fraud detection + data consistency
│   ├── prediction_agent.py      # Cash flow prediction
│   ├── alert_agent.py           # Proactive alerts
│   ├── predictive_alerts.py     # AI-driven predictive warnings
│   ├── chatbot_agent.py         # Multilingual AI chatbot
│   ├── client_risk.py           # Client risk profiling (0-100)
│   ├── invoice_lifecycle.py     # Invoice creation + tracking
│   ├── bank_parser.py           # Multi-bank statement parser
│   ├── tax_agent.py             # SST/GST tax reports
│   ├── payment_channel_agent.py # Payment channel recommendations
│   ├── multi_treasury.py        # Multi-business aggregation
│   ├── document_vault.py        # Secure document storage
│   ├── multilingual_nlp.py      # Language detection + translation
│   ├── telegram_bot.py          # Telegram message handling
│   ├── whatsapp_agent.py        # WhatsApp integration
│   ├── email_agent.py           # Email reminder generation
│   └── report_scheduler.py      # Automated report generation
├── blockchain/
│   └── logger.py                # Polygon testnet audit trail
├── templates/
│   ├── dashboard.html           # Main dashboard UI
│   └── login.html               # Login page
├── static/
│   ├── style.css                # Dashboard styles
│   ├── charts.js                # Chart.js configurations
│   └── nav.js                   # Navigation logic
├── sample_data/
│   ├── invoices.xlsx            # Demo invoices
│   └── bank_statement_demo.xlsx # Demo bank statement (with fraud)
└── utils/
    ├── fx_rates.py              # FX rate fetching
    ├── excel_handler.py         # Excel parsing
    ├── accounting_export.py     # Export to QuickBooks/SQL/Wave
    └── i18n.py                  # Internationalization
```

---

## SDG Alignment

| SDG | Goal | Contribution |
|-----|------|-------------|
| 1 | No Poverty | Prevents SME financial collapse from undetected errors |
| 8 | Decent Work | Saves hours of manual reconciliation monthly |
| 10 | Reduced Inequalities | Fortune 500 tools for micro-SMEs |
| 17 | Partnerships | Enables cross-border trade for developing nations |

---

## Morpheus AI Alignment

- **Agentic by Design** — Multi-agent pipeline making autonomous decisions
- **Decentralised Compute** — Runs on Chutes AI (decentralised inference)
- **On-Chain Transparency** — Every decision recorded on Polygon testnet
- **MOR Token Utility** — Future deployment on Morpheus network

---

## Languages Supported

- 🇬🇧 English
- 🇲🇾 Bahasa Malaysia
- 🇨🇳 中文 (Mandarin)
- 🇮🇳 தமிழ் (Tamil)

---

## Team

AI Marathon 2026 | APU AIC × Morpheus AI × Chutes AI

---

## License

Built for AI Marathon 2026 hackathon. All rights reserved.
