"""Étape 3 — Point d'entrée de l'application; aucun entraînement à l'ouverture."""

import os
import tkinter as tk
from tkinter import messagebox

from donnees import Historique
from exceptions import DonneeInvalideError
from interface import Application
from modele import Modele, ServicePrediction


def main() -> None:
    """Charge le modèle et lance Tkinter; explique les erreurs de démarrage sans traceback."""
    dossier_projet = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    try:
        fenetre = tk.Tk()
    except tk.TclError:
        print("Impossible d'ouvrir la fenêtre Tkinter. Lancez l'application dans une session graphique.")
        return
    fenetre.withdraw()
    try:
        modele = Modele.charger(os.path.join(dossier_projet, "modeles"))
        historique = Historique(os.path.join(dossier_projet, "donnees", "historique_predictions.json"))
        service = ServicePrediction(modele, historique)
        application = Application(fenetre, service, modele.metadonnees)
    except FileNotFoundError:
        messagebox.showerror("Modèle absent", "Créez d'abord le modèle avec :\npython src/entrainer.py\nPuis relancez l'application.", parent=fenetre)
        fenetre.destroy()
        return
    except DonneeInvalideError as erreur:
        messagebox.showerror("Modèle inutilisable", str(erreur), parent=fenetre)
        fenetre.destroy()
        return
    except OSError:
        messagebox.showerror("Accès impossible", "Vérifiez l'accès aux fichiers du dossier modeles.", parent=fenetre)
        fenetre.destroy()
        return
    fenetre.deiconify()
    fenetre.mainloop()


if __name__ == "__main__":
    main()
