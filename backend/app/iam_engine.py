from fastapi import HTTPException

from .iam_rules import IAM_RULES


# Ce fichier contient le moteur IAM simple du projet :
# permissions disponibles, role_name, trust policy et permission policy.


trust_policy_services = {
    "lambda": "lambda.amazonaws.com",
    "ec2": "ec2.amazonaws.com",
}


def build_role_name(aws_service_type: str, service: str, action: str) -> str:
    return f"{aws_service_type}-{service}-{action}-role"


def build_multi_role_name(aws_service_type: str) -> str:
    return f"{aws_service_type}-multi-service-role"


def get_actions_for_request(service: str, action: str) -> list[str]:
    service_rules = IAM_RULES.get(service)

    if service_rules is None:
        raise HTTPException(
            status_code=400,
            detail=f"Le service '{service}' n'est pas encore disponible.",
        )

    action_rules = service_rules.get(action)

    if action_rules is None:
        raise HTTPException(
            status_code=400,
            detail=(
                f"L'action '{action}' n'est pas disponible "
                f"pour le service '{service}'."
            ),
        )

    return action_rules["actions"]


def build_permission_items(
    permissions: list[dict[str, str]],
    resource_name: str | None,
) -> tuple[list[dict], list[str], list[str]]:
    permission_items = []
    warnings = []
    all_actions = []

    for permission in permissions:
        service = permission["service"]
        action = permission["action"]
        actions = get_actions_for_request(service, action)
        resource, resource_warnings = build_resource(service, resource_name)

        permission_items.append(
            {
                "service": service,
                "action": action,
                "actions": actions,
                "resource": resource,
            }
        )
        all_actions.extend(actions)
        warnings.extend(resource_warnings)

    return permission_items, warnings, all_actions


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


def build_permission_policy_from_items(permission_items: list[dict]) -> dict:
    return {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": permission["actions"],
                "Resource": permission["resource"],
            }
            for permission in permission_items
        ],
    }


def build_explanations(actions: list[str], mode: str = "beginner") -> list[dict[str, str]]:
    description_key = (
        "description_expert" if mode == "expert" else "description_beginner"
    )
    descriptions = {}

    for service_rules in IAM_RULES.values():
        for action_rules in service_rules.values():
            descriptions.update(action_rules.get(description_key, {}))

    return [
        {
            "permission": action,
            "description": descriptions.get(
                action,
                "Aucune explication disponible pour cette permission.",
            ),
        }
        for action in actions
    ]
