import streamlit as st
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, WebRtcMode
import av
import speech_recognition as sr
from gtts import gTTS
import google.generativeai as genai
import tempfile

# Configure Gemini API
genai.configure(api_key="AIzaSyAIrU13BmlwB8NwX9PpNZ411nwh7J884dw")

st.set_page_config(page_title="Voice Chat with Gemini", page_icon="🎙️")
st.title("🎙️ AI Chatbot")
st.write("Speak into your microphone and hear Gemini respond!")

# Maintain chat history
if "history" not in st.session_state:
    st.session_state.history = []

# Custom audio processor to save raw audio
class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.frames = []

    def recv_audio(self, frame):
        audio = frame.to_ndarray()
        self.frames.append(audio)
        return frame

# Start WebRTC streamer
webrtc_ctx = webrtc_streamer(
    key="speech-to-text",
    mode=WebRtcMode.SENDRECV,
    audio_processor_factory=AudioProcessor,
    media_stream_constraints={"audio": True, "video": False},
)

# Once recording is done
if webrtc_ctx.audio_processor and st.button("Process Recording"):
    # Save audio to temporary WAV
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        processor = webrtc_ctx.audio_processor
        import soundfile as sf
        if processor.frames:
            sf.write(f.name, processor.frames[0], 16000)
            audio_path = f.name

            # Speech-to-text
            r = sr.Recognizer()
            with sr.AudioFile(audio_path) as source:
                audio_data = r.record(source)
                try:
                    user_text = r.recognize_google(audio_data)
                    st.write("**You said:**", user_text)
                except Exception as e:
                    st.error("Speech recognition failed: " + str(e))
                    user_text = None

            # Send to Gemini and play response
            if user_text:
                model = genai.GenerativeModel("gemini-2.5-flash")
                response = model.generate_content(user_text)
                bot_reply = response.text
                st.write("**Gemini says:**", bot_reply)

                tts = gTTS(bot_reply)
                reply_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
                tts.save(reply_file.name)
                st.audio(reply_file.name, format="audio/mp3")

                # Save to history
                st.session_state.history.append((user_text, bot_reply))
        else:
            st.error("No audio captured. Please try speaking again.")

# Display chat history
if st.session_state.history:
    st.subheader("Chat History")
    for q, a in st.session_state.history:
        st.markdown(f"**You:** {q}")
        st.markdown(f"**Gemini:** {a}")
        st.markdown("---")
