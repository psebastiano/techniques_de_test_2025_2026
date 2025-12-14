# Retour d'expérience - Micro-service Triangulator  

## 1. Introduction  
Ce document présente un retour d'expérience synthétique suite à la réalisation du micro-service **Triangulator** pour le TP de Techniques de Test 2025/2026. L'objectif principal de ce projet était d'adopter une approche **test-first** et de mettre en place une suite de tests unitaires, d'intégration et de performance pour valider une implémentation.

## 2. Bilan Global des Tests et de la Qualité  

| Aspect                     | Statut Final      | Commentaire                                                                                                                                 |
|----------------------------|-------------------|---------------------------------------------------------------------------------------------------------------------------------------------|
| **Couverture de Code**     | 100%              | Objectif atteint sur la logique métier et la couche API, en excluant uniquement la ligne de lancement du serveur (`triangulator_app.run(debug=True, port=5000)', avec le commentaire : '# pragma: no cover`. |
| **Tests Unitaires**        | Très complet      | Tests granulaires sur la conversion binaire, la validation d'UUID, et la logique de triangulation.                                           |
| **Tests d'API (Intégration)** | Complet          | Couverture des chemins de succès (200 OK) et de toutes les erreurs HTTP attendues (400, 404, 500, 503) grâce au mocking.                    |
| **Tests de performance** | Satisfaisant          | Evaluation du temps de triangulation pour un PointSet de 1000 points aléatoires.                                                          |
| **Qualité de Code (Ruff)** | Satisfaisant      | Conformité aux règles de style et de documentation imposées par `ruff check`.                                                               |

## 3. Apprentissage de la Méthodologie Test-First  

L'approche **test-first** m'a permis de découvrir l'utilité concrète des tests dans le processus de développement. Je me suis rendu compte qu'une fois les tests en place, le codage des fonctions devient considérablement plus simple car tout est déjà défini : le workflow, les types en entrée et les types en sortie.

J'ai appris à analyser le logiciel d'abord à un **niveau élevé d'abstraction**, en définissant uniquement les signatures des fonctions, puis en évaluant systématiquement les cas de succès et d'échec avant même de commencer l'implémentation. Cette méthode, bien que demandant un travail important et semblant contre-intuitive au départ, s'est révélée extrêmement payante au moment de l'implémentation proprement dite, garantissant un code plus robuste et mieux structuré.

## 4. Difficultés Rencontrées et Leçons Apprises  

### 4.1. Maîtrise de l'Architecture et du Mocking (Difficulté Majeure)  
La principale source de difficulté a résidé dans la compréhension de l'architecture micro-service et l'utilisation des **Mocks**.

- **Complexité Initiale** : Mon expérience limitée en développement web et architecture distribuée a rendu difficle de déterminer précisément quelle partie du système je devais implémenter (Triangulator) et quelles interactions (avec le PointSetManager et la Base de Données) devaient être isolées et simulées (mockées). La compréhension du rôle exact du Triangulator dans l'architecture générale a été un challenge.
- **Les Mocks** : La maîtrise de la bibliothèque `unittest.mock.patch` s'est révélée un obstacle majeur. Les erreurs récurrentes liées au chemin d'accès au module (patch target) (`AttributeError: module 'application' does not have the attribute 'getTriangulation'`) ont nécessité une compréhension approfondie de la façon dont Python résout les importations en environnement de test.

**Leçon Apprise** : Le mocking est indispensable pour tester une couche d'API interdépendante. Il est crucial de s'assurer que le chemin de patch pointe vers **l'endroit où l'objet est utilisé** (`application.triangulator_app.getTriangulation`) et non pas simplement où il est défini.

### 4.2. Découverte et Utilisation des Outils de Qualité et de Couverture
- **Ruff** : J'ai découvert l'outil Ruff et je le trouve excellent. Bien qu'il soit parfois exigeant de se conformer à toutes ses règles de style et de documentation, le travail se fait progressivement durant le développement. Le résultat est très positif : le code final sort déjà propre, bien documenté et conforme aux standards, ce qui améliore grandement sa lisibilité et sa maintenabilité.
- **Couverture de code (Coverage)** : J'ai trouvé la mesure de couverture très utile pour s'assurer que les tests balayaient effectivement toutes les parties du code. Dans mon cas, j'ai dû exclure explicitement la ligne `triangulator_app.run(debug=True, port=5000)` dans le bloc `if __name__ == "__main__"` du fichier principal. En effet, couvrir cette ligne de démarrage du serveur Flask n'avait pas de sens dans un contexte de test automatisé, puisque l'objet `triangulator_app` et sa route étaient déjà testés de manière exhaustive par des fonctions de test dédiées.
  
### 4.3. Maîtrise des Outils de Développement et Architecture Python
- **Utilisation des Makefiles** : Ce projet m'a permis de découvrir l'utilité pratique des Makefiles pour automatiser les tâches de développement. J'ai appris à exploiter les commandes `make test_all`, `make test_unit`, `make test_perf`, `make quality` et `make coverage` pour standardiser et simplifier mon workflow, réduisant ainsi les erreurs manuelles et garantissant la reproductibilité des vérifications.
- **Compréhension de l'Architecture** : L'exercice m'a offert une vision beaucoup plus claire de la structure typique d'une application Python moderne, avec sa séparation entre modules d'application, de test, et de configuration. J'ai notamment mieux compris l'organisation des imports, la gestion des dépendances, et l'importance d'une séparation nette des responsabilités entre les différentes couches (API, logique métier, utilitaires).

## 5. Rétrospective : Ce que je Ferais Différemment  

### 5.1. Organisation et Maintenance des Fixtures
Bien que mes fixtures aient été fonctionnelles et bien commentées, j'ai réalisé que leur organisation pouvait être optimisée pour une meilleure maintenabilité.

**Observation** : Certaines fixtures paramétrées mélangeaient différents types de scénarios d'erreur (ex: format UUID invalide ET type de données incorrect), ce qui pouvait rendre le diagnostic plus difficile lors d'un échec de test.

**Approche améliorée** : Je structurerais désormais les fixtures de manière plus granulaire :
- Séparer les fixtures par **type de faute** (format vs type)
- Créer des fixtures dédiées aux **cas de succès** vs **cas d'échec**
- Extraire les grandes fixtures complexes (comme `triangulation_geometric_pairs` avec ses 9 cas) en plusieurs fixtures plus petites et ciblées

Cette approche faciliterait la lisibilité des tests et permettrait une couverture plus facile à tracer et à maintenir à long terme.

### 5.2. Structuration et Clarté du Code  
Bien que le code soit fonctionnel, la structure des fichiers et des imports pourrait être améliorée.  

**Action Corrigée** : Je mettrais plus d'effort à séparer plus strictement les responsabilités : par exemple, regrouper toutes les fonctions utilitaires (conversion binaire, validation d'UUID) dans un module dédié (`utils.py`) au lieu de les laisser dans le module principal (`triangulator_app.py`). Cela simplifierait à la fois les imports et les chemins de patch dans les tests.

### 5.3. Apprentissage de la Gestion des Erreurs HTTP dans Flask  
Bien que j'aie anticipé dès le départ la nécessité de tester les différents codes d'erreur HTTP (400, 404, 500, 503), je manquais d'expérience concrète avec Flask pour savoir comment les implémenter correctement.

**Découverte technique** : J'ai appris que Flask nécessite l'utilisation explicite de décorateurs `@app.errorhandler` pour intercepter et formater proprement les différentes erreurs HTTP. Cette approche diffère d'autres frameworks où la gestion d'erreurs peut être plus implicite ou centralisée.

**Réalisation** : Mon plan de tests était donc théoriquement complet, mais je n'avais pas prévu le travail d'implémentation spécifique requis par Flask pour rendre ces erreurs "testables" de manière unitaire.

**Leçon apprise** : Je réalise maintenant l'importance de comprendre non seulement **quoi** tester (les cas d'erreur), mais aussi **comment** le framework sous-jacent permet de gérer ces cas. Dans un futur projet Flask, je rechercherais dès le début les bonnes pratiques de gestion d'erreurs propres à ce framework.

## 6. Conclusion  
Ce projet a été une excellente opportunité pour passer d'une approche de codage simple à une approche de **développement piloté par les tests (TDD)**. La nécessité d'atteindre **100% de couverture** a forcé l'exploration de cas d'erreurs complexes (mocking, exceptions HTTP), transformant les difficultés initiales en une solide compréhension des meilleures pratiques de tests en Python/Flask. L'approche test-first, bien qu'exigeante, s'est révélée être un investissement précieux pour produire un code plus fiable et maintenable.
