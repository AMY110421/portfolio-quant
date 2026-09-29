# Simulateur pédagogique de confidentialité différentielle

Application de bureau Python/Tkinter issue du projet de stage de recherche. Elle affiche des statistiques sur des données synthétiques, applique les mécanismes de Laplace et gaussien et simule une attaque de distinction entre deux bases voisines.

## Rapport de stage

Le [rapport de stage](rapport_stage.pdf) présente les motivations, la définition mathématique, les mécanismes de Laplace et de Gauss, le point de vue de l'attaquant et les limites pratiques du prototype. Il accompagne le code, sans constituer une certification mathématique du comportement de l'application.

## Exécuter

Python 3 avec Tkinter installé est nécessaire, ainsi que NumPy et Matplotlib :

```bash
python -m pip install -r requirements.txt
python app.py
```

Les fichiers `app.py`, `data.py`, `utils.py`, `mechanisms.py` et `verification.py` doivent rester ensemble. Les données d'exemple sont codées dans `data.py`. Un CSV peut être chargé localement depuis l'interface ; aucun CSV personnel n'est inclus dans le dépôt.

## Portée et limites

La démonstration illustre la sensibilité, le bruit et le compromis entre confidentialité et précision. Le « diagnostic numérique » repose sur une estimation empirique et **ne prouve pas** une garantie mathématique de confidentialité différentielle. La calibration des mécanismes dépend de la définition de l'adjacence, des bornes des données, des paramètres et de la composition éventuelle de requêtes. La simulation d'attaque utilise une suppression de ligne, tandis que le calcul de sensibilité de la moyenne est fondé sur une taille `n` fixe : ne pas interpréter les résultats comme une certification générale de la garantie. Le mode de sigma gaussien manuel ne calcule pas automatiquement une garantie associée.
