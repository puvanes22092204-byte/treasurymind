"""TreasuryMind Flask Server."""
import os
import sys
import json
import io
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.ocr_agent import OCRAgent
from agents.fx_agent import FXAgent
from agents.reconciliation_agent import ReconciliationAgent
from agents.prediction_agent import PredictionAgent
from agents.alert_agent import AlertAgent
from agents.chatbot_agent import ChatbotAgent
from agents.bank_parser import BankParser
from agents.tax_agent import TaxAgent
from agents.payment_channel_agent import PaymentChannelAgent
from agents.client_risk import ClientRiskProfiler
from agents.predictive_alerts import PredictiveAlertEngine
from agents.report_scheduler import ReportScheduler
from agents.multi_treasury import MultiTreasuryManager
from agents.document_vault import DocumentVault
from agents.telegram_bot import TelegramBot
from agents.invoice_lifecycle import InvoiceLifecycleManager
from agents.multilingual_nlp import MultilingualNLP
from agents.treasury_intelligence import TreasuryIntelligenceAgent
from blockchain.logger import BlockchainLogger

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = "treasurymind-secret-2026"

# Init agents
ocr = OCRAgent()
fx = FXAgent()
recon = ReconciliationAgent()
prediction = PredictionAgent()
alert_agent = AlertAgent()
chatbot = ChatbotAgent()
bank_parser = BankParser()
tax_agent = TaxAgent()
channel_agent = PaymentChannelAgent()
blockchain = BlockchainLogger()
risk_profiler = ClientRiskProfiler()
predictive_engine = PredictiveAlertEngine()
report_scheduler = ReportScheduler()
multi_treasury = MultiTreasuryManager()
doc_vault = DocumentVault(vault_path=os.path.join(os.path.dirname(__file__), "vault"))
telegram = TelegramBot()
invoice_mgr = InvoiceLifecycleManager()
nlp = MultilingualNLP()
treasury_intel = TreasuryIntelligenceAgent()


@app.route("/")
def index():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template("dashboard.html", user=session.get("user_name", "User"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form.get("name", "")
        email = request.form.get("email", "")
        if name and email:
            session["logged_in"] = True
            session["user_name"] = name
            return redirect(url_for("index"))
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.json
    message = data.get("message", "")
    response = chatbot.chat(message)
    return jsonify({"response": response})


@app.route("/api/chat-with-file", methods=["POST"])
def api_chat_with_file():
    """Chat with file attachment — extracts data from image/PDF/Excel and responds."""
    file = request.files.get("file")
    message = request.form.get("message", "Analyze this file")

    if not file:
        return jsonify({"response": "No file received."})

    filename = file.filename.lower()
    extracted_info = ""

    # Process based on file type
    if filename.endswith((".png", ".jpg", ".jpeg")):
        # OCR extraction from image
        result = ocr.extract_from_image(file)
        extracted_info = (
            f"**Receipt/Image Analysis:**\n"
            f"- Amount: {result.get('currency', 'MYR')} {result.get('amount', 0)}\n"
            f"- Date: {result.get('date', 'N/A')}\n"
            f"- Reference: {result.get('reference', 'N/A')}\n"
            f"- Payer: {result.get('payer', 'N/A')}\n"
        )
        # Convert to MYR
        if result.get("amount") and result.get("currency"):
            from utils.fx_rates import convert_to_myr
            conversion = convert_to_myr(result["amount"], result["currency"])
            extracted_info += f"- MYR Equivalent: RM {conversion['myr_amount']:.2f} (rate: {conversion['rate']})\n"

    elif filename.endswith(".pdf"):
        results = ocr.extract_from_pdf(file)
        extracted_info = f"**PDF Analysis ({len(results)} entries found):**\n"
        for i, r in enumerate(results[:5], 1):
            extracted_info += f"{i}. {r.get('currency','MYR')} {r.get('amount',0)} — Ref: {r.get('reference','N/A')}\n"

    elif filename.endswith((".xlsx", ".xls", ".csv")):
        entries = bank_parser.parse_statement(file, None)
        if entries and not entries[0].get("error"):
            total = sum(float(e.get("amount", 0)) for e in entries)
            extracted_info = (
                f"**Bank Statement Analysis ({len(entries)} transactions):**\n"
                f"- Total credits: RM {total:,.2f}\n"
                f"- Date range: {entries[0].get('date', 'N/A')} to {entries[-1].get('date', 'N/A')}\n"
                f"- Unique payers: {len(set(e.get('payer','') for e in entries if e.get('payer')))}\n"
            )
        else:
            extracted_info = "Could not parse the bank statement. Please check the format."
    else:
        extracted_info = f"File type not supported for analysis: {filename}"

    # Combine extraction with user question for AI response
    full_prompt = f"User uploaded: {file.filename}\n\nExtracted data:\n{extracted_info}\n\nUser question: {message}"
    ai_response = chatbot.chat(full_prompt)

    # Format response with extracted data + AI analysis
    response = f"{extracted_info}\n\n**AI Analysis:** {ai_response}"
    return jsonify({"response": response.replace("\n", "<br>")})


@app.route("/api/reconcile", methods=["POST"])
def api_reconcile():
    """Handle file uploads and run reconciliation with formula-based classification."""
    files = request.files.getlist("receipts")
    bank_file = request.files.get("bank_statement")

    invoice_data = []
    for f in files:
        if f.filename.lower().endswith(".pdf"):
            invoice_data.extend(ocr.extract_from_pdf(f))
        else:
            invoice_data.append(ocr.extract_from_image(f))

    bank_data = []
    if bank_file:
        bank_data = bank_parser.parse_statement(bank_file, None)

    invoice_data = fx.convert_batch(invoice_data)
    bank_data = fx.convert_batch(bank_data)
    results = recon.reconcile(invoice_data, bank_data)
    fx_summary = fx.get_fx_summary(invoice_data)
    alerts = alert_agent.generate_all_alerts({
        "invoices": invoice_data, "payments": bank_data,
        "fx_data": fx_summary, "cash_flow": {}
    })
    blockchain.log_batch(results["matched"] + results["partial_matches"])

    # Build detailed results for frontend
    all_results = results.get("all_results", results["matched"] + results["partial_matches"])
    detailed = []
    for r in all_results:
        inv = r.get("invoice", {})
        entry = r.get("bank_entry", {})
        detailed.append({
            "invoice_ref": inv.get("reference", "N/A"),
            "payer": inv.get("payer", entry.get("payer", "Unknown")),
            "expected": float(inv.get("myr_amount", inv.get("amount", 0))),
            "received": float(entry.get("myr_amount", entry.get("amount", 0))) if entry else 0,
            "currency": inv.get("currency", "MYR"),
            "fx_rate": float(inv.get("fx_rate", 1.0)),
            "fx_variance": r.get("fx_variance", 0),
            "confidence": r.get("confidence", 0),
            "match_score": r.get("match_score", 0),
            "status": r.get("status", "PROCESSING"),
            "explanation": r.get("explanation", ""),
        })

    summary = results["summary"]
    response_data = {
        "success": True,
        "kpis": {
            "transactions": summary["total_transactions"],
            "reconciled": summary["reconciled_count"],
            "pending_review": summary["pending_count"],
            "suspicious": summary["suspicious_count"],
            "processing": summary["processing_count"],
            "fx_variance": summary["fx_variance_total"],
            "cash_flow": summary["cash_flow_total"],
            "match_rate": summary["match_rate"],
        },
        "results": detailed,
        "summary": summary,
    }

    # Run Treasury Intelligence Agent
    intel_analysis = treasury_intel.analyze(detailed, {"summary": summary}, fx_summary)
    response_data["intelligence"] = intel_analysis

    # Store for session
    session["last_results"] = response_data
    return jsonify(response_data)


@app.route("/api/kpis")
def api_kpis():
    """Get current KPI state. Returns all 0s if no reconciliation has been run."""
    data = session.get("last_results", None)
    if data and data.get("kpis"):
        return jsonify({"success": True, "kpis": data["kpis"]})
    return jsonify({
        "success": True,
        "kpis": {
            "transactions": 0,
            "reconciled": 0,
            "pending_review": 0,
            "suspicious": 0,
            "processing": 0,
            "fx_variance": 0,
            "cash_flow": 0,
            "match_rate": 0,
        }
    })


@app.route("/api/results")
def api_results():
    """Get last reconciliation results."""
    data = session.get("last_results", None)
    if data:
        return jsonify(data)
    return jsonify({"success": False, "message": "No results yet. Run reconciliation first."})


@app.route("/api/download-report")
def download_report():
    """Download reconciliation report as Excel."""
    import pandas as pd
    data = session.get("last_results", None)
    if not data or not data.get("results"):
        return "No results", 404

    rows = []
    for r in data["results"]:
        rows.append({
            "Invoice": r["invoice_ref"],
            "Payer": r["payer"],
            "Currency": r["currency"],
            "FX Rate": r["fx_rate"],
            "Expected (MYR)": r["expected"],
            "Received (MYR)": r["received"],
            "FX Variance": r["fx_variance"],
            "Confidence": f"{r['confidence']*100:.0f}%",
            "Status": r["status"],
            "Explanation": r["explanation"],
        })

    df = pd.DataFrame(rows)
    output = io.BytesIO()
    df.to_excel(output, index=False, engine="openpyxl")
    output.seek(0)

    from flask import send_file
    return send_file(output, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                     as_attachment=True, download_name="reconciliation_report.xlsx")


@app.route("/api/predictive-alerts", methods=["POST"])
def api_predictive_alerts():
    """Get AI-driven predictive alerts."""
    data = request.json or {}
    transactions = data.get("transactions", [])
    invoices = data.get("invoices", [])
    alerts = predictive_engine.analyze_and_alert(transactions, invoices)
    return jsonify({"alerts": alerts, "count": len(alerts)})


@app.route("/api/client-risk/<client_name>")
def api_client_risk(client_name):
    """Get risk profile for a client."""
    # Use stored transactions if available
    last = session.get("last_results", {})
    transactions = []
    if last and last.get("results"):
        transactions = [{"payer": r["payer"], "myr_amount": r["received"],
                        "currency": r["currency"]} for r in last["results"]]
    profile = risk_profiler.build_profile(client_name, transactions)
    return jsonify(profile)


@app.route("/api/client-risk")
def api_all_client_risks():
    """Get all client risk profiles."""
    last = session.get("last_results", {})
    transactions = []
    if last and last.get("results"):
        transactions = [{"payer": r["payer"], "myr_amount": r["received"],
                        "currency": r["currency"]} for r in last["results"]]
    # Build profiles for all unique payers
    payers = set(r["payer"] for r in last.get("results", []) if r.get("payer"))
    profiles = [risk_profiler.build_profile(p, transactions) for p in payers]
    return jsonify({"profiles": profiles})


@app.route("/api/reports/generate", methods=["POST"])
def api_generate_report():
    """Generate a report on demand."""
    data = request.json or {}
    report_type = data.get("type", "daily_reconciliation")
    language = data.get("language", "en")
    last = session.get("last_results", {})
    report = report_scheduler.generate_report(report_type, {"summary": last.get("summary", {})}, language)
    return jsonify(report)


@app.route("/api/reports/available")
def api_available_reports():
    """List available report types."""
    return jsonify({"reports": report_scheduler.get_available_reports()})


@app.route("/api/treasury/consolidated")
def api_consolidated():
    """Get consolidated multi-business treasury view."""
    view = multi_treasury.get_consolidated_view()
    exposure = multi_treasury.get_currency_exposure()
    return jsonify({"view": view, "exposure": exposure})


@app.route("/api/vault/stats")
def api_vault_stats():
    """Get document vault statistics."""
    return jsonify(doc_vault.get_stats())


@app.route("/api/telegram", methods=["POST"])
def api_telegram():
    """Handle Telegram webhook messages."""
    data = request.json or {}
    chat_id = data.get("chat_id", "")
    message = data.get("message", {})
    result = telegram.process_message(chat_id, message)

    # If it's a chat query, route through AI
    if result.get("action") == "chat" and result.get("query"):
        lang = nlp.detect_language(result["query"])
        ai_response = chatbot.chat(result["query"])
        result["reply"] = ai_response
        result["language"] = lang

    return jsonify(result)


@app.route("/api/invoices", methods=["GET", "POST"])
def api_invoices():
    """Create or list invoices."""
    if request.method == "POST":
        data = request.json or {}
        invoice = invoice_mgr.create_invoice(
            client=data.get("client", {}),
            items=data.get("items", []),
            currency=data.get("currency", "MYR"),
            due_days=data.get("due_days", 30),
            language=data.get("language", "en"),
        )
        return jsonify(invoice)
    else:
        return jsonify({
            "invoices": invoice_mgr.invoices,
            "stats": invoice_mgr.get_lifecycle_stats(),
            "aging": invoice_mgr.get_aging_report(),
        })


@app.route("/api/invoices/<ref>/pay", methods=["POST"])
def api_invoice_pay(ref):
    """Record payment against an invoice."""
    data = request.json or {}
    result = invoice_mgr.record_payment(ref, data.get("amount", 0), data.get("currency", "MYR"))
    return jsonify(result)


@app.route("/api/invoices/<ref>/status", methods=["POST"])
def api_invoice_status(ref):
    """Update invoice status."""
    data = request.json or {}
    result = invoice_mgr.update_status(ref, data.get("status", "SENT"))
    return jsonify(result)


@app.route("/api/detect-language", methods=["POST"])
def api_detect_language():
    """Detect language of input text."""
    data = request.json or {}
    text = data.get("text", "")
    lang = nlp.detect_language(text)
    return jsonify({"language": lang, "text": text})


@app.route("/api/intelligence")
def api_intelligence():
    """Run Treasury Intelligence Agent analysis."""
    last = session.get("last_results", {})
    transactions = []
    if last and last.get("results"):
        transactions = last["results"]

    results_data = {"summary": last.get("summary", {})}
    fx_data = last.get("kpis", {})

    analysis = treasury_intel.analyze(transactions, results_data, fx_data)
    return jsonify(analysis)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV") != "production"
    app.run(debug=debug, host="0.0.0.0", port=port)
