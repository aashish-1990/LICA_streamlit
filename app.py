import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, AudioProcessorBase
import av
import numpy as np
import tempfile
from pydub import AudioSegment
import base64
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# TTT & TTS endpoints
TTT_API = "https://indictrans2-api.ai4bharat.org/translate"
TTS_API = "https://model-api.sarvam.ai/tts/inference/"

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY", "your_sarvam_api_key_here")  # put your API key in .env

st.set_page_config(page_title="LICA Bilingual Voice Assistant", layout="centered")
st.title("🎙️ LICA Bilingual Voice Assistant (Hindi ↔ Punjabi)")
st.markdown("Real-time voice translation with waveform and MP3 playback")

role = st.radio("Select Your Role", ["👨‍🏫 Teacher (Hindi)", "👩‍🎓 Student (Punjabi)"])
source_lang = "hi" if "Teacher" in role else "pa"
target_lang = "pa" if source_lang == "hi" else "hi"

class AudioProcessor(AudioProcessorBase):
    def __init__(self) -> None:
        self.recorded_frames = []

    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        pcm = frame.to_ndarray()
        self.recorded_frames.append(pcm)
        return frame

audio_ctx = webrtc_streamer(
    key="audio",
    mode=WebRtcMode.SENDRECV,
    audio_processor_factory=AudioProcessor,
    media_stream_constraints={"audio": True, "video": False},
)

if audio_ctx and audio_ctx.audio_processor:
    if st.button("🛑 Stop & Translate"):
        audio = np.concatenate(audio_ctx.audio_processor.recorded_frames, axis=1)
        audio = audio.astype(np.int16).tobytes()
        tmp_pcm = tempfile.NamedTemporaryFile(suffix=".pcm", delete=False)
        tmp_pcm.write(audio)
        tmp_pcm.close()

        tmp_mp3 = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
        sound = AudioSegment.from_file(tmp_pcm.name, format="s16le", frame_rate=48000, channels=1)
        sound.export(tmp_mp3.name, format="mp3")

        audio_file = tmp_mp3.name
        with open(audio_file, "rb") as f:
            mp3_b64 = base64.b64encode(f.read()).decode("utf-8")

        st.audio(audio_file, format="audio/mp3")
        st.success("✅ Voice captured and converted to MP3")

        # --- Speech-to-Text placeholder ---
        original_text = "Placeholder input sentence"  # replace with STT output if needed

        # --- Translate ---
        with st.spinner("Translating..."):
            ttt_payload = {
                "input": [{"source": original_text}],
                "config": {
                    "model": "ai4bharat/indictrans2-en-indic",
                    "src_lang": source_lang,
                    "tgt_lang": target_lang
                }
            }
            ttt_response = requests.post(TTT_API, json=ttt_payload)
            translated_text = ttt_response.json()["output"][0]["target"]

        st.markdown(f"**Original ({source_lang}):** {original_text}")
        st.markdown(f"**Translated ({target_lang}):** {translated_text}")

        # --- TTS ---
        with st.spinner("Generating Speech..."):
            tts_payload = {
                "text": translated_text,
                "language": target_lang,
                "voice": "saarika:v2",
                "sampling_rate": 24000
            }
            headers = {"Authorization": f"Bearer {SARVAM_API_KEY}"}
            tts_response = requests.post(TTS_API, json=tts_payload, headers=headers)
            tts_audio = base64.b64decode(tts_response.json()["audio"])

            tts_file = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
            tts_file.write(tts_audio)
            tts_file.close()

        st.audio(tts_file.name, format="audio/mp3")
        st.success("✅ Translated speech ready!")

