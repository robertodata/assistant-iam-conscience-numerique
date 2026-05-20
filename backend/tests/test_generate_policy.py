from fastapi.testclient import TestClient
import pytest

from app import ai_provider
from app.aws_service_catalog import get_actions_for_service
from app.iam_validator import validate_iam_policy
from app.main import app


client = TestClient(app)


def test_health_returns_status_ok():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_iam_services_returns_supported_service_catalog():
    response = client.get("/iam/services")

    assert response.status_code == 200
    catalog = response.json()
    assert set(catalog) == {
        "s3",
        "dynamodb",
        "lambda",
        "ec2",
        "ecr",
        "cloudwatch",
        "billing",
    }
    assert catalog["s3"]["read"] == ["s3:GetObject", "s3:ListBucket"]
    assert catalog["ecr"]["push"] == [
        "ecr:GetAuthorizationToken",
        "ecr:BatchCheckLayerAvailability",
        "ecr:InitiateLayerUpload",
        "ecr:UploadLayerPart",
        "ecr:CompleteLayerUpload",
        "ecr:PutImage",
    ]


def test_get_actions_for_service_returns_catalog_actions():
    assert get_actions_for_service("lambda", "invoke") == ["lambda:InvokeFunction"]
    assert get_actions_for_service("ec2", "start_stop") == [
        "ec2:StartInstances",
        "ec2:StopInstances",
    ]


def test_get_actions_for_service_returns_empty_list_for_unknown_values():
    assert get_actions_for_service("unknown", "read") == []
    assert get_actions_for_service("s3", "unknown") == []


def test_iam_analyze_detects_s3_read_request():
    response = client.post(
        "/iam/analyze",
        json={"request": "Je veux qu'une Lambda lise un bucket S3"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "request": "Je veux qu'une Lambda lise un bucket S3",
        "services": ["s3", "lambda"],
        "intents": ["read"],
        "actions": ["s3:GetObject", "s3:ListBucket"],
        "risk_level": "low",
        "recommendations": [
            "Précisez un ARN de ressource pour éviter Resource *.",
        ],
    }


def test_iam_analyze_detects_ecr_push_request():
    response = client.post(
        "/iam/analyze",
        json={"request": "Je veux pousser une image Docker dans ECR"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["services"] == ["ecr"]
    assert data["intents"] == ["push"]
    assert data["actions"] == [
        "ecr:GetAuthorizationToken",
        "ecr:BatchCheckLayerAvailability",
        "ecr:InitiateLayerUpload",
        "ecr:UploadLayerPart",
        "ecr:CompleteLayerUpload",
        "ecr:PutImage",
    ]
    assert data["risk_level"] == "medium"


def test_iam_analyze_detects_ecr_push_without_explicit_service():
    response = client.post(
        "/iam/analyze",
        json={"request": "Je veux pousser une image Docker"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["services"] == ["ecr"]
    assert data["intents"] == ["push"]
    assert data["actions"] == [
        "ecr:GetAuthorizationToken",
        "ecr:BatchCheckLayerAvailability",
        "ecr:InitiateLayerUpload",
        "ecr:UploadLayerPart",
        "ecr:CompleteLayerUpload",
        "ecr:PutImage",
    ]


def test_iam_analyze_detects_ec2_push_to_ecr():
    response = client.post(
        "/iam/analyze",
        json={"request": "Une EC2 doit push sur ECR"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["services"] == ["ec2", "ecr"]
    assert data["intents"] == ["push"]
    assert data["actions"] == [
        "ecr:GetAuthorizationToken",
        "ecr:BatchCheckLayerAvailability",
        "ecr:InitiateLayerUpload",
        "ecr:UploadLayerPart",
        "ecr:CompleteLayerUpload",
        "ecr:PutImage",
    ]


def test_iam_analyze_detects_ecr_pull_without_explicit_service():
    response = client.post(
        "/iam/analyze",
        json={"request": "Je veux pull une image"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["services"] == ["ecr"]
    assert data["intents"] == ["pull"]
    assert data["actions"] == [
        "ecr:GetAuthorizationToken",
        "ecr:BatchGetImage",
        "ecr:GetDownloadUrlForLayer",
    ]


def test_iam_analyze_detects_billing_read_request():
    response = client.post(
        "/iam/analyze",
        json={"request": "Consulter les coûts de facturation AWS"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["services"] == ["billing"]
    assert data["intents"] == ["read"]
    assert data["actions"] == ["aws-portal:ViewBilling", "ce:GetCostAndUsage"]
    assert data["risk_level"] == "low"


def test_iam_analyze_detects_delete_risk():
    response = client.post(
        "/iam/analyze",
        json={"request": "Supprimer des objets dans un bucket S3"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["services"] == ["s3"]
    assert data["intents"] == ["delete"]
    assert data["actions"] == ["s3:DeleteObject"]
    assert data["risk_level"] == "medium"
    assert "Validez les permissions destructrices avec une revue de sécurité." in data[
        "recommendations"
    ]


def test_iam_analyze_returns_guidance_for_unknown_request():
    response = client.post(
        "/iam/analyze",
        json={"request": "Je veux quelque chose de vague"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["services"] == []
    assert data["intents"] == []
    assert data["actions"] == []
    assert data["risk_level"] == "low"
    assert "Précisez le service AWS concerné." in data["recommendations"]
    assert (
        "Précisez l'action attendue : lire, écrire, supprimer ou invoquer."
        in data["recommendations"]
    )


def test_ai_status_returns_false_without_openai_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    response = client.get("/ai/status")

    assert response.status_code == 200
    assert response.json() == {"openai_configured": False}


@pytest.mark.parametrize("api_key", ["", "YOUR_OPENAI_API_KEY"])
def test_ai_status_returns_false_with_invalid_openai_key(monkeypatch, api_key):
    monkeypatch.setenv("OPENAI_API_KEY", api_key)

    response = client.get("/ai/status")

    assert response.status_code == 200
    assert response.json() == {"openai_configured": False}


def test_ai_status_returns_true_with_openai_key(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    response = client.get("/ai/status")

    assert response.status_code == 200
    assert response.json() == {"openai_configured": True}


@pytest.mark.parametrize("api_key", [None, "", "YOUR_OPENAI_API_KEY"])
def test_ai_explain_returns_simulated_explanation_without_valid_key(
    monkeypatch,
    api_key,
):
    if api_key is None:
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    else:
        monkeypatch.setenv("OPENAI_API_KEY", api_key)

    response = client.post(
        "/ai/explain",
        json={"prompt": "Explique s3:GetObject"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "explanation": "Explication IA simulée : Explique s3:GetObject"
    }


def test_ai_explain_calls_openai_when_key_is_configured(monkeypatch):
    class FakeCompletions:
        def create(self, model, messages, max_tokens):
            assert model == "gpt-4.1-mini"
            assert messages[0]["role"] == "system"
            assert messages[1] == {"role": "user", "content": "Explique s3:GetObject"}
            assert max_tokens == 200
            fake_message = type("FakeMessage", (), {"content": "Explication OpenAI"})()
            fake_choice = type("FakeChoice", (), {"message": fake_message})()
            return type("FakeResponse", (), {"choices": [fake_choice]})()

    class FakeChat:
        def __init__(self):
            self.completions = FakeCompletions()

    class FakeOpenAI:
        def __init__(self, api_key, timeout):
            assert api_key == "test-key"
            assert timeout == 20.0
            self.chat = FakeChat()

    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(ai_provider, "OpenAI", FakeOpenAI)

    response = client.post(
        "/ai/explain",
        json={"prompt": "Explique s3:GetObject"},
    )

    assert response.status_code == 200
    assert response.json() == {"explanation": "Explication OpenAI"}


def test_ai_explain_returns_clear_error_when_openai_fails(monkeypatch):
    class FailingCompletions:
        def create(self, model, messages, max_tokens):
            raise RuntimeError("OpenAI indisponible")

    class FailingChat:
        def __init__(self):
            self.completions = FailingCompletions()

    class FailingOpenAI:
        def __init__(self, api_key, timeout):
            self.chat = FailingChat()

    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(ai_provider, "OpenAI", FailingOpenAI)

    response = client.post(
        "/ai/explain",
        json={"prompt": "Explique s3:GetObject"},
    )

    assert response.status_code == 200
    assert response.json() == {"explanation": "Erreur IA : impossible de générer une réponse."}


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
