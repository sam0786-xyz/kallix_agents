import streamlit as st
from utils.elevenlabs_tools import fetch_sessions, get_session_details

def voice_audio_tool():
    st.write("🎧 **AI Voice Recordings (Synced from ElevenLabs)**")

    agent_map = {
        "Ananya (Real Estate)": "agent_id_real_estate",
        "Aisha (Chiropractor)": "agent_id_chiro",
        "Mira (E-Commerce)": "agent_id_ecom"
    }

    selected_agent = st.selectbox("Select Agent", list(agent_map.keys()))
    agent_id = agent_map[selected_agent]

    sessions = fetch_sessions(agent_id)
    if not sessions:
        st.info("No call sessions found for this agent.")
        return

    session_ids = [s["session_id"] for s in sessions]
    selected_session = st.selectbox("Select Call Session", session_ids)

    if selected_session:
        details = get_session_details(agent_id, selected_session)
        if not details:
            st.warning("No details available.")
            return

        st.markdown(f"**Client:** {details.get('client_name', 'Unknown')}")
        st.markdown(f"**Call Duration:** {details.get('duration', 'N/A')} seconds")

        audio_url = details.get("audio_url")
        transcript = details.get("transcript")

        if audio_url:
            st.audio(audio_url, format="audio/mp3")

        if transcript:
            with st.expander("🗒️ View Transcription"):
                st.text_area("Transcription", transcript, height=250)
                st.download_button("📥 Download Transcription", transcript, file_name=f"{selected_session}.txt")
