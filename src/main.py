import os

from donnees import charger_donnees, nettoyer_donnees


def main() -> None:
    """Charge, examine et nettoie les données du projet.

    Ne reçoit aucun argument et ne renvoie aucune valeur.
    Affiche un message si le fichier est introuvable.
    Les autres erreurs de lecture sont propagées.
    """
    dossier_src = os.path.dirname(os.path.abspath(__file__))
    dossier_projet = os.path.dirname(dossier_src)
    chemin_csv = os.path.join(dossier_projet, "donnees", "Video_Games.csv")

    try:
        df = charger_donnees(chemin_csv)
    except FileNotFoundError as erreur:
        print(erreur)
        return

    print("Nombre de lignes :", df.shape[0])
    print("Nombre de colonnes :", df.shape[1])

    colonnes = [
        "Platform",
        "Genre",
        "Year_of_Release",
        "Rating",
        "Critic_Score",
        "User_Score",
    ]

    print("\nTypes des colonnes utilisées :")
    print(df[colonnes].dtypes)

    print("\nValeurs manquantes par colonne :")
    print(df[colonnes].isna().sum())

    print("\nNombre de notes joueurs égales à 'tbd' :")
    print((df["User_Score"] == "tbd").sum())

    df_nettoye = nettoyer_donnees(df)

    print("\nLignes avant nettoyage :", len(df))
    print("Lignes après nettoyage :", len(df_nettoye))
    print("Lignes retirées :", len(df) - len(df_nettoye))

    print("\nValeurs manquantes après nettoyage :")
    print(df_nettoye.isna().sum())


if __name__ == "__main__":
    main()