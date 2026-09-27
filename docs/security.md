# Sécurité

Les mots de passe sont hachés bcrypt et les sessions sont des JWT signés avec expiration. Pydantic valide toutes les entrées écrites; SQLAlchemy lie les paramètres SQL. Les actions utilisateur requièrent le JWT et les contraintes SQL préviennent les doublons. CORS est configurable. En production, remplacer le secret JWT, servir HTTPS, déplacer le JWT dans un cookie HttpOnly avec protection CSRF, mettre un rate limiter Redis, ajouter des migrations, des en-têtes de sécurité et un contrôle d'accès RBAC administratif.
