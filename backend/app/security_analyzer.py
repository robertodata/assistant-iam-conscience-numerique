# Ce fichier contient les regles simples d'analyse de securite IAM.


def analyze_security_findings(
    resource: str | list[str],
    actions: list[str],
) -> list[dict[str, str]]:
    # Les findings sont des risques potentiels detectes dans la policy IAM.
    findings = []

    if resource == "*":
        findings.append(
            {
                "severity": "medium",
                "title": "Resource trop large",
                "description": "Resource '*' applique la permission a toutes les ressources compatibles.",
            }
        )

    for action in actions:
        if "*" in action:
            findings.append(
                {
                    "severity": "high",
                    "title": "Wildcard Action detecte",
                    "description": "Action '*' donne tous les droits possibles pour le perimetre cible.",
                }
            )

        if "Delete" in action:
            findings.append(
                {
                    "severity": "medium",
                    "title": "Permission Delete detectee",
                    "description": f"La permission {action} peut supprimer des donnees ou des ressources.",
                }
            )

        if action.startswith("iam:"):
            findings.append(
                {
                    "severity": "high",
                    "title": "Permission IAM sensible",
                    "description": f"La permission {action} peut modifier ou gerer des identites et acces IAM.",
                }
            )

        if action.startswith("kms:"):
            findings.append(
                {
                    "severity": "high",
                    "title": "Permission KMS sensible",
                    "description": f"La permission {action} peut agir sur des cles de chiffrement KMS.",
                }
            )

        if action.startswith("sts:"):
            findings.append(
                {
                    "severity": "medium",
                    "title": "Permission STS sensible",
                    "description": f"La permission {action} peut permettre d'obtenir ou d'assumer des identites temporaires.",
                }
            )

    return findings


def calculate_security_score(findings: list[dict[str, str]]) -> int:
    # Le score part de 100 et baisse selon la severite des findings.
    score = 100

    for finding in findings:
        if finding["severity"] == "high":
            score -= 30
        elif finding["severity"] == "medium":
            score -= 15
        else:
            score -= 5

    return max(score, 0)


def get_security_level(score: int) -> str:
    if score >= 80:
        return "Bon"

    if score >= 50:
        return "Moyen"

    return "Risque eleve"
