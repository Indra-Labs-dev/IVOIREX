# API

OpenAPI : `/api/v1/openapi.json`, Swagger UI : `/docs`. Authentification et profil : `POST /auth/register`, `/auth/login`, `/auth/refresh`, `/auth/logout`, `GET /auth/me`, `GET/PUT /profile/me`.

Campus : `GET /courses` (page, page_size, q, category, level, max_duration_minutes), `GET /courses/{slug}`, `POST /enrollments`, `GET /enrollments/me`, `GET /lessons/{lesson_id}` et `POST /progress/complete`. Le catalogue et le détail exposent uniquement les cours publiés. L’inscription, l’accès aux leçons et la complétion exigent une session; chaque compte ne voit que ses propres inscriptions et progressions.

Régénérer les contrats TypeScript depuis le schéma actif avec `cd frontend/app && npm run api:types`. Les tests PostgreSQL et le navigateur sont exécutés dans des services et bases temporaires avec `scripts/test-campus-postgres.sh` et `scripts/test-campus-e2e.sh`.
