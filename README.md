# Assistant IAM Conscience Numérique

Assistant IAM intelligent pour AWS, basé sur un moteur NLP pédagogique, une
analyse de sécurité IAM et une première intégration OpenAI.

Le projet aide à transformer une demande en langage naturel en permissions IAM
compréhensibles, avec génération d'ARN, recommandations de sécurité et exports
Infrastructure as Code.

## Vision

L'objectif est de construire progressivement un assistant SaaS capable d'aider
un utilisateur à comprendre, générer et sécuriser des permissions AWS IAM.

Le MVP met l'accent sur :

- la pédagogie IAM ;
- le principe du moindre privilège ;
- la détection de risques simples ;
- la génération d'exports réutilisables ;
- l'intégration progressive de l'IA.

## Fonctionnalités

- Analyse IAM en langage naturel.
- Détection de services AWS et d'intentions IAM.
- Génération de permissions IAM proposées.
- Sélection interactive des permissions.
- Génération intelligente d'ARN AWS.
- Application automatique du Least Privilege lorsque la ressource est détectée.
- Intégration OpenAI pour expliquer des concepts IAM.
- Génération de policy IAM JSON.
- Export Terraform.
- Export CloudFormation.
- Score de risque IAM.
- Recommandations de sécurité.
- Historique local des générations.
- Tests backend automatisés.

## Architecture

```text
Utilisateur
↓
Frontend Next.js
↓
FastAPI backend
↓
Moteur IAM NLP
↓
OpenAI
↓
Génération IAM
```

### Frontend

- Next.js
- React
- TypeScript
- CSS global sobre et responsive

Le frontend permet :

- d'analyser une demande IAM ;
- de sélectionner les actions IAM proposées ;
- de visualiser une policy JSON ;
- de copier ou exporter les résultats ;
- d'interroger l'assistant IA IAM.

### Backend

- FastAPI
- Python
- Pytest

Le backend contient :

- un catalogue de services AWS ;
- un moteur NLP IAM déterministe ;
- un générateur d'ARN ;
- un générateur de policies ;
- un analyseur de sécurité ;
- une intégration OpenAI contrôlée par variable d'environnement.

### Infrastructure

Le projet est préparé pour une exécution sur :

- AWS EC2 ;
- Apache en reverse proxy ;
- HTTPS via Let's Encrypt ;
- backend FastAPI en service Linux ;
- frontend Next.js en mode production.

### CI/CD

- GitHub Actions
- Job backend : installation Python et `pytest`
- Job frontend : installation Node.js et build Next.js
- Pas de déploiement automatique pour l'instant

## Structure du projet

```text
assistant-iam-conscience-numerique/
├── backend/
│   ├── app/
│   │   ├── ai_provider.py
│   │   ├── arn_generator.py
│   │   ├── aws_service_catalog.py
│   │   ├── iam_analyzer.py
│   │   ├── iam_engine.py
│   │   ├── iam_rules.py
│   │   ├── iam_validator.py
│   │   ├── iac_generator.py
│   │   ├── main.py
│   │   ├── nlp_parser.py
│   │   └── security_analyzer.py
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── globals.css
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── Dockerfile
│   └── package.json
├── docs/
├── scripts/
└── README.md
```

## Installation locale

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Vérifier le backend :

```bash
curl http://127.0.0.1:8000/health
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Le frontend local est disponible sur :

```text
http://localhost:3000
```

### Tests backend

Depuis la racine du projet :

```bash
PYTHONPATH=backend pytest backend/tests
```

Ou depuis le dossier `backend` :

```bash
pytest
```

## Variables d'environnement

### Backend

Créer un fichier `.env` côté backend si nécessaire :

```env
OPENAI_API_KEY=sk-...
```

Si la clé est absente ou vaut `YOUR_OPENAI_API_KEY`, le backend retourne une
réponse IA simulée. La clé API ne doit jamais être commitée.

### Frontend

Créer `frontend/.env.local` :

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

En production, cette variable peut pointer vers l'API publique :

```env
NEXT_PUBLIC_API_URL=https://consciencenumerique.com/api
```

## Endpoints principaux

```text
GET  /health
GET  /ai/status
POST /ai/explain
GET  /iam/services
POST /iam/analyze
POST /parse-request
POST /generate-policy
```

Exemple d'analyse IAM :

```bash
curl -X POST http://127.0.0.1:8000/iam/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "request": "Je veux pousser une image Docker dans le repository backend-api"
  }'
```

Exemple de réponse :

```json
{
  "request": "Je veux pousser une image Docker dans le repository backend-api",
  "services": ["ecr"],
  "intents": ["push"],
  "actions": [
    "ecr:GetAuthorizationToken",
    "ecr:BatchCheckLayerAvailability",
    "ecr:InitiateLayerUpload",
    "ecr:UploadLayerPart",
    "ecr:CompleteLayerUpload",
    "ecr:PutImage"
  ],
  "resource_name": "backend-api",
  "resource_arn": "arn:aws:ecr:eu-west-3:123456789012:repository/backend-api",
  "risk_level": "low",
  "recommendations": [
    "Least privilege appliqué automatiquement."
  ]
}
```

## Déploiement EC2

Le projet est documenté pour un déploiement Linux simple sur EC2.

Workflow recommandé :

```text
Développement local
↓
Commit Git
↓
Push GitHub
↓
Connexion EC2
↓
bash scripts/deploy-ec2.sh
```

Le script de déploiement effectue :

- `git pull`
- installation des dépendances backend ;
- build frontend ;
- redémarrage des services systemd ;
- reload Apache.

Commande côté serveur :

```bash
bash scripts/deploy-ec2.sh
```

Documentation complémentaire :

- `docs/DEPLOYMENT.md`
- `docs/BACKEND_PRODUCTION.md`
- `docs/FRONTEND_PRODUCTION.md`
- `docs/AWS_EC2_ARCHITECTURE.md`
- `docs/NGINX_EXPLANATION.md`

## Captures écran

> Placeholders à remplacer par de vraies captures du SaaS.

### Analyse IAM intelligente

```text
[Screenshot placeholder: formulaire d'analyse IAM avec actions proposées]
```

### Policy JSON générée

```text
[Screenshot placeholder: policy JSON interactive avec ARN généré]
```

### Assistant IA IAM

```text
[Screenshot placeholder: réponse OpenAI dans l'interface]
```

## Sécurité

Le projet met en avant plusieurs bonnes pratiques IAM :

- éviter `Resource: "*"` ;
- préférer des ARN précis ;
- identifier les permissions sensibles ;
- afficher un score de risque ;
- séparer trust policy et permission policy ;
- conserver les clés API hors du code source.

Ce projet ne déploie pas automatiquement de ressources AWS.

## Roadmap

- IAM Simulator.
- Terraform avancé.
- Multi-services complexes.
- Analyse de policies existantes.
- Fonctionnalités proches de IAM Access Analyzer.
- Explication IA permission par permission.
- Détection automatique des ressources depuis un compte AWS.
- Génération de rôles IAM prêts pour production.
- Gestion multi-comptes et multi-régions.

## Statut

Projet MVP actif, orienté portfolio, pédagogie cloud security et préparation
SaaS.
