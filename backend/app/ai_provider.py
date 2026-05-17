import logging
import os

from dotenv import load_dotenv
from openai import OpenAI


logger = logging.getLogger(__name__)


# .env permet de garder les secrets en dehors du code source.
# Une cle API ne doit jamais etre hardcodee dans Git, car elle pourrait etre
# fuitee, reutilisee ou facturee par erreur.
load_dotenv()


def get_openai_api_key() -> str | None:
    return os.getenv("OPENAI_API_KEY")


def is_openai_configured() -> bool:
    api_key = get_openai_api_key()

    if not api_key or not api_key.strip():
        return False

    return api_key.strip() != "YOUR_OPENAI_API_KEY"


def generate_ai_explanation(prompt: str) -> str:
    # Sans vraie cle API, on garde un fallback simule pour ne pas casser
    # l'application et pour eviter tout appel externe involontaire.
    if not is_openai_configured():
        return "Explication IA simulée : " + prompt

    try:
        client = OpenAI(api_key=get_openai_api_key(), timeout=20.0)
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Tu expliques IAM simplement en francais. "
                        "Reponds en 150 mots maximum."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=200,
        )

        return response.choices[0].message.content.strip()
    except Exception:
        logger.exception("Erreur pendant l'appel OpenAI du provider IA.")
        return "Erreur IA : impossible de générer une réponse."
