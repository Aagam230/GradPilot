"""Provider-agnostic LLM generation."""

import json
from tenacity import retry, stop_after_attempt, wait_exponential
from ..config import settings


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8))
def generate_text(
    system: str,
    user: str,
    max_tokens: int = 2000,
    json_mode: bool = False,
) -> str:

    if settings.llm_provider == "groq":
        return _generate_groq(
            system,
            user,
            max_tokens,
            json_mode,
        )

    raise ValueError(
        f"Unknown LLM_PROVIDER: {settings.llm_provider}"
    )


def _generate_groq(
    system: str,
    user: str,
    max_tokens: int,
    json_mode: bool,
) -> str:

    from groq import Groq

    client = Groq(api_key=settings.groq_api_key)

    kwargs = {}

    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    response = client.chat.completions.create(
        model=settings.llm_model,
        messages=[
            {
                "role": "system",
                "content": system,
            },
            {
                "role": "user",
                "content": user,
            },
        ],
        max_tokens=max_tokens,
        temperature=0.1,
        **kwargs,
    )

    return response.choices[0].message.content


def generate_json(
    system: str,
    user: str,
    max_tokens: int = 2000,
) -> dict:

    text = generate_text(
        system,
        user,
        max_tokens=max_tokens,
        json_mode=True,
    )

    text = text.strip()

    if text.startswith("```"):
        text = text.split("```")[1]

        if text.startswith("json"):
            text = text[4:]

    try:
        return json.loads(text)

    except json.JSONDecodeError as e:
        raise ValueError(
            f"LLM did not return valid JSON: {e}\n"
            f"Raw: {text[:500]}"
        )