import pandas as pd
import os


def charger_donnees(chemin: str) -> pd.DataFrame:
    """Charge un fichier CSV dans un tableau pandas.

    Paramètre :
        chemin : chemin du CSV à lire.

    Retour :
        Le tableau contenant les données originales.

    Erreurs :
        FileNotFoundError si le fichier n'existe pas.
        Les autres erreurs de lecture sont propagées.
    """
    if not os.path.isfile(chemin):
        raise FileNotFoundError(f"Fichier introuvable : {chemin}")

    with open(chemin, "r", encoding="utf-8") as fichier:
        donnees = pd.read_csv(fichier)

    return donnees

def nettoyer_donnees(donnees: pd.DataFrame) -> pd.DataFrame:
    """Prépare les données nécessaires à notre modèle.

    Paramètre :
        donnees : tableau contenant les colonnes du CSV original.

    Retour :
        Un nouveau tableau sans valeurs manquantes ni notes hors limites.

    Erreur :
        KeyError si une colonne nécessaire est absente.
    """
    colonnes = [
        "Name",
        "Platform",
        "Genre",
        "Year_of_Release",
        "Rating",
        "Critic_Score",
        "User_Score",
    ]

    resultat = donnees[colonnes].copy()

    colonnes_numeriques = [
        "Year_of_Release",
        "Critic_Score",
        "User_Score",
    ]

    for colonne in colonnes_numeriques:
        resultat[colonne] = pd.to_numeric(
            resultat[colonne], errors="coerce"
        )

    resultat = resultat.dropna()

    notes_valides = (
        resultat["Critic_Score"].between(0, 100)
        & resultat["User_Score"].between(0, 10)
    )

    resultat = resultat[notes_valides]

    return resultat

