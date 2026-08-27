"""
Modelo Bayesiano Paso 3 — Beta-Binomial (solución analítica + Monte Carlo)
==========================================================================
Estima y compara la proporción de consumidores con historial de pagos
tardíos (Late_Payment_History = Yes) entre grupos de Employment_Status.

Fundamento matemático:
  Verosimilitud:  X_k | π_k ~ Binomial(n_k, π_k)
  Prior:          π_k ~ Beta(α₀, β₀)    [para cada grupo k]
  Posterior:      π_k | datos ~ Beta(α₀ + X_k, β₀ + n_k - X_k)  [conjugado]

  Prior elegido: Beta(1, 1) = Uniforme(0, 1) — no informativo
  (refleja ausencia de conocimiento previo sobre las tasas por grupo)

Comparaciones bayesianas (Monte Carlo):
  P(π_Unemployed > π_Employed | datos)
  P(π_Freelancer > π_Employed | datos)
  P(π_Student    > π_Employed | datos)

Salidas:
  figuras/fig11_beta_posteriors.png
  figuras/fig12_comparaciones_proporciones.png
  analisis/tabla_beta_binomial.csv
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy import stats

# ── Configuración ─────────────────────────────────────────────────────────────
FIGURAS_DIR  = os.path.join(os.path.dirname(__file__), '..', 'figuras')
ANALISIS_DIR = os.path.join(os.path.dirname(__file__), '..', 'analisis')
os.makedirs(FIGURAS_DIR, exist_ok=True)

PALETTE = {
    'Employed':   '#3498DB',
    'Freelancer': '#E67E22',
    'Student':    '#9B59B6',
    'Unemployed': '#E74C3C',
}
plt.rcParams.update({'figure.dpi': 150, 'font.family': 'DejaVu Sans'})
SEED = 42
rng  = np.random.default_rng(SEED)

# ── Datos ─────────────────────────────────────────────────────────────────────
CSV = os.path.join(os.path.dirname(__file__), '..', 'BNPL_Financial_Default_Risk_Dataset.csv')
df = pd.read_csv(CSV)

GRUPOS = ['Employed', 'Freelancer', 'Student', 'Unemployed']

# ── Especificación del prior ───────────────────────────────────────────────────
# Beta(1, 1) = Uniforme(0, 1): no informativo sobre la tasa de pagos tardíos
ALPHA_0 = 1.0
BETA_0  = 1.0

print("=" * 60)
print("MODELO BAYESIANO PASO 3 — Beta-Binomial")
print("=" * 60)
print(f"\nPrior: π_k ~ Beta(α₀={ALPHA_0}, β₀={BETA_0}) = Uniforme(0,1)")
print("Justificación: sin conocimiento previo sobre la tasa de pagos tardíos")
print("por grupo de empleo → distribución uniforme sobre [0, 1].\n")

# ── Cálculo del posterior por grupo ───────────────────────────────────────────
posteriors_beta = {}
resultados_beta = []

for grupo in GRUPOS:
    mask = df['Employment_Status'] == grupo
    n_k = mask.sum()
    X_k = (df.loc[mask, 'Late_Payment_History'] == 'Yes').sum()

    # Parámetros del posterior (conjugado)
    alpha_n = ALPHA_0 + X_k
    beta_n  = BETA_0  + n_k - X_k

    # Estadísticas del posterior
    media_post  = alpha_n / (alpha_n + beta_n)
    moda_post   = (alpha_n - 1) / (alpha_n + beta_n - 2) if (alpha_n > 1 and beta_n > 1) else media_post
    varianza_post = (alpha_n * beta_n) / ((alpha_n + beta_n)**2 * (alpha_n + beta_n + 1))

    # IC 95% (igual cola)
    ic_low  = stats.beta.ppf(0.025, alpha_n, beta_n)
    ic_high = stats.beta.ppf(0.975, alpha_n, beta_n)

    posteriors_beta[grupo] = {
        'n': n_k, 'X': X_k, 'tasa_obs': X_k / n_k,
        'alpha_n': alpha_n, 'beta_n': beta_n,
        'media': media_post, 'moda': moda_post, 'var': varianza_post,
        'ic_low': ic_low, 'ic_high': ic_high
    }

    resultados_beta.append({
        'Grupo': grupo,
        'n': n_k,
        'Pagos tardíos (X)': X_k,
        'Tasa observada': round(X_k / n_k, 4),
        'α posterior': round(alpha_n, 1),
        'β posterior': round(beta_n, 1),
        'Media posterior': round(media_post, 4),
        'IC 95% inf.': round(ic_low, 4),
        'IC 95% sup.': round(ic_high, 4),
    })

    print(f"Grupo: {grupo}")
    print(f"  n={n_k:,}, X={X_k:,} (tasa obs.={X_k/n_k:.3f})")
    print(f"  Posterior: π ~ Beta({alpha_n:.0f}, {beta_n:.0f})")
    print(f"  Media posterior: {media_post:.4f}")
    print(f"  IC 95%: [{ic_low:.4f}, {ic_high:.4f}]")
    print()

tabla_beta = pd.DataFrame(resultados_beta)
tabla_beta.to_csv(os.path.join(ANALISIS_DIR, 'tabla_beta_binomial.csv'), index=False)
print("Tabla Beta-Binomial guardada.\n")


# ── Comparaciones bayesianas (Monte Carlo) ────────────────────────────────────
N_MC = 500_000
print("COMPARACIONES BAYESIANAS (Monte Carlo, N=500 000)")
print("Referencia: Employed\n")

muestras_mc = {}
for grupo in GRUPOS:
    p = posteriors_beta[grupo]
    muestras_mc[grupo] = rng.beta(p['alpha_n'], p['beta_n'], N_MC)

comparaciones = []
for grupo in ['Freelancer', 'Student', 'Unemployed']:
    diff = muestras_mc[grupo] - muestras_mc['Employed']
    prob  = np.mean(muestras_mc[grupo] > muestras_mc['Employed'])
    d_mean = diff.mean()
    d_ic   = np.percentile(diff, [2.5, 97.5])
    comparaciones.append({
        'Comparación': f'π_{grupo} > π_Employed',
        'Probabilidad': round(prob, 4),
        'Diferencia media': round(d_mean, 4),
        'IC 95% diferencia inf.': round(d_ic[0], 4),
        'IC 95% diferencia sup.': round(d_ic[1], 4),
    })
    print(f"  P(π_{grupo} > π_Employed | datos) = {prob:.4f}")
    print(f"  Diferencia media: {d_mean:.4f},  IC 95%: [{d_ic[0]:.4f}, {d_ic[1]:.4f}]")
    print()

pd.DataFrame(comparaciones).to_csv(
    os.path.join(ANALISIS_DIR, 'tabla_comparaciones_proporciones.csv'), index=False)


# ─────────────────────────────────────────────────────────────────────────────
# FIGURA 11 — Distribuciones posteriores de π_k
# ─────────────────────────────────────────────────────────────────────────────
x = np.linspace(0.10, 0.55, 1000)

fig, axes = plt.subplots(1, 4, figsize=(16, 4.5), sharey=False)
fig.suptitle('Distribuciones posteriores de la tasa de pagos tardíos por estado laboral',
             fontsize=12)

prior_y = stats.beta.pdf(x, ALPHA_0, BETA_0)  # Beta(1,1) = constante

for ax, grupo in zip(axes, GRUPOS):
    p = posteriors_beta[grupo]
    post_y = stats.beta.pdf(x, p['alpha_n'], p['beta_n'])

    ax.fill_between(x, post_y, alpha=0.35, color=PALETTE[grupo])
    ax.plot(x, post_y, color=PALETTE[grupo], lw=2.5,
            label=f"Posterior\nπ ~ Beta({p['alpha_n']:.0f},{p['beta_n']:.0f})")

    # Prior (muy plano, escalar para visibilidad)
    prior_scaled = np.ones_like(x) * post_y.max() * 0.12
    ax.axhline(prior_scaled[0], color='gray', lw=1.2, ls='--', label='Prior Unif(0,1)')

    # IC 95%
    ax.axvline(p['ic_low'],  color=PALETTE[grupo], lw=1, ls='-.')
    ax.axvline(p['ic_high'], color=PALETTE[grupo], lw=1, ls='-.',
               label=f"IC 95%\n[{p['ic_low']:.3f},{p['ic_high']:.3f}]")
    ax.axvline(p['media'], color='#2C3E50', lw=1.5, ls='--',
               label=f"μ={p['media']:.3f}")

    ax.set_title(f'{grupo}\n(n={p["n"]:,}, X={p["X"]:,})', fontsize=10)
    ax.set_xlabel('π_k (tasa pagos tardíos)', fontsize=9)
    ax.set_ylabel('Densidad posterior', fontsize=8)
    ax.legend(fontsize=7.5, framealpha=0.6)

plt.tight_layout()
fig.savefig(os.path.join(FIGURAS_DIR, 'fig11_beta_posteriors.png'),
            bbox_inches='tight', dpi=150)
plt.close()
print("Figura 11 guardada.")


# ─────────────────────────────────────────────────────────────────────────────
# FIGURA 12 — Distribuciones de diferencias (π_k − π_Employed)
# ─────────────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(14, 4.5))
fig.suptitle('Distribuciones posteriores de la diferencia (π_k − π_Employed)',
             fontsize=12)

grupos_comp = ['Freelancer', 'Student', 'Unemployed']
for ax, grupo in zip(axes, grupos_comp):
    diff = muestras_mc[grupo] - muestras_mc['Employed']
    prob  = np.mean(diff > 0)
    d_ic  = np.percentile(diff, [2.5, 97.5])

    ax.hist(diff, bins=70, color=PALETTE[grupo], alpha=0.7,
            edgecolor='white', linewidth=0.3, density=True)
    ax.axvline(0, color='gray', lw=1.5, ls='--', alpha=0.8)
    ax.axvline(diff.mean(), color='#2C3E50', lw=2, ls='-',
               label=f'Media: {diff.mean():.4f}')
    ax.axvline(d_ic[0], color=PALETTE[grupo], lw=1.2, ls='-.',
               label=f'IC 95%: [{d_ic[0]:.3f}, {d_ic[1]:.3f}]')
    ax.axvline(d_ic[1], color=PALETTE[grupo], lw=1.2, ls='-.')

    # Sombrear región > 0
    hist_data = np.histogram(diff, bins=70, density=True)
    bin_centers = (hist_data[1][:-1] + hist_data[1][1:]) / 2
    mask_pos = bin_centers > 0
    ax.fill_between(bin_centers[mask_pos],
                    np.zeros(mask_pos.sum()),
                    hist_data[0][mask_pos],
                    alpha=0.35, color='#E74C3C',
                    label=f'P(π_{grupo}>π_Emp) = {prob:.4f}')

    ax.set_title(f'π_{grupo} − π_Employed', fontsize=10)
    ax.set_xlabel('Diferencia en tasa de pagos tardíos', fontsize=9)
    ax.set_ylabel('Densidad', fontsize=9)
    ax.legend(fontsize=7.5)

plt.tight_layout()
fig.savefig(os.path.join(FIGURAS_DIR, 'fig12_comparaciones_proporciones.png'),
            bbox_inches='tight', dpi=150)
plt.close()
print("Figura 12 guardada.")

print("\n✅ Modelo Bayesiano Paso 3 completado.")
