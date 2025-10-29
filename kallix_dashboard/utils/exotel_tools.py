import streamlit as st, requests, json, os

def _cfg():
    return json.load(open("client_config.json")) if os.path.exists("client_config.json") else {}

def phone_tool(agent_name=None, account_sid=None, trial_number=None, flow_id=None):
    c = _cfg()
    sid = account_sid or c.get("exotel_sid")
    num = trial_number or c.get("exotel_trial_number")
    flow = flow_id or c.get("exotel_flow_id")
    key, token = c.get("exotel_api_key"), c.get("exotel_api_token")

    st.write(f"Account: `{sid}`  |  Trial No: `{num}`  |  Flow ID: `{flow}`")
    phone = st.text_input("Client Phone Number")
    if st.button("Start Call"):
        if not phone: return st.warning("Enter number first.")
        if not key or not token:
            return st.success(f"Simulated call to {phone} from {num}")
        url = f"https://api.exotel.com/v1/Accounts/{sid}/Calls/connect.json"
        payload = {"From": num, "To": phone, "CallerId": num, "Url": ""}
        r = requests.post(url, data=payload, auth=(key, token))
        st.write(r.text if r.ok else f"Error: {r.status_code}")
