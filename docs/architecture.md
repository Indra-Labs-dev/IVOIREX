# Architecture

Le monorepo contient `apps/web` (SPA statique, design system CSS et carte spatiale IVOIREX WORLD) et `apps/api` (FastAPI + SQLAlchemy). Docker isole web, API, PostgreSQL et Redis sur un réseau privé. L'API utilise PostgreSQL en conteneur; SQLite est réservé aux tests locaux. L'interface consomme l'API versionnée via `/api/v1` et stocke le JWT en localStorage pour cette V1. La carte WORLD est une scène CSS 3D légère et interactive, compatible sans WebGL.
