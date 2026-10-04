import os


DEFAULT_AWS_REGION = "eu-west-3"
DEFAULT_AWS_ACCOUNT_ID = "123456789012"


def get_aws_region() -> str:
    return os.getenv("AWS_REGION", DEFAULT_AWS_REGION).strip() or DEFAULT_AWS_REGION


def get_aws_account_id() -> str:
    return (
        os.getenv("AWS_ACCOUNT_ID", DEFAULT_AWS_ACCOUNT_ID).strip()
        or DEFAULT_AWS_ACCOUNT_ID
    )


def generate_arn(
    service: str,
    resource_name: str,
    region: str | None = None,
    account_id: str | None = None,
) -> str | list[str] | None:
    """Construit un ARN à partir d'un service et d'un nom de ressource.

    La région et l'identifiant de compte peuvent être passés explicitement ou
    fournis par l'environnement. Les valeurs par défaut restent volontairement
    fictives pour que le projet fonctionne en local sans dépendre d'un compte AWS.
    """

    normalized_service = service.lower()
    region = region or get_aws_region()
    account_id = account_id or get_aws_account_id()

    if normalized_service == "s3":
        return [
            f"arn:aws:s3:::{resource_name}",
            f"arn:aws:s3:::{resource_name}/*",
        ]

    if normalized_service == "dynamodb":
        return f"arn:aws:dynamodb:{region}:{account_id}:table/{resource_name}"

    if normalized_service == "ecr":
        return f"arn:aws:ecr:{region}:{account_id}:repository/{resource_name}"

    if normalized_service == "lambda":
        return f"arn:aws:lambda:{region}:{account_id}:function:{resource_name}"

    if normalized_service == "cloudwatch":
        return f"arn:aws:logs:{region}:{account_id}:log-group:{resource_name}:*"

    if normalized_service == "ec2":
        return f"arn:aws:ec2:{region}:{account_id}:instance/{resource_name}"

    return None
