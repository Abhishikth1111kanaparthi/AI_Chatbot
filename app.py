import streamlit as st
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase
import speech_recognition as sr
from gtts import gTTS
import google.generativeai as genai
import av

genai.configure(api_key="AIzaSyAIrU13BmlwB8NwX9PpNZ411nwh7J884dw")  # Configure Gemini API

# Streamlit page setup
st.set_page_config(page_title="Voice Chat with Gemini", page_icon="🎙️")
st.title("🎙️ AI Chatbot")
st.write("Speak into your microphone and hear Chatbot respond!")

# Maintain chat history
if "history" not in st.session_state:
    st.session_state.history = []  # list of (user_text, bot_text)

# Recognizer instance
recognizer = sr.Recognizer()

class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.frames = []

    def recv_audio(self, frame: av.AudioFrame) -> av.AudioFrame:
        # Collect audio frames for processing
        audio = frame.to_ndarray()
        self.frames.append(audio)
        return frame

    def get_audio_data(self):
        import numpy as np
        if not self.frames:
            return None
        audio_data = np.concatenate(self.frames, axis=0).astype("int16")
        self.frames = []  # clear buffer
        return audio_data

# Start WebRTC streamer
ctx = webrtc_streamer(key="speech-to-text", audio_processor_factory=AudioProcessor)

if ctx.audio_processor:
    if st.button("Process Speech"):
        audio_data = ctx.audio_processor.get_audio_data()
        if audio_data is None:
            st.warning("No audio captured.")
        else:
            # Save to WAV file
            import soundfile as sf
            sf.write("input.wav", audio_data, 16000)  # 16kHz sample rate

            # Convert speech to text
            with sr.AudioFile("input.wav") as source:
                audio = recognizer.record(source)
                try:
                    user_text = recognizer.recognize_google(audio)
                    st.write("**You said:**", user_text)
                except Exception as e:
                    st.error("Speech recognition failed: " + str(e))
                    user_text = None

            if user_text:
                # Send text to Gemini API
                model = genai.GenerativeModel("gemini-2.5-flash")
                response = model.generate_content(user_text)
                bot_reply = response.text
                st.write("**Gemini says:**", bot_reply)

                # Convert AI response to speech
                tts = gTTS(bot_reply)
                tts.save("reply.mp3")
                st.audio("reply.mp3", format="audio/mp3")

                # Save to chat history
                st.session_state.history.append((user_text, bot_reply))

# Display chat history
if st.session_state.history:
    st.subheader("Chat History")
    for i, (q, a) in enumerate(st.session_state.history, 1):
        st.markdown(f"**You:** {q}")
        st.markdown(f"**Gemini:** {a}")
        st.markdown("---")
