import os, requests
from dotenv import load_dotenv
load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

def fetch_sessions(agent_id):
    if not ELEVENLABS_API_KEY: raise RuntimeError("No ELEVENLABS_API_KEY set")
    url = f"https://api.elevenlabs.io/v1/agents/{agent_id}/sessions"
    r = requests.get(url, headers={"Authorization": f"Bearer {ELEVENLABS_API_KEY}"}, timeout=10)
    return r.json() if r.status_code == 200 else []

def get_session_details(agent_id, session_id):
    url = f"https://api.elevenlabs.io/v1/agents/{agent_id}/sessions/{session_id}"
    r = requests.get(url, headers={"Authorization": f"Bearer {ELEVENLABS_API_KEY}"}, timeout=10)
    return r.json() if r.status_code == 200 else None
