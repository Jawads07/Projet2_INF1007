"""Étapes 1 à 3 — Données, variables du formulaire et historique des prédictions."""

import os
import json
import math
from abc import ABC, abstractmethod
from datetime import datetime

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
    # Une liste Python évite de transmettre un tableau de chaînes PyArrow à sklearn.
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


# Étape 3 — Une même méthode valider, deux comportements selon le type de variable.
LIBELLES = {
    "Platform": "Plateforme", "Genre": "Genre", "Year_of_Release": "Année de sortie",
    "Rating": "Classification d'âge", "Critic_Score": "Note de la presse",
}


class Variable(ABC):
    """Classe parente des caractéristiques décrites dans les métadonnées."""

    def __init__(self, nom: str) -> None:
        """Conserve le nom; lève DonneeInvalideError s'il est vide."""
        if not isinstance(nom, str) or not nom.strip():
            raise DonneeInvalideError("Le nom d'une variable doit être renseigné.")
        self._nom = nom

    @property
    def nom(self) -> str:
        """Renvoie le nom de colonne, sans modifier l'état."""
        return self._nom

    @property
    def libelle(self) -> str:
        """Renvoie un libellé lisible pour les messages et les champs."""
        return LIBELLES.get(self._nom, self._nom)

    @abstractmethod
    def valider(self, valeur: str) -> str | int | float:
        """Renvoie la saisie convertie; lève DonneeInvalideError si invalide."""
        raise NotImplementedError

    def __str__(self) -> str:
        """Renvoie le libellé de la caractéristique."""
        return self.libelle


class VariableNumerique(Variable):
    """Valide un nombre dans l'intervalle observé pendant l'entraînement."""

    def __init__(self, nom: str, minimum: float, maximum: float, entier: bool = False) -> None:
        """Conserve les bornes; lève DonneeInvalideError si non finies ou inversées."""
        super().__init__(nom)
        if not math.isfinite(minimum) or not math.isfinite(maximum) or minimum > maximum:
            raise DonneeInvalideError("Les limites numériques du modèle sont invalides.")
        self._minimum = minimum
        self._maximum = maximum
        self._entier = entier

    @property
    def minimum(self) -> float:
        """Renvoie la borne inférieure inclusive."""
        return self._minimum

    @property
    def maximum(self) -> float:
        """Renvoie la borne supérieure inclusive."""
        return self._maximum

    @property
    def entier(self) -> bool:
        """Indique si la saisie doit être entière."""
        return self._entier

    def valider(self, valeur: str) -> int | float:
        """Convertit la saisie; accepte la virgule décimale et refuse vide/NaN/hors limites."""
        if not isinstance(valeur, str) or not valeur.strip():
            raise DonneeInvalideError(f"{self.libelle} : saisissez une valeur.")
        try:
            nombre = float(valeur.strip().replace(",", "."))
        except ValueError as erreur:
            raise DonneeInvalideError(f"{self.libelle} : saisissez un nombre.") from erreur
        if not math.isfinite(nombre):
            raise DonneeInvalideError(f"{self.libelle} : saisissez un nombre fini.")
        if self._entier and not nombre.is_integer():
            raise DonneeInvalideError(f"{self.libelle} : saisissez une année entière.")
        if not self._minimum <= nombre <= self._maximum:
            raise DonneeInvalideError(
                f"{self.libelle} : valeur attendue entre {self._minimum:g} et {self._maximum:g}."
            )
        return int(nombre) if self._entier else nombre


class VariableCategorielle(Variable):
    """Valide un choix parmi les catégories apprises et sauvegardées."""

    def __init__(self, nom: str, valeurs: list[str]) -> None:
        """Copie les choix; lève DonneeInvalideError si aucun choix valide n'est fourni."""
        super().__init__(nom)
        if not valeurs or any(not isinstance(v, str) or not v.strip() for v in valeurs):
            raise DonneeInvalideError("Les catégories du modèle sont invalides.")
        self._valeurs = list(valeurs)

    @property
    def valeurs(self) -> list[str]:
        """Renvoie une copie des catégories possibles."""
        return list(self._valeurs)

    def valider(self, valeur: str) -> str:
        """Renvoie le choix sans espaces; lève DonneeInvalideError si vide ou inconnu."""
        if not isinstance(valeur, str) or not valeur.strip():
            raise DonneeInvalideError(f"{self.libelle} : choisissez une valeur.")
        choix = valeur.strip()
        if choix not in self._valeurs:
            raise DonneeInvalideError(f"{self.libelle} : choisissez une valeur de la liste.")
        return choix


def creer_variables(metadonnees: dict) -> list[Variable]:
    """Construit les cinq variables depuis le JSON sauvegardé.

    Renvoie une liste ordonnée; lève DonneeInvalideError pour un schéma incomplet,
    une variable répétée, un type inattendu ou des limites invalides.
    """
    try:
        descriptions = metadonnees["variables"]
        variables = []
        for description in descriptions:
            nom = description["nom"]
            if description["type"] == "numerique":
                variable = VariableNumerique(
                    nom, float(description["minimum"]), float(description["maximum"]),
                    description.get("entier", False),
                )
            elif description["type"] == "categorielle":
                variable = VariableCategorielle(nom, description["valeurs"])
            else:
                raise DonneeInvalideError("Type de variable non reconnu dans les métadonnées.")
            variables.append(variable)
        if [v.nom for v in variables] != CARACTERISTIQUES:
            raise DonneeInvalideError("Les cinq caractéristiques du modèle sont incohérentes.")
    except (KeyError, TypeError, ValueError) as erreur:
        raise DonneeInvalideError("Les descriptions des caractéristiques sont incomplètes.") from erreur
    return variables


class Historique:
    """Conserve les prédictions en JSON, indépendamment de l'interface graphique."""

    def __init__(self, chemin: str) -> None:
        """Conserve le chemin; le fichier n'est créé qu'à la première prédiction."""
        self._chemin = chemin

    def _verifier_entrees(self, entrees: dict) -> None:
        """Lève DonneeInvalideError si un enregistrement contient des champs invalides."""
        if not isinstance(entrees, dict) or set(entrees) != set(CARACTERISTIQUES):
            raise DonneeInvalideError("Les caractéristiques de l'historique sont invalides.")
        for nom in ["Platform", "Genre", "Rating"]:
            if not isinstance(entrees[nom], str) or not entrees[nom].strip():
                raise DonneeInvalideError("Une catégorie de l'historique est invalide.")
        for nom in ["Year_of_Release", "Critic_Score"]:
            valeur = entrees[nom]
            if isinstance(valeur, bool) or not isinstance(valeur, (int, float)) or not math.isfinite(valeur):
                raise DonneeInvalideError("Un nombre de l'historique est invalide.")
        annee = entrees["Year_of_Release"]
        if annee <= 0 or int(annee) != annee or not 0 <= entrees["Critic_Score"] <= 100:
            raise DonneeInvalideError("Les caractéristiques de l'historique sont hors limites.")

    def lire(self) -> list[dict]:
        """Renvoie les enregistrements, ou une liste vide si le fichier est absent.

        Lève DonneeInvalideError pour un JSON invalide ou un format inattendu;
        propage les erreurs d'accès. Ne modifie jamais le fichier.
        """
        if not os.path.exists(self._chemin):
            return []
        try:
            with open(self._chemin, "r", encoding="utf-8") as fichier:
                enregistrements = json.load(fichier)
        except (json.JSONDecodeError, UnicodeDecodeError) as erreur:
            raise DonneeInvalideError("Le fichier d'historique est illisible; il n'a pas été modifié.") from erreur
        if not isinstance(enregistrements, list):
            raise DonneeInvalideError("Le format de l'historique est invalide.")
        for ligne in enregistrements:
            if not isinstance(ligne, dict) or not isinstance(ligne.get("date"), str):
                raise DonneeInvalideError("Un enregistrement de l'historique est invalide.")
            self._verifier_entrees(ligne.get("entrees"))
            note = ligne.get("prediction")
            if (isinstance(note, bool) or not isinstance(note, (int, float)) or not math.isfinite(note)
                    or not 0 <= note <= 10):
                raise DonneeInvalideError("Un enregistrement de l'historique est invalide.")
        return enregistrements

    def ajouter(self, entrees: dict, prediction: float) -> None:
        """Ajoute une prédiction; ne renvoie rien et préserve un historique illisible.

        Lève DonneeInvalideError pour des entrées ou une note invalides. Les
        erreurs d'accès sont propagées. Le JSON est fermé avant le retour.
        """
        self._verifier_entrees(entrees)
        if (isinstance(prediction, bool) or not isinstance(prediction, (int, float)) or not math.isfinite(prediction)
                or not 0 <= prediction <= 10):
            raise DonneeInvalideError("La prédiction à enregistrer est invalide.")
        lignes = self.lire()
        lignes.append({
            "date": datetime.now().astimezone().isoformat(timespec="seconds"),
            "entrees": dict(entrees), "prediction": float(prediction),
        })
        os.makedirs(os.path.dirname(self._chemin) or ".", exist_ok=True)
        with open(self._chemin, "w", encoding="utf-8") as fichier:
            json.dump(lignes, fichier, ensure_ascii=False, indent=2, allow_nan=False)

    def __str__(self) -> str:
        """Renvoie un libellé du fichier d'historique."""
        return f"Historique : {os.path.basename(self._chemin)}"
