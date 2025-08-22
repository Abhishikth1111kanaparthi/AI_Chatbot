import streamlit as st
import sounddevice as sd
import soundfile as sf
import speech_recognition as sr
from gtts import gTTS
import google.generativeai as genai


genai.configure(api_key="AIzaSyAIrU13BmlwB8NwX9PpNZ411nwh7J884dw")  # getting api


# Streamlit page setup
st.set_page_config(page_title="Voice Chat with Gemini", page_icon="🎙️") # PAGE TITLE
st.title("🎙️ AI Chatbot")
st.write("Speak into your microphone and hear Chatbot will respond!")

# Maintainig chat history
if "history" not in st.session_state:
    st.session_state.history = []  # list of (user_text, bot_text)

# Recorder settings
samplerate = 16000 # audio sampling 
duration = 5  #seconds # recording only for 5 seconds 

# Recording audio
if st.button("🎤 Record 5s Audio"):
    st.info("Recording... Speak now!")
    audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1)
    sd.wait()
    sf.write("input.wav", audio, samplerate)
    st.success("Recording complete!")

    #Speech-to-Text 
    r = sr.Recognizer()
    with sr.AudioFile("input.wav") as source:
        audio_data = r.record(source)
        try:
            user_text = r.recognize_google(audio_data)
            st.write("**You said:**", user_text)
        except Exception as e:
            st.error("Speech recognition failed: " + str(e))
            user_text = None

    if user_text:
        # Sending the converted text to Gemini using the api_key 
        model = genai.GenerativeModel("gemini-2.5-flash") # using gemini 2.5 flesh model 
        response = model.generate_content(user_text) # user_text is the converted text file 
        bot_reply = response.text #  ai response text file 
        st.write("**Gemini says:**", bot_reply)

        # response to voice 
        # from text to audio (tts)  
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
