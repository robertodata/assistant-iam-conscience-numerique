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


def parse_user_request(text: str) -> dict[str, str | None]:
    normalized_text = normalize_text(text)

    aws_service_type = find_keyword(
        normalized_text,
        {
            "lambda": ["lambda", "fonction lambda"],
            "ec2": ["ec2", "instance ec2", "serveur ec2"],
        },
    )
    service = find_keyword(
        normalized_text,
        {
            "s3": ["s3", "bucket"],
            "dynamodb": ["dynamodb", "dynamo db", "table dynamodb"],
        },
    )
    action = find_keyword(
        normalized_text,
        {
            # Les accents sont retires par normalize_text avant la detection.
            "read": ["lire", "lis", "lise", "lecture", "read", "consulter", "acces lecture"],
            "write": [
                "ecrire",
                "ecriture",
                "write",
                "modifier",
                "ajouter",
                "acces ecriture",
            ],
        },
    )

    return {
        "aws_service_type": aws_service_type,
        "service": service,
        "action": action,
    }
