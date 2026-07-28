from functools import lru_cache

from groq import Groq

from app.config import settings


@lru_cache(maxsize=1)
def get_groq_client() -> Groq:
    # Explicit timeout so a stalled/misconfigured provider fails fast instead
    # of tying up a request thread indefinitely (the default client timeout
    # is much longer, and this endpoint retries on failure — see
    # app/langgraph/parser.py:call_llm_json).
    return Groq(api_key=settings.groq_api_key, timeout=20.0)


def chat_completion_json(system_prompt: str, user_prompt: str, temperature: float = 0.2) -> str:
    """Runs a single Groq chat completion and returns the raw text content.

    Attempts JSON mode first (constrains the model to emit a JSON object);
    falls back to a plain completion if the model/account doesn't support
    that response format. Callers are responsible for parsing/validating
    the returned text (see app/langgraph/parser.py) — nothing here
    guarantees the text is valid JSON.
    """
    client = get_groq_client()
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    try:
        response = client.chat.completions.create(
            model=settings.groq_model,
            messages=messages,
            temperature=temperature,
            response_format={"type": "json_object"},
        )
    except Exception:
        response = client.chat.completions.create(
            model=settings.groq_model,
            messages=messages,
            temperature=temperature,
        )

    return response.choices[0].message.content or ""
