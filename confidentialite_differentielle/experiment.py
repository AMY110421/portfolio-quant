"""Seeded Laplace distinction experiment without a graphical desktop."""
import csv
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from data import get_dataset
from utils import adjacent_replacement, compute_sensitivity, compute_stats
from verification import distribution_diagnostic


def main():
    data,_=get_dataset("Salaires")
    d,dp=adjacent_replacement(data,"Moyenne",0,100000)
    centers=[compute_stats(x,"Moyenne") for x in (d,dp)]
    sensitivity=compute_sensitivity("Moyenne",0,100000,len(d))
    rng=np.random.default_rng(42)
    rows=[];out=Path("results");out.mkdir(exist_ok=True)
    for eps in (.1,.25,.5,1.,2.,5.):
        result=distribution_diagnostic(*centers,sensitivity/eps,"Laplace",n_sim=10000,rng=rng)
        rows.append([eps,result['accuracy'],result['stderr'],*result['ci95']])
    with (out/"distinction.csv").open("w",newline="") as f:
        writer=csv.writer(f);writer.writerow(["epsilon","accuracy","mc_se","ci95_low","ci95_high"]);writer.writerows(rows)
    fig,ax=plt.subplots(figsize=(8,4))
    ax.errorbar([r[0] for r in rows],[r[1] for r in rows],yerr=[1.96*r[2] for r in rows],marker="o")
    ax.axhline(.5,ls="--",color="gray",label="Random guessing")
    ax.set(xlabel="Epsilon",ylabel="Classification accuracy (95% MC bars)",title="One adjacent pair, one output, equal priors")
    ax.legend();fig.tight_layout();fig.savefig(out/"distinction.png",dpi=150);plt.close(fig)
    print("Seed=42; salaries mean; fixed-size replacement; bounds [0,100000]; n_sim=10000 per hypothesis")
    print(rows)


if __name__ == "__main__":
    main()
