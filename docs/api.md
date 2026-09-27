# API

L'OpenAPI interactive est disponible sur `/docs`. Les routes d'identité sont `POST /api/v1/auth/register` et `login`; les autres mutations nécessitent `Authorization: Bearer <JWT>`. Ressources actives : profiles, courses (enroll/complete), posts (comment/react), opportunities (apply), challenges (submit), projects, events (register), search et ai/chat. Les erreurs renvoient les codes HTTP FastAPI et un champ `detail`.
