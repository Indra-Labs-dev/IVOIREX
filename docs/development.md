# Développement

```bash
cd apps/web && npm install && npm run typecheck && npm run build
cd ../api && python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
pytest -q
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```

Docker reste la voie recommandée pour lancer les services d’infrastructure. Le développement local API peut employer SQLite, mais PostgreSQL doit être utilisé pour valider les migrations.
