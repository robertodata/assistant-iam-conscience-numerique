# Frontend Next.js en production simple

Ce document explique comment preparer et lancer le frontend Next.js en mode
production sur une machine Linux simple, par exemple une future instance AWS
EC2.

Ce guide ne deploie rien sur AWS. Il prepare seulement les commandes de base.

## Installer les dependances

Depuis la racine du projet :

```bash
cd frontend
npm install
```

Cette commande installe les dependances definies dans `package.json` et
`package-lock.json`.

## Construire le frontend

Avant un lancement production, il faut generer un build optimise :

```bash
npm run build
```

Cette commande cree les fichiers de production dans le dossier `.next/`.

## Lancer le frontend en production

Apres le build :

```bash
npm run start
```

Le script `frontend/start.sh` lance la meme commande :

```bash
./start.sh
```

## Difference entre npm run dev et npm run start

`npm run dev` lance Next.js en mode developpement.

Ce mode est pratique en local car il recharge rapidement l'application quand le
code change. Il n'est pas fait pour servir l'application en production.

`npm run start` lance Next.js en mode production.

Il utilise le resultat de `npm run build` et sert une version optimisee de
l'application.

## Pourquoi faire un build avant start

`npm run start` a besoin d'un build Next.js deja genere.

Sans `npm run build`, Next.js n'a pas les fichiers optimises necessaires pour
servir l'application en mode production.

Le cycle correct est donc :

```bash
npm install
npm run build
npm run start
```

## URL du backend en production

En developpement, le frontend appelle actuellement le backend local.

En production, le frontend devra appeler l'URL reelle du backend, par exemple :

```text
https://api.example.com
```

ou l'adresse publique de l'instance EC2 si le projet est encore en phase
d'apprentissage.

Il faudra donc preparer une configuration propre pour remplacer les URLs locales
comme `http://127.0.0.1:8000` par l'URL du backend de production.

## Verification rapide

Avant un futur deploiement, verifier TypeScript et le build :

```bash
npm run build
```

Si le build passe, le frontend est pret pour un lancement production simple avec
`npm run start`.
