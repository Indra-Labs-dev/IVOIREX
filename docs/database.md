# Database

Les entités persistées sont `User`, `Course`, `Enrollment`, `Post`, `Challenge`, `Project` et `Opportunity`. Les emails et pseudos sont uniques et indexés ; les inscriptions possèdent une contrainte unique utilisateur/cours. Le schéma de développement est créé au démarrage. Alembic est inclus dans les dépendances, mais les migrations versionnées ne sont pas encore créées : elles sont le prochain jalon obligatoire avant production.
