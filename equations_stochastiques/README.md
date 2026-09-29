# Équations différentielles stochastiques

Projet numérique individuel : analyse théorique et simulation de solutions d’équations différentielles stochastiques (EDS). Le rapport en LaTeX (`rapport.tex`) et les figures associées sont fournis avec le code Python original (`code_PNI.py`).

## Contenu

- Simulation du mouvement brownien et de trajectoires par Euler–Maruyama.
- Étude d’une diffusion en racine carrée et d’un modèle CIR réfléchi en zéro.
- Illustration numérique de la convergence vers une EDO lorsque le bruit diminue.
- Comparaison empirique de l’erreur forte d’Euler–Maruyama et de Milstein sur une EDS linéaire à solution exacte.

## Exécution

```bash
python -m pip install -r requirements.txt
python code_PNI.py
```

Le script affiche plusieurs figures interactives et utilise des tirages aléatoires sans graine fixe : les résultats changent d’un lancement à l’autre. Le calcul final de convergence simule 5 000 trajectoires pour chacune de sept grilles ; il peut prendre du temps. Le rapport peut être compilé avec une distribution LaTeX comprenant les paquets indiqués dans son préambule.

Les figures fournies correspondent au travail d’origine. L’interface Windows empaquetée et ses dépendances ne sont pas incluses ici ; ce dépôt privilégie le code source et le rapport. Le code du simulateur graphique peut être ajouté après examen séparé de ses expressions saisies par l’utilisateur.
