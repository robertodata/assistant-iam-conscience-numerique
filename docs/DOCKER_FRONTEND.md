# Docker pour le frontend Next.js

Ce document explique comment preparer le frontend Next.js avec Docker.

Cette etape ne remplace pas la production actuelle. Le site peut continuer a
tourner avec le lancement Linux direct, `systemd`, Apache ou la configuration
existante.

## Objectif

Le fichier `frontend/Dockerfile` permet de construire une image Docker du
frontend.

Cette image contient :

- Node.js ;
- les dependances npm ;
- le code Next.js ;
- le build de production ;
- la commande `npm run start`.

## Build de l'image frontend

Depuis la racine du projet :

```bash
cd frontend
sudo docker build -t assistant-iam-frontend .
```

Cette commande construit une image nommee `assistant-iam-frontend`.

## Lancer un conteneur frontend

Pour lancer le frontend Docker en test :

```bash
sudo docker run -d -p 3002:3000 --name assistant-iam-frontend-test assistant-iam-frontend
```

Explication :

- `-d` lance le conteneur en arriere-plan ;
- `-p 3002:3000` expose le port `3000` du conteneur sur le port `3002` de la
  machine ;
- `--name assistant-iam-frontend-test` donne un nom clair au conteneur ;
- `assistant-iam-frontend` est l'image utilisee.

Le port `3002` permet de tester Docker sans prendre la place du frontend actuel
qui peut deja utiliser le port `3000`.

## Tester localement le frontend Docker

Une fois le conteneur lance, ouvrir :

```text
http://127.0.0.1:3002
```

Ou tester rapidement avec :

```bash
curl http://127.0.0.1:3002
```

Pour voir les logs :

```bash
sudo docker logs assistant-iam-frontend-test
```

Pour arreter puis supprimer le conteneur de test :

```bash
sudo docker stop assistant-iam-frontend-test
sudo docker rm assistant-iam-frontend-test
```

## Difference entre Linux direct et Docker

### Linux direct

En mode Linux direct, le frontend est lance directement sur la machine.

Exemple :

```bash
npm install
npm run build
npm run start
```

Cette approche est simple pour un premier deploiement EC2.

### Docker

Avec Docker, le frontend tourne dans un conteneur isole.

Cela permet :

- de mieux controler l'environnement Node.js ;
- de reduire les differences entre machines ;
- de reconstruire une image propre a chaque version ;
- de preparer une future architecture Docker Compose ou ECS.

## Pourquoi on ne remplace pas encore la production actuelle

Docker frontend est ajoute pour preparer une evolution future.

On ne remplace pas encore la production actuelle car :

- la configuration existante doit rester stable ;
- Apache et `systemd` peuvent deja servir le site ;
- il faut tester Docker sans casser le trafic utilisateur ;
- il faudra plus tard adapter le reverse proxy pour pointer vers le conteneur.

## Prochaine evolution possible

Plus tard, le projet pourra ajouter :

- un script de lancement Docker frontend ;
- un `docker-compose.yml` pour frontend et backend ;
- une configuration Apache ou Nginx qui pointe vers les conteneurs ;
- une migration vers ECS si le projet devient plus cloud-native.
