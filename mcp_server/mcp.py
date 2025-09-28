# mcp.py
import re
import json
from datetime import datetime
from typing import Dict, Any

from llm_adapter import generate_intent, llm_extract_slots, USE_MOCK_LLM
from tools import book_tool, cancel_tool, reschedule_tool

# Use LLM to extract slots if regex heuristics fail
USE_LLM_FOR_SLOTS = not USE_MOCK_LLM

# regex heuristics for common slot patterns
DATE_RE = re.compile(r"(?P<date>\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4}|\d{1,2}-\d{1,2}-\d{4})")
TIME_RE = re.compile(r"(?P<time>\d{1,2}:\d{2}(?::\d{2})?\s*(?:am|pm)?)", re.I)
IATA_RE = re.compile(r"\b([A-Z]{3})\b")
BK_REF_RE = re.compile(r"\b(BK[-_]?[\w\d]+)\b", re.I)
FROM_TO_RE = re.compile(r"from\s+([A-Za-z0-9\s,]+?)\s+(?:to|->|-)\s+([A-Za-z0-9\s,]+)", re.I)
NAME_RE = re.compile(r"(?:name is|this is|i am|passenger is)\s+([A-Z][a-zA-Z\s]{1,40})", re.I)

def _normalize_date(found: str) -> str:
    if not found:
        return ""
    found = found.strip()
    if re.match(r"\d{4}-\d{2}-\d{2}", found):
        return found
    parts = re.split(r"[-/]", found)
    if len(parts) == 3:
        if len(parts[0]) == 4:
            y,m,d = parts
        else:
            d,m,y = parts
        try:
            dt = datetime(int(y), int(m), int(d))
            return dt.strftime("%Y-%m-%d")
        except Exception:
            return found
    return found

def _normalize_time(found: str) -> str:
    if not found:
        return ""
    try:
        t = found.strip().lower()
        t = re.sub(r"\s+", "", t)
        if re.search(r"(am|pm)$", t):
            dt = datetime.strptime(t, "%I:%M%p")
            return dt.strftime("%H:%M")
        if re.match(r"\d{1,2}:\d{2}(:\d{2})?", t):
            hh, mm = t.split(":")[:2]
            return f"{int(hh):02d}:{int(mm):02d}"
    except Exception:
        return found
    return found

def regex_slot_extraction(user_input: str) -> Dict[str,str]:
    ui = user_input.strip()
    slots = {"passenger_name":"", "origin":"", "destination":"", "date":"", "time":"", "booking_reference":""}

    m = BK_REF_RE.search(ui)
    if m:
        slots["booking_reference"] = m.group(1)

    m = NAME_RE.search(ui)
    if m:
        slots["passenger_name"] = m.group(1).strip()

    m = DATE_RE.search(ui)
    if m:
        slots["date"] = _normalize_date(m.group("date"))

    m = TIME_RE.search(ui)
    if m:
        slots["time"] = _normalize_time(m.group("time"))

    codes = IATA_RE.findall(ui)
    if len(codes) >= 2:
        slots["origin"] = codes[0]
        slots["destination"] = codes[1]
    else:
        m = FROM_TO_RE.search(ui)
        if m:
            origin = m.group(1).strip().split(",")[0].strip()
            dest = m.group(2).strip().split(",")[0].strip()
            slots["origin"] = origin
            slots["destination"] = dest

    return slots

def extract_slots(user_input: str) -> Dict[str,str]:
    slots = regex_slot_extraction(user_input)
    # consider meaningful if any slot (except booking_reference) present or ref present
    meaningful = any(v for k,v in slots.items() if k != "booking_reference") or slots["booking_reference"]
    if meaningful:
        return slots
    if USE_LLM_FOR_SLOTS:
        return llm_extract_slots(user_input)
    return slots

def handle_message(user_text: str) -> Dict[str, Any]:
    intent = generate_intent(user_text)
    slots = extract_slots(user_text)
    assistant_text = ""
    tool_output = {}

    if intent == "book":
        missing = [k for k in ["passenger_name","origin","destination","date","time"] if not slots.get(k)]
        if missing:
            assistant_text = ("I detected you want to book a flight, but I need more info: " +
                              ", ".join(missing) +
                              ". Example: 'Book flight for Vaishak from BOM to BLR on 2025-10-10 at 10:30'.")
            return {"assistant_text": assistant_text, "tool_output": tool_output, "intent": intent, "slots": slots}

        payload = {
            "passenger_name": slots.get("passenger_name"),
            "origin": slots.get("origin"),
            "destination": slots.get("destination"),
            "date": slots.get("date"),
            "time": slots.get("time"),
            "flight_class": "Economy"
        }
        tool_output = book_tool(payload)
        if "error" in tool_output:
            assistant_text = f"Failed to create booking: {tool_output['error']}"
        else:
            assistant_text = (f"Booking confirmed. Reference: {tool_output.get('booking_reference')}. "
                              f"{tool_output.get('origin')} -> {tool_output.get('destination')} on {tool_output.get('date')} at {tool_output.get('time')}.")
        return {"assistant_text": assistant_text, "tool_output": tool_output, "intent": intent, "slots": slots}

    elif intent == "cancel":
        br = slots.get("booking_reference")
        if not br:
            assistant_text = "I detected a cancel intent but could not find a booking reference. Please provide your booking reference (e.g., BK-20250928-xxxx)."
            return {"assistant_text": assistant_text, "tool_output": tool_output, "intent": intent, "slots": slots}
        tool_output = cancel_tool(br)
        if "error" in tool_output:
            assistant_text = f"Failed to cancel booking: {tool_output['error']}"
        else:
            assistant_text = f"Booking {tool_output.get('booking_reference')} has been cancelled."
        return {"assistant_text": assistant_text, "tool_output": tool_output, "intent": intent, "slots": slots}

    elif intent == "reschedule":
        br = slots.get("booking_reference")
        if not br:
            assistant_text = "I detected a reschedule request but could not find a booking reference. Please give me your booking reference and the new date/time."
            return {"assistant_text": assistant_text, "tool_output": tool_output, "intent": intent, "slots": slots}
        if not slots.get("date") or not slots.get("time"):
            assistant_text = "Please provide the new date and time for your booking (YYYY-MM-DD and HH:MM)."
            return {"assistant_text": assistant_text, "tool_output": tool_output, "intent": intent, "slots": slots}

        payload = {"booking_reference": br, "new_date": slots.get("date"), "new_time": slots.get("time")}
        tool_output = reschedule_tool(payload)
        if "error" in tool_output:
            assistant_text = f"Failed to reschedule booking: {tool_output['error']}"
        else:
            assistant_text = (f"Booking {tool_output.get('booking_reference')} rescheduled to {tool_output.get('date')} at {tool_output.get('time')}.")
        return {"assistant_text": assistant_text, "tool_output": tool_output, "intent": intent, "slots": slots}

    else:
        assistant_text = "Sorry — I didn't understand that. I can help with booking, cancelling, or rescheduling flights."
        return {"assistant_text": assistant_text, "tool_output": tool_output, "intent": intent, "slots": slots}


if __name__ == "__main__":
    print("MCP interactive test. Type messages (quit to exit).")
    while True:
        try:
            txt = input(">> ").strip()
            if not txt or txt.lower() in {"quit", "exit"}:
                break
            out = handle_message(txt)
            print(json.dumps(out, indent=2, default=str))
        except KeyboardInterrupt:
            break
