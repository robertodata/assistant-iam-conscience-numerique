import logging
import os

from dotenv import load_dotenv
from openai import OpenAI


logger = logging.getLogger(__name__)
load_dotenv()

DEFAULT_OPENAI_MODEL = "gpt-4.1-mini"
DEFAULT_MAX_TOKENS = 200
DEFAULT_TIMEOUT_SECONDS = 20.0


def get_openai_api_key() -> str | None:
    return os.getenv("OPENAI_API_KEY")


def get_openai_model() -> str:
    return os.getenv("OPENAI_MODEL", DEFAULT_OPENAI_MODEL).strip() or DEFAULT_OPENAI_MODEL


def get_ai_max_tokens() -> int:
    raw_value = os.getenv("AI_MAX_TOKENS", str(DEFAULT_MAX_TOKENS))

    try:
        return max(50, min(int(raw_value), 500))
    except ValueError:
        return DEFAULT_MAX_TOKENS


def get_ai_timeout_seconds() -> float:
    raw_value = os.getenv("AI_TIMEOUT_SECONDS", str(DEFAULT_TIMEOUT_SECONDS))

    try:
        return max(5.0, min(float(raw_value), 60.0))
    except ValueError:
        return DEFAULT_TIMEOUT_SECONDS


def is_openai_configured() -> bool:
    api_key = get_openai_api_key()

    if not api_key or not api_key.strip():
        return False

    return api_key.strip() != "YOUR_OPENAI_API_KEY"


def generate_ai_explanation(prompt: str) -> str:
    if not is_openai_configured():
        return "Explication IA simulée : " + prompt

    try:
        client = OpenAI(
            api_key=get_openai_api_key(),
            timeout=get_ai_timeout_seconds(),
        )
        response = client.chat.completions.create(
            model=get_openai_model(),
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Tu expliques AWS IAM en français clair. "
                        "Va droit au but, précise les risques utiles et évite le jargon inutile. "
                        "La réponse doit rester courte."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=get_ai_max_tokens(),
        )

        return response.choices[0].message.content.strip()
    except Exception:
        logger.exception("Erreur pendant l'appel au fournisseur IA.")
        return "Erreur IA : impossible de générer une réponse."
