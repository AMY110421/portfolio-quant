# Differential privacy: teaching simulator and distinction experiment

[Français](README.fr.md) · [Original internship report](rapport_stage.pdf)

Python/Tkinter desktop prototype for scalar queries on synthetic or locally loaded numerical data. It illustrates noise, utility and an attack distinguishing two known adjacent datasets. It is **not a production privacy library or a private data-release application**: exact statistics are displayed intentionally for teaching.

## Run

From this folder, Python 3.11+ (local reference: Python 3.12):

```bash
python -m pip install -r requirements.txt
python app.py
# Seeded experiment without a graphical desktop:
python experiment.py
```

The desktop app requires Tkinter and a graphical session. Tk is supplied by the Python distribution or OS, not pip. Keep the Python modules in the same folder. CSV input must be a nonempty, finite, one-dimensional numerical array without a header; data stay local.

## Mathematical convention

**Adjacency means replacing one record while preserving public dataset size n.** Clipping bounds [L,U] and counting threshold are public and fixed before querying. Each record is clipped before computing the scalar statistic.

| Query | Global sensitivity under this convention |
| --- | --- |
| Mean | (U − L) / n |
| Sum | U − L |
| Count above a fixed threshold | 1 |

The attack replaces the first record by one clipping bound, chosen to maximize the change among these two candidate replacements. This creates one adjacent pair; it is not an exhaustive privacy analysis.

Laplace scale is sensitivity / epsilon, with finite epsilon > 0. The textbook Gaussian calibration is restricted to **0 < epsilon < 1, 0 < delta < 1**, using sensitivity × sqrt(2 log(1.25/delta)) / epsilon with a small conservative factor. Manual sigma is a noise experiment and does **not** automatically imply an (epsilon, delta) guarantee. Invalid parameters are rejected; epsilon = 0 never returns the true value as a purported private output.

Reference: [Dwork & Roth, The Algorithmic Foundations of Differential Privacy, Appendix A](https://www.cis.upenn.edu/~aaroth/Papers/privacybook.pdf).

## Distribution diagnostic

The diagnostic classifies outputs using the known likelihoods under D and D', with equal prior probabilities and one observed release. It reports classification accuracy and an approximate 95% Monte Carlo interval. Graphs, attack and diagnostic use the same current parameters, including manual Gaussian sigma.

It **does not certify DP**, scan all adjacent datasets or measurable events, or account for composition. Approximate intervals concern simulation uncertainty only. Repeated releases require privacy accounting absent from this prototype. NumPy's random generator is suitable for these experiments, not a hardened privacy service.

![Seeded Laplace distinction experiment](results/distinction.png)

[Results](results/distinction.csv): synthetic salaries, clipped mean, bounds [0,100000], seed 42, 10,000 simulations per hypothesis, fixed-size replacement. Increasing epsilon makes this selected pair easier to distinguish; this experiment is not a universal theorem.

## Original report

The PDF is the original internship report, retained as historical context. The **current code and this README** define the corrected prototype; the original PDF has not been revised to document all subsequent implementation changes.
