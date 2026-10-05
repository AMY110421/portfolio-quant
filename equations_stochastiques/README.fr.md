# Équations différentielles stochastiques

[English](README.md) · [Rapport PDF](rapport.pdf) · [Source LaTeX](rapport.tex)

Projet académique dont le rapport mentionne **Ndeye Amy Diop, Néné Konte et Ndèye Sira Ndiaye**, sous la direction de Clément Foucart. L'attribution collective est conservée. La partie numérique a été corrigée ; les développements théoriques d'origine ne font pas l'objet d'une nouvelle certification complète.

```bash
python -m pip install -r requirements.txt
python code_PNI.py --seed 42 --paths 5000 --output results
```

Depuis ce dossier, avec Python 3.11+ ; testé localement sous Python 3.12. Le script sauvegarde les figures et tableaux sans ouvrir de fenêtres. Les fonctions sont séparées dans `simulation.py` ; aucun calcul n'est déclenché à l'import.

## Comparaison Euler–Milstein

GBM à solution exacte : μ = 2, σ = 1, X0 = 1, T = 1. Toutes les grilles et les deux méthodes partagent le même Brownien fin. L'erreur est la moyenne Monte-Carlo de l'écart absolu terminal : **erreur forte L1**.

Avec 5 000 trajectoires et la graine 42, les pentes empiriques sur les quatre grilles fines valent **0,523 pour Euler et 0,988 pour Milstein**. Les barres d'erreur sont des intervalles Monte-Carlo approximatifs pour les erreurs moyennes, pas pour les pentes. Voir les [résultats détaillés](results/convergence.csv).

![Comparaison des erreurs fortes](results/figure_euler_milstein_loglog.png)

## Corrections et limites

L'ancien schéma positif semi-implicite introduisait une dérive parasite. Il est remplacé par Euler avec troncature complète : état interne signé, coefficients évalués en sa partie positive, sortie égale à cette partie positive. Il conserve un biais à pas fini ; un test contrôle la moyenne sur dX = √X dW.

La correction par valeur absolue est une illustration séparée à dérive constante. Elle ne représente pas le CIR financier avec retour à la moyenne et ne prouve pas la convergence vers une EDS réfléchie.

L'expérience de petit bruit utilise la solution exacte de l'EDO exp(−t), 1 000 trajectoires et 1 000 pas. Le maximum est pris sur la grille ; un biais temporel reste présent. Le rapport et les figures ont été alignés sur ces expériences. La capture d'interface est historique ; l'exécutable Windows n'est pas fourni.
