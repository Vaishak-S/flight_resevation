# llm_adapter.py
import os
import requests
import json
import re
from typing import Dict
from .prompt_template import INTENT_PROMPT, SLOT_PROMPT

# Toggle between mock and real LLM
USE_MOCK_LLM = False  # set True for deterministic testing

# OpenAI API config (read key from env)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
# Pick a chat-capable model you have access to. Change as needed.
OPENAI_MODEL_NAME = "gpt-4o-mini"  # or "gpt-4o", "gpt-4o-realtime-preview", etc.

REQUEST_TIMEOUT = 30  # seconds


def _call_openai(prompt: str, max_tokens: int = 60, temperature: float = 0.0) -> str:
    """
    Call OpenAI Chat Completions endpoint and return the assistant text.
    Uses the messages format with a single user message containing the prompt.
    """
    if not OPENAI_API_KEY:
        print("OPENAI_API_KEY not set in environment")
        return ""

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": OPENAI_MODEL_NAME,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "n": 1,
    }

    try:
        resp = requests.post(OPENAI_API_URL, headers=headers, json=payload, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        # best-effort extract text
        choices = data.get("choices") or []
        if not choices:
            return ""
        # Chat-style
        msg = choices[0].get("message", {}) if isinstance(choices[0], dict) else {}
        text = msg.get("content") or choices[0].get("text") or ""
        if isinstance(text, list):
            text = " ".join([t.get("content", "") for t in text])
        return text.strip()
    except Exception as e:
        # non-fatal: print for debugging and return empty string to fallback
        print("OpenAI call failed:", e, getattr(e, "response", ""))
        try:
            # attempt to surface useful json if present
            print("response:", resp.text)
        except Exception:
            pass
        return ""


def generate_intent(user_input: str) -> str:
    """
    Use OpenAI to generate a single-word intent: book/cancel/reschedule/unknown.
    Falls back to simple rule-based detection if USE_MOCK_LLM or OpenAI fails.
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

    prompt = INTENT_PROMPT.format(user_input=user_input)
    text = _call_openai(prompt, max_tokens=12, temperature=0.0).lower().strip()

    if not text:
        return "unknown"
    # keep only first token-like word
    text = re.split(r"\s+|\W+", text)[0]
    if text in {"book", "cancel", "reschedule", "unknown"}:
        return text
    return "unknown"


def llm_extract_slots(user_input: str) -> Dict[str, str]:
    """
    Use OpenAI to extract slots in a strict JSON format.
    If OpenAI fails or returns invalid JSON, return empty slots.
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
    text = _call_openai(prompt, max_tokens=300, temperature=0.0)
    if not text:
        return {
            "passenger_name": "",
            "origin": "",
            "destination": "",
            "date": "",
            "time": "",
            "booking_reference": ""
        }

    raw = text.strip()
    # remove code fences/backticks if present
    raw = raw.strip("` \n")
    # find first { and last }
    s = raw.find("{")
    e = raw.rfind("}")
    try:
        if s != -1 and e != -1 and e > s:
            json_text = raw[s:e+1]
            parsed = json.loads(json_text)
            # ensure all keys exist
            for k in ["passenger_name", "origin", "destination", "date", "time", "booking_reference"]:
                parsed.setdefault(k, "")
            # ensure values are strings
            parsed = {k: (str(v) if v is not None else "") for k, v in parsed.items()}
            return parsed
    except Exception as ex:
        print("Failed to parse JSON from OpenAI slot extractor:", ex, "raw:", raw)

    # fallback empty
    return {
        "passenger_name": "",
        "origin": "",
        "destination": "",
        "date": "",
        "time": "",
        "booking_reference": ""
    }
