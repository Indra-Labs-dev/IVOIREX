# API

OpenAPI est exposé par FastAPI à `/docs`. Les routes actives sont : identité (`/api/v1/auth/*`), profil courant, catalogue de cours et inscription, publication, recherche globale et activité du monde. Les mutations nécessitent un Bearer JWT, à l’exception de l’inscription/connexion. Les données d’activité sont des agrégats réels des tables, pas des compteurs affichés en dur.
