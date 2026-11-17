# Fiche de décisions

## Étape 0 — Organisation et outils

| Choix | Options envisagées | Choix retenu et justification | Validé par l'auxiliaire (date) |
|---|---|---|---|
| Environnement | Python système, Anaconda ou environnement virtuel | Anaconda conservé sur le poste; le même interpréteur doit servir à installer et exécuter. Un environnement virtuel n'est pas exigé. | Choix technique |
| Dépendances | Noms seuls ou contraintes de version | Noms seuls dans requirements.txt pour les bibliothèques réellement utilisées. Les bornes minimales proposées précédemment n'avaient pas été justifiées par des besoins précis et sont retirées. Les versions effectivement vérifiées restent indiquées dans le README. | Choix technique |
| Tests et CI | Vérifications manuelles ou tests automatiques | pytest pour les cas usuels, limites et erreurs; coverage pour leur portée; GitHub Actions après chaque push, comme demandé. La nouvelle CI doit encore être confirmée. | Exigence du projet |
| Imports des tests | Réglage du chemin de recherche ou imports différents dans les scripts et tests | pytest.ini ajoute src au chemin de recherche. C'est une configuration facultative en général, retenue ici pour conserver Run Python File et des imports simples. Elle n'ajoute aucune bibliothèque. | Choix technique |
| Organisation des fichiers | Créer tous les fichiers vides immédiatement ou les créer au besoin | Créer uniquement les modules utilisés. modele.py et interface.py seront ajoutés lors de leur implémentation. graphiques.py contient l'histogramme et ne remplace pas la future interface. | Choix technique |

## Étape 1 — Domaine et jeu de données

| Choix | Options envisagées | Choix retenu et justification | Validé par l'auxiliaire (date) |
|---|---|---|---|
| Domaine | Jeux vidéo, sport ou transport | Jeux vidéo, par intérêt pour le domaine et facilité d'illustration. | A à confirmer |
| Données | Données de ventes seules ou données avec notes | CSV avec les caractéristiques et notes des joueurs nécessaires; taille compatible et licence CC0 annoncée sur la fiche source. | B à confirmer |
| Cible | Ventes ou note des joueurs | User_Score : résultat numérique sur 10, simple à interpréter. La note de presse est une entrée distincte, supposée déjà disponible. | C à présenter avant entraînement |
| Exploration | Histogramme ou nuage de points | Histogramme de la cible pour voir les intervalles peu représentés. Titre et axes présents; image enregistrée pour la présentation. | À présenter avec les données |

## Étape 2 — Préparation des données (partie A)

| Choix | Options envisagées | Choix retenu et justification | Validé par l'auxiliaire (date) |
|---|---|---|---|
| Colonnes | Toutes les variables ou cinq entrées sélectionnées | Platform, Genre, Year_of_Release, Rating et Critic_Score. User_Score sert de cible et Name sert uniquement à regrouper les titres. Les ventes et autres colonnes ne sont pas nécessaires à ce problème. | À expliquer lors de C |
| Copie du tableau | Modifier l'entrée ou renvoyer un nouveau tableau | copy et propriétés retournant des copies : préserver les données brutes et éviter des modifications indirectes. Le CSV original n'est jamais réécrit. | Choix technique |
| Valeurs non numériques | Garder le texte, inventer une note ou exclure l'observation | to_numeric avec errors="coerce" transforme les textes inutilisables en valeurs manquantes; dropna retire les lignes incomplètes dans les colonnes nécessaires. La cible manquante n'est pas inventée. Limite : biais possible de sélection après suppression. | À expliquer lors de C |
| Titres et catégories | Garder ou retirer les espaces extérieurs | Les retirer et considérer une chaîne vide comme manquante; éviter de créer plusieurs catégories pour un même libellé. | Choix technique |
| Notes et années | Accepter tout nombre ou vérifier le sens des valeurs | between garde la presse dans [0,100] et les joueurs dans [0,10], bornes incluses. Ces échelles proviennent du sens des colonnes, pas d'une recherche d'un meilleur score. L'année doit être finie, entière et positive. | À expliquer lors de C |
| Encodage du CSV | UTF-8 avec ou sans marque initiale | utf-8-sig accepte les deux et évite de conserver une marque initiale dans le premier nom de colonne. | Choix technique |
| Erreurs | Laisser des erreurs techniques ou produire un message métier | DonneeInvalideError pour le CSV vide ou mal formé, les colonnes absentes et une séparation impossible. main intercepte des exceptions précises pour afficher un message. | Exigence d'une exception personnalisée |
| Séparation | Répartir les lignes ou regrouper les titres | train_test_split sur les titres uniques, sans distinction de casse; 20 % des titres pour le test : compromis simple entre apprentissage et évaluation, sans optimisation sur les résultats. Graine 42 choisie arbitrairement et fixée pour reproduire le découpage. Toutes les plateformes d'un titre restent ensemble pour limiter les fuites. La proportion de lignes peut différer de 20 %. | C à présenter |
| Compatibilité des titres | Transmettre le tableau de chaînes pandas ou une liste Python | unique().tolist() conserve les titres uniques dans une liste Python acceptée par train_test_split. Le tableau PyArrow provoquait une TypeError reproduite avec pandas 3.1.1; la correction passe les tests avec et sans ce stockage. | Choix technique vérifié |
| Encodage | Apprendre sur toutes les données ou sur l'entraînement seulement | À ajuster uniquement sur l'entraînement lors de l'étape 2B. Aucun encodage n'est encore réalisé. | C à présenter |
| Classe des données | Fonctions seules ou objet conservant l'état | JeuDeDonnees conserve les états brut et nettoyé; méthodes de nettoyage et séparation, propriétés de lecture et résumé __str__. Les fonctions restent testables séparément. | Exigence de POO, à compléter aux étapes suivantes |

Les dates des validations doivent être renseignées après les échanges effectifs.
La validation technique locale ne constitue pas une validation par l'auxiliaire.

## Étape 2 — Modèle, évaluation et sauvegarde (partie B)

| Choix | Options envisagées | Choix retenu et justification | Validé par l'auxiliaire (date) |
|---|---|---|---|
| Référence | Valeur constante, moyenne ou médiane | Moyenne des notes d'entraînement, via DummyRegressor. Référence simple proposée dans les consignes, calculée sans consulter les notes du test. | C à confirmer |
| Modèle | Régression linéaire ou arbre de décision | Arbre peu profond : seuils interprétables et relations non linéaires. Un seul modèle, sans recherche d'hyperparamètres sur le test. | C à confirmer |
| Réglages | Arbre sans limite ou complexité limitée | Profondeur 5 et au moins 10 observations par feuille, choisis avant évaluation pour limiter complexité et feuilles trop petites. Graine 42 fixée pour la reproductibilité. Ces nombres ne sont pas présentés comme optimaux. | C à confirmer |
| Métrique | MAE, RMSE ou R² | MAE : erreur moyenne en points sur 10, directement interprétable. Calcul vectorisé NumPy vérifié contre sklearn dans un test. | C à confirmer |
| Critère d'entraînement | Critère quadratique ou absolu | Conserver le critère quadratique par défaut de l'arbre; ses feuilles prédisent une moyenne. La métrique de présentation est la MAE, distincte du critère interne. | Choix technique à expliquer |
| Catégories | Codes entiers ou indicateurs binaires | OneHotEncoder sans ordre artificiel entre plateformes; handle_unknown="ignore" pour rester utilisable sur une catégorie nouvelle. L'interface proposera les catégories du JSON. | Choix technique |
| Prétraitement | Préparer toutes les données ou ajuster sur train seulement | Pipeline réunissant ColumnTransformer et arbre. Seul l'entraînement est donné à fit; évaluer et prédire ne réajustent jamais l'encodage. | Choix technique vérifié |
| Variables numériques | Normalisation ou transmission directe | Transmission directe : l'arbre utilise des seuils et ne repose pas sur une distance entre variables. | Choix technique |
| Entrées et cible | Toutes les colonnes ou cinq entrées explicites | Seules les cinq caractéristiques sont données au pipeline; User_Score et Name sont exclus. Un test modifie cible et titre sans changer les prédictions. | Choix technique vérifié |
| Métadonnées | Catégories/intervalles de toutes les données ou de train | Utiliser ceux de l'entraînement seulement; enregistrer aussi métrique, référence, réglages, distribution de cible et importances pour préparer l'interface. | Choix technique |
| Tri des catégories | Ordre d'apparition ou ordre alphabétique | sorted avec clé lambda insensible à la casse : listes lisibles; utilisation pertinente d'un outil du chapitre 7. | Choix technique |
| Sauvegarde | Modèle seul ou prétraitement et modèle ensemble | Un fichier joblib contient le pipeline et la référence; JSON séparé lisible par l'interface. Vérification des prédictions avant/après rechargement. | Exigence du projet |
| Compatibilité des fichiers | Charger toute version ou contrôler la cohérence | Enregistrer les versions et refuser un scikit-learn différent ou un JSON incohérent, avec consigne de régénération. La persistance interversions n'est pas garantie par sklearn. | Choix technique |
| Dépendance joblib | Compter sur une dépendance indirecte ou la déclarer | Déclaration explicite sans contrainte de version arbitraire : le code importe et utilise joblib directement. | Choix technique |
| Graphique d'évaluation | Score seul ou comparaison visuelle | Nuage prédit/réel avec diagonale et légende. Il rend visibles les fortes erreurs sur certaines faibles notes malgré une MAE globale améliorée. | À présenter |

Les valeurs mesurées sont dans le README et le JSON. La comparaison avec la
référence n'est pas une garantie de performance sur les jeux actuels. Aucun
accord de l'auxiliaire n'est déduit des tests ou de la CI.
