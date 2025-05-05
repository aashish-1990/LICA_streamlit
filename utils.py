import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import tempfile
import os
import base64
import requests
from pydub import AudioSegment
from pydub.playback import play

# Sarvam AI endpoints
STT_API = "https://stt.api.sarvam.ai/api/stt"
TTT_API = "https://transliteration.api.sarvam.ai/api/translate"
TTS_API = "https://tts.api.sarvam.ai/api/tts"

# Recording function
def record_audio(duration=5, fs=16000):
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        wav.write(f.name, fs, recording)
        return f.name

# Transcription
def transcribe_audio(file_path, source_lang="hi"):
    with open(file_path, "rb") as f:
        response = requests.post(STT_API, files={"file": f}, data={"language": source_lang})
    return response.json().get("text", "Transcription failed")

# Translation
def translate_text(text, src_lang="hi", tgt_lang="pa"):
    payload = {"text": text, "source_language": src_lang, "target_language": tgt_lang}
    response = requests.post(TTT_API, json=payload)
    return response.json().get("translated_text", "Translation failed")

# Speech synthesis
def synthesize_speech(text, language="pa"):
    payload = {"text": text, "language": language}
    response = requests.post(TTS_API, json=payload)
    audio_base64 = response.json().get("audio_base64")
    if audio_base64:
        audio_data = base64.b64decode(audio_base64)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
            f.write(audio_data)
            return f.name
    return None

# Audio playback
def play_audio(file_path):
    audio = AudioSegment.from_file(file_path)
    play(audio)

# Optional voice config if needed later
def set_voice_params():
    return {
        "voice": "default",
        "rate": "medium"
    }
