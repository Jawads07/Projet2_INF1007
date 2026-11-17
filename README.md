# Projet2_INF1007 — Estimation de la note d'un jeu vidéo

## Objectif

Estimer la note moyenne des joueurs (`User_Score`, sur 10) à partir de cinq
caractéristiques : plateforme, genre, année de sortie, classification d'âge et
note de la presse (`Critic_Score`, sur 100). Les critiques de presse sont donc
supposées déjà disponibles. Le titre sert au regroupement des observations,
mais n'est jamais une entrée du modèle. Les ventes ne sont pas utilisées.


## Installation et exécution

Depuis le dossier principal, avec le même interpréteur Python :

```powershell
python -m pip install -r requirements.txt
python -m pytest
python src/main.py
```

Dans VS Code, **Run Python File** sur `src/main.py` fonctionne également.
Un environnement virtuel est facultatif. Le poste de l'équipe utilise Anaconda
avec Python 3.14; les vérifications décrites ci-dessous ont été réalisées sous
Python 3.12. La CI est configurée pour Python 3.14 et doit être vérifiée après push.

`main.py` est actuellement le script de préparation : il entraîne le modèle,
l'évalue et régénère ses fichiers. L'interface de l'étape 3 utilisera
`Modele.charger` sans lire le CSV ni réentraîner à chaque lancement.

## Étape 0 — Organisation

Le dépôt prévu public et partagé est https://github.com/Jawads07/Projet2_INF1007.
Le workflow exécute pytest et mesure la couverture après chaque push. `pytest.ini`
indique où trouver les modules (`src`) et les tests (`tests`), afin de conserver
les mêmes imports simples dans le code et dans les tests.

!!! Organisation du travail en équipe !!!
Nous utilisons l'extension Visual Studio Live Share pour travailler en binôme sur une même session VS Code.

Certaines modifications sont réalisées et relues ensemble avant d'être regroupées dans un commit correspondant à une partie cohérente du projet.

L'auteur affiché dans Git correspond à la personne ayant créé le commit; il ne représente donc pas nécessairement l'unique participant aux modifications effectuées pendant la session.

## Étape 1 — Données et exploration

- Fichier original : `donnees/Video_Games.csv`, 16 719 observations et 16 colonnes,
  environ 1,62 Mo.
- Source : https://www.kaggle.com/datasets/ibriiee/video-games-sales-dataset-2022-updated-extra-feat
- Licence annoncée sur la fiche source : CC0, domaine public.
- Données tabulaires avec cinq entrées : trois catégorielles et deux numériques;
  cible numérique claire, sans données identifiant une personne dans les colonnes utilisées.
- Graphique enregistré : `donnees/distribution_notes.png`. Les observations
  conservées se concentrent surtout entre 6 et 9. Les faibles notes sont rares.
- Une observation représente un titre sur une plateforme, pas forcément un titre unique.

Les validations A (domaine) et B (données) sont à confirmer avec l'auxiliaire.

## Étape 2A — Préparation et séparation

Le chargement vérifie l'existence du CSV et utilise `with`. Le nettoyage travaille
sur une copie : sélection des cinq entrées, de la cible et du titre; retrait des
espaces extérieurs; conversion numérique avec `to_numeric(errors="coerce")`;
retrait des lignes incomplètes. Les notes doivent respecter [0,100] pour la presse
et [0,10] pour les joueurs, bornes incluses. L'année doit être finie, entière et positive.
Le CSV et le tableau original ne sont pas modifiés.

Résultat reproduit : **6 826 observations conservées, 9 893 retirées**.
Les valeurs manquantes de colonnes inutilisées ne font pas exclure une observation.
La suppression de nombreuses lignes peut créer un biais de sélection.
Les données conservées concernent les années 1985 à 2016 et ne représentent donc
pas automatiquement les jeux récents.

`train_test_split` répartit les titres uniques : **20 % des titres pour le test,
graine 42**, sans titre commun entre les ensembles. Toutes les plateformes d'un
même titre restent du même côté; la casse et les espaces extérieurs sont ignorés
pour ce regroupement. La conversion des titres uniques en liste Python évite une
incompatibilité d'indexation PyArrow. La règle ne détecte pas les liens entre des
remakes ou des jeux différents d'une même série.

| Ensemble | Observations | Titres regroupés |
|---|---:|---:|
| Entraînement | 5 454 | 3 502 |
| Test | 1 372 | 876 |

Le nettoyage utilise des règles fixes et n'apprend aucun paramètre statistique sur
le test. Les catégories et paramètres du modèle sont appris seulement après séparation.

## Étape 2B — Référence, apprentissage et évaluation

### Référence et modèle

La référence `DummyRegressor(strategy="mean")` prédit toujours la moyenne des notes
d'entraînement : **7,156857/10**. Elle ignore les caractéristiques.

L'arbre de régression a une profondeur maximale de **5**, au moins **10 observations
par feuille** et une graine de **42**. Ces réglages ont été fixés avant d'observer
le score de test, sans recherche de paramètres sur ce test. La profondeur limite
la complexité; le minimum de dix observations évite des feuilles fondées sur un
seul exemple. L'arbre utilise le critère d'entraînement par défaut, erreur quadratique,
et prédit la moyenne des observations de chaque feuille.

Les catégories sont transformées par `OneHotEncoder(handle_unknown="ignore")` :
une colonne binaire par catégorie, sans introduire d'ordre artificiel entre les
plateformes. Une catégorie inconnue ne provoque pas de nouvel apprentissage.
Les deux entrées numériques sont transmises sans normalisation, qui n'est pas
nécessaire pour les seuils d'un arbre. `ColumnTransformer` et `Pipeline` regroupent
le prétraitement et l'arbre : un seul `fit` est réalisé sur l'entraînement.
`Name` et `User_Score` sont explicitement exclus des entrées.

### Métrique et résultats

La métrique est l'**erreur absolue moyenne (MAE)**, en points sur 10 :
`mean(abs(notes_reelles - notes_predites))`. Le calcul utilise NumPy sans boucle
Python et un test vérifie sa concordance avec `mean_absolute_error` de scikit-learn.
Une MAE plus faible est meilleure; ce n'est ni un pourcentage de réussite ni un
intervalle de confiance pour chaque prédiction.

| Méthode | MAE sur les 1 372 observations de test |
|---|---:|
| Moyenne d'entraînement | 1,060943 |
| Arbre de décision | 0,762572 |
| Réduction de MAE | 0,298371 |

Ces valeurs ont été reproduites avec scikit-learn 1.8.0 et 1.9.1 dans les deux
environnements de vérification. Le graphique `donnees/predictions_test.png`
compare les notes prédites aux notes réelles. La diagonale représente la prédiction
parfaite. Les bandes horizontales viennent des valeurs constantes prédites dans
les feuilles de l'arbre. Les faibles notes peuvent être fortement surestimées :
la MAE globale ne garantit pas la même qualité pour tous les jeux.

### Sauvegarde et métadonnées

- `modeles/modele.joblib` : classe Modele, pipeline déjà ajusté et référence.
- `modeles/metadonnees.json` : cinq entrées dans l'ordre, catégories et intervalles
  observés **dans l'entraînement**, cible, métriques, réglages et versions.
- Le JSON contient aussi la distribution de cible d'entraînement et les importances
  regroupées par variable, pour le futur graphique d'interface. Une importance
  reflète le découpage appris par l'arbre, pas une relation causale.

Un contrôle vérifie que le rechargement produit les mêmes prédictions sans `fit`.
Le chargement vérifie la correspondance entre modèle et JSON et la version de
scikit-learn. Si cette version diffère, relancer `python src/main.py` avec le Python
local pour recréer **ensemble** les deux fichiers. Le modèle inclus dans l'archive
a été généré avec scikit-learn 1.9.1; ne pas supposer sa compatibilité avec une autre
version. Charger seulement les sauvegardes de confiance produites par le projet.

La validation C (cible, métrique et modèle) n'est pas déclarée effectuée; la fiche
de décisions contient les choix à présenter. Aucun accord de l'auxiliaire n'est inventé.

## Tests et couverture

```powershell
python -m pytest
python -m coverage run --source=src -m pytest
python -m coverage report -m
```

**65 cas passent** avec pandas 3.1.1 et PyArrow. Avec pandas 2.2.3 sans PyArrow :
**64 passent et 1 est ignoré**, car ce test cible un stockage optionnel absent.
Les tests couvrent les fichiers, le nettoyage, les bornes, les copies, la séparation,
la MAE, la référence, la protection contre l'évaluation sur train, les catégories
inconnues, l'exclusion de la cible, la sauvegarde et le rechargement.

Couverture unitaire mesurée : **73 % des instructions de src**; données et
exceptions 100 %, modèle 99 %. Le point d'entrée et les graphiques ont été exécutés
séparément et inspectés; ils ne sont pas inclus dans cette couverture unitaire.
Aucun seuil n'est exigé par les consignes. Une CI verte de cette révision reste à
confirmer sur GitHub après push.

Vérifications sous Python 3.12.14 :

| Bibliothèque | Environnement de base | Environnement récent |
|---|---|---|
| pandas | 2.2.3 | 3.1.1 |
| NumPy | 2.3.5 | 2.5.5 |
| scikit-learn | 1.8.0 | 1.9.1 |
| joblib | 1.5.3 | 1.6.0 |
| Matplotlib | 3.10.8 | 3.11.2 |
| pytest / coverage | 9.2.0 / 7.17.3 | 9.2.0 / 7.17.3 |

PyArrow 26.0.1 est présent seulement dans le second environnement. Les versions
ne sont pas imposées dans requirements.txt; les tests doivent être relancés après
installation. Le test spécifique à PyArrow est ignoré s'il n'est pas installé.

## Organisation et choix techniques

| Fichier ou dossier | Rôle |
|---|---|
| `src/donnees.py` | Chargement, nettoyage, séparation; classe JeuDeDonnees |
| `src/modele.py` | Référence, pipeline, métrique, évaluation et persistance; classe Modele |
| `src/exceptions.py` | DonneeInvalideError, levée puis interceptée explicitement |
| `src/graphiques.py` | Figures d'exploration et d'évaluation |
| `src/main.py` | Appels dans l'ordre du travail; lancement direct dans VS Code |
| `donnees/` | CSV original et graphiques enregistrés |
| `modeles/` | Modèle ajusté et métadonnées JSON |
| `tests/` | Tests pytest de la logique |
| `pytest.ini` | Recherche des modules dans src et des tests dans tests |

Les méthodes ont des annotations et docstrings. Les calculs renvoient leurs
résultats, l'affichage est dans main. Les classes conservent leur état dans des
attributs internes; les propriétés renvoient des copies. Modele contient ses
objets pipeline et référence (composition), et redéfinit `__str__`.
Outil du chapitre 7 : la clé **lambda** trie les catégories des métadonnées sans
distinction de casse, pour des listes déroulantes lisibles et stables.

`requirements.txt` contient pandas (tableaux), numpy (calculs vectorisés),
scikit-learn (modèles), joblib (sauvegarde), matplotlib (figures), pytest et coverage
(vérification). `joblib` est déclaré explicitement, même s'il peut être installé
par scikit-learn, car le code l'importe directement. `os`, `copy`, `json` et
`pickle` sont fournis avec Python. `pytest.ini` est facultatif en général, mais
retenu ici pour éviter de modifier sys.path et conserver le lancement direct.

## Suite du projet

- Étape 3 : choix de technologie et maquette à présenter pour D, `interface.py`,
  saisies construites depuis le JSON, contrôles de champs et d'intervalles,
  prédiction, graphique Matplotlib et historique. Compléter les classes exigées,
  notamment la classe parente et deux enfants avec redéfinition de méthode.
- Étape 4 : audit complet, installation dans un dossier neuf, couverture finale,
  documents finalisés, contributions réelles des deux membres et CI finale verte.
- Étape 5 : cinq minutes d'exposé puis cinq minutes de questions, démo normale,
  saisie invalide, graphique, parole partagée et plan B.

L'interface n'est pas encore implémentée. L'historique des prédictions et
l'héritage/polymorphisme sont donc encore à compléter. Les trois documents sont
mis à jour par grande étape, sans inventer de validations ou de résultats.

## Notes de cours et références

Les fichiers et os sont issus du chapitre 5, les fonctions et modules des
chapitres 6–7, les tests et exceptions du chapitre 8, les classes/propriétés des
chapitres 9–11, NumPy et figures des chapitres 12–13. Les outils supplémentaires
sont documentés ici :

- pandas, lecture : https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html
- pandas, conversion : https://pandas.pydata.org/docs/reference/api/pandas.to_numeric.html
- pandas, valeurs manquantes : https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.dropna.html
- Séparation : https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.train_test_split.html
- Référence : https://scikit-learn.org/stable/modules/generated/sklearn.dummy.DummyRegressor.html
- Encodage : https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.OneHotEncoder.html
- Pipeline et colonnes : https://scikit-learn.org/stable/modules/compose.html
- Arbre : https://scikit-learn.org/stable/modules/generated/sklearn.tree.DecisionTreeRegressor.html
- MAE : https://scikit-learn.org/stable/modules/generated/sklearn.metrics.mean_absolute_error.html
- Sauvegarde : https://scikit-learn.org/stable/model_persistence.html
- pytest : https://docs.pytest.org/en/stable/reference/customize.html
- Histogramme : https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.hist.html
- CI : https://docs.github.com/en/actions/tutorials/build-and-test-code/python

La documentation de la technologie d'interface sera ajoutée au choix de l'étape 3.
