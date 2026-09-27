# Développement

```bash
cd apps/api
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
pytest -q
uvicorn app.main:app --reload
```

Lancer le frontend via un serveur statique, ou utiliser `docker compose up --build`. Les valeurs sensibles sont uniquement fournies par variables d'environnement; ne commitez jamais `.env`.
