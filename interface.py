import streamlit as st
import os
import requests

# 1. Page Configuration
st.set_page_config(
    page_title="Fox of Wallstreet",
    layout="wide" # Wide layout gives the horizontal bar space
)

# 2. Styling (CSS for a modern 2026 look)
st.markdown("""
    <style>
        /* Big Title Styling */
        .big-title {
            text-align: center;
            font-size: 5.5rem;
            margin-bottom: 20px;
            font-weight: 800;
        }

        /* The Main Container for Slogans + Logo + Quote */
        .brand-container {
            display: flex;
            justify-content: center; /* Center horizontally */
            align-items: center; /* Center vertically */
            gap: 20px; /* Space between elements */
            margin-top: 10px;
        }

        /* Standard Slogan Styling */
        .slogan-text {
            font-size: 1.5rem;
            margin: 0;
            white-space: nowrap; /* Keep on one line */
        }

        /* Left Slogan (Muted) */
        .stop-slogan {
            color: #666;
            font-weight: 400;
        }

        /* Right Slogan (Bold Green) */
        .start-slogan {
            color: #2e7d32;
            font-weight: 700;
        }

        /* The central unit: Image + Quote */
        .logo-and-quote {
            display: flex;
            flex-direction: column; /* Stack image over quote */
            align-items: center; /* Center them relative to each other */
        }

        /* The Quote below the picture */
        .quote-text {
            font-size: 1.1rem;
            font-weight: bold;
            font-style: italic;
            color: #444;
            margin-top: 5px; /* Tiny space under image */
            text-align: center;
            width: auto; /* Width will match content */
            max-width: fit-content; /* Key to match image width */
        }
    </style>
""", unsafe_allow_html=True)

# 3. Render the Header (Main Title)
st.markdown('<h1 class="big-title">Fox of Wallstreet</h1>', unsafe_allow_html=True)

# 4. Render the Branding Bar using Flexbox
logo_path = "Fox Of Wallstreet.png"
if os.path.exists(logo_path):
    # Using columns for the main horizontal alignment, but CSS for internal alignment
    col1, col2, col3 = st.columns([2, 1, 2], vertical_alignment="center")

    with col1:
        st.markdown("""
            <div style="text-align: right;">
                <h3 class="slogan-text stop-slogan">Stop Reinforced Learning</h3>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        # Wrap image and quote in a centering div
        st.markdown('<div class="logo-and-quote">', unsafe_allow_html=True)
        # Using 2026-compliant width='content' so the logo stays its natural size
        st.image(logo_path, width='content')
        # The quote right below the picture
        # st.markdown('<p class="quote-text">Become rich or die trying</p>', unsafe_allow_html=True)
        st.markdown('<h3 class="big-title">Become rich or die trying</h1>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown("""
            <div style="text-align: left;">
                <h3 class="slogan-text start-slogan">Start Reinforced Earning</h3>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='border: 0.5px solid #ddd; margin-top: 20px;'>", unsafe_allow_html=True)

else:
    st.error(f"Logo file '{logo_path}' missing.")

# Set this to your mapped Docker port (e.g., 8081 or 8080)
BACKEND_URL = "http://localhost:8081" 
BACKEND_URL = "https://fow-qrmnqxuopa-ew.a.run.app"
BACKEND_URL = "https://fow-937802069275.europe-west1.run.app"
st.set_page_config(page_title="Fox of Wallstreet Control", layout="wide")
st.title("🦊 Fox of Wallstreet: Task Control")

# --- Initialize Session State for persistent logs ---
for task in ["data", "train", "trade"]:
    if f"{task}_logs" not in st.session_state:
        st.session_state[f"{task}_logs"] = ""

def run_task(endpoint, display_name, params):
    """Calls FastAPI, streams logs, and saves them to session state."""
    url = f"{BACKEND_URL}/{endpoint}"
    
    # Clear previous logs for this specific task before starting
    st.session_state[f"{endpoint}_logs"] = ""
    
    with st.status(f"Running {display_name}...", expanded=True) as status:
        try:
            with requests.get(url, params={"params": params}, stream=True, timeout=3600) as r:
                if r.status_code != 200:
                    st.error(f"Backend Error: {r.status_code}")
                    return

                # Create a placeholder to show live updates
                log_placeholder = st.empty()
                
                for line in r.iter_lines():
                    if line:
                        decoded_line = line.decode("utf-8") + "\n"
                        # Append to session state so it persists
                        st.session_state[f"{endpoint}_logs"] += decoded_line
                        # Update the live UI
                        log_placeholder.code(st.session_state[f"{endpoint}_logs"])
                
            status.update(label=f"{display_name} Finished", state="complete", expanded=False)
        except Exception as e:
            st.error(f"Connection failed: {e}")
            status.update(label="Failed", state="error")

# --- UI Layout ---
col1, col2, col3 = st.columns(3)

with col1:
    st.header("1. Data Engine")
    data_params = st.text_input("Data Args", "", key="data_input")
    if st.button("Start Data Sync", use_container_width=True):
        run_task("data", "Data Engine", data_params)
    # Display persistent logs from session state
    st.code(st.session_state["data_logs"] if st.session_state["data_logs"] else "No logs yet.")

with col2:
    st.header("2. Training")
    train_params = st.text_input("Train Args", "", key="train_input")
    if st.button("Start Training", use_container_width=True):
        run_task("train", "Model Trainer", train_params)
    st.code(st.session_state["train_logs"] if st.session_state["train_logs"] else "No logs yet.")

with col3:
    st.header("3. Live Trader")
    trade_params = st.text_input("Trade Args", "--bot", key="trade_input")
    if st.button("Start Live Trading", use_container_width=True):
        run_task("trade", "Live Trader", trade_params)
    st.code(st.session_state["trade_logs"] if st.session_state["trade_logs"] else "No logs yet.")
