# Audit d’architecture IVOIREX

Date de l’audit : 2026-09-27. Audit fondé sur les fichiers suivis du dépôt et leurs imports/configurations.

## Current State

Le dépôt contenait deux frontends concurrents : une application Next.js 15 / React 19 / TypeScript strict dans `apps/web/app`, et un prototype HTML/CSS/JavaScript à côté du projet Next. Le `Dockerfile` Next ne copiait et ne servait que l’application Next. L’API FastAPI, les modèles SQLAlchemy et un test existaient dans `apps/api`. PostgreSQL et Redis étaient déclarés dans Compose. La documentation décrivait certaines capacités prévues comme si elles étaient disponibles.

## Problems

- Le prototype HTML envoyait des requêtes vers `/posts`, `/challenges`, `/opportunities`, `/ai/chat`, la réaction et la fin de cours ; ces routes n’existaient pas. Il conservait le jeton dans `localStorage` et rendait plusieurs champs distants avec `innerHTML`.
- La page Next dépendait de `/courses` et `/world/activity`, supprimés de la nouvelle API foundation. Plusieurs sections étaient des titres sans interaction métier.
- Toute l’API vivait dans `main.py`. Elle utilisait un secret JWT de secours, des tokens à longue durée sans refresh/logout, et bcrypt via passlib. L’enregistrement et le démarrage amorçaient des données inventées.
- `Base.metadata.create_all()` tournait au démarrage ; aucun fichier de migration versionné n’existait malgré Alembic installé.
- Les modèles réunissaient plusieurs fonctionnalités non abouties. L’unique test écrivait dans une base SQLite de fichier et vérifiait un état prérempli.
- Redis était lancé mais n’était consommé par aucun code. Aucune limite de débit, session distribuée ou tâche asynchrone n’existait.
- Le Compose racine publiait le conteneur Next sur le port 80 alors que Next écoutait sur 3000. Le Dockerfile utilisait `npm install` sans lockfile. Les identifiants de développement étaient codés dans Compose.
- Aucun client de contrat OpenAPI, aucun lint/typecheck frontend dans Compose, pas de lockfile, pas d’E2E, pas d’infrastructure de tests PostgreSQL.
- Tailwind, shadcn/ui, Radix, Zustand et React Hook Form étaient demandés comme préférences dans le brief, mais absents. Les dépendances 3D étaient présentes sans vraie carte interactive : seule une balise 3D décorative était rendue.

## Keep

- Next.js App Router, TypeScript strict et la direction visuelle IVOIREX comme point de départ.
- FastAPI, Pydantic, SQLAlchemy 2, PostgreSQL et la modélisation d’identité utilisateur.
- Healthcheck, secrets en variables d’environnement, conteneurs séparés et réseau Compose privé pour les bases.

## Remove

- Le HTML/JS historique parallèle et son stockage de jeton local.
- Les routes absentes présentées comme actions fonctionnelles, les données de démonstration créées à chaque lancement et les compteurs/product stories non étayés.
- Les endpoints et modèles Python de démonstration des cours, posts, challenges, projets et opportunités qui n’étaient pas exposés par une API cohérente. Les tables physiques PostgreSQL historiques sont conservées par sécurité et devront faire l’objet de migrations explicites.

## Rebuild

- Layout physique séparé `frontend/`, `backend/`, `infrastructure/`, `docs/`.
- API FastAPI à routeur versionné, configuration centralisée, modèles de requête/réponse, hachage Argon2 avec re-hachage des hashes bcrypt historiques, JWT courts access/refresh, migrations Alembic adoptant les tables utilisateur existantes et tests isolés.
- Compose root avec frontend, API, PostgreSQL et Redis, checks de santé et ports cohérents.
- Configuration de génération des types TypeScript à partir de l’OpenAPI exposé par FastAPI.

## Target Architecture

```text
frontend/app/       Next.js client; appels HTTP vers FastAPI
backend/app/        HTTP API, schemas, core, sécurité, modèles
backend/migrations/ Alembic; évolution du schéma explicite
infrastructure/     notes et extensions infra
Docker Compose      frontend + backend + PostgreSQL + Redis
```

Le contrat public est FastAPI OpenAPI à `/api/v1/openapi.json`; le Swagger UI reste disponible à `/docs`. La génération TypeScript est lancée depuis le frontend avec `npm run api:types` après démarrage de l’API.

## Migration Plan

1. Basculer les dossiers d’applications vers `frontend/` et `backend/`, retirer les pages prototypes orphelines. **Fait.**
2. Arrêter le DDL et le seed au démarrage ; poser une première migration utilisateur. **Fait.**
3. Créer la frontière API/configuration/authentification, préparer les contrats et tests. **Fait, fondation limitée à l’identité et au healthcheck.**
4. Reconfigurer Compose et variables de développement ; documenter chaque service. **Fait.**
5. Lancer les tests, build/typecheck frontend, migration et smoke tests. **Fait : 4 tests API, build Next 16 + TypeScript, audit npm à 0 vulnérabilité, migration PostgreSQL sur le volume existant et cycle auth réel register/me/refresh/logout.**
6. Ajouter les domaines métier un par un avec schémas, permissions, migration et tests avant de les brancher à l’interface.

## Limits at this phase

- Seule l’identité est persistée. Les domaines produit ont été retirés, et devront être implémentés après validation de cette fondation.
- Redis sert au limiteur de débit sur register/login/refresh. Il ne gère pas encore les sessions, le cache métier ni le temps réel.
- Les jetons sont des JWT bearer sans cookie HttpOnly ; le logout incrémente un compteur de version au niveau du compte et révoque toutes ses sessions émises. La révocation individuelle n’est pas disponible.
- Les comptes créés reçoivent `USER`; RBAC n’est pas encore appliqué aux routes.
- Pas de couverture E2E navigateur ni de suite automatisée PostgreSQL dans cette première étape ; un smoke test auth réel a toutefois validé l’écriture PostgreSQL. Le volume historique est adopté sans historique Alembic, et les tables métier existantes restent intactes.
- L’URL API Next est injectée pour l’environnement local ; la configuration de domaine de production reste à définir.

## Addendum produit — 28 septembre 2026

- Le premier parcours produit complet est livré : inscription, connexion, édition du profil personnel, relecture des données persistées et déconnexion.
- `profiles` a été ajouté par `0002_profiles`; les profils historiques sont construits à partir des colonnes `users` conservées.
- Le BFF Next.js garde les JWT dans des cookies HttpOnly SameSite; le proxy approuvé transmet l’adresse client au limiteur Redis sans faire confiance aux appels directs à l’API.
- Le logo racine a été préservé et intégré à l’interface et aux métadonnées. L’image est copiée dans l’image Docker finale.
- Validation : 7 tests backend, build/lint/TypeScript frontend, audit npm à zéro vulnérabilité, migration `0002_profiles` active et parcours BFF/PostgreSQL réel.

Cette tranche ne rend pas encore les profils publics et n’ajoute pas Campus, Community, Career ou World. Le prochain domaine recommandé est Campus, livré comme flux complet incluant inscription persistée à un cours. Voir `roadmap.md` et `AUTONOMOUS-NIGHT-REPORT.md`.
