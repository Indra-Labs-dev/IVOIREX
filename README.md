# IVOIREX V1 Ultra

**La ville numérique de la nouvelle génération ivoirienne.** IVOIREX relie un parcours d’apprentissage, la contribution communautaire, les challenges, les projets et les opportunités dans un même monde.

## Architecture active

- `apps/web` — Next.js 15 / React 19 / TypeScript strict, avec la carte IVOIREX World et recherche API.
- `apps/api` — FastAPI, SQLAlchemy 2, Pydantic v2, authentification JWT et PostgreSQL.
- `postgres` et `redis` — services privés Docker ; Redis est réservé à la future diffusion realtime/rate limiting.

## Lancer

```bash
cp .env.example .env
docker compose down --remove-orphans
docker compose up --build
```

- World : http://localhost:43100
- API OpenAPI : http://localhost:43101/docs
- Health : http://localhost:43101/health

## Vérifier

```bash
cd apps/web && npm install && npm run typecheck && npm run build
cd ../api && pip install -r requirements.txt && pytest -q
```

Voir `docs/` pour les décisions d’architecture, sécurité, IA, temps réel, 3D et déploiement. Les fonctionnalités non actives ne sont pas présentées comme livrées dans ces documents.
