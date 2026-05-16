"""
A2go.ai Webhook Server
Receives inbound events from GHL, Brevo, and MessageBird
and triggers safety pause logic in the local state database.

Deploy with: gunicorn server:app
"""

import logging
import os
import threading
from flask import Flask, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from src.webhooks.ghl_handler import handle_ghl_webhook
from src.webhooks.brevo_handler import handle_brevo_webhook
from src.webhooks.messagebird_handler import handle_messagebird_webhook
from src.sequencer import Sequencer
from src.sync_leads import sync_sheets_to_ghl

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(name)s %(levelname)s %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ─── Shared token auth ─────────────────────────────────────────────────────────
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")

def _check_secret(req) -> bool:
    """Validate shared secret passed as ?secret= or X-Webhook-Secret header."""
    if not WEBHOOK_SECRET:
        return True  # No secret configured → open (dev mode)
    token = req.args.get("secret") or req.headers.get("X-Webhook-Secret", "")
    return token == WEBHOOK_SECRET


# ─── Background Scheduler ──────────────────────────────────────────────────────
def run_orchestration_cycle():
    """Background job that syncs leads and runs the sequencer."""
    try:
        logger.info("=== Starting background orchestration cycle ===")
        # 1. Sync new leads from Sheets to GHL & DB
        logger.info("Running sync_leads...")
        sync_sheets_to_ghl()
        
        # 2. Run the sequencer iteration
        logger.info("Running sequencer...")
        seq = Sequencer()
        seq.run_iteration()
        logger.info("=== Finished background orchestration cycle ===")
    except Exception as e:
        logger.error(f"Error in background orchestration cycle: {e}")

# Initialize and start the scheduler
scheduler = BackgroundScheduler()
# Run every 15 minutes
scheduler.add_job(func=run_orchestration_cycle, trigger="interval", minutes=15)
scheduler.start()


# ─── Dashboard / Root ──────────────────────────────────────────────────────────
@app.route("/", methods=["GET"])
def index():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>A2go Orchestration Engine</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background-color: #0f172a; color: #f8fafc; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
            .card { background-color: #1e293b; padding: 3rem; border-radius: 12px; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5), 0 10px 10px -5px rgba(0, 0, 0, 0.2); text-align: center; max-width: 500px; border: 1px solid #334155; }
            h1 { color: #38bdf8; margin-top: 0; font-size: 1.8rem; }
            .status { display: inline-block; background-color: #10b981; color: white; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.875rem; font-weight: bold; margin: 1rem 0; letter-spacing: 0.05em; }
            p { color: #94a3b8; line-height: 1.6; }
            .footer { margin-top: 2rem; font-size: 0.75rem; color: #475569; }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>A2go Marketing Orchestration</h1>
            <div class="status">● SYSTEM ONLINE</div>
            <p>The webhook server and background scheduler are actively running.</p>
            <p>Waiting for GoHighLevel, Brevo, and MessageBird webhooks.</p>
            <div class="footer">Version 1.0.0 &bull; Python Flask Engine</div>
        </div>
    </body>
    </html>
    """
    return html, 200

# ─── Health check ──────────────────────────────────────────────────────────────
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


# ─── GHL inbound webhook ───────────────────────────────────────────────────────
@app.route("/webhooks/ghl", methods=["POST"])
def ghl_webhook():
    if not _check_secret(request):
        return jsonify({"error": "Unauthorized"}), 401
    payload = request.get_json(silent=True) or {}
    
    # Allow passing type via query string (e.g. ?type=appointment)
    event_type = request.args.get("type") or payload.get("type")
    if event_type:
        payload["type"] = event_type
        
    logger.info(f"GHL webhook received: type={payload.get('type')}")
    try:
        handle_ghl_webhook(payload)
        return jsonify({"status": "processed"}), 200
    except Exception as e:
        logger.error(f"GHL webhook error: {e}")
        return jsonify({"error": str(e)}), 500


# ─── Brevo inbound webhook ─────────────────────────────────────────────────────
@app.route("/webhooks/brevo", methods=["POST"])
def brevo_webhook():
    if not _check_secret(request):
        return jsonify({"error": "Unauthorized"}), 401
    payload = request.get_json(silent=True) or {}
    logger.info(f"Brevo webhook received: event={payload.get('event')}")
    try:
        handle_brevo_webhook(payload)
        return jsonify({"status": "processed"}), 200
    except Exception as e:
        logger.error(f"Brevo webhook error: {e}")
        return jsonify({"error": str(e)}), 500


# ─── MessageBird inbound webhook ───────────────────────────────────────────────
@app.route("/webhooks/messagebird", methods=["POST"])
def messagebird_webhook():
    if not _check_secret(request):
        return jsonify({"error": "Unauthorized"}), 401
    payload = request.get_json(silent=True) or {}
    logger.info(f"MessageBird webhook received: {payload}")
    try:
        handle_messagebird_webhook(payload)
        return jsonify({"status": "processed"}), 200
    except Exception as e:
        logger.error(f"MessageBird webhook error: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
