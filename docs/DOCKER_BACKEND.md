# Docker pour le backend FastAPI

Ce document explique le workflow Docker du backend FastAPI du projet
`assistant-iam-conscience-numerique`.

Docker est prepare ici comme une evolution future. Il ne remplace pas encore le
lancement actuel avec `systemd`.

## Definition simple de Docker

Docker est un outil qui permet d'executer une application dans un environnement
isole appele conteneur.

Avec Docker, on peut regrouper dans une meme unite :

- le systeme minimal necessaire ;
- Python ;
- les dependances du backend ;
- le code FastAPI ;
- la commande de lancement.

Cela rend l'application plus facile a tester et plus reproductible entre
plusieurs machines.

## Image vs conteneur

Une image Docker est un modele pret a etre lance.

Elle contient tout ce qui est necessaire pour demarrer l'application, mais elle
n'est pas encore en cours d'execution.

Un conteneur Docker est une instance lancee a partir d'une image.

On peut resumer ainsi :

```text
Dockerfile -> image Docker -> conteneur en cours d'execution
```

Dans ce projet :

- l'image s'appelle `assistant-iam-backend` ;
- le conteneur de test peut s'appeler `assistant-iam-backend-test`.

## Qu'est-ce qu'un Dockerfile ?

Un `Dockerfile` est un fichier qui decrit comment construire une image Docker.

Dans ce projet, `backend/Dockerfile` :

- utilise `python:3.11-slim` ;
- definit le dossier de travail `/app` ;
- copie `requirements.txt` ;
- installe les dependances Python ;
- copie le code backend ;
- expose le port `8000` ;
- lance FastAPI avec Uvicorn.

## Builder l'image backend

Depuis la racine du projet, aller dans le backend :

```bash
cd backend
```

Puis construire l'image :

```bash
sudo docker build -t assistant-iam-backend .
```

Cette commande lit le `Dockerfile` et cree une image Docker nommee
`assistant-iam-backend`.

## Lancer un conteneur de test

Pour lancer un conteneur de test en arriere-plan :

```bash
sudo docker run -d -p 8002:8000 --name assistant-iam-backend-test assistant-iam-backend
```

Explication :

- `-d` lance le conteneur en arriere-plan ;
- `-p 8002:8000` expose le port `8000` du conteneur sur le port `8002` de la
  machine ;
- `--name assistant-iam-backend-test` donne un nom clair au conteneur ;
- `assistant-iam-backend` est l'image utilisee.

Le port `8002` est utilise ici pour eviter de perturber un backend FastAPI deja
lance sur le port `8000`.

## Tester le backend Docker

Pour verifier que le conteneur repond :

```bash
curl http://127.0.0.1:8002/health
```

La reponse attendue est :

```json
{"status":"ok"}
```

## Voir les logs du conteneur

Pour lire les logs :

```bash
sudo docker logs assistant-iam-backend-test
```

Les logs permettent de verifier que Uvicorn a bien demarre et que les requetes
arrivent jusqu'au backend.

## Arreter et supprimer le conteneur de test

Arreter le conteneur :

```bash
sudo docker stop assistant-iam-backend-test
```

Supprimer le conteneur :

```bash
sudo docker rm assistant-iam-backend-test
```

Ces deux commandes nettoient le test sans supprimer l'image Docker.

## Verifier l'espace Docker utilise

Pour voir l'espace disque utilise par Docker :

```bash
sudo docker system df
```

Cette commande est utile sur une EC2, car les images et conteneurs peuvent
prendre de la place avec le temps.

## Role de .dockerignore

Le fichier `backend/.dockerignore` evite de copier dans l'image Docker des
fichiers inutiles ou locaux :

- `.venv`
- `__pycache__`
- `.pytest_cache`
- `*.pyc`

Cela garde l'image plus propre et evite d'envoyer des fichiers de developpement
dans le conteneur.

## Pourquoi on ne remplace pas encore systemd par Docker

Le backend peut deja etre lance sur EC2 avec `systemd`.

Pour l'instant, on ne remplace pas encore `systemd` par Docker car :

- le deploiement actuel doit rester stable ;
- WordPress ou d'autres services peuvent deja tourner sur la meme EC2 ;
- Docker change la maniere de gerer les logs, les ports et les redemarrages ;
- il faut aussi reflechir au frontend, a Nginx ou Apache, et au workflow de
  deploiement complet ;
- une migration progressive limite le risque de casser l'existant.

Docker sert donc d'abord a tester une execution isolee du backend. Quand le
workflow sera bien compris, il pourra devenir la base d'une architecture plus
standardisee.

## Prochaine evolution : Docker Compose ou ECS

Deux evolutions possibles :

- Docker Compose : utile pour lancer localement plusieurs services ensemble,
  par exemple backend, frontend et reverse proxy.
- Amazon ECS : service AWS permettant d'executer des conteneurs de maniere plus
  industrielle, avec une meilleure gestion du deploiement et du scaling.

Pour debuter, Docker Compose est souvent plus simple a comprendre.

ECS pourra venir plus tard si le projet doit devenir plus proche d'une
architecture cloud production.
