#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from data import get_dataset, get_dataset_names
from utils import compute_sensitivity, compute_stats, adjacent_replacement
from mechanisms import (
    laplace_mechanism,
    gaussian_mechanism,
    gaussian_mechanism_from_eps_delta,
    gaussian_scale,
)
from verification import distribution_diagnostic, log_density

# =====================================================
# STYLES
# =====================================================

BG = "#1e1e2e"
FG = "#cdd6f4"
CARD = "#313244"
ACCENT = "#89b4fa"

class DPApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Confidentialité Différentielle")
        self.root.geometry("1200x800")
        self.root.configure(bg=BG)
        
        # Variables
        self.data = None
        self.description = ""
        self.true_value = 0
        self.sensitivity = 1
        self.result = 0
        self.mechanism_name = ""
        self.sigma_used = 0
        
        # Variables Tkinter
        self.dataset_var = tk.StringVar(value="Salaires")
        self.func_var = tk.StringVar(value="Moyenne")
        self.mech_var = tk.StringVar(value="Laplace")
        self.epsilon_var = tk.DoubleVar(value=0.5)
        self.delta_var = tk.DoubleVar(value=1e-5)
        self.sigma_var = tk.DoubleVar(value=1.0)
        self.use_manual_sigma = tk.BooleanVar(value=False)
        self.clip_min_var = tk.DoubleVar(value=0)
        self.clip_max_var = tk.DoubleVar(value=100000)
        self.threshold_var = tk.DoubleVar(value=50)
        
        self.create_widgets()
        
        # Liaison du changement de base
        self.dataset_var.trace('w', lambda *args: self.load_dataset())
        
        self.load_dataset()
    
    def create_widgets(self):
        main = tk.Frame(self.root, bg=BG)
        main.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        tk.Label(main, text="🔐 Confidentialité Différentielle", 
                 font=('Segoe UI', 20, 'bold'), bg=BG, fg=FG).pack(anchor=tk.W, pady=(0, 20))
        
        row1 = tk.Frame(main, bg=BG)
        row1.pack(fill=tk.X, pady=5)
        
        # Base
        card1 = self._make_card(row1, "📊 Base")
        self._combobox(card1, self.dataset_var, get_dataset_names() + ["Charger CSV..."])
        btn = tk.Button(card1, text="📁", command=self.load_csv, bg=ACCENT, fg=BG, font=('Segoe UI', 10))
        btn.pack(side=tk.LEFT, padx=2)
        self.info_label = tk.Label(card1, text="", bg=CARD, fg=FG, font=('Segoe UI', 8))
        self.info_label.pack(side=tk.LEFT, padx=10)
        
        # Statistique
        card2 = self._make_card(row1, "📈 Statistique")
        for f in ["Moyenne", "Comptage", "Somme"]:
            rb = tk.Radiobutton(card2, text=f, variable=self.func_var, value=f,
                                bg=CARD, fg=FG, selectcolor=BG, font=('Segoe UI', 10))
            rb.pack(side=tk.LEFT, padx=5)
        
        tk.Label(card2, text="Seuil:", bg=CARD, fg=FG, font=('Segoe UI', 10)).pack(side=tk.LEFT, padx=(15, 5))
        self._entry(card2, self.threshold_var, width=8)
        
        # Mécanisme
        card3 = self._make_card(row1, "🔐 Mécanisme")
        for m in ["Laplace", "Gaussien"]:
            rb = tk.Radiobutton(card3, text=m, variable=self.mech_var, value=m,
                                bg=CARD, fg=FG, selectcolor=BG, font=('Segoe UI', 10),
                                command=self._update_sigma_widgets)
            rb.pack(side=tk.LEFT, padx=5)
        
        row2 = tk.Frame(main, bg=BG)
        row2.pack(fill=tk.X, pady=10)
        
        card4 = self._make_card(row2, "⚙️ Paramètres")
        
        # ε
        tk.Label(card4, text="ε:", bg=CARD, fg=FG, font=('Segoe UI', 10)).pack(side=tk.LEFT, padx=(0, 5))
        scale = tk.Scale(card4, from_=0.01, to=5.0, resolution=0.01, orient=tk.HORIZONTAL,
                         variable=self.epsilon_var, bg=CARD, fg=FG, highlightthickness=0, length=150)
        scale.pack(side=tk.LEFT, padx=5)
        self.eps_label = tk.Label(card4, text="0.50", bg=CARD, fg=FG, font=('Segoe UI', 10, 'bold'), width=5)
        self.eps_label.pack(side=tk.LEFT, padx=5)
        
        # δ
        tk.Label(card4, text="δ:", bg=CARD, fg=FG, font=('Segoe UI', 10)).pack(side=tk.LEFT, padx=(15, 5))
        self._entry(card4, self.delta_var, width=12)
        
        # σ
        tk.Label(card4, text="σ:", bg=CARD, fg=FG, font=('Segoe UI', 10)).pack(side=tk.LEFT, padx=(15, 5))
        self.sigma_entry = self._entry(card4, self.sigma_var, width=10, state='disabled')
        cb = tk.Checkbutton(card4, text="Manuel", variable=self.use_manual_sigma,
                            bg=CARD, fg=FG, selectcolor=BG, font=('Segoe UI', 10),
                            command=self._update_sigma_widgets)
        cb.pack(side=tk.LEFT, padx=5)
        
        # Clipping
        tk.Label(card4, text="Clipping:", bg=CARD, fg=FG, font=('Segoe UI', 10)).pack(side=tk.LEFT, padx=(15, 5))
        self._entry(card4, self.clip_min_var, width=8)
        tk.Label(card4, text="à", bg=CARD, fg=FG, font=('Segoe UI', 10)).pack(side=tk.LEFT, padx=2)
        self._entry(card4, self.clip_max_var, width=8)
        
        row3 = tk.Frame(main, bg=BG)
        row3.pack(fill=tk.X, pady=10)
        
        self._btn(row3, "🔄 Lancer", self.run_calculation)
        self._btn(row3, "📊 Graphiques", self.show_all_graphs)
        self._btn(row3, "🔍 Distinction empirique", self.verify_dp)
        self._btn(row3, "🎯 Attaque", self.simulate_attack)
        
        row4 = tk.Frame(main, bg=BG)
        row4.pack(fill=tk.BOTH, expand=True, pady=10)
        
        left = tk.Frame(row4, bg=CARD)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 10))
        
        tk.Label(left, text="📊 Résultats", font=('Segoe UI', 12, 'bold'), bg=CARD, fg=FG).pack(anchor=tk.W, pady=(10, 5), padx=10)
        
        self.result_text = tk.Text(left, height=14, width=35, bg=BG, fg=FG, font=('Segoe UI', 10), relief='flat', padx=10, pady=10)
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        self.result_text.config(state=tk.DISABLED)
        
        right = tk.Frame(row4, bg=CARD)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.fig, self.ax = plt.subplots(figsize=(7, 5))
        self.fig.patch.set_facecolor(CARD)
        self.ax.set_facecolor(BG)
        self.ax.tick_params(colors=FG)
        for spine in self.ax.spines.values():
            spine.set_color(FG)
        self.ax.xaxis.label.set_color(FG)
        self.ax.yaxis.label.set_color(FG)
        self.ax.title.set_color(FG)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=right)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.epsilon_var.trace('w', self._update_eps_label)
        self._update_eps_label()
        self._update_sigma_widgets()
    
    def _make_card(self, parent, title):
        frame = tk.Frame(parent, bg=CARD, padx=10, pady=5)
        frame.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        if title:
            tk.Label(frame, text=title, bg=CARD, fg=FG, font=('Segoe UI', 10, 'bold')).pack(anchor=tk.W)
        content = tk.Frame(frame, bg=CARD)
        content.pack(fill=tk.X, pady=2)
        return content
    
    def _entry(self, parent, var, width, state='normal'):
        entry = tk.Entry(parent, textvariable=var, width=width, bg=BG, fg=FG,
                         insertbackground=FG, relief='flat', font=('Segoe UI', 10), state=state)
        entry.pack(side=tk.LEFT, padx=2)
        return entry
    
    def _combobox(self, parent, var, values):
        cb = ttk.Combobox(parent, textvariable=var, values=values, state='readonly', width=18, font=('Segoe UI', 10))
        cb.pack(side=tk.LEFT, padx=2)
        return cb
    
    def _btn(self, parent, text, cmd):
        btn = tk.Button(parent, text=text, command=cmd, bg=ACCENT, fg=BG,
                        font=('Segoe UI', 10, 'bold'), relief='flat', padx=15, pady=5)
        btn.pack(side=tk.LEFT, padx=5)
        return btn
    
    def _update_eps_label(self, *args):
        self.eps_label.config(text=f"{self.epsilon_var.get():.2f}")
    
    def _update_sigma_widgets(self):
        if self.mech_var.get() == "Gaussien" and self.use_manual_sigma.get():
            self.sigma_entry.config(state='normal')
        else:
            self.sigma_entry.config(state='disabled')
    
    def load_dataset(self):
        name = self.dataset_var.get()
        if name == "Charger CSV...":
            return
        self.data, self.description = get_dataset(name)
        
        # Adapter le clipping à la base
        if name == "Âges":
            self.clip_min_var.set(0)
            self.clip_max_var.set(100)
        elif name == "Données médicales":
            self.clip_min_var.set(0)
            self.clip_max_var.set(15)
        else:  # Salaires
            self.clip_min_var.set(0)
            self.clip_max_var.set(100000)
        
        self._update_info()
        self._plot_data()
    
    def load_csv(self):
        path = filedialog.askopenfilename(title="Sélectionner un fichier CSV", filetypes=[("CSV files", "*.csv")])
        if not path:
            self.dataset_var.set("Salaires")
            return
        try:
            candidate = np.atleast_1d(np.loadtxt(path, delimiter=','))
            compute_stats(candidate, "Moyenne")
            self.data = candidate
            self.description = f"Données chargées"
            self.dataset_var.set("Charger CSV...")
            self._update_info()
            self._plot_data()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur : {e}")
            self.dataset_var.set("Salaires")
    
    def _update_info(self):
        if self.data is not None and len(self.data) > 0:
            self.info_label.config(text=f"{len(self.data)} enr. | Min: {np.min(self.data):.1f} | Max: {np.max(self.data):.1f}")
    
    def _plot_data(self):
        if self.data is None or len(self.data) == 0:
            return
        self.ax.clear()
        self.ax.hist(self.data, bins=20, alpha=0.7, color=ACCENT, edgecolor=FG)
        self.ax.set_xlabel('Valeur', color=FG)
        self.ax.set_ylabel('Fréquence', color=FG)
        self.ax.set_title('Données', color=FG)
        self.ax.grid(True, alpha=0.2, color=FG)
        self.ax.tick_params(colors=FG)
        self.canvas.draw_idle()
    
    def _parameters(self):
        if self.data is None:
            raise ValueError("Aucune donnée chargée")
        func, mech = self.func_var.get(), self.mech_var.get()
        epsilon, delta = float(self.epsilon_var.get()), float(self.delta_var.get())
        lower, upper = float(self.clip_min_var.get()), float(self.clip_max_var.get())
        threshold = float(self.threshold_var.get())
        sensitivity = compute_sensitivity(func, lower, upper, len(self.data))
        if not np.isfinite(epsilon) or epsilon <= 0:
            raise ValueError("ε doit être fini et strictement positif")
        d, dp = adjacent_replacement(self.data, func, lower, upper, threshold)
        value_d = compute_stats(d, func, threshold)
        value_dp = compute_stats(dp, func, threshold)
        if mech == "Laplace":
            scale = sensitivity / epsilon
        elif self.use_manual_sigma.get():
            scale = float(self.sigma_var.get())
            log_density(value_d, value_d, scale, mech)
        else:
            scale = gaussian_scale(sensitivity, epsilon, delta)
        return func, mech, epsilon, delta, sensitivity, scale, value_d, value_dp

    def run_calculation(self):
        try:
            func, mech, eps, delta, sensitivity, scale, value_d, _ = self._parameters()
            self.true_value, self.sensitivity = value_d, sensitivity
            self.mechanism_name = mech
            self.sigma_used = scale if mech == "Gaussien" else 0
            if mech == "Laplace":
                self.result = laplace_mechanism(value_d, sensitivity, eps)
            else:
                self.result = gaussian_mechanism(value_d, scale)
            self._display_results()
            self._plot_comparison()
        except Exception as exc:
            messagebox.showerror("Paramètres invalides", str(exc))

    def _display_results(self):
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        
        text = f"Statistique : {self.func_var.get()}\n"
        text += "-" * 30 + "\n"
        text += f"Vraie valeur : {self.true_value:.2f}\n"
        text += f"Mécanisme : {self.mechanism_name}\n"
        text += f"ε = {self.epsilon_var.get():.2f}\n"
        if self.mechanism_name == "Gaussien":
            text += f"σ = {self.sigma_used:.4f}\n"
        text += f"Résultat : {self.result:.2f}\n"
        text += f"Écart : {abs(self.result - self.true_value):.2f}\n"
        text += "-" * 30 + "\n"
        text += f"Sensibilité : {self.sensitivity:.2f}"
        
        self.result_text.insert(1.0, text)
        self.result_text.config(state=tk.DISABLED)
    
    def _plot_comparison(self):
        self.ax.clear()
        bars = self.ax.bar(
            ['Vraie valeur', self.mechanism_name],
            [self.true_value, self.result],
            color=['#89b4fa', '#f9e2af'],
            alpha=0.8,
            edgecolor='white'
        )
        self.ax.set_ylabel('Valeur', color=FG)
        self.ax.set_title('Comparaison', color=FG)
        self.ax.grid(True, alpha=0.2, color=FG)
        self.ax.tick_params(colors=FG)
        
        for bar, val in zip(bars, [self.true_value, self.result]):
            height = bar.get_height()
            self.ax.text(
                bar.get_x() + bar.get_width()/2.,
                height + 0.05 * abs(height) if height >= 0 else height - 0.05 * abs(height),
                f'{val:.2f}',
                ha='center',
                va='bottom' if height >= 0 else 'top',
                fontweight='bold',
                color=FG
            )
        
        self.canvas.draw_idle()
    
    def show_all_graphs(self):
        try:
            _, mech, eps, _, _, scale, value_d, value_dp = self._parameters()
            result = distribution_diagnostic(value_d, value_dp, scale, mech, n_sim=1000)
            fig, ax = plt.subplots(figsize=(8, 5))
            ax.hist(result["outputs_d"], bins=50, density=True, alpha=0.7)
            ax.axvline(value_d, color="red", linestyle="--", label="Valeur exacte")
            ax.set(xlabel="Sortie bruitée", ylabel="Densité", title=f"Distribution ({mech}, ε={eps:.2f})")
            ax.legend()
            fig.tight_layout()
            plt.show()
        except Exception as exc:
            messagebox.showerror("Paramètres invalides", str(exc))

    def simulate_attack(self):
        try:
            _, mech, eps, _, _, scale, value_d, value_dp = self._parameters()
            result = distribution_diagnostic(value_d, value_dp, scale, mech)
            fig, ax = plt.subplots(figsize=(8, 5))
            ax.hist(result["outputs_d"], bins=45, density=True, alpha=0.55, label="D")
            ax.hist(result["outputs_dp"], bins=45, density=True, alpha=0.55, label="D' : une ligne remplacée")
            ax.set(xlabel="Sortie observée", ylabel="Densité", title=f"Attaque simulée ({mech}, ε={eps:.2f})")
            ax.legend()
            fig.tight_layout()
            plt.show()
            self._show_diagnostic(result)
        except Exception as exc:
            messagebox.showerror("Paramètres invalides", str(exc))

    def _show_diagnostic(self, result):
        lo, hi = result["ci95"]
        messagebox.showinfo("Diagnostic de distinction", (
            "Adjacence : remplacement d'une ligne, taille publique fixe.\n"
            f"Décisions correctes : {100*result['accuracy']:.1f} %\n"
            f"Intervalle Monte-Carlo approximatif à 95 % : [{100*lo:.1f}, {100*hi:.1f}] %\n\n"
            "Hypothèses : deux bases connues, probabilités a priori égales, une sortie.\n"
            "Ce diagnostic ne vérifie ni ne certifie une garantie DP.\n"
            "Le mode σ manuel n'associe pas automatiquement une garantie (ε, δ)."
        ))

    def verify_dp(self):
        try:
            _, mech, _, _, _, scale, value_d, value_dp = self._parameters()
            self._show_diagnostic(distribution_diagnostic(value_d, value_dp, scale, mech))
        except Exception as exc:
            messagebox.showerror("Paramètres invalides", str(exc))

def main():
    root = tk.Tk()
    app = DPApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()

