# =========================================================
# Kallix Real Estate Lead Capture (Ananya)
# =========================================================
# ✅ Uses FastAPI + Modal to capture leads from ElevenLabs calls
# ✅ Sends lead data to Google Sheets via webhook
# ✅ Logs everything for debugging
# =========================================================

import modal
from fastapi import FastAPI, Request
import requests
import os
from datetime import datetime
from loguru import logger
from dotenv import load_dotenv

# ---------------------------------------------------------
# Load environment variables
# ---------------------------------------------------------
load_dotenv()

# ---------------------------------------------------------
# Initialize Modal and FastAPI apps
# ---------------------------------------------------------
app = modal.App("kallix_real_estate_lead")
web_app = FastAPI(title="Kallix Real Estate Lead API")

# ---------------------------------------------------------
# Environment variables
# ---------------------------------------------------------
GOOGLE_SHEET_WEBHOOK = os.environ.get("GOOGLE_SHEET_WEBHOOK")

if not GOOGLE_SHEET_WEBHOOK:
    logger.warning("⚠️ GOOGLE_SHEET_WEBHOOK not set — leads won't be saved to Sheets!")

# ---------------------------------------------------------
# In-memory storage (for quick testing only)
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
                logger.warning(f"❌ Missing required field: {field}")
                return {"status": "error", "message": f"Missing field: {field}"}

        # Build lead entry
        lead = {
            "client_name": data.get("client_name"),
            "phone": data.get("phone"),
            "email": data.get("email", ""),
            "demo_time": data.get("demo_time", ""),
            "remarks": data.get("remarks", ""),
            "agent": data.get("agent_name", "Ananya"),
            "industry": "Real Estate",
            "timestamp": datetime.now().isoformat() + "Z"
        }

        # Store locally (temporary buffer)
        leads.append(lead)
        logger.info(f"🧾 Lead appended locally: {lead['client_name']}")

        # -------------------------------------------------
        # Send data to Google Sheet via Apps Script webhook
        # -------------------------------------------------
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
            logger.warning("⚠️ Skipped sending to Google Sheets (no webhook set).")

        return {"status": "success", "message": "Lead captured successfully!"}

    except Exception as e:
        logger.exception(f"🔥 Unexpected error in capture_lead: {e}")
        return {"status": "error", "message": "Internal Server Error"}


# ---------------------------------------------------------
# Modal Deployment Wrapper
# ---------------------------------------------------------
@app.function()
@modal.asgi_app()
def fastapi_app():
    """Deploy FastAPI app to Modal as a web endpoint."""
    return web_app