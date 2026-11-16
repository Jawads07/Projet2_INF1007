import os
from pathlib import Path

import pytest

from src.donnees import charger_donnees


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