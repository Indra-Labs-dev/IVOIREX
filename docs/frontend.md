# Frontend

Next.js App Router, React 19 et TypeScript strict dans `frontend/app`. Campus comprend `/campus`, `/campus/[slug]` et `/campus/[slug]/learn`; les cartes, contenus et états de progression proviennent de l’API. Le BFF same-origin `app/api/campus/[...path]/route.ts` applique une liste de routes permises, vérifie l’origine sur les mutations, renouvelle les cookies HttpOnly et ne révèle pas les jetons au navigateur. Les types générés dans `app/types/api.ts` sont réutilisés par les écrans Campus. Playwright valide le parcours complet sur une instance dédiée.
