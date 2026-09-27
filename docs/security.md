# Security

Les mots de passe sont hachés par bcrypt ; les sessions sont des JWT signés et expirants. Pydantic valide les entrées, SQLAlchemy lie les requêtes et les contraintes SQL préviennent les doublons d’inscription. Pour production : secrets gérés hors Git, HTTPS, cookies HttpOnly+CSRF ou rotation de tokens, Alembic, rate limiting Redis, audit log, RBAC et security headers sont requis avant ouverture publique.
