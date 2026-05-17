# GitHub Actions CI

Ce document explique le workflow GitHub Actions ajoute au projet
`assistant-iam-conscience-numerique`.

Le workflow sert uniquement a verifier le projet. Il ne deploie rien
automatiquement sur EC2.

## Qu'est-ce que CI/CD ?

CI/CD signifie Continuous Integration / Continuous Deployment.

### CI : Continuous Integration

La CI verifie automatiquement que le projet reste sain quand le code change.

Exemples :

- installer les dependances ;
- lancer les tests ;
- verifier qu'un build frontend fonctionne ;
- detecter une erreur avant de fusionner ou deployer.

### CD : Continuous Deployment

Le CD va plus loin : il peut deployer automatiquement l'application apres une
validation.

Dans ce projet, nous n'activons pas encore le deploiement automatique.

## Ce que fait le workflow CI

Le fichier GitHub Actions se trouve ici :

```text
.github/workflows/ci.yml
```

Il se lance sur :

- `push`
- `pull_request`

Il contient deux jobs.

## Job backend

Le job backend :

- utilise Ubuntu latest ;
- installe Python 3.11 ;
- installe les dependances depuis `backend/requirements.txt` ;
- lance `pytest` dans le dossier `backend`.

Objectif : verifier que l'API FastAPI et le moteur IAM passent toujours les
tests.

## Job frontend

Le job frontend :

- utilise Ubuntu latest ;
- installe Node.js 20 ;
- lance `npm install` dans le dossier `frontend` ;
- lance `npm run build`.

Objectif : verifier que l'application Next.js peut etre construite correctement.

## Difference entre CI et deploiement automatique

La CI repond a la question :

```text
Est-ce que le projet fonctionne toujours ?
```

Le deploiement automatique repond a la question :

```text
Est-ce qu'on met cette nouvelle version en production automatiquement ?
```

Pour l'instant, ce projet utilise seulement la CI.

Le deploiement EC2 reste manuel avec le script :

```bash
bash scripts/deploy-ec2.sh
```

## Pourquoi ne pas deployer automatiquement maintenant ?

Le projet est encore en phase de stabilisation.

De plus, l'EC2 peut contenir WordPress et une configuration Apache existante.

Il est donc plus prudent de :

- verifier le code avec GitHub Actions ;
- garder le deploiement manuel ;
- observer les resultats ;
- automatiser le deploiement plus tard, quand l'architecture sera totalement
  maitrisee.

## Ce que ce workflow ne fait pas

- Il ne se connecte pas a AWS.
- Il ne modifie pas l'EC2.
- Il ne redemarre pas les services systemd.
- Il ne recharge pas Apache.
- Il ne deploie pas automatiquement le backend ou le frontend.
