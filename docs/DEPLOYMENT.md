# Déploiement EC2

Ce document explique comment utiliser le script de déploiement EC2 du projet
Assistant IAM.

Le script ne crée aucune ressource AWS. Il sert uniquement à mettre à jour le
projet déjà présent sur une instance EC2.

## Script de déploiement

Le script se trouve ici :

```text
scripts/deploy-ec2.sh
```

Sur l'EC2, il se lance depuis la racine du projet avec :

```bash
bash scripts/deploy-ec2.sh
```

## Pourquoi ce script automatise les mises à jour

Sans script, il faudrait lancer manuellement toutes les commandes après chaque
nouvelle version du projet.

Le script automatise les étapes principales :

- récupérer la dernière version avec `git pull` ;
- mettre à jour les dépendances backend ;
- redémarrer le service backend FastAPI ;
- installer les dépendances frontend ;
- reconstruire le frontend Next.js ;
- redémarrer le service frontend ;
- recharger Apache.

Cela réduit les oublis et rend les mises à jour plus répétables.

## Workflow de déploiement

Le workflow cible est :

```text
Mac
↓
GitHub
↓
EC2
↓
deploy-ec2.sh
```

1. Sur le Mac, le code est modifié puis commit avec Git.
2. Le commit est envoyé sur GitHub.
3. Sur l'EC2, le projet récupère la dernière version avec `git pull`.
4. Le script `deploy-ec2.sh` met à jour backend, frontend et services.

## Ce que fait le script

Le script exécute :

```bash
cd /home/ec2-user/assistant-iam
git pull
cd backend
source .venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart assistant-iam-backend
cd ../frontend
npm install
npm run build
sudo systemctl restart assistant-iam-frontend
sudo systemctl reload httpd
```

## Conditions avant utilisation

Avant de lancer le script, vérifier que :

- le projet existe dans `/home/ec2-user/assistant-iam` ;
- le dépôt Git est bien configuré sur l'EC2 ;
- le backend possède un environnement virtuel `.venv` ;
- Node.js et npm sont installés ;
- les services `assistant-iam-backend` et `assistant-iam-frontend` existent ;
- Apache est utilisé et peut être rechargé avec `systemctl reload httpd`.

## Commande finale

```bash
bash scripts/deploy-ec2.sh
```
