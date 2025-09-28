# llm_adapter.py
import requests
import json
import re
from typing import Dict
from prompt_template import INTENT_PROMPT, SLOT_PROMPT

# Toggle between mock and real LLM
USE_MOCK_LLM = False  # set True for deterministic testing

# Local Ollama server config (adjust if necessary)
OLLAMA_API_URL = "http://localhost:11434"  # default Ollama server
# OLLAMA_MODEL_NAME = "gpt-oss:20b"          # change to your model if different
OLLAMA_MODEL_NAME = "deepseek-v3.1:671b-cloud"          # change to your model if different


REQUEST_TIMEOUT = 30  # seconds


def _call_ollama(prompt: str, max_tokens: int = 60, temperature: float = 0.0) -> str:
    """
    Call Ollama generate endpoint synchronously and return text part (best-effort).
    """
    payload = {
        "model": OLLAMA_MODEL_NAME,
        "prompt": prompt,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False
    }
    try:
        r = requests.post(f"{OLLAMA_API_URL}/api/generate", json=payload, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        data = r.json()
        # Ollama might return {"response": "..."} or {"text": "..."} depending on version
        text = (data.get("response") or data.get("text") or "")
        if isinstance(text, list):  # some versions return list; join
            text = " ".join([t.get("content", "") for t in text])
        return text.strip()
    except Exception as e:
        print("Ollama call failed:", e)
        return ""


def generate_intent(user_input: str) -> str:
    """
    Use Ollama to generate a single-word intent: book/cancel/reschedule/unknown.
    Falls back to simple rule-based detection if USE_MOCK_LLM or Ollama fails.
    """
    if USE_MOCK_LLM:
        ui = user_input.lower()
        if "book" in ui or "reserve" in ui:
            return "book"
        if "cancel" in ui:
            return "cancel"
        if "reschedule" in ui or "change" in ui:
            return "reschedule"
        return "unknown"

    # Call Ollama with constrained prompt
    prompt = INTENT_PROMPT.format(user_input=user_input)
    text = _call_ollama(prompt, max_tokens=10, temperature=0.0).lower().strip()

    # Clean the response: keep only first token
    if not text:
        return "unknown"
    # remove non-word characters
    text = re.split(r"\s+|\W+", text)[0]
    if text in {"book", "cancel", "reschedule", "unknown"}:
        return text
    return "unknown"


def llm_extract_slots(user_input: str) -> Dict[str, str]:
    """
    Use Ollama to extract slots in a strict JSON format.
    If Ollama fails or returns invalid JSON, return empty slots.
    """
    if USE_MOCK_LLM:
        return {
            "passenger_name": "",
            "origin": "",
            "destination": "",
            "date": "",
            "time": "",
            "booking_reference": ""
        }

    prompt = SLOT_PROMPT.format(user_input=user_input)
    text = _call_ollama(prompt, max_tokens=200, temperature=0.0)
    if not text:
        return {
            "passenger_name": "",
            "origin": "",
            "destination": "",
            "date": "",
            "time": "",
            "booking_reference": ""
        }

    # Clean and parse JSON substring
    raw = text.strip()
    # Remove leading/trailing code fences/backticks if present
    raw = raw.strip("` \n")
    # Find first { and last }
    s = raw.find("{")
    e = raw.rfind("}")
    try:
        if s != -1 and e != -1 and e > s:
            json_text = raw[s:e+1]
            parsed = json.loads(json_text)
            # ensure all keys exist
            for k in ["passenger_name", "origin", "destination", "date", "time", "booking_reference"]:
                parsed.setdefault(k, "")
            return parsed
    except Exception as ex:
        print("Failed to parse JSON from Ollama slot extractor:", ex, "raw:", raw)
    # fallback empty
    return {
        "passenger_name": "",
        "origin": "",
        "destination": "",
        "date": "",
        "time": "",
        "booking_reference": ""
    }
