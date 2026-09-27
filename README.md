# IVOIREX V1

**La ville numérique ivoirienne** : un parcours connecté pour apprendre, contribuer, prouver ses compétences et saisir des opportunités.

## Démarrer

```bash
cp .env.example .env
docker compose up --build
```

- Web : http://localhost:43100
- API : http://localhost:43101/docs
- Santé : http://localhost:43101/health

La V1 livre les boucles produit persistées : identité JWT, profil, catalogue et progression de formation, posts/réactions/commentaires, défis à réponse vérifiée, opportunités/candidatures, projets, événements et assistant de recommandation local.

Voir [l'architecture](docs/architecture.md), le [développement](docs/development.md), la [sécurité](docs/security.md), l'[API](docs/api.md), les [données](docs/database.md) et la [roadmap](docs/roadmap.md).

## Ports locaux

IVOIREX n’expose pas les ports de développement classiques : le web utilise **43100** et l’API **43101**. Après avoir récupéré la branche qui contient ce réglage, vérifiez la configuration effectivement utilisée avant le démarrage :

```bash
git log -1 --oneline
docker compose config
docker compose down --remove-orphans
docker compose up --build
```

Si la sortie de `docker compose config` contient encore `3000:80` ou `8000:8000`, le répertoire local ne contient pas encore le commit de changement de ports : récupérez la branche/PR à jour puis relancez les commandes ci-dessus. Les ports publiés attendus sont `43100:80` (web) et `43101:8000` (API).
