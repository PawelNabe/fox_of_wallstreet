import streamlit as st
import os
import requests

# 1. Page Configuration (Single call at the top)
st.set_page_config(
    page_title="Fox of Wallstreet Control", 
    layout="wide"
)

# 2. Styling (CSS for a modern 2026 look)
st.markdown("""
    <style>
        .big-title {
            text-align: center;
            font-size: 5.5rem;
            margin-bottom: 20px;
            font-weight: 800;
        }
        .slogan-text {
            font-size: 1.5rem;
            margin: 0;
            white-space: nowrap;
        }
        .stop-slogan { color: #666; font-weight: 400; }
        .start-slogan { color: #2e7d32; font-weight: 700; }
        .logo-and-quote {
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .quote-text {
            font-size: 1.2rem;
            font-weight: bold;
            font-style: italic;
            color: #444;
            margin-top: 10px;
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

# 3. Branding Header
st.markdown('<h1 class="big-title">Fox of Wallstreet</h1>', unsafe_allow_html=True)

logo_path = "Fox Of Wallstreet.png"
if os.path.exists(logo_path):
    col_l, col_c, col_r = st.columns([2, 1, 2], vertical_alignment="center")
    with col_l:
        st.markdown('<div style="text-align: right;"><h3 class="slogan-text stop-slogan">Stop Reinforced Learning</h3></div>', unsafe_allow_html=True)
    with col_c:
        st.markdown('<div class="logo-and-quote">', unsafe_allow_html=True)
        st.image(logo_path, width='content')
        st.markdown('<h3 class="big-title">Become rich or die trying</h3>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col_r:
        st.markdown('<div style="text-align: left;"><h3 class="slogan-text start-slogan">Start Reinforced Earning</h3></div>', unsafe_allow_html=True)
    st.markdown("<hr style='border: 0.5px solid #ddd; margin-top: 20px;'>", unsafe_allow_html=True)
else:
    st.error(f"Logo file '{logo_path}' missing.")

# 4. Backend Configuration

BACKEND_URL = os.getenv('TEST_BACKEND_URL', "https://fow-937802069275.europe-west1.run.app")

# --- Initialize Session State ---
if "trade_logs" not in st.session_state:
    st.session_state["trade_logs"] = ""

# --- Helper Functions ---
def fetch_available_models():
    try:
        r = requests.get(f"{BACKEND_URL}/available-models", timeout=5)
        return r.json().get("models", []) if r.status_code == 200 else []
    except:
        return []

def fetch_model_details(name):
    try:
        r = requests.get(f"{BACKEND_URL}/model-details/{name}", timeout=5)
        return r.json() if r.status_code == 200 else {}
    except:
        return {}

def run_trade(params):
    url = f"{BACKEND_URL}/trade"
    st.session_state["trade_logs"] = ""
    with st.status("Live Trader Active...", expanded=True) as status:
        try:
            with requests.get(url, params={"params": params}, stream=True, timeout=3600) as r:
                log_placeholder = st.empty()
                for line in r.iter_lines():
                    if line:
                        decoded_line = line.decode("utf-8") + "\n"
                        st.session_state["trade_logs"] += decoded_line
                        log_placeholder.code(st.session_state["trade_logs"])
            status.update(label="Trading Session Finished", state="complete")
        except Exception as e:
            st.error(f"Connection failed: {e}")
            status.update(label="Failed", state="error")

# --- UI Layout: Live Trader Solo ---
st.header("🦊 Live Trader Control")

# Model Selection Section
available_foxes = fetch_available_models()

if available_foxes:
    col_sel, col_stats = st.columns([1, 2])
    
    with col_sel:
        selected_model = st.selectbox("Select specialized Fox:", available_foxes)
        trade_args = st.text_input("Trade Arguments", f"--model {selected_model} --bot")
        
    with col_stats:
        # Show model metadata
        details = fetch_model_details(selected_model)
        m_col1, m_col2, m_col3 = st.columns(3)
        m_col1.metric("Sharpe Ratio", details.get("sharpe_ratio", "N/A"))
        m_col2.metric("Profit", f"{details.get('total_profit', '0')}%")
        m_col3.metric("Trained", details.get("training_date", "Unknown"))
    
    if st.button("🚀 Start Reinforced Earning", use_container_width=True):
        run_trade(trade_args)
else:
    st.warning("No valid trading models found in backend artifacts.")

# Persistent Logs
st.subheader("Trading Logs")
st.code(st.session_state["trade_logs"] if st.session_state["trade_logs"] else "Waiting for session...")
