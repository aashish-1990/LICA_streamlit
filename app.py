import streamlit as st
from audio_recorder_streamlit import audio_recorder
from utils import transcribe_and_translate, generate_audio, play_audio

st.set_page_config(page_title="LICA Voice Translator", layout="wide")

st.title("🎙️ LICA: Multilingual Classroom Voice Assistant")

role = st.radio("Select your role", ["Teacher", "Student"], horizontal=True)

left_col, right_col = st.columns(2)

# Layout helper
def render_section(col, label, role_tag):
    with col:
        st.markdown(f"### {label} Section")
        audio_bytes = audio_recorder(
            text=f"Click to record ({label})",
            icon_size="2x"
        )
        original_text = ""
        translated_text = ""
        audio_out = None

        if audio_bytes:
            with st.spinner("Transcribing..."):
                original_text, translated_text = transcribe_and_translate(audio_bytes, role_tag)
            with st.spinner("Generating audio..."):
                audio_out = generate_audio(translated_text, role_tag)

        if original_text:
            st.markdown("**Original Text:**")
            st.success(original_text)
        if translated_text:
            st.markdown("**Translated Text:**")
            st.info(translated_text)
        if audio_out:
            play_audio(audio_out)

# Teacher speaks → show original in Teacher, translated + audio in Student
# Student speaks → show original in Student, translated + audio in Teacher
if role == "Teacher":
    render_section(left_col, "Teacher", "teacher")
    render_section(right_col, "Student", "student_dummy")  # dummy right card just for layout
else:
    render_section(left_col, "Teacher", "teacher_dummy")
    render_section(right_col, "Student", "student")
