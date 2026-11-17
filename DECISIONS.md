# Fiche de décisions

## Étape 0 — Organisation et outils

| Choix | Options envisagées | Choix retenu et justification | Validé par l'auxiliaire |
|---|---|---|---|
| Environnement | Python système, Anaconda ou environnement virtuel | Anaconda conservé sur le poste; le même interpréteur doit servir à installer et exécuter. Un environnement virtuel n'est pas exigé. | Choix technique |
| Dépendances | Noms seuls ou contraintes de version | Noms seuls dans requirements.txt pour les bibliothèques réellement utilisées. Les bornes minimales proposées précédemment n'avaient pas été justifiées par des besoins précis et sont retirées. Les versions effectivement vérifiées restent indiquées dans le README. | Choix technique |
| Tests et CI | Vérifications manuelles ou tests automatiques | pytest pour les cas usuels, limites et erreurs; coverage pour leur portée; GitHub Actions après chaque push, comme demandé. La nouvelle CI doit encore être confirmée. | Exigence du projet |
| Imports des tests | Réglage du chemin de recherche ou imports différents dans les scripts et tests | pytest.ini ajoute src au chemin de recherche. C'est une configuration facultative en général, retenue ici pour conserver Run Python File et des imports simples. Elle n'ajoute aucune bibliothèque. | Choix technique |
| Organisation des fichiers | Créer tous les fichiers vides immédiatement ou les créer au besoin | Créer uniquement les modules utilisés. modele.py et interface.py seront ajoutés lors de leur implémentation. graphiques.py contient l'histogramme et ne remplace pas la future interface. | Choix technique |

## Étape 1 — Domaine et jeu de données

| Choix | Options envisagées | Choix retenu et justification | Validé par l'auxiliaire |
|---|---|---|---|
| Domaine | Jeux vidéo, sport ou transport | Jeux vidéo, par intérêt pour le domaine et facilité d'illustration. | A à confirmer |
| Données | Données de ventes seules ou données avec notes | CSV avec les caractéristiques et notes des joueurs nécessaires; taille compatible et licence CC0 annoncée sur la fiche source. | B à confirmer |
| Cible | Ventes ou note des joueurs | User_Score : résultat numérique sur 10, simple à interpréter. La note de presse est une entrée distincte, supposée déjà disponible. | C à présenter avant entraînement |
| Exploration | Histogramme ou nuage de points | Histogramme de la cible pour voir les intervalles peu représentés. Titre et axes présents; image enregistrée pour la présentation. | À présenter avec les données |

## Étape 2 — Préparation des données (partie A)

| Choix | Options envisagées | Choix retenu et justification | Validé par l'auxiliaire |
|---|---|---|---|
| Colonnes | Toutes les variables ou cinq entrées sélectionnées | Platform, Genre, Year_of_Release, Rating et Critic_Score. User_Score sert de cible et Name sert uniquement à regrouper les titres. Les ventes et autres colonnes ne sont pas nécessaires à ce problème. | À expliquer lors de C |
| Copie du tableau | Modifier l'entrée ou renvoyer un nouveau tableau | copy et propriétés retournant des copies : préserver les données brutes et éviter des modifications indirectes. Le CSV original n'est jamais réécrit. | Choix technique |
| Valeurs non numériques | Garder le texte, inventer une note ou exclure l'observation | to_numeric avec errors="coerce" transforme les textes inutilisables en valeurs manquantes; dropna retire les lignes incomplètes dans les colonnes nécessaires. La cible manquante n'est pas inventée. Limite : biais possible de sélection après suppression. | À expliquer lors de C |
| Titres et catégories | Garder ou retirer les espaces extérieurs | Les retirer et considérer une chaîne vide comme manquante; éviter de créer plusieurs catégories pour un même libellé. | Choix technique |
| Notes et années | Accepter tout nombre ou vérifier le sens des valeurs | between garde la presse dans [0,100] et les joueurs dans [0,10], bornes incluses. Ces échelles proviennent du sens des colonnes, pas d'une recherche d'un meilleur score. L'année doit être finie, entière et positive. | À expliquer lors de C |
| Encodage du CSV | UTF-8 avec ou sans marque initiale | utf-8-sig accepte les deux et évite de conserver une marque initiale dans le premier nom de colonne. | Choix technique |
| Erreurs | Laisser des erreurs techniques ou produire un message métier | DonneeInvalideError pour le CSV vide ou mal formé, les colonnes absentes et une séparation impossible. main intercepte des exceptions précises pour afficher un message. | Exigence d'une exception personnalisée |
| Séparation | Répartir les lignes ou regrouper les titres | train_test_split sur les titres uniques, sans distinction de casse; 20 % des titres pour le test : compromis simple entre apprentissage et évaluation, sans optimisation sur les résultats. Graine 42 choisie arbitrairement et fixée pour reproduire le découpage. Toutes les plateformes d'un titre restent ensemble pour limiter les fuites. La proportion de lignes peut différer de 20 %. | C à présenter |
| Encodage | Apprendre sur toutes les données ou sur l'entraînement seulement | À ajuster uniquement sur l'entraînement lors de l'étape 2B. Aucun encodage n'est encore réalisé. | C à présenter |
| Classe des données | Fonctions seules ou objet conservant l'état | JeuDeDonnees conserve les états brut et nettoyé; méthodes de nettoyage et séparation, propriétés de lecture et résumé __str__. Les fonctions restent testables séparément. | Exigence de POO, à compléter aux étapes suivantes |

Les dates des validations doivent être renseignées après les échanges effectifs.
La validation technique locale ne constitue pas une validation par l'auxiliaire.
