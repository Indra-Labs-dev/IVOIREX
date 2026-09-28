# IVOIREX — AUTONOMOUS BUILD REPORT

## Date

28 septembre 2026, Africa/Abidjan.

## Starting State

Le dépôt contenait une fondation Next.js/FastAPI opérationnelle, les routes d’authentification et une base PostgreSQL historique préservée. Il n’y avait ni interface de connexion, ni profil produit éditable. Le logo officiel `logo.png` était présent à la racine.

## Completed

- **DONE** — Un premier parcours utilisateur complet : créer un compte, ouvrir une session, éditer son profil, relire les données persistées, puis se déconnecter.
- **DONE** — Profil propriétaire avec nom affiché, bio, ville, pays, compétences et intérêts, avec validation, nettoyage des champs et plafonds de taille.
- **DONE** — Chargement rétrocompatible des profils depuis les colonnes utilisateur historiques.
- **PARTIAL** — Le profil est privé à son propriétaire. Les pages publiques de profil, abonnements et visibilité configurable ne sont pas encore développés.

## Database Changes

- **DONE** — Migration `0002_profiles` crée `profiles` avec clé étrangère en cascade et dates de création/mise à jour.
- **DONE** — Les profils des comptes existants reprennent pseudo, bio, ville et compétences historiques sans supprimer ni réécrire les tables métier historiques.
- **DONE** — L’inscription crée le profil par défaut dans la même transaction que le compte.
- **PARTIAL** — Les compétences et intérêts sont des listes JSON dans le profil; aucune taxonomie ni table de compétences n’est encore nécessaire à cette tranche.

## API Changes

- **DONE** — `GET /api/v1/profile/me` lit le profil authentifié; `PUT /api/v1/profile/me` le met à jour.
- **DONE** — Schémas Pydantic limitent tailles, texte vide, nombre de tags et longueur des éléments.
- **DONE** — Le contrat OpenAPI génère les types TypeScript utilisés par l’interface.
- **PARTIAL** — Il n’y a pas encore de lecture publique de profil ni de politique de visibilité.

## Frontend Changes

- **DONE** — Formulaires de création de compte et connexion; état de chargement, erreurs lisibles, sauvegarde confirmée et déconnexion.
- **DONE** — Éditeur de profil connecté à PostgreSQL via API; compétences et intérêts éditables sous forme de listes séparées par des virgules.
- **DONE** — Le BFF Next.js conserve les JWT dans des cookies `HttpOnly`, `SameSite=Lax` et `Secure` en production; il renouvelle l’access token quand nécessaire.
- **DONE** — Les opérations de modification vérifient l’origine. Aucun jeton n’est exposé au JavaScript de la page.
- **DONE** — Le rate limiter Redis lit l’IP transmise uniquement depuis l’IP privée frontend explicitement approuvée; le BFF ne relaie `X-Forwarded-For` qu’avec un opt-in réservé à un ingress qui le remplace.
- **DONE** — Affichage responsive, focus clavier visible et respect de `prefers-reduced-motion`.

## Design Changes

- **DONE** — Page d’accès et espace profil redessinés dans une direction sombre, orange IVOIREX, accents ivoiriens mesurés et effets lumineux discrets.
- **DONE** — Aucun chiffre d’usage ni contenu de démonstration n’est présenté comme réel.
- **PARTIAL** — Ce système visuel ne couvre que l’accès et le profil; les autres surfaces produit restent à concevoir.

## Security

- **DONE** — Les mots de passe restent hachés côté API; les jetons restent dans des cookies HttpOnly côté navigateur web.
- **DONE** — Les champs profil sont validés avant persistance et rendus avec échappement React.
- **PARTIAL** — Refresh tokens encore réutilisables et déconnexion globale du compte; pas de RBAC ni de révocation de session individuelle.
- **PARTIAL** — Les protections production (CSP, headers, audit log, supervision, sauvegardes et vérification complète CSRF) restent à faire.

## Tests

- **DONE** — 7 tests API couvrent auth, validation, propriétaire authentifié, création, nettoyage, persistance profil et confiance proxy.
- **DONE** — Build de production Next inclut lint et vérification TypeScript; `npm audit` rapporte zéro vulnérabilité.
- **DONE** — Parcours réel via Compose : inscription, émission de cookies HttpOnly, mise à jour et relecture PostgreSQL, déconnexion et confirmation de session invalide.
- **DONE** — Comptes créés pour le smoke test supprimés après validation; aucun enregistrement de test n’est laissé dans la base.
- **PARTIAL** — Pas encore de suite PostgreSQL automatisée, de tests navigateur E2E ni de CI.

## Docker

- **DONE** — Le contexte de build frontend inclut `frontend/public` et l’image finale sert les assets statiques.
- **DONE** — Compose applique les migrations avant le démarrage API; les volumes restent préservés.
- **PARTIAL** — Compose est configuré pour le développement local, pas pour le déploiement public.

## Logo / Branding

- **DONE** — Le fichier officiel racine est conservé et copié sans modification dans `frontend/public/images/ivoirex-logo.png`.
- **DONE** — Logo dans la navigation, branding de page, métadonnées favicon/Apple icon et Open Graph; proportions respectées.
- **PARTIAL** — Les mêmes pixels haute résolution sont réutilisés pour les icônes; des variantes optimisées pourront être générées sans redessiner le logo.

## Remaining Work

- E2E navigateur automatisé du parcours inscription → édition persistée → déconnexion; tests de migration avec un jeu legacy en PostgreSQL.
- Ajouter les protections d’authentification par session, rotation/révocation individuelle et RBAC.
- Construire le prochain domaine complet, recommandé : catalogue Campus et inscription réelle à un cours.
- Définir visibilité/consentement avant de rendre les profils publics.
- Revoir CSP, en-têtes, observabilité, sauvegardes et secrets de production.

## Known Limitations

- `/api/v1/profile/me` ne permet au propriétaire que de consulter et modifier son propre profil.
- Les tags sont du texte libre; aucun profil public, upload d’avatar ou gestion d’éducation/expérience n’est implémenté.
- En production, configurer le reverse proxy public pour écraser `X-Forwarded-For`, puis configurer son adresse comme proxy de confiance et activer le relais BFF.
- Le logo réutilisé pour les icônes est un PNG de 1,7 Mo; le serveur le réduit côté affichage, mais une dérivation officielle optimisée reste à faire.

## Recommended Next Phase

Ajouter une suite E2E et une migration legacy automatisée, puis développer **Campus** en tranche fermée : cours publiés, catalogue filtrable, inscription persistée et état d’inscription affiché depuis la base. Ne pas introduire de fausse progression avant l’existence de leçons et d’un modèle de complétion.
