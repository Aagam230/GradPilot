"""LLM generation for GradPilot using Groq."""
import json
from tenacity import retry, stop_after_attempt, wait_exponential
from ..config import settings


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8))
def generate_text(system: str, user: str, max_tokens: int = 2000, json_mode: bool = False) -> str:
    if settings.llm_provider != "groq":
        raise ValueError(f"Unknown LLM_PROVIDER: {settings.llm_provider}")

    from groq import Groq

    client = Groq(api_key=settings.groq_api_key)
    kwargs = {}
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    resp = client.chat.completions.create(
        model=settings.llm_model,
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        **kwargs,
    )
    return resp.choices[0].message.content or ""


def generate_json(system: str, user: str, max_tokens: int = 2000) -> dict:
    """Ask the LLM for strict JSON and parse it, stripping markdown fences if present."""
    text = generate_text(system, user, max_tokens=max_tokens, json_mode=True).strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"LLM did not return valid JSON: {e}\nRaw: {text[:500]}")
