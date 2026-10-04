# Assistant IAM Conscience Numérique

Ce projet part d'un besoin simple : rendre AWS IAM plus lisible.

Au lieu de demander à quelqu'un de connaître immédiatement les noms exacts des
permissions AWS, l'assistant accepte une demande formulée en langage courant,
essaie d'identifier le service concerné, propose les actions IAM utiles, construit
les ARN quand il dispose d'assez d'informations et signale les permissions qui
méritent une attention particulière.

Le projet sert à la fois de laboratoire technique, de support pédagogique et de
base pour une future intégration dans Conscience Numérique.

## Ce que l'assistant sait faire aujourd'hui

Le MVP permet notamment de :

- analyser une demande IAM écrite en langage naturel ;
- reconnaître plusieurs services AWS courants ;
- proposer des actions IAM adaptées à l'intention détectée ;
- générer une trust policy et une permission policy ;
- construire des ARN pour plusieurs types de ressources ;
- attirer l'attention sur `Resource: "*"`, les wildcards et certaines
  permissions sensibles ;
- produire un score de risque simple ;
- générer des exemples Terraform et CloudFormation ;
- fournir une explication pédagogique via OpenAI lorsque cette intégration est
  configurée ;
- conserver un historique local côté interface ;
- vérifier le backend et le build du frontend avec GitHub Actions.

L'analyse principale reste volontairement déterministe. L'appel à un modèle IA
n'est pas utilisé pour décider automatiquement quelles permissions doivent être
accordées.

## Architecture

```text
Utilisateur
   |
   v
Frontend Next.js
   |
   v
API FastAPI
   |
   +--> moteur IAM / règles locales
   |
   +--> analyse de sécurité
   |
   +--> génération JSON / Terraform / CloudFormation
   |
   `--> OpenAI pour les explications, si activé
```

### Backend

Le backend est écrit en Python avec FastAPI.

Les principaux modules se trouvent dans `backend/app/` :

- `iam_analyzer.py` : analyse d'une demande libre ;
- `nlp_parser.py` : interprétation des formulations simples ;
- `iam_rules.py` : règles IAM connues par le projet ;
- `arn_generator.py` : construction des ARN ;
- `iam_engine.py` : génération des rôles et policies ;
- `iam_validator.py` : validation de règles sensibles ;
- `security_analyzer.py` : score et constats de sécurité ;
- `iac_generator.py` : exports Terraform et CloudFormation ;
- `ai_provider.py` : explications via OpenAI.

### Frontend

L'interface est construite avec Next.js, React et TypeScript.

Elle permet de partir d'un besoin en français, d'examiner les permissions
proposées et de consulter les différents résultats avant de les exporter.

## Lancer le projet en local

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Vérification rapide :

```bash
curl http://127.0.0.1:8000/health
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

L'interface est alors disponible sur :

```text
http://localhost:3000
```

## Configuration

Les vraies valeurs d'environnement ne doivent pas être versionnées.

Des modèles sont fournis dans :

- `backend/.env.example`
- `frontend/.env.example`

Pour le backend, les variables principales sont :

```env
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4.1-mini
AI_MAX_TOKENS=200
AI_TIMEOUT_SECONDS=20

AWS_REGION=eu-west-3
AWS_ACCOUNT_ID=123456789012

CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

`AWS_ACCOUNT_ID=123456789012` est une valeur d'exemple. En production, il faut
la remplacer par l'identifiant du compte concerné.

Pour le frontend :

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

Sur Conscience Numérique, cette valeur pourra pointer vers l'API exposée par
Apache, par exemple :

```env
NEXT_PUBLIC_API_URL=https://consciencenumerique.com/api/iam
```

## Endpoints principaux

```text
GET  /health
GET  /ai/status
GET  /iam/services
POST /iam/analyze
POST /parse-request
POST /generate-policy
POST /ai/explain
```

Exemple :

```bash
curl -X POST http://127.0.0.1:8000/iam/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "request": "Je veux pousser une image Docker dans le repository backend-api"
  }'
```

Une réponse peut ressembler à ceci :

```json
{
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
  "risk_level": "low"
}
```

## Tests et intégration continue

Les tests backend peuvent être lancés depuis la racine :

```bash
PYTHONPATH=backend pytest backend/tests
```

Le workflow GitHub Actions vérifie également :

- les tests Python ;
- le build Next.js.

Le déploiement vers EC2 reste volontairement manuel pour le moment.

## Déploiement sur l'EC2 Conscience Numérique

Le serveur Conscience Numérique utilise Apache. L'objectif n'est donc pas
d'installer un second serveur web, mais d'intégrer proprement l'assistant derrière
l'Apache déjà en place.

La documentation correspondante se trouve dans :

- `docs/PRODUCTION_APACHE.md`
- `docs/EXISTING_EC2_AUDIT.md`
- `docs/BACKEND_PRODUCTION.md`
- `docs/FRONTEND_PRODUCTION.md`

Le script `scripts/deploy-ec2.sh` prépare le cycle classique : récupération du
code, installation des dépendances, build du frontend, redémarrage des services
et reload d'Apache.

## Sécurité

Le dépôt ne contient pas de clé AWS ni de clé OpenAI réelle.

Les fichiers `.env` sont ignorés par Git. Seuls les modèles
`.env.example` doivent être versionnés.

Avant d'ouvrir l'API à des utilisateurs externes, il restera à ajouter :

- une authentification ;
- une limitation du nombre de requêtes ;
- des quotas sur les fonctions qui peuvent générer un coût ;
- un suivi de consommation ;
- une revue plus poussée des policies avant application sur un compte réel.

Les règles de sécurité du projet sont précisées dans `SECURITY.md`.

## Suite prévue

Les prochaines étapes prévues sont surtout fonctionnelles :

- simulation IAM plus avancée ;
- analyse de policies existantes ;
- meilleure couverture des services AWS ;
- gestion multi-régions et multi-comptes ;
- découpage du frontend en composants plus petits ;
- intégration progressive dans la plateforme Conscience Numérique.

Le projet reste un MVP actif. Il est suffisamment structuré pour servir de base
solide, mais il ne cherche pas encore à remplacer les outils natifs d'AWS ni une
revue IAM professionnelle.
