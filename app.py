import streamlit as st
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase
import numpy as np
import av
import tempfile
from pydub import AudioSegment
import base64
import requests
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="LICA Voice Translator", layout="centered")

# Sarvam endpoint
TRANSLATION_API = os.getenv("TRANSLATION_API_URL", "http://localhost:8000/translate_play")

st.title("🗣️ LICA Teacher Assist — Hindi ↔ Punjabi")

role = st.radio("🎭 Select Your Role:", ["👨‍🏫 Teacher (Hindi)", "🎓 Student (Punjabi)"])
selected_role = "teacher" if "Teacher" in role else "student"

status_placeholder = st.empty()
translated_text = st.empty()

class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.recorded_frames = []

    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        pcm = frame.to_ndarray()
        self.recorded_frames.append(pcm)
        return frame

audio_ctx = webrtc_streamer(
    key="audio",
    mode="SENDRECV",
    audio_processor_factory=AudioProcessor,
    media_stream_constraints={"audio": True, "video": False},
    async_processing=False,
)

if audio_ctx.state.playing:
    status_placeholder.info("🎙️ Recording... Speak now!")

    if st.button("Stop and Translate"):
        # Convert frames to np.int16
        audio_data = np.concatenate(audio_ctx.audio_processor.recorded_frames).astype(np.int16)

        # Save as .webm then convert to .mp3
        temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        temp_mp3 = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")

        # Save .wav using PyAV
        with open(temp_wav.name, "wb") as f:
            wav_audio = AudioSegment(
                audio_data.tobytes(),
                frame_rate=48000,
                sample_width=2,
                channels=1
            )
            wav_audio.export(f, format="wav")

        # Convert to mp3
        sound = AudioSegment.from_wav(temp_wav.name)
        sound.export(temp_mp3.name, format="mp3")

        # Send to backend as base64
        with open(temp_mp3.name, "rb") as f:
            b64_audio = base64.b64encode(f.read()).decode("utf-8")

        status_placeholder.info("🔄 Translating...")
        res = requests.post(TRANSLATION_API, json={
            "audio": f"data:audio/mp3;base64,{b64_audio}",
            "role": selected_role
        })

        if res.status_code == 200:
            data = res.json()
            original = data.get("original", "N/A")
            translated = data.get("translated", "N/A")
            audio_response = data.get("audio", "")

            translated_text.success(f"✅ Original: {original}\n\n🗣️ Translated: {translated}")

            # Auto-play response
            st.audio(f"data:audio/mp3;base64,{audio_response}", format="audio/mp3")
        else:
            st.error("❌ Failed to translate. Try again.")
