# Structure Linux cible pour AWS EC2

Ce document propose une organisation simple du projet
`assistant-iam-conscience-numerique` sur un futur serveur Linux AWS EC2.

Il ne cree aucune ressource AWS et ne modifie pas le code applicatif.

Une bonne organisation Linux simplifie la maintenance et la securite.

## Structure proposee

```text
/home/ec2-user/assistant-iam/
├── frontend/
├── backend/
├── docs/
├── logs/
├── scripts/
```

Cette structure garde les grandes responsabilites du projet separees et faciles
a retrouver.

## Role des dossiers

### frontend/

Le dossier `frontend/` contient l'application Next.js.

Il sert a gerer :

- l'interface utilisateur ;
- les pages React ;
- les styles ;
- le build frontend ;
- le lancement du serveur Next.js sur le port `3000`.

### backend/

Le dossier `backend/` contient l'API FastAPI.

Il sert a gerer :

- les routes API ;
- le moteur IAM ;
- l'analyse de securite ;
- les tests backend ;
- le lancement du serveur FastAPI sur le port `8000`.

### docs/

Le dossier `docs/` contient la documentation technique et pedagogique.

Il peut inclure :

- les plans de deploiement ;
- les explications Nginx ;
- l'architecture AWS EC2 cible ;
- les notes de production ;
- les procedures de maintenance.

### logs/

Le dossier `logs/` sert a centraliser les journaux applicatifs.

Il permet de retrouver rapidement ce qui s'est passe sur le serveur.

### scripts/

Le dossier `scripts/` sert a stocker les scripts Linux utiles a l'exploitation.

Il peut contenir des scripts pour demarrer, arreter ou redemarrer les services
du projet.

## Logs

Les logs sont importants car ils aident a comprendre le comportement de
l'application.

Ils permettent de diagnostiquer :

- une erreur backend ;
- un probleme de lancement frontend ;
- une erreur de configuration Nginx ;
- une requete API qui echoue ;
- un comportement inattendu apres un deploiement.

Exemples de fichiers de logs :

```text
logs/frontend.log
logs/backend.log
logs/nginx.log
```

Au debut, ces fichiers peuvent etre simples. Plus tard, ils pourront etre
geres par `systemd`, Docker ou un outil de monitoring.

## Scripts Linux

Les scripts Linux permettent de lancer les services de maniere plus claire et
plus reproductible.

### start.sh

`start.sh` sert a demarrer un service.

Exemples :

- demarrer le backend FastAPI ;
- demarrer le frontend Next.js ;
- lancer les deux services dans un environnement de test.

### restart.sh

`restart.sh` sert a redemarrer un service.

Il est utile apres :

- une mise a jour du code ;
- un changement de configuration ;
- un deploiement manuel.

### stop.sh

`stop.sh` sert a arreter un service.

Il est utile pour :

- liberer un port ;
- arreter proprement une application ;
- preparer une maintenance.

## Processus

Dans une premiere version EC2 simple, les processus peuvent etre organises ainsi
:

- frontend Next.js : port `3000` ;
- backend FastAPI : port `8000` ;
- Nginx : ports `80` et `443`.

Nginx recoit le trafic public, puis redirige les requetes vers les services
internes.

Le frontend et le backend ne devraient pas etre exposes directement au public.

## Architecture future

Cette structure peut evoluer progressivement.

### systemd

`systemd` permettra de transformer le frontend et le backend en services Linux.

Cela permettra :

- un demarrage automatique au boot ;
- un redemarrage automatique en cas d'erreur ;
- une lecture centralisee des logs avec `journalctl`.

### Docker

Docker permettra d'emballer le frontend, le backend et leurs dependances dans
des conteneurs.

Cela rendra l'environnement plus reproductible et plus simple a deplacer.

### CI/CD

Une pipeline CI/CD pourra automatiser :

- les tests ;
- le build frontend ;
- le deploiement sur le serveur ;
- les verifications apres deploiement.

### Monitoring

Le monitoring permettra de surveiller :

- l'etat des processus ;
- l'utilisation CPU et memoire ;
- les erreurs applicatives ;
- les temps de reponse ;
- la disponibilite du service.

## Recommandation pour debuter

Pour un premier deploiement pedagogique, garder une structure simple :

```text
/home/ec2-user/assistant-iam/
├── frontend/
├── backend/
├── docs/
├── logs/
├── scripts/
```

Ensuite, ajouter progressivement `systemd`, Docker, CI/CD et monitoring quand
le projet devient plus stable.
