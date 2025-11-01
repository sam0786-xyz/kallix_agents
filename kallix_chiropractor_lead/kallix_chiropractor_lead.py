import modal
from fastapi import FastAPI, Request
import requests, os
from datetime import datetime
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

image = (
    modal.Image.debian_slim()
    .pip_install("fastapi", "requests", "loguru", "python-dotenv", "uvicorn")
)

app = modal.App("kallix_chiropractor_lead")
web_app = FastAPI(title="Kallix Chiropractor Lead API")

@web_app.post("/capture-lead")
async def capture_lead(request: Request):
    try:
        data = await request.json()
        logger.info(f"📩 Incoming Chiropractor Lead: {data}")

        lead = {
            "client_name": data.get("client_name"),
            "phone": data.get("phone"),
            "email": data.get("email", ""),
            "demo_time": data.get("demo_time", ""),
            "remarks": data.get("remarks", ""),
            "agent": data.get("agent_name", "Riya"),
            "timestamp": datetime.now().isoformat() + "Z"
        }

        GOOGLE_SHEET_WEBHOOK_CHIROPRACTOR = os.environ.get("GOOGLE_SHEET_WEBHOOK_CHIROPRACTOR")
        logger.info(f"🧩 Using Google Sheet Webhook: {GOOGLE_SHEET_WEBHOOK_CHIROPRACTOR}")

        resp = requests.post(GOOGLE_SHEET_WEBHOOK_CHIROPRACTOR, json=lead, timeout=5)
        logger.info(f"🔁 Google Sheet Response: {resp.status_code} - {resp.text}")

        return {"status": "success", "message": "Chiropractor lead captured!"}

    except Exception as e:
        logger.exception(f"🔥 Error capturing Chiropractor lead: {e}")
        return {"status": "error", "message": str(e)}

@app.function(image=image, secrets=[modal.Secret.from_name("kallix-secrets")])
@modal.asgi_app()
def fastapi_app():
    return web_app
