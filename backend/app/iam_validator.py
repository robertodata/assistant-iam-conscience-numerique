# Ce fichier contient une validation IAM pedagogique avant l'affichage final.
# Les regles restent simples et explicites pour faciliter l'apprentissage.


sensitive_permissions = {
    "s3:DeleteBucket": {
        "severity": "high",
        "message": "Cette permission permet de supprimer un bucket S3.",
        "recommendation": "A utiliser seulement dans des roles d'administration tres controles.",
    },
    "iam:PassRole": {
        "severity": "high",
        "message": "Cette permission permet de transmettre un role IAM a un service AWS.",
        "recommendation": "Limiter cette permission a des roles precis avec une ressource ARN explicite.",
    },
    "iam:CreateUser": {
        "severity": "high",
        "message": "Cette permission permet de creer de nouveaux utilisateurs IAM.",
        "recommendation": "Eviter cette permission dans les roles applicatifs standards.",
    },
    "iam:AttachRolePolicy": {
        "severity": "high",
        "message": "Cette permission permet d'attacher des policies a un role IAM.",
        "recommendation": "Restreindre cette permission aux administrateurs IAM.",
    },
}


def validate_iam_policy(
    actions: list[str],
    resource: str | list[str],
) -> list[dict[str, str]]:
    findings = []

    for action in actions:
        if action == "*":
            findings.append(
                {
                    "severity": "high",
                    "permission": action,
                    "message": "Wildcard action '*' donne tous les droits possibles.",
                    "recommendation": "Remplacer '*' par une liste precise d'actions necessaires.",
                }
            )

        if action in sensitive_permissions:
            finding = sensitive_permissions[action]
            findings.append(
                {
                    "severity": finding["severity"],
                    "permission": action,
                    "message": finding["message"],
                    "recommendation": finding["recommendation"],
                }
            )

    if resource == "*":
        findings.append(
            {
                "severity": "medium",
                "permission": "Resource *",
                "message": "Resource '*' applique les permissions a toutes les ressources compatibles.",
                "recommendation": "Preciser un ARN de ressource pour mieux respecter le Least Privilege.",
            }
        )

    return findings
