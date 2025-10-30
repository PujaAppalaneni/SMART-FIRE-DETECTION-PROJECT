import streamlit as st
import os
import tempfile
import cv2
import numpy as np
import time  

from utils.image_utils import detect_fire_smoke  # simplified unified version
from utils.audio_utils import play_alert_sound
from utils.sms_utils import send_whatsapp_alert_with_location
from utils.gps_utils import get_gps_location

# -----------------------------------------------
# Streamlit Config
# -----------------------------------------------
st.set_page_config(page_title="🔥 Smart Fire & Chemical Detection System", layout="centered")

# -----------------------------------------------
# Custom CSS for Full-Page Gradient + Smoke Overlay
# -----------------------------------------------
st.markdown(
    """
    <style>
    html, body, [data-testid="stAppViewContainer"], [data-testid="stAppViewRoot"], [data-testid="stSidebar"], [data-testid="stVerticalBlock"] {
        height: 100%;
        min-height: 100vh;
        margin: 0;
        padding: 0;
    }

    [data-testid="stAppViewContainer"] {
        background: linear-gradient(-45deg, #ff512f, #ff9966, #ff5f6d, #ffc371);
        background-size: 400% 400%;
        animation: fireGlow 8s ease infinite;
        position: relative;
        overflow: hidden;
    }

    [data-testid="stAppViewContainer"]::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: url("smoke.gif") ;
        background-repeat:repeat;
        background-size: 150px 150px;
        background-attachment: fixed;
        opacity: 0.15;
        mix-blend-mode: screen;
        animation: smokeMove 30s linear infinite;
        z-index: 0;
    }

    @keyframes fireGlow {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    @keyframes smokeMove {
        from { background-position: 0 0; }
        to { background-position: 1000px 1000px; }
    }

    [data-testid="stAppViewContainer"] > div {
        position: relative;
        z-index: 1;
    }

    .custom-upload-box {
        text-align: center;
        margin: 4rem auto;
        padding: 25px 35px;
        border-radius: 20px;
        background: rgba(0, 0, 0, 0.45);
        backdrop-filter: blur(6px);
        box-shadow: 0 0 30px 10px rgba(255, 143, 0, 0.4);
        animation: pulseGlow 3s ease-in-out infinite;
        width: fit-content;
    }

    @keyframes pulseGlow {
        0%, 100% { box-shadow: 0 0 30px 10px rgba(255,143,0,0.5); }
        50% { box-shadow: 0 0 50px 20px rgba(255,174,0,0.7); }
    }

    .custom-upload-text {
        font-size: 1.7rem;
        font-weight: 700;
        color: #fff6dc;
        text-shadow:
            0 0 5px #ffae00,
            0 0 15px #ffae00,
            0 0 25px #ffa600,
            0 0 45px #ff8a00;
        display: block;
        margin-bottom: 12px;
    }

    .custom-upload-subtext {
        font-size: 1.1rem;
        font-weight: 500;
        color: #ffd88a;
        text-shadow: 0 0 5px #aa7a00;
    }

    h1, h2, h3, p, label {
        color: #fff !important;
        font-family: "Poppins", sans-serif;
        text-shadow: 2px 2px 8px rgba(0,0,0,0.7);
    }
    </style>

    <div class="custom-upload-box">
        <span class="custom-upload-text">🔥 Upload Image or Use Webcam to Detect Fire / Smoke 🔥</span>
    </div>
    """,
    unsafe_allow_html=True
)

# -----------------------------------------------
# Upload or Webcam Mode
# -----------------------------------------------
uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])
use_webcam = st.checkbox("Use CC camera for Live Detection")

# -----------------------------------------------
# Webcam Mode
# -----------------------------------------------
if use_webcam:
    cap = cv2.VideoCapture(0)
    frame_placeholder = st.empty()

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                st.error("Cannot access webcam")
                break

            # Detect fire/smoke
            result_img, label, confidence = detect_fire_smoke(frame)

            # Display combined image
            frame_placeholder.image(cv2.cvtColor(result_img, cv2.COLOR_BGR2RGB), use_column_width=True)

            # Alert if danger detected
            if label == "Fire/Smoke":
                st.warning(f"🚨 Fire/Smoke Detected ({confidence*100:.1f}%)")
                play_alert_sound("assets/fire_alert.mp3")
                latitude, longitude = get_gps_location(port='COM4')
                if latitude and longitude:
                    send_whatsapp_alert_with_location(latitude, longitude)
                    st.success(f"📍 Location sent: {latitude}, {longitude}")
                else:
                    send_whatsapp_alert_with_location(17.5207, 78.3680)

            time.sleep(0.1)

    finally:
        cap.release()
        st.write("Webcam stopped.")

# -----------------------------------------------
# Uploaded Image Mode
# -----------------------------------------------
elif uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
        tmp_file.write(uploaded_file.read())
        image_path = tmp_file.name

    st.subheader("Detection Result")
    try:
        result_img, label, confidence = detect_fire_smoke(cv2.imread(image_path))

        st.image(cv2.cvtColor(result_img, cv2.COLOR_BGR2RGB),
                 caption=f"{label} ({confidence*100:.1f}%)",
                 use_container_width=True)

        if label == "Fire/Smoke":
            st.warning("🚨 Danger Detected! Playing alert...")
            play_alert_sound("assets/fire_alert.mp3")
            play_alert_sound("assets/emergency_exit_instructions.mp3")
            latitude, longitude = get_gps_location(port='COM4')
            if latitude and longitude:
                send_whatsapp_alert_with_location(latitude, longitude)
                st.success(f"📍 Location sent: {latitude}, {longitude}")
            else:
                send_whatsapp_alert_with_location(17.5207, 78.3680)
        else:
            st.success("✅ No danger detected.")
    except Exception as e:
        st.error(f"❌ Error: {e}")
