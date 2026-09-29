# Portfolio — mathématiques appliquées et finance quantitative

Trois projets Python réalisés dans le cadre de ma formation et de mon stage de recherche. Ils illustrent la résolution numérique, la simulation de processus aléatoires et l'analyse de données. Le premier est directement consacré au pricing ; les deux autres présentent des méthodes utiles en modélisation quantitative.

| Projet | Ce qui a été réalisé | Accès direct |
| --- | --- | --- |
| **Pricing Black–Scholes** | Valorisation d'un call européen par schémas aux différences finies explicite et implicite ; comparaison à la formule analytique. | [Code, méthode et exécution](black_scholes_fd/) |
| **Équations différentielles stochastiques** | Simulations de trajectoires et comparaison numérique d'Euler–Maruyama et de Milstein ; étude d'une diffusion en racine carrée. | [Code et rapport LaTeX](equations_stochastiques/) |
| **Confidentialité différentielle** | Prototype Python/Tkinter avec bruit de Laplace et gaussien et simulation d'une attaque de distinction entre bases voisines. | [Code et limites](confidentialite_differentielle/) · [Rapport de stage (PDF)](confidentialite_differentielle/rapport_stage.pdf) |

## Résultat vérifié : pricing d'un call

Pour l'exemple fourni dans le code (`S0 = K = 100`, `r = 5 %`, `σ = 20 %`, `T = 1 an`) :

| Méthode | Prix | Écart absolu à la formule analytique |
| --- | ---: | ---: |
| Black–Scholes analytique | 10,450584 | — |
| Différences finies, explicite | 10,441212 | 0,009372 |
| Différences finies, implicite | 10,435422 | 0,015162 |

Ces valeurs correspondent à **un jeu de paramètres et une grille** ; elles ne constituent pas une étude de convergence. Les hypothèses et limites numériques sont détaillées dans le [README du projet](black_scholes_fd/README.md).

## Reproduire les projets

Chaque dossier possède son propre `requirements.txt` et ses instructions dans son README. Par exemple, depuis la racine du dépôt :

```bash
cd black_scholes_fd
python -m pip install -r requirements.txt
python pricing.py
```

Le projet d'équations stochastiques produit des figures interactives avec des tirages aléatoires. L'application de confidentialité différentielle nécessite un environnement graphique avec Tkinter. Son diagnostic numérique est pédagogique et **ne certifie pas** une garantie mathématique de confidentialité.
