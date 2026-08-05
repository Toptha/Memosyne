"""
engine/generation/response_generator.py

Sends a built prompt to a local Ollama server and returns the
generated answer text. Uses the plain HTTP API (no SDK dependency)
so it stays lightweight and easy to swap models later.
"""

import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "phi3.5"
DEFAULT_TIMEOUT = 120  # generation on CPU/limited VRAM can be slow


def generate_answer(prompt: str, model: str = DEFAULT_MODEL, timeout: int = DEFAULT_TIMEOUT) -> str:
    """
    Sends the prompt to Ollama and returns the raw generated text.
    Raises a clear error if Ollama isn't running, rather than a
    confusing connection traceback.
    """
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.2,  # low temperature - we want grounded, not creative
                },
            },
            timeout=timeout,
        )
        response.raise_for_status()
    except requests.exceptions.ConnectionError:
        raise RuntimeError(
            "Could not reach Ollama at localhost:11434. "
            "Make sure Ollama is running (it usually auto-starts, "
            "or run 'ollama serve' manually)."
        )

    data = response.json()
    return data.get("response", "").strip()


if __name__ == "__main__":
    test_prompt = (
        "Context:\n[1] The refund policy allows returns within 30 days.\n\n"
        "Question: How long do customers have to return an item?\n"
        "Answer (cite sources inline using [1], [2], etc.):"
    )
    print(generate_answer(test_prompt))