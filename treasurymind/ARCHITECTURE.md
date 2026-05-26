# TreasuryMind — System Architecture

## Unified Data Flow

```
[Input Sources]
    ├── Receipt Images (OCR) ──────┐
    ├── PDF Invoices ──────────────┤
    ├── Bank Statements (Excel) ───┤
    ├── WhatsApp Messages ─────────┤
    ├── Telegram Messages ─────────┤
    └── Manual Entry ──────────────┘
                                   │
                                   ▼
            ┌──────────────────────────────────┐
            │     DOCUMENT VAULT (Secure)       │
            │  SHA-256 hashing + audit trail    │
            └──────────────────────────────────┘
                                   │
                                   ▼
            ┌──────────────────────────────────┐
            │     OCR + EXTRACTION AGENT        │
            │  Tesseract / AI-powered parsing   │
            └──────────────────────────────────┘
                                   │
                                   ▼
            ┌──────────────────────────────────┐
            │     FX CONVERSION AGENT           │
            │  Real-time + historical rates     │
            │  expectedAmount = amount × fxRate │
            └──────────────────────────────────┘
                                   │
                                   ▼
            ┌──────────────────────────────────┐
            │   RECONCILIATION ENGINE           │
            │  Fuzzy matching + formula-based   │
            │  fxVariance = received - expected │
            │                                  │
            │  Classification:                 │
            │  ≥90% conf + low var → RECONCILED│
            │  70-89% conf → PENDING           │
            │  High var/dup → SUSPICIOUS       │
            │  Else → PROCESSING               │
            └──────────────────────────────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    ▼              ▼              ▼
        ┌───────────────┐ ┌──────────────┐ ┌──────────────┐
        │ ALERT ENGINE  │ │ BLOCKCHAIN   │ │ INVOICE      │
        │ Predictive +  │ │ AUDIT LOG    │ │ LIFECYCLE    │
        │ Anomaly       │ │ Polygon      │ │ MANAGER      │
        └───────────────┘ └──────────────┘ └──────────────┘
                    │                              │
                    ▼                              ▼
        ┌───────────────┐              ┌──────────────┐
        │ CLIENT RISK   │              │ REPORT       │
        │ PROFILER      │              │ SCHEDULER    │
        │ 0-100 scoring │              │ Auto-gen     │
        └───────────────┘              └──────────────┘
                    │
                    ▼
        ┌───────────────────────────────────────────┐
        │          TREASURY COPILOT (AI)            │
        │  DeepSeek V3 via Chutes AI                │
        │  Multilingual: EN, BM, ZH, TA            │
        │  Context-aware financial responses        │
        └───────────────────────────────────────────┘
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
    [Dashboard] [WhatsApp] [Telegram]
```

## Agent Architecture

| Agent | Responsibility | Input | Output |
|-------|---------------|-------|--------|
| OCR Agent | Extract data from images/PDFs | Image/PDF files | Structured payment data |
| FX Agent | Currency conversion | Amount + currency | MYR equivalent + rate |
| Reconciliation Agent | Match payments to invoices | Invoices + bank entries | Classified results |
| Prediction Agent | Cash flow forecasting | Transaction history | 30-day forecast |
| Alert Agent | Proactive notifications | All transaction data | Prioritized alerts |
| Predictive Alert Engine | AI-driven warnings | Patterns + history | Escalated alerts |
| Client Risk Profiler | Risk scoring | Client transaction history | 0-100 risk score |
| Invoice Lifecycle | Full invoice management | Invoice data | Status tracking |
| Report Scheduler | Automated reports | Reconciliation data | Formatted reports |
| Multi-Treasury | Portfolio aggregation | Multiple businesses | Consolidated view |
| Document Vault | Secure storage | Files | Hashed + verified storage |
| Multilingual NLP | Language detection + translation | Text input | Detected lang + response |
| Chatbot Agent | Conversational AI | User queries | Contextual answers |
| WhatsApp Agent | Messaging integration | WhatsApp messages | Reconciliation replies |
| Telegram Bot | Messaging integration | Telegram messages | Financial responses |
| Blockchain Logger | Immutable audit trail | Decisions | On-chain records |

## KPI Formulas

```
Transactions     = count(all transactions)
Reconciled       = count(status === "RECONCILED")
Pending Review   = count(status === "PENDING")
Suspicious       = count(status === "SUSPICIOUS")
Processing       = count(status === "PROCESSING")
FX Variance      = sum(all fxVariance)
Cash Flow        = sum(receivedAmount)

expectedAmount   = invoiceAmount × fxRate
fxVariance       = receivedAmount - expectedAmount
confidence       = matchScore / 100
```

## Client Risk Scoring Model

```
Risk Score (0-100) = sum of:
  - Late payment factor (0-40): lateRatio × 40
  - Transaction variance (0-20): (max-min)/max × 20
  - Volume factor (0-15): low volume = higher risk
  - Frequency factor (0-15): few transactions = uncertainty
  - FX complexity (0-10): multiple currencies = complexity

Risk Levels:
  - LOW (0-39): Net 30 terms, RM 50k credit
  - MEDIUM (40-69): Net 15 terms, RM 5k credit
  - HIGH (70-100): Prepayment/COD, no credit
```

## Alert Escalation Logic

```
Severity 1 (Critical):
  → Notify: owner + WhatsApp + email
  → Auto-action: enabled
  → Timeout: 2 hours

Severity 2 (High):
  → Notify: owner + email
  → Auto-action: disabled
  → Timeout: 24 hours

Severity 3+ (Medium/Low):
  → Notify: dashboard only
  → Auto-action: disabled
  → Timeout: 72 hours
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Flask (Python 3.12) |
| AI/LLM | DeepSeek V3 via Chutes AI |
| Frontend | HTML/CSS/JS + Chart.js |
| OCR | Tesseract + Pillow |
| PDF | pdfplumber |
| Excel | pandas + openpyxl |
| FX Rates | ExchangeRate-API |
| Blockchain | Web3.py + Polygon Amoy |
| NLP | Custom multilingual detection |
| Messaging | WhatsApp + Telegram APIs |
| Deployment | Render.com / Railway |

## SDG Alignment

- SDG 1: Prevents SME financial collapse
- SDG 8: Saves hours of manual work monthly
- SDG 10: Fortune 500 tools for micro-SMEs
- SDG 17: Enables cross-border trade
