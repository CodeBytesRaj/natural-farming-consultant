import streamlit as st
import google.generativeai as genai

# ==========================
# GEMINI CONFIGURATION
# ==========================

genai.configure(api_key="")
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
    """
)

# ==========================
# TITLE
# ==========================

st.title("🌱 Natural Farming Consultant")

st.write(
    "Voice-ready AI farming assistant helping farmers with crop diseases, weather information and market intelligence."
)

# ==========================
# AI FARMING CONSULTANT
# ==========================

st.header("🤖 AI Farming Expert")

question = st.text_input(
    "Ask your farming question",
    placeholder="Example: Tomato leaves have yellow spots"
)

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