import requests
from prompt_template import PROMPT_TEMPLATE

# Toggle between mock and real LLM
USE_MOCK_LLM = False  # set True for deterministic testing

# Local Ollama server config
OLLAMA_API_URL = "http://localhost:11434"  # default Ollama server
OLLAMA_MODEL_NAME = "gpt-oss:20b"     # replace with your local model name


def generate_response(user_input: str) -> str:
    """
    Sends the user input to local Ollama model and returns the predicted intent:
    'book', 'cancel', 'reschedule', or 'unknown'.
    """
    if USE_MOCK_LLM:
        # Simple deterministic rules for testing
        user_input_lower = user_input.lower()
        if "book" in user_input_lower or "reserve" in user_input_lower:
            return "book"
        elif "cancel" in user_input_lower:
            return "cancel"
        elif "reschedule" in user_input_lower or "change" in user_input_lower:
            return "reschedule"
        else:
            return "unknown"

    # Build structured prompt
    prompt = PROMPT_TEMPLATE.format(user_input=user_input)

    payload = {
        "model": OLLAMA_MODEL_NAME,
        "prompt": prompt,
        "temperature": 0.0,   # deterministic output
        "max_tokens": 10,
        "stream": False       # full response in one JSON
    }

    try:
        response = requests.post(f"{OLLAMA_API_URL}/api/generate", json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()

        # Ollama often returns 'response', fallback to 'text'
        text = (data.get("response") or data.get("text") or "").strip().lower()

        # Normalize to allowed intents
        if text in {"book", "cancel", "reschedule", "unknown"}:
            return text

        # Handle cases like "book\n" or "book flight"
        cleaned = text.splitlines()[0].strip().split()[0]
        if cleaned in {"book", "cancel", "reschedule", "unknown"}:
            return cleaned

        return "unknown"

    except Exception as e:
        print(f"Error calling Ollama model: {e}")
        return "unknown"
