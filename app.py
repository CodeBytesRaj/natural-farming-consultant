import streamlit as st
import google.generativeai as genai
from streamlit_mic_recorder import mic_recorder
import speech_recognition as sr
from gtts import gTTS
from pydub import AudioSegment
import tempfile
import os
import io

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

model = genai.GenerativeModel("gemini-2.5-flash")

# ==========================
# PAGE CONFIG
# ==========================

st.set_page_config(
    page_title="Natural Farming Consultant",
    page_icon="🌱",
    layout="wide"
)

# ==========================
# SIDEBAR
# ==========================

st.sidebar.title("🌱 Natural Farming Consultant")

st.sidebar.info(
    """
    AI-powered assistant for farmers

    Features:
    ✅ Disease Identification
    ✅ Organic Treatment
    ✅ Weather Intelligence
    ✅ Market Intelligence
    ✅ Voice Input (Hindi/Hinglish/English)
    ✅ Voice Output (Hindi/English)
    """
)

st.title("🌱 Natural Farming Consultant")

st.write(
    "Voice-ready AI farming assistant helping farmers with crop diseases, weather information and market intelligence."
)

# ==========================
# SESSION STATE INIT
# ==========================
# Used to pass recognized speech text into the question text box,
# and to remember the last AI answer so TTS can be regenerated on demand.

if "voice_question" not in st.session_state:
    st.session_state.voice_question = ""

if "last_answer" not in st.session_state:
    st.session_state.last_answer = ""

# ==========================
# HELPER: SPEECH-TO-TEXT
# ==========================

def transcribe_audio(audio_bytes):
    """
    Converts recorded microphone audio (raw bytes from mic_recorder)
    into text using Google Web Speech API via SpeechRecognition.

    Tries Hindi first (covers Hindi + most Hinglish speech patterns),
    then falls back to Indian English if Hindi recognition fails.

    Returns (recognized_text, error_message). One of them will be None.
    """
    tmp_webm_path = None
    tmp_wav_path = None
    try:
        # Save raw recorded bytes to a temp file first (mic_recorder usually
        # returns webm/ogg-style audio depending on browser).
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp_webm:
            tmp_webm.write(audio_bytes)
            tmp_webm_path = tmp_webm.name

        # Convert to clean 16-bit PCM WAV using pydub (requires ffmpeg).
        sound = AudioSegment.from_file(tmp_webm_path)
        tmp_wav_path = tmp_webm_path.replace(".webm", ".wav")
        sound.export(tmp_wav_path, format="wav")

        recognizer = sr.Recognizer()
        with sr.AudioFile(tmp_wav_path) as source:
            audio_data = recognizer.record(source)

        # Try Hindi first
        try:
            text = recognizer.recognize_google(audio_data, language="hi-IN")
            return text, None
        except sr.UnknownValueError:
            # Fall back to Indian English (handles English / mixed Hinglish typed in Latin script)
            try:
                text = recognizer.recognize_google(audio_data, language="en-IN")
                return text, None
            except sr.UnknownValueError:
                return None, "Sorry, I could not understand the audio. Please speak clearly and try again."
            except sr.RequestError as e:
                return None, f"Speech recognition service error: {e}"
        except sr.RequestError as e:
            return None, f"Speech recognition service error: {e}"

    except Exception as e:
        return None, f"Could not process the recorded audio: {e}"

    finally:
        # Clean up temp files regardless of success/failure
        for path in (tmp_webm_path, tmp_wav_path):
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except Exception:
                    pass


# ==========================
# HELPER: TEXT-TO-SPEECH
# ==========================

def text_to_speech_bytes(text, lang_code):
    """
    Converts text into speech audio bytes using gTTS.
    Returns (audio_bytes, error_message).
    """
    try:
        tts = gTTS(text=text, lang=lang_code)
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        buf.seek(0)
        return buf.read(), None
    except Exception as e:
        return None, f"Could not generate audio: {e}"


# ==========================
# VOICE ASSISTANT (STT)
# ==========================

st.header("🎤 Voice Assistant")

st.caption("Speak in Hindi, Hinglish, or English. Click Stop when done.")

audio = mic_recorder(
    start_prompt="🎙️ Start Recording",
    stop_prompt="⏹️ Stop Recording",
    key="voice"
)

# Handle microphone / recording failures gracefully
if audio is None:
    st.info("Waiting for microphone input... (click 'Start Recording' above)")
elif not audio.get("bytes"):
    st.warning("No audio detected. Please check microphone permissions and try again.")
else:
    with st.spinner("Transcribing your speech..."):
        recognized_text, stt_error = transcribe_audio(audio["bytes"])

    if stt_error:
        st.error(stt_error)
    elif recognized_text:
        st.success("Recognized Speech:")
        st.write(f"🗣️ **{recognized_text}**")
        # Push recognized text into the question box below
        st.session_state.voice_question = recognized_text

# ==========================
# AI FARMING CONSULTANT
# ==========================

st.header("🤖 AI Farming Expert")

# Text input is pre-filled with recognized voice text (if any),
# but farmers can still type directly — original behavior preserved.
question = st.text_input(
    "Ask your farming question",
    value=st.session_state.voice_question,
    placeholder="Example: Tomato leaves have yellow spots"
)

# Language choice for the spoken (TTS) response
voice_lang = st.radio(
    "🔊 Voice response language",
    options=["Hindi", "English"],
    horizontal=True
)
voice_lang_code = "hi" if voice_lang == "Hindi" else "en"

if question:

    prompt = f"""
    You are an expert Natural Farming Consultant for Indian farmers.

    Answer ONLY farming and agriculture related questions.

    Provide:

    1. Problem Identification
    2. Organic Treatment
    3. Prevention Measures

    Rules:
    - Use simple language.
    - Promote natural farming.
    - Avoid chemical pesticides.
    - If unsure, advise consulting a local agricultural officer.

    Question:
    {question}
    """

    try:
        response = model.generate_content(prompt)

        st.success("AI Recommendation")
        st.write(response.text)

        st.session_state.last_answer = response.text

        # ==========================
        # TEXT-TO-SPEECH OUTPUT
        # ==========================
        with st.spinner("Generating voice response..."):
            audio_bytes, tts_error = text_to_speech_bytes(response.text, voice_lang_code)

        if tts_error:
            st.warning(tts_error)
        elif audio_bytes:
            st.audio(audio_bytes, format="audio/mp3")

    except Exception as e:
        st.error(f"Error: {e}")

# ==========================
# WEATHER INFORMATION
# ==========================

st.header("☁️ Weather Intelligence")

weather_data = {
    "Agra": {"temp": 38, "humidity": 58},
    "Delhi": {"temp": 37, "humidity": 55},
    "Noida": {"temp": 36, "humidity": 62},
    "Lucknow": {"temp": 35, "humidity": 68},
    "Jaipur": {"temp": 39, "humidity": 45},
    "Kanpur": {"temp": 34, "humidity": 70}
}

city = st.selectbox(
    "Select City",
    list(weather_data.keys())
)

if st.button("Get Weather Information"):

    temp = weather_data[city]["temp"]
    humidity = weather_data[city]["humidity"]

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Temperature", f"{temp} °C")

    with col2:
        st.metric("Humidity", f"{humidity}%")

# ==========================
# MARKET INTELLIGENCE
# ==========================

st.header("📈 Market Intelligence")

market_prices = {
    "Wheat": "₹2450 / Quintal",
    "Rice": "₹2800 / Quintal",
    "Mustard": "₹6100 / Quintal",
    "Tomato": "₹2200 / Quintal",
    "Potato": "₹1800 / Quintal",
    "Onion": "₹2500 / Quintal",
    "Maize": "₹2100 / Quintal"
}

crop = st.selectbox(
    "Select Crop",
    list(market_prices.keys())
)

if st.button("Get Market Price"):

    st.success(
        f"Current Market Price of {crop}: {market_prices[crop]}"
    )

# ==========================
# NATURAL FARMING EDUCATION
# ==========================

st.header("🌾 Natural Farming Tips")

st.info(
    """
    • Use Neem Oil Spray for pest control.

    • Practice crop rotation to maintain soil fertility.

    • Use cow dung compost and vermicompost.

    • Avoid excessive chemical fertilizers.

    • Maintain proper irrigation schedules.

    • Encourage beneficial insects in the field.
    """
)

# ==========================
# FOOTER
# ==========================

st.markdown("---")

st.caption(
    "Built for Connecting Dreams Foundation (CDF) Technical Assignment"
)