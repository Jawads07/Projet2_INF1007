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