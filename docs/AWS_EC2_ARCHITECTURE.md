# Architecture AWS EC2 cible

Ce document decrit une architecture cible simple pour heberger le projet
`assistant-iam-conscience-numerique` sur AWS EC2.

Il s'agit d'une preparation pedagogique. Aucune ressource AWS n'est creee pour
l'instant.

## Qu'est-ce qu'une instance EC2 ?

EC2 signifie Elastic Compute Cloud.

Une instance EC2 est une machine virtuelle louee sur AWS. Elle fonctionne comme
un serveur distant sur lequel on peut installer Linux, Python, Node.js, Nginx et
l'application.

Dans ce projet, une instance EC2 pourra heberger :

- le frontend Next.js ;
- le backend FastAPI ;
- Nginx comme point d'entree web.

## Pourquoi utiliser Linux ?

Linux est tres utilise pour heberger des applications web.

Il est adapte a ce projet car :

- il est stable pour faire tourner des serveurs ;
- il est bien supporte par AWS EC2 ;
- il fonctionne bien avec Python, Node.js et Nginx ;
- il permet d'automatiser facilement les services avec `systemd` ou Docker ;
- il ressemble a l'environnement utilise dans beaucoup d'architectures
  professionnelles.

## Role de Nginx

Nginx sera le point d'entree public du serveur.

Son role sera de recevoir les requetes venant d'Internet, puis de les transmettre
au bon service interne :

- le frontend Next.js pour l'interface utilisateur ;
- le backend FastAPI pour les appels API.

Nginx permet aussi, plus tard, d'ajouter HTTPS avec un certificat TLS.

## Role du frontend Next.js

Le frontend Next.js est l'interface visible par l'utilisateur.

Il affiche :

- le formulaire IAM ;
- l'analyse NLP ;
- l'aperçu final ;
- les policies IAM ;
- les exports JSON, CloudFormation et Terraform.

Sur EC2, il pourra tourner sur le port `3000`.

## Role du backend FastAPI

Le backend FastAPI contient la logique serveur.

Il recoit les demandes du frontend, puis retourne :

- le role IAM genere ;
- la trust policy ;
- la permission policy ;
- les explications ;
- les findings de securite ;
- les templates CloudFormation et Terraform.

Sur EC2, il pourra tourner sur le port `8000`.

## Schema cible

```text
Utilisateur Internet
↓
Nom de domaine
↓
Nginx (port 80 / 443)
↓
Frontend Next.js (3000)
↓
Backend FastAPI (8000)
```

Dans cette architecture, l'utilisateur ne parle pas directement a Next.js ou a
FastAPI. Il passe d'abord par Nginx.

## Ports utilises

### 80 = HTTP

Le port `80` est le port standard pour le trafic web non chiffre.

Il peut servir au premier test ou rediriger ensuite vers HTTPS.

### 443 = HTTPS

Le port `443` est le port standard pour le trafic web chiffre avec TLS.

En production, c'est le port a privilegier pour securiser les connexions.

### 3000 = frontend Next.js

Le port `3000` est utilise par Next.js.

Dans une architecture propre, il reste interne a la machine EC2. Le public ne
devrait pas appeler directement ce port.

### 8000 = backend FastAPI

Le port `8000` est utilise par FastAPI.

Lui aussi devrait rester interne a la machine EC2. Les appels API publics
passent par Nginx, qui redirige ensuite vers FastAPI.

## Security Group AWS

Un Security Group AWS agit comme un pare-feu autour de l'instance EC2.

Pour cette architecture, l'approche simple est :

- ouvrir le port `80` au public pour HTTP ;
- ouvrir le port `443` au public pour HTTPS ;
- eviter d'ouvrir les ports `3000` et `8000` directement au public ;
- garder `3000` et `8000` accessibles seulement depuis la machine elle-meme.

Cette approche est plus propre car l'utilisateur passe par Nginx.

Nginx protege l'architecture en jouant le role de point d'entree unique. Cela
evite d'exposer directement les services applicatifs internes.

## Architecture future

Plus tard, le projet pourra evoluer vers une architecture plus complete.

### Docker

Docker permettrait d'emballer le frontend et le backend dans des conteneurs.

Cela rendrait le deploiement plus reproductible et plus simple a automatiser.

### HTTPS

HTTPS permettra de chiffrer les connexions entre l'utilisateur et le serveur.

Il pourra etre configure avec Nginx et un certificat TLS.

### CloudFront

CloudFront pourrait etre ajoute devant l'application pour distribuer le contenu
plus rapidement et rapprocher les pages des utilisateurs.

### Load Balancer

Un Load Balancer pourrait repartir le trafic entre plusieurs instances EC2.

Il deviendrait utile si l'application doit accepter plus de trafic ou etre plus
resiliente.

### RDS

RDS pourrait etre ajoute si le projet a besoin d'une base de donnees geree.

Par exemple, il pourrait stocker des historiques, des utilisateurs, des
configurations IAM ou des rapports d'analyse.

## Pourquoi cette architecture ressemble a une vraie architecture SaaS

Cette architecture se rapproche d'un modele SaaS classique car elle separe les
responsabilites :

- l'utilisateur accede a une interface web ;
- Nginx sert de point d'entree propre ;
- le frontend gere l'experience utilisateur ;
- le backend gere la logique metier ;
- l'infrastructure peut evoluer progressivement vers HTTPS, Docker, Load
  Balancer, CloudFront et base de donnees.

Cette separation rend le projet plus lisible, plus securisable et plus facile a
faire grandir.

## Ce que ce document ne fait pas

- Il ne cree aucune instance EC2.
- Il ne modifie aucun Security Group.
- Il n'installe pas Nginx.
- Il ne configure pas de nom de domaine.
- Il ne connecte pas le projet a AWS.
- Il ne modifie pas le code applicatif.
