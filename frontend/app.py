import streamlit as st
import requests
from fpdf import FPDF
import speech_recognition as sr
import re

# --- CONFIGURATION ---
ST_API_URL = "http://127.0.0.1:5000/api/chat"

st.set_page_config(
    page_title="MediAssist AI",
    page_icon="🩺",
    layout="centered"
)

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- SAFE RERUN FUNCTION (Fixes Version Errors) ---
def safe_rerun():
    """Handles rerun for both new and old Streamlit versions"""
    try:
        st.rerun()
    except AttributeError:
        st.experimental_rerun()

# --- THEME MANAGER (Simplified & Safe) ---
def apply_theme(mode):
    try:
        # 1. Define Defaults
        text_color = "#000000"
        bg_color = "#FFFFFF"
        header_bg = "transparent"
        bg_image = "none"
        chat_bg = "#F0F2F6"

        # 2. Set Colors based on Mode
        if mode == "Dark Mode":
            text_color = "#FFFFFF"
            bg_color = "#0E1117"
            chat_bg = "#262730"
        
        elif mode == "Medical Mode":
            text_color = "#000000"
            bg_color = "rgba(255, 255, 255, 0.9)"
            chat_bg = "rgba(255, 255, 255, 0.8)"
            header_bg = "rgba(255, 255, 255, 0.9)"
            bg_image = "url('https://img.freepik.com/free-vector/clean-medical-background_53876-97927.jpg')"

        # 3. Inject CSS
        st.markdown(f"""
        <style>
            /* Main Background */
            .stApp {{
                background-color: {bg_color};
                background-image: {bg_image};
                background-size: cover;
                background-attachment: fixed;
            }}
            /* Text Coloring */
            h1, h2, h3, p, span, div, .stMarkdown, label {{
                color: {text_color} !important;
            }}
            /* Chat Message Bubbles */
            div[data-testid="stChatMessage"] {{
                background-color: {chat_bg};
                border-radius: 10px;
                padding: 10px;
            }}
            /* Header Area */
            .main-header {{
                text-align: center;
                padding: 20px;
                border-bottom: 2px solid #ddd;
                margin-bottom: 20px;
                background-color: {header_bg};
                border-radius: 10px;
            }}
            .title {{
                font-size: 40px;
                font-weight: bold;
                margin: 0;
                color: {text_color} !important;
            }}
            .icon {{
                font-size: 50px;
                display: block;
                margin-bottom: 10px;
            }}
            .disclaimer {{
                font-size: 14px;
                opacity: 0.8;
                margin-top: 5px;
                line-height: 1.5;
                color: {text_color} !important;
            }}
        </style>
        """, unsafe_allow_html=True)
    except Exception as e:
        # Fallback if styling fails
        print(f"Theme Error: {e}")

# --- TEXT SANITIZER (fixes latin-1 crashes) ---
_LATIN1_SAFE_MAP = {
    "\u2018": "'",  # left single quote
    "\u2019": "'",  # right single quote
    "\u201C": '"',  # left double quote
    "\u201D": '"',  # right double quote
    "\u2013": "-",  # en dash
    "\u2014": "-",  # em dash
    "\u2022": "-",  # bullet
    "\u2212": "-",  # minus sign
    "\u00A0": " ",  # non-breaking space
    "\u200B": "",   # zero-width space
    "\uFEFF": "",   # BOM/ZWNBSP
}

def sanitize_to_latin1(text: str) -> str:
    if not isinstance(text, str):
        text = str(text)
    # Replace common troublemakers
    for bad, good in _LATIN1_SAFE_MAP.items():
        text = text.replace(bad, good)
    # Strip other non-latin-1 code points while keeping readable content
    # (encode/decode trick)
    text = text.encode("latin-1", "ignore").decode("latin-1")
    # Collapse accidental control characters except newlines/tabs
    text = re.sub(r"[^\x09\x0A\x0D\x20-\x7E\xA0-\xFF]", "", text)
    return text

# --- PDF GENERATOR ---
def create_pdf(chat_history):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, txt="MediAssist AI - Consultation Report", ln=True, align='C')
    pdf.ln(5)

    for msg in chat_history:
        role = "Patient" if msg.get("role") == "user" else "MediAssist AI"
        # Remove markdown emphasis then sanitize to latin-1
        raw = (msg.get("content") or "").replace("**", "").replace("*", "")
        text = sanitize_to_latin1(raw)

        pdf.set_font("Arial", style='B', size=12)
        pdf.cell(0, 8, sanitize_to_latin1(f"{role}:"), ln=True)
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 8, text)
        pdf.ln(1)

    # FPDF classic produces a str for dest='S'; Streamlit needs bytes
    return pdf.output(dest='S').encode('latin-1')

# --- VOICE RECORDER ---
def record_voice():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.toast("🎤 Listening... Speak now!", icon="👂")
        try:
            audio = r.listen(source, timeout=5)
            text = r.recognize_google(audio)
            return text
        except Exception:
            return None

# --- BACKEND API CALL ---
def get_bot_response(user_text):
    try:
        response = requests.post(ST_API_URL, json={"message": user_text})
        if response.status_code == 200:
            return response.json().get("response", "Error: Empty response.")
        return "Error: Backend returned failure status."
    except Exception as e:
        return f"Error: Could not connect to server. ({str(e)})"

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Settings")
    selected_theme = st.radio("Theme:", ["Light Mode", "Dark Mode", "Medical Mode"])
    apply_theme(selected_theme)
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.messages = []
            safe_rerun()
    with col2:
        if st.session_state.messages:
            pdf_data = create_pdf(st.session_state.messages)
            st.download_button(
                "💾 PDF",
                data=pdf_data,
                file_name="Report.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

# --- MAIN PAGE ---

# 1. HEADER
st.markdown("""
    <div class="main-header">
        <div class="icon">🩺</div>
        <div class="title">MediAssist AI</div>
        <div class="disclaimer">
            I am an AI-powered health assistant designed to analyze symptoms and provide medical information. 
            <br><b>Disclaimer:</b> I am not a doctor. Please consult a medical professional for serious conditions.
            <br><b>Creator:</b><i>Ayush Pritam </i>
        </div>
    </div>
""", unsafe_allow_html=True)

# 2. CHAT HISTORY
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# 3. INPUT AREA
st.write("---")  # Visual Separator
col_mic, col_dummy = st.columns([1, 8])

with col_mic:
    if st.button("🎙️ Speak"):
        voice_text = record_voice()
        if voice_text:
            st.session_state.messages.append({"role": "user", "content": voice_text})
            with st.spinner("Processing voice..."):
                bot_reply = get_bot_response(voice_text)
                st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            safe_rerun()

# TEXT INPUT
prompt = st.chat_input("Type your symptoms here...")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.spinner("Thinking..."):
        bot_reply = get_bot_response(prompt)
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
    safe_rerun()
