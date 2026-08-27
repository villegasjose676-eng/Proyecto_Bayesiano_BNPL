"""
Modelo Bayesiano Paso 1 — Inferencia Normal-Normal (analítica)
==============================================================
Estima la distribución posterior de la media del Credit_Score
para cada grupo de Default_Risk (Low, Medium, High).

Fundamento matemático:
  Verosimilitud:  Y_i | μ, σ² ~ Normal(μ, σ²)
  Prior:          μ ~ Normal(μ₀, τ₀²)       [prior sobre la media]
  Varianza σ² se estima con la varianza muestral (enfoque empírico-bayesiano).

  Posterior analítico (σ² conocida):
    μ | datos ~ Normal(μₙ, τₙ²)

    Donde:
      τₙ² = 1 / (1/τ₀² + n/σ²)
      μₙ  = τₙ² * (μ₀/τ₀² + n*ȳ/σ²)

Salidas:
  figuras/fig6_normal_normal_posteriors.png
  figuras/fig7_comparacion_grupos.png
  analisis/tabla_posteriors_creditscore.csv
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy import stats

# ── Configuración ─────────────────────────────────────────────────────────────
FIGURAS_DIR = os.path.join(os.path.dirname(__file__), '..', 'figuras')
ANALISIS_DIR = os.path.dirname(__file__)
os.makedirs(FIGURAS_DIR, exist_ok=True)

PALETTE = {"Low": "#2ECC71", "Medium": "#F39C12", "High": "#E74C3C"}
plt.rcParams.update({'figure.dpi': 150, 'font.family': 'DejaVu Sans'})

# ── Datos ─────────────────────────────────────────────────────────────────────
CSV = os.path.join(os.path.dirname(__file__), '..', 'BNPL_Financial_Default_Risk_Dataset.csv')
df = pd.read_csv(CSV)
df['Default_Risk'] = pd.Categorical(df['Default_Risk'],
    categories=['Low', 'Medium', 'High'], ordered=True)

GRUPOS = ['Low', 'Medium', 'High']

# ── Especificación del prior ───────────────────────────────────────────────────
# Prior débilmente informativo: centrado en la media general del puntaje FICO
# μ₀ = 650 (ligeramente por debajo de la media muestral, representando
#           conocimiento previo genérico sobre puntajes crediticios)
# τ₀² = 100² = 10000 (prior muy difuso, equivale a ±200 pts al 95%)
MU_0 = 650.0          # media del prior
TAU_0_SQ = 100.0**2   # varianza del prior (τ₀² = 10000)

print("=" * 60)
print("MODELO BAYESIANO PASO 1 — Normal-Normal")
print("=" * 60)
print(f"\nPrior: μ ~ Normal(μ₀={MU_0}, τ₀={100.0})")
print("Justificación: prior débilmente informativo centrado en 650")
print("(promedio aproximado del rango FICO 300-850 ponderado hacia")
print(" la distribución de la población general de BNPL usuarios).\n")

# ── Cálculo del posterior por grupo ───────────────────────────────────────────
resultados = []
posteriors = {}

for grupo in GRUPOS:
    data = df.loc[df['Default_Risk'] == grupo, 'Credit_Score'].dropna()
    n = len(data)
    y_bar = data.mean()
    sigma_sq = data.var(ddof=1)   # varianza muestral usada como σ² conocida

    # Parámetros del posterior
    tau_n_sq = 1.0 / (1.0/TAU_0_SQ + n/sigma_sq)
    mu_n = tau_n_sq * (MU_0/TAU_0_SQ + n*y_bar/sigma_sq)
    tau_n = np.sqrt(tau_n_sq)

    # Intervalo de credibilidad al 95% (HPD = intervalo de igual cola para Normal)
    ic_low  = stats.norm.ppf(0.025, mu_n, tau_n)
    ic_high = stats.norm.ppf(0.975, mu_n, tau_n)

    # Distribución predictiva posterior: Y_nuevo ~ Normal(μₙ, σ² + τₙ²)
    sigma_pred = np.sqrt(sigma_sq + tau_n_sq)

    posteriors[grupo] = {
        'n': n, 'y_bar': y_bar, 'sigma': np.sqrt(sigma_sq),
        'mu_n': mu_n, 'tau_n': tau_n, 'tau_n_sq': tau_n_sq,
        'ic_low': ic_low, 'ic_high': ic_high,
        'sigma_pred': sigma_pred
    }

    resultados.append({
        'Grupo': grupo,
        'n': n,
        'Media muestral (ȳ)': round(y_bar, 2),
        'Std muestral (σ)': round(np.sqrt(sigma_sq), 2),
        'Media posterior (μₙ)': round(mu_n, 4),
        'Std posterior (τₙ)': round(tau_n, 4),
        'IC 95% inferior': round(ic_low, 2),
        'IC 95% superior': round(ic_high, 2),
        'Amplitud IC': round(ic_high - ic_low, 2)
    })

    print(f"Grupo: {grupo}")
    print(f"  n = {n:,}")
    print(f"  ȳ = {y_bar:.2f},  σ̂ = {np.sqrt(sigma_sq):.2f}")
    print(f"  Posterior: μ ~ Normal({mu_n:.4f}, {tau_n:.4f}²)")
    print(f"  IC 95%: [{ic_low:.2f}, {ic_high:.2f}]")
    print()

tabla_post = pd.DataFrame(resultados)
tabla_post.to_csv(os.path.join(ANALISIS_DIR, 'tabla_posteriors_creditscore.csv'), index=False)
print("Tabla de posteriors guardada.\n")


# ── Comparación bayesiana entre grupos ────────────────────────────────────────
# P(μ_High < μ_Low | datos) y P(μ_Medium < μ_Low | datos)
# Como los posteriors son normales independientes:
# μ_Low - μ_High ~ Normal(μₙ_Low - μₙ_High, τₙ²_Low + τₙ²_High)

N_MC = 500_000
rng = np.random.default_rng(42)

mu_low_mc    = rng.normal(posteriors['Low']['mu_n'],    posteriors['Low']['tau_n'],    N_MC)
mu_medium_mc = rng.normal(posteriors['Medium']['mu_n'], posteriors['Medium']['tau_n'], N_MC)
mu_high_mc   = rng.normal(posteriors['High']['mu_n'],   posteriors['High']['tau_n'],   N_MC)

p_high_lt_low   = np.mean(mu_high_mc < mu_low_mc)
p_medium_lt_low = np.mean(mu_medium_mc < mu_low_mc)
p_high_lt_med   = np.mean(mu_high_mc < mu_medium_mc)
diff_hl_mean    = np.mean(mu_low_mc - mu_high_mc)
diff_hl_ic      = np.percentile(mu_low_mc - mu_high_mc, [2.5, 97.5])

print("COMPARACIONES BAYESIANAS (Monte Carlo, N=500 000)")
print(f"  P(μ_High < μ_Low | datos)   = {p_high_lt_low:.6f}")
print(f"  P(μ_Med  < μ_Low | datos)   = {p_medium_lt_low:.6f}")
print(f"  P(μ_High < μ_Med | datos)   = {p_high_lt_med:.6f}")
print(f"  E[μ_Low - μ_High | datos]   = {diff_hl_mean:.2f} puntos")
print(f"  IC 95% diferencia (Low-High)= [{diff_hl_ic[0]:.2f}, {diff_hl_ic[1]:.2f}]")


# ─────────────────────────────────────────────────────────────────────────────
# FIGURA 6 — Prior vs. Posterior por grupo
# ─────────────────────────────────────────────────────────────────────────────
x = np.linspace(400, 850, 1200)

fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=False)
fig.suptitle('Distribuciones a priori y posteriores del Credit Score por grupo de riesgo',
             fontsize=13)

prior_y = stats.norm.pdf(x, MU_0, np.sqrt(TAU_0_SQ))

for ax, grupo in zip(axes, GRUPOS):
    p = posteriors[grupo]
    post_y = stats.norm.pdf(x, p['mu_n'], p['tau_n'])
    pred_y = stats.norm.pdf(x, p['mu_n'], p['sigma_pred'])

    # Escalar prior para que sea visible (es muy plano)
    prior_scaled = prior_y / prior_y.max() * post_y.max() * 0.35

    ax.fill_between(x, post_y, alpha=0.35, color=PALETTE[grupo], label='Posterior μ')
    ax.plot(x, post_y, color=PALETTE[grupo], lw=2)
    ax.plot(x, prior_scaled, color='#888888', lw=1.5, ls='--', label='Prior (escalado)')
    ax.plot(x, pred_y / pred_y.max() * post_y.max() * 0.6,
            color='#2C3E50', lw=1.2, ls=':', label='Predictiva posterior')

    # IC 95%
    ax.axvline(p['ic_low'],  color=PALETTE[grupo], lw=1, ls='-.',
               label=f"IC 95%: [{p['ic_low']:.0f}, {p['ic_high']:.0f}]")
    ax.axvline(p['ic_high'], color=PALETTE[grupo], lw=1, ls='-.')
    ax.axvline(p['mu_n'], color='#2C3E50', lw=1.5, ls='--',
               label=f"μₙ = {p['mu_n']:.1f}")

    ax.set_title(f'Grupo: {grupo}\n(n={p["n"]:,})', fontsize=11)
    ax.set_xlabel('Credit Score')
    ax.set_ylabel('Densidad', fontsize=9)
    ax.legend(fontsize=7.5, framealpha=0.7)
    ax.set_xlim(400, 850)

plt.tight_layout()
fig.savefig(os.path.join(FIGURAS_DIR, 'fig6_normal_normal_posteriors.png'),
            bbox_inches='tight', dpi=150)
plt.close()
print("\nFigura 6 guardada.")


# ─────────────────────────────────────────────────────────────────────────────
# FIGURA 7 — Comparación de posteriors superpuestos + diferencia
# ─────────────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
fig.suptitle('Comparación bayesiana del Credit Score entre grupos de riesgo', fontsize=13)

# Panel izquierdo: posteriors superpuestos
x_zoom = np.linspace(530, 730, 1000)
for grupo in GRUPOS:
    p = posteriors[grupo]
    y = stats.norm.pdf(x_zoom, p['mu_n'], p['tau_n'])
    axes[0].fill_between(x_zoom, y, alpha=0.25, color=PALETTE[grupo])
    axes[0].plot(x_zoom, y, color=PALETTE[grupo], lw=2.5, label=f"{grupo} (μₙ={p['mu_n']:.1f})")
    axes[0].axvline(p['mu_n'], color=PALETTE[grupo], lw=1.2, ls='--')
    # IC 95% como segmento horizontal
    y_pos = y.max() * 0.08
    axes[0].annotate('', xy=(p['ic_high'], y_pos), xytext=(p['ic_low'], y_pos),
                     arrowprops=dict(arrowstyle='<->', color=PALETTE[grupo], lw=1.2))

axes[0].set_xlabel('Credit Score')
axes[0].set_ylabel('Densidad posterior de μ')
axes[0].set_title('Distribuciones posteriores (zoom)')
axes[0].legend(fontsize=9)

# Panel derecho: distribución de μ_Low - μ_High
diff_samples = mu_low_mc - mu_high_mc
axes[1].hist(diff_samples, bins=80, color='#5B8DB8', alpha=0.75,
             edgecolor='white', linewidth=0.3, density=True)
axes[1].axvline(diff_hl_ic[0], color='#E74C3C', lw=1.5, ls='--',
                label=f'IC 95%: [{diff_hl_ic[0]:.1f}, {diff_hl_ic[1]:.1f}]')
axes[1].axvline(diff_hl_ic[1], color='#E74C3C', lw=1.5, ls='--')
axes[1].axvline(diff_hl_mean,  color='#2C3E50', lw=2,   ls='-',
                label=f'Media: {diff_hl_mean:.1f} pts')
axes[1].axvline(0, color='gray', lw=1, ls=':', alpha=0.6)
axes[1].fill_betweenx([0, 0.04], diff_hl_ic[0], diff_hl_ic[1],
                       alpha=0.15, color='#E74C3C')
axes[1].set_xlabel('μ_Low − μ_High (diferencia en puntos)')
axes[1].set_ylabel('Densidad')
axes[1].set_title(f'P(μ_Low > μ_High | datos) = {p_high_lt_low:.4f}')
axes[1].legend(fontsize=9)

plt.tight_layout()
fig.savefig(os.path.join(FIGURAS_DIR, 'fig7_comparacion_grupos.png'),
            bbox_inches='tight', dpi=150)
plt.close()
print("Figura 7 guardada.")

print("\n✅ Modelo Bayesiano Paso 1 completado.")
