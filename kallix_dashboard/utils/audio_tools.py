import streamlit as st
import os

# =========================================================
# 🎧 Voice / Audio Tool
# =========================================================
def voice_audio_tool():
    st.write("🎧 Play or Download AI Call Audio")

    uploaded_audio = st.file_uploader("Upload Audio File", type=["mp3", "wav"])
    if uploaded_audio:
        st.audio(uploaded_audio, format="audio/mp3")
        st.download_button(
            label="📥 Download Audio",
            data=uploaded_audio,
            file_name=uploaded_audio.name
        )
    else:
        st.info("No audio uploaded yet. You can play ElevenLabs recordings here later.")

# =========================================================
# 🗒️ Transcription Tool
# =========================================================
def transcription_tool():
    st.write("🗒️ Transcription Viewer / Downloader")

    uploaded_txt = st.file_uploader("Upload Transcription File", type=["txt"])
    if uploaded_txt:
        st.success(f"Transcription file uploaded: {uploaded_txt.name}")
        transcript = uploaded_txt.read().decode("utf-8")
        st.text_area("Transcription Content", transcript, height=250)
        st.download_button(
            label="📥 Download Transcription",
            data=transcript,
            file_name=uploaded_txt.name
        )
    else:
        st.info("Upload or view transcription text files from AI calls here.")
