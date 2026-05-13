# Plan de deploiement

Ce document prepare le futur deploiement du projet
`assistant-iam-conscience-numerique`.

Le projet n'est pas encore connecte a AWS et ce plan ne lance aucun
deploiement. Il sert uniquement a comparer des options simples pour une future
mise en ligne.

## Etat actuel du projet

- Frontend : application Next.js.
- Backend : API Python FastAPI.
- Base de donnees : aucune pour l'instant.
- Connexion AWS : aucune pour l'instant.
- IA externe : aucune pour l'instant.
- Sorties generees : IAM JSON, trust policy, CloudFormation YAML et Terraform.

## Option A : Frontend sur Vercel, backend sur AWS EC2 ou AWS Lambda

### Principe

Le frontend Next.js est deployee sur Vercel.
Le backend FastAPI est deployee separement sur AWS :

- soit sur une instance EC2 ;
- soit sous forme de fonction Lambda exposee par API Gateway.

### Avantages

- Vercel est tres simple pour deployer un frontend Next.js.
- Le frontend beneficie automatiquement d'une URL publique, du HTTPS et d'un
  workflow Git propre.
- Le backend reste separe, ce qui clarifie les responsabilites entre interface
  et API.
- Cette option ressemble a une architecture SaaS moderne.

### Inconvenients

- Il faut gerer la communication entre deux plateformes differentes.
- Il faut configurer CORS correctement entre Vercel et le backend AWS.
- Lambda + API Gateway demande plus de notions AWS que EC2.
- Le debug peut etre un peu moins direct pour un debutant.

### Difficulte

- Avec EC2 : moyenne.
- Avec Lambda + API Gateway : moyenne a elevee pour un debutant.

### Cout estime

- Vercel : faible au debut, selon l'offre utilisee.
- EC2 : faible a moyen selon la taille de l'instance et le temps d'execution.
- Lambda + API Gateway : faible au debut si le trafic reste limite.

### Recommandation pour debutant

Pour commencer, Vercel + EC2 est souvent plus simple a comprendre :

- Vercel s'occupe du frontend.
- EC2 permet de voir concretement comment tourne un serveur backend.

Lambda peut venir plus tard, quand le projet sera plus stable et que le besoin
serverless sera plus clair.

## Option B : Frontend et backend sur AWS EC2 au debut

### Principe

Le frontend Next.js et le backend FastAPI sont deployes sur une meme instance
AWS EC2.

Une configuration simple peut ressembler a ceci :

- FastAPI ecoute en local sur un port comme `8000`.
- Next.js est lance ou servi depuis la meme machine.
- Un reverse proxy comme Nginx pourra plus tard exposer proprement le frontend
  et router les appels API vers le backend.

### Avantages

- Une seule plateforme a comprendre : AWS EC2.
- Tout le projet est au meme endroit.
- Plus simple pour observer les logs et comprendre ce qui tourne.
- Bon choix pedagogique pour apprendre les bases du deploiement serveur.

### Inconvenients

- Il faut gerer soi-meme le serveur, les processus et les mises a jour.
- Il faut securiser l'instance EC2.
- Il faut configurer le HTTPS, le nom de domaine et le reverse proxy.
- Moins automatise qu'une plateforme comme Vercel pour le frontend.

### Difficulte

- Moyenne.
- Plus accessible que Lambda si l'objectif est de comprendre pas a pas ce qui
  se passe sur un serveur.

### Cout estime

- Faible a moyen.
- Le cout depend surtout du type d'instance EC2, du stockage et du temps
  pendant lequel l'instance reste allumee.

### Recommandation pour debutant

Cette option est la plus pedagogique pour un premier deploiement AWS complet.

Elle permet de comprendre :

- comment demarrer un backend FastAPI sur un serveur ;
- comment servir un frontend ;
- comment ouvrir les ports necessaires ;
- comment lire les logs ;
- comment preparer plus tard un vrai domaine et HTTPS.

## Recommandation generale

Pour un debutant, la meilleure progression est :

1. Deployement local verifie avec `pytest` et `next build`.
2. Premier deploiement simple sur une seule instance EC2.
3. Ajout d'un reverse proxy et du HTTPS.
4. Deploiement du frontend sur Vercel quand le backend est stable.
5. Eventuellement, migration du backend vers Lambda + API Gateway.

## Points a preparer avant un vrai deploiement

- Ajouter des variables d'environnement pour l'URL du backend cote frontend.
- Eviter les URLs locales codees en dur comme `http://127.0.0.1:8000`.
- Definir une configuration CORS adaptee au domaine de production.
- Ajouter une documentation de lancement en production.
- Prevoir une strategie de logs.
- Verifier les risques de securite avant toute connexion AWS reelle.
- Ne jamais stocker de secrets AWS dans le code source.

## Ce que ce plan ne fait pas

- Il ne cree aucune ressource AWS.
- Il ne connecte pas le projet a AWS.
- Il ne configure pas Vercel.
- Il ne modifie pas le code applicatif.
- Il ne deploie ni le frontend ni le backend.
