import streamlit as st
import speech_recognition as sr
from gtts import gTTS
import google.generativeai as genai
import tempfile

genai.configure(api_key="AIzaSyAIrU13BmlwB8NwX9PpNZ411nwh7J884dw")

st.set_page_config(page_title="Voice Chat with Gemini", page_icon="🎙️")
st.title("🎙️ AI Chatbot")
st.write("Speak into your microphone and hear Chatbot respond!")

if "history" not in st.session_state:
    st.session_state.history = []

# Browser microphone capture
audio_data = st.audio_input("🎤 Record 5s Audio")

if audio_data is not None:
    st.info("Processing your voice...")

    # Save the browser audio to a temp WAV file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        tmp_file.write(audio_data.getvalue())
        tmp_path = tmp_file.name

    # Speech-to-Text
    r = sr.Recognizer()
    with sr.AudioFile(tmp_path) as source:
        audio_content = r.record(source)
        try:
            user_text = r.recognize_google(audio_content)
            st.write("**You said:**", user_text)
        except Exception as e:
            st.error("Speech recognition failed: " + str(e))
            user_text = None

    if user_text:
        # Gemini response
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(user_text)
        bot_reply = response.text
        st.write("**Gemini says:**", bot_reply)

        # Text-to-Speech
        tts = gTTS(bot_reply)
        tts.save("reply.mp3")
        st.audio("reply.mp3", format="audio/mp3")

        st.session_state.history.append((user_text, bot_reply))

# Display chat history
if st.session_state.history:
    st.subheader("Chat History")
    for i, (q, a) in enumerate(st.session_state.history, 1):
        st.markdown(f"**You:** {q}")
        st.markdown(f"**Gemini:** {a}")
        st.markdown("---")
