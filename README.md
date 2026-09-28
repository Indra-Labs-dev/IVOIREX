# IVOIREX — Le futur se construit ici

IVOIREX est une plateforme numérique pensée en Côte d’Ivoire pour apprendre, créer et faire grandir les talents locaux. Cette première tranche produit propose un compte sécurisé et un profil personnel réellement enregistré dans PostgreSQL.

## Démarrer

```sh
cp .env.example .env
docker compose up --build
```

- Frontend : http://localhost:43100
- API et OpenAPI : http://localhost:43101/docs
- Schéma OpenAPI : http://localhost:43101/api/v1/openapi.json
- Santé API : http://localhost:43101/health
- Profil : http://localhost:43100 (création de compte, connexion et édition de profil)

Au premier lancement, le conteneur API applique les migrations Alembic avant de démarrer Uvicorn. Les valeurs de `.env.example` sont réservées au développement local.

## Développement

```sh
cd frontend/app
npm install
npm run api:types   # l’API doit être démarrée
npm run typecheck
npm run lint
npm run build
```

```sh
cd backend
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python -m pytest
```

Voir [docs/ARCHITECTURE-AUDIT.md](docs/ARCHITECTURE-AUDIT.md) pour l’inventaire, les décisions, les limites et les étapes suivantes.
