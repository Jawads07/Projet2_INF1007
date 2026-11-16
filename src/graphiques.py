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
    ax.set_ylabel("Nombre de jeux")

    fig.savefig(chemin, dpi=150, bbox_inches="tight")
    plt.close(fig)