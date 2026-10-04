# Déploiement avec Apache sur l'EC2 existante

Le serveur Conscience Numérique utilise déjà Apache. L'assistant IAM doit donc
s'intégrer à cet environnement sans remplacer le serveur web ni perturber le
site existant.

## Principe

Apache reste le point d'entrée public sur les ports 80 et 443.

Le frontend Next.js et le backend FastAPI tournent derrière lui, sur des ports
locaux. Une organisation simple est :

```text
Internet
  |
  v
Apache :80 / :443
  |-- site principal Conscience Numérique
  |-- /assistant-iam  -> Next.js
  `-- /api/iam       -> FastAPI
```

Les ports applicatifs ne doivent pas être ouverts au public dans le Security
Group. Ils servent uniquement aux échanges locaux sur l'instance.

## Variables à définir

Backend :

```env
AWS_REGION=eu-west-3
AWS_ACCOUNT_ID=123456789012
CORS_ALLOWED_ORIGINS=https://consciencenumerique.com
```

Frontend :

```env
NEXT_PUBLIC_API_URL=https://consciencenumerique.com/api/iam
```

L'identifiant de compte AWS ci-dessus est un exemple. Il doit être remplacé en
production.

## Vérifications avant déploiement

Avant de modifier Apache, vérifier les VirtualHosts déjà actifs :

```bash
sudo httpd -S
sudo ss -lntp
sudo apachectl configtest
```

Puis vérifier les services applicatifs :

```bash
curl -sS http://127.0.0.1:8000/health
curl -I http://127.0.0.1:3000
```

Après une modification de configuration Apache, toujours lancer
`apachectl configtest` avant un reload.

## Ce dépôt ne doit pas contenir de secrets

Les fichiers `.env` réels restent sur le serveur ou dans un gestionnaire de
secrets. Seuls les fichiers `.env.example` sont versionnés.

À minima, ne jamais commiter :

- une clé OpenAI ;
- une clé d'accès AWS ;
- un secret d'application ;
- un mot de passe de base de données ;
- un jeton GitHub.

## Avant ouverture au public

Les endpoints de génération et d'explication ne sont pas encore destinés à un
accès public sans contrôle. Avant de les exposer à des utilisateurs externes,
ajouter une authentification, une limite de requêtes et un suivi de consommation
pour les appels facturés.
