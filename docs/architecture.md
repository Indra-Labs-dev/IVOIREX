# Architecture

IVOIREX est reconstruit sur un frontend Next.js strict et une API FastAPI. L’API sépare aujourd’hui le noyau (`core/database`), le domaine (`models/domain`) et l’entrée HTTP (`main`), afin que les prochains routers/services/repositories soient ajoutés sans mélanger les responsabilités. PostgreSQL est la cible runtime. Le modèle de monde est une source d’entrée unique dans les boucles produit réelles : cours, profil, contribution et recherche.
