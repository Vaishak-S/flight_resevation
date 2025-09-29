import streamlit as st
from mcp_server.mcp import handle_message  # import your MCP handler directly

# --- Page setup ---
st.set_page_config(page_title="Flight Reservation Assistant", page_icon="✈️", layout="centered")
st.title("Flight Reservation Assistant")

# --- Session state defaults ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # list of {"role": "user"|"assistant", "content": str, "tool_output": dict}
if "loading" not in st.session_state:
    st.session_state.loading = False
if "last_user_input" not in st.session_state:
    st.session_state.last_user_input = ""

# --- Helpers ---
def post_to_mcp(message: str):
    """Call MCP handler directly and return (assistant_text, tool_output)."""
    try:
        # handle_message should return (assistant_text: str, tool_output: dict)
        assistant_text, tool_output = handle_message(message)
        return assistant_text, tool_output
    except Exception as e:
        return f"Error in MCP handler: {str(e)}", {}

def render_tool_output(tool_output):
    """Render booking cards and return a mapping of booking references shown (useful for actions)."""
    shown_refs = []
    bookings = tool_output.get("bookings", []) or tool_output.get("booking", []) or []
    if isinstance(bookings, dict):
        bookings = [bookings]
    for booking in bookings:
        reference = booking.get("reference") or booking.get("booking_reference") or booking.get("bookingRef")
        status = booking.get("status", "UNKNOWN")
        flight = booking.get("flight", f"{booking.get('from','?')} -> {booking.get('to','?')}")
        date = booking.get("date", booking.get("travel_date", "N/A"))
        passenger = booking.get("passenger") or booking.get("passenger_name") or "N/A"

        status_color = "#d4edda" if status.upper() == "CONFIRMED" else "#f8d7da"
        with st.container():
            st.markdown(
                f"""
                <div style='background-color:{status_color};padding:12px;border-radius:8px;margin-bottom:8px'>
                    <b>Booking Reference:</b> {reference}<br>
                    <b>Status:</b> {status}<br>
                    <b>Flight:</b> {flight}<br>
                    <b>Date:</b> {date}<br>
                    <b>Passenger:</b> {passenger}<br>
                </div>
                """,
                unsafe_allow_html=True,
            )
            col1, col2 = st.columns([1, 1])
            with col1:
                cancel_key = f"cancel_{reference}"
                if st.button("Cancel", key=cancel_key):
                    st.session_state.chat_history.append({"role": "user", "content": f"Cancel booking {reference}"})
                    st.experimental_rerun()
            with col2:
                resch_key = f"reschedule_{reference}"
                if st.button("Reschedule", key=resch_key):
                    st.session_state.chat_history.append({"role": "user", "content": f"Reschedule booking {reference} to <new-date> <new-time>"})
                    st.experimental_rerun()
        shown_refs.append(reference)
    return shown_refs

def render_chat():
    """Render chat history stored in session_state."""
    for msg in st.session_state.chat_history:
        role = msg.get("role")
        content = msg.get("content", "")
        if role == "user":
            try:
                st.chat_message("user").write(content)
            except Exception:
                st.markdown(f"**You:** {content}")
        else:
            try:
                st.chat_message("assistant").write(content)
            except Exception:
                st.markdown(f"<div style='background-color:#f0f8ff;padding:8px;border-radius:6px'><b>Assistant:</b> {content}</div>", unsafe_allow_html=True)

        if role == "assistant" and msg.get("tool_output"):
            render_tool_output(msg["tool_output"])

# --- UI: input area ---
with st.form(key="input_form", clear_on_submit=True):
    user_input = st.text_input("Type your message", value="", key="user_input")
    submit = st.form_submit_button("Send")

if submit and user_input:
    st.session_state.last_user_input = user_input
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    st.session_state.loading = True

    with st.spinner("Assistant is typing..."):
        assistant_text, tool_output = post_to_mcp(user_input)
        st.session_state.chat_history.append({"role": "assistant", "content": assistant_text, "tool_output": tool_output})
    st.session_state.loading = False
    st.experimental_rerun()

# --- Show chat ---
render_chat()

if st.session_state.loading:
    st.info("Waiting for assistant...")
