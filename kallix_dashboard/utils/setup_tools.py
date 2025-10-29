import streamlit as st, json, os
CONFIG_FILE = "client_config.json"

def load_config():
    return json.load(open(CONFIG_FILE)) if os.path.exists(CONFIG_FILE) else {}

def save_config(c): json.dump(c, open(CONFIG_FILE, "w"), indent=2); st.success("✅ Saved configuration")

def setup_client():
    st.write("Setup your business and call details below:")
    c = load_config()
    with st.form("setup"):
        c["business_name"] = st.text_input("🏢 Business Name", c.get("business_name", ""))
        c["google_sheet_webhook"] = st.text_input("📄 Google Sheet Webhook URL", c.get("google_sheet_webhook", ""))
        c["exotel_sid"] = st.text_input("🔐 Exotel Account SID", c.get("exotel_sid", "theaizoned1"))
        c["exotel_trial_number"] = st.text_input("📞 Exotel Trial Number", c.get("exotel_trial_number", "09513886363"))
        c["exotel_flow_id"] = st.text_input("📲 Exotel Flow ID", c.get("exotel_flow_id", "1014318"))
        c["exotel_api_key"] = st.text_input("🔑 Exotel API Key", c.get("exotel_api_key", ""), type="password")
        c["exotel_api_token"] = st.text_input("🔐 Exotel API Token", c.get("exotel_api_token", ""), type="password")
        c["selected_agent"] = st.selectbox("🤖 Choose AI Agent", ["Ananya (Real Estate)", "Aisha (Chiropractor)", "Mira (E-Commerce)"], index=0)
        if st.form_submit_button("💾 Save"):
            save_config(c)
    return c
