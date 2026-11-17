import os
from pathlib import Path

import pytest

from donnees import JeuDeDonnees, charger_donnees, nettoyer_donnees, separer_donnees
from exceptions import DonneeInvalideError
import pandas as pd


def test_charger_csv_existant(tmp_path: Path) -> None:
    """Vérifie que le chargement conserve les colonnes et les valeurs."""
    chemin = os.path.join(str(tmp_path), "exemple.csv")

    with open(chemin, "w", encoding="utf-8") as fichier:
        fichier.write("Name,User_Score\nJeu test,7.5\n")

    donnees = charger_donnees(chemin)

    assert donnees.shape == (1, 2)
    assert list(donnees.columns) == ["Name", "User_Score"]
    assert donnees["Name"].iloc[0] == "Jeu test"
    assert donnees["User_Score"].iloc[0] == pytest.approx(7.5)


def test_charger_csv_absent(tmp_path: Path) -> None:
    """Vérifie qu'un fichier absent déclenche FileNotFoundError."""
    chemin = os.path.join(str(tmp_path), "absent.csv")

    with pytest.raises(FileNotFoundError):
        charger_donnees(chemin)

# Étape 2A — Cas de nettoyage définis par les règles du projet.
def creer_ligne(**changements: object) -> dict:
    """Renvoie une observation valide fictive, avec les changements demandés."""
    ligne = {
        "Name": "Jeu test", "Platform": "PC", "Genre": "Action",
        "Year_of_Release": "2015", "Rating": "T",
        "Critic_Score": "80", "User_Score": "7.5",
    }
    ligne.update(changements)
    return ligne


def test_charger_csv_vide(tmp_path: Path) -> None:
    """Un fichier sans données doit produire notre exception métier."""
    chemin = os.path.join(str(tmp_path), "vide.csv")
    with open(chemin, "w", encoding="utf-8") as fichier:
        fichier.write("")
    with pytest.raises(DonneeInvalideError, match="vide ou mal formé"):
        charger_donnees(chemin)


def test_nettoyage_conserve_valeurs_et_colonnes() -> None:
    """Une ligne valide garde ses valeurs et exclut les colonnes inutiles."""
    source = pd.DataFrame([creer_ligne(Publisher="Éditeur")])
    resultat = nettoyer_donnees(source)
    assert list(resultat.columns) == [
        "Name", "Platform", "Genre", "Year_of_Release", "Rating", "Critic_Score", "User_Score"
    ]
    assert resultat.iloc[0]["Year_of_Release"] == 2015
    assert resultat.iloc[0]["User_Score"] == pytest.approx(7.5)


@pytest.mark.parametrize("champ,valeur", [
    ("User_Score", "tbd"), ("Critic_Score", None), ("Rating", "  "),
    ("Name", ""), ("Year_of_Release", "N/A"),
    ("Year_of_Release", "2015.5"), ("Year_of_Release", float("inf")),
])
def test_nettoyage_retire_ligne_inutilisable(champ: str, valeur: object) -> None:
    """Chaque observation incomplète ou année invalide est retirée."""
    source = pd.DataFrame([creer_ligne(), creer_ligne(**{champ: valeur})])
    assert len(nettoyer_donnees(source)) == 1


@pytest.mark.parametrize("presse,joueurs", [(0, 0), (100, 10)])
def test_nettoyage_accepte_bornes(presse: float, joueurs: float) -> None:
    """Les extrémités des deux échelles sont autorisées."""
    source = pd.DataFrame([creer_ligne(Critic_Score=presse, User_Score=joueurs)])
    assert len(nettoyer_donnees(source)) == 1


@pytest.mark.parametrize("champ,valeur", [
    ("Critic_Score", -1), ("Critic_Score", 101),
    ("User_Score", -0.1), ("User_Score", 10.1),
])
def test_nettoyage_refuse_notes_hors_echelle(champ: str, valeur: float) -> None:
    """Une note hors de son échelle exclut la ligne."""
    source = pd.DataFrame([creer_ligne(**{champ: valeur})])
    assert nettoyer_donnees(source).empty


def test_nettoyage_preserve_original() -> None:
    """Nettoyer puis modifier le résultat ne doit pas modifier l'entrée."""
    source = pd.DataFrame([creer_ligne()])
    avant = source.copy(deep=True)
    resultat = nettoyer_donnees(source)
    resultat.loc[0, "Name"] = "Autre titre"
    pd.testing.assert_frame_equal(source, avant)


def test_colonne_obligatoire_absente() -> None:
    """Un schéma incomplet produit un message mentionnant la colonne manquante."""
    source = pd.DataFrame([creer_ligne()]).drop(columns="Rating")
    with pytest.raises(DonneeInvalideError, match="Rating"):
        nettoyer_donnees(source)


def creer_jeu_multiplateforme() -> pd.DataFrame:
    """Renvoie dix titres dont un possède plusieurs variantes de casse et plateforme."""
    lignes = [creer_ligne(Name=f"Jeu {i}") for i in range(10)]
    lignes += [creer_ligne(Name=" jeu 0 ", Platform="PS4"), creer_ligne(Name="JEU 0", Platform="Wii")]
    return nettoyer_donnees(pd.DataFrame(lignes))


@pytest.mark.parametrize("stockage", ["python", "pyarrow"])
def test_separation_complete_sans_fuite_de_titres(stockage: str) -> None:
    """Chaque observation est affectée une fois, et aucun titre ne traverse la séparation."""
    if stockage == "pyarrow":
        pytest.importorskip("pyarrow", reason="Stockage optionnel des chaînes pandas")
    with pd.option_context("mode.string_storage", stockage):
        source = creer_jeu_multiplateforme()
        avant = source.copy(deep=True)
        entrainement, test = separer_donnees(source)
    noms_train = set(entrainement["Name"].str.casefold())
    noms_test = set(test["Name"].str.casefold())
    assert noms_train.isdisjoint(noms_test)
    assert len(noms_test) == 2
    assert len(entrainement) + len(test) == len(source)
    assert set(entrainement.index).isdisjoint(test.index)
    assert set(entrainement.index) | set(test.index) == set(source.index)
    pd.testing.assert_frame_equal(source, avant)


def test_separation_reproductible() -> None:
    """Deux appels avec la même graine donnent exactement les mêmes tableaux."""
    source = creer_jeu_multiplateforme()
    train_a, test_a = separer_donnees(source, graine=42)
    train_b, test_b = separer_donnees(source, graine=42)
    pd.testing.assert_frame_equal(train_a, train_b)
    pd.testing.assert_frame_equal(test_a, test_b)


@pytest.mark.parametrize("proportion", [0, 1, -0.1, 1.1])
def test_proportion_test_invalide(proportion: float) -> None:
    """La proportion doit permettre de réserver une partie des titres au test."""
    with pytest.raises(DonneeInvalideError, match="proportion"):
        separer_donnees(creer_jeu_multiplateforme(), proportion_test=proportion)


def test_separation_titre_unique_refusee() -> None:
    """Plusieurs plateformes d'un seul titre ne permettent pas un test indépendant."""
    source = nettoyer_donnees(pd.DataFrame([creer_ligne(), creer_ligne()]))
    with pytest.raises(DonneeInvalideError, match="deux titres"):
        separer_donnees(source)


def test_etat_jeu_de_donnees_et_copies(tmp_path: Path) -> None:
    """La classe protège ses données et exige le nettoyage avant séparation."""
    chemin = os.path.join(str(tmp_path), "jeux.csv")
    with open(chemin, "w", encoding="utf-8", newline="") as fichier:
        creer_jeu_multiplateforme().to_csv(fichier, index=False)
    jeu = JeuDeDonnees(chemin)
    assert "lignes brutes" in str(jeu)
    with pytest.raises(DonneeInvalideError, match="Nettoyez"):
        jeu.separer()
    copie = jeu.originales
    copie.loc[0, "Name"] = "Titre modifié"
    assert jeu.originales.loc[0, "Name"] != "Titre modifié"
    jeu.nettoyer()
    assert "lignes nettoyées" in str(jeu)
    copie_propre = jeu.nettoyees
    copie_propre.loc[0, "Name"] = "Titre modifié"
    assert jeu.nettoyees.loc[0, "Name"] != "Titre modifié"
    train, test = jeu.separer()
    assert len(train) + len(test) == len(jeu.nettoyees)


def test_csv_mal_forme(tmp_path: Path) -> None:
    """Une citation CSV non fermée produit un message métier plutôt qu'une erreur pandas."""
    chemin = os.path.join(str(tmp_path), "mal_forme.csv")
    with open(chemin, "w", encoding="utf-8") as fichier:
        fichier.write('Name,User_Score\n"titre sans fin,7.5\n')
    with pytest.raises(DonneeInvalideError, match="mal formé"):
        charger_donnees(chemin)


def test_separation_ensemble_vide_refuse() -> None:
    """Un tableau nettoyé sans observations ne peut pas servir à l'apprentissage."""
    source = nettoyer_donnees(pd.DataFrame([creer_ligne(User_Score="tbd")]))
    with pytest.raises(DonneeInvalideError, match="non vides"):
        separer_donnees(source)


def test_separation_refuse_valeur_manquante() -> None:
    """La séparation exige un tableau entièrement exploitable."""
    source = creer_jeu_multiplateforme()
    source.loc[0, "Rating"] = pd.NA
    with pytest.raises(DonneeInvalideError, match="nettoyées"):
        separer_donnees(source)


def test_separation_refuse_notes_invalides() -> None:
    """Une note hors échelle ne doit pas atteindre les ensembles d'apprentissage."""
    source = creer_jeu_multiplateforme()
    source.loc[0, "User_Score"] = 15.0
    with pytest.raises(DonneeInvalideError, match="invalides"):
        separer_donnees(source)


def test_separation_refuse_nombres_non_convertis() -> None:
    """Un tableau brut même convertible doit être nettoyé avant séparation."""
    source = pd.DataFrame([creer_ligne(Name="A"), creer_ligne(Name="B")])
    with pytest.raises(DonneeInvalideError, match="converties"):
        separer_donnees(source)


def test_separation_proportion_incompatible_avec_effectif() -> None:
    """Une proportion valide mais impossible avec deux titres produit une erreur claire."""
    source = nettoyer_donnees(pd.DataFrame([creer_ligne(Name="A"), creer_ligne(Name="B")]))
    with pytest.raises(DonneeInvalideError, match="non vides"):
        separer_donnees(source, proportion_test=0.99)


def test_nettoyage_supprime_espaces_exterieurs() -> None:
    """Les catégories et titres ne sont pas dédoublés par de simples espaces extérieurs."""
    resultat = nettoyer_donnees(pd.DataFrame([creer_ligne(Name=" A ", Platform=" PC ")]))
    assert resultat.iloc[0]["Name"] == "A"
    assert resultat.iloc[0]["Platform"] == "PC"
