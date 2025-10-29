# =========================================================
# 🧠 Kallix Real Estate Lead & Audio Capture API
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

app = modal.App("kallix_real_estate_lead")
web_app = FastAPI(title="Kallix Real Estate Lead API")

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

        GOOGLE_SHEET_WEBHOOK = os.environ.get("GOOGLE_SHEET_WEBHOOK")

        if GOOGLE_SHEET_WEBHOOK:
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
        else:
            logger.warning("⚠️ GOOGLE_SHEET_WEBHOOK not set — skipped sending to Sheets.")

        return {"status": "success", "message": "Lead captured successfully!"}

    except Exception as e:
        logger.exception(f"🔥 Unexpected error in capture_lead: {e}")
        return {"status": "error", "message": "Internal Server Error"}

# =========================================================
# 🎧 2. Capture Audio + Transcription from ElevenLabs
# =========================================================
@web_app.post("/capture-audio")
async def capture_audio(request: Request):
    """Capture audio + transcription from ElevenLabs call."""
    try:
        data = await request.json()
        logger.info(f"🎧 Incoming audio data: {data}")

        call_id = data.get("call_id", f"call_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        client_name = data.get("client_name", "Unknown")
        phone = data.get("phone", "")
        audio_url = data.get("audio_url")
        transcript_text = data.get("transcript_text", "")

        # -------------------------------------------------
        # Save transcription text locally
        # -------------------------------------------------
        txt_path = f"/tmp/{call_id}.txt"
        with open(txt_path, "w") as f:
            f.write(transcript_text or "")
        logger.info(f"📝 Transcription saved: {txt_path}")

        # -------------------------------------------------
        # Download audio file from ElevenLabs (if provided)
        # -------------------------------------------------
        audio_path = None
        if audio_url:
            try:
                audio_resp = requests.get(audio_url, timeout=10)
                if audio_resp.status_code == 200:
                    audio_path = f"/tmp/{call_id}.mp3"
                    with open(audio_path, "wb") as f:
                        f.write(audio_resp.content)
                    logger.info(f"🎵 Audio file saved: {audio_path}")
                else:
                    logger.warning(f"⚠️ Could not download audio: {audio_resp.status_code}")
            except Exception as e:
                logger.error(f"❌ Error downloading audio: {e}")

        # -------------------------------------------------
        # Send metadata to Google Sheet
        # -------------------------------------------------
        GOOGLE_SHEET_WEBHOOK = os.environ.get("GOOGLE_SHEET_WEBHOOK")

        if GOOGLE_SHEET_WEBHOOK:
            entry = {
                "call_id": call_id,
                "client_name": client_name,
                "phone": phone,
                "audio_url": audio_url or "",
                "timestamp": datetime.now().isoformat(),
            }
            try:
                resp = requests.post(GOOGLE_SHEET_WEBHOOK, json=entry, timeout=5)
                if resp.status_code == 200:
                    logger.success("✅ Audio metadata sent to Google Sheet.")
                else:
                    logger.warning(f"⚠️ Sheet responded with {resp.status_code}: {resp.text}")
            except Exception as e:
                logger.error(f"❌ Error sending metadata to Google Sheet: {e}")
        else:
            logger.warning("⚠️ GOOGLE_SHEET_WEBHOOK not set — skipping Google Sheet sync.")

        logger.success("✅ Audio + transcription captured successfully.")
        return {"status": "success", "message": "Audio + transcription stored."}

    except Exception as e:
        logger.exception(f"🔥 Error in capture_audio: {e}")
        return {"status": "error", "message": str(e)}

# =========================================================
# 🚀 3. Modal Deployment Wrapper
# =========================================================
@app.function(image=image, secrets=[modal.Secret.from_name("kallix-secrets")])
@modal.asgi_app()
def fastapi_app():
    return web_app
