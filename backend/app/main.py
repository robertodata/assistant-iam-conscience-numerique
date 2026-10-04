import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .ai_provider import generate_ai_explanation, is_openai_configured
from .iam_analyzer import analyze_iam_request
from .aws_service_catalog import list_supported_services
from .iac_generator import build_cloudformation_template, build_terraform_template
from .iam_engine import (
    build_explanations,
    build_multi_role_name,
    build_permission_items,
    build_permission_policy_from_items,
    build_role_name,
    build_trust_policy,
)
from .iam_validator import validate_iam_policy
from .nlp_parser import parse_user_request
from .security_analyzer import (
    analyze_security_findings,
    calculate_security_score,
    get_security_level,
)


DEFAULT_CORS_ORIGINS = [
    "http://127.0.0.1:3000",
    "http://localhost:3000",
]


def get_allowed_origins() -> list[str]:
    raw_origins = os.getenv("CORS_ALLOWED_ORIGINS")

    if not raw_origins:
        return DEFAULT_CORS_ORIGINS

    return [
        origin.strip()
        for origin in raw_origins.split(",")
        if origin.strip()
    ]


app = FastAPI(title="Assistant IAM Conscience Numérique")

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PolicyRequest(BaseModel):
    service: str | None = None
    action: str | None = None
    permissions: list[dict[str, str]] | None = None
    resource_name: str | None = None
    aws_service_type: str = "lambda"
    mode: str = "beginner"


class ParseRequest(BaseModel):
    text: str = Field(min_length=1, max_length=4000)


class AiExplainRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=2500)


class IamAnalyzeRequest(BaseModel):
    request: str = Field(min_length=1, max_length=4000)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/parse-request")
def parse_request(request: ParseRequest) -> dict:
    return parse_user_request(request.text)


@app.post("/ai/explain")
def explain_with_ai(request: AiExplainRequest) -> dict[str, str]:
    return {"explanation": generate_ai_explanation(request.prompt)}


@app.get("/ai/status")
def get_ai_status() -> dict[str, bool]:
    return {"openai_configured": is_openai_configured()}


@app.get("/iam/services")
def get_iam_services() -> dict:
    return list_supported_services()


@app.post("/iam/analyze")
def analyze_iam(request: IamAnalyzeRequest) -> dict:
    return analyze_iam_request(request.request)


@app.post("/generate-policy")
def generate_policy(request: PolicyRequest) -> dict:
    aws_service_type = request.aws_service_type.lower()
    mode = request.mode.lower()

    if request.permissions:
        requested_permissions = request.permissions
    else:
        requested_permissions = [
            {
                "service": request.service,
                "action": request.action,
            }
        ]

    permission_items, warnings, actions = build_permission_items(
        requested_permissions,
        request.resource_name,
    )
    role_name = (
        build_multi_role_name(aws_service_type)
        if len(permission_items) > 1
        else build_role_name(
            aws_service_type,
            permission_items[0]["service"],
            permission_items[0]["action"],
        )
    )
    trust_policy = build_trust_policy(aws_service_type)
    policy = build_permission_policy_from_items(permission_items)
    explanations = build_explanations(actions, mode)
    validation_findings = []
    security_findings = []

    for permission in permission_items:
        validation_findings.extend(
            validate_iam_policy(permission["actions"], permission["resource"], mode)
        )
        security_findings.extend(
            analyze_security_findings(permission["resource"], permission["actions"])
        )

    security_score = calculate_security_score(security_findings)
    security_level = get_security_level(security_score)
    cloudformation_template = build_cloudformation_template(
        role_name,
        trust_policy,
        policy,
    )
    terraform_template = build_terraform_template(
        role_name,
        trust_policy,
        policy,
    )

    return {
        "role_name": role_name,
        "trust_policy": trust_policy,
        "policy": policy,
        "cloudformation_template": cloudformation_template,
        "terraform_template": terraform_template,
        "warnings": warnings,
        "explanations": explanations,
        "validation_findings": validation_findings,
        "security_findings": security_findings,
        "security_score": security_score,
        "security_level": security_level,
    }
