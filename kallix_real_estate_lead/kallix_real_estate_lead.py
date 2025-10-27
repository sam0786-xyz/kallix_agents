# =========================================================
# Kallix Real Estate Lead Capture (Ananya)
# =========================================================

import modal
from fastapi import FastAPI, Request
import requests
import os
from datetime import datetime
from loguru import logger
from dotenv import load_dotenv

# ---------------------------------------------------------
# Load local .env (for local testing only)
# ---------------------------------------------------------
load_dotenv()

# ---------------------------------------------------------
# Modal image (includes dependencies)
# ---------------------------------------------------------
image = (
    modal.Image.debian_slim()
    .pip_install("fastapi", "requests", "loguru", "python-dotenv", "uvicorn")
)

# ---------------------------------------------------------
# Initialize Modal and FastAPI
# ---------------------------------------------------------
app = modal.App("kallix_real_estate_lead")
web_app = FastAPI(title="Kallix Real Estate Lead API")

# ---------------------------------------------------------
# In-memory storage (for local debugging only)
# ---------------------------------------------------------
leads = []

# ---------------------------------------------------------
# Main endpoint: /capture-lead
# ---------------------------------------------------------
@web_app.post("/capture-lead")
async def capture_lead(request: Request):
    """Capture lead details sent from ElevenLabs agent webhook."""
    try:
        data = await request.json()
        logger.info(f"📩 Incoming lead data: {data}")

        # Basic validation
        required_fields = ["client_name", "phone"]
        for field in required_fields:
            if field not in data or not data[field]:
                return {"status": "error", "message": f"Missing field: {field}"}

        # Build lead entry
        lead = {
            "client_name": data.get("client_name"),
            "phone": data.get("phone"),
            "email": data.get("email", ""),
            "demo_time": data.get("demo_time", ""),
            "remarks": data.get("remarks", ""),
            "agent": data.get("agent_name", "Ananya"),
            "timestamp": datetime.now().isoformat() + "Z"
        }

        leads.append(lead)
        logger.info(f"🧾 Lead appended locally: {lead['client_name']}")

        # Get webhook from environment (Modal injects secrets as env vars)
        GOOGLE_SHEET_WEBHOOK = os.environ.get("GOOGLE_SHEET_WEBHOOK")

        if GOOGLE_SHEET_WEBHOOK:
            try:
                resp = requests.post(
                    GOOGLE_SHEET_WEBHOOK,
                    json=lead,
                    timeout=5,
                    headers={"Content-Type": "application/json"},
                )
                if resp.status_code == 200:
                    logger.success("✅ Lead successfully sent to Google Sheet.")
                else:
                    logger.warning(
                        f"⚠️ Google Sheet responded with {resp.status_code}: {resp.text}"
                    )
            except Exception as e:
                logger.error(f"❌ Error sending to Google Sheet: {e}")
        else:
            logger.warning("⚠️ GOOGLE_SHEET_WEBHOOK not set — skipped sending to Sheets.")

        return {"status": "success", "message": "Lead captured successfully!"}

    except Exception as e:
        logger.exception(f"🔥 Unexpected error in capture_lead: {e}")
        return {"status": "error", "message": "Internal Server Error"}

# ---------------------------------------------------------
# Modal Deployment Wrapper
# ---------------------------------------------------------
@app.function(image=image, secrets=[modal.Secret.from_name("kallix-secrets")])
@modal.asgi_app()
def fastapi_app():
    return web_app
