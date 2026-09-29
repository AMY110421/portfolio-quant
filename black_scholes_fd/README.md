# Valorisation d'un call européen par différences finies

Ce projet résout numériquement l'équation de Black-Scholes par schémas explicite et implicite, puis compare le résultat à la formule analytique. Il porte sur un call européen sans dividendes, avec volatilité et taux constants.

## Lancer

```bash
python -m pip install -r requirements.txt
python pricing.py
```

Le cas d'exemple utilise S0 = K = 100, r = 5 %, volatilité = 20 %, échéance = 1 an. La grille de prix couvre [0, 400]. L'erreur affichée est l'écart absolu au prix analytique.

## Méthode

Le temps numérique τ = T − t augmente de zéro (payoff terminal) à T (prix actuel). Sur la grille des prix S, les dérivées en S sont remplacées par des différences centrées. Le schéma explicite met à jour chaque point avec les valeurs du pas précédent; le schéma implicite résout à chaque pas un système tridiagonal (algorithme de Thomas). La condition à S = 0 est V = 0 et la condition à Smax vaut Smax − K exp(−r τ). Le prix au spot est obtenu par interpolation linéaire.

Le schéma explicite vérifie une borne conservative sur le pas de temps et rejette une grille susceptible d'être instable. L'implicite permet des pas plus grands, avec une erreur temporelle qui dépend encore de la résolution. Le domaine tronqué, l'interpolation et les pas spatiaux causent aussi une erreur numérique.

## Pistes d'amélioration

- Ajouter une étude de convergence selon les pas d'espace et de temps.
- Tracer l'erreur absolue et le temps de calcul des deux schémas.
- Expliquer le choix de la borne supérieure Smax et contrôler son impact.
- Faire une comparaison sur plusieurs spots et volatilités.
