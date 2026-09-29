# Projets de mathématiques appliquées

Ce dépôt réunit deux projets distincts : la valorisation numérique d'une option européenne et un prototype pédagogique de confidentialité différentielle.

## Black-Scholes : différences finies

Le dossier [`black_scholes_fd`](black_scholes_fd/) contient une version exécutable en Python d'un pricer de call européen. Elle compare la solution analytique à deux discrétisations de l'équation de Black-Scholes (explicite et implicite). Voir le README du dossier pour les hypothèses, l'exécution et les limites numériques.

## Confidentialité différentielle

Le dossier [`confidentialite_differentielle`](confidentialite_differentielle/) contient l'interface Tkinter et ses modules Python, récupérés depuis l'archive complète du projet de stage. Son README détaille l'exécution et les limites de l'interprétation des diagnostics numériques.

## État

Le pricer Black-Scholes a été exécuté localement. Les modules du logiciel de confidentialité différentielle s'importent correctement et son diagnostic gaussien a été testé hors interface. L'interface graphique nécessite un écran et n'a pas été ouverte dans cet environnement.
