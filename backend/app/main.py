from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .ai_provider import generate_ai_explanation, is_openai_configured
from .iac_generator import build_cloudformation_template, build_terraform_template
from .iam_engine import (
    build_explanations,
    build_multi_role_name,
    build_permission_policy,
    build_permission_items,
    build_permission_policy_from_items,
    build_resource,
    build_role_name,
    build_trust_policy,
    get_actions_for_request,
)
from .iam_validator import validate_iam_policy
from .nlp_parser import parse_user_request
from .security_analyzer import (
    analyze_security_findings,
    calculate_security_score,
    get_security_level,
)


# Ce fichier garde l'application FastAPI et les routes principales.

app = FastAPI(title="Assistant IAM Conscience Numerique")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:3000", "http://localhost:3000"],
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
    text: str


class AiExplainRequest(BaseModel):
    prompt: str


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/parse-request")
def parse_request(request: ParseRequest) -> dict:
    # Ce endpoint transforme une phrase utilisateur en intention IAM simple.
    # Pour l'instant, il utilise uniquement des mots-cles et aucune IA externe.
    return parse_user_request(request.text)


@app.post("/ai/explain")
def explain_with_ai(request: AiExplainRequest) -> dict[str, str]:
    # Ce endpoint prepare une future integration IA.
    # Aujourd'hui, il retourne seulement une reponse simulee.
    return {"explanation": generate_ai_explanation(request.prompt)}


@app.get("/ai/status")
def get_ai_status() -> dict[str, bool]:
    return {"openai_configured": is_openai_configured()}


@app.post("/generate-policy")
def generate_policy(request: PolicyRequest) -> dict:
    # Ce endpoint recoit une demande simple et retourne un role IAM complet.
    # Une requete POST sert a envoyer des donnees au backend.
    # Le JSON recu est transforme en objet Python grace au modele PolicyRequest.
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

    # Le backend retourne ici un dictionnaire Python converti en JSON.
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
