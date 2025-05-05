import io
import numpy as np
import soundfile as sf
import requests

SARVAM_STT_URL = "https://api.sarvam.ai/stt"
SARVAM_TTT_URL = "https://api.sarvam.ai/translate"
SARVAM_TTS_URL = "https://api.sarvam.ai/tts"

def process_audio_bytes(audio_np, sample_rate, role):
    # Convert raw numpy audio to WAV in-memory
    wav_io = io.BytesIO()
    sf.write(wav_io, audio_np, sample_rate, format='WAV')
    wav_io.seek(0)

    # 1. Speech-to-Text
    stt_response = requests.post(SARVAM_STT_URL, files={"audio": ("audio.wav", wav_io, "audio/wav")})
    stt_text = stt_response.json().get("text", "")

    # 2. Translate
    if role == "Teacher":
        src, tgt = "hi", "pa"
    else:
        src, tgt = "pa", "hi"

    ttt_response = requests.post(SARVAM_TTT_URL, json={"text": stt_text, "source": src, "target": tgt})
    translated_text = ttt_response.json().get("translated_text", "")

    # 3. Text-to-Speech
    tts_response = requests.post(SARVAM_TTS_URL, json={"text": translated_text, "lang": tgt})
    audio_mp3 = tts_response.content

    return stt_text, translated_text, io.BytesIO(audio_mp3)
