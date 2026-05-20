# Ce module analyse une phrase utilisateur avec des regles simples.
# Il n'appelle pas OpenAI : il s'appuie uniquement sur le catalogue AWS local.

from app.aws_service_catalog import get_actions_for_service


SERVICE_KEYWORDS = {
    "s3": ["s3", "bucket"],
    "dynamodb": ["dynamodb", "table"],
    "lambda": ["lambda"],
    "ec2": ["ec2", "instance"],
    "ecr": ["ecr", "docker", "image", "image docker", "registry"],
    "cloudwatch": ["cloudwatch", "logs", "metriques", "métriques", "metrics"],
    "billing": ["facturation", "cout", "couts", "coût", "coûts", "billing"],
}


INTENT_KEYWORDS = {
    "read": ["lire", "lise", "lit", "consulter", "read"],
    "write": ["ecrire", "écrire", "creer", "créer", "modifier", "upload"],
    "push": ["push", "pousse", "pousser"],
    "pull": ["pull", "telecharger image", "télécharger image", "recuperer image", "récupérer image"],
    "delete": ["supprimer", "delete"],
    "invoke": ["invoquer"],
    "start_stop": ["demarrer", "démarrer", "arreter", "arrêter"],
}


def normalize_text(text: str) -> str:
    return text.lower()


def detect_services(text: str) -> list[str]:
    detected_services = []

    for service, keywords in SERVICE_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            detected_services.append(service)

    return detected_services


def detect_intents(text: str, services: list[str]) -> list[str]:
    detected_intents = []

    for intent, keywords in INTENT_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            detected_intents.append(intent)

    if (
        "ecr" in services
        and "pull" not in detected_intents
        and "push" not in detected_intents
        and any(keyword in text for keyword in ["docker", "image", "registry"])
    ):
        detected_intents.append("push")

    if "billing" in services and "read" not in detected_intents:
        detected_intents.append("read")

    if "cloudwatch" in services and "logs" in text and "logs" not in detected_intents:
        detected_intents.append("logs")

    return detected_intents


def get_risk_level(intents: list[str], actions: list[str]) -> str:
    if any(intent in ["delete", "manage"] for intent in intents):
        return "medium"

    if any("Delete" in action for action in actions):
        return "medium"

    if any(intent in ["write", "push", "pull", "start_stop", "logs"] for intent in intents):
        return "medium"

    return "low"


def build_recommendations(
    services: list[str],
    intents: list[str],
    actions: list[str],
) -> list[str]:
    recommendations = [
        "Précisez un ARN de ressource pour éviter Resource *.",
    ]

    if not services:
        recommendations.append("Précisez le service AWS concerné.")

    if not intents:
        recommendations.append("Précisez l'action attendue : lire, écrire, supprimer ou invoquer.")

    if not actions and services and intents:
        recommendations.append(
            "Aucune action IAM exacte n'a été trouvée pour cette combinaison service/intention."
        )

    if any(intent in ["delete", "manage"] for intent in intents):
        recommendations.append("Validez les permissions destructrices avec une revue de sécurité.")

    return recommendations


def analyze_iam_request(user_request: str) -> dict:
    normalized_request = normalize_text(user_request)
    services = detect_services(normalized_request)
    intents = detect_intents(normalized_request, services)
    actions = []

    for service in services:
        for intent in intents:
            actions.extend(get_actions_for_service(service, intent))

    unique_actions = list(dict.fromkeys(actions))

    return {
        "request": user_request,
        "services": services,
        "intents": intents,
        "actions": unique_actions,
        "risk_level": get_risk_level(intents, unique_actions),
        "recommendations": build_recommendations(
            services,
            intents,
            unique_actions,
        ),
    }
