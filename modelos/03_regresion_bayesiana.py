"""
Modelo Bayesiano Paso 2 — Regresión Lineal Bayesiana con MCMC
=============================================================
Modela Credit_Score en función de variables demográficas, laborales
y de comportamiento financiero usando PyMC (MCMC - NUTS sampler).

Modelo:
  Credit_Score_i ~ Normal(μᵢ, σ²)
  μᵢ = β₀ + β₁·Income_USD_std + β₂·Age_std
       + β₃·Total_BNPL_Active_Loans_std
       + β₄·Average_Transaction_Value_USD_std
       + β₅·Late_Payment_History
       + γ_Employment  (efectos de grupo)

Priors débilmente informativos:
  β₀ ~ Normal(650, 100)       [intercepto: media general del Credit Score]
  βⱼ ~ Normal(0, 50)          [coeficientes: ±100 puntos al 95% en escala std]
  σ  ~ HalfNormal(80)         [dispersión: prior difuso sobre la variabilidad]

Nota: Default_Risk NO se incluye como predictor (ver plan metodológico §4).

Salidas:
  figuras/fig8_trazas_mcmc.png
  figuras/fig9_forest_plot_coeficientes.png
  figuras/fig10_posterior_predictive.png
  analisis/tabla_coeficientes_regresion.csv
  modelos/modelo_regresion_trace.nc   (ArviZ InferenceData)
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import pymc as pm
import arviz as az
from scipy import stats

# ── Configuración ─────────────────────────────────────────────────────────────
FIGURAS_DIR  = os.path.join(os.path.dirname(__file__), '..', 'figuras')
ANALISIS_DIR = os.path.join(os.path.dirname(__file__), '..', 'analisis')
MODELOS_DIR  = os.path.dirname(__file__)
os.makedirs(FIGURAS_DIR, exist_ok=True)

plt.rcParams.update({'figure.dpi': 150, 'font.family': 'DejaVu Sans'})
SEED = 42

# ── Carga y preprocesamiento ───────────────────────────────────────────────────
CSV = os.path.join(os.path.dirname(__file__), '..', 'BNPL_Financial_Default_Risk_Dataset.csv')
df_raw = pd.read_csv(CSV)

# Estrategia de valores faltantes: análisis de casos completos
# (Income_USD: 305 NA, Credit_Score: 298 NA → <3.2%, asumimos MCAR)
df = df_raw.dropna(subset=['Credit_Score', 'Income_USD']).copy()
print(f"Casos completos para regresión: {len(df):,} (perdidos: {len(df_raw) - len(df):,})")

# Codificación de variables
# Employment_Status: variables dummy (referencia = Employed)
df['emp_Student']    = (df['Employment_Status'] == 'Student').astype(float)
df['emp_Freelancer'] = (df['Employment_Status'] == 'Freelancer').astype(float)
df['emp_Unemployed'] = (df['Employment_Status'] == 'Unemployed').astype(float)

# Late_Payment_History: 1 = Yes, 0 = No
df['late_payment'] = (df['Late_Payment_History'] == 'Yes').astype(float)

# Estandarización de variables continuas (z-score) para priors en escala común
def standardize(series):
    return (series - series.mean()) / series.std()

df['Income_std']   = standardize(df['Income_USD'])
df['Age_std']      = standardize(df['Age'])
df['Loans_std']    = standardize(df['Total_BNPL_Active_Loans'])
df['AvgTx_std']    = standardize(df['Average_Transaction_Value_USD'])

# Arrays numpy para PyMC
y       = df['Credit_Score'].values
X_income   = df['Income_std'].values
X_age      = df['Age_std'].values
X_loans    = df['Loans_std'].values
X_avgtx    = df['AvgTx_std'].values
X_late     = df['late_payment'].values
X_student  = df['emp_Student'].values
X_freelance= df['emp_Freelancer'].values
X_unemployed= df['emp_Unemployed'].values

n = len(y)
print(f"n = {n:,},  Var. respuesta: Credit_Score  [min={y.min()}, max={y.max()}, mean={y.mean():.1f}]")

# ── Especificación del modelo en PyMC ─────────────────────────────────────────
print("\nEspecificando modelo en PyMC...")
with pm.Model() as modelo_regresion:

    # --- Priors ---
    beta_0         = pm.Normal('beta_0',      mu=650,  sigma=100)   # intercepto
    beta_income    = pm.Normal('beta_income', mu=0,    sigma=50)    # ingreso (std)
    beta_age       = pm.Normal('beta_age',    mu=0,    sigma=50)    # edad (std)
    beta_loans     = pm.Normal('beta_loans',  mu=0,    sigma=50)    # préstamos (std)
    beta_avgtx     = pm.Normal('beta_avgtx',  mu=0,    sigma=50)    # val. transacción (std)
    beta_late      = pm.Normal('beta_late',   mu=0,    sigma=50)    # pago tardío (binaria)
    beta_student   = pm.Normal('beta_student',   mu=0, sigma=50)    # vs. Employed
    beta_freelance = pm.Normal('beta_freelance',  mu=0, sigma=50)
    beta_unemployed= pm.Normal('beta_unemployed', mu=0, sigma=50)

    sigma = pm.HalfNormal('sigma', sigma=80)

    # --- Función de enlace (media del posterior) ---
    mu = (beta_0
          + beta_income    * X_income
          + beta_age       * X_age
          + beta_loans     * X_loans
          + beta_avgtx     * X_avgtx
          + beta_late      * X_late
          + beta_student   * X_student
          + beta_freelance * X_freelance
          + beta_unemployed* X_unemployed)

    # --- Verosimilitud ---
    y_obs = pm.Normal('y_obs', mu=mu, sigma=sigma, observed=y)

    # --- Muestreo MCMC (NUTS) ---
    # En Windows, PyMC requiere cores=1 cuando se ejecuta como script
    # (el multiprocessing necesita el guard __main__, que no aplica en scripts directos)
    print("\nIniciando MCMC (NUTS)...")
    print("Configuracion: 4 cadenas, 1000 tune + 1000 draw (cores=1 para compatibilidad Windows)")
    idata = pm.sample(
        draws=1000,
        tune=1000,
        chains=4,
        cores=1,           # Windows: evita error de multiprocessing bootstrap
        random_seed=SEED,
        target_accept=0.92,
        return_inferencedata=True,
        progressbar=True
    )

    # --- Posterior predictive check ---
    pm.sample_posterior_predictive(idata, extend_inferencedata=True, random_seed=SEED)

# ── Diagnóstico de convergencia ───────────────────────────────────────────────
print("\n" + "=" * 60)
print("DIAGNÓSTICO DE CONVERGENCIA")
print("=" * 60)

summary = az.summary(idata, var_names=[
    'beta_0', 'beta_income', 'beta_age', 'beta_loans',
    'beta_avgtx', 'beta_late', 'beta_student', 'beta_freelance',
    'beta_unemployed', 'sigma'
], round_to=4)

print(summary.to_string())

r_hat_max = summary['r_hat'].max()
ess_bulk_min = summary['ess_bulk'].min()
print(f"\nR̂ máximo: {r_hat_max:.4f}  (criterio convergencia: < 1.01)")
print(f"ESS bulk mínimo: {ess_bulk_min:.0f}  (criterio: > 400)")

if r_hat_max < 1.01:
    print("✅ Convergencia alcanzada (R̂ < 1.01)")
else:
    print("⚠️  Advertencia: R̂ fuera de rango. Revisar trazas.")


# ── Tabla de coeficientes para el informe ─────────────────────────────────────
PARAM_LABELS = {
    'beta_0':          'Intercepto (β₀)',
    'beta_income':     'Ingreso anual (estandarizado)',
    'beta_age':        'Edad (estandarizada)',
    'beta_loans':      'Préstamos BNPL activos (std)',
    'beta_avgtx':      'Valor prom. transacción (std)',
    'beta_late':       'Historial pago tardío (Sí=1)',
    'beta_student':    'Estado: Student (vs. Employed)',
    'beta_freelance':  'Estado: Freelancer (vs. Employed)',
    'beta_unemployed': 'Estado: Unemployed (vs. Employed)',
    'sigma':           'Desv. típica residual (σ)',
}

coef_rows = []
for var, label in PARAM_LABELS.items():
    post = idata.posterior[var].values.flatten()
    mean_val = post.mean()
    std_val  = post.std()
    ic_low   = np.percentile(post, 2.5)
    ic_high  = np.percentile(post, 97.5)
    r_hat    = float(summary.loc[var, 'r_hat']) if var in summary.index else np.nan
    coef_rows.append({
        'Parámetro': label,
        'Media posterior': round(mean_val, 3),
        'Std posterior':   round(std_val, 3),
        'IC 95% inf.':     round(ic_low, 3),
        'IC 95% sup.':     round(ic_high, 3),
        'R̂':               round(r_hat, 4)
    })

tabla_coef = pd.DataFrame(coef_rows)
tabla_coef.to_csv(os.path.join(ANALISIS_DIR, 'tabla_coeficientes_regresion.csv'), index=False)
print("\nTabla de coeficientes guardada.")
print(tabla_coef.to_string(index=False))


# ── Guardar trace ─────────────────────────────────────────────────────────────
try:
    idata.to_netcdf(os.path.join(MODELOS_DIR, 'modelo_regresion_trace.nc'))
    print("\nTrace guardado (modelo_regresion_trace.nc).")
except Exception as e:
    print(f"\nAviso: no se pudo guardar el trace en NetCDF4 ({e}).")
    print("Los coeficientes ya estan guardados en analisis/tabla_coeficientes_regresion.csv")


# ─────────────────────────────────────────────────────────────────────────────
# FIGURA 8 — Trazas MCMC (subset de parámetros clave) — matplotlib manual
# ─────────────────────────────────────────────────────────────────────────────
params_trazas = ['beta_income', 'beta_late', 'beta_unemployed', 'sigma']
labels_trazas = ['Ingreso (std)', 'Pago tardio', 'Desempleado', 'sigma']
cadena_colors = ['#3498DB', '#E74C3C', '#2ECC71', '#9B59B6']

fig, axes = plt.subplots(len(params_trazas), 2, figsize=(12, 9))
fig.suptitle('Trazas MCMC — Parametros clave del modelo de regresion', fontsize=12)

for row, (param, label) in enumerate(zip(params_trazas, labels_trazas)):
    n_chains = idata.posterior.dims['chain']
    n_draws  = idata.posterior.dims['draw']
    all_samples = []
    for c in range(n_chains):
        chain_samples = idata.posterior[param].values[c]
        color = cadena_colors[c % len(cadena_colors)]
        axes[row, 0].plot(chain_samples, color=color, alpha=0.7, lw=0.8,
                          label=f'Cadena {c+1}')
        all_samples.append(chain_samples)
    axes[row, 0].set_title(f'Traza: {label}', fontsize=9)
    axes[row, 0].set_xlabel('Iteracion')
    axes[row, 0].set_ylabel(param)
    if row == 0:
        axes[row, 0].legend(fontsize=7)

    combined = np.concatenate(all_samples)
    for c, (samp, col) in enumerate(zip(all_samples, cadena_colors)):
        axes[row, 1].hist(samp, bins=40, color=col, alpha=0.5, density=True)
    axes[row, 1].set_title(f'Posterior: {label}', fontsize=9)
    axes[row, 1].set_xlabel('Valor del parametro')
    axes[row, 1].axvline(combined.mean(), color='#2C3E50', lw=1.5, ls='--',
                          label=f'Media={combined.mean():.2f}')
    axes[row, 1].legend(fontsize=7)

plt.tight_layout()
plt.savefig(os.path.join(FIGURAS_DIR, 'fig8_trazas_mcmc.png'),
            bbox_inches='tight', dpi=150)
plt.close()
print("Figura 8 guardada.")



# ─────────────────────────────────────────────────────────────────────────────
# FIGURA 9 — Forest plot de coeficientes
# ─────────────────────────────────────────────────────────────────────────────
params_forest = ['beta_income', 'beta_age', 'beta_loans', 'beta_avgtx',
                 'beta_late', 'beta_student', 'beta_freelance', 'beta_unemployed']
labels_forest = [
    'Ingreso anual (std)',
    'Edad (std)',
    'Préstamos activos (std)',
    'Val. transacción (std)',
    'Pago tardío (Sí)',
    'Empleo: Student',
    'Empleo: Freelancer',
    'Empleo: Desempleado',
]

fig, ax = plt.subplots(figsize=(9, 6))
ax.axvline(0, color='gray', lw=1, ls='--', alpha=0.7)

colors = []
for i, (param, label) in enumerate(zip(params_forest, labels_forest)):
    post = idata.posterior[param].values.flatten()
    m    = post.mean()
    ic_l = np.percentile(post, 2.5)
    ic_h = np.percentile(post, 97.5)
    ic_25= np.percentile(post, 25)
    ic_75= np.percentile(post, 75)
    color = '#E74C3C' if ic_h < 0 else ('#2ECC71' if ic_l > 0 else '#7F8C8D')
    ax.errorbar(m, i, xerr=[[m - ic_l], [ic_h - m]],
                fmt='o', color=color, capsize=4, capthick=1.5,
                elinewidth=1.5, markersize=7, zorder=3)
    # IQR
    ax.plot([ic_25, ic_75], [i, i], color=color, lw=5, alpha=0.4, zorder=2)
    ax.text(ic_h + 0.5, i, f'{m:.1f} [{ic_l:.1f}, {ic_h:.1f}]',
            va='center', fontsize=8.5)

ax.set_yticks(range(len(labels_forest)))
ax.set_yticklabels(labels_forest, fontsize=10)
ax.set_xlabel('Efecto sobre Credit Score (puntos)', fontsize=10)
ax.set_title('Coeficientes bayesianos — IC 95% y IQR\n(referencia: Employed, sin pago tardío)', fontsize=11)
ax.set_xlim(ax.get_xlim()[0], ax.get_xlim()[1] * 1.4)

patches = [
    mpatches.Patch(color='#2ECC71', label='Efecto positivo significativo'),
    mpatches.Patch(color='#E74C3C', label='Efecto negativo significativo'),
    mpatches.Patch(color='#7F8C8D', label='IC incluye 0'),
]
ax.legend(handles=patches, loc='lower right', fontsize=8)
plt.tight_layout()
fig.savefig(os.path.join(FIGURAS_DIR, 'fig9_forest_plot_coeficientes.png'),
            bbox_inches='tight', dpi=150)
plt.close()
print("Figura 9 guardada.")


# ─────────────────────────────────────────────────────────────────────────────
# FIGURA 10 — Posterior Predictive Check (manual, sin az.plot_ppc)
# ─────────────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(9, 5))

# Muestras de la distribucion predictiva posterior
ppc_samples = idata.posterior_predictive['y_obs'].values  # shape (chains, draws, n_obs)
ppc_flat = ppc_samples.reshape(-1, ppc_samples.shape[-1])  # (chains*draws, n_obs)

# Graficar 200 replicas (KDE suavizado con histograma)
rng_ppc = np.random.default_rng(42)
idx_plot = rng_ppc.choice(ppc_flat.shape[0], size=200, replace=False)
for i in idx_plot:
    ax.hist(ppc_flat[i], bins=60, density=True,
            color='lightgray', alpha=0.05, histtype='step', lw=0.5)

# KDE de las replicas (media del PPC)
ppc_means = ppc_flat.mean(axis=1)  # media de cada replica
from scipy.stats import gaussian_kde
kde_ppc = gaussian_kde(ppc_flat.mean(axis=0))
x_vals = np.linspace(300, 850, 300)
ax.plot(x_vals, kde_ppc(x_vals), color='steelblue', lw=2.5, ls='--',
        label='Media predictiva posterior')

# Distribucion observada
ax.hist(y, bins=60, density=True, color='#2C3E50', alpha=0.4,
        label='Datos observados', histtype='bar')

ax.set_title('Posterior Predictive Check — Credit Score\n(gris: replicas del modelo; negro: datos observados)',
             fontsize=11)
ax.set_xlabel('Credit Score')
ax.set_ylabel('Densidad')
ax.legend(fontsize=9)
plt.tight_layout()
plt.savefig(os.path.join(FIGURAS_DIR, 'fig10_posterior_predictive.png'),
            bbox_inches='tight', dpi=150)
plt.close()
print("Figura 10 guardada.")


# ── Predicción para perfil hipotético ────────────────────────────────────────
print("\n" + "=" * 60)
print("PREDICCIÓN BAYESIANA — Perfil hipotético de consumidor")
print("=" * 60)

# Perfiles a evaluar
income_mean = df['Income_USD'].mean()
income_std_val = df['Income_USD'].std()
age_mean = df['Age'].mean()
age_std_val = df['Age'].std()
loans_mean = df['Total_BNPL_Active_Loans'].mean()
loans_std_val = df['Total_BNPL_Active_Loans'].std()
avgtx_mean = df['Average_Transaction_Value_USD'].mean()
avgtx_std_val = df['Average_Transaction_Value_USD'].std()

perfiles = [
    {'nombre': 'Empleado sin riesgo',
     'income': 75000, 'age': 35, 'loans': 1, 'avgtx': 200,
     'late': 0, 'student': 0, 'freelance': 0, 'unemployed': 0},
    {'nombre': 'Desempleado con pagos tardíos',
     'income': 15000, 'age': 27, 'loans': 4, 'avgtx': 150,
     'late': 1, 'student': 0, 'freelance': 0, 'unemployed': 1},
    {'nombre': 'Estudiante típico',
     'income': 12000, 'age': 22, 'loans': 2, 'avgtx': 100,
     'late': 0, 'student': 1, 'freelance': 0, 'unemployed': 0},
]

# Extraer muestras del posterior
samples_b0    = idata.posterior['beta_0'].values.flatten()
samples_binc  = idata.posterior['beta_income'].values.flatten()
samples_bage  = idata.posterior['beta_age'].values.flatten()
samples_bloans= idata.posterior['beta_loans'].values.flatten()
samples_bav   = idata.posterior['beta_avgtx'].values.flatten()
samples_blate = idata.posterior['beta_late'].values.flatten()
samples_bst   = idata.posterior['beta_student'].values.flatten()
samples_bfr   = idata.posterior['beta_freelance'].values.flatten()
samples_bun   = idata.posterior['beta_unemployed'].values.flatten()
samples_sig   = idata.posterior['sigma'].values.flatten()

for p in perfiles:
    inc_s  = (p['income'] - income_mean) / income_std_val
    age_s  = (p['age']    - age_mean)    / age_std_val
    loan_s = (p['loans']  - loans_mean)  / loans_std_val
    av_s   = (p['avgtx']  - avgtx_mean)  / avgtx_std_val

    mu_pred = (samples_b0 + samples_binc*inc_s + samples_bage*age_s
               + samples_bloans*loan_s + samples_bav*av_s
               + samples_blate*p['late'] + samples_bst*p['student']
               + samples_bfr*p['freelance'] + samples_bun*p['unemployed'])
    y_pred  = np.random.normal(mu_pred, samples_sig)

    print(f"\nPerfil: {p['nombre']}")
    print(f"  Income=${p['income']:,}, Age={p['age']}, Loans={p['loans']}, Late={p['late']}")
    print(f"  Credit Score predicho: media={mu_pred.mean():.1f}, "
          f"IC 95%=[{np.percentile(y_pred,2.5):.0f}, {np.percentile(y_pred,97.5):.0f}]")

print("\n✅ Modelo Bayesiano Paso 2 completado.")
