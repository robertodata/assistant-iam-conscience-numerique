# Sécurité

Ce dépôt contient un assistant IAM en cours de développement. Les exemples sont
faits pour l'apprentissage et la validation technique ; ils ne doivent pas être
considérés comme des policies prêtes à appliquer sans revue.

## Secrets

Les secrets ne doivent jamais être ajoutés au dépôt. Utilisez les fichiers
`.env.example` comme modèle et gardez les vraies valeurs hors de Git.

Si un secret est commité par erreur, le supprimer du dernier commit ne suffit
pas : il faut aussi le révoquer ou le faire tourner.

## Exposition de l'API

Le backend possède des endpoints qui peuvent générer des policies et appeler un
fournisseur IA. Avant une mise à disposition publique, prévoir au minimum :

- une authentification ;
- une limitation du nombre de requêtes ;
- des quotas pour les fonctions facturées ;
- des logs d'accès sans données sensibles ;
- une validation stricte des entrées.

## Policies générées

Une policy générée doit être relue avant utilisation sur un compte AWS réel.
L'objectif du projet est de réduire les permissions excessives, pas de remplacer
une revue IAM complète.

## Signaler un problème

Pour un problème de sécurité non sensible, ouvrez une issue GitHub. Pour un
secret exposé ou une vulnérabilité exploitable, évitez de publier les détails
dans une issue publique.
