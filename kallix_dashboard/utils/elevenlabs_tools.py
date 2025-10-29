import requests
import streamlit as st
import os

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

def fetch_sessions(agent_id: str):
    """Fetch all call sessions for a specific ElevenLabs agent."""
    url = f"https://api.elevenlabs.io/v1/agents/{agent_id}/sessions"
    headers = {"Authorization": f"Bearer {ELEVENLABS_API_KEY}"}
    resp = requests.get(url, headers=headers)
    if not resp.ok:
        st.error(f"Failed to fetch sessions: {resp.text}")
        return []
    return resp.json()

def get_session_details(agent_id: str, session_id: str):
    """Fetch details (audio + transcript) for a specific session."""
    url = f"https://api.elevenlabs.io/v1/agents/{agent_id}/sessions/{session_id}"
    headers = {"Authorization": f"Bearer {ELEVENLABS_API_KEY}"}
    resp = requests.get(url, headers=headers)
    if not resp.ok:
        st.error(f"Error fetching session: {resp.text}")
        return None
    return resp.json()
