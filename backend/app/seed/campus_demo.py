"""Insert or refresh clearly labelled local Campus demonstration content."""
from datetime import datetime, timezone
from sqlalchemy import select
from app.core.database import SessionLocal
from app.models.domain import Course, CourseModule, Lesson


COURSES = [
    {
        "title": "Python pour débutants",
        "slug": "python-pour-debutants",
        "short_description": "Tes premières lignes de code, des variables à un petit programme utile.",
        "description": "Découvre la logique de programmation avec Python. Tu vas lire du code, manipuler des données simples et écrire un programme court que tu pourras ensuite adapter à tes idées.",
        "category": "Programmation",
        "level": "Débutant",
        "modules": [
            ("Les bases du langage", "bases-du-langage", [
                ("Préparer son environnement", "preparer-environnement", 8, "Un programme est une suite d’instructions que la machine exécute dans l’ordre. Dans cette leçon, découvre Python, son interpréteur et la différence entre une instruction et son résultat. Commence par afficher un message, puis modifie-le et relance le programme pour observer le changement."),
                ("Variables et types simples", "variables-et-types", 12, "Une variable associe un nom à une valeur. En Python, essaie les nombres entiers, les nombres décimaux, le texte et les valeurs vrai/faux. Affiche ensuite le type d’une valeur avec type(). Choisir un nom explicite, comme total ou ville, aide une autre personne à comprendre ton intention."),
            ]),
            ("Construire un petit programme", "petit-programme", [
                ("Conditions et répétitions", "conditions-et-boucles", 15, "Une condition permet de choisir une action selon une situation. Une boucle répète une action tant qu’une règle le permet. Parcours une liste de prénoms avec for, puis utilise if pour afficher un message différent lorsque le prénom correspond à une valeur recherchée."),
                ("Fonctions et mini-projet", "fonctions-mini-projet", 15, "Une fonction regroupe des instructions réutilisables. Donne-lui un nom, des paramètres utiles et une valeur de retour claire. Pour pratiquer, écris une fonction qui calcule le coût total d’une liste d’articles, puis vérifie son résultat avec plusieurs exemples simples."),
            ]),
        ],
    },
    {
        "title": "Introduction à la cybersécurité",
        "slug": "introduction-cybersecurite",
        "short_description": "Comprends les risques courants et les gestes de défense essentiels.",
        "description": "Une introduction défensive à la sécurité numérique : actifs, menaces, mises à jour, authentification et réponse aux incidents. Les exercices restent sur des systèmes de test autorisés.",
        "category": "Cybersécurité",
        "level": "Débutant",
        "modules": [
            ("Comprendre les risques", "comprendre-risques", [
                ("Actifs, menaces et risques", "actifs-menaces-risques", 10, "Un actif est ce que l’on veut protéger : compte, appareil, document ou service. Une menace peut exploiter une faiblesse et provoquer un impact. Le risque aide à prioriser les protections selon la probabilité et les conséquences. Commence par dresser l’inventaire des actifs d’un petit projet."),
                ("Hameçonnage et ingénierie sociale", "hameconnage", 12, "Un message pressant qui demande un code secret, une pièce jointe inattendue ou un domaine presque identique au vrai sont des signaux d’alerte. Vérifie l’expéditeur par un canal indépendant et ne partage jamais un code à usage unique. Signale le message selon la procédure de ton organisation."),
            ]),
            ("Mettre en place des défenses", "defenses-essentielles", [
                ("Comptes et authentification", "comptes-authentification", 13, "Utilise un mot de passe différent pour chaque service, stocké dans un gestionnaire reconnu, et active l’authentification multifacteur. Limite les privilèges au strict nécessaire. Prépare aussi une méthode sûre de récupération du compte avant d’en avoir besoin."),
                ("Mises à jour et réponse", "mises-a-jour-reponse", 15, "Les mises à jour corrigent notamment des vulnérabilités connues. Active les mises à jour automatiques lorsque c’est possible et sauvegarde les données importantes. Si un incident survient, isole l’appareil concerné, conserve les éléments utiles et contacte l’équipe responsable; évite d’effacer les traces."),
            ]),
        ],
    },
    {
        "title": "Développement Web moderne",
        "slug": "developpement-web-moderne",
        "short_description": "Construis une page accessible et comprends le trajet navigateur-serveur.",
        "description": "Parcours les fondations du Web : structure HTML, présentation CSS, interactions, requêtes HTTP et accessibilité. Le mini-projet organise ces notions dans une page responsive simple.",
        "category": "Développement Web",
        "level": "Intermédiaire",
        "modules": [
            ("Structure et présentation", "structure-presentation", [
                ("HTML qui a du sens", "html-semantique", 12, "HTML décrit la structure et la signification d’une page. Utilise un seul titre principal, des sections nommées et des boutons pour les actions. Un lien mène vers une autre ressource; un bouton déclenche une action. Cette distinction améliore la navigation clavier et les technologies d’assistance."),
                ("CSS responsive", "css-responsive", 16, "Le modèle de boîte explique contenu, bordure, marge et espace intérieur. Utilise une grille ou flexbox pour disposer les éléments, puis une media query pour adapter les colonnes à la largeur disponible. Vérifie la page sur petit écran et évite les largeurs fixes qui provoquent un défilement horizontal."),
            ]),
            ("Interaction et livraison", "interaction-livraison", [
                ("JavaScript et événements", "javascript-evenements", 15, "Le navigateur peut réagir à une action de l’utilisateur par un événement. Sélectionne un élément, écoute un clic et mets à jour son état sans reconstruire toute la page. Valide les données avant de les utiliser et préfère textContent à l’insertion de HTML fourni par l’utilisateur."),
                ("HTTP, formulaires et accessibilité", "http-formulaires", 17, "Un formulaire transmet des données au serveur par une requête HTTP. Le serveur vérifie les champs et répond avec un statut compréhensible. Associe chaque champ à un label, conserve un focus visible, annonce les erreurs près du formulaire et indique clairement le résultat d’une action."),
            ]),
        ],
    },
    {
        "title": "Introduction à l’intelligence artificielle",
        "slug": "introduction-intelligence-artificielle",
        "short_description": "Distingue données, modèles et prédictions, avec une approche responsable.",
        "description": "Une première exploration des systèmes d’apprentissage automatique : jeu de données, entraînement, évaluation et limites. Aucun outil externe ni résultat prétendument généré par une IA n’est nécessaire.",
        "category": "Intelligence artificielle",
        "level": "Débutant",
        "modules": [
            ("Les idées fondamentales", "idees-fondamentales", [
                ("Données et exemples", "donnees-exemples", 10, "Un modèle apprend des régularités à partir d’exemples. Chaque exemple possède des caractéristiques et parfois une réponse attendue. Vérifie d’où viennent les données, qui elles représentent et quelles informations personnelles elles contiennent avant tout usage."),
                ("Entraînement et prédiction", "entrainement-prediction", 12, "L’entraînement ajuste les paramètres d’un modèle sur un ensemble d’exemples. La prédiction applique ensuite le modèle à une nouvelle entrée. Sépare les données d’entraînement et de test pour mesurer si le système généralise au-delà de ce qu’il a déjà vu."),
            ]),
            ("Évaluer avec recul", "evaluer-avec-recul", [
                ("Mesurer les erreurs", "mesurer-erreurs", 15, "Une métrique résume une partie des erreurs, jamais toute la qualité. La précision peut masquer des cas manqués; le rappel peut masquer de fausses alertes. Examine plusieurs exemples, décris le coût des erreurs et choisis les mesures qui correspondent à l’usage réel."),
                ("Biais, limites et usages", "biais-limites-usages", 15, "Des données incomplètes ou peu représentatives peuvent produire des résultats inégaux. Documente les limites connues, protège les données sensibles et garde un contrôle humain pour les décisions importantes. Un modèle de langage peut formuler une erreur avec assurance : vérifie les faits avant de les réutiliser."),
            ]),
        ],
    },
    {
        "title": "Linux et systèmes",
        "slug": "linux-et-systemes",
        "short_description": "Explore les fichiers, le terminal, les permissions et les processus.",
        "description": "Découvre les concepts Linux utiles pour développer et administrer un environnement de travail : arborescence, commandes, droits, processus et journaux.",
        "category": "Systèmes & Réseaux",
        "level": "Débutant",
        "modules": [
            ("Prendre ses repères", "reperes-linux", [
                ("Fichiers et arborescence", "fichiers-arborescence", 10, "Le système organise les fichiers dans une arborescence qui commence à la racine /. Le dossier personnel contient les fichiers d’un compte. pwd affiche le dossier courant, ls son contenu et cd permet de changer de dossier. Utilise des chemins absolus quand le contexte doit être sans ambiguïté."),
                ("Commandes et aide", "commandes-aide", 12, "Une commande reçoit souvent des options et des arguments. Lis sa documentation avec man ou l’option --help. Commence par pwd, ls, cat et less sur des fichiers que tu possèdes. Comprends la commande avant d’utiliser sudo ou une opération qui modifie plusieurs fichiers."),
            ]),
            ("Comptes et activité", "comptes-activite", [
                ("Permissions et groupes", "permissions-groupes", 14, "Les permissions contrôlent lecture, écriture et exécution pour le propriétaire, le groupe et les autres. Accorde uniquement les droits nécessaires. Avant de modifier un droit, vérifie le propriétaire et l’effet du changement; évite de rendre un dossier sensible accessible à tout le monde."),
                ("Processus et journaux", "processus-journaux", 16, "Un processus est un programme en cours d’exécution. Consulte son identifiant et sa consommation avant de l’arrêter. Les journaux enregistrent des événements utiles au diagnostic; limite leur accès et évite d’y écrire des mots de passe ou des données personnelles."),
            ]),
        ],
    },
    {
        "title": "Entrepreneuriat numérique",
        "slug": "entrepreneuriat-numerique",
        "short_description": "Passe d’un problème observé à une proposition de valeur testable.",
        "description": "Une méthode pratique pour cadrer un besoin, parler aux personnes concernées et tester une solution avant d’investir dans sa réalisation complète.",
        "category": "Entrepreneuriat",
        "level": "Débutant",
        "modules": [
            ("Comprendre le besoin", "comprendre-le-besoin", [
                ("Observer un problème concret", "observer-probleme", 10, "Commence par décrire une situation vécue par un groupe précis. Qui rencontre le problème, à quel moment et avec quelles conséquences ? Sépare les observations des suppositions. Une bonne question de départ est suffisamment précise pour pouvoir être vérifiée auprès des personnes concernées."),
                ("Mener des entretiens utiles", "entretiens-utiles", 12, "Pose des questions ouvertes sur les comportements passés : raconte la dernière fois où… Évite de demander si une personne aimerait une idée hypothétique. Écoute les solutions de contournement et prends des notes anonymisées avec l’accord des participants."),
            ]),
            ("Tester une première solution", "tester-solution", [
                ("Formuler une proposition de valeur", "proposition-valeur", 14, "Relie un public, un besoin et le résultat apporté : pour qui, quel problème, quel bénéfice ? Décris aussi ce que la première version ne fera pas. Cette limite protège le temps de l’équipe et rend le test plus facile à interpréter."),
                ("Définir une expérience", "experience-mesure", 16, "Transforme une hypothèse en test observable : action demandée, durée, résultat mesuré et règle de décision. Fixe les critères avant de regarder les résultats. Un petit test honnête peut montrer qu’il faut changer de public ou de solution, et c’est une information utile."),
            ]),
        ],
    },
]


def seed() -> int:
    now = datetime.now(timezone.utc)
    updated = 0
    with SessionLocal() as db:
        for item in COURSES:
            course = db.scalar(select(Course).where(Course.slug == item["slug"]))
            if course is None:
                course = Course(slug=item["slug"], title=item["title"], short_description=item["short_description"], description=item["description"], category=item["category"], level=item["level"], duration_minutes=1, language="fr", instructor="Équipe de démonstration IVOIREX", status="PUBLISHED", is_demo=True, published_at=now)
                db.add(course)
                db.flush()
            else:
                course.title = item["title"]
                course.short_description = item["short_description"]
                course.description = item["description"]
                course.category = item["category"]
                course.level = item["level"]
                course.language = "fr"
                course.instructor = "Équipe de démonstration IVOIREX"
                course.status = "PUBLISHED"
                course.is_demo = True
                course.published_at = course.published_at or now
            duration_total = 0
            for module_position, (module_title, module_slug, lessons) in enumerate(item["modules"]):
                module = db.scalar(select(CourseModule).where(CourseModule.course_id == course.id, CourseModule.slug == module_slug))
                if module is None:
                    module = CourseModule(course_id=course.id, title=module_title, slug=module_slug, position=module_position)
                    db.add(module)
                    db.flush()
                else:
                    module.title = module_title
                    module.position = module_position
                for lesson_position, (lesson_title, lesson_slug, lesson_duration, content) in enumerate(lessons):
                    lesson = db.scalar(select(Lesson).where(Lesson.module_id == module.id, Lesson.slug == lesson_slug))
                    if lesson is None:
                        lesson = Lesson(module_id=module.id, title=lesson_title, slug=lesson_slug, content=content, content_type="ARTICLE", duration_minutes=lesson_duration, position=lesson_position)
                        db.add(lesson)
                    else:
                        lesson.title = lesson_title
                        lesson.content = content
                        lesson.content_type = "ARTICLE"
                        lesson.duration_minutes = lesson_duration
                        lesson.position = lesson_position
                    duration_total += lesson_duration
            course.duration_minutes = duration_total
            updated += 1
        db.commit()
    return updated


if __name__ == "__main__":
    print(f"Cours de démonstration créés ou actualisés : {seed()}")
