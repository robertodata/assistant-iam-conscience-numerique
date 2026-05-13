# Audit de l'EC2 existante avant deploiement

Ce document prepare l'audit de l'instance EC2 qui heberge deja WordPress.

Objectif : comprendre l'existant avant d'installer ou de configurer
`assistant-iam-conscience-numerique` sur la meme machine.

Ce document ne modifie rien. Il ne demande pas d'installer Nginx, de toucher a
Apache, de changer WordPress ou de creer une ressource AWS.

## Regle de securite

Avant toute modification, on doit comprendre l'existant pour eviter de casser
WordPress.

Une EC2 qui heberge deja un site WordPress peut contenir :

- une configuration Apache active ;
- des certificats HTTPS deja en place ;
- un domaine deja configure ;
- des fichiers WordPress importants ;
- une base de donnees utilisee par le site ;
- des ports deja occupes.

Il faut donc auditer avant d'agir.

## Points a verifier

### Systeme Linux utilise

Identifier la distribution Linux permet de savoir quelles commandes et quels
chemins systeme utiliser.

Exemples possibles :

- Amazon Linux ;
- Ubuntu ;
- Debian ;
- CentOS.

### Serveur web actuel : Apache ou Nginx

WordPress est souvent servi par Apache, parfois par Nginx.

Il faut verifier quel serveur web est actif avant d'ajouter un nouveau service.

### Ports utilises

Verifier les ports deja occupes :

- `80` : HTTP ;
- `443` : HTTPS ;
- `3000` : futur frontend Next.js ;
- `8000` : futur backend FastAPI.

Si un port est deja utilise, il ne faut pas lancer un nouveau service dessus
sans comprendre pourquoi.

### Presence de WordPress

Verifier que WordPress est bien present, actif et servi par le serveur web.

Il faudra eviter toute modification qui pourrait interrompre le site existant.

### Emplacement du site WordPress

Identifier ou se trouvent les fichiers WordPress.

Emplacements possibles :

- `/var/www/html`
- `/var/www/wordpress`
- un dossier specifique au domaine

### Configuration Apache existante

Si Apache est utilise, il faut inspecter les fichiers de configuration avant
toute modification.

Sur Amazon Linux ou CentOS, les fichiers peuvent se trouver dans :

```text
/etc/httpd/conf.d/
```

Sur Ubuntu ou Debian, ils peuvent se trouver dans :

```text
/etc/apache2/sites-available/
/etc/apache2/sites-enabled/
```

### Certificats HTTPS existants

Verifier si HTTPS est deja configure.

Il faut identifier :

- l'outil utilise pour les certificats ;
- les domaines couverts ;
- les fichiers de configuration TLS ;
- la date d'expiration des certificats.

### Domaine utilise

Identifier le domaine deja pointe vers l'EC2.

Exemples :

- `example.com`
- `www.example.com`
- un sous-domaine dedie a WordPress

Cela aidera a decider plus tard si l'assistant IAM doit utiliser :

- un sous-domaine ;
- un chemin specifique ;
- une autre instance.

### Espace disque disponible

Verifier que l'instance a assez d'espace disque avant d'ajouter Node.js,
dependances frontend, environnement Python et logs.

### Memoire RAM disponible

Verifier que l'instance a assez de memoire pour faire tourner :

- WordPress ;
- la base de donnees si elle est locale ;
- Next.js ;
- FastAPI ;
- Apache ou Nginx.

## Commandes Linux a executer plus tard

Ces commandes seront a executer sur l'EC2 existante, uniquement en audit.

### Informations systeme

```bash
uname -a
cat /etc/os-release
```

### Etat des serveurs web

```bash
sudo systemctl status httpd
sudo systemctl status nginx
```

Sur certaines distributions, Apache peut s'appeler `apache2` au lieu de
`httpd`.

### Ports utilises

```bash
sudo ss -tulpn
```

Cette commande affiche les ports ouverts et les processus qui les utilisent.

### Espace disque

```bash
df -h
```

### Memoire RAM

```bash
free -h
```

### Configuration Apache

```bash
ls /etc/httpd/conf.d/
sudo httpd -S
```

Ces commandes sont utiles si l'EC2 utilise Apache avec la structure Amazon
Linux ou CentOS.

## Resultats a collecter

Pendant l'audit, noter :

- la distribution Linux ;
- le serveur web actif ;
- les ports deja utilises ;
- le chemin du site WordPress ;
- les fichiers Apache importants ;
- le domaine configure ;
- l'etat HTTPS ;
- l'espace disque disponible ;
- la memoire disponible.

## Ce qu'il ne faut pas faire pendant l'audit

- Ne pas installer Nginx.
- Ne pas modifier Apache.
- Ne pas redemarrer WordPress sans raison claire.
- Ne pas changer les certificats HTTPS.
- Ne pas modifier les Security Groups AWS.
- Ne pas lancer Next.js ou FastAPI sur un port public.
- Ne pas creer de ressources AWS.
