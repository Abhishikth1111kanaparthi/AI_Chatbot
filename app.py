import streamlit as st
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, WebRtcMode
import speech_recognition as sr
from gtts import gTTS
import google.generativeai as genai
import av
import soundfile as sf
import numpy as np
import time

# Configure Gemini API
genai.configure(api_key="YOUR_API_KEY_HERE")  # <-- replace with your Gemini API key

# Streamlit page setup
st.set_page_config(page_title="Voice Chat with Gemini", page_icon="🎙️")
st.title("🎙️ AI Chatbot")
st.write("Click the button, speak for 5 seconds, and hear Gemini respond!")

# Maintain chat history
if "history" not in st.session_state:
    st.session_state.history = []  # list of (user_text, bot_text)

# Speech recognition instance
recognizer = sr.Recognizer()

# Audio processor to collect mic input
class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.frames = []

    def recv_audio(self, frame: av.AudioFrame) -> av.AudioFrame:
        audio = frame.to_ndarray()
        self.frames.append(audio)
        return frame

    def get_audio_data(self):
        if not self.frames:
            return None
        audio_data = np.concatenate(self.frames, axis=0).astype("int16")
        self.frames = []
        return audio_data

# Button to record for 5 seconds
if st.button("🎤 Record 5 Seconds"):
    st.info("Recording... Speak now!")
    ctx = webrtc_streamer(
        key="audio-only",
        mode=WebRtcMode.SENDONLY,
        audio_processor_factory=AudioProcessor,
        media_stream_constraints={"audio": True, "video": False},
    )

    # Wait for 5 seconds while recording
    start_time = time.time()
    while time.time() - start_time < 5:
        time.sleep(0.1)
    st.success("Recording complete!")

    # Extract audio and stop stream
    if ctx.audio_processor:
        audio_data = ctx.audio_processor.get_audio_data()
        ctx.stop()  # stop the WebRTC stream

        if audio_data is None:
            st.warning("No audio captured. Please try again.")
        else:
            # Save to WAV for speech recognition
            sf.write("input.wav", audio_data, 16000)

            # Speech-to-text using Google Speech Recognition
            with sr.AudioFile("input.wav") as source:
                audio = recognizer.record(source)
                try:
                    user_text = recognizer.recognize_google(audio)
                    st.write("**You said:**", user_text)
                except Exception as e:
                    st.error("Speech recognition failed: " + str(e))
                    user_text = None

            if user_text:
                # Send user text to Gemini API
                model = genai.GenerativeModel("gemini-2.5-flash")
                response = model.generate_content(user_text)
                bot_reply = response.text
                st.write("**Gemini says:**", bot_reply)

                # Convert bot reply to speech
                tts = gTTS(bot_reply)
                tts.save("reply.mp3")
                st.audio("reply.mp3", format="audio/mp3")

                # Save conversation
                st.session_state.history.append((user_text, bot_reply))

# Display chat history
if st.session_state.history:
    st.subheader("Chat History")
    for i, (q, a) in enumerate(st.session_state.history, 1):
        st.markdown(f"**You:** {q}")
        st.markdown(f"**Gemini:** {a}")
        st.markdown("---")
