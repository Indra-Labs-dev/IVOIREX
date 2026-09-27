# Données

Tables relationnelles : `users`, `courses`, `enrollments`, `posts`, `comments`, `opportunities`, `applications`, `challenges`, `submissions`, `projects`, `events`, `registrations`. Les contraintes uniques empêchent les doubles inscriptions, candidatures, soumissions et inscriptions événement. Les emails et pseudos sont indexés. Le schéma est créé au démarrage V1; une migration Alembic est la première étape recommandée avant évolution de production.
