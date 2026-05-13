# Backend FastAPI en production simple

Ce document explique comment lancer le backend FastAPI du projet en local et
sur une machine Linux de production simple, par exemple une future instance AWS
EC2.

Ce guide ne connecte pas encore le projet a AWS et ne cree aucune ressource
cloud.

## Lancer le backend en local

Depuis la racine du projet :

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

En local, `--reload` est pratique car le serveur redemarre automatiquement
quand le code change.

Le backend est ensuite disponible sur :

```text
http://127.0.0.1:8000
```

## Lancer le backend en production Linux

Depuis la racine du projet :

```bash
cd backend
./start.sh
```

Le script `start.sh` fait deux choses :

```bash
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Il active l'environnement virtuel Python, puis lance FastAPI avec Uvicorn sans
mode `--reload`.

## Difference entre localhost et 0.0.0.0

`localhost` ou `127.0.0.1` signifie que le backend ecoute seulement sur la
machine elle-meme.

C'est adapte au developpement local, mais pas suffisant pour exposer une API a
un navigateur ou a une autre machine.

`0.0.0.0` signifie que le backend ecoute sur toutes les interfaces reseau de la
machine.

Sur une instance Linux comme EC2, c'est necessaire pour rendre le service
accessible depuis l'exterieur, a condition que les regles reseau et de securite
autorisent aussi le trafic.

## Pourquoi enlever --reload en production

Le mode `--reload` sert au developpement.

En production, on l'evite car :

- il surveille les fichiers en continu ;
- il peut redemarrer le serveur de maniere inattendue ;
- il consomme des ressources inutiles ;
- il n'est pas concu comme mode stable de production.

En production simple, on lance donc :

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Preparation future pour systemd ou Docker

Pour un vrai deploiement durable, `./start.sh` est une premiere etape utile,
mais il faudra plus tard automatiser le demarrage du backend.

Deux options simples :

- `systemd` : permet de demarrer automatiquement le backend au boot de la
  machine, de le relancer en cas d'erreur et de consulter les logs avec
  `journalctl`.
- Docker : permet d'emballer le backend dans une image reproductible, plus
  facile a deployer sur plusieurs environnements.

Pour debuter sur EC2, `systemd` est souvent le plus direct.
Docker devient interessant quand le projet grandit ou quand on veut standardiser
l'environnement d'execution.

## Verification rapide

Avant un futur deploiement, verifier que les tests passent :

```bash
cd backend
pytest
```

Verifier aussi que Python peut compiler les fichiers du backend :

```bash
python -m compileall app
```
