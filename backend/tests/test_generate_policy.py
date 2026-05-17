from fastapi.testclient import TestClient
import pytest

from app.iam_validator import validate_iam_policy
from app.main import app


client = TestClient(app)


def test_health_returns_status_ok():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ai_status_returns_false_without_openai_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    response = client.get("/ai/status")

    assert response.status_code == 200
    assert response.json() == {"openai_configured": False}


def test_ai_status_returns_true_with_openai_key(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    response = client.get("/ai/status")

    assert response.status_code == 200
    assert response.json() == {"openai_configured": True}


def test_ai_explain_returns_clear_error_without_openai_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    response = client.post(
        "/ai/explain",
        json={"prompt": "Explique s3:GetObject"},
    )

    assert response.status_code == 200
    assert response.json() == {"explanation": "OPENAI_API_KEY manquante"}


def test_ai_explain_returns_simulated_explanation(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    response = client.post(
        "/ai/explain",
        json={"prompt": "Explique s3:GetObject"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "explanation": "Explication IA simulée : Explique s3:GetObject"
    }


def test_parse_request_for_lambda_s3_read_sentence():
    response = client.post(
        "/parse-request",
        json={"text": "Je veux qu'une Lambda lise un bucket S3"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "aws_service_type": "lambda",
        "service": "s3",
        "action": "read",
        "permissions": [
            {
                "service": "s3",
                "action": "read",
            }
        ],
        "resource_name": None,
    }


def test_parse_request_for_ec2_dynamodb_write_sentence():
    response = client.post(
        "/parse-request",
        json={"text": "EC2 doit ecrire dans une table DynamoDB"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "aws_service_type": "ec2",
        "service": "dynamodb",
        "action": "write",
        "permissions": [
            {
                "service": "dynamodb",
                "action": "write",
            }
        ],
        "resource_name": None,
    }


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        (
            "La fonction Lambda doit consulter un bucket S3",
            {
                "aws_service_type": "lambda",
                "service": "s3",
                "action": "read",
                "permissions": [{"service": "s3", "action": "read"}],
                "resource_name": None,
            },
        ),
        (
            "Je veux un acces lecture pour une fonction Lambda",
            {
                "aws_service_type": "lambda",
                "service": None,
                "action": "read",
                "permissions": [],
                "resource_name": None,
            },
        ),
        (
            "Un serveur EC2 doit ajouter des donnees dans DynamoDB",
            {
                "aws_service_type": "ec2",
                "service": "dynamodb",
                "action": "write",
                "permissions": [{"service": "dynamodb", "action": "write"}],
                "resource_name": None,
            },
        ),
        (
            "Une instance EC2 a besoin d'un acces ecriture sur une table DynamoDB",
            {
                "aws_service_type": "ec2",
                "service": "dynamodb",
                "action": "write",
                "permissions": [{"service": "dynamodb", "action": "write"}],
                "resource_name": None,
            },
        ),
        (
            "Je veux modifier un bucket S3",
            {
                "aws_service_type": None,
                "service": "s3",
                "action": "write",
                "permissions": [{"service": "s3", "action": "write"}],
                "resource_name": None,
            },
        ),
    ],
)
def test_parse_request_supports_multiple_natural_formulations(text, expected):
    response = client.post("/parse-request", json={"text": text})

    assert response.status_code == 200
    assert response.json() == expected


def test_parse_request_extracts_bucket_resource_name():
    response = client.post(
        "/parse-request",
        json={"text": "Je veux qu'une Lambda lise le bucket mon-bucket"},
    )

    assert response.status_code == 200
    assert response.json()["resource_name"] == "mon-bucket"
    assert response.json()["permissions"] == [
        {
            "service": "s3",
            "action": "read",
            "resource_name": "mon-bucket",
        }
    ]


def test_parse_request_extracts_named_table_resource_name():
    response = client.post(
        "/parse-request",
        json={"text": "EC2 doit ecrire dans la table nommee ma-table"},
    )

    assert response.status_code == 200
    assert response.json()["resource_name"] == "ma-table"
    assert response.json()["permissions"] == [
        {
            "service": "dynamodb",
            "action": "write",
            "resource_name": "ma-table",
        }
    ]


def test_parse_request_without_resource_name_returns_null():
    response = client.post(
        "/parse-request",
        json={"text": "Je veux une Lambda avec acces lecture"},
    )

    assert response.status_code == 200
    assert response.json()["resource_name"] is None


def test_parse_request_detects_multiple_permissions():
    response = client.post(
        "/parse-request",
        json={"text": "Une Lambda lit S3 et ecrit dans DynamoDB"},
    )

    assert response.status_code == 200
    assert response.json()["aws_service_type"] == "lambda"
    assert response.json()["permissions"] == [
        {
            "service": "s3",
            "action": "read",
        },
        {
            "service": "dynamodb",
            "action": "write",
        },
    ]


def test_parse_request_detects_resources_for_each_permission():
    response = client.post(
        "/parse-request",
        json={
            "text": "Une Lambda lit le bucket mon-bucket et ecrit dans la table ma-table"
        },
    )

    assert response.status_code == 200
    assert response.json()["aws_service_type"] == "lambda"
    assert response.json()["resource_name"] == "mon-bucket"
    assert response.json()["permissions"] == [
        {
            "service": "s3",
            "action": "read",
            "resource_name": "mon-bucket",
        },
        {
            "service": "dynamodb",
            "action": "write",
            "resource_name": "ma-table",
        },
    ]


def test_parse_request_multiple_permissions_without_resources():
    response = client.post(
        "/parse-request",
        json={"text": "Une Lambda lit S3 et ecrit dans DynamoDB"},
    )

    assert response.status_code == 200
    assert response.json()["resource_name"] is None
    assert response.json()["permissions"] == [
        {
            "service": "s3",
            "action": "read",
        },
        {
            "service": "dynamodb",
            "action": "write",
        },
    ]


def test_generate_policy_for_s3_read_lambda_bucket():
    response = client.post(
        "/generate-policy",
        json={
            "service": "s3",
            "action": "read",
            "aws_service_type": "lambda",
            "resource_name": "mon-bucket",
        },
    )

    data = response.json()
    actions = data["policy"]["Statement"][0]["Action"]

    assert response.status_code == 200
    assert data["role_name"] == "lambda-s3-read-role"
    assert "s3:GetObject" in actions
    assert "s3:ListBucket" in actions


def test_generate_policy_supports_multiple_permissions():
    response = client.post(
        "/generate-policy",
        json={
            "aws_service_type": "lambda",
            "permissions": [
                {
                    "service": "s3",
                    "action": "read",
                },
                {
                    "service": "dynamodb",
                    "action": "write",
                },
            ],
            "resource_name": "ma-ressource",
        },
    )

    data = response.json()

    assert response.status_code == 200
    assert data["role_name"] == "lambda-multi-service-role"
    assert len(data["policy"]["Statement"]) == 2
    assert data["policy"]["Statement"][0]["Action"] == [
        "s3:GetObject",
        "s3:ListBucket",
    ]
    assert data["policy"]["Statement"][1]["Action"] == ["dynamodb:PutItem"]
    assert "dynamodb:PutItem" in [
        explanation["permission"] for explanation in data["explanations"]
    ]


def test_generate_policy_uses_resource_name_per_permission():
    response = client.post(
        "/generate-policy",
        json={
            "aws_service_type": "lambda",
            "permissions": [
                {
                    "service": "s3",
                    "action": "read",
                    "resource_name": "mon-bucket",
                },
                {
                    "service": "dynamodb",
                    "action": "write",
                    "resource_name": "ma-table",
                },
            ],
        },
    )

    data = response.json()

    assert response.status_code == 200
    assert data["policy"]["Statement"][0]["Resource"] == [
        "arn:aws:s3:::mon-bucket",
        "arn:aws:s3:::mon-bucket/*",
    ]
    assert data["policy"]["Statement"][1]["Resource"] == (
        "arn:aws:dynamodb:eu-west-3:123456789012:table/ma-table"
    )
    assert data["warnings"] == []


def test_generate_policy_keeps_global_resource_name_compatibility():
    response = client.post(
        "/generate-policy",
        json={
            "aws_service_type": "lambda",
            "permissions": [
                {
                    "service": "s3",
                    "action": "read",
                }
            ],
            "resource_name": "mon-bucket",
        },
    )

    data = response.json()

    assert response.status_code == 200
    assert data["policy"]["Statement"][0]["Resource"] == [
        "arn:aws:s3:::mon-bucket",
        "arn:aws:s3:::mon-bucket/*",
    ]


def test_generate_policy_without_resource_name_returns_warning():
    response = client.post(
        "/generate-policy",
        json={
            "service": "s3",
            "action": "read",
            "aws_service_type": "lambda",
        },
    )

    data = response.json()

    assert response.status_code == 200
    assert data["policy"]["Statement"][0]["Resource"] == "*"
    assert "Attention : Resource '*' donne un acces trop large." in data["warnings"]
    assert data["validation_findings"] == [
        {
            "severity": "medium",
            "permission": "Resource *",
            "message": "Resource '*' applique les permissions a toutes les ressources compatibles.",
            "recommendation": "Preciser un ARN de ressource pour mieux respecter le Least Privilege.",
        }
    ]


def test_generate_policy_for_dynamodb_write_ec2_table():
    response = client.post(
        "/generate-policy",
        json={
            "service": "dynamodb",
            "action": "write",
            "aws_service_type": "ec2",
            "resource_name": "ma-table",
        },
    )

    data = response.json()
    actions = data["policy"]["Statement"][0]["Action"]

    assert response.status_code == 200
    assert data["role_name"] == "ec2-dynamodb-write-role"
    assert "dynamodb:PutItem" in actions


def test_generate_policy_returns_cloudformation_template():
    response = client.post(
        "/generate-policy",
        json={
            "service": "s3",
            "action": "read",
            "aws_service_type": "lambda",
            "resource_name": "mon-bucket",
        },
    )

    data = response.json()

    assert response.status_code == 200
    assert "cloudformation_template" in data
    assert "AWS::IAM::Role" in data["cloudformation_template"]
    assert "AssumeRolePolicyDocument" in data["cloudformation_template"]
    assert "PolicyDocument" in data["cloudformation_template"]


def test_generate_policy_returns_terraform_template():
    response = client.post(
        "/generate-policy",
        json={
            "service": "s3",
            "action": "read",
            "aws_service_type": "lambda",
            "resource_name": "mon-bucket",
        },
    )

    data = response.json()

    assert response.status_code == 200
    assert "terraform_template" in data
    assert 'resource "aws_iam_role" "generated_role"' in data["terraform_template"]
    assert "assume_role_policy" in data["terraform_template"]
    assert 'resource "aws_iam_role_policy" "generated_policy"' in data["terraform_template"]
    assert "policy = <<POLICY" in data["terraform_template"]


def test_generate_policy_returns_validation_findings_key():
    response = client.post(
        "/generate-policy",
        json={
            "service": "s3",
            "action": "read",
            "aws_service_type": "lambda",
            "resource_name": "mon-bucket",
        },
    )

    data = response.json()

    assert response.status_code == 200
    assert data["validation_findings"] == []


def test_generate_policy_uses_beginner_explanations_by_default():
    response = client.post(
        "/generate-policy",
        json={
            "service": "s3",
            "action": "read",
            "aws_service_type": "lambda",
            "resource_name": "mon-bucket",
        },
    )

    data = response.json()

    assert response.status_code == 200
    assert data["explanations"][0]["description"] == (
        "s3:GetObject permet de lire des fichiers dans un bucket S3."
    )


def test_generate_policy_uses_expert_explanations():
    response = client.post(
        "/generate-policy",
        json={
            "service": "s3",
            "action": "read",
            "aws_service_type": "lambda",
            "resource_name": "mon-bucket",
            "mode": "expert",
        },
    )

    data = response.json()

    assert response.status_code == 200
    assert data["explanations"][0]["description"] == (
        "s3:GetObject autorise les operations GET sur les objets S3 et doit etre limite a des ARN precis."
    )


def test_generate_policy_uses_expert_validation_recommendations():
    response = client.post(
        "/generate-policy",
        json={
            "service": "s3",
            "action": "read",
            "aws_service_type": "lambda",
            "mode": "expert",
        },
    )

    data = response.json()

    assert response.status_code == 200
    assert data["validation_findings"][0]["recommendation"] == (
        "Remplacer '*' par des ARN explicites et, si possible, ajouter des conditions IAM."
    )


@pytest.mark.parametrize(
    ("permission", "expected_message"),
    [
        ("s3:DeleteBucket", "Cette permission permet de supprimer un bucket S3."),
        ("iam:PassRole", "Cette permission permet de transmettre un role IAM a un service AWS."),
        ("iam:CreateUser", "Cette permission permet de creer de nouveaux utilisateurs IAM."),
        ("iam:AttachRolePolicy", "Cette permission permet d'attacher des policies a un role IAM."),
    ],
)
def test_validate_iam_policy_detects_sensitive_permissions(permission, expected_message):
    findings = validate_iam_policy([permission], "arn:aws:example:::resource")

    assert findings[0]["severity"] == "high"
    assert findings[0]["permission"] == permission
    assert findings[0]["message"] == expected_message
    assert findings[0]["recommendation"]


def test_validate_iam_policy_detects_wildcard_action():
    findings = validate_iam_policy(["*"], "arn:aws:example:::resource")

    assert findings == [
        {
            "severity": "high",
            "permission": "*",
            "message": "Wildcard action '*' donne tous les droits possibles.",
            "recommendation": "Remplacer '*' par une liste precise d'actions necessaires.",
        }
    ]
