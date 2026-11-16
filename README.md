# Projet2_INF1007 — Estimation de la note d'un jeu vidéo

## Objectif

Développer une application locale qui estime la note moyenne des joueurs
sur 10 à partir de cinq caractéristiques :

- Plateforme : Platform
- Genre : Genre
- Année de sortie : Year_of_Release
- Classification d'âge : Rating
- Note moyenne de la presse sur 100 : Critic_Score

La variable cible est User_Score.
L'application suppose que la note de la presse est déjà disponible.

## Jeu de données

Fichier : donnees/Video_Games.csv

Source :
https://www.kaggle.com/datasets/ibriiee/video-games-sales-dataset-2022-updated-extra-feat

Licence annoncée sur la fiche Kaggle : CC0, domaine public.

Le fichier contient 16 719 lignes et 16 colonnes.
Ces dimensions ont été vérifiées en exécutant le programme.

## Installation

Python 3.14.7 est utilisé pour le développement.

Depuis le dossier principal du projet :

```powershell
python -m pip install -r requirements.txt
```

## Exécution

Depuis le dossier principal du projet :

```powershell
python src/main.py
```

## Organisation

- src/ : code Python.
- donnees/ : CSV original.
- modeles/ : futur modèle sauvegardé et métadonnées.
- tests/ : tests automatisés.
- DECISIONS.md : choix et justifications.
- JOURNAL_IA.md : utilisation de l'IA et vérifications.

## Démarche et état actuel

Le programme charge le CSV avec pandas et affiche ses dimensions
ainsi que ses premières lignes.

Le nettoyage est implémenté : il conserve les colonnes nécessaires,
convertit les valeurs numériques et retire les lignes incomplètes
ou contenant des notes hors limites.

Sur 16 719 lignes initiales, 6 826 sont conservées et 9 893 retirées.
Le CSV original reste inchangé.

L'entraînement n'est pas encore implémenté.
Le modèle envisagé est un arbre de décision pour la régression.
L'évaluation prévue utilise l'erreur absolue moyenne, comparée à
une référence prédisant toujours la moyenne des notes d'entraînement.

## Documentation consultée

- Lecture d'un CSV avec pandas :
  https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html

  ## Tests

Depuis le dossier principal :

```powershell
python -m pytest
```

Deux tests vérifient le chargement :
- un fichier CSV existant est lu correctement;
- un fichier absent déclenche FileNotFoundError.

Ces tests passent localement et sur GitHub Actions.
Le workflow relance les tests après chaque push.

## Environnement de développement

Nous utilisons Python 3.14, avec Anaconda sur notre poste.
Les bibliothèques nécessaires sont indiquées dans requirements.txt.
La CI utilise Python 3.14 sur Ubuntu.

## Nettoyage réalisé

La fonction travaille sur une copie du tableau et conserve les colonnes
nécessaires au projet.

Les colonnes numériques sont converties avec pandas. Les valeurs
non convertibles, comme "tbd", deviennent des valeurs manquantes.
Les lignes incomplètes sont retirées.

Les notes de la presse doivent être comprises entre 0 et 100,
et celles des joueurs entre 0 et 10, bornes incluses.

Résultat : 6 826 lignes conservées sur 16 719, soit 9 893 retirées.
Le CSV original reste inchangé.

Cette suppression peut réduire la représentativité des données :
les jeux sans notes complètes sont exclus.

L'entraînement du modèle n'est pas encore implémenté.

## Exploration des notes

Le graphique donnees/distribution_notes.png présente la distribution
des notes des joueurs dans les données conservées après nettoyage.

Les observations se concentrent principalement entre 6 et 9,
particulièrement entre 7 et 9. Les faibles notes sont peu représentées,
ce qui pourrait limiter les prédictions du modèle pour ces valeurs.

Chaque observation correspond à une ligne du CSV; un même titre
peut apparaître sur plusieurs plateformes.