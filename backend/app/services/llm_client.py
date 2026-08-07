"""Provider-agnostic LLM text generation. Swap providers via env vars."""
import json
from tenacity import retry, stop_after_attempt, wait_exponential
from ..config import settings

# Deterministic by default: this tool makes evidence-grounded classification calls (Reach/Target/
# Likely, ratings) that should be consistent for the same student+program, not vary run to run.
DEFAULT_TEMPERATURE = 0.0


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8))
def generate_text(
    system: str, user: str, max_tokens: int = 2000, json_mode: bool = False, temperature: float = DEFAULT_TEMPERATURE
) -> str:
    if settings.llm_provider == "groq":
        return _generate_groq(system, user, max_tokens, json_mode, temperature)
    if settings.llm_provider == "anthropic":
        return _generate_anthropic(system, user, max_tokens, temperature)
    elif settings.llm_provider == "openai":
        return _generate_openai(system, user, max_tokens, json_mode, temperature)
    raise ValueError(f"Unknown LLM_PROVIDER: {settings.llm_provider}")



def _generate_groq(system: str, user: str, max_tokens: int, json_mode: bool, temperature: float) -> str:
    from groq import Groq

    client = Groq(api_key=settings.groq_api_key)
    kwargs = {}
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    resp = client.chat.completions.create(
        model=settings.llm_model,
        max_tokens=max_tokens,
        temperature=temperature,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        **kwargs,
    )
    return resp.choices[0].message.content


def _generate_anthropic(system: str, user: str, max_tokens: int, temperature: float) -> str:
    import anthropic

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    resp = client.messages.create(
        model=settings.llm_model,
        max_tokens=max_tokens,
        temperature=temperature,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return "".join(b.text for b in resp.content if b.type == "text")


def _generate_openai(system: str, user: str, max_tokens: int, json_mode: bool, temperature: float) -> str:
    from openai import OpenAI

    client = OpenAI(api_key=settings.openai_api_key)
    kwargs = {}
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    resp = client.chat.completions.create(
        model=settings.llm_model,
        max_tokens=max_tokens,
        temperature=temperature,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        **kwargs,
    )
    return resp.choices[0].message.content


def generate_json(system: str, user: str, max_tokens: int = 2000, temperature: float = DEFAULT_TEMPERATURE) -> dict:
    """Ask the LLM for strict JSON and parse it, stripping markdown fences if present."""
    text = generate_text(system, user, max_tokens=max_tokens, json_mode=True, temperature=temperature)
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"LLM did not return valid JSON: {e}\nRaw: {text[:500]}")
