import os
from typing import List
import sys
from pathlib import Path

# Ensure parent directory is on path so `dashboard` package imports resolve
sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st

from dashboard.schemas import (
    ClientBusinessDetails,
    KnowledgeBaseEntry,
    CallRecord,
)
from dashboard.utils import generate_id, now_iso, validate_drive_link, extract_text_from_pdf
from dashboard.storage import (
    upsert_client,
    list_clients,
    add_kb_entry,
    list_kb_entries,
    add_call_record,
    list_call_records,
    list_tool_actions,
)
from dashboard.integrations import (
    fetch_elevenlabs_transcript_and_audio,
    book_google_calendar_event,
    create_calendly_invite,
    send_email_action,
    send_brochure_action,
    update_google_sheet,
    update_crm,
)


st.set_page_config(page_title="Kallix Agents Dashboard", layout="wide")

# Assets
ASSET_LOGO = Path(__file__).resolve().parent / "assets" / "Kallix_LOGO.png"


AGENTS = {
    "E-commerce Kallix": "ecommerce_kallix",
    "Chiropractor Kallix": "chiropractor_kallix",
    "Real Estate Kallix": "real_estate_kallix",
}


def ensure_session():
    if "agent_id" not in st.session_state:
        st.session_state.agent_id = list(AGENTS.values())[0]
    if "client_id_ctx" not in st.session_state:
        st.session_state.client_id_ctx = ""


def sidebar():
    if ASSET_LOGO.exists():
        st.sidebar.image(str(ASSET_LOGO), width=160)
    st.sidebar.title("Kallix Agents")
    agent_name = st.sidebar.selectbox("Select Agent", list(AGENTS.keys()))
    st.session_state.agent_id = AGENTS[agent_name]
    nav = st.sidebar.radio(
        "Navigate",
        ["Business Setup", "Knowledge Base", "Calls", "Integrations & Actions"],
    )
    st.sidebar.caption(
        f"Agent context: {st.session_state.agent_id}. Passed to downstream actions."
    )
    return nav


def page_business_setup():
    st.header("Client Business Setup")
    st.subheader("Create or Update Client")
    with st.form("client_form"):
        client_id = st.text_input("Client ID", value=st.session_state.client_id_ctx)
        business_name = st.text_input("Business Name")
        business_description = st.text_area("Business Description")
        industry = st.text_input("Industry")
        email = st.text_input("Email")
        phone = st.text_input("Phone")
        submitted = st.form_submit_button("Save Client Details")
    if submitted:
        try:
            payload = ClientBusinessDetails(
                client_id=client_id,
                business_name=business_name,
                business_description=business_description,
                industry=industry,
                contact_info={"email": email, "phone": phone},
            )
            saved = upsert_client(payload)
            st.session_state.client_id_ctx = client_id
            st.success("Client saved.")
            st.json(saved)
        except Exception as e:
            st.error(f"Validation failed: {e}")


def page_kb():
    st.header("Knowledge Base Management")
    if not st.session_state.client_id_ctx:
        st.warning("Set a Client ID in Business Setup to tie entries.")
    client_id = st.session_state.client_id_ctx

    with st.expander("Upload TXT"):
        txt_file = st.file_uploader("TXT File", type=["txt"], key="txt_upl")
        if txt_file and st.button("Save TXT Entry"):
            text = txt_file.getvalue().decode("utf-8", errors="ignore")
            entry = KnowledgeBaseEntry(
                kb_entry_id=generate_id("kb"),
                client_id=client_id,
                type="txt",
                value=text,
                created_at=now_iso(),
            )
            saved = add_kb_entry(entry)
            st.success("TXT entry saved")
            st.json(saved)

    with st.expander("Upload PDF"):
        pdf_file = st.file_uploader("PDF File", type=["pdf"], key="pdf_upl")
        if pdf_file and st.button("Save PDF Entry"):
            text = extract_text_from_pdf(pdf_file.getvalue())
            entry = KnowledgeBaseEntry(
                kb_entry_id=generate_id("kb"),
                client_id=client_id,
                type="pdf",
                value=text,
                created_at=now_iso(),
            )
            saved = add_kb_entry(entry)
            st.success("PDF entry saved")
            st.json(saved)

    with st.expander("Google Drive Link"):
        drive_link = st.text_input("Drive URL")
        if st.button("Save Drive Link"):
            if not validate_drive_link(drive_link):
                st.error("Invalid Google Drive/Docs link format.")
            else:
                entry = KnowledgeBaseEntry(
                    kb_entry_id=generate_id("kb"),
                    client_id=client_id,
                    type="drive_link",
                    value=drive_link,
                    created_at=now_iso(),
                )
                saved = add_kb_entry(entry)
                st.success("Drive link saved")
                st.json(saved)

    # Entries list removed per request


def page_calls():
    st.header("Call Tracking and Records")
    client_id = st.session_state.client_id_ctx
    agent_id = st.session_state.agent_id
    st.info("Purpose: Show calls tied to client/agent; inputs: client_id, filters")

    with st.expander("Simulate New Call Record"):
        callee = st.text_input("Callee")
        hist_id = st.text_input("ElevenLabs History Item ID")
        api_key = os.getenv("ELEVENLABS_API_KEY")
        if st.button("Create Call Record"):
            fetched = fetch_elevenlabs_transcript_and_audio(hist_id, api_key)
            transcript = fetched.get("transcript") or "Transcript unavailable"
            audio_url = fetched.get("audio_url") or ""
            error = fetched.get("error")
            status = "completed" if not error else "failed"
            record = CallRecord(
                call_id=generate_id("call"),
                client_id=client_id,
                timestamp=now_iso(),
                agent_id=agent_id,
                callee=callee,
                transcript=transcript,
                audio_url=audio_url,
                call_status=status,
                error_message=error,
            )
            saved = add_call_record(record)
            st.success("Call record saved")
            st.json(saved)

    st.subheader("Call List")
    f_client = st.text_input("Filter Client ID", value=client_id)
    f_status = st.selectbox("Status", [None, "completed", "failed"])
    page = st.number_input("Page", min_value=1, value=1, key="call_page")
    per_page = st.selectbox("Per Page", [5, 10, 20], index=1, key="call_pp")
    sort_by = st.selectbox("Sort By", ["timestamp", "callee"], key="call_sort_by")
    sort_order = st.selectbox("Order", ["asc", "desc"], index=1, key="call_sort_order")
    resp = list_call_records(
        client_id=f_client or None,
        agent_id=agent_id,
        call_status=f_status or None,
        page=page,
        per_page=int(per_page),
        sort_by=sort_by,
        sort_order=sort_order,
    )
    st.caption(
        f"Pagination: page={resp['page']}, per_page={resp['per_page']}, total_items={resp['total_items']}"
    )
    st.dataframe(resp["items"], use_container_width=True)

    sel = st.selectbox("Select Call for Detail", ["-"] + [it["call_id"] for it in resp["items"]])
    if sel != "-":
        call = next((it for it in resp["items"] if it["call_id"] == sel), None)
        if call:
            st.write("Transcript:")
            st.code(call["transcript"])
            if call.get("audio_url"):
                st.audio(call["audio_url"])
            if call.get("error_message"):
                st.error(call["error_message"])


def page_integrations():
    st.header("User Actions and Integrations")
    client_id = st.session_state.client_id_ctx
    agent_id = st.session_state.agent_id

    st.subheader("Appointment Booking")
    method = st.selectbox("Method", ["Google Calendar", "Calendly"])
    if method == "Google Calendar":
        st.caption("Purpose: Book calendar event; inputs: token, calendarId, event")
        token = os.getenv("GOOGLE_OAUTH_TOKEN")
        calendar_id = st.text_input("Calendar ID")
        title = st.text_input("Event Title")
        start = st.text_input("Start ISO")
        end = st.text_input("End ISO")
        if st.button("Book via Google Calendar"):
            payload = {
                "summary": title,
                "start": {"dateTime": start},
                "end": {"dateTime": end},
            }
            event = book_google_calendar_event(client_id, token, calendar_id, payload)
            from dashboard.storage import add_tool_action
            from dashboard.schemas import ToolActionEvent
            add_tool_action(ToolActionEvent(**event))
            st.json(event)
    else:
        st.caption("Purpose: Schedule via Calendly; inputs: scheduling link, invitee, token")
        token = os.getenv("CALENDLY_API_TOKEN")
        link = st.text_input("Scheduling Link")
        inv_name = st.text_input("Invitee Name")
        inv_email = st.text_input("Invitee Email")
        if st.button("Book via Calendly"):
            event = create_calendly_invite(client_id, link, {"name": inv_name, "email": inv_email}, token)
            from dashboard.storage import add_tool_action
            from dashboard.schemas import ToolActionEvent
            add_tool_action(ToolActionEvent(**event))
            st.json(event)

    st.subheader("Send Email")
    st.caption("Purpose: Send email; inputs: SMTP creds, to, subject, content")
    to_email = st.text_input("To Email")
    subject = st.text_input("Subject")
    content = st.text_area("Content")
    if st.button("Send Email"):
        event = send_email_action(client_id, to_email, subject, content)
        from dashboard.storage import add_tool_action
        from dashboard.schemas import ToolActionEvent
        add_tool_action(ToolActionEvent(**event))
        st.json(event)

    st.subheader("Send Brochure")
    st.caption("Purpose: Send brochure; inputs: file content")
    broch = st.file_uploader("Upload Brochure (PDF)", type=["pdf"], key="brochure")
    if broch and st.button("Send Brochure"):
        event = send_brochure_action(client_id, broch.name, len(broch.getvalue()))
        from dashboard.storage import add_tool_action
        from dashboard.schemas import ToolActionEvent
        add_tool_action(ToolActionEvent(**event))
        st.json(event)

    st.subheader("Google Sheets Update")
    st.caption("Purpose: Update sheet; inputs: service account JSON, sheet_id, range, values")
    sheet_id = st.text_input("Sheet ID")
    range_a1 = st.text_input("Range (A1)")
    values_raw = st.text_area("Values (comma-separated rows)")
    if st.button("Update Sheet"):
        values = [[c.strip() for c in row.split(",")] for row in values_raw.splitlines() if row.strip()]
        event = update_google_sheet(client_id, sheet_id, range_a1, values)
        from dashboard.storage import add_tool_action
        from dashboard.schemas import ToolActionEvent
        add_tool_action(ToolActionEvent(**event))
        st.json(event)

    st.subheader("CRM Update")
    st.caption("Purpose: Update CRM; inputs: CRM type, token env, payload")
    crm = st.selectbox("CRM", ["zoho", "hubspot"]) 
    payload_txt = st.text_area("Payload JSON")
    if st.button("Update CRM"):
        import json
        try:
            payload = json.loads(payload_txt or "{}")
        except Exception as e:
            st.error(f"Invalid JSON: {e}")
            payload = {}
        event = update_crm(client_id, crm, payload)
        from dashboard.storage import add_tool_action
        from dashboard.schemas import ToolActionEvent
        add_tool_action(ToolActionEvent(**event))
        st.json(event)

    st.subheader("Action Logs")
    page = st.number_input("Page", min_value=1, value=1, key="act_page")
    per_page = st.selectbox("Per Page", [5, 10, 20], index=1, key="act_pp")
    sort_by = st.selectbox("Sort By", ["timestamp", "action_type", "status"], key="act_sort_by")
    sort_order = st.selectbox("Order", ["asc", "desc"], index=1, key="act_sort_order")
    resp = list_tool_actions(
        client_id=client_id or None,
        page=page,
        per_page=int(per_page),
        sort_by=sort_by,
        sort_order=sort_order,
    )
    st.caption(
        f"Pagination: page={resp['page']}, per_page={resp['per_page']}, total_items={resp['total_items']}"
    )
    st.dataframe(resp["items"], use_container_width=True)


def main():
    ensure_session()
    nav = sidebar()
    if nav == "Business Setup":
        page_business_setup()
    elif nav == "Knowledge Base":
        page_kb()
    elif nav == "Calls":
        page_calls()
    elif nav == "Integrations & Actions":
        page_integrations()


if __name__ == "__main__":
    main()
