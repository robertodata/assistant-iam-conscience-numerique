# Ce fichier liste les services AWS et les intentions IAM que le projet sait
# reconnaitre. Il prepare un moteur IAM plus universel sans remplacer le
# fonctionnement pedagogique actuel.


AWS_SERVICE_CATALOG = {
    "s3": {
        "read": ["s3:GetObject", "s3:ListBucket"],
        "write": ["s3:PutObject"],
        "delete": ["s3:DeleteObject"],
    },
    "dynamodb": {
        "read": ["dynamodb:GetItem", "dynamodb:Query", "dynamodb:Scan"],
        "write": ["dynamodb:PutItem", "dynamodb:UpdateItem"],
        "delete": ["dynamodb:DeleteItem"],
    },
    "lambda": {
        "invoke": ["lambda:InvokeFunction"],
        "manage": ["lambda:CreateFunction", "lambda:UpdateFunctionCode"],
    },
    "ec2": {
        "read": ["ec2:DescribeInstances"],
        "start_stop": ["ec2:StartInstances", "ec2:StopInstances"],
    },
    "ecr": {
        "push": [
            "ecr:GetAuthorizationToken",
            "ecr:BatchCheckLayerAvailability",
            "ecr:InitiateLayerUpload",
            "ecr:UploadLayerPart",
            "ecr:CompleteLayerUpload",
            "ecr:PutImage",
        ],
        "pull": [
            "ecr:GetAuthorizationToken",
            "ecr:BatchGetImage",
            "ecr:GetDownloadUrlForLayer",
        ],
    },
    "cloudwatch": {
        "read": ["cloudwatch:GetMetricData", "cloudwatch:ListMetrics"],
        "logs": ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"],
    },
    "billing": {
        "read": ["aws-portal:ViewBilling", "ce:GetCostAndUsage"],
        "manage": ["aws-portal:ModifyBilling"],
    },
}


def get_actions_for_service(service: str, intent: str) -> list[str]:
    service_actions = AWS_SERVICE_CATALOG.get(service.lower())

    if service_actions is None:
        return []

    return service_actions.get(intent.lower(), [])


def list_supported_services() -> dict[str, dict[str, list[str]]]:
    return AWS_SERVICE_CATALOG
