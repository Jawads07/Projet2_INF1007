"""Point d'entrée — Étapes 1 et 2A, exécutable avec Run Python File."""

import os

from donnees import CARACTERISTIQUES, CIBLE, JeuDeDonnees
from exceptions import DonneeInvalideError
from graphiques import enregistrer_distribution_notes


def main() -> None:
    """Charge, explore, nettoie et sépare les données; ne renvoie rien.

    Affiche les erreurs attendues de fichier, d'encodage et de données.
    Aucun modèle n'est entraîné dans ce lot.
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
        print("Étape suivante : référence, encodage, entraînement et évaluation (lot 2B).")
    except (OSError, UnicodeDecodeError, DonneeInvalideError) as erreur:
        print("Impossible de préparer les données :", erreur)


if __name__ == "__main__":
    main()
