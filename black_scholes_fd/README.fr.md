# Pricing d'un call européen par différences finies

[English](README.md)

Schémas explicite et implicite, dérivées spatiales centrées, solveur tridiagonal de Thomas et comparaison à Black–Scholes analytique. Hypothèses : taux et volatilité constants, sans dividendes ; spot, strike, volatilité et maturité strictement positifs.

```bash
python -m pip install -r requirements.txt
python pricing.py
python benchmark.py
```

Depuis ce dossier, avec Python 3.11+ ; environnement local vérifié : Python 3.12. Les expériences produisent des figures et CSV sans interface graphique.

Sur le cas S = K = 100, r = 5 %, volatilité = 20 %, T = 1 an, Smax = 400 et une grille commune de 200 × 2 000 pas : prix analytique **10,450584**, explicite **10,441212**, implicite **10,440159**. Le précédent exemple implicite utilisait seulement 200 pas de temps ; il a été remplacé par une comparaison à grille identique.

![Convergence et durées indicatives](results/convergence.png)

Les tableaux couvrent le [raffinement des grilles](results/convergence.csv), le [domaine tronqué](results/domain.csv) et [plusieurs paramètres](results/parameter_cases.csv). Les durées sont indicatives, issues d'une seule exécution. Une étude à coût de calcul identique reste à faire.

Les bornes imposent V(0,τ) = 0 et V(Smax,τ) = Smax − K exp(−rτ). Le prix au spot est interpolé. L'explicite rejette les pas de temps incompatibles avec son contrôle de coefficients ; les deux schémas rejettent les coefficients internes non monotones. Ces restrictions ne permettent pas de couvrir tous les couples taux/volatilité. La troncature du domaine, la grille et l'interpolation contribuent aux erreurs.

Les tests contrôlent le prix analytique, des bornes d'absence d'arbitrage sur l'exemple, le raffinement, les paramètres invalides et les résidus du solveur. Ils ne constituent pas une validation universelle. Voir le README anglais pour le détail.
