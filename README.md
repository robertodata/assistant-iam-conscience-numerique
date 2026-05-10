# assistant-iam-conscience-numerique

## Vision du projet

`assistant-iam-conscience-numerique` est un MVP d'assistant IAM pedagogique.
Son objectif est d'aider a comprendre comment construire un role AWS IAM plus
sur, en partant d'un besoin simple : un service AWS, une action, un type de role
et une ressource cible.

A terme, le projet pourra evoluer vers un assistant intelligent capable de
recommander des policies IAM securisees. Pour l'instant, il reste volontairement
simple : aucune IA, aucune connexion AWS et aucun deploiement cloud.

## Fonctionnalites actuelles

- Generation d'un role IAM simple pour Lambda ou EC2.
- Generation d'une trust policy selon le type de role choisi.
- Generation d'une permission policy pour S3 ou DynamoDB.
- Support des actions `read` et `write`.
- Generation d'ARN simples a partir d'un nom de ressource.
- Warning lorsque `Resource` vaut `"*"`.
- Explication pedagogique des permissions IAM generees.
- Analyse de securite IAM avec findings, score et niveau de risque.
- Export d'un template CloudFormation simple.
- Export d'un template Terraform simple.
- Interface Next.js avec selecteurs dynamiques.
- Copie de la policy JSON, du template CloudFormation et du template Terraform.
- Tests backend automatises avec `pytest`.

## Objectif pedagogique

Ce projet sert a comprendre progressivement plusieurs notions importantes :

- IAM et les permissions AWS.
- Le principe du Least Privilege.
- La difference entre une trust policy et une permission policy.
- Le role des ARN pour cibler des ressources precises.
- Les risques lies a `Resource: "*"` ou aux permissions trop larges.
- Les bases de l'Infrastructure as Code avec CloudFormation et Terraform.

L'application est donc volontairement explicite et lisible, afin de rester utile
pour un apprentissage pas a pas.

## Architecture technique

```text
assistant-iam-conscience-numerique/
├── backend/
│   ├── app/
│   │   ├── iac_generator.py
│   │   ├── iam_engine.py
│   │   ├── main.py
│   │   └── security_analyzer.py
│   ├── tests/
│   │   └── test_generate_policy.py
│   └── requirements.txt
├── docs/
│   └── README.md
├── frontend/
│   ├── app/
│   │   ├── globals.css
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── next-env.d.ts
│   ├── next.config.mjs
│   ├── package.json
│   └── tsconfig.json
└── README.md
```

### Backend

Le backend FastAPI expose l'API principale du projet.

- `main.py` contient l'application FastAPI et les routes.
- `iam_engine.py` contient la logique IAM.
- `security_analyzer.py` contient l'analyse de securite.
- `iac_generator.py` contient la generation CloudFormation et Terraform.

### Frontend

Le frontend Next.js permet de configurer un role IAM depuis une interface simple.
Il appelle le backend avec `fetch()`, puis affiche la policy, les explications,
le score de securite et les sorties Infrastructure as Code.

## Technologies utilisees

- Next.js
- React
- TypeScript
- Python
- FastAPI
- Pytest
- CloudFormation
- Terraform

## Lancer le backend

Depuis la racine du projet :

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Le backend est disponible sur :

```text
http://127.0.0.1:8000
```

Endpoint de verification :

```text
GET http://127.0.0.1:8000/health
```

## Lancer le frontend

Depuis la racine du projet :

```bash
cd frontend
npm install
npm run dev
```

Le frontend est disponible sur :

```text
http://localhost:3000
```

## Lancer les tests

Depuis le dossier `backend`, avec l'environnement virtuel active :

```bash
pytest
```

## Exemple de requete API

```bash
curl -X POST http://127.0.0.1:8000/generate-policy \
  -H "Content-Type: application/json" \
  -d '{
    "service": "s3",
    "action": "read",
    "aws_service_type": "lambda",
    "resource_name": "mon-bucket"
  }'
```

## Exemple de reponse generee

```json
{
  "role_name": "lambda-s3-read-role",
  "trust_policy": {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Principal": {
          "Service": "lambda.amazonaws.com"
        },
        "Action": "sts:AssumeRole"
      }
    ]
  },
  "policy": {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": [
          "s3:GetObject",
          "s3:ListBucket"
        ],
        "Resource": [
          "arn:aws:s3:::mon-bucket",
          "arn:aws:s3:::mon-bucket/*"
        ]
      }
    ]
  },
  "warnings": [],
  "explanations": [
    {
      "permission": "s3:GetObject",
      "description": "Permet de lire les objets dans un bucket S3."
    },
    {
      "permission": "s3:ListBucket",
      "description": "Permet de lister le contenu d'un bucket S3."
    }
  ],
  "security_findings": [],
  "security_score": 100,
  "security_level": "Bon",
  "cloudformation_template": "AWSTemplateFormatVersion: '2010-09-09'...",
  "terraform_template": "resource \"aws_iam_role\" \"generated_role\" {...}"
}
```

## Ce que le projet ne fait pas encore

- Pas encore d'IA.
- Pas encore de connexion AWS reelle.
- Pas encore d'audit automatique de compte AWS.
- Pas encore de validation exhaustive des permissions IAM AWS.
- Pas encore de deploiement CloudFormation ou Terraform.

## Roadmap future

- Ajouter plus de services AWS.
- Ajouter plus d'actions IAM.
- Ameliorer le moteur d'analyse de securite.
- Ajouter une generation de role IAM plus complete.
- Ajouter une validation plus precise des ARN.
- Ajouter une future couche IA pour traduire un besoin utilisateur en policy.
- Ajouter un mode audit pour analyser des policies existantes.
