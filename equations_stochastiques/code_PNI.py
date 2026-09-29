# %%
#PNI

# %%
import numpy as np
import numpy.random as npr
import matplotlib.pyplot as plt

# %%
def mouvementBrownien(T, h):
    
    #Simule un mouvement brownien sur [0,T] avec un pas h.
    
    n = int(T / h)
    increments = npr.randn(n) * np.sqrt(h)
    B = np.cumsum(increments)
    B = np.hstack(([0], B))
    return B

# %%
def euler_eds(sigma, b, x0, T, N, M=1000, mode="standard", afficher_problemes=True):
    """
    Simule N trajectoires de l'EDS :

        dX_t = b(X_t) dt + sigma(X_t) dB_t

    par un schéma d'Euler-Maruyama.

    Modes :
    - "standard" : schéma d'Euler-Maruyama classique.
    - "positif" : schéma positif adapté au cas sigma(x)=sqrt(x).
    - "cir_reflechi" : réflexion en zéro avec valeur absolue.
    """

    h = T / M
    temps = np.linspace(0, T, M + 1)

    X = np.zeros((N, M + 1))
    X[:, 0] = x0

    for i in range(N):

        for k in range(M):

            x_actuel = X[i, k]

            # Accroissement brownien : Delta B_k ~ N(0,h)
            delta_B = np.sqrt(h) * npr.randn()

            if mode == "standard":

                derive = b(x_actuel)
                diffusion = sigma(x_actuel)

                # Schéma d'Euler-Maruyama classique
                X[i, k + 1] = x_actuel + derive * h + diffusion * delta_B

            elif mode == "positif":

                # Ce mode est utilisé pour le cas sigma(x)=sqrt(x).
                # On veut éviter :
                # - les valeurs négatives,
                # - l'écrasement artificiel en zéro.

                x_utilise = max(x_actuel, 0)

                # Pour sigma(x)=c*sqrt(x), on récupère c avec sigma(1).
                # Dans le cas sigma(x)=sqrt(x), on a c=1.
                c = sigma(1)

                # On utilise un schéma semi-implicite positif :
                #
                # X_{k+1} = X_k + b(X_k)h + c sqrt(X_{k+1}) DeltaB_k
                #
                # On pose Y = sqrt(X_{k+1}), donc X_{k+1}=Y^2.
                # Alors :
                #
                # Y^2 - c DeltaB_k Y - (X_k + b(X_k)h) = 0.
                #
                # On garde la racine positive.

                A = x_utilise + b(x_utilise) * h
                A = max(A, 0)

                Y = (c * delta_B + np.sqrt((c * delta_B) ** 2 + 4 * A)) / 2

                X[i, k + 1] = Y ** 2

            elif mode == "cir_reflechi":

                # Cas CIR réfléchi :
                # on utilise la valeur absolue pour éviter les valeurs négatives.

                x_utilise = abs(x_actuel)

                derive = b(x_utilise)
                diffusion = sigma(x_utilise)

                x_suivant = x_utilise + derive * h + diffusion * delta_B

                X[i, k + 1] = abs(x_suivant)

            else:
                raise ValueError("Mode inconnu. Utiliser 'standard', 'positif' ou 'cir_reflechi'.")

    return temps, X

# %%
def tracer_trajectoires(temps, X, titre="Simulation de trajectoires d'une EDS"):
    """
    Représente graphiquement les trajectoires simulées.
    """
    plt.figure(figsize=(10, 6))

    for i in range(X.shape[0]):
        plt.plot(temps, X[i], linewidth=1)

    plt.xlabel("Temps t")
    plt.ylabel("X_t")
    plt.title(titre)
    plt.grid(True)
    plt.show()

# %%
# TEST 1 : EDS simple


b = lambda x: 1
sigma = lambda x: 0.5

x0 = 0
T = 1
N = 10
M = 1000

temps, X = euler_eds(sigma, b, x0, T, N, M, mode="standard")

print("Nombre de trajectoires simulées :", X.shape[0])

tracer_trajectoires(temps, X, "Test 1 : EDS simple")

# %%
# TEST 2 : sigma(x) = sqrt(x)

b = lambda x: 0.1
sigma = lambda x: np.sqrt(x)

x0 = 1
T = 1
N = 10
M = 1000

temps, X = euler_eds(sigma, b, x0, T, N, M, mode="positif")

print("Test sigma(x)=sqrt(x)")

tracer_trajectoires(temps, X, "Test 2 : sigma(x) = sqrt(x)")

# %%
# TEST 3 : modèle CIR réfléchi

sigma_cir = 0.7
delta = 0.3

b = lambda x: delta
sigma = lambda x: sigma_cir * np.sqrt(abs(x))

x0 = 1
T = 1
N = 10
M = 1000

temps, X = euler_eds(sigma, b, x0, T, N, M, mode="cir_reflechi")

print("Test CIR réfléchi")

tracer_trajectoires(temps, X, "Test 3 : modèle CIR réfléchi")

# %%
import numpy as np
import numpy.random as npr
import matplotlib.pyplot as plt


# ============================================================
# 1. Paramètres
# ============================================================

T = 1          # horizon de temps
M = 1000       # nombre de pas de temps
N = 100        # nombre de trajectoires simulées
x0 = 1         # condition initiale

h = T / M
temps = np.linspace(0, T, M + 1)

# Valeurs de epsilon : plus epsilon est petit, plus le bruit disparaît
epsilons = [1, 0.5, 0.2, 0.1, 0.05, 0.01]


# ============================================================
# 2. Choix de la dérive b et de la diffusion sigma
# ============================================================

def b(x):
    return -x


def sigma(x):
    return 1 / (1 + x**2)


# Constante de Lipschitz approximative pour b(x) = -x
# Ici b est 1-lipschitzienne.
L = 1


# ============================================================
# 3. Solution de l'EDO : dx_t = b(x_t) dt
# ============================================================

x_edo = np.zeros(M + 1)
x_edo[0] = x0

for k in range(M):
    x_edo[k + 1] = x_edo[k] + b(x_edo[k]) * h


# ============================================================
# 4. Simulation de l'EDS avec sigma_epsilon = epsilon * sigma
# ============================================================

erreurs_moyennes = []
bornes_moyennes = []

plt.close("all")
plt.figure(figsize=(10, 6))

# On trace d'abord la solution de l'EDO
plt.plot(temps, x_edo, linewidth=3, label="Solution de l'EDO")

for epsilon in epsilons:

    X = np.zeros((N, M + 1))
    X[:, 0] = x0

    erreurs = []
    bornes = []

    for i in range(N):

        somme_abs_dB = 0

        for k in range(M):

            x_actuel = X[i, k]

            # Accroissement brownien : Delta B_k ~ N(0,h)
            delta_B = npr.randn() * np.sqrt(h)

            # Coefficient de diffusion qui tend uniformément vers 0
            sigma_epsilon = epsilon * sigma(x_actuel)

            # Schéma d'Euler-Maruyama
            X[i, k + 1] = x_actuel + b(x_actuel) * h + sigma_epsilon * delta_B

            somme_abs_dB += abs(delta_B)

        # Erreur uniforme entre la trajectoire EDS et la solution EDO
        erreur = np.max(np.abs(X[i, :] - x_edo))
        erreurs.append(erreur)

        # Borne théorique discrète simplifiée
        # sup |X^epsilon - x| <= exp(LT) * sup|sigma_epsilon| * somme |Delta B|
        # Ici |sigma(x)| <= 1, donc sup|sigma_epsilon| <= epsilon.
        borne = np.exp(L * T) * epsilon * somme_abs_dB
        bornes.append(borne)

    erreur_moyenne = np.mean(erreurs)
    borne_moyenne = np.mean(bornes)

    erreurs_moyennes.append(erreur_moyenne)
    bornes_moyennes.append(borne_moyenne)

    # On trace seulement quelques trajectoires pour ne pas surcharger le graphique
    for j in range(5):
        plt.plot(temps, X[j, :], linewidth=0.8, alpha=0.5)

plt.xlabel("Temps t")
plt.ylabel("Valeur")
plt.title("Convergence de l'EDS vers l'EDO quand sigma tend vers 0")
plt.grid(True)
plt.legend()
plt.show()


# ============================================================
# 5. Quantification de l'erreur et de la borne
# ============================================================

print("epsilon | erreur moyenne sup_t | borne moyenne")
print("-----------------------------------------------")

for epsilon, erreur, borne in zip(epsilons, erreurs_moyennes, bornes_moyennes):
    print(f"{epsilon:7.3f} | {erreur:20.6f} | {borne:13.6f}")


# ============================================================
# 6. Graphique erreur / epsilon
# ============================================================

plt.close("all")

plt.plot(epsilons, erreurs_moyennes, marker="o", label="Erreur moyenne")
plt.plot(epsilons, bornes_moyennes, marker="o", label="Borne moyenne")

plt.xlabel("epsilon")
plt.ylabel("Erreur")
plt.title("Quantification de la convergence vers l'EDO")
plt.grid(True)
plt.legend()
plt.show()

# %%
import numpy as np
import numpy.random as npr
import matplotlib.pyplot as plt


# =====================================================
# Paramètres de l'EDS
# =====================================================

mu = 2.0
sigma_const = 1.0
x0 = 1.0
T = 1.0

# Nombre de trajectoires Monte-Carlo
N = 5000

# Différents nombres de pas
M_values = [10, 20, 40, 80, 160, 320, 640]

h_values = []
erreurs_euler = []
erreurs_milstein = []


# =====================================================
# Fonctions b, sigma et dérivée de sigma
# =====================================================

def b(x):
    return mu * x


def sigma(x):
    return sigma_const * x


def sigma_prime(x):
    return sigma_const


# =====================================================
# Boucle sur les différents pas de temps
# =====================================================

for M in M_values:

    h = T / M
    h_values.append(h)

    erreurs_euler_M = []
    erreurs_milstein_M = []

    for i in range(N):

        # On simule les mêmes accroissements browniens
        # pour Euler et Milstein
        dB = npr.randn(M) * np.sqrt(h)

        # Brownien final
        B_T = np.sum(dB)

        # Solution exacte au temps T
        X_exact = x0 * np.exp((mu - 0.5 * sigma_const**2) * T + sigma_const * B_T)

        # Initialisation des schémas
        X_euler = x0
        X_milstein = x0

        for k in range(M):

            delta_B = dB[k]

            # ============================
            # Schéma d'Euler-Maruyama
            # ============================

            X_euler = X_euler + b(X_euler) * h + sigma(X_euler) * delta_B

            # ============================
            # Schéma de Milstein
            # ============================

            X_milstein = (
                X_milstein
                + b(X_milstein) * h
                + sigma(X_milstein) * delta_B
                + 0.5 * sigma(X_milstein) * sigma_prime(X_milstein) * (delta_B**2 - h)
            )

        # Erreur forte au temps T
        erreurs_euler_M.append(abs(X_exact - X_euler))
        erreurs_milstein_M.append(abs(X_exact - X_milstein))

    # Erreur moyenne sur les N trajectoires
    erreurs_euler.append(np.mean(erreurs_euler_M))
    erreurs_milstein.append(np.mean(erreurs_milstein_M))


# =====================================================
# Estimation des pentes en échelle log-log
# =====================================================

log_h = np.log(h_values)
log_err_euler = np.log(erreurs_euler)
log_err_milstein = np.log(erreurs_milstein)

pente_euler, intercept_euler = np.polyfit(log_h, log_err_euler, 1)
pente_milstein, intercept_milstein = np.polyfit(log_h, log_err_milstein, 1)

print("Pente Euler-Maruyama :", pente_euler)
print("Pente Milstein :", pente_milstein)


# =====================================================
# Graphique en échelle log-log
# =====================================================

plt.close("all")

plt.loglog(h_values, erreurs_euler, "o-", label=f"Euler, pente ≈ {pente_euler:.2f}")
plt.loglog(h_values, erreurs_milstein, "o-", label=f"Milstein, pente ≈ {pente_milstein:.2f}")

plt.xlabel("Pas de temps h")
plt.ylabel("Erreur moyenne E[|X_T - X_T^approx|]")
plt.title("Comparaison de convergence : Euler-Maruyama vs Milstein")
plt.grid(True, which="both")
plt.legend()
plt.show()


