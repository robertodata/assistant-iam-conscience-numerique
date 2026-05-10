# Ce fichier contient une validation IAM pedagogique avant l'affichage final.
# Les regles restent simples et explicites pour faciliter l'apprentissage.

from .iam_rules import IAM_SENSITIVE_RULES


def validate_iam_policy(
    actions: list[str],
    resource: str | list[str],
    mode: str = "beginner",
) -> list[dict[str, str]]:
    findings = []
    message_key = "expert_message" if mode == "expert" else "beginner_message"
    recommendation_key = (
        "expert_recommendation" if mode == "expert" else "beginner_recommendation"
    )

    for action in actions:
        if action == "*":
            if mode == "expert":
                message = "Wildcard action '*' autorise toutes les actions IAM compatibles avec la ressource cible."
                recommendation = "Remplacer '*' par des actions explicites et separer les permissions par besoin fonctionnel."
            else:
                message = "Wildcard action '*' donne tous les droits possibles."
                recommendation = "Remplacer '*' par une liste precise d'actions necessaires."

            findings.append(
                {
                    "severity": "high",
                    "permission": action,
                    "message": message,
                    "recommendation": recommendation,
                }
            )

        if action in IAM_SENSITIVE_RULES:
            finding = IAM_SENSITIVE_RULES[action]
            findings.append(
                {
                    "severity": finding["severity"],
                    "permission": action,
                    "message": finding[message_key],
                    "recommendation": finding[recommendation_key],
                }
            )

    if resource == "*":
        if mode == "expert":
            message = "Resource '*' elargit le scope a toutes les ressources compatibles et augmente le rayon d'impact."
            recommendation = "Remplacer '*' par des ARN explicites et, si possible, ajouter des conditions IAM."
        else:
            message = "Resource '*' applique les permissions a toutes les ressources compatibles."
            recommendation = "Preciser un ARN de ressource pour mieux respecter le Least Privilege."

        findings.append(
            {
                "severity": "medium",
                "permission": "Resource *",
                "message": message,
                "recommendation": recommendation,
            }
        )

    return findings
