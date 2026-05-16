# Docker pour le backend FastAPI

Ce document explique comment preparer le backend FastAPI avec Docker.

Cette etape ne remplace pas encore le lancement actuel avec `systemd`. Elle
ajoute seulement une base Docker pour tester et preparer une evolution future.

## Qu'est-ce qu'un Dockerfile ?

Un `Dockerfile` est un fichier qui decrit comment construire une image Docker.

Une image Docker contient :

- une base systeme ;
- Python ;
- les dependances du backend ;
- le code de l'application ;
- la commande de lancement du serveur.

Dans ce projet, le fichier `backend/Dockerfile` prepare une image capable de
lancer FastAPI avec Uvicorn sur le port `8000`.

## Construire l'image Docker

Depuis la racine du projet :

```bash
cd backend
docker build -t assistant-iam-backend .
```

Cette commande lit le `Dockerfile`, installe les dependances Python et cree une
image appelee `assistant-iam-backend`.

## Lancer le conteneur

Apres le build :

```bash
docker run --rm -p 8000:8000 assistant-iam-backend
```

Cette commande lance le backend dans un conteneur et expose le port `8000`.

Le backend devrait ensuite etre accessible sur :

```text
http://127.0.0.1:8000
```

## Role de .dockerignore

Le fichier `backend/.dockerignore` evite de copier dans l'image Docker des
fichiers inutiles ou locaux :

- `.venv`
- `__pycache__`
- `.pytest_cache`
- `*.pyc`

Cela rend l'image plus propre et evite d'envoyer des fichiers de developpement
dans le conteneur.

## Pourquoi on ne remplace pas encore systemd

Actuellement, le projet est prepare pour un deploiement EC2 simple avec
`systemd`.

On ne remplace pas encore `systemd` par Docker car :

- le deploiement actuel doit rester stable ;
- Docker ajoute une couche d'exploitation supplementaire ;
- il faudra plus tard definir une strategie complete pour le frontend, le
  backend, les logs et le reverse proxy ;
- un changement progressif est plus prudent sur une EC2 qui peut deja heberger
  d'autres services.

Docker est donc prepare comme evolution future, pas comme remplacement immediat.

## Commande lancee dans le conteneur

Le conteneur lance :

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

`0.0.0.0` permet au serveur d'ecouter dans le conteneur et d'etre accessible via
le port publie avec `docker run -p`.

## Prochaine evolution possible

Plus tard, le projet pourra ajouter :

- un `docker-compose.yml` ;
- un conteneur frontend ;
- une configuration de logs Docker ;
- une integration avec Nginx ;
- une pipeline CI/CD qui construit l'image automatiquement.
