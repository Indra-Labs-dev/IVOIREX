# Déploiement

Le Compose actuel est destiné au développement. Il utilise HTTP local, valeurs par défaut non secrètes, `COOKIE_SECURE=false`, aucun proxy TLS, révocation individuelle de session, observabilité ou sauvegarde automatisée. Il ne constitue pas une configuration production. En HTTPS, définir `COOKIE_SECURE=true`, le domaine public, les secrets, backups, politique réseau, `TRUSTED_PROXY_IPS` et `TRUST_CLIENT_IP_HEADERS=true` uniquement si le proxy remplace `X-Forwarded-For`, migrations supervisées et health monitoring avant déploiement public.
