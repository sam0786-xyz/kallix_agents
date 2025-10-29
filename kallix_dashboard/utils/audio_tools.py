import streamlit as st, requests
from utils.elevenlabs_tools import fetch_sessions, get_session_details

def voice_audio_tool():
    agent_map = {
        "Ananya (Real Estate)": "agent_id_real_estate",
        "Aisha (Chiropractor)": "agent_id_chiro",
        "Mira (E-Commerce)": "agent_id_ecom"
    }

    agent = st.selectbox("Select Agent", list(agent_map.keys()))
    sessions = fetch_sessions(agent_map[agent])
    if not sessions: return st.info("No recordings yet.")

    sids = [s["session_id"] for s in sessions]
    sid = st.selectbox("Select Call Session", sids)
    d = get_session_details(agent_map[agent], sid)
    if not d: return st.warning("No details.")
    audio = d.get("audio_url") or d.get("recording_url")
    if audio:
        st.audio(audio)
        try:
            res = requests.get(audio, timeout=10)
            if res.ok:
                st.download_button("📥 Download Audio", res.content, file_name=f"{sid}.mp3", mime="audio/mp3")
        except: pass
