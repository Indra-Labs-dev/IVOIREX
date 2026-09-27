# IVOIREX V1

**La ville numérique ivoirienne** : un parcours connecté pour apprendre, contribuer, prouver ses compétences et saisir des opportunités.

## Démarrer

```bash
cp .env.example .env
docker compose up --build
```

- Web : http://localhost:3000
- API : http://localhost:8000/docs
- Santé : http://localhost:8000/health

La V1 livre les boucles produit persistées : identité JWT, profil, catalogue et progression de formation, posts/réactions/commentaires, défis à réponse vérifiée, opportunités/candidatures, projets, événements et assistant de recommandation local.

Voir [l'architecture](docs/architecture.md), le [développement](docs/development.md), la [sécurité](docs/security.md), l'[API](docs/api.md), les [données](docs/database.md) et la [roadmap](docs/roadmap.md).
