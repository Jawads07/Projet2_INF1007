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
la fiche de décisions. Les résultats du modèle seront ajoutés après son entraînement.

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
