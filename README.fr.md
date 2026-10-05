# Portfolio — finance quantitative et mathématiques appliquées

[English](README.md)

Trois projets Python académiques : pricing numérique, simulation stochastique et confidentialité différentielle. Les résultats publiés sont des expériences reproductibles avec leurs hypothèses et limites.

| Projet | Compétences illustrées | Accès |
| --- | --- | --- |
| **Pricing Black–Scholes** | Différences finies explicites/implicites, algorithme de Thomas, référence analytique, convergence et domaine tronqué | [Code et résultats](black_scholes_fd/) |
| **Équations stochastiques** | Euler–Maruyama/Milstein, GBM exact, Brownien couplé, incertitude Monte-Carlo, diffusion en racine carrée | [Code et rapport PDF](equations_stochastiques/) |
| **Confidentialité différentielle** | Sensibilité, Laplace/Gauss, adjacence par remplacement, attaque de distinction et interface Tkinter | [Application et limites](confidentialite_differentielle/) |

## Résultats reproductibles

Call européen : S = K = 100, r = 5 %, volatilité = 20 %, T = 1 an, Smax = 400. Les deux schémas utilisent **200 pas d'espace et 2 000 pas de temps**.

| Méthode | Prix | Erreur absolue |
| --- | ---: | ---: |
| Analytique | 10,450584 | — |
| Explicite | 10,441212 | 0,009372 |
| Implicite | 10,440159 | 0,010425 |

![Convergence et durée indicative du pricing](black_scholes_fd/results/convergence.png)

Pour la comparaison Euler–Milstein : 5 000 trajectoires, graine 42, mêmes incréments browniens sous-jacents entre méthodes et grilles. Les pentes empiriques sur les quatre grilles fines valent **0,523 et 0,988**. Les barres d'erreur représentent l'incertitude Monte-Carlo des erreurs moyennes, pas un intervalle sur la pente.

## Exécution et validation

Environnement de référence : Python 3.12, NumPy 2.3.5, Matplotlib 3.10.8. Depuis la racine :

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
```

Créer de préférence un environnement virtuel ; les commandes Windows et Linux/macOS figurent dans le [README anglais](README.md). Chaque projet fournit des instructions spécifiques et une version française. Les scripts d'expériences sauvegardent des figures et tableaux sans bureau graphique ; l'application Tkinter nécessite une session graphique.

## Attribution et limites

Le rapport stochastique mentionne Ndeye Amy Diop, Néné Konte et Ndèye Sira Ndiaye : son attribution collective est conservée. Le simulateur de confidentialité provient d'un stage de recherche ; son rapport d'origine est distinct de la version corrigée du prototype.

Le pricing reste limité au call européen sans dividendes. Les corrections numériques en racine carrée gardent un biais de discrétisation. Le logiciel DP affiche les valeurs exactes à des fins pédagogiques, n'effectue pas de comptabilité de composition et ne certifie aucune garantie globale.

[Historique des corrections](CHANGELOG.md)
