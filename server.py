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
