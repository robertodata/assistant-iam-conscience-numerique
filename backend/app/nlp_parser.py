import re
import unicodedata


# Ce fichier contient un interpreteur de texte tres simple.
# Il ne s'agit pas encore d'une IA ou d'un LLM : seulement de regles lisibles.


def normalize_text(text: str) -> str:
    lowered_text = text.lower()
    normalized_text = unicodedata.normalize("NFD", lowered_text)

    return "".join(
        character
        for character in normalized_text
        if unicodedata.category(character) != "Mn"
    )


def find_keyword(text: str, keywords: dict[str, list[str]]) -> str | None:
    for value, words in keywords.items():
        if any(word in text for word in words):
            return value

    return None


service_keywords = {
    "s3": ["s3", "bucket"],
    "dynamodb": ["dynamodb", "dynamo db", "table dynamodb", "table"],
}


action_keywords = {
    # Les accents sont retires par normalize_text avant la detection.
    "read": ["lire", "lit", "lis", "lise", "lecture", "read", "consulter", "acces lecture"],
    "write": [
        "ecrire",
        "ecrit",
        "ecris",
        "ecriture",
        "write",
        "modifier",
        "ajouter",
        "acces ecriture",
    ],
}


def extract_resource_name(text: str) -> str | None:
    # On detecte uniquement des formulations simples et pedagogiques.
    resource_match = re.search(
        r"\b(?:bucket|table)\s+(?:nomme\s+|nommee\s+|appele\s+|appelee\s+)?([a-z0-9][a-z0-9._-]*)",
        text,
    )

    if not resource_match:
        return None

    resource_name = resource_match.group(1)

    if resource_name in ["s3", "dynamodb"]:
        return None

    return resource_name


def detect_permissions(text: str) -> list[dict[str, str]]:
    permissions = []
    text_parts = re.split(r"\bet\b|,|;", text)

    for part in text_parts:
        service = find_keyword(part, service_keywords)
        action = find_keyword(part, action_keywords)
        resource_name = extract_resource_name(part)

        if service and action:
            permission = {"service": service, "action": action}

            # Quand une ressource est proche d'une permission, on l'attache a
            # cette permission precise : bucket => s3, table => dynamodb.
            if resource_name:
                permission["resource_name"] = resource_name

            permissions.append(permission)

    if permissions:
        return permissions

    service = find_keyword(text, service_keywords)
    action = find_keyword(text, action_keywords)

    if service and action:
        permission = {"service": service, "action": action}
        resource_name = extract_resource_name(text)

        if resource_name:
            permission["resource_name"] = resource_name

        return [permission]

    return []


def parse_user_request(text: str) -> dict:
    normalized_text = normalize_text(text)

    aws_service_type = find_keyword(
        normalized_text,
        {
            "lambda": ["lambda", "fonction lambda"],
            "ec2": ["ec2", "instance ec2", "serveur ec2"],
        },
    )
    permissions = detect_permissions(normalized_text)
    first_permission = permissions[0] if permissions else {}
    service = first_permission.get("service") or find_keyword(
        normalized_text,
        service_keywords,
    )
    action = first_permission.get("action") or find_keyword(
        normalized_text,
        action_keywords,
    )
    resource_name = extract_resource_name(normalized_text)

    return {
        "aws_service_type": aws_service_type,
        "service": service,
        "action": action,
        "permissions": permissions,
        "resource_name": resource_name,
    }
