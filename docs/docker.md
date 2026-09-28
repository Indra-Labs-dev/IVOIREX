# Docker Compose

Depuis la racine : `cp .env.example .env && docker compose up --build`. Les services sont frontend (43100), backend (43101), PostgreSQL et Redis sur un réseau privé ; PostgreSQL et Redis n’exposent aucun port hôte. Les bases disposent d’un volume nommé, d’un healthcheck et d’une politique de redémarrage. L’API attend les deux services sains puis applique Alembic ; `/ready` vérifie PostgreSQL et Redis. `/health` ne vérifie que le processus API. Compose utilise des valeurs de développement par défaut : les remplacer pour tout environnement partagé ou déployé.

Le frontend a une adresse fixe sur ce réseau; le rate limiter ne fait confiance à son en-tête `X-Forwarded-For` que depuis cette adresse. Le BFF ne relaie les IPs transmises que si `TRUST_CLIENT_IP_HEADERS=true`. En production, ne l’activer qu’avec un proxy public qui écrase l’en-tête depuis l’IP qu’il observe; en développement local, laisser désactivé.

Les profils Compose `test` et `e2e` créent des bases PostgreSQL temporaires en `tmpfs` et des services de test isolés. Utiliser `scripts/test-campus-postgres.sh` ou `scripts/test-campus-e2e.sh`; ces commandes ne touchent pas au volume PostgreSQL normal.
