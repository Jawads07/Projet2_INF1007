# Fiche de décisions

| Choix | Options envisagées | Choix retenu et justification | Validation |
|---|---|---|---|
| Domaine | Jeux vidéo, sport, transport | Jeux vidéo : domaine qui nous intéresse et résultat facile à illustrer. | À discuter avec l'auxiliaire. |
| Jeu de données | Différents jeux de données sur les jeux vidéo | Video Games : les cinq entrées choisies et la note des joueurs sont disponibles; le fichier respecte les critères de taille et mélange des variables numériques et catégorielles. La fiche annonce une licence CC0. | À discuter avec l'auxiliaire. |
| Cible | Note des joueurs ou ventes | Note des joueurs : résultat sur 10, facile à comprendre et à évaluer. | À présenter lors de la validation C. |
| Environnement | Python système, Anaconda, environnement virtuel | Anaconda conservé pour utiliser un interpréteur stable avec les bibliothèques nécessaires. | Choix technique. |
| Nettoyage | Supprimer les lignes incomplètes ou remplacer les valeurs manquantes | Suppression choisie pour sa simplicité, sans inventer les notes absentes. Les limites de représentativité seront discutées. | À discuter avec l'auxiliaire. |
| Tests et CI | Vérifications manuelles et tests automatisés | pytest et GitHub Actions utilisés conformément aux consignes. Deux tests passent localement et sur GitHub. | Exigence du projet. |
| Graphique d'exploration | Histogramme ou nuage de points | Histogramme retenu pour examiner la répartition de la cible et repérer les intervalles peu représentés. | À présenter avec les données. |