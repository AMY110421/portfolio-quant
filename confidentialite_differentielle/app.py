#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from data import get_dataset, get_dataset_names
from utils import compute_sensitivity, compute_stats
from mechanisms import (
    laplace_mechanism,
    gaussian_mechanism,
    gaussian_mechanism_from_eps_delta,
)
from verification import verify_epsilon_dp

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
        self.epsilon_var = tk.DoubleVar(value=1.0)
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
        self.eps_label = tk.Label(card4, text="1.00", bg=CARD, fg=FG, font=('Segoe UI', 10, 'bold'), width=5)
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
        self._btn(row3, "🔍 Diagnostic numérique", self.verify_dp)
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
            self.data = np.loadtxt(path, delimiter=',')
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
    
    def run_calculation(self):
        if self.data is None or len(self.data) == 0:
            messagebox.showwarning("Avertissement", "Aucune donnée chargée")
            return
        
        self.ax.clear()
        
        func = self.func_var.get()
        mech = self.mech_var.get()
        eps = self.epsilon_var.get()
        delta = self.delta_var.get()
        clip_min = self.clip_min_var.get()
        clip_max = self.clip_max_var.get()
        threshold = self.threshold_var.get()
        
        data_clipped = np.clip(self.data, clip_min, clip_max)
        self.true_value = compute_stats(data_clipped, func, threshold)
        self.sensitivity = compute_sensitivity(func, clip_min, clip_max, len(data_clipped))
        
        if mech == "Laplace":
            self.result = laplace_mechanism(self.true_value, self.sensitivity, eps)
            self.mechanism_name = "Laplace"
            self.sigma_used = 0
        elif mech == "Gaussien":
            if self.use_manual_sigma.get():
                sigma = self.sigma_var.get()
                self.result = gaussian_mechanism(self.true_value, sigma)
                self.sigma_used = sigma
            else:
                self.result = gaussian_mechanism_from_eps_delta(self.true_value, self.sensitivity, eps, delta)
                self.sigma_used = (self.sensitivity * np.sqrt(2 * np.log(1.25 / delta))) / eps
            self.mechanism_name = "Gaussien"
        
        self._display_results()
        self._plot_comparison()
    
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
        """Affiche la distribution empirique des sorties du mécanisme sélectionné."""
        if self.data is None or len(self.data) == 0:
            return

        plt.style.use('dark_background')
        mech = self.mech_var.get()
        fig, ax = plt.subplots(figsize=(8, 5))
        fig.patch.set_facecolor('#1e1e2e')

        n_sim = 1000
        results = []
        for _ in range(n_sim):
            if mech == "Laplace":
                results.append(
                    laplace_mechanism(
                        self.true_value, self.sensitivity, self.epsilon_var.get()
                    )
                )
            else:
                if self.use_manual_sigma.get():
                    results.append(
                        gaussian_mechanism(self.true_value, self.sigma_var.get())
                    )
                else:
                    results.append(
                        gaussian_mechanism_from_eps_delta(
                            self.true_value,
                            self.sensitivity,
                            self.epsilon_var.get(),
                            self.delta_var.get(),
                        )
                    )

        ax.hist(results, bins=50, density=True, alpha=0.7, color='#89b4fa')
        ax.axvline(
            self.true_value,
            color='#f38ba8',
            linestyle='--',
            label=f'Valeur exacte = {self.true_value:.2f}',
        )
        ax.set_xlabel('Valeur bruitée', color='#cdd6f4')
        ax.set_ylabel('Densité', color='#cdd6f4')
        ax.set_title(
            f'Distribution des sorties ({mech}, ε = {self.epsilon_var.get():.2f})',
            color='#cdd6f4',
        )
        ax.legend()
        ax.grid(True, alpha=0.2)
        ax.tick_params(colors='#cdd6f4')
        plt.tight_layout()
        plt.show()

    @staticmethod
    def _log_density(value, center, scale, mechanism):
        """Log-densité utilisée par le classifieur de l'attaque simulée."""
        if scale <= 0:
            raise ValueError("L'échelle du bruit doit être strictement positive.")
        if mechanism == "Laplace":
            return -abs(value - center) / scale - np.log(2 * scale)
        return (
            -0.5 * ((value - center) / scale) ** 2
            - np.log(scale)
            - 0.5 * np.log(2 * np.pi)
        )

    def simulate_attack(self):
        """Simule la décision d'un attaquant entre deux bases adjacentes."""
        if self.data is None or len(self.data) < 2:
            messagebox.showwarning(
                "Avertissement",
                "Il faut au moins deux enregistrements pour construire une base adjacente.",
            )
            return

        try:
            func = self.func_var.get()
            mech = self.mech_var.get()
            epsilon = float(self.epsilon_var.get())
            delta = float(self.delta_var.get())
            clip_min = float(self.clip_min_var.get())
            clip_max = float(self.clip_max_var.get())
            threshold = float(self.threshold_var.get())
            if epsilon <= 0 or clip_min >= clip_max:
                raise ValueError("Les paramètres ε et les bornes de clipping sont invalides.")
            if mech == "Gaussien" and not (0 < delta < 1):
                raise ValueError("δ doit être compris entre 0 et 1.")

            data_d = np.clip(self.data, clip_min, clip_max)
            data_dp = data_d[1:]
            value_d = compute_stats(data_d, func, threshold)
            value_dp = compute_stats(data_dp, func, threshold)
            sensitivity = compute_sensitivity(
                func, clip_min, clip_max, len(data_d)
            )

            if mech == "Laplace":
                scale = sensitivity / epsilon
                draw = lambda center: laplace_mechanism(
                    center, sensitivity, epsilon
                )
            else:
                if self.use_manual_sigma.get():
                    scale = float(self.sigma_var.get())
                    draw = lambda center: gaussian_mechanism(center, scale)
                else:
                    scale = (
                        sensitivity
                        * np.sqrt(2 * np.log(1.25 / delta))
                        / epsilon
                    )
                    draw = lambda center: gaussian_mechanism_from_eps_delta(
                        center, sensitivity, epsilon, delta
                    )

            n_sim = 1000
            outputs_d = np.array([draw(value_d) for _ in range(n_sim)])
            outputs_dp = np.array([draw(value_dp) for _ in range(n_sim)])

            decisions_d = np.array([
                self._log_density(z, value_d, scale, mech)
                >= self._log_density(z, value_dp, scale, mech)
                for z in outputs_d
            ])
            decisions_dp = np.array([
                self._log_density(z, value_dp, scale, mech)
                > self._log_density(z, value_d, scale, mech)
                for z in outputs_dp
            ])
            accuracy = 0.5 * (decisions_d.mean() + decisions_dp.mean())

            fig, ax = plt.subplots(figsize=(8, 5))
            ax.hist(outputs_d, bins=45, density=True, alpha=0.55, label='Sorties depuis D')
            ax.hist(outputs_dp, bins=45, density=True, alpha=0.55, label="Sorties depuis D'")
            ax.axvline(value_d, color='#1f77b4', linestyle='--', label='Centre sous D')
            ax.axvline(value_dp, color='#ff7f0e', linestyle='--', label="Centre sous D'")
            ax.set_xlabel('Sortie observée')
            ax.set_ylabel('Densité empirique')
            ax.set_title(f'Attaque simulée ({mech}, ε = {epsilon:.2f})')
            ax.legend()
            ax.grid(alpha=0.2)
            fig.tight_layout()
            plt.show()

            msg = "🎯 Attaque simulée\n" + "-" * 30 + "\n"
            msg += f"Base D : {len(data_d)} enregistrements\n"
            msg += f"Base D' : {len(data_dp)} enregistrements\n"
            msg += f"Valeur sous D : {value_d:.2f}\n"
            msg += f"Valeur sous D' : {value_dp:.2f}\n"
            msg += f"Décisions correctes : {100 * accuracy:.1f} %\n"
            msg += "-" * 30 + "\n"
            msg += (
                "Plus les distributions se recouvrent, plus la distinction est difficile. "
                "Ce résultat est une simulation et ne constitue pas une preuve de DP."
            )
            messagebox.showinfo("Attaque simulée", msg)
        except Exception as exc:
            messagebox.showerror("Erreur", f"Impossible de simuler l'attaque : {exc}")

    def verify_dp(self):
        if self.data is None or len(self.data) == 0:
            messagebox.showwarning("Avertissement", "Aucune donnée chargée")
            return
        
        mech_choice = 1 if self.mech_var.get() == "Laplace" else 2
        ratio, e_eps, bayes, ok = verify_epsilon_dp(
            self.true_value, self.sensitivity, self.epsilon_var.get(), self.delta_var.get(), mech_choice
        )
        
        msg = f"🔍 Vérification de la garantie ε-DP\n"
        msg += "-" * 30 + "\n"
        msg += f"e^ε = {e_eps:.4f}\n"
        msg += f"Rapport estimé : {ratio:.4f}\n"
        msg += f"Erreur de Bayes : {bayes:.4f}\n"
        msg += "-" * 30 + "\n"
        msg += "✅ Simulation compatible avec la borne" if ok else "⚠️ Simulation incompatible avec la borne"
        
        messagebox.showinfo("Diagnostic numérique", msg)

def main():
    root = tk.Tk()
    app = DPApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
