"""Étapes 1 et 2 — Script de préparation, distinct du lancement de l’interface."""

import os

import numpy as np

from donnees import CARACTERISTIQUES, CIBLE, JeuDeDonnees
from exceptions import DonneeInvalideError
from graphiques import enregistrer_distribution_notes, enregistrer_predictions
from modele import Modele


def entrainer() -> None:
    """Charge, prépare, entraîne, évalue et sauvegarde le modèle; ne renvoie rien.

    Affiche les erreurs attendues de fichier, d'encodage et de données.
    Ce point d’entrée prépare le modèle; l'interface recharge ensuite sa sauvegarde.
    """
    dossier_src = os.path.dirname(os.path.abspath(__file__))
    dossier_projet = os.path.dirname(dossier_src)
    chemin_csv = os.path.join(dossier_projet, "donnees", "Video_Games.csv")

    try:
        # Étape 1 — Chargement et exploration.
        jeu = JeuDeDonnees(chemin_csv)
        df = jeu.originales
        print("Nombre de lignes :", df.shape[0])
        print("Nombre de colonnes :", df.shape[1])
        colonnes = CARACTERISTIQUES + [CIBLE]
        if any(nom not in df.columns for nom in colonnes):
            raise DonneeInvalideError("Le CSV ne contient pas les colonnes du projet.")
        print("\nTypes des colonnes utilisées :")
        print(df[colonnes].dtypes)
        print("\nValeurs manquantes par colonne :")
        print(df[colonnes].isna().sum())
        print("\nNombre de notes joueurs égales à 'tbd' :")
        print((df[CIBLE] == "tbd").sum())

        # Étape 2A — Nettoyage et contrôle du résultat.
        jeu.nettoyer()
        df_nettoye = jeu.nettoyees
        print("\nLignes avant nettoyage :", len(df))
        print("Lignes après nettoyage :", len(df_nettoye))
        print("Lignes retirées :", len(df) - len(df_nettoye))
        print("\nValeurs manquantes après nettoyage :")
        print(df_nettoye.isna().sum())

        # Graphique d'exploration de l'étape 1, sur les observations conservées.
        chemin_graphique = os.path.join(dossier_projet, "donnees", "distribution_notes.png")
        enregistrer_distribution_notes(df_nettoye, chemin_graphique)
        print("\nGraphique enregistré :", chemin_graphique)

        # Étape 2A — Le même titre ne peut pas apparaître des deux côtés.
        entrainement, test = jeu.separer(proportion_test=0.2, graine=42)
        print("\n", jeu, sep="")
        print("Lignes d'entraînement :", len(entrainement))
        print("Lignes de test :", len(test))
        print("Titres d'entraînement :", entrainement["Name"].str.casefold().nunique())
        print("Titres de test :", test["Name"].str.casefold().nunique())
        print("Graine : 42 ; 20 % des titres réservés au test.")
        # Étape 2B — Référence, apprentissage sur train et évaluation sur test.
        modele = Modele()
        modele.entrainer(entrainement)
        evaluation = modele.evaluer(test)
        print("\nMoyenne de référence :", round(modele.metadonnees["moyenne_reference"], 3))
        print("MAE de référence :", round(evaluation["mae_reference"], 3))
        print("MAE du modèle :", round(evaluation["mae_modele"], 3))
        print("Réduction de MAE (positive si meilleure) :", round(evaluation["gain_mae"], 3))
        print(modele)
        chemin_predictions = os.path.join(dossier_projet, "donnees", "predictions_test.png")
        enregistrer_predictions(test[CIBLE], modele.predire(test), chemin_predictions)

        # Étape 2B — La sauvegarde contient aussi le prétraitement appris.
        dossier_modeles = os.path.join(dossier_projet, "modeles")
        modele.sauvegarder(dossier_modeles)
        recharge = Modele.charger(dossier_modeles)
        exemples = test.head(5)
        if not np.array_equal(modele.predire(exemples), recharge.predire(exemples)):
            raise DonneeInvalideError("Les prédictions changent après rechargement.")
        print("Modèle et métadonnées enregistrés dans :", dossier_modeles)
        print("Rechargement vérifié : mêmes prédictions, sans nouvel entraînement.")
        print("Graphique d'évaluation enregistré :", chemin_predictions)
        print("Lancez maintenant main.py pour ouvrir l’interface sans réentraîner.")
    except (OSError, UnicodeDecodeError, DonneeInvalideError) as erreur:
        print("Impossible de préparer les données :", erreur)


if __name__ == "__main__":
    entrainer()
