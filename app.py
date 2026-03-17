import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Algo Trading Console", layout="wide")
st.title("🤖 System Control Center")

def api_call(method, endpoint):
    try:
        if method == "GET":
            return requests.get(f"{API_URL}{endpoint}").json()
        return requests.post(f"{API_URL}{endpoint}").json()
    except:
        return None

@st.fragment(run_every="2s")
def render_log_window(script_id):
    data = api_call("GET", f"/logs/{script_id}?lines=15")
    if data:
        st.code(data.get("logs", ""), language="text")

# Main Interface
status_data = api_call("GET", "/status")

if status_data:
    cols = st.columns(3)
    for i, (name, status) in enumerate(status_data.items()):
        with cols[i]:
            with st.container(border=True):
                st.subheader(name.replace("_", " ").title())
                
                # Action Buttons
                c1, c2 = st.columns(2)
                with c1:
                    if status == "Running":
                        if st.button(f"Stop", key=f"stop_{name}", use_container_width=True):
                            api_call("POST", f"/stop/{name}")
                            st.rerun()
                    else:
                        if st.button(f"Start", key=f"start_{name}", use_container_width=True):
                            api_call("POST", f"/start/{name}")
                            st.rerun()
                
                with c2:
                    if st.button(f"Clear Logs", key=f"clear_{name}", use_container_width=True):
                        api_call("POST", f"/clear_logs/{name}")
                        # No rerun needed; fragment will update log view in 2s
                
                st.write(f"**Status:** {status}")
                st.write("---")
                render_log_window(name)
else:
    st.error("Backend Offline. Please start backend.py first.")

if st.button("Global Refresh"):
    st.rerun()