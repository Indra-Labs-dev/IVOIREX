# Architecture

`frontend/app` héberge l’interface Next.js et son petit BFF de session ; `backend/app` héberge uniquement l’API FastAPI. Le BFF garde les jetons dans des cookies HttpOnly et transmet les appels authentifiés à l’API. PostgreSQL persiste comptes et profils ; Alembic est le seul mécanisme de changement de schéma. Redis stocke les compteurs de limite de débit de l’authentification ; il ne porte pas encore de sessions, cache produit ou événements temps réel.

Le backend sépare routeurs versionnés, dépendances HTTP, schémas, configuration, services, sécurité et modèles. Les parcours produit réels couvrent création de compte, connexion, déconnexion et profil personnel modifiable. Les autres domaines restent à implémenter avec leur propre migration, service, contrat et tests.
