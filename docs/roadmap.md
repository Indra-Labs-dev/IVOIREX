# Roadmap IVOIREX

## Livré

- Fondation Docker, API versionnée, migrations, documentation et contrôles de santé.
- Inscription, connexion et déconnexion avec une interface web de même origine, cookies HttpOnly et validation côté serveur.
- Profil personnel persistant : nom affiché, bio, ville, pays, compétences et intérêts. Les données des comptes historiques sont reprises par migration.
- Branding web à partir du logo officiel, favicon/Apple icon et image Open Graph; mise en page responsive et prise en charge de `prefers-reduced-motion`.
- Campus : catalogue paginé avec recherche/filtres, détail des cours publiés, inscription persistée, contenus d’article protégés et progression/idempotence des leçons.
- Données de démonstration Campus identifiées comme telles; tests PostgreSQL et parcours navigateur Playwright isolés des volumes de développement.

## Prochaines phases

1. Développer Community en tranche complète : publications, commentaires et réactions avec contrôle d’appartenance et persistance.
2. Renforcer l’identité : rotation/révocation individuelle des refresh tokens, RBAC appliqué, sessions et revue des protections web avant production.
3. Développer Career, Events et Arena, puis XP avec ledger avant tout système de récompense.
4. Définir déploiement, secrets, CSP/headers, supervision et procédure de sauvegarde avant ouverture publique.
