import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, ClientSettings
from utils import process_audio_bytes
import av

st.set_page_config(page_title="LICA Voice Translator", layout="centered")
st.title("🎙️ LICA - Bilingual Voice Translator")

role = st.radio("Select your role:", ("Teacher", "Student"))

st.markdown("Speak into the mic. Your translated audio will play below after processing.")

result_placeholder = st.empty()

def audio_frame_callback(frame: av.AudioFrame) -> av.AudioFrame:
    audio = frame.to_ndarray()
    sample_rate = frame.sample_rate

    with st.spinner("Processing..."):
        original_text, translated_text, translated_audio = process_audio_bytes(audio, sample_rate, role)

        result_placeholder.markdown(f"**You said:** {original_text}  \n**Translated:** {translated_text}")
        st.audio(translated_audio, format="audio/mp3")

    return frame

webrtc_streamer(
    key="voice",
    mode=WebRtcMode.SENDONLY,
    in_audio_frame_callback=audio_frame_callback,
    client_settings=ClientSettings(
        media_stream_constraints={"audio": True, "video": False},
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
    ),
)
