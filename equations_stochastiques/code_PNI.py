"""Reproducible experiments. Example: python code_PNI.py --seed 42 --paths 5000."""
import argparse
import csv
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from simulation import brownian, euler_eds, gbm_convergence


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--paths", type=int, default=5000)
    parser.add_argument("--output", type=Path, default=Path("results"))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed)
    def save(name):
        plt.tight_layout()
        plt.savefig(args.output/name, dpi=150)
        plt.close()
    t, b = brownian(paths=5, rng=rng)
    plt.figure(figsize=(8, 4)); plt.plot(t, b.T)
    plt.xlabel("Time"); plt.ylabel("W(t)"); plt.title("Brownian paths")
    save("figure_brownien.png")
    experiments = [
        (lambda x: np.full_like(x, .5), lambda x: np.ones_like(x), 0., "standard", "figure_eds_simple.png", "Additive-noise SDE"),
        (np.sqrt, lambda x: np.full_like(x, .1), 1., "full_truncation", "figure_sigma_racine.png", "Square-root diffusion: full truncation"),
        (lambda x: .7*np.sqrt(x), lambda x: np.full_like(x, .3), 1., "reflection", "figure_cir_reflechi.png", "Reflected Euler illustration (constant drift)")]
    for sigma, drift, x0, mode, filename, title in experiments:
        t, x = euler_eds(sigma, drift, x0, 1., 10, mode=mode, rng=rng)
        plt.figure(figsize=(8, 4)); plt.plot(t, x.T)
        plt.xlabel("Time"); plt.ylabel("X(t)"); plt.title(title)
        save(filename)
    # Coupled draws across noise amplitudes; exact ODE reference exp(-t).
    epsilons = np.array([1., .5, .2, .1, .05, .01])
    increments = rng.normal(size=(1000, 1000))*np.sqrt(.001)
    t = np.linspace(0, 1, 1001); exact_ode = np.exp(-t)
    errors, ses = [], []
    plt.figure(figsize=(8, 4)); plt.plot(t, exact_ode, color="black", lw=2, label="Exact ODE")
    for eps in epsilons:
        x = np.ones((1000, 1001))
        for k in range(1000):
            state = x[:, k]
            x[:, k+1] = state-state*.001+eps/(1+state*state)*increments[:, k]
        error = np.max(np.abs(x-exact_ode), axis=1)
        errors.append(float(error.mean())); ses.append(float(error.std(ddof=1)/np.sqrt(len(error))))
        plt.plot(t, x[0], alpha=.7, label=f"noise={eps:g}")
    plt.xlabel("Time"); plt.ylabel("X(t)"); plt.legend(fontsize=8)
    save("figure_convergence_edo.png")
    plt.figure(figsize=(8, 4)); plt.errorbar(epsilons, errors, yerr=1.96*np.array(ses), marker="o")
    plt.xscale("log"); plt.yscale("log"); plt.xlabel("Noise amplitude")
    plt.ylabel("Mean pathwise sup error (95% MC bars)")
    plt.title("Small-noise limit; fixed time grid")
    save("figure_quantification_convergence.png")
    with (args.output/"small_noise.csv").open("w", newline="") as f:
        writer=csv.writer(f); writer.writerow(["epsilon", "mean_sup_error", "mc_standard_error"])
        writer.writerows(zip(epsilons, errors, ses))
    result = gbm_convergence(paths=args.paths, seed=args.seed)
    with (args.output/"convergence.csv").open("w", newline="") as f:
        writer=csv.writer(f); writer.writerow(["steps","h","euler_l1_error","euler_mc_se","milstein_l1_error","milstein_mc_se"])
        writer.writerows(zip(result.steps,result.h,result.euler_error,result.euler_se,result.milstein_error,result.milstein_se))
    plt.figure(figsize=(8, 4))
    for label, error, se, slope in [("Euler",result.euler_error,result.euler_se,result.euler_slope),("Milstein",result.milstein_error,result.milstein_se,result.milstein_slope)]:
        plt.errorbar(result.h,error,yerr=1.96*se,marker="o",label=f"{label}: fitted slope {slope:.2f}")
    plt.xscale("log"); plt.yscale("log"); plt.xlabel("Time step h")
    plt.ylabel("Terminal strong L1 error (95% MC bars)"); plt.legend()
    save("figure_euler_milstein_loglog.png")
    summary={"seed":args.seed,"paths":args.paths,"mu":2.,"volatility":1.,"T":1.,"x0":1.,"euler_slope":result.euler_slope,"milstein_slope":result.milstein_slope,"slope_fit":"finest four grids", "numpy":np.__version__,"matplotlib":matplotlib.__version__}
    (args.output/"summary.json").write_text(json.dumps(summary, indent=2)+"\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
