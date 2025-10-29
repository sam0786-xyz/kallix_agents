# =========================================================
# 🧠 Kallix AI Dashboard
# Central control for agents, tools, voice, and CRM workflow
# =========================================================

import os
import streamlit as st
from utils.google_tools import google_sheet_tool
from utils.email_tools import email_tool
from utils.audio_tools import voice_audio_tool, transcription_tool
from utils.exotel_tools import phone_tool
from utils.llm_agent_tools import agent_selector, knowledge_base_tool
from utils.audio_tools import voice_audio_tool


# =========================================================
# 🔧 PAGE CONFIGURATION  — must be first Streamlit command
# =========================================================
st.set_page_config(
    page_title="Kallix Dashboard",
    page_icon="🤖",
    layout="wide",
)

# =========================================================
# 🎨 HEADER SECTION WITH LOGO
# =========================================================
col1, col2 = st.columns([1, 4])
with col1:
    if os.path.exists("assets/logo.png"):
        st.image("assets/logo.png")
    else:
        st.warning("⚠️ Logo not found — please add one to assets/logo.png")

with col2:
    st.markdown("### **Kallix.AI Dashboard**")
    st.caption("Central control for AI agents, tools, and client communications.")

st.markdown("---")

# =========================================================
# 🧠 AGENT SELECTION
# =========================================================
st.header("🧠 Agent Selection")
selected_agent = agent_selector()

# =========================================================
# 📚 KNOWLEDGE BASE
# =========================================================
st.header("📚 Knowledge Base")
knowledge_base_tool(selected_agent)

st.markdown("---")

# =========================================================
# 🧰 TOOLS SECTION
# =========================================================
st.header("🧰 Tools & Integrations")

tool_tabs = st.tabs([
    "📑 Google Sheet", 
    "📧 Email", 
    "📁 Drive", 
    "📜 Brochure",
    "🔊 Audio", 
    "🗒️ Transcription", 
    "📞 Phone"
])

# ---------------- Google Sheet ----------------
with tool_tabs[0]:
    google_sheet_tool()

# ---------------- Email ----------------
with tool_tabs[1]:
    email_tool(selected_agent)

# ---------------- Drive ----------------
with tool_tabs[2]:
    st.info("📁 Upload or link Drive PDF documents here.")
    uploaded_drive = st.file_uploader("Upload PDF", type=["pdf"])
    if uploaded_drive:
        st.success(f"✅ Uploaded: {uploaded_drive.name}")

# ---------------- Brochure ----------------
with tool_tabs[3]:
    st.info("📄 Upload Brochure File")
    uploaded_brochure = st.file_uploader("Upload Brochure", type=["pdf"])
    if uploaded_brochure:
        st.download_button("📥 Download Brochure", uploaded_brochure, file_name=uploaded_brochure.name)

# ---------------- Voice Audio ----------------
with tool_tabs[4]:
    voice_audio_tool()

# ---------------- Transcription ----------------
with tool_tabs[5]:
    transcription_tool()

# ---------------- Phone (Exotel) ----------------
with tool_tabs[6]:
    phone_tool(selected_agent)

st.markdown("---")
st.caption("💡 Built with ❤️ using Streamlit | Kallix.ai Internal Tool")
