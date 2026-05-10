from fastapi.testclient import TestClient
import pytest

from app.main import app


client = TestClient(app)


def test_health_returns_status_ok():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


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
    }


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        (
            "La fonction Lambda doit consulter un bucket S3",
            {"aws_service_type": "lambda", "service": "s3", "action": "read"},
        ),
        (
            "Je veux un acces lecture pour une fonction Lambda",
            {"aws_service_type": "lambda", "service": None, "action": "read"},
        ),
        (
            "Un serveur EC2 doit ajouter des donnees dans DynamoDB",
            {"aws_service_type": "ec2", "service": "dynamodb", "action": "write"},
        ),
        (
            "Une instance EC2 a besoin d'un acces ecriture sur une table DynamoDB",
            {"aws_service_type": "ec2", "service": "dynamodb", "action": "write"},
        ),
        (
            "Je veux modifier un bucket S3",
            {"aws_service_type": None, "service": "s3", "action": "write"},
        ),
    ],
)
def test_parse_request_supports_multiple_natural_formulations(text, expected):
    response = client.post("/parse-request", json={"text": text})

    assert response.status_code == 200
    assert response.json() == expected


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
