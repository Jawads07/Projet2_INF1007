# Projet2_INF1007 — Estimation de la note d'un jeu vidéo

## Objectif

L'application prévue estimera la note moyenne des joueurs (`User_Score`, sur 10)
à partir de cinq entrées : `Platform`, `Genre`, `Year_of_Release`, `Rating`
(classification d'âge) et `Critic_Score` (note de presse sur 100).
La note de presse est donc supposée déjà disponible. `Name` identifie les jeux
pour la séparation, mais ne sera pas utilisé comme caractéristique prédictive.

## !!! Organisation du travail en équipe !!!

Nous utilisons l'extension Visual Studio Live Share pour travailler
en binôme sur une même session VS Code.

Certaines modifications sont réalisées et relues ensemble avant
d'être regroupées dans un commit correspondant à une partie cohérente
du projet.

L'auteur affiché dans Git correspond à la personne ayant créé le
commit; il ne représente donc pas nécessairement l'unique participant
aux modifications effectuées pendant la session.

## Installation et lancement

Depuis le dossier principal, avec le même Python pour les deux commandes :

```powershell
python -m pip install -r requirements.txt
python src/main.py
```

Dans VS Code, sélectionner ce même interpréteur puis utiliser **Run Python File**
sur `src/main.py`. Les chemins sont construits avec `os` à partir de `__file__` :
le lancement ne dépend pas du répertoire courant du terminal.
Un environnement virtuel est possible, mais pas obligatoire. Anaconda est utilisé
sur le poste de développement de l'équipe; la CI est configurée pour Python 3.14.
Les vérifications disponibles ont été réalisées sous Python 3.12;
le lancement sous Python 3.14 reste à confirmer sur le poste de l’équipe et en CI.

## Étape 0 — Mise en place

Dépôt prévu public et partagé : https://github.com/Jawads07/Projet2_INF1007
L'équipe doit confirmer l'invitation du coéquipier et la visibilité publique.
Le workflow `.github/workflows/tests.yml` installe les dépendances et exécute les
tests à chaque push. La version précédente avait une CI verte; la nouvelle
exécution doit être vérifiée après l’envoi des changements.

## Étape 1 — Domaine, données et exploration

- Fichier original : `donnees/Video_Games.csv`.
- Source : https://www.kaggle.com/datasets/ibriiee/video-games-sales-dataset-2022-updated-extra-feat
- Licence annoncée sur cette fiche : CC0, domaine public.
- Dimensions vérifiées : 16 719 observations et 16 colonnes, environ 1,62 Mo.
- Entrées mixtes : trois catégorielles et deux numériques; cible numérique claire.
- Les colonnes utilisées décrivent des jeux et ne contiennent pas d'identifiants personnels.
- Les données retenues concernent les années 1985 à 2016 : elles ne représentent
  pas automatiquement le marché actuel. Les validations A et B restent à présenter
  si elles n'ont pas encore été effectuées.

Le graphique `donnees/distribution_notes.png` est enregistré par `savefig` et sera
montré lors de la présentation. Il compte les observations après nettoyage,
chaque ligne correspondant à un jeu sur une plateforme. Les notes se concentrent
entre 6 et 9, surtout entre 7 et 9. Les faibles notes sont peu représentées.

## Étape 2 — Préparation des données (partie A)

### Chargement et nettoyage

`charger_donnees` vérifie l'existence du fichier, l'ouvre avec `with`, puis le lit
avec pandas. Une erreur métier claire signale un CSV vide ou mal formé.
`nettoyer_donnees` travaille sur une copie et :

1. conserve le titre, les cinq entrées et la cible;
2. retire les espaces extérieurs des titres et catégories et reconnaît les champs vides;
3. convertit année et notes avec `to_numeric(errors="coerce")` : un texte comme `tbd`
   devient une valeur manquante;
4. retire les observations incomplètes dans les colonnes retenues;
5. vérifie une année finie, entière et positive, la presse dans [0, 100] et les
   joueurs dans [0, 10], bornes incluses.

Résultat reproduit : **6 826 observations conservées, 9 893 retirées**.
Ni le fichier CSV ni le tableau original reçu par la fonction ne sont modifiés.
Aucune moyenne n'est utilisée pour inventer une cible manquante. La suppression
d'une grande partie des observations peut toutefois introduire un biais de
sélection. Des valeurs manquantes dans les colonnes inutilisées n'excluent pas un jeu.

### Séparation reproductible

`train_test_split` réserve **20 % des titres uniques**, avec `random_state=42`.
Les titres sont regroupés sans distinction de casse ni espaces extérieurs.
Toutes les plateformes d'un même titre restent du même côté : cela réduit le
risque de retrouver un jeu presque identique pendant l'entraînement et le test.
Cette règle ne garantit pas l'absence de liens entre remakes ou jeux d'une même série.

Résultat avec le CSV fourni :

| Ensemble | Observations | Titres regroupés |
|---|---:|---:|
| Entraînement | 5 454 | 3 502 |
| Test | 1 372 | 876 |

Les proportions de lignes peuvent différer de 80/20, car on répartit les titres.
La sélection de colonnes, les conversions et les règles d'échelle sont fixes :
elles n'apprennent pas de paramètres sur le test. L'encodage des catégories sera
ajusté seulement sur l'entraînement dans le lot 2B.

La classe `JeuDeDonnees` contient les données brutes et nettoyées, protège son état
par des attributs internes et renvoie des copies via ses propriétés. Sa méthode
spéciale `__str__` donne un résumé lisible. `DonneeInvalideError` est levée pour les
erreurs métier et interceptée dans `main` avec des exceptions précises.

### Tests

```powershell
python -m pytest
python -m coverage run --source=src -m pytest
python -m coverage report -m
```

`pytest.ini` indique à pytest de chercher les modules dans `src` et les tests dans
`tests`. Le code et les tests utilisent donc les mêmes imports simples.
La configuration est expliquée dans DECISIONS.md. Les tests se lancent avec pytest, pas avec
Run Python File.
34 cas de test passent dans l’environnement de vérification. La couverture unitaire
est de 60 % pour src et de 100 % des instructions pour donnees.py et exceptions.py.
Le point d’entrée et les graphiques ont aussi été exécutés séparément.
La couverture ne concerne que les instructions parcourues par les tests, pas
la qualité des prédictions. La nouvelle CI reste à vérifier après push.

## Travail restant

- **2B** : référence prédisant la moyenne d'entraînement, encodage, modèle simple,
  métrique MAE calculée avec NumPy et comparée à scikit-learn, évaluation, sauvegarde
  joblib et métadonnées JSON. Validation C : cible, métrique et modèle à justifier.
- **3** : `interface.py` pour l'interface locale, maquette et validation D, saisies
  numériques et catégorielles construites depuis les métadonnées, validation,
  prédiction, graphique et historique. Compléter héritage, polymorphisme et composition.
- **4** : audit de toutes les exigences, couverture finale, références, documents,
  essai d'installation propre et CI finale verte. Ajouter un outil pertinent du chapitre 7.
- **5** : cinq minutes de présentation puis cinq minutes de questions, parole
  partagée, démo normale et invalide, graphique et plan B.

Le modèle et l’interface ne sont pas encore implémentés.

## Organisation

| Emplacement | Rôle |
|---|---|
| `src/donnees.py` | Étapes 1 et 2A : chargement, nettoyage, séparation et classe des données |
| `src/exceptions.py` | Exception métier personnalisée |
| `src/graphiques.py` | Graphique d'exploration; distinct de la future interface |
| `src/main.py` | Appels successifs et affichage des résultats |
| `src/modele.py` | Sera créé pour le modèle à l’étape 2B |
| `donnees/` | CSV original et histogramme |
| `modeles/` | Réservé au modèle sauvegardé et aux métadonnées |
| `tests/` | Tests automatisés de la logique |
| `DECISIONS.md`, `JOURNAL_IA.md` | Choix, validations et aide reçue |

## Dépendances et configuration

`requirements.txt` contient seulement les noms des bibliothèques utilisées :

| Bibliothèque | Utilisation |
|---|---|
| pandas | Lecture et nettoyage des tableaux |
| NumPy | Vérification vectorisée des années finies; calcul de métrique prévu ensuite |
| scikit-learn | Séparation des titres avec train_test_split |
| Matplotlib | Histogramme enregistré |
| pytest | Tests automatiques |
| coverage | Mesure de la couverture des tests |

Aucune version minimale n'est imposée dans ce fichier. Les vérifications actuelles
ont utilisé pandas 2.2.3, NumPy 2.3.5, scikit-learn 1.8.0, Matplotlib 3.10.8,
pytest 9.2.0 et coverage 7.17.3 sous Python 3.12.14. Une installation sur un autre
Python peut choisir d'autres versions compatibles; il faut alors relancer les tests.
`os` est fourni avec Python : il ne doit pas être installé.

`pytest.ini` est le seul fichier de configuration ajouté pour les imports des tests :
`pythonpath = src` permet d'importer les modules comme dans main.py;
`testpaths = tests` indique où chercher les tests. Ce fichier n'est pas imposé par
l'énoncé. Il évite des imports différents et conserve le lancement direct dans VS Code.

## Notes de cours et documentation officielle

- Ch. 5 : fichiers, `with`, chemins avec `os`.
- Ch. 6–7 : fonctions, annotations, docstrings et modules.
- Ch. 8 : exceptions, pytest et intégration continue.
- Ch. 9–11 : classes, encapsulation, propriétés et méthodes spéciales.
- Ch. 12–13 : tableaux, graphiques et lecture des documentations.
- pandas, lecture : https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html
- pandas, conversion : https://pandas.pydata.org/docs/reference/api/pandas.to_numeric.html
- pandas, valeurs manquantes : https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.dropna.html
- scikit-learn, séparation : https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.train_test_split.html
- pytest, configuration : https://docs.pytest.org/en/stable/reference/customize.html
- Matplotlib, histogramme : https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.hist.html
- GitHub Actions : https://docs.github.com/en/actions/tutorials/build-and-test-code/python

La référence de la technologie d'interface et les résultats du modèle seront
ajoutés lors des lots concernés. Aucun score de modèle n'a encore été mesuré.
