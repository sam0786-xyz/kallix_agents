# =========================================================
# 🧠 Kallix Chiropractor Lead & Audio Capture API
# =========================================================
# ✅ Handles lead capture from ElevenLabs agents
# ✅ Handles audio + transcription upload for dashboard
# ✅ Sends both to Google Sheets for reference
# =========================================================

import modal
from fastapi import FastAPI, Request
import requests
import os
from datetime import datetime
from loguru import logger
from dotenv import load_dotenv

# ---------------------------------------------------------
# 🔧 Load environment (for local testing)
# ---------------------------------------------------------
load_dotenv()

# ---------------------------------------------------------
# 🧰 Modal Image & App Config
# ---------------------------------------------------------
image = (
    modal.Image.debian_slim()
    .pip_install("fastapi", "requests", "loguru", "python-dotenv", "uvicorn")
)

app = modal.App("kallix_chiropactor_lead")
web_app = FastAPI(title="Kallix Chiropractor Lead API")

# ---------------------------------------------------------
# 📦 Temporary In-memory storage (for testing only)
# ---------------------------------------------------------
leads = []

# =========================================================
# 📞 1. Capture Lead from ElevenLabs Agent
# =========================================================
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

        # Get Chiropractor Webhook
        GOOGLE_SHEET_WEBHOOK_CHIROPACTOR = os.environ.get("GOOGLE_SHEET_WEBHOOK_CHIROPACTOR")

        if GOOGLE_SHEET_WEBHOOK_CHIROPACTOR:
            resp = requests.post(
                GOOGLE_SHEET_WEBHOOK_CHIROPACTOR,
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
        else:
            logger.warning("⚠️ GOOGLE_SHEET_WEBHOOK_CHIROPACTOR not set — skipped sending to Sheets.")

        return {"status": "success", "message": "Lead captured successfully!"}

    except Exception as e:
        logger.exception(f"🔥 Unexpected error in capture_lead: {e}")
        return {"status": "error", "message": "Internal Server Error"}


# =========================================================
# 🚀 3. Modal Deployment Wrapper
# =========================================================
@app.function(image=image, secrets=[modal.Secret.from_name("kallix-secrets")])
@modal.asgi_app()
def fastapi_app():
    return web_app
