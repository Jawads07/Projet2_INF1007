"""Étape 3 — Validation et historique testés sans écran ni lancement de Tkinter."""

from pathlib import Path
import pandas as pd
import pytest
from donnees import CARACTERISTIQUES, Historique, Variable, VariableCategorielle, VariableNumerique, creer_variables
from exceptions import DonneeInvalideError
from modele import Modele, ServicePrediction


@pytest.fixture
def modele() -> Modele:
    """Prépare un modèle fictif, indépendant du CSV et de la sauvegarde livrée."""
    tableau = pd.DataFrame([{
        "Name": f"Jeu {i}", "Platform": "PC" if i % 2 else "PS4",
        "Genre": "Action", "Rating": "T", "Year_of_Release": 2000 + i % 10,
        "Critic_Score": 20 + i * 1.5, "User_Score": 2 + i * 0.12,
    } for i in range(40)])
    resultat = Modele()
    resultat.entrainer(tableau)
    test = tableau.head(3).copy()
    test["Name"] = [f"Test {i}" for i in range(3)]
    resultat.evaluer(test)
    return resultat


@pytest.fixture
def saisies() -> dict[str, str]:
    """Renvoie cinq saisies valides dans les limites du modèle fictif."""
    return {"Platform": "PC", "Genre": "Action", "Year_of_Release": "2005", "Rating": "T", "Critic_Score": "60"}


def test_heritage_et_polymorphisme() -> None:
    """La même méthode valide un nombre ou un choix selon l'objet enfant."""
    with pytest.raises(TypeError):
        Variable("Genre")
    variables = [VariableNumerique("Critic_Score", 0, 100), VariableCategorielle("Genre", ["Action"])]
    assert all(isinstance(v, Variable) for v in variables)
    assert [v.valider(t) for v, t in zip(variables, ["75,5", " Action "])] == [75.5, "Action"]
    assert "presse" in str(variables[0]).lower()


@pytest.mark.parametrize("valeur", ["", " ", "abc", "nan", "inf", "-inf", "-0.1", "100.1"])
def test_nombre_invalide(valeur: str) -> None:
    """Un nombre vide, non fini ou hors intervalle est refusé."""
    with pytest.raises(DonneeInvalideError):
        VariableNumerique("Critic_Score", 0, 100).valider(valeur)


def test_bornes_inclusives_et_annee_entiere() -> None:
    """Les limites sont admises; une année décimale n'est pas arrondie."""
    annee = VariableNumerique("Year_of_Release", 2000, 2010, entier=True)
    assert annee.valider("2000") == 2000
    assert annee.valider("2010.0") == 2010
    with pytest.raises(DonneeInvalideError, match="entière"):
        annee.valider("2005.5")
    presse = VariableNumerique("Critic_Score", 0, 100)
    assert presse.valider("0") == pytest.approx(0)
    assert presse.valider("100") == pytest.approx(100)


@pytest.mark.parametrize("minimum,maximum", [(2, 1), (float("nan"), 1), (0, float("inf"))])
def test_limites_incoherentes(minimum: float, maximum: float) -> None:
    """Des limites numériques incohérentes doivent être signalées."""
    with pytest.raises(DonneeInvalideError):
        VariableNumerique("Critic_Score", minimum, maximum)


def test_categorie_et_copies() -> None:
    """Les listes extérieures ne peuvent pas modifier les catégories internes."""
    choix = ["PC", "PS4"]
    variable = VariableCategorielle("Platform", choix)
    choix.append("Autre")
    variable.valeurs.append("Autre")
    assert variable.valeurs == ["PC", "PS4"]
    for texte in ["", "Autre", "pc"]:
        with pytest.raises(DonneeInvalideError):
            variable.valider(texte)
    with pytest.raises(DonneeInvalideError):
        VariableCategorielle("Platform", [])
    with pytest.raises(DonneeInvalideError):
        VariableCategorielle("", ["PC"])


def test_factory_depuis_metadonnees(modele: Modele) -> None:
    """Ordre, catégories et limites viennent des descriptions sauvegardées."""
    variables = creer_variables(modele.metadonnees)
    assert [v.nom for v in variables] == CARACTERISTIQUES
    assert isinstance(variables[0], VariableCategorielle)
    assert variables[0].valeurs == ["PC", "PS4"]
    assert isinstance(variables[-1], VariableNumerique)
    assert variables[-1].maximum == pytest.approx(78.5)


@pytest.mark.parametrize("erreur", ["absent", "type", "ordre", "borne", "categorie"])
def test_metadonnees_invalides(modele: Modele, erreur: str) -> None:
    """Une description absente, inattendue ou incohérente est refusée."""
    meta = modele.metadonnees
    if erreur == "absent":
        del meta["variables"]
    elif erreur == "type":
        meta["variables"][0]["type"] = "inconnu"
    elif erreur == "ordre":
        meta["variables"].reverse()
    elif erreur == "borne":
        meta["variables"][-1]["minimum"] = 900
    else:
        meta["variables"][0]["valeurs"] = []
    with pytest.raises(DonneeInvalideError):
        creer_variables(meta)


def test_historique_persistant(modele: Modele, saisies: dict, tmp_path: Path) -> None:
    """Une nouvelle instance retrouve deux prédictions, sans précision perdue."""
    chemin = tmp_path / "donnees" / "historique.json"
    historique = Historique(str(chemin))
    assert historique.lire() == []
    assert not chemin.exists()
    service = ServicePrediction(modele, historique)
    note = service.predire(saisies)
    saisies["Critic_Score"] = "40,5"
    service.predire(saisies)
    lignes = Historique(str(chemin)).lire()
    assert len(lignes) == 2
    assert lignes[0]["prediction"] == pytest.approx(note)
    assert lignes[0]["entrees"]["Year_of_Release"] == 2005
    assert lignes[1]["entrees"]["Critic_Score"] == pytest.approx(40.5)
    assert "T" in lignes[0]["date"]
    assert "historique.json" in str(historique)


@pytest.mark.parametrize("contenu", ["{", "{}", "[{}]", '[{"date":"x","entrees":{},"prediction":8}]'])
def test_historique_corrompu_preserve(modele: Modele, saisies: dict, tmp_path: Path, contenu: str) -> None:
    """Un fichier illisible reste intact après une tentative d'ajout."""
    chemin = tmp_path / "historique.json"
    chemin.write_text(contenu, encoding="utf-8")
    service = ServicePrediction(modele, Historique(str(chemin)))
    with pytest.raises(DonneeInvalideError):
        service.predire(saisies)
    assert chemin.read_text(encoding="utf-8") == contenu


@pytest.mark.parametrize("champ,valeur", [
    ("Platform", "Nouvelle"), ("Genre", ""), ("Critic_Score", "abc"),
    ("Critic_Score", "90"), ("Year_of_Release", "1999"),
    ("Year_of_Release", "2005.5"), ("Rating", " "),
])
def test_service_refuse_sans_enregistrer(modele: Modele, saisies: dict, tmp_path: Path, champ: str, valeur: str) -> None:
    """Les limites sont celles du train; une erreur ne crée aucun fichier."""
    chemin = tmp_path / "historique.json"
    saisies[champ] = valeur
    with pytest.raises(DonneeInvalideError):
        ServicePrediction(modele, Historique(str(chemin))).predire(saisies)
    assert not chemin.exists()


def test_service_refuse_champ_absent(modele: Modele, saisies: dict, tmp_path: Path) -> None:
    """Un formulaire incomplet ne parvient pas au modèle."""
    del saisies["Genre"]
    with pytest.raises(DonneeInvalideError):
        ServicePrediction(modele, Historique(str(tmp_path / "h.json"))).predire(saisies)


def test_prediction_apres_recharge_sans_csv_ni_fit(modele: Modele, saisies: dict, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """La sauvegarde suffit, même si fit/read_csv sont rendus inutilisables."""
    modele.sauvegarder(str(tmp_path))
    attendu = float(modele.predire(pd.DataFrame([saisies]))[0])
    def interdit(*args: object, **kwargs: object) -> None:
        raise AssertionError("Ni CSV ni entraînement pendant l'utilisation")
    monkeypatch.setattr(Modele, "entrainer", interdit)
    monkeypatch.setattr(pd, "read_csv", interdit)
    recharge = Modele.charger(str(tmp_path))
    service = ServicePrediction(recharge, Historique(str(tmp_path / "h.json")))
    assert service.predire(saisies) == pytest.approx(attendu)
    assert len(service.lire_historique()) == 1
    copie = service.variables
    copie.clear()
    assert len(service.variables) == 5


def test_acces_historique_refuse_pas_de_faux_succes(modele: Modele, saisies: dict, tmp_path: Path) -> None:
    """Une erreur d'accès doit remonter au contrôleur d'interface."""
    with pytest.raises(OSError):
        ServicePrediction(modele, Historique(str(tmp_path))).predire(saisies)


@pytest.mark.parametrize("note", [-0.1, 10.1, float("nan"), float("inf")])
def test_note_invalide_non_enregistree(saisies: dict, tmp_path: Path, note: float) -> None:
    """Une note hors échelle ou non finie ne doit pas être enregistrée."""
    chemin = tmp_path / "h.json"
    with pytest.raises(DonneeInvalideError):
        Historique(str(chemin)).ajouter({**saisies, "Year_of_Release": 2005, "Critic_Score": 60.0}, note)
    assert not chemin.exists()


def test_historique_entrees_invalides_preserve(modele: Modele, saisies: dict, tmp_path: Path) -> None:
    """Des données impossibles ne doivent pas effacer les prédictions déjà enregistrées."""
    chemin = tmp_path / "h.json"
    service = ServicePrediction(modele, Historique(str(chemin)))
    service.predire(saisies)
    avant = chemin.read_bytes()
    entrees = service.lire_historique()[0]["entrees"]
    for nom, valeur in [("Genre", ""), ("Critic_Score", float("nan")), ("Year_of_Release", 2000.5)]:
        invalide = dict(entrees)
        invalide[nom] = valeur
        with pytest.raises(DonneeInvalideError):
            Historique(str(chemin)).ajouter(invalide, 8.0)
        assert chemin.read_bytes() == avant


def test_historique_encodage_invalide(modele: Modele, saisies: dict, tmp_path: Path) -> None:
    """Un contenu non UTF-8 produit le message métier et reste intact."""
    chemin = tmp_path / "h.json"
    chemin.write_bytes(b'\xff\xfe')
    with pytest.raises(DonneeInvalideError, match="illisible"):
        ServicePrediction(modele, Historique(str(chemin))).predire(saisies)
    assert chemin.read_bytes() == b'\xff\xfe'


@pytest.mark.parametrize("note", [float("nan"), -1.0, 11.0])
def test_resultat_modele_invalide_ne_touche_pas_historique(
    modele: Modele, saisies: dict, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, note: float
) -> None:
    """Une réponse du modèle impossible n'efface ni n'ajoute une estimation enregistrée."""
    chemin = tmp_path / "h.json"
    service = ServicePrediction(modele, Historique(str(chemin)))
    service.predire(saisies)
    original = chemin.read_bytes()
    def resultat_invalide(entrees: pd.DataFrame) -> list[float]:
        return [note]
    monkeypatch.setattr(modele, "predire", resultat_invalide)
    with pytest.raises(DonneeInvalideError, match="note invalide"):
        service.predire(saisies)
    assert chemin.read_bytes() == original
