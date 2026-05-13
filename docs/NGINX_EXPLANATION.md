# Nginx dans le projet IAM

Ce document explique le role de Nginx pour un futur deploiement du projet
`assistant-iam-conscience-numerique`.

Il s'agit uniquement d'une preparation. Nginx n'est pas installe et aucune
configuration n'est appliquee pour l'instant.

## Qu'est-ce que Nginx ?

Nginx est un serveur web.

Il peut servir des fichiers web, recevoir des requetes HTTP depuis Internet et
les rediriger vers une application interne.

Dans beaucoup d'architectures web, Nginx est place devant les applications. Il
devient alors le point d'entree public du site.

## Role de Nginx dans une architecture web

Nginx peut jouer plusieurs roles :

- recevoir les requetes depuis Internet ;
- rediriger les requetes vers le bon service interne ;
- exposer une seule URL publique meme si plusieurs applications tournent
  derriere ;
- plus tard, gerer HTTPS avec un certificat TLS ;
- aider a structurer proprement le trafic entre frontend et backend.

## Pourquoi utiliser Nginx devant Next.js et FastAPI ?

Dans ce projet, le frontend Next.js et le backend FastAPI tournent sur deux
ports differents :

- Next.js : port `3000`
- FastAPI : port `8000`

Un utilisateur ne devrait pas avoir a connaitre ces ports.

Nginx peut recevoir les requetes sur le port web standard `80`, puis les envoyer
au bon endroit :

- les pages du site vers Next.js ;
- les appels API vers FastAPI.

## Frontend, backend et reverse proxy

### Frontend

Le frontend est la partie visible par l'utilisateur.

Dans ce projet, il s'agit de l'application Next.js. Elle affiche les formulaires,
les resultats IAM, les exports et les explications pedagogiques.

### Backend

Le backend est la partie serveur.

Dans ce projet, il s'agit de l'API FastAPI. Elle recoit les demandes du
frontend, genere les policies IAM, analyse la securite et retourne les resultats
en JSON.

### Reverse proxy

Un reverse proxy est un serveur place devant une ou plusieurs applications.

L'utilisateur parle au reverse proxy, puis le reverse proxy transmet la requete
au bon service interne.

Dans notre cas, Nginx peut jouer ce role.

## Schema simple

```text
Internet
↓
Nginx
↓
Frontend Next.js (3000)
↓
Backend FastAPI (8000)
```

Dans une configuration pratique, Nginx recoit les requetes sur le port `80`.
Ensuite :

- `/` est envoye vers Next.js ;
- `/api/` est envoye vers FastAPI.

## Notions importantes dans une configuration Nginx

### listen 80

`listen 80` indique que Nginx ecoute les requetes HTTP classiques sur le port
`80`.

C'est le port web standard pour HTTP.

### server_name

`server_name` indique le nom de domaine associe a cette configuration.

Exemples :

```nginx
server_name example.com;
server_name iam.example.com;
```

Pendant une phase de test, on peut utiliser `_` comme valeur generique.

### location

`location` definit une regle selon le chemin de l'URL.

Par exemple :

- `location /` concerne toutes les pages du site ;
- `location /api/` concerne les routes qui commencent par `/api/`.

### proxy_pass

`proxy_pass` indique a Nginx ou envoyer la requete.

Exemples :

```nginx
proxy_pass http://127.0.0.1:3000;
proxy_pass http://127.0.0.1:8000;
```

Cela signifie que Nginx recoit la requete publique puis la transmet a une
application locale qui tourne sur un port interne.

## Fichier d'exemple

Un exemple de configuration est disponible ici :

```text
docs/nginx-example.conf
```

Ce fichier est pedagogique. Il ne doit pas etre applique tel quel en production
sans verification.
