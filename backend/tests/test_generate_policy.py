from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_returns_status_ok():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


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
