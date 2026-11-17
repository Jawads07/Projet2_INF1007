"""Étapes 1 et 2 — Chargement, nettoyage et séparation des observations."""

import os

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from exceptions import DonneeInvalideError

CARACTERISTIQUES = [
    "Platform", "Genre", "Year_of_Release", "Rating", "Critic_Score"
]
CIBLE = "User_Score"
COLONNES_REQUISES = ["Name"] + CARACTERISTIQUES + [CIBLE]


# Étape 1 — Lire les données originales.
def charger_donnees(chemin: str) -> pd.DataFrame:
    """Reçoit le chemin d'un CSV et renvoie son tableau sans le modifier.

    Lève FileNotFoundError si le fichier manque, DonneeInvalideError si le
    CSV est vide ou mal formé. Les erreurs d'accès et d'encodage sont propagées.
    """
    if not os.path.isfile(chemin):
        raise FileNotFoundError(f"Fichier introuvable : {chemin}")
    try:
        with open(chemin, "r", encoding="utf-8-sig", newline="") as fichier:
            donnees = pd.read_csv(fichier)
    except (pd.errors.EmptyDataError, pd.errors.ParserError) as erreur:
        raise DonneeInvalideError("Le fichier CSV est vide ou mal formé.") from erreur
    return donnees


def verifier_colonnes(donnees: pd.DataFrame) -> None:
    """Vérifie les colonnes du tableau; ne renvoie rien.

    Lève DonneeInvalideError si une colonne du projet est absente.
    """
    absentes = [nom for nom in COLONNES_REQUISES if nom not in donnees.columns]
    if absentes:
        raise DonneeInvalideError("Colonnes manquantes : " + ", ".join(absentes))


# Étape 2A — Préparer une copie des observations utilisables.
def nettoyer_donnees(donnees: pd.DataFrame) -> pd.DataFrame:
    """Reçoit le tableau brut et renvoie une copie des observations utilisables.

    Conserve le titre, cinq entrées et la cible. Retire les champs vides,
    nombres invalides, années non entières ou non positives et notes hors
    échelle. Lève DonneeInvalideError si le schéma est incomplet. Un résultat
    vide est possible et sera refusé au moment de la séparation.
    """
    verifier_colonnes(donnees)
    resultat = donnees[COLONNES_REQUISES].copy()

    for colonne in ["Name", "Platform", "Genre", "Rating"]:
        resultat[colonne] = resultat[colonne].astype("string").str.strip()
        resultat[colonne] = resultat[colonne].replace("", pd.NA)

    for colonne in ["Year_of_Release", "Critic_Score", CIBLE]:
        resultat[colonne] = pd.to_numeric(resultat[colonne], errors="coerce")

    resultat = resultat.dropna()
    annee = resultat["Year_of_Release"]
    annees_finies = np.isfinite(annee)
    resultat = resultat[annees_finies].copy()
    annee = resultat["Year_of_Release"]
    lignes_valides = (
        (annee > 0)
        & (annee % 1 == 0)
        & resultat["Critic_Score"].between(0, 100)
        & resultat[CIBLE].between(0, 10)
    )
    return resultat[lignes_valides].copy()


def separer_donnees(
    donnees: pd.DataFrame, proportion_test: float = 0.2, graine: int = 42
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Renvoie deux copies : entraînement et test, à partir du tableau nettoyé.

    Répartit les titres uniques avec train_test_split : toutes les plateformes
    d'un titre restent ensemble. proportion_test concerne les titres, donc la
    proportion exacte de lignes peut différer. Lève DonneeInvalideError pour
    une proportion invalide, des données non nettoyées ou moins de deux titres.
    Aucun encodage ni apprentissage n'est réalisé ici.
    """
    verifier_colonnes(donnees)
    if not 0 < proportion_test < 1:
        raise DonneeInvalideError("La proportion de test doit être entre 0 et 1, exclus.")
    if donnees.empty or donnees[COLONNES_REQUISES].isna().any().any():
        raise DonneeInvalideError("Les données doivent être nettoyées et non vides.")
    if len(nettoyer_donnees(donnees)) != len(donnees):
        raise DonneeInvalideError("Des observations invalides restent dans les données.")
    for colonne in ["Year_of_Release", "Critic_Score", CIBLE]:
        if not pd.api.types.is_numeric_dtype(donnees[colonne]):
            raise DonneeInvalideError("Les colonnes numériques doivent être converties.")
    # Ignore la casse et les espaces extérieurs lors du regroupement des titres.
    groupes = donnees["Name"].astype("string").str.strip().str.casefold()
    titres = groupes.unique().tolist()
    if len(titres) < 2:
        raise DonneeInvalideError("Il faut au moins deux titres différents.")
    try:
        titres_train, titres_test = train_test_split(
            titres, test_size=proportion_test, random_state=graine
        )
    except ValueError as erreur:
        raise DonneeInvalideError("La proportion ne permet pas deux ensembles non vides.") from erreur
    entrainement = donnees[groupes.isin(titres_train)].copy()
    test = donnees[groupes.isin(titres_test)].copy()
    return entrainement, test


class JeuDeDonnees:
    """Étape 2A — Garde les données originales et leur préparation en mémoire."""

    def __init__(self, chemin: str) -> None:
        """Charge le CSV; propage les erreurs de charger_donnees."""
        self._chemin = chemin
        self._originales = charger_donnees(chemin)
        self._nettoyees = None

    @property
    def originales(self) -> pd.DataFrame:
        """Renvoie une copie des données brutes, sans modifier l'état."""
        return self._originales.copy()

    @property
    def nettoyees(self) -> pd.DataFrame:
        """Renvoie une copie nettoyée; lève DonneeInvalideError avant nettoyer."""
        if self._nettoyees is None:
            raise DonneeInvalideError("Nettoyez les données avant de les utiliser.")
        return self._nettoyees.copy()

    def nettoyer(self) -> None:
        """Prépare l'état nettoyé; ne renvoie rien et propage les erreurs de schéma."""
        self._nettoyees = nettoyer_donnees(self._originales)

    def separer(
        self, proportion_test: float = 0.2, graine: int = 42
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Renvoie entraînement et test; lève DonneeInvalideError si non préparé."""
        return separer_donnees(self.nettoyees, proportion_test, graine)

    def __str__(self) -> str:
        """Renvoie un résumé lisible de l'état du jeu de données."""
        if self._nettoyees is None:
            return f"{os.path.basename(self._chemin)} : {len(self._originales)} lignes brutes"
        return (
            f"{os.path.basename(self._chemin)} : {len(self._originales)} lignes brutes, "
            f"{len(self._nettoyees)} lignes nettoyées"
        )
