import streamlit as st
import speech_recognition as sr
from gtts import gTTS
import google.generativeai as genai
import tempfile

# getting gemini api key 
genai.configure(api_key="AIzaSyAIrU13BmlwB8NwX9PpNZ411nwh7J884dw")

# desgining the web page 
st.set_page_config(page_title="Voice Chat with Gemini", page_icon="🎙️") # page title 
st.title("🎙️ AI Chatbot")
st.write("Speak into your microphone and hear Chatbot respond!")

if "history" not in st.session_state: # saving chat history 
    st.session_state.history = []

# Using Browser microphone capture audio
audio_data = st.audio_input("🎤 Record Audio")

if audio_data is not None:
    st.info("Processing your voice...")

    # Saving the browser audio to a temp WAV file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        tmp_file.write(audio_data.getvalue())
        tmp_path = tmp_file.name

    # Speech-to-Text STT converting
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
        model = genai.GenerativeModel("gemini-2.5-flash") # using gemini 2.5 flash model 
        response = model.generate_content(user_text)
        bot_reply = response.text
        st.write("**Gemini says:**", bot_reply)

        # Text-to-Speech TTS conversion
        tts = gTTS(bot_reply)
        tts.save("reply.mp3")
        st.audio("reply.mp3", format="audio/mp3")

        st.session_state.history.append((user_text, bot_reply))

# Displaying chat history
if st.session_state.history:
    st.subheader("Chat History")
    for i, (q, a) in enumerate(st.session_state.history, 1):
        st.markdown(f"**You:** {q}")
        st.markdown(f"**Gemini:** {a}")
        st.markdown("---")

