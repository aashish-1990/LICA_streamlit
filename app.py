import streamlit as st
from audiorecorder import audiorecorder
import base64
import requests
import io
from pydub import AudioSegment
from dotenv import load_dotenv
import os

# Load API key
load_dotenv()
API_KEY = os.getenv("SARVAM_API_KEY")

st.set_page_config(page_title="LICA Teacher Assist", layout="centered")
st.title("🎙️ LICA Teacher Assist")

role = st.radio("Select your role:", ("Teacher (Hindi)", "Student (Punjabi)"))

if "Teacher" in role:
    source_lang, target_lang, speaker = "hi-IN", "pa-IN", "anushka"
else:
    source_lang, target_lang, speaker = "pa-IN", "hi-IN", "karun"

st.markdown("Press the button and speak.")

# Record audio
audio = audiorecorder("🔴 Start Recording", "⏹️ Stop Recording")

if len(audio) > 0:
    st.success("Audio recorded!")

    # Convert to MP3
    wav_io = io.BytesIO(audio.tobytes())
    audio_seg = AudioSegment.from_file(wav_io, format="wav")
    mp3_io = io.BytesIO()
    audio_seg.export(mp3_io, format="mp3")
    mp3_io.seek(0)

    # Step 1: STT
    st.info("Transcribing...")
    stt = requests.post(
        "https://api.sarvam.ai/speech-to-text",
        headers={"API-Subscription-Key": API_KEY},
        files={"file": ("audio.mp3", mp3_io, "audio/mp3")},
        data={"model": "saarika:v2", "language_code": "unknown"}
    ).json()

    transcript = stt.get("transcript", "")
    st.markdown(f"**Original:** {transcript}")

    # Step 2: Translate
    st.info("Translating...")
    translation = requests.post(
        "https://api.sarvam.ai/translate",
        headers={"API-Subscription-Key": API_KEY, "Content-Type": "application/json"},
        json={
            "input": transcript,
            "source_language_code": source_lang,
            "target_language_code": target_lang,
            "mode": "formal"
        }
    ).json().get("translated_text", "")

    st.markdown(f"**Translated:** {translation}")

    # Step 3: TTS
    st.info("Generating speech...")
    tts = requests.post(
        "https://api.sarvam.ai/text-to-speech",
        headers={"API-Subscription-Key": API_KEY, "Content-Type": "application/json"},
        json={
            "text": translation,
            "target_language_code": target_lang,
            "speaker": speaker
        }
    ).json()

    audio_b64 = tts.get("audios", [""])[0]
    st.audio(f"data:audio/mp3;base64,{audio_b64}", format="audio/mp3")
