import json


# Ce fichier genere les sorties Infrastructure as Code du projet.


def build_cloudformation_template(
    role_name: str,
    trust_policy: dict,
    permission_policy: dict,
) -> str:
    actions = permission_policy["Statement"][0]["Action"]
    resources = permission_policy["Statement"][0]["Resource"]
    principal_service = trust_policy["Statement"][0]["Principal"]["Service"]

    action_lines = "\n".join(f"                  - {action}" for action in actions)

    if isinstance(resources, list):
        resource_lines = "\n".join(f"                  - {resource}" for resource in resources)
    else:
        resource_lines = f"                  - {resources}"

    # CloudFormation permet de decrire une infrastructure AWS dans un fichier.
    # Ici, on cree seulement un exemple pedagogique avec un role IAM et sa policy.
    return f"""AWSTemplateFormatVersion: '2010-09-09'
Description: Role IAM genere par Assistant IAM Intelligent

Resources:
  GeneratedIamRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: {role_name}
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: {principal_service}
            Action: sts:AssumeRole
      Policies:
        - PolicyName: {role_name}-policy
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
{action_lines}
                Resource:
{resource_lines}
"""


def build_terraform_template(
    role_name: str,
    trust_policy: dict,
    permission_policy: dict,
) -> str:
    trust_policy_json = json.dumps(trust_policy, indent=2)
    permission_policy_json = json.dumps(permission_policy, indent=2)

    # Terraform permet aussi de decrire une infrastructure cloud en code.
    # Les blocs heredoc gardent ici les policies IAM en JSON lisible.
    return f"""resource "aws_iam_role" "generated_role" {{
  name = "{role_name}"

  assume_role_policy = <<POLICY
{trust_policy_json}
POLICY
}}

resource "aws_iam_role_policy" "generated_policy" {{
  name = "{role_name}-policy"
  role = aws_iam_role.generated_role.id

  policy = <<POLICY
{permission_policy_json}
POLICY
}}
"""
