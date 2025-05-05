import requests
import streamlit as st
from pydub import AudioSegment
import tempfile
import base64

SARVAM_STT = "https://stt.api.sarvam.ai/asr"
SARVAM_TTT = "https://sarvam.ai/api/translate"
SARVAM_TTS = "https://tts.api.sarvam.ai/tts"

def transcribe_and_translate(audio_bytes, role):
    # Convert MP3 to WAV in memory
    audio = AudioSegment.from_mp3(tempfile.NamedTemporaryFile(delete=False).name)
    audio.export("temp.wav", format="wav")
    files = {'file': open("temp.wav", 'rb')}

    # STT
    stt_response = requests.post(SARVAM_STT, files=files).json()
    original_text = stt_response.get("text", "")

    # TTT
    if role == "teacher":
        ttt_data = {"text": original_text, "source": "hi", "target": "pa"}
    else:
        ttt_data = {"text": original_text, "source": "pa", "target": "hi"}
    ttt_response = requests.post(SARVAM_TTT, json=ttt_data).json()
    translated_text = ttt_response.get("translated_text", "")

    return original_text, translated_text

def generate_audio(text, role):
    lang = "pa" if role == "teacher" else "hi"
    tts_data = {"text": text, "lang": lang}
    tts_response = requests.post(SARVAM_TTS, json=tts_data)
    return tts_response.content if tts_response.status_code == 200 else None

def play_audio(audio_bytes):
    b64 = base64.b64encode(audio_bytes).decode()
    audio_tag = f"""
        <audio autoplay controls>
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
    """
    st.markdown(audio_tag, unsafe_allow_html=True)
