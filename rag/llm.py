"""LLM client. Works with Groq (cloud) or Ollama (offline) - both speak the
OpenAI chat-completions format, so one function handles both.

Groq's free tier allows a limited number of tokens per minute. When that limit
is hit (HTTP 429), we wait the time Groq suggests and retry automatically."""
import re
import time

from config import GROQ_API_KEY, GROQ_MODEL, GROQ_URL, LLM_PROVIDER, OLLAMA_MODEL, OLLAMA_URL

MAX_RETRIES = 4          # attempts after a rate-limit error
MAX_WAIT_SECONDS = 30    # never wait longer than this per retry


class LLMError(Exception):
    pass


def provider_info() -> dict:
    if LLM_PROVIDER == "ollama":
        return {"provider": "ollama", "model": OLLAMA_MODEL, "configured": True}
    return {"provider": "groq", "model": GROQ_MODEL, "configured": bool(GROQ_API_KEY)}


def retry_after(resp) -> float:
    """Seconds to wait before retrying, from the Retry-After header or Groq's
    'Please try again in 7.89s' message. Defaults to 10 seconds."""
    header = resp.headers.get("retry-after")
    if header:
        try:
            return min(float(header) + 0.5, MAX_WAIT_SECONDS)
        except ValueError:
            pass
    m = re.search(r"try again in (?:(\d+)m)?([\d.]+)s", resp.text)
    if m:
        return min(int(m.group(1) or 0) * 60 + float(m.group(2)) + 0.5, MAX_WAIT_SECONDS)
    return 10.0


def ask_llm(system_prompt: str, user_prompt: str, temperature: float = 0.1, max_tokens: int = 1500) -> str:
    if LLM_PROVIDER == "ollama":
        url, model, headers = OLLAMA_URL, OLLAMA_MODEL, {}
    else:
        if not GROQ_API_KEY:
            raise LLMError("GROQ_API_KEY is not set. Add it to the .env file (see .env.example).")
        url, model, headers = GROQ_URL, GROQ_MODEL, {"Authorization": f"Bearer {GROQ_API_KEY}"}

    import httpx

    body = {
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }
    for attempt in range(MAX_RETRIES + 1):
        try:
            resp = httpx.post(url, headers=headers, json=body, timeout=180)
        except httpx.HTTPError as e:
            where = "Ollama (is `ollama serve` running?)" if LLM_PROVIDER == "ollama" else "Groq"
            raise LLMError(f"Could not reach {where}: {e}") from e
        if resp.status_code == 429 and attempt < MAX_RETRIES:
            time.sleep(retry_after(resp))  # free-tier rate limit: wait, then try again
            continue
        if resp.status_code == 429:
            raise LLMError("The AI service is busy (free-tier rate limit). Wait one minute and try again.")
        if resp.status_code != 200:
            raise LLMError(f"{LLM_PROVIDER.title()} error {resp.status_code}: {resp.text[:300]}")
        return (resp.json()["choices"][0]["message"].get("content") or "").strip()
    raise LLMError("The AI service did not respond. Please try again.")
