# Journal d'utilisation de l'IA

| Outil | Ce qui a été demandé | Réponse reçue | Vérification faite | Décision |
|---|---|---|---|---|
| ChatGPT | Chercher un sujet simple sur les jeux vidéo | Proposition d'estimer la note des joueurs et aide au choix des entrées et du CSV | Fiche source examinée; lecture du CSV : 16 719 observations et 16 colonnes | Retenu |
| ChatGPT | Comprendre les chemins, modules et environnements Python | Explications et propositions de code de chargement; aide aux erreurs de pandas et d'import | Exécution avec le même interpréteur; une proposition d'import échouait avec Run Python File et a été corrigée | Proposition initiale modifiée après vérification |
| ChatGPT | Préparer le nettoyage et comprendre pandas | Proposition de la fonction de nettoyage et explication de DataFrame, sélection, conversion, dropna et masques booléens | Exécution : 6 826 observations conservées; tests des bornes, valeurs manquantes et préservation de l'original | Retenu; limite de représentativité documentée |
| ChatGPT | Produire le graphique d'exploration | Proposition d'une fonction Matplotlib et explication des intervalles et de savefig | Image exécutée et inspectée : titre, axes et concentration des notes entre 6 et 9 | Retenu |
| ChatGPT | Tester la logique et automatiser la vérification | Proposition des tests pytest, fichiers temporaires, pytest.ini et workflow CI | Deux premiers tests validés localement et en CI; suite initiale de 34 cas exécutée dans l'environnement de vérification; nouvelle CI à confirmer après push | Retenu |
| ChatGPT | Compléter la préparation de façon lisible | Proposition de code pour JeuDeDonnees, l'exception personnalisée et la séparation par titres | Exécution : 5 454 observations d'entraînement et 1 372 de test; contrôles d'absence de titres communs, reproductibilité et état de la classe | Retenu pour intégration et vérification sur le poste de l'équipe |
| ChatGPT | Clarifier les choix et réduire les fichiers supplémentaires | Réorganisation des documents, retrait du guide de livraison et des fichiers vides; retrait des contraintes minimales de versions insuffisamment justifiées | Inventaire des fichiers, lecture des décisions et relance des tests | Révision retenue; pytest.ini conservé pour une raison technique explicitée |
| ChatGPT | Corriger les trois échecs de séparation sur le poste de l’équipe | Diagnostic d’une incompatibilité PyArrow et conversion des titres uniques en liste Python; ajout d’un cas de test de compatibilité | Erreur reproduite avec pandas 3.1.1 et PyArrow 26.0.1, puis 35 tests réussis après correction. Avec pandas 2.2.3 sans PyArrow : 34 réussis, un cas optionnel ignoré | Proposition initiale corrigée après vérification |

Les explications complémentaires et références sont regroupées dans le README et
la fiche de décisions. Les résultats du modèle et les contrôles de l’interface sont consignés ci-dessous.

## Étape 2B — Modèle et persistance

| Outil | Ce qui a été demandé | Réponse reçue | Vérification faite | Décision |
|---|---|---|---|---|
| ChatGPT | Compléter la référence, le modèle et leur évaluation | Proposition du module Modele, référence par moyenne, pipeline d'encodage et arbre; code de la MAE vectorisée et tests | Tests avec réponse calculée à la main puis comparaison à sklearn; exécution sur le CSV : MAE référence 1,060943 et arbre 0,762572 | Retenu, sans présenter ces réglages comme optimaux |
| ChatGPT | Éviter les fuites et les erreurs de catégories | Proposition de fit sur l'entraînement uniquement, sélection des cinq entrées et catégories inconnues ignorées | Tests : exclusion de la cible, absence de réapprentissage en prédiction, moyenne issue de train et refus d'évaluer des titres déjà vus | Retenu |
| ChatGPT | Sauvegarder pour la future interface | Proposition du code joblib et JSON, métadonnées et rechargement de la classe | Prédictions identiques avant et après rechargement; tests de fichiers absents, JSON invalide, version incompatible et couple de fichiers incohérent | Retenu; exécution locale de l'équipe à confirmer |
| ChatGPT | Vérifier le code complet et clarifier la démarche | Ajout des tests et du graphique prédit/réel, organisation des fichiers et rédaction des explications techniques | 65 cas réussis avec pandas 3.1.1/PyArrow; 64 réussis et un cas optionnel ignoré avec pandas 2.2.3; programme exécuté sous les deux environnements | Retenu pour intégration, nouvelle CI à confirmer après push |

L'aide comprend des propositions de code pour ce module et ses tests, ainsi que
les explications, références et vérifications. L'équipe reste responsable de leur
compréhension et de leur adaptation; les validations A à D ne sont pas supposées
avoir été réalisées.


## Étape 3 — Interface, variables et historique

| Outil | Ce qui a été demandé | Réponse reçue | Vérification faite | Décision |
|---|---|---|---|---|
| ChatGPT | Construire l'interface locale de l'étape 3 | Proposition de maquette et code Tkinter : champs issus des métadonnées, note, graphique intégré et onglet historique | Fenêtre ouverte sous Linux/Tk 9; cinq champs, axes, légende, résultat et deux onglets inspectés à deux tailles | Retenu pour intégration; validation D avec l'auxiliaire et essai Windows à confirmer |
| ChatGPT | Utiliser l'héritage de manière utile | Proposition du parent abstrait Variable, des deux enfants et du service séparé de Tkinter | Tests de valider pour nombres et catégories : vide, texte, bornes inclusives, NaN, année entière et catégories inconnues | Retenu; callbacks et ABC documentés par les références officielles |
| ChatGPT | Conserver les estimations sans modifier le CSV | Proposition de classe Historique, code JSON avec date et table de consultation | Deux prédictions retrouvées après fermeture/réouverture; erreurs de format et d'accès contrôlées | Retenu pour une utilisation locale, sans écriture concurrente |
| ChatGPT | Empêcher un nouvel apprentissage à chaque ouverture | Déplacement de la préparation dans entrainer.py; main.py charge le modèle et ouvre la fenêtre | Ouverture et prédiction exécutées en rendant la lecture CSV et l'entraînement inutilisables; prédiction obtenue depuis la sauvegarde | Retenu; deux commandes distinctes expliquées dans README et DECISIONS |
| ChatGPT | Vérifier le code et compléter les explications | Proposition des tests de l'étape 3, vérification de l'interface et révision des trois documents | 106 tests réussis avec pandas 3.1.1/PyArrow; 105 et un ignoré sans PyArrow. Contrôles graphiques séparés, historique d'essai exclu de l'archive | Retenu pour intégration; CI de cette révision et poste Windows à vérifier |
| ChatGPT | Vérifier qu'un historique invalide reste intact | Relecture de l'enregistrement et ajout d'un contrôle du contenu avant ouverture en écriture | Cas ajouté : catégories vides, année décimale, nombre non fini et contenu non UTF-8 refusés; fichier existant inchangé | Première proposition renforcée après vérification |

L'aide de cette étape comprend des propositions de code et de tests, des
explications, du débogage et une révision des documents. Les essais décrits ont
été effectués dans l'environnement de vérification indiqué au README; ils ne
sont pas présentés comme des essais déjà réalisés sur le poste de l'équipe.
Les validations pédagogiques et la compréhension du code restent à confirmer.


## Étapes 4 et 5 — Consolidation et préparation de la démo

| Outil | Ce qui a été demandé | Réponse reçue | Vérification faite | Décision |
|---|---|---|---|---|
| ChatGPT | Vérifier le projet contre l'énoncé et les notes | Audit du code, des documents et des exigences; ajout de tests sur le parcours complet et l'état après réentraînement | Énoncé relu; lambda, ABC et composition retrouvés dans les chapitres 7 et 11. 111 cas réussis avec PyArrow; 110 + un ignoré sans | Retenu; vérifications finales de l'équipe encore indiquées |
| ChatGPT | Vérifier une installation indépendante | Clonage du dépôt public, installation des dépendances dans un environnement neuf et exécution des commandes documentées | Nettoyage, séparation et MAE reproduits; sauvegarde rechargée et fenêtre exécutée sous Linux. Couverture unitaire 58 % | Retenu; ne constitue pas un essai Windows |
| ChatGPT | Conserver le travail courant de l'équipe | Comparaison du dépôt distant avec l'archive précédente | Modification du paragraphe Live Share et modèle généré avec sklearn 1.9.0 trouvés sur le dépôt; conservés plutôt que remplacés par l'ancienne version | Proposition adaptée à partir du dépôt réel |
| ChatGPT | Vérifier la propreté du dépôt et la CI | Ajout de .gitignore et commande de retrait des caches déjà suivis, sans réécrire l'historique | Trois fichiers .pyc et des réglages locaux repérés dans le dépôt; étape 3, commit 7ad9be4, CI verte. Six commits, un seul auteur déclaré | Retenu; contributions réelles du coéquipier et CI du dernier commit à confirmer |
| ChatGPT | Préparer l'exposé et une solution de secours | Proposition de minutage partagé, cas de démo, questions et PDF de trois captures | Démo normale et invalide exécutée, historique retrouvé; PDF rendu et inspecté. Aucune répétition de l'équipe déclarée | Retenu comme préparation, à répéter et expliquer par les deux membres |

Cette consolidation comprend des propositions de tests et de documentation,
une vérification technique et la préparation du support de secours. Les accords
avec l'auxiliaire, la présentation, la compréhension du code et les contributions
personnelles ne sont pas déduits des résultats automatiques.
