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
python src/entrainer.py
python src/main.py
```

Dans VS Code, **Run Python File** sur `src/main.py` fonctionne également.
Un environnement virtuel est facultatif. Le poste de l'équipe utilise Anaconda
avec Python 3.14; les vérifications décrites ci-dessous ont été réalisées sous
Python 3.12. La CI est configurée pour Python 3.14 et doit être vérifiée après push.

`entrainer.py` effectue les étapes 1 et 2 : lecture, préparation, apprentissage,
évaluation et sauvegarde. L'exécuter une première fois avec le Python local,
puis seulement si les données, choix de modèle ou versions changent.
`main.py` ouvre ensuite l'interface avec `Modele.charger`, sans relire le CSV et
sans entraîner. Il peut être lancé depuis un autre dossier car ses chemins sont
construits à partir de son propre emplacement.

Tkinter doit être disponible avec l'installation Python choisie. Pour le vérifier :
`python -m tkinter` doit ouvrir une petite fenêtre. Ce module appartient à la
bibliothèque standard, mais sa présence dépend de la distribution Python; il ne
s'ajoute pas en écrivant `tkinter` dans requirements.txt. Consulter la documentation
de la distribution s'il manque. Aucun serveur web n'est nécessaire.

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
  regroupées par variable, pour le graphique d'interface. Une importance
  reflète le découpage appris par l'arbre, pas une relation causale.

Un contrôle vérifie que le rechargement produit les mêmes prédictions sans `fit`.
Le chargement vérifie la correspondance entre modèle et JSON et la version de
scikit-learn. Si cette version diffère, relancer `python src/entrainer.py` avec le Python
local pour recréer **ensemble** les deux fichiers. Le modèle inclus dans l'archive
a été généré avec scikit-learn 1.9.1; ne pas supposer sa compatibilité avec une autre
version. Charger seulement les sauvegardes de confiance produites par le projet.

La validation C (cible, métrique et modèle) n'est pas déclarée effectuée; la fiche
de décisions contient les choix à présenter. Aucun accord de l'auxiliaire n'est inventé.

## Étape 3 — Interface et historique

La maquette `donnees/maquette_interface.png` décrit les deux onglets et peut être
imprimée pour la discussion avec l'auxiliaire. Elle n'est pas une preuve
d'approbation. Tkinter a été retenu pour une fenêtre locale avec peu de
dépendances; l'accord technique D et la validation de la maquette restent à
confirmer avec l'auxiliaire, comme A, B et C.

- **Estimer une note** : plateforme, genre et classification sont des listes
  déroulantes; année et note de presse sont des champs numériques. Les noms,
  catégories, intervalles et caractère entier de l'année viennent des métadonnées
  JSON vérifiées au chargement. Aucune liste de plateformes n'est copiée dans l'interface.
- **Estimer la note** valide les cinq saisies, prédit et enregistre la note sur 10.
  Une saisie vide, non numérique, non finie, une année décimale ou une valeur hors
  intervalle affiche un message dans la fenêtre. La virgule décimale est acceptée.
  Le résultat précédent est effacé en cas d'erreur.
- **Graphique intégré** : histogramme des notes du train, lu depuis les effectifs
  sauvegardés dans le JSON, avec un trait indiquant la dernière estimation valide.
  Titre, axes et légende sont présents. La MAE de test est affichée comme qualité
  globale; aucun pourcentage de confiance individuel n'est inventé.
- **Historique** : table des dates, cinq entrées et notes prédites; les plus récentes
  sont en premier. Les estimations valides sont conservées dans
  `donnees/historique_predictions.json`, créé au premier usage et retrouvé après
  fermeture. Le bouton Actualiser relit ce fichier. Réinitialiser efface le résultat
  à l'écran et rétablit des valeurs permises, sans supprimer l'historique.

L'historique est un seul document JSON, relu puis réécrit avec `with`, adapté à
une application locale et peu d'estimations. Ce n'est pas une base multiutilisateur.
Un fichier d'historique invalide est signalé et n'est pas remplacé automatiquement.
Une erreur d'accès ne produit pas de faux message de succès. L'archive ne contient
pas les prédictions fictives des vérifications.

Les limites de l'interface sont celles observées sur train, donc plus étroites que
les échelles théoriques : année 1985–2016 et presse 13–98 sur ce jeu de données.
Par exemple, 100 est une note de presse possible en général, mais hors du domaine
observé retenu ici. Ce choix limite l'extrapolation et est annoncé près des champs.
Les catégories inconnues restent gérées dans la logique du modèle; la fenêtre
propose seulement les catégories déjà observées.

### Classes utilisées

`Variable` est une classe abstraite. `VariableNumerique` et
`VariableCategorielle` héritent de ses attributs et redéfinissent toutes deux
`valider`. `ServicePrediction` parcourt les variables avec le même appel
`variable.valider(...)` : c'est le polymorphisme. Les nombres et les choix sont
ainsi contrôlés selon leur type sans placer ces calculs dans Tkinter.

`Application` compose un service et les composants visuels. Le service compose
un `Modele`, un `Historique` et cinq objets `Variable`. `JeuDeDonnees` et `Modele`
conservent leur rôle des étapes précédentes. Les attributs internes sont préfixés
par `_`; les propriétés de listes et métadonnées renvoient des copies. Les méthodes
spéciales `__str__` donnent un résumé lisible des objets.

Pour suivre le programme : `main` charge → `Application` reçoit le service → le
bouton appelle `ServicePrediction.predire` → chaque variable valide sa saisie →
`Modele.predire` calcule → `Historique.ajouter` conserve → la fenêtre affiche.
L'entraînement reste dans le script distinct `entrainer.py`.

## Tests et couverture

```powershell
python -m pytest
python -m coverage run --source=src -m pytest
python -m coverage report -m
```

**106 cas passent** avec pandas 3.1.1 et PyArrow. Avec pandas 2.2.3 sans PyArrow :
**105 passent et 1 est ignoré**, car ce test cible un stockage optionnel absent.
Les tests couvrent les fichiers, le nettoyage, les limites, les copies, la séparation,
la MAE, la référence, la protection contre les fuites de titres et de cible, la
sauvegarde, les variables du formulaire, l'historique persistant ou invalide, et
l'utilisation de la sauvegarde sans lecture CSV ni nouvel apprentissage.

La couverture unitaire globale est de **58 %** des instructions de src; elle
inclut les modules graphiques et points d'entrée non appelés par pytest. Les
composants de logique sont couverts séparément : données **98 %**, modèle **99 %**,
exceptions **100 %**. Cette mesure n'est pas une mesure de qualité graphique et
aucun seuil n'est exigé par les consignes.

La fenêtre a également été exécutée dans une session graphique Linux sous
Python 3.12/Tk 9 : estimation normale, vide/texte/NaN/hors intervalle, virgule
décimale, résultat effacé après erreur, repère sur le graphique, deux prédictions
retrouvées après réouverture, historique invalide préservé, ouverture par main.py
sans CSV ni entraînement. L'affichage et les deux onglets ont été inspectés à
1180×800 et 1000×700. Le lancement sous Windows par l'équipe et la nouvelle CI
Python 3.14 restent à vérifier après intégration et push.

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
| `src/donnees.py` | Chargement/nettoyage/séparation, variables et historique |
| `src/modele.py` | Modèle, MAE, persistance et service de prédiction |
| `src/exceptions.py` | DonneeInvalideError, levée puis interceptée explicitement |
| `src/graphiques.py` | Figures d'exploration et d'évaluation |
| `src/entrainer.py` | Préparation et entraînement, étapes 1 et 2 |
| `src/interface.py` | Fenêtre, contrôles, graphique intégré et table d’historique |
| `src/main.py` | Ouverture de l’interface, étape 3; lancement direct dans VS Code |
| `donnees/` | CSV original et graphiques enregistrés |
| `modeles/` | Modèle ajusté et métadonnées JSON |
| `tests/` | Tests pytest de la logique |
| `pytest.ini` | Recherche des modules dans src et des tests dans tests |

Les méthodes ont des annotations et docstrings. Les calculs renvoient leurs
résultats; l’affichage appartient à l’interface ou au script d’entraînement. Les classes conservent leur état dans des
attributs internes; les propriétés renvoient des copies. Modele contient ses
objets pipeline et référence (composition), et redéfinit `__str__`.
Outil du chapitre 7 : la clé **lambda** trie les catégories des métadonnées sans
distinction de casse, pour des listes déroulantes lisibles et stables.

`requirements.txt` contient pandas (tableaux), numpy (calculs vectorisés),
scikit-learn (modèles), joblib (sauvegarde), matplotlib (figures), pytest et coverage
(vérification). `joblib` est déclaré explicitement, même s'il peut être installé
par scikit-learn, car le code l'importe directement. `os`, `copy`, `json`, `pickle`, `math`,
`datetime`, `abc` et `tkinter` sont des modules de Python; Tkinter reste optionnel
selon la distribution installée. `datetime` date les enregistrements, `math` vérifie
les nombres finis et `abc` exprime le contrat commun des deux types de variables. `pytest.ini` est facultatif en général, mais
retenu ici pour éviter de modifier sys.path et conserver le lancement direct.

## Suite du projet

- Étape 4 : audit complet des consignes, installation dans un dossier neuf,
  vérification locale Windows, couverture finale, documents relus, contributions
  réelles des deux membres et CI finale verte.
- Étape 5 : cinq minutes d'exposé puis cinq minutes de questions; démonstration
  normale, saisie invalide et graphique; parole partagée et plan B.

### Validations restant à confirmer

| Point | Avec qui et ce qu'il faut présenter |
|---|---|
| A | Auxiliaire : domaine des jeux vidéo et question étudiée |
| B | Auxiliaire : source/licence, taille, colonnes et limites du CSV |
| C | Auxiliaire : cinq entrées, cible, séparation, MAE, référence et arbre; accord prévu avant entraînement, non confirmé ici |
| D | Auxiliaire : choix Tkinter et maquette imprimée, accord prévu avant codage, non confirmé ici |
| Vérifications d'équipe | Sous Windows : installation, tests, entraînement, ouverture de la fenêtre et reprise de l'historique; sur GitHub : CI de cette révision et contributions des deux membres |

L'étape 3 est implémentée et vérifiée dans l'environnement décrit. Les tests ne
remplacent pas les accords pédagogiques; leurs dates ne seront inscrites qu'après
les échanges réels. Les documents sont mis à jour par grande étape.

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

- Tkinter (fenêtre, variables et callbacks) : https://docs.python.org/3/library/tkinter.html
- ttk (Combobox, Notebook et Treeview) : https://docs.python.org/3/library/tkinter.ttk.html
- Matplotlib intégré dans Tk : https://matplotlib.org/stable/gallery/user_interfaces/embedding_in_tk_sgskip.html
- Classe abstraite et abstractmethod : https://docs.python.org/3/library/abc.html
- Historique JSON : https://docs.python.org/3/library/json.html

Les callbacks et les composants Tkinter sont les outils nouveaux de l'étape 3.
Ils sont isolés dans interface.py; les fonctions de calcul et de validation
restent testables avec les notions de fonctions, classes et exceptions du cours.
