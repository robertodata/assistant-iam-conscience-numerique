# Ce module genere des ARN AWS pedagogiques a partir d'un service et d'un nom
# de ressource detecte dans une phrase utilisateur.


def generate_arn(
    service: str,
    resource_name: str,
    region: str = "eu-west-3",
    account_id: str = "123456789012",
) -> str | list[str] | None:
    normalized_service = service.lower()

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
