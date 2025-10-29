import os
import streamlit as st
from utils.setup_tools import setup_client
from utils.llm_agent_tools import agent_selector, knowledge_base_tool
from utils.google_tools import google_sheet_tool
from utils.email_tools import email_tool
from utils.audio_tools import voice_audio_tool
from utils.transcription_tools import transcription_tool
from utils.exotel_tools import phone_tool

st.set_page_config(page_title="Kallix Dashboard", page_icon="🤖", layout="wide")

col1, col2 = st.columns([1, 4])
with col1:
    if os.path.exists("kallix_dashboard/assets/logo.png"):
        st.image("kallix_dashboard/assets/logo.png", width=100)
with col2:
    st.markdown("### Kallix.AI Dashboard")
    st.caption("Control your AI agents, calls, and business tools — all in one place.")

st.markdown("---")

st.header("🧩 Client Setup")
client_config = setup_client()
st.markdown("---")

st.header("🧠 Agent Selection")
selected_agent = agent_selector()
st.markdown("---")

st.header("📚 Knowledge Base")
knowledge_base_tool(selected_agent)
st.markdown("---")

st.header("🧰 Tools")
tabs = st.tabs(["📑 Google Sheet", "📧 Email", "📁 Drive", "📜 Brochure"])

with tabs[0]: google_sheet_tool()
with tabs[1]: email_tool(selected_agent)
with tabs[2]:
    st.info("Upload Drive PDF here.")
    pdf = st.file_uploader("Upload PDF", type=["pdf"])
    if pdf: st.success(f"Uploaded: {pdf.name}")
with tabs[3]:
    st.info("Upload Brochure PDF.")
    brochure = st.file_uploader("Upload Brochure", type=["pdf"])
    if brochure:
        st.download_button("📥 Download Brochure", brochure, file_name=brochure.name)

st.markdown("---")
st.header("🎧 Voice Recordings")
voice_audio_tool()
st.markdown("---")

st.header("🗒️ Transcriptions")
transcription_tool()
st.markdown("---")

st.header("📞 Exotel Phone Integration")
phone_tool(
    agent_name=client_config.get("selected_agent"),
    account_sid=client_config.get("exotel_sid"),
    trial_number=client_config.get("exotel_trial_number"),
    flow_id=client_config.get("exotel_flow_id"),
)
st.caption("Built with ❤️ by Kallix.ai")
