"""Étape 3 — Interface Tkinter; la validation et le calcul restent dans les autres modules."""

import tkinter as tk
from tkinter import ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from donnees import VariableCategorielle, VariableNumerique
from exceptions import DonneeInvalideError
from modele import ServicePrediction


class Application:
    """Compose le service de prédiction, les contrôles Tkinter et le graphique."""

    def __init__(self, fenetre: tk.Tk, service: ServicePrediction, metadonnees: dict) -> None:
        """Crée les champs à partir des métadonnées et charge l'historique existant."""
        self._fenetre = fenetre
        self._service = service
        self._metadonnees = metadonnees
        self._champs = {}
        self._resultat_var = tk.StringVar(value="— / 10")
        self._message_var = tk.StringVar(value="Renseignez les caractéristiques, puis cliquez sur Estimer.")
        self._historique_var = tk.StringVar()
        self._ligne_prediction = None
        fenetre.title("Notes des joueurs — Projet INF1007")
        fenetre.geometry("1180x800")
        fenetre.minsize(1000, 700)
        style = ttk.Style(fenetre)
        style.configure("Titre.TLabel", font=("Arial", 20, "bold"))
        style.configure("Note.TLabel", font=("Arial", 32, "bold"), foreground="#175d88")
        style.configure("Message.TLabel", foreground="#234c60")
        style.configure("Erreur.TLabel", foreground="#a32020")
        cadre = ttk.Frame(fenetre, padding=20)
        cadre.pack(fill="both", expand=True)
        ttk.Label(cadre, text="Quelle note donneront les joueurs ?", style="Titre.TLabel").pack(anchor="w")
        ttk.Label(cadre, text="Estimation de la note moyenne des joueurs, à partir des informations du jeu.").pack(anchor="w", pady=(6, 14))
        self._onglets = ttk.Notebook(cadre)
        self._onglets.pack(fill="both", expand=True)
        estimation = ttk.Frame(self._onglets, padding=18)
        historique = ttk.Frame(self._onglets, padding=18)
        self._onglets.add(estimation, text="  Estimer une note  ")
        self._onglets.add(historique, text="  Historique  ")
        self._creer_estimation(estimation)
        self._creer_historique(historique)
        self.reinitialiser()
        self.actualiser_historique()

    def _creer_estimation(self, cadre: ttk.Frame) -> None:
        """Construit les cinq contrôles, le résultat et le graphique intégré."""
        cadre.columnconfigure(0, weight=0, minsize=310)
        cadre.columnconfigure(1, weight=1)
        cadre.rowconfigure(0, weight=1)
        saisie = ttk.Frame(cadre, padding=(0, 0, 22, 0))
        saisie.grid(row=0, column=0, sticky="nsew")
        ttk.Label(saisie, text="Caractéristiques du jeu", font=("Arial", 13, "bold")).pack(anchor="w", pady=(0, 12))
        for variable in self._service.variables:
            ttk.Label(saisie, text=variable.libelle).pack(anchor="w", pady=(9, 3))
            valeur = tk.StringVar()
            self._champs[variable.nom] = valeur
            if isinstance(variable, VariableCategorielle):
                controle = ttk.Combobox(saisie, textvariable=valeur, values=variable.valeurs, state="readonly", width=28)
            else:
                controle = ttk.Entry(saisie, textvariable=valeur, width=30)
            controle.pack(fill="x")
            if isinstance(variable, VariableNumerique):
                precision = "année entière" if variable.entier else "nombre, virgule ou point accepté"
                ttk.Label(saisie, text=f"{variable.minimum:g} à {variable.maximum:g} inclus · {precision}", wraplength=285).pack(anchor="w", pady=(3, 0))
        boutons = ttk.Frame(saisie)
        boutons.pack(fill="x", pady=(22, 14))
        self._bouton_predire = ttk.Button(boutons, text="Estimer la note", command=self.predire)
        self._bouton_predire.pack(side="left")
        ttk.Button(boutons, text="Réinitialiser", command=self.reinitialiser).pack(side="left", padx=8)
        ttk.Label(saisie, text="La note de la presse doit déjà être disponible.\nLes catégories et limites proposées proviennent des jeux d'entraînement (1985 à 2016).", wraplength=285).pack(anchor="w", pady=8)
        affichage = ttk.Frame(cadre)
        affichage.grid(row=0, column=1, sticky="nsew")
        ttk.Label(affichage, text="Note estimée des joueurs", font=("Arial", 12, "bold")).pack(anchor="w")
        ttk.Label(affichage, textvariable=self._resultat_var, style="Note.TLabel").pack(anchor="w", pady=5)
        self._message = ttk.Label(affichage, textvariable=self._message_var, style="Message.TLabel", wraplength=620)
        self._message.pack(anchor="w", fill="x", pady=(0, 10))
        mae = self._metadonnees["evaluation"]["mae_modele"]
        ttk.Label(affichage, text=f"Erreur absolue moyenne sur le test : {mae:.2f} point sur 10.\nCette moyenne ne donne pas l'erreur certaine de ce jeu.", wraplength=620).pack(anchor="w")
        self._figure = Figure(figsize=(6, 3.4), dpi=100, layout="constrained")
        self._axes = self._figure.add_subplot(111)
        distribution = self._metadonnees["distribution_cible_entrainement"]
        bornes = distribution["bornes"]
        largeurs = [droite - gauche for gauche, droite in zip(bornes, bornes[1:])]
        self._axes.bar(bornes[:-1], distribution["effectifs"], width=largeurs, align="edge", color="#3986ad", edgecolor="white", label="Jeux d'entraînement")
        self._axes.set(title="Notes observées pendant l'entraînement", xlabel="Note des joueurs sur 10", ylabel="Nombre de jeux", xlim=(0, 10))
        self._axes.legend(loc="upper left", fontsize=8)
        self._canvas = FigureCanvasTkAgg(self._figure, master=affichage)
        self._canvas.get_tk_widget().pack(fill="both", expand=True, pady=(12, 0))

    def _creer_historique(self, cadre: ttk.Frame) -> None:
        """Crée une table consultable avec défilement et bouton d'actualisation."""
        ttk.Label(cadre, text="Prédictions enregistrées sur cet ordinateur", font=("Arial", 13, "bold")).pack(anchor="w")
        ttk.Label(cadre, text="Chaque estimation valide est conservée dans donnees/historique_predictions.json.").pack(anchor="w", pady=(5, 12))
        zone = ttk.Frame(cadre)
        zone.pack(fill="both", expand=True)
        zone.rowconfigure(0, weight=1)
        zone.columnconfigure(0, weight=1)
        colonnes = ("date", "plateforme", "genre", "annee", "age", "presse", "note")
        self._table_historique = ttk.Treeview(zone, columns=colonnes, show="headings")
        titres = ("Date et heure", "Plateforme", "Genre", "Année", "Classification", "Presse /100", "Estimation /10")
        for nom, titre in zip(colonnes, titres):
            self._table_historique.heading(nom, text=titre)
            self._table_historique.column(nom, width=195 if nom == "date" else 125, minwidth=80)
        self._table_historique.grid(row=0, column=0, sticky="nsew")
        verticale = ttk.Scrollbar(zone, orient="vertical", command=self._table_historique.yview)
        verticale.grid(row=0, column=1, sticky="ns")
        horizontale = ttk.Scrollbar(zone, orient="horizontal", command=self._table_historique.xview)
        horizontale.grid(row=1, column=0, sticky="ew")
        self._table_historique.configure(yscrollcommand=verticale.set, xscrollcommand=horizontale.set)
        ttk.Label(cadre, textvariable=self._historique_var, wraplength=960).pack(anchor="w", pady=10)
        ttk.Button(cadre, text="Actualiser l'historique", command=self.actualiser_historique).pack(anchor="w")

    def _retirer_prediction(self) -> None:
        """Efface le repère précédent afin de ne pas afficher une ancienne estimation."""
        if self._ligne_prediction is not None:
            self._ligne_prediction.remove()
            self._ligne_prediction = None
        self._axes.legend(loc="upper left", fontsize=8)
        self._canvas.draw_idle()

    def predire(self) -> None:
        """Valide et enregistre via le service; affiche une note ou une erreur lisible."""
        self._resultat_var.set("— / 10")
        self._retirer_prediction()
        try:
            note = self._service.predire({nom: valeur.get() for nom, valeur in self._champs.items()})
        except DonneeInvalideError as erreur:
            self._message_var.set(str(erreur))
            self._message.configure(style="Erreur.TLabel")
            return
        except OSError:
            self._message_var.set("Impossible d'enregistrer l'historique. Vérifiez l'accès au dossier donnees, puis réessayez.")
            self._message.configure(style="Erreur.TLabel")
            return
        self._resultat_var.set(f"{note:.2f} / 10")
        self._message_var.set("Estimation enregistrée. Vous pouvez la retrouver dans l'onglet Historique.")
        self._message.configure(style="Message.TLabel")
        self._ligne_prediction = self._axes.axvline(note, color="#b34f20", linewidth=2, label=f"Estimation : {note:.2f}/10")
        self._axes.legend(loc="upper left", fontsize=8)
        self._canvas.draw_idle()
        self.actualiser_historique()

    def reinitialiser(self) -> None:
        """Rétablit des valeurs permises et efface le résultat sans supprimer l'historique."""
        preferences = {"Platform": "PC", "Genre": "Action", "Rating": "T"}
        for variable in self._service.variables:
            if isinstance(variable, VariableCategorielle):
                choix = preferences.get(variable.nom)
                valeur = choix if choix in variable.valeurs else variable.valeurs[0]
            else:
                milieu = (variable.minimum + variable.maximum) / 2
                valeur = str(round(milieu)) if variable.entier else f"{milieu:g}"
            self._champs[variable.nom].set(valeur)
        self._resultat_var.set("— / 10")
        self._message_var.set("Renseignez les caractéristiques, puis cliquez sur Estimer.")
        self._message.configure(style="Message.TLabel")
        self._retirer_prediction()

    def actualiser_historique(self) -> None:
        """Recharge la table; signale un fichier invalide sans l'effacer ni le remplacer."""
        for identifiant in self._table_historique.get_children():
            self._table_historique.delete(identifiant)
        try:
            lignes = self._service.lire_historique()
        except (DonneeInvalideError, OSError) as erreur:
            self._historique_var.set(f"Historique indisponible : {erreur}")
            return
        for ligne in reversed(lignes):
            entrees = ligne["entrees"]
            self._table_historique.insert("", "end", values=(
                ligne["date"].replace("T", " "), entrees["Platform"], entrees["Genre"],
                entrees["Year_of_Release"], entrees["Rating"], entrees["Critic_Score"],
                f"{ligne['prediction']:.2f}",
            ))
        self._historique_var.set(f"{len(lignes)} estimation(s) enregistrée(s). Les plus récentes sont en premier.")
