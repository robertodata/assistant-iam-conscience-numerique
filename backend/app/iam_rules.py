# Ce fichier centralise les regles IAM connues par le projet.
# Il evite de disperser les actions, descriptions et risques dans plusieurs modules.
#
# Pour ajouter un nouveau service :
# 1. Ajouter une cle de service dans IAM_RULES, par exemple "sqs".
# 2. Ajouter une action fonctionnelle, par exemple "read" ou "write".
# 3. Renseigner la liste des actions IAM et les descriptions beginner/expert.
# 4. Ajouter les permissions sensibles dans IAM_SENSITIVE_RULES si necessaire.


IAM_RULES = {
    "s3": {
        "read": {
            "actions": [
                "s3:GetObject",
                "s3:ListBucket",
            ],
            "description_beginner": {
                "s3:GetObject": "s3:GetObject permet de lire des fichiers dans un bucket S3.",
                "s3:ListBucket": "s3:ListBucket permet de voir la liste des fichiers d'un bucket S3.",
            },
            "description_expert": {
                "s3:GetObject": "s3:GetObject autorise les operations GET sur les objets S3 et doit etre limite a des ARN precis.",
                "s3:ListBucket": "s3:ListBucket autorise l'enumeration du contenu d'un bucket et doit cibler l'ARN du bucket.",
            },
        },
        "write": {
            "actions": [
                "s3:PutObject",
            ],
            "description_beginner": {
                "s3:PutObject": "s3:PutObject permet d'ajouter ou modifier des fichiers dans un bucket S3.",
            },
            "description_expert": {
                "s3:PutObject": "s3:PutObject autorise l'ecriture d'objets S3 et doit etre limite aux prefixes necessaires.",
            },
        },
    },
    "dynamodb": {
        "read": {
            "actions": [
                "dynamodb:GetItem",
            ],
            "description_beginner": {
                "dynamodb:GetItem": "dynamodb:GetItem permet de lire un element dans une table DynamoDB.",
            },
            "description_expert": {
                "dynamodb:GetItem": "dynamodb:GetItem autorise la lecture d'items par cle primaire et doit cibler une table precise.",
            },
        },
        "write": {
            "actions": [
                "dynamodb:PutItem",
            ],
            "description_beginner": {
                "dynamodb:PutItem": "dynamodb:PutItem permet d'ecrire ou remplacer un element dans une table DynamoDB.",
            },
            "description_expert": {
                "dynamodb:PutItem": "dynamodb:PutItem autorise l'ecriture ou le remplacement d'items et doit cibler une table precise.",
            },
        },
    },
}


IAM_SENSITIVE_RULES = {
    "s3:DeleteBucket": {
        "severity": "high",
        "beginner_message": "Cette permission permet de supprimer un bucket S3.",
        "expert_message": "s3:DeleteBucket autorise la suppression complete d'un bucket S3 et peut provoquer une perte de service.",
        "beginner_recommendation": "A utiliser seulement dans des roles d'administration tres controles.",
        "expert_recommendation": "Limiter cette action a des roles break-glass, avec MFA, journalisation et ARN explicites.",
    },
    "iam:PassRole": {
        "severity": "high",
        "beginner_message": "Cette permission permet de transmettre un role IAM a un service AWS.",
        "expert_message": "iam:PassRole peut permettre l'escalade de privileges si le role transmis possede des droits eleves.",
        "beginner_recommendation": "Limiter cette permission a des roles precis avec une ressource ARN explicite.",
        "expert_recommendation": "Restreindre iam:PassRole par ARN et par condition iam:PassedToService.",
    },
    "iam:CreateUser": {
        "severity": "high",
        "beginner_message": "Cette permission permet de creer de nouveaux utilisateurs IAM.",
        "expert_message": "iam:CreateUser autorise la creation d'identites IAM persistantes.",
        "beginner_recommendation": "Eviter cette permission dans les roles applicatifs standards.",
        "expert_recommendation": "Reserver cette action aux workflows d'administration IAM controles et audites.",
    },
    "iam:AttachRolePolicy": {
        "severity": "high",
        "beginner_message": "Cette permission permet d'attacher des policies a un role IAM.",
        "expert_message": "iam:AttachRolePolicy peut augmenter les privileges d'un role en lui attachant une policy managed.",
        "beginner_recommendation": "Restreindre cette permission aux administrateurs IAM.",
        "expert_recommendation": "Limiter aux roles d'administration IAM et controler les ARN de policies autorisees.",
    },
}
