# Documentation du projet

## But du projet

Le projet `assistant-iam-conscience-numerique` a pour objectif de construire progressivement un assistant IAM intelligent.

A terme, cet assistant devra aider un utilisateur a transformer un besoin simple en policy AWS IAM securisee, claire et limitee aux permissions necessaires.

Pour cette premiere etape, le projet ne contient pas encore :

- d'integration avec une IA ;
- de connexion a AWS ;
- de generation reelle de policies IAM.

Il contient uniquement une base technique simple pour organiser le frontend, le backend et la documentation.

## Role du frontend

Le dossier `frontend/` contient l'application Next.js.

Son role sera d'afficher l'interface utilisateur. Plus tard, c'est ici que l'utilisateur pourra decrire son besoin IAM dans un formulaire ou une interface de discussion.

Pour l'instant, le frontend affiche seulement une page d'accueil avec le titre du projet et une courte description.

## Role du backend

Le dossier `backend/` contient l'application Python FastAPI.

Son role sera de recevoir les demandes du frontend, de traiter la logique metier, puis de retourner des reponses structurees.

Pour l'instant, le backend expose uniquement un endpoint de sante :

```text
GET /health
```

Cet endpoint retourne :

```json
{"status": "ok"}
```

## Fonctionnement general

L'architecture est separee en deux parties :

- le frontend Next.js gere l'affichage et les interactions utilisateur ;
- le backend FastAPI gere les endpoints API et la logique serveur.

Dans une future version, le frontend pourra envoyer au backend une description du besoin utilisateur. Le backend pourra ensuite analyser cette demande et preparer une reponse IAM.

Cette separation permet de faire evoluer chaque partie du projet progressivement, sans melanger l'interface utilisateur et la logique serveur.

