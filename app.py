import streamlit as st
from utils import (
    record_audio,
    transcribe_audio,
    translate_text,
    synthesize_speech,
    play_audio,
    set_voice_params
)
import tempfile
import os

st.set_page_config(layout="centered", page_title="LICA - Bilingual Voice Translator")

st.title("🗣️ LICA: Bilingual Voice Translator for Classrooms")

# Role Selection
role = st.radio("Select your role:", ["👩‍🏫 Teacher", "🧑‍🎓 Student"], horizontal=True)

# UI Sections
if role == "👩‍🏫 Teacher":
    st.subheader("🎤 Teacher speaks in Hindi → Student hears in Punjabi")

    if st.button("Start Recording (Teacher)"):
        st.info("Recording Teacher's audio...")
        teacher_audio = record_audio()
        st.success("Recording complete!")

        st.audio(teacher_audio, format="audio/mp3", start_time=0)

        with st.spinner("Transcribing (Hindi)..."):
            teacher_text = transcribe_audio(teacher_audio, source_lang="hi")
        st.write("✍️ Transcribed Text (Hindi):", teacher_text)

        with st.spinner("Translating to Punjabi..."):
            translated_text = translate_text(teacher_text, src_lang="hi", tgt_lang="pa")
        st.write("🌐 Translated Text (Punjabi):", translated_text)

        with st.spinner("Synthesizing Punjabi Speech..."):
            output_audio = synthesize_speech(translated_text, language="pa")
        st.success("✅ Translated audio ready!")

        st.audio(output_audio, format="audio/mp3", start_time=0)
        play_audio(output_audio)

elif role == "🧑‍🎓 Student":
    st.subheader("🎤 Student speaks in Punjabi → Teacher hears in Hindi")

    if st.button("Start Recording (Student)"):
        st.info("Recording Student's audio...")
        student_audio = record_audio()
        st.success("Recording complete!")

        st.audio(student_audio, format="audio/mp3", start_time=0)

        with st.spinner("Transcribing (Punjabi)..."):
            student_text = transcribe_audio(student_audio, source_lang="pa")
        st.write("✍️ Transcribed Text (Punjabi):", student_text)

        with st.spinner("Translating to Hindi..."):
            translated_text = translate_text(student_text, src_lang="pa", tgt_lang="hi")
        st.write("🌐 Translated Text (Hindi):", translated_text)

        with st.spinner("Synthesizing Hindi Speech..."):
            output_audio = synthesize_speech(translated_text, language="hi")
        st.success("✅ Translated audio ready!")

        st.audio(output_audio, format="audio/mp3", start_time=0)
        play_audio(output_audio)
