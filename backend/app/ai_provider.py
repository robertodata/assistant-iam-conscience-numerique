import os

from dotenv import load_dotenv


# .env permet de garder les secrets en dehors du code source.
# Une cle API ne doit jamais etre hardcodee dans Git, car elle pourrait etre
# fuitee, reutilisee ou facturee par erreur.
load_dotenv()


def get_openai_api_key() -> str | None:
    return os.getenv("OPENAI_API_KEY")


def is_openai_configured() -> bool:
    return get_openai_api_key() is not None


def generate_ai_explanation(prompt: str) -> str:
    # Pour l'instant, on verifie seulement la configuration.
    # Aucun appel reel a OpenAI n'est effectue ici.
    if not is_openai_configured():
        return "OPENAI_API_KEY manquante"

    return "Explication IA simulée : " + prompt
