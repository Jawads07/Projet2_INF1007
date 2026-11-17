# Journal d'utilisation de l'IA

| Outil | Ce qui a été demandé | Réponse reçue | Vérification faite | Décision |
|---|---|---|---|---|
| ChatGPT | Chercher un sujet simple sur les jeux vidéo | Proposition d'estimer la note des joueurs et aide au choix des entrées et du CSV | Fiche source examinée; lecture du CSV : 16 719 observations et 16 colonnes | Retenu |
| ChatGPT | Comprendre les chemins, modules et environnements Python | Explications et propositions de code de chargement; aide aux erreurs de pandas et d'import | Exécution avec le même interpréteur; une proposition d'import échouait avec Run Python File et a été corrigée | Proposition initiale modifiée après vérification |
| ChatGPT | Préparer le nettoyage et comprendre pandas | Proposition de la fonction de nettoyage et explication de DataFrame, sélection, conversion, dropna et masques booléens | Exécution : 6 826 observations conservées; tests des bornes, valeurs manquantes et préservation de l'original | Retenu; limite de représentativité documentée |
| ChatGPT | Produire le graphique d'exploration | Proposition d'une fonction Matplotlib et explication des intervalles et de savefig | Image exécutée et inspectée : titre, axes et concentration des notes entre 6 et 9 | Retenu |
| ChatGPT | Tester la logique et automatiser la vérification | Proposition des tests pytest, fichiers temporaires, pytest.ini et workflow CI | Deux premiers tests validés localement et en CI; suite actuelle de 34 cas exécutée dans l'environnement de vérification; nouvelle CI à confirmer après push | Retenu |
| ChatGPT | Compléter la préparation de façon lisible | Proposition de code pour JeuDeDonnees, l'exception personnalisée et la séparation par titres | Exécution : 5 454 observations d'entraînement et 1 372 de test; contrôles d'absence de titres communs, reproductibilité et état de la classe | Retenu pour intégration et vérification sur le poste de l'équipe |
| ChatGPT | Clarifier les choix et réduire les fichiers supplémentaires | Réorganisation des documents, retrait du guide de livraison et des fichiers vides; retrait des contraintes minimales de versions insuffisamment justifiées | Inventaire des fichiers, lecture des décisions et relance des tests | Révision retenue; pytest.ini conservé pour une raison technique explicitée |

Les explications complémentaires et références sont regroupées dans le README et
la fiche de décisions. Les résultats du modèle seront ajoutés après son entraînement.
