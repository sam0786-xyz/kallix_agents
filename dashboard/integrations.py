from __future__ import annotations
import os
from typing import Dict, Optional
import requests

from .schemas import ToolActionEvent
from .utils import generate_id, now_iso


def _event(client_id: str, action_type: str, ok: bool, error: Optional[str]) -> Dict:
    return ToolActionEvent(
        action_id=generate_id("act"),
        client_id=client_id,
        action_type=action_type,  # type: ignore
        status="success" if ok else "failed",
        error_message=error,
        timestamp=now_iso(),
    ).model_dump()


def fetch_elevenlabs_transcript_and_audio(history_item_id: str, api_key: Optional[str]) -> Dict[str, Optional[str]]:
    # Purpose: Fetch transcript and audio URL from Eleven Labs; inputs: history_item_id, api_key
    if not api_key:
        return {"transcript": None, "audio_url": None, "error": "Missing ELEVENLABS_API_KEY"}
    try:
        headers = {"xi-api-key": api_key}
        # Note: Endpoint paths may change; this is a placeholder.
        # History details
        hist = requests.get(
            f"https://api.elevenlabs.io/v1/history/{history_item_id}", headers=headers, timeout=15
        )
        hist.raise_for_status()
        data = hist.json()
        transcript = data.get("text") or data.get("transcript")
        audio_url = data.get("audio_url")  # Some responses provide a URL or require a second call
        return {"transcript": transcript, "audio_url": audio_url, "error": None}
    except Exception as e:
        return {"transcript": None, "audio_url": None, "error": str(e)}


def book_google_calendar_event(client_id: str, token: Optional[str], calendar_id: str, event_payload: Dict) -> Dict:
    # Purpose: Create event in Google Calendar; inputs: oauth token, calendar_id, event payload
    if not token:
        return _event(client_id, "calendar_booking", False, "Missing GOOGLE_OAUTH_TOKEN")
    try:
        resp = requests.post(
            f"https://www.googleapis.com/calendar/v3/calendars/{calendar_id}/events",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json=event_payload,
            timeout=20,
        )
        ok = resp.status_code in (200, 201)
        err = None if ok else f"HTTP {resp.status_code}: {resp.text[:200]}"
        return _event(client_id, "calendar_booking", ok, err)
    except Exception as e:
        return _event(client_id, "calendar_booking", False, str(e))


def create_calendly_invite(client_id: str, scheduling_link: str, invitee: Dict[str, str], token: Optional[str]) -> Dict:
    # Purpose: Schedule via Calendly; inputs: scheduling link, invitee(name,email), token
    if not token:
        return _event(client_id, "calendar_booking", False, "Missing CALENDLY_API_TOKEN")
    try:
        resp = requests.post(
            "https://api.calendly.com/scheduled_events",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json={"scheduling_link": scheduling_link, "invitee": invitee},
            timeout=20,
        )
        ok = resp.status_code in (200, 201)
        err = None if ok else f"HTTP {resp.status_code}: {resp.text[:200]}"
        return _event(client_id, "calendar_booking", ok, err)
    except Exception as e:
        return _event(client_id, "calendar_booking", False, str(e))


def send_email_action(client_id: str, to_email: str, subject: str, content: str) -> Dict:
    # Purpose: Send an email; inputs: SMTP creds (env), to, subject, content
    # Demo stub: Only logs the action; implement SMTP if creds provided.
    smtp_host = os.getenv("SMTP_HOST")
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    if not (smtp_host and smtp_user and smtp_pass):
        return _event(client_id, "email", False, "Missing SMTP credentials")
    try:
        # Minimal example using requests to a hypothetical email API or implement smtplib.
        return _event(client_id, "email", True, None)
    except Exception as e:
        return _event(client_id, "email", False, str(e))


def send_brochure_action(client_id: str, filename: str, bytes_len: int) -> Dict:
    # Purpose: Send brochure to prospect; inputs: file name and bytes length
    # Demo: assume success if bytes_len > 0
    ok = bytes_len > 0
    err = None if ok else "Empty file"
    return _event(client_id, "brochure", ok, err)


def update_google_sheet(client_id: str, sheet_id: str, range_a1: str, values: list) -> Dict:
    # Purpose: Update Google Sheet; inputs: service account JSON env, sheet_id, range, values
    try:
        sa_path = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
        if not sa_path or not os.path.exists(sa_path):
            return _event(client_id, "sheet_update", False, "Missing GOOGLE_SERVICE_ACCOUNT_JSON")
        import gspread  # type: ignore
        from google.oauth2.service_account import Credentials  # type: ignore

        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = Credentials.from_service_account_file(sa_path, scopes=scopes)
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(sheet_id)
        ws = sh.sheet1
        ws.update(range_a1, values)
        return _event(client_id, "sheet_update", True, None)
    except Exception as e:
        return _event(client_id, "sheet_update", False, str(e))


def update_crm(client_id: str, crm: str, payload: Dict) -> Dict:
    # Purpose: Update CRM (Zoho/HubSpot); inputs: crm type, auth token env, payload
    try:
        if crm == "zoho":
            token = os.getenv("ZOHO_OAUTH_TOKEN")
            if not token:
                return _event(client_id, "crm_update", False, "Missing ZOHO_OAUTH_TOKEN")
            resp = requests.post(
                "https://www.zohoapis.com/crm/v2/Leads",
                headers={"Authorization": f"Zoho-oauthtoken {token}"},
                json=payload,
                timeout=20,
            )
        elif crm == "hubspot":
            token = os.getenv("HUBSPOT_PRIVATE_APP_TOKEN")
            if not token:
                return _event(client_id, "crm_update", False, "Missing HUBSPOT_PRIVATE_APP_TOKEN")
            resp = requests.post(
                "https://api.hubapi.com/crm/v3/objects/contacts",
                headers={"Authorization": f"Bearer {token}"},
                json=payload,
                timeout=20,
            )
        else:
            return _event(client_id, "crm_update", False, f"Unsupported CRM: {crm}")
        ok = resp.status_code in (200, 201)
        err = None if ok else f"HTTP {resp.status_code}: {resp.text[:200]}"
        return _event(client_id, "crm_update", ok, err)
    except Exception as e:
        return _event(client_id, "crm_update", False, str(e))

