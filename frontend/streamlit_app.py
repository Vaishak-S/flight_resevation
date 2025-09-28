
import streamlit as st
import requests
from datetime import datetime

# MCP server URL (adjust if needed)
MCP_SERVER_URL = "http://127.0.0.1:5000"  # change if MCP runs on another port
MCP_ENDPOINT = "/handle-message"           # optional if you have HTTP wrapper

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state["messages"] = []  # each item: {"role": "user"/"assistant", "text": str, "tool_output": dict}

st.set_page_config(page_title="Flight Reservation Chat", layout="wide")

st.title("✈️ Flight Reservation Assistant")

# Sidebar instructions
with st.sidebar:
    st.markdown("### Instructions")
    st.markdown("""
    - Type your message below and press **Send**
    - Booking, cancellation, and rescheduling are supported
    - Click **Cancel** or **Reschedule** buttons on previous bookings to prefill the form
    """)

# --- Chat message stream ---
chat_container = st.container()

# --- Input box ---
user_input = st.text_input("Your message:", key="input_text")
send_button = st.button("Send")

def send_to_mcp(message: str):
    """
    Sends user message to MCP server (via HTTP) and returns JSON response
    {assistant_text, tool_output, intent, slots}
    """
    try:
        resp = requests.post(f"{MCP_SERVER_URL}{MCP_ENDPOINT}", json={"user_text": message}, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"assistant_text": f"Error contacting MCP server: {e}", "tool_output": {}, "intent": "error", "slots": {}}

def render_booking_card(booking: dict):
    """
    Display booking details as a card with status and action buttons
    """
    status = booking.get("status", "UNKNOWN")
    color = {"CONFIRMED":"#d4edda", "CANCELLED":"#f8d7da"}.get(status, "#fff3cd")
    st.markdown(f"""
        <div style="background-color:{color}; padding:10px; border-radius:10px; margin-bottom:10px;">
            <b>Passenger:</b> {booking.get('passenger_name', '')}<br>
            <b>Flight:</b> {booking.get('origin', '')} ➔ {booking.get('destination', '')}<br>
            <b>Date/Time:</b> {booking.get('date','')} {booking.get('time','')}<br>
            <b>Reference:</b> {booking.get('booking_reference','')}<br>
            <b>Status:</b> {status}
        </div>
    """, unsafe_allow_html=True)

# --- Handle send button ---
if send_button and user_input.strip():
    # Append user message to chat
    st.session_state.messages.append({"role":"user","text":user_input,"tool_output":{}})
    
    # Show loading spinner
    with st.spinner("Assistant is typing..."):
        mcp_resp = send_to_mcp(user_input)
    
    # Append assistant message
    st.session_state.messages.append({
        "role":"assistant",
        "text": mcp_resp.get("assistant_text",""),
        "tool_output": mcp_resp.get("tool_output",{})
    })
    
    # Clear input box
    st.session_state.input_text = ""

# --- Render chat messages ---
with chat_container:
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"**You:** {msg['text']}")
        else:
            st.markdown(f"**Assistant:** {msg['text']}")
            # Render booking cards if present
            tool_out = msg.get("tool_output", {})
            if isinstance(tool_out, dict) and "booking_reference" in tool_out:
                render_booking_card(tool_out)
                # Add action buttons for convenience
                col1, col2 = st.columns([1,1])
                with col1:
                    if st.button("Cancel", key=f"cancel_{tool_out['booking_reference']}"):
                        prefill = f"Please cancel my booking {tool_out['booking_reference']}"
                        st.session_state.input_text = prefill
                with col2:
                    if st.button("Reschedule", key=f"reschedule_{tool_out['booking_reference']}"):
                        prefill = f"Reschedule {tool_out['booking_reference']} to YYYY-MM-DD HH:MM"
                        st.session_state.input_text = prefill
