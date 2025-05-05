import requests
from pydub import AudioSegment
import tempfile
import base64

# Sarvam AI endpoints
STT_API = "https://stt.api.sarvam.ai/v1/audio"
TTT_API = "https://api.sarvam.ai/v1/translate"
TTS_API = "https://api.sarvam.ai/v1/tts"

# Headers for Sarvam TTT and TTS (STT does not need headers)
HEADERS = {"accept": "application/json", "Content-Type": "application/json"}

# Role-based language logic
def detect_language(role):
    return "hi" if role == "teacher" else "pa"  # Hindi if Teacher, Punjabi if Student

def detect_target_language(role):
    return "pa" if role == "teacher" else "hi"  # Opposite of source

def transcribe_and_translate(audio_bytes, role):
    # Save MP3 bytes to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
        tmp.write(audio_bytes)
        tmp.flush()
        tmp_path = tmp.name

    # Convert to WAV
    audio = AudioSegment.from_mp3(tmp_path)
    audio.export("temp.wav", format="wav")

    # Call Sarvam STT
    files = {'file': open("temp.wav", 'rb')}
    response = requests.post(STT_API, files=files)
    original_text = response.json().get("text", "")

    # Call Sarvam TTT
    payload = {
        "text": original_text,
        "source_language": detect_language(role),
        "target_language": detect_target_language(role)
    }
    res = requests.post(TTT_API, json=payload, headers=HEADERS)
    translated_text = res.json().get("text", "")

    return original_text, translated_text

def generate_audio(text, role):
    # Call Sarvam TTS
    payload = {
        "text": text,
        "speaker": "ai2",  # Choose from available voices: ai1, ai2, ...
        "language": detect_target_language(role)
    }
    res = requests.post(TTS_API, json=payload, headers=HEADERS)
    audio_base64 = res.json().get("audio", "")
    return base64.b64decode(audio_base64)
