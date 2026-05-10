from fastapi import HTTPException


# Ce fichier contient le moteur IAM simple du projet :
# permissions disponibles, role_name, trust policy et permission policy.

iam_permissions = {
    "s3": {
        "read": [
            "s3:GetObject",
            "s3:ListBucket",
        ],
        "write": [
            "s3:PutObject",
        ],
    },
    "dynamodb": {
        "read": [
            "dynamodb:GetItem",
        ],
        "write": [
            "dynamodb:PutItem",
        ],
    },
}


iam_permission_explanations = {
    "s3:GetObject": "Permet de lire les objets dans un bucket S3.",
    "s3:ListBucket": "Permet de lister le contenu d'un bucket S3.",
    "s3:PutObject": "Permet d'ajouter ou modifier des objets dans un bucket S3.",
    "dynamodb:GetItem": "Permet de lire un element dans une table DynamoDB.",
    "dynamodb:PutItem": "Permet d'ecrire ou remplacer un element dans une table DynamoDB.",
}


trust_policy_services = {
    "lambda": "lambda.amazonaws.com",
    "ec2": "ec2.amazonaws.com",
}


def build_role_name(aws_service_type: str, service: str, action: str) -> str:
    return f"{aws_service_type}-{service}-{action}-role"


def get_actions_for_request(service: str, action: str) -> list[str]:
    service_permissions = iam_permissions.get(service)

    if service_permissions is None:
        raise HTTPException(
            status_code=400,
            detail=f"Le service '{service}' n'est pas encore disponible.",
        )

    actions = service_permissions.get(action)

    if actions is None:
        raise HTTPException(
            status_code=400,
            detail=(
                f"L'action '{action}' n'est pas disponible "
                f"pour le service '{service}'."
            ),
        )

    return actions


def build_trust_policy(aws_service_type: str) -> dict:
    principal_service = trust_policy_services.get(aws_service_type)

    if principal_service is None:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Le type de service AWS '{aws_service_type}' "
                "n'est pas encore disponible."
            ),
        )

    # La trust policy indique quel service AWS a le droit d'utiliser le role.
    return {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": principal_service,
                },
                "Action": "sts:AssumeRole",
            }
        ],
    }


def build_resource(service: str, resource_name: str | None) -> tuple[str | list[str], list[str]]:
    warnings = []

    if not resource_name:
        # Resource "*" est risque car la permission peut s'appliquer a toutes
        # les ressources du service au lieu d'une ressource precise.
        warnings.append("Attention : Resource '*' donne un acces trop large.")
        return "*", warnings

    if service == "s3":
        # Un ARN est l'identifiant unique d'une ressource AWS.
        # Pour S3, on cible le bucket et les objets contenus dans ce bucket.
        return [
            f"arn:aws:s3:::{resource_name}",
            f"arn:aws:s3:::{resource_name}/*",
        ], warnings

    if service == "dynamodb":
        # Preciser une ressource limite la policy a une table et respecte mieux
        # le principe du Least Privilege.
        return f"arn:aws:dynamodb:eu-west-3:123456789012:table/{resource_name}", warnings

    return "*", warnings


def build_permission_policy(actions: list[str], resource: str | list[str]) -> dict:
    return {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": actions,
                "Resource": resource,
            }
        ],
    }


def build_explanations(actions: list[str]) -> list[dict[str, str]]:
    return [
        {
            "permission": action,
            "description": iam_permission_explanations.get(
                action,
                "Aucune explication disponible pour cette permission.",
            ),
        }
        for action in actions
    ]
