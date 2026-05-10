from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .iac_generator import build_cloudformation_template, build_terraform_template
from .iam_engine import (
    build_explanations,
    build_permission_policy,
    build_resource,
    build_role_name,
    build_trust_policy,
    get_actions_for_request,
)
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
    service: str
    action: str
    resource_name: str | None = None
    aws_service_type: str = "lambda"


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/generate-policy")
def generate_policy(request: PolicyRequest) -> dict:
    # Ce endpoint recoit une demande simple et retourne un role IAM complet.
    # Une requete POST sert a envoyer des donnees au backend.
    # Le JSON recu est transforme en objet Python grace au modele PolicyRequest.
    aws_service_type = request.aws_service_type.lower()
    actions = get_actions_for_request(request.service, request.action)
    resource, warnings = build_resource(request.service, request.resource_name)
    role_name = build_role_name(aws_service_type, request.service, request.action)
    trust_policy = build_trust_policy(aws_service_type)
    policy = build_permission_policy(actions, resource)
    explanations = build_explanations(actions)
    security_findings = analyze_security_findings(resource, actions)
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
        "security_findings": security_findings,
        "security_score": security_score,
        "security_level": security_level,
    }
