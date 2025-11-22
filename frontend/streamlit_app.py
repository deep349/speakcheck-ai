import os, sys
# ensure the project root (one level above frontend/) is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


# streamlit_app.py
import os
import streamlit as st
from dotenv import load_dotenv
from backend.scoring_engine import analyze

# Load environment variables
load_dotenv()

st.set_page_config(page_title="SpeakCheck AI", layout="wide")
st.title(" SpeakCheck AI")
st.markdown(
    """
    <h3 style='margin-top:-10px; color:#555; font-weight:400;'>
        AI-powered clarity for every student voice
    </h3>
    <p style='font-size:14px; color:#888; margin-top:-8px;'>
        Developed by <strong>Deepanshu Vashishth</strong>
    </p>
    """,
    unsafe_allow_html=True
)

# ---------------- SIDEBAR ----------------
st.sidebar.header("Settings")
api_key = st.sidebar.text_input("Gemini API Key (or set GOOGLE_API_KEY in .env)", type="password")

if not api_key:
    api_key = os.getenv("GOOGLE_API_KEY")

# ---------------- MAIN INPUT ----------------
st.markdown("Paste the transcript and set the audio duration (seconds).")

transcript = st.text_area("Transcript", height=240, placeholder="Hello, my name is ...")
duration = st.number_input("Audio duration (seconds)", min_value=1.0, value=60.0)

# ---------------- BUTTON ACTION ----------------
if st.button("Analyze"):
    if not transcript.strip():
        st.warning("Please paste a transcript.")
    elif not api_key:
        st.warning("API key missing. Provide a Gemini API key or set GOOGLE_API_KEY in .env.")
    else:
        with st.spinner("Analyzing..."):
            result = analyze(transcript, float(duration), api_key)

        # Display Final Score
        st.metric("Overall Score", f"{result['final_score']:.1f} / 100")

        # ---------------- BREAKDOWN ----------------
        st.subheader("Detailed Breakdown")
        for k, v in result["breakdown"].items():
            st.write(f"### {k}")

            # If an item has a score, display it
            if "score" in v:
                st.write(f"**Score:** {v['score']:.2f}")

            # Show the JSON evidence
            st.json(v)
        # ---------------- SIGNALS (DEBUG INFO) ----------------
        st.subheader("Signals (Debug Info)")
        st.json(result["signals"])
