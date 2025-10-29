import streamlit as st
from utils.elevenlabs_tools import fetch_sessions, get_session_details

def transcription_tool():
    agent_map = {
        "Ananya (Real Estate)": "agent_id_real_estate",
        "Aisha (Chiropractor)": "agent_id_chiro",
        "Mira (E-Commerce)": "agent_id_ecom"
    }

    agent = st.selectbox("Select Agent for Transcripts", list(agent_map.keys()))
    sessions = fetch_sessions(agent_map[agent])
    if not sessions: return st.info("No transcripts found.")
    sids = [s["session_id"] for s in sessions]
    sid = st.selectbox("Select Session", sids)
    d = get_session_details(agent_map[agent], sid)
    if not d: return st.warning("No details.")
    txt = d.get("transcript") or d.get("transcription") or ""
    if not txt: return st.info("Transcription unavailable.")
    st.text_area("Transcription", txt, height=300)
    st.download_button("📥 Download", txt, file_name=f"{sid}.txt")
