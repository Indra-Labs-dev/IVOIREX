# Déploiement

Démarrage local : `docker compose up --build`. Le web est publié sur `43100`, l’API sur `43101`; PostgreSQL et Redis restent privés au réseau Compose. Avant production, injecter les secrets via le gestionnaire de secrets de la plateforme et remplacer les valeurs de développement.
