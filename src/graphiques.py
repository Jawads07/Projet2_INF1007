"""Étape 1 — Figures d’exploration, distinctes de la future interface.py."""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def enregistrer_distribution_notes(
    donnees: pd.DataFrame, chemin: str
) -> None:
    """Enregistre un histogramme des notes des joueurs.

    Paramètres :
        donnees : tableau nettoyé contenant User_Score.
        chemin : emplacement de l'image à créer.

    Retour :
        Aucune valeur.

    Erreurs :
        KeyError si User_Score est absente.
        OSError si l'image ne peut pas être enregistrée.
    """
    fig, ax = plt.subplots()

    ax.hist(
        donnees["User_Score"],
        bins=10,
        range=(0, 10),
        edgecolor="black",
    )

    ax.set_title("Notes des joueurs — jeux conservés après nettoyage")
    ax.set_xlabel("Note des joueurs sur 10")
    ax.set_ylabel("Nombre d’observations (jeu et plateforme)")

    fig.savefig(chemin, dpi=150, bbox_inches="tight")
    plt.close(fig)

def enregistrer_predictions(
    reels: pd.Series, predits: np.ndarray, chemin: str
) -> None:
    """Étape 2B — Enregistre les prédictions contre les notes réelles du test.

    Reçoit deux vecteurs de même longueur et un chemin d'image; ne renvoie rien.
    Propage les erreurs de sauvegarde et ValueError si les tailles diffèrent.
    La diagonale représente une prédiction parfaite, pas un intervalle de confiance.
    """
    fig, ax = plt.subplots()
    ax.scatter(reels, predits, alpha=0.25, s=12, label="Observations de test")
    ax.plot([0, 10], [0, 10], "--", color="black", label="Prédiction parfaite")
    ax.set_title("Arbre de décision — prédictions sur les titres de test")
    ax.set_xlabel("Note réelle des joueurs sur 10")
    ax.set_ylabel("Note prédite sur 10")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.legend()
    fig.savefig(chemin, dpi=150, bbox_inches="tight")
    plt.close(fig)
