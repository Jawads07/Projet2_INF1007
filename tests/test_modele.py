"""Étape 2B — Contrats indépendants du résultat obtenu sur le vrai CSV."""

import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from sklearn.metrics import mean_absolute_error

from donnees import CARACTERISTIQUES
from exceptions import DonneeInvalideError
from modele import Modele, mae_numpy


@pytest.fixture
def entrainement() -> pd.DataFrame:
    """Renvoie quarante observations fictives réservées à l'entraînement."""
    return pd.DataFrame([{
        "Name": f"Train {i}", "Platform": "PC" if i % 2 else "PS4",
        "Genre": "Action" if i % 3 else "Racing", "Rating": "T",
        "Year_of_Release": 2000 + i % 10, "Critic_Score": 20 + i * 1.5,
        "User_Score": 2 + i * 0.12,
    } for i in range(40)])


@pytest.fixture
def test_independant() -> pd.DataFrame:
    """Renvoie huit observations fictives de titres jamais vus à l'entraînement."""
    return pd.DataFrame([{
        "Name": f"Test {i}", "Platform": "PC", "Genre": "Action", "Rating": "T",
        "Year_of_Release": 2005, "Critic_Score": 25 + i * 5,
        "User_Score": 2.3 + i * 0.4,
    } for i in range(8)])


def test_mae_resultat_manuel_et_sklearn() -> None:
    """Les erreurs 1, 2 et 0 donnent une moyenne de 1; sklearn doit être d'accord."""
    reels = np.array([2.0, 4.0, 7.0])
    predits = np.array([3.0, 2.0, 7.0])
    assert mae_numpy(reels, predits) == pytest.approx(1.0)
    assert mae_numpy(reels, predits) == pytest.approx(mean_absolute_error(reels, predits))


@pytest.mark.parametrize("reels,predits", [
    ([], []), ([1], [1, 2]), ([[1]], [[1]]),
    ([float("nan")], [1]), ([1], [float("inf")]), (["invalide"], [1]),
])
def test_mae_refuse_vecteurs_invalides(reels: list, predits: list) -> None:
    """Un calcul ambigu ou non fini doit produire l'exception métier."""
    with pytest.raises(DonneeInvalideError):
        mae_numpy(reels, predits)


def test_modele_non_entraine(test_independant: pd.DataFrame, tmp_path: Path) -> None:
    """Prédire, évaluer, sauvegarder ou lire les métadonnées exige l'apprentissage."""
    modele = Modele()
    assert "non entraîné" in str(modele)
    with pytest.raises(DonneeInvalideError):
        modele.predire(test_independant)
    with pytest.raises(DonneeInvalideError):
        modele.evaluer(test_independant)
    with pytest.raises(DonneeInvalideError):
        modele.sauvegarder(str(tmp_path))
    with pytest.raises(DonneeInvalideError):
        _ = modele.metadonnees


def test_reference_est_moyenne_du_train(
    entrainement: pd.DataFrame, test_independant: pd.DataFrame
) -> None:
    """Toutes les prédictions de référence valent la moyenne du train, jamais du test."""
    modele = Modele()
    modele.entrainer(entrainement)
    attendu = entrainement["User_Score"].mean()
    assert attendu != pytest.approx(test_independant["User_Score"].mean())
    assert modele.predire_reference(test_independant) == pytest.approx(np.full(8, attendu))
    assert modele.metadonnees["moyenne_reference"] == pytest.approx(attendu)


def test_evaluation_concorde_avec_sklearn(
    entrainement: pd.DataFrame, test_independant: pd.DataFrame
) -> None:
    """Les métriques du rapport correspondent aux prédictions indépendamment recalculées."""
    modele = Modele()
    modele.entrainer(entrainement)
    resultats = modele.evaluer(test_independant)
    attendu = mean_absolute_error(test_independant["User_Score"], modele.predire(test_independant))
    assert resultats["mae_modele"] == pytest.approx(attendu)
    assert resultats["gain_mae"] == pytest.approx(resultats["mae_reference"] - attendu)
    assert resultats["effectif_test"] == len(test_independant)
    assert "MAE test" in str(modele)


def test_refuse_evaluation_sur_train(entrainement: pd.DataFrame) -> None:
    """Le garde-fou sur les titres empêche une évaluation sur l'entraînement."""
    modele = Modele()
    modele.entrainer(entrainement)
    with pytest.raises(DonneeInvalideError, match="titre déjà"):
        modele.evaluer(entrainement)


def test_categorie_inconnue_ne_reentraine_pas(
    entrainement: pd.DataFrame, test_independant: pd.DataFrame
) -> None:
    """Prédire une catégorie jamais vue ne l'ajoute pas aux catégories apprises."""
    modele = Modele()
    avant = entrainement.copy(deep=True)
    modele.entrainer(entrainement)
    variables_avant = modele.metadonnees["variables"]
    test_independant.loc[0, "Platform"] = "Nouvelle plateforme"
    predictions = modele.predire(test_independant)
    assert predictions.shape == (8,)
    assert np.isfinite(predictions).all()
    assert ((predictions >= 0) & (predictions <= 10)).all()
    assert modele.metadonnees["variables"] == variables_avant
    pd.testing.assert_frame_equal(entrainement, avant)


def test_cible_et_nom_exclus_des_entrees(
    entrainement: pd.DataFrame, test_independant: pd.DataFrame
) -> None:
    """Modifier la réponse et le titre ne peut pas changer une prédiction."""
    modele = Modele()
    modele.entrainer(entrainement)
    attendu = modele.predire(test_independant)
    test_independant["Name"] = "Autre nom"
    test_independant["User_Score"] = 0
    np.testing.assert_array_equal(modele.predire(test_independant), attendu)
    assert modele.metadonnees["caracteristiques"] == CARACTERISTIQUES


@pytest.mark.parametrize("champ,valeur", [
    ("Critic_Score", "tbd"), ("Critic_Score", 101),
    ("Year_of_Release", 2005.5), ("Year_of_Release", -1),
    ("Year_of_Release", float("inf")), ("Genre", " "), ("Rating", None),
])
def test_predire_refuse_saisie_invalide(
    entrainement: pd.DataFrame, test_independant: pd.DataFrame, champ: str, valeur: object
) -> None:
    """Les valeurs manquantes, non numériques et hors échelle sont refusées."""
    modele = Modele()
    modele.entrainer(entrainement)
    entree = test_independant.head(1).astype(object)
    entree.loc[entree.index[0], champ] = valeur
    with pytest.raises(DonneeInvalideError):
        modele.predire(entree)


def test_predire_colonne_absente_et_tableau_vide(
    entrainement: pd.DataFrame, test_independant: pd.DataFrame
) -> None:
    """Une entrée incomplète ou un lot vide doit produire une erreur explicite."""
    modele = Modele()
    modele.entrainer(entrainement)
    with pytest.raises(DonneeInvalideError, match="Entrées manquantes"):
        modele.predire(test_independant.drop(columns="Genre"))
    with pytest.raises(DonneeInvalideError, match="au moins une"):
        modele.predire(test_independant.iloc[:0])


def test_entrainement_invalide(entrainement: pd.DataFrame) -> None:
    """Le modèle ne doit pas supprimer silencieusement des cibles invalides."""
    entrainement.loc[0, "User_Score"] = 100
    with pytest.raises(DonneeInvalideError):
        Modele().entrainer(entrainement)


def test_metadonnees_protegees(entrainement: pd.DataFrame, tmp_path: Path) -> None:
    """Les valeurs observées viennent du train et les copies ne modifient pas l'état."""
    modele = Modele()
    modele.entrainer(entrainement)
    assert "évaluation" in str(modele)
    meta = modele.metadonnees
    assert len(meta["variables"]) == 5
    assert meta["effectif_entrainement"] == 40
    assert sum(meta["distribution_cible_entrainement"]["effectifs"]) == 40
    assert sum(meta["importance_variables"].values()) == pytest.approx(1.0)
    presse = next(v for v in meta["variables"] if v["nom"] == "Critic_Score")
    assert presse["maximum"] == pytest.approx(78.5)
    meta["variables"][0]["valeurs"].append("Modification externe")
    assert "Modification externe" not in modele.metadonnees["variables"][0]["valeurs"]
    with pytest.raises(DonneeInvalideError, match="Évaluez"):
        modele.sauvegarder(str(tmp_path))


def test_sauvegarde_recharge_identique(
    entrainement: pd.DataFrame, test_independant: pd.DataFrame, tmp_path: Path
) -> None:
    """JSON lisible et prédictions inchangées après rechargement sans fit."""
    modele = Modele()
    modele.entrainer(entrainement)
    modele.evaluer(test_independant)
    dossier = os.path.join(str(tmp_path), "sauvegarde")
    modele.sauvegarder(dossier)
    recharge = Modele.charger(dossier)
    np.testing.assert_array_equal(modele.predire(test_independant), recharge.predire(test_independant))
    np.testing.assert_array_equal(modele.predire_reference(test_independant), recharge.predire_reference(test_independant))
    assert recharge.metadonnees == modele.metadonnees
    with open(os.path.join(dossier, "metadonnees.json"), encoding="utf-8") as fichier:
        meta = json.load(fichier)
    assert meta["evaluation"]["effectif_test"] == 8


def test_chargement_absent(tmp_path: Path) -> None:
    """Un dossier sans sauvegarde ne peut pas être chargé."""
    with pytest.raises(FileNotFoundError):
        Modele.charger(str(tmp_path))


@pytest.mark.parametrize("modification", ["version", "json", "format", "contenu", "binaire"])
def test_chargement_incoherent_refuse(
    entrainement: pd.DataFrame, test_independant: pd.DataFrame,
    tmp_path: Path, modification: str
) -> None:
    """Une sauvegarde altérée ou d'une autre version ne doit pas être utilisée."""
    modele = Modele()
    modele.entrainer(entrainement)
    modele.evaluer(test_independant)
    modele.sauvegarder(str(tmp_path))
    chemin = os.path.join(str(tmp_path), "metadonnees.json")
    meta = modele.metadonnees
    if modification == "version":
        meta["versions"]["scikit_learn"] = "version différente"
    elif modification == "format":
        meta["format"] = -1
    elif modification == "contenu":
        meta["cible"] = "Autre cible"
    if modification == "binaire":
        with open(os.path.join(str(tmp_path), "modele.joblib"), "wb") as fichier:
            fichier.write(b"")
    with open(chemin, "w", encoding="utf-8") as fichier:
        if modification == "json":
            fichier.write("{invalide")
        else:
            json.dump(meta, fichier)
    with pytest.raises(DonneeInvalideError):
        Modele.charger(str(tmp_path))


def test_reentrainement_remplace_etat(
    entrainement: pd.DataFrame, test_independant: pd.DataFrame, tmp_path: Path
) -> None:
    """Un nouvel apprentissage remplace référence et métriques, sans conserver un ancien score."""
    modele = Modele()
    modele.entrainer(entrainement)
    modele.evaluer(test_independant)
    nouveau = entrainement.copy()
    nouveau["User_Score"] = 5.0
    nouveau["Name"] = [f"Nouveau {i}" for i in range(len(nouveau))]
    modele.entrainer(nouveau)
    assert modele.metadonnees["evaluation"] is None
    assert modele.metadonnees["moyenne_reference"] == pytest.approx(5.0)
    assert modele.predire(test_independant) == pytest.approx(np.full(len(test_independant), 5.0))
    with pytest.raises(DonneeInvalideError, match="Évaluez"):
        modele.sauvegarder(str(tmp_path))
    resultat = modele.evaluer(test_independant)
    assert resultat["mae_modele"] == pytest.approx(resultat["mae_reference"])


def test_parcours_csv_modele_historique_preserve_original(
    entrainement: pd.DataFrame, tmp_path: Path
) -> None:
    """La chaîne complète écrit ses sorties ailleurs et conserve chaque octet du CSV source."""
    from donnees import Historique, JeuDeDonnees
    from modele import ServicePrediction

    csv = tmp_path / "source.csv"
    with open(csv, "w", encoding="utf-8", newline="") as fichier:
        entrainement.to_csv(fichier, index=False)
    original = csv.read_bytes()
    jeu = JeuDeDonnees(str(csv))
    jeu.nettoyer()
    train, test = jeu.separer()
    modele = Modele()
    modele.entrainer(train)
    modele.evaluer(test)
    dossier = str(tmp_path / "modeles")
    modele.sauvegarder(dossier)
    recharge = Modele.charger(dossier)
    exemple = train[CARACTERISTIQUES].head(1)
    saisies = {nom: str(exemple.iloc[0][nom]) for nom in CARACTERISTIQUES}
    service = ServicePrediction(recharge, Historique(str(tmp_path / "historique.json")))
    note = service.predire(saisies)
    assert note == pytest.approx(float(modele.predire(exemple)[0]))
    assert len(service.lire_historique()) == 1
    assert csv.read_bytes() == original
