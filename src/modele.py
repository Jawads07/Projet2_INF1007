"""Étape 2B — Référence, arbre de régression, évaluation et sauvegarde."""

import copy
import json
import os
import pickle

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeRegressor

from donnees import CARACTERISTIQUES, CIBLE, nettoyer_donnees
from exceptions import DonneeInvalideError

CATEGORIELLES = ["Platform", "Genre", "Rating"]
NUMERIQUES = ["Year_of_Release", "Critic_Score"]


def mae_numpy(reels: np.ndarray, predits: np.ndarray) -> float:
    """Renvoie l'erreur absolue moyenne de deux vecteurs numériques.

    Le calcul est vectorisé, sans boucle Python. Lève DonneeInvalideError si
    les vecteurs sont vides, de formes différentes, non numériques ou non finis.
    """
    try:
        reels = np.asarray(reels, dtype=float)
        predits = np.asarray(predits, dtype=float)
    except (ValueError, TypeError) as erreur:
        raise DonneeInvalideError("La métrique exige des nombres.") from erreur
    if reels.ndim != 1 or predits.ndim != 1 or reels.shape != predits.shape or reels.size == 0:
        raise DonneeInvalideError("La métrique exige deux vecteurs non vides de même taille.")
    if not np.isfinite(reels).all() or not np.isfinite(predits).all():
        raise DonneeInvalideError("La métrique refuse les valeurs manquantes ou infinies.")
    return float(np.mean(np.abs(reels - predits)))


def preparer_entrees(donnees: pd.DataFrame) -> pd.DataFrame:
    """Reçoit les cinq caractéristiques et renvoie une copie typée, dans leur ordre.

    Accepte des catégories nouvelles, que l'encodeur ignorera. Lève
    DonneeInvalideError pour une colonne absente, un tableau vide, un champ vide,
    une année non entière ou non positive et une note de presse hors [0,100].
    Les limites observées d'entraînement sont exposées dans les métadonnées;
    leur contrôle par les champs d'interface sera réalisé à l'étape 3.
    """
    absentes = [nom for nom in CARACTERISTIQUES if nom not in donnees.columns]
    if absentes:
        raise DonneeInvalideError("Entrées manquantes : " + ", ".join(absentes))
    if donnees.empty:
        raise DonneeInvalideError("Il faut au moins une observation à prédire.")
    entrees = donnees[CARACTERISTIQUES].copy()
    for nom in CATEGORIELLES:
        entrees[nom] = entrees[nom].astype("string").str.strip()
        if entrees[nom].isna().any() or entrees[nom].eq("").any():
            raise DonneeInvalideError(f"La catégorie {nom} est vide.")
    for nom in NUMERIQUES:
        entrees[nom] = pd.to_numeric(entrees[nom], errors="coerce")
        if not np.isfinite(entrees[nom].to_numpy(dtype=float)).all():
            raise DonneeInvalideError(f"Le champ {nom} doit être numérique et fini.")
    annees = entrees["Year_of_Release"]
    if ((annees <= 0) | (annees % 1 != 0)).any():
        raise DonneeInvalideError("L'année doit être un entier positif.")
    if not entrees["Critic_Score"].between(0, 100).all():
        raise DonneeInvalideError("La note de presse doit être entre 0 et 100.")
    return entrees


def verifier_observations(donnees: pd.DataFrame) -> pd.DataFrame:
    """Renvoie une copie des observations complètes pour entraînement/évaluation.

    Lève DonneeInvalideError si le schéma est incomplet ou si une ligne devrait
    être retirée par le nettoyage. Ne supprime aucune observation en silence.
    """
    propres = nettoyer_donnees(donnees)
    if propres.empty or len(propres) != len(donnees):
        raise DonneeInvalideError("Les observations doivent être nettoyées et non vides.")
    return propres


class Modele:
    """Contient le prétraitement, l'arbre, la référence et les métadonnées."""

    def __init__(self) -> None:
        """Initialise un modèle non entraîné; ne reçoit aucun paramètre."""
        self._pipeline = None
        self._reference = None
        self._metadonnees = {}
        self._titres_entrainement = set()

    def _verifier_entraine(self) -> None:
        """Ne renvoie rien; lève DonneeInvalideError avant l'entraînement."""
        if self._pipeline is None:
            raise DonneeInvalideError("Le modèle doit d'abord être entraîné ou chargé.")

    @property
    def metadonnees(self) -> dict:
        """Renvoie une copie profonde des métadonnées; exige un modèle entraîné."""
        self._verifier_entraine()
        return copy.deepcopy(self._metadonnees)

    # Étape 2B — Apprendre la référence et l'encodeur uniquement sur train.
    def entrainer(self, entrainement: pd.DataFrame) -> None:
        """Apprend sur les observations d'entraînement et remplace l'état du modèle.

        Ne reçoit pas le test et ne renvoie rien. Lève DonneeInvalideError pour
        des observations incomplètes ou invalides. Réglages fixés avant évaluation :
        profondeur 5, au moins 10 observations par feuille et graine 42.
        """
        propres = verifier_observations(entrainement)
        entrees = preparer_entrees(propres)
        cible = propres[CIBLE].to_numpy(dtype=float)
        reference = DummyRegressor(strategy="mean")
        reference.fit(np.zeros((len(propres), 1)), cible)

        preparation = ColumnTransformer([
            ("categories", OneHotEncoder(handle_unknown="ignore"), CATEGORIELLES),
            ("nombres", "passthrough", NUMERIQUES),
        ])
        pipeline = Pipeline([
            ("preparation", preparation),
            ("arbre", DecisionTreeRegressor(
                max_depth=5, min_samples_leaf=10, random_state=42
            )),
        ])
        pipeline.fit(entrees, cible)
        self._pipeline = pipeline
        self._reference = reference
        self._titres_entrainement = set(propres["Name"].str.casefold())
        self._metadonnees = self._construire_metadonnees(entrees, cible)

    def _construire_metadonnees(self, entrees: pd.DataFrame, cible: np.ndarray) -> dict:
        """Renvoie le dictionnaire JSON issu de l'entraînement; exige un modèle ajusté."""
        variables = []
        for nom in CARACTERISTIQUES:
            if nom in CATEGORIELLES:
                # Chapitre 7 : clé lambda pour trier sans tenir compte de la casse.
                categories = sorted(entrees[nom].unique().tolist(), key=lambda valeur: valeur.casefold())
                variables.append({"nom": nom, "type": "categorielle", "valeurs": categories})
            else:
                variables.append({
                    "nom": nom, "type": "numerique",
                    "minimum": float(entrees[nom].min()),
                    "maximum": float(entrees[nom].max()),
                    "entier": nom == "Year_of_Release",
                })
        effectifs, bornes = np.histogram(cible, bins=10, range=(0, 10))
        return {
            "format": 1,
            "caracteristiques": list(CARACTERISTIQUES), "cible": CIBLE,
            "echelle_cible": [0, 10], "variables": variables,
            "modele": {"type": "DecisionTreeRegressor", "max_depth": 5,
                       "min_samples_leaf": 10, "random_state": 42},
            "separation": {"unite": "titre", "proportion_test_titres": 0.2, "graine": 42},
            "effectif_entrainement": len(entrees),
            "moyenne_reference": float(self._reference.constant_[0, 0]),
            "metrique": "MAE", "evaluation": None,
            "distribution_cible_entrainement": {"effectifs": effectifs.tolist(), "bornes": bornes.tolist()},
            "importance_variables": self._importance_variables(),
            "versions": {"scikit_learn": sklearn.__version__, "pandas": pd.__version__,
                         "numpy": np.__version__, "joblib": joblib.__version__},
        }

    def _importance_variables(self) -> dict[str, float]:
        """Regroupe les importances des colonnes encodées par variable d'origine."""
        importance = self._pipeline.named_steps["arbre"].feature_importances_
        encodeur = self._pipeline.named_steps["preparation"].named_transformers_["categories"]
        resultat = {}
        position = 0
        for nom, categories in zip(CATEGORIELLES, encodeur.categories_):
            nombre = len(categories)
            resultat[nom] = float(importance[position:position + nombre].sum())
            position += nombre
        for nom in NUMERIQUES:
            resultat[nom] = float(importance[position])
            position += 1
        return resultat

    def predire(self, entrees: pd.DataFrame) -> np.ndarray:
        """Renvoie une note par observation, sans apprentissage.

        Exige un modèle entraîné; propage les erreurs de preparer_entrees.
        Les colonnes supplémentaires, dont la cible éventuelle, sont exclues.
        """
        self._verifier_entraine()
        return self._pipeline.predict(preparer_entrees(entrees))

    def predire_reference(self, entrees: pd.DataFrame) -> np.ndarray:
        """Renvoie la moyenne d'entraînement pour chaque entrée; exige un modèle ajusté."""
        self._verifier_entraine()
        entrees = preparer_entrees(entrees)
        return self._reference.predict(np.zeros((len(entrees), 1)))

    def evaluer(self, test: pd.DataFrame) -> dict:
        """Calcule les MAE du modèle et de la référence sur le test sans réentraîner.

        Enregistre les résultats dans les métadonnées et renvoie leur copie.
        Lève DonneeInvalideError si non entraîné, test invalide ou titre déjà vu.
        """
        self._verifier_entraine()
        propres = verifier_observations(test)
        titres_test = set(propres["Name"].str.casefold())
        if self._titres_entrainement.intersection(titres_test):
            raise DonneeInvalideError("Le test contient un titre déjà présent dans l'entraînement.")
        reels = propres[CIBLE].to_numpy(dtype=float)
        mae_modele = mae_numpy(reels, self.predire(propres))
        mae_reference = mae_numpy(reels, self.predire_reference(propres))
        resultat = {
            "mae_modele": mae_modele, "mae_reference": mae_reference,
            "gain_mae": mae_reference - mae_modele, "effectif_test": len(propres),
        }
        self._metadonnees["evaluation"] = resultat
        return resultat.copy()

    # Étape 2B — Sauvegarder le pipeline complet et le descriptif pour l'interface.
    def sauvegarder(self, dossier: str) -> None:
        """Écrit modele.joblib et metadonnees.json; ne renvoie rien.

        Exige un modèle évalué (DonneeInvalideError sinon). Crée le dossier
        si nécessaire; les erreurs de fichiers sont propagées.
        """
        self._verifier_entraine()
        if self._metadonnees["evaluation"] is None:
            raise DonneeInvalideError("Évaluez le modèle avant sa sauvegarde.")
        os.makedirs(dossier, exist_ok=True)
        chemin_modele = os.path.join(dossier, "modele.joblib")
        chemin_json = os.path.join(dossier, "metadonnees.json")
        with open(chemin_modele, "wb") as fichier:
            joblib.dump(self, fichier)
        with open(chemin_json, "w", encoding="utf-8") as fichier:
            json.dump(self._metadonnees, fichier, ensure_ascii=False, indent=2, allow_nan=False)

    @classmethod
    def charger(cls, dossier: str) -> "Modele":
        """Recharge la sauvegarde produite par sauvegarder, sans apprentissage.

        Lève FileNotFoundError si un fichier manque et DonneeInvalideError si
        le format, le contenu ou la version de scikit-learn ne convient pas.
        Charger uniquement une sauvegarde de confiance produite par le projet.
        Les erreurs d'accès sont propagées.
        """
        chemin_modele = os.path.join(dossier, "modele.joblib")
        chemin_json = os.path.join(dossier, "metadonnees.json")
        for chemin in [chemin_json, chemin_modele]:
            if not os.path.isfile(chemin):
                raise FileNotFoundError(f"Sauvegarde introuvable : {chemin}")
        try:
            with open(chemin_json, "r", encoding="utf-8") as fichier:
                metadonnees = json.load(fichier)
        except json.JSONDecodeError as erreur:
            raise DonneeInvalideError("Le JSON des métadonnées est invalide.") from erreur
        if not isinstance(metadonnees, dict) or metadonnees.get("format") != 1:
            raise DonneeInvalideError("Format des métadonnées non reconnu.")
        versions = metadonnees.get("versions", {})
        if not isinstance(versions, dict) or versions.get("scikit_learn") != sklearn.__version__:
            raise DonneeInvalideError("Version scikit-learn différente : relancez main.py pour recréer le modèle.")
        try:
            with open(chemin_modele, "rb") as fichier:
                modele = joblib.load(fichier)
        except (ValueError, EOFError, TypeError, pickle.UnpicklingError) as erreur:
            raise DonneeInvalideError("Le modèle sauvegardé est illisible.") from erreur
        if not isinstance(modele, cls):
            raise DonneeInvalideError("Le fichier ne contient pas un modèle du projet.")
        modele._verifier_entraine()
        if modele.metadonnees != metadonnees:
            raise DonneeInvalideError("Le modèle et les métadonnées ne correspondent pas.")
        return modele

    def __str__(self) -> str:
        """Renvoie un résumé textuel de l'état et de l'évaluation éventuelle."""
        if self._pipeline is None:
            return "Arbre de régression non entraîné"
        evaluation = self._metadonnees["evaluation"]
        if evaluation is None:
            return "Arbre entraîné, évaluation à effectuer"
        return f"Arbre de profondeur maximale 5 : MAE test = {evaluation['mae_modele']:.3f}/10"
