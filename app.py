import streamlit as st
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase
import av
import io
import base64
import requests
from pydub import AudioSegment
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("SARVAM_API_KEY")

st.set_page_config(page_title="LICA Teacher Assist", layout="centered")
st.title("🎙️ LICA Teacher Assist")

st.markdown("A real-time Hindi ↔ Punjabi voice translator for classrooms.")

role = st.radio("Select your role:", ("Teacher (Hindi)", "Student (Punjabi)"))

# Set language directions
if "Teacher" in role:
    source_lang, target_lang, speaker = "hi-IN", "pa-IN", "anushka"
else:
    source_lang, target_lang, speaker = "pa-IN", "hi-IN", "karun"

class AudioProcessor(AudioProcessorBase):
    def __init__(self) -> None:
        self.recorded_frames = []

    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        self.recorded_frames.append(frame)
        return frame

    def get_audio_segment(self) -> AudioSegment:
        if not self.recorded_frames:
            return None
        buffer = io.BytesIO()
        out = av.open(buffer, 'w', format='mp3')
        stream = out.add_stream('mp3')
        for frame in self.recorded_frames:
            frame.pts = None
            out.mux(stream.encode(frame))
        out.close()
        buffer.seek(0)
        return AudioSegment.from_file(buffer, format="mp3")

# Start streamlit-webrtc
ctx = webrtc_streamer(
    key="translate",
    audio_processor_factory=AudioProcessor,
    media_stream_constraints={"audio": True, "video": False},
    async_processing=True
)

if ctx.audio_processor and ctx.state.playing:
    st.info("Recording... Speak now.")
    if st.button("🔁 Translate and Play"):
        audio_segment = ctx.audio_processor.get_audio_segment()
        if audio_segment:
            # Save as MP3
            mp3_io = io.BytesIO()
            audio_segment.export(mp3_io, format="mp3")
            mp3_io.seek(0)

            # STT
            st.info("Transcribing...")
            stt_resp = requests.post(
                "https://api.sarvam.ai/speech-to-text",
                headers={"API-Subscription-Key": API_KEY},
                files={"file": ("audio.mp3", mp3_io, "audio/mp3")},
                data={"model": "saarika:v2", "language_code": "unknown"},
            ).json()
            transcript = stt_resp.get("transcript", "")

            # Translation
            st.info("Translating...")
            trans_resp = requests.post(
                "https://api.sarvam.ai/translate",
                headers={
                    "API-Subscription-Key": API_KEY,
                    "Content-Type": "application/json"
                },
                json={
                    "input": transcript,
                    "source_language_code": source_lang,
                    "target_language_code": target_lang,
                    "mode": "formal"
                }
            ).json()
            translated = trans_resp.get("translated_text", "")

            # TTS
            st.info("Converting to Speech...")
            tts_resp = requests.post(
                "https://api.sarvam.ai/text-to-speech",
                headers={
                    "API-Subscription-Key": API_KEY,
                    "Content-Type": "application/json"
                },
                json={
                    "text": translated,
                    "target_language_code": target_lang,
                    "speaker": speaker
                }
            ).json()
            audio_b64 = tts_resp.get("audios", [""])[0]

            st.success("✅ Translation Complete")

            st.markdown(f"**Original:** {transcript}")
            st.markdown(f"**Translated:** {translated}")
            st.audio(f"data:audio/mp3;base64,{audio_b64}", format="audio/mp3")
        else:
            st.warning("No audio recorded.")
