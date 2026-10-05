"""Fixed-grid accuracy comparisons and indicative runtime measurements."""
import csv
import platform
from pathlib import Path
from time import perf_counter
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from pricing import Market, black_scholes_call, finite_difference_call


def main():
    out=Path("results"); out.mkdir(exist_ok=True)
    m=Market(); reference=black_scholes_call(m)
    rows=[]
    for space_steps in (100, 200, 400):
        # Same spatial and temporal grids for both schemes; explicit monotonicity.
        time_steps=max(2000, int(np.ceil(1.1*m.maturity*(m.volatility**2*(space_steps-1)**2+m.rate))))
        for scheme in ("explicit","implicit"):
            start=perf_counter()
            price=finite_difference_call(m,scheme=scheme,space_steps=space_steps,time_steps=time_steps)
            rows.append([space_steps,time_steps,scheme,price,abs(price-reference),perf_counter()-start])
    with (out/"convergence.csv").open("w",newline="") as f:
        writer=csv.writer(f);writer.writerow(["space_steps","time_steps","scheme","price","absolute_error","seconds"]);writer.writerows(rows)
    # Sensitivity to the finite domain, keeping spatial step approximately one.
    domains=[]
    for s_max in (200.,300.,400.,600.):
        space_steps=int(s_max)
        price=finite_difference_call(m,scheme="implicit",space_steps=space_steps,time_steps=4000,s_max=s_max)
        domains.append([s_max,space_steps,price,abs(price-reference)])
    with (out/"domain.csv").open("w",newline="") as f:
        writer=csv.writer(f);writer.writerow(["s_max","space_steps","price","absolute_error"]);writer.writerows(domains)
    # A small validation matrix, not a claim of universal accuracy.
    with (out/"parameter_cases.csv").open("w",newline="") as f:
        writer=csv.writer(f);writer.writerow(["spot","volatility","analytical","implicit","absolute_error"])
        for spot in (80.,100.,120.):
            for volatility in (.2,.4):
                case=Market(spot=spot,volatility=volatility)
                price=finite_difference_call(case,scheme="implicit",space_steps=200,time_steps=2000)
                exact=black_scholes_call(case)
                writer.writerow([spot,volatility,exact,price,abs(price-exact)])
    fig,axes=plt.subplots(1,2,figsize=(10,4))
    for scheme in ("explicit","implicit"):
        selected=[row for row in rows if row[2]==scheme]
        axes[0].loglog([row[0] for row in selected],[row[4] for row in selected],"o-",label=scheme)
        axes[1].plot([row[0] for row in selected],[row[5] for row in selected],"o-",label=scheme)
    axes[0].set(xlabel="Space steps",ylabel="Absolute pricing error",title="Same-grid accuracy")
    axes[1].set(xlabel="Space steps",ylabel="Wall time (seconds)",title="Indicative runtime; one run")
    for ax in axes: ax.legend();ax.grid(alpha=.3)
    fig.tight_layout();fig.savefig(out/"convergence.png",dpi=150);plt.close(fig)
    (out/"environment.txt").write_text(f"Python {platform.python_version()}\nNumPy {np.__version__}\nRuntime measurements depend on hardware and load; no equal-runtime claim.\n")
    print("Analytical:",reference)
    for row in rows:print(row)


if __name__ == "__main__":
    main()
