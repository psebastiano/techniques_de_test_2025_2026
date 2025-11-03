# Plan de Tests : Service de Triangulation

Ce plan détaille les vérifications essentielles pour valider le bon fonctionnement du service de triangulation (T) et son interaction avec le gestionnaire de jeux de points (PSM).

---

## 1. Tests de Connexion et Flux (End-to-End)

Ces tests vérifient que les composants peuvent communiquer correctement, permettant au client de déclencher une opération complète.

* **Connexion Client <-> Triangulateur (T)**
    - Est-ce que le Triangulateur (T) est connecté au Client (C) ?
* **Connexion Triangulateur (T) <-> PointSetManager (PSM)**
    - Est-ce que le T est connecté au PointSetManager (PSM) ?
* **Validation de l'Appel Inter-Service**
    - Est-ce qu'une demande au T **génère** un appel vers le PSM ?

> Si ces tests sont validés, le Client peut communiquer avec T, et ce dernier peut communiquer avec le PSM.

---

## 2. Intégrité des Données d'Entrée (PointSet)

Ces tests assurent que les données reçues du PSM sont valides et cohérentes avant tout traitement interne.

* **Format de l'Identifiant (PSid)**
    - Est-ce que l'identifiant du PointSet (PS), le PSid, a le bon format ?
* **Existence du PointSet**
    - Est-ce que le PS existe ? On pourra évaluer la réponse du PSM.
* **Cohérence de la Longueur Binaire**
    - Est-ce que le PS est correct : sa **longueur** correspond au nombre de points **annoncé** dans les 4 premiers bytes ?
* **Unicité des Points**
    - Est-ce que chaque point est unique ?

> Si ces tests **passent**, on peut alors procéder à l'étape de conversion entre la chaîne **binaire** du PS et la représentation interne des points dans le T.

---

## 3. Validation de la Conversion de Données

Ces tests vérifient l'exactitude des transformations entre les formats binaire et interne du Triangulateur.

### 3.1. Conversion Pré-Triangulation (Binaire -> Géométrique)

* **Avant triangulation : conversion de PS binaire vers PS "géométrique"**
    - Est-ce que l'on a le bon nombre de points après conversion ?

### 3.2. Conversion Post-Triangulation (Géométrique -> Binaire)

* **Après triangulation : conversion de Triangles (Tr) "géométrique" vers binaire**
    - Est-ce que la chaîne commence bien par la partie PS, identique à l'entrée ?
    - Est-ce que le nombre de **triangles** indiqué correspond à la longueur de la deuxième partie de la chaîne ?

---

## 4. Tests de l'Algorithme de Triangulation

Ces tests se concentrent sur la robustesse et la justesse de l'algorithme de triangulation lui-même.

* **Conditions Préalables**
    - Avant de commencer l'algorithme, il convient de vérifier que l'ensemble de **points vérifie** les conditions nécessaires à la triangulation (ex. il ne doit pas s'agir d'un **ensemble** de points tous alignés sur une droite).
* **Convergence et Robustesse**
    - Est-ce que l'algorithme converge ? On peut tester pour les ensembles suivants :
        - Distribution aléatoire
        - Densité variable
        - Zone pleine et zone creuse
        - Ensemble très petit : 1, 2 ou 3 points non alignés
* **Validité de la Sortie (Si convergence)**
    - Si convergence, est-ce que :
        - On obtient effectivement des **triangles** ?
        - Les **triangles** ne **s'entrecoupent** pas ?
        - Il n'y a pas d'espace vide ?

---

## 5. Performance et Qualité

Ces tests évaluent l'efficacité et la qualité du résultat de la triangulation.

* **Temps de Convergence**
    - En combien de temps l'algorithme converge-t-il ?
    - En fonction du type de distribution ?
    - En fonction de l'ordre de grandeur du nombre de points de PS (10^n, n = 1 à 9) ?
* **Qualité de la Triangulation**
    - Est-ce que la taille des **triangles** connaît des variations soudaines ou extrêmes ?
 
- ---

## 6. Tests de Robustesse et Gestion des Erreurs

Ces tests vérifient le comportement du Triangulateur face à des requêtes invalides, des données corrompues, ou des défaillances de services externes (non-happy path).

### 6.1. Erreurs Liées à l'Entrée Utilisateur (API)

* **Format du PSid Invalide**
    - Est-ce que l'identifiant du PointSet (PSid) fourni par le Client (C) est un **format invalide** (non-UUID) ? Le T doit retourner une erreur **`400 Bad Request`**.

### 6.2. Erreurs Liées au PointSetManager (PSM)

* **PointSet Non Trouvé (404)**
    - Le T gère-t-il correctement le cas où le PSM répond **`404 Not Found`** pour un PSid valide ? Le T doit retourner une erreur appropriée au Client.
* **PSM Indisponible (5xx)**
    - Le T gère-t-il correctement une défaillance ou une indisponibilité du PSM (ex. réponse **`503 Service Unavailable`**) ? Le T doit relayer l'erreur au Client.
* **Données du PSM Invalides**
    - Le T gère-t-il le cas où le PSM renvoie une chaîne binaire qui **ne respecte pas la structure du `PointSet`** (longueur incohérente, données tronquées, etc.) ? Le T doit retourner une erreur interne/client appropriée.

### 6.3. Erreurs Internes et Sortie

* **Échec de la Triangulation**
    - Si l'algorithme de triangulation échoue pour une raison interne (problème mémoire, exception), le T retourne-t-il un code d'erreur **`500 Internal Server Error`** ?

---
