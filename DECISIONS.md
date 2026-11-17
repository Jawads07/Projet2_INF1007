# Fiche de décisions

Les choix sont regroupés par étape; les détails d'exécution, résultats et liens
officiels figurent dans le README. « À confirmer » ne signifie pas approuvé :
l'équipe doit présenter ces choix à l'auxiliaire et ajouter la date réelle.

| Étape / choix | Options envisagées | Décision et justification | Validation auxiliaire / date |
|---|---|---|---|
| 0 — Python | Système, Anaconda, venv | Anaconda déjà utilisé sur le poste; même interpréteur pour installer, tester et exécuter. venv reste facultatif. | Choix technique |
| 0 — Dépendances | Versions imposées ou noms seuls | Bibliothèques importées directement et outils pytest/coverage, sans bornes arbitraires. Versions testées dans le README; nouvelle installation à vérifier. Tkinter vient de la distribution Python. | Choix technique |
| 0 — Imports et CI | Modifier sys.path ou configurer pytest | pytest.ini ajoute src et sélectionne tests : imports simples et Run Python File conservés. Workflow pytest/coverage à chaque push, comme demandé. | CI de cette révision à vérifier |
| 1 — Domaine et CSV | Jeux, sport, transport; ventes ou notes | Jeux vidéo : sujet familier. CSV de 16 719 lignes, 16 colonnes, licence CC0 annoncée, cible disponible, pas de données personnelles dans les colonnes utilisées. | A domaine et B données à confirmer |
| 1 — Exploration | Résumé seul ou histogramme | Histogramme enregistré avec axes : rend visibles les notes faibles rares et la concentration entre 6 et 9. | À présenter avec B |
| 2A — Cible et entrées | Ventes ou User_Score; toutes les colonnes ou cinq | Prédire User_Score /10 avec Platform, Genre, Year_of_Release, Rating, Critic_Score. Presse supposée connue; ventes exclues. Name sert uniquement au regroupement. | C à confirmer |
| 2A — Nettoyage | Modifier l'original, imputer ou exclure | Copie des sept colonnes utiles; espaces retirés, textes numériques convertis avec coerce, dropna sur ces colonnes. Ne pas inventer la cible. Coût : biais de sélection possible après retrait de 9 893 lignes. | Règles à expliquer avec C |
| 2A — Validité | Simple conversion ou contrôles de domaine | Année finie, entière et positive; between inclusif pour presse 0–100 et joueurs 0–10. Refus des infinis. Les colonnes inutilisées ne font pas exclure de lignes. CSV jamais réécrit. | Choix technique |
| 2A — Séparation | Lignes ou titres uniques | 20 % des titres en test, graine 42; casse et espaces ignorés. Évite qu'un même titre multiplateforme soit des deux côtés. Ne regroupe pas une série entière. Titres convertis en liste pour éviter l'erreur d'indexation PyArrow constatée. | C à confirmer |
| 2B — Référence et métrique | Constante, moyenne, médiane; MAE, RMSE, R² | Moyenne du train via DummyRegressor. MAE en points /10, lisible et calculée par NumPy vectorisé; vérifiée contre sklearn. Ce n'est pas une confiance individuelle. | C à confirmer |
| 2B — Modèle et réglages | Régression linéaire ou arbre | Arbre profondeur 5, minimum 10 observations/feuille, graine 42 : relations non linéaires, complexité limitée. Choisis avant lecture du test, sans optimisation sur ce test. Critère quadratique par défaut, distinct de la MAE de présentation. | C à confirmer |
| 2B — Prétraitement | Codes entiers ou indicateurs; normalisation ou non | OneHotEncoder évite un faux ordre des catégories; ignore les inconnues. Numériques directs : l'arbre utilise des seuils. ColumnTransformer/Pipeline ajustés uniquement sur train; titre et cible exclus des entrées. | Choix technique vérifié |
| 2B — Métadonnées | Train ou données complètes | Catégories et intervalles de train seulement; distribution, métriques et versions sauvegardées. Tri alphabétique avec lambda pour les listes. Importances regroupées, sans interprétation causale. | Choix technique |
| 2B — Persistance | Modèle seul ou pipeline complet | joblib contient prétraitement, arbre et référence; JSON lisible séparé. Correspondance et version sklearn contrôlées; paire à régénérer si incompatible. Graphique prédit/réel : montre les grosses erreurs cachées par la moyenne. | Choix technique vérifié |
| 3 — Technologie et maquette | Tkinter ou Streamlit | Tkinter : fenêtre locale, aucune nouvelle bibliothèque pip, objets et callbacks simples à isoler. Maquette PNG imprimable avec formulaire, résultat, graphique et historique. | D technologie et maquette à confirmer |
| 3 — Lancement | Entraîner à chaque ouverture ou recharger | main.py ouvre la fenêtre; entrainer.py reprend la préparation. Ce fichier supplémentaire évite le réapprentissage à chaque usage et rend les deux actions explicites. graphiques.py reste pour les figures enregistrées; interface.py gère la fenêtre. | Choix technique |
| 3 — Saisies et classes | Contrôles dispersés ou objets de variables | Parent abstrait Variable, enfants numérique/catégoriel redéfinissant valider. Catégories, bornes et année entière viennent du JSON. Listes readonly, erreurs dans la fenêtre, virgule admise. Domaine limité au train pour éviter l'extrapolation. | À présenter avec D |
| 3 — Résultat et figure | Confiance inventée ou qualité globale | Note /10, MAE globale explicitée, histogramme du train avec repère de la prédiction. Résultat périmé effacé après erreur. Aucune lecture du CSV dans l'interface. | Choix technique vérifié |
| 3 — Historique | Mémoire, CSV ou JSON | JSON local : conserve date, cinq entrées et note; table consultable après réouverture. with ferme les fichiers. Erreurs de format/accès signalées, fichier invalide préservé. Adapté à peu de saisies, pas aux écritures simultanées. | Choix technique vérifié |
| 3 — Composition et vérification | Tkinter chargé du calcul ou service séparé | Application possède un ServicePrediction, qui possède modèle, historique et variables. Logique testée sans écran; fenêtre vérifiée séparément. Attributs internes, copies et __str__ rendent état et rôles explicites. | Windows et CI à vérifier par l'équipe |

A/B concernent le domaine et les données; C la cible, métrique et modèle avant
entraînement; D la technologie et la maquette avant codage. Ces accords ne sont
pas déclarés obtenus. Les tests locaux ne les remplacent pas. Live Share permet
un travail conjoint avant un commit; les contributions réelles doivent être
représentées dans Git sans reconstituer artificiellement une chronologie.
