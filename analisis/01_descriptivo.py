"""
Análisis Descriptivo — Proyecto Bayesiano BNPL
===============================================
Genera todas las tablas y figuras para la sección de Análisis Descriptivo
del informe (máximo 3 páginas).

Salidas:
  figuras/fig1_distribuciones_continuas.png
  figuras/fig2_categoricas.png
  figuras/fig3_credit_score_por_riesgo.png
  figuras/fig4_correlaciones.png
  figuras/fig5_income_por_riesgo.png
  analisis/tabla_descriptiva.csv
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from scipy import stats

# ── Configuración visual ──────────────────────────────────────────────────────
PALETTE_RIESGO = {"Low": "#2ECC71", "Medium": "#F39C12", "High": "#E74C3C"}
PALETTE_EMPLEO = {"Employed": "#3498DB", "Student": "#9B59B6",
                  "Freelancer": "#E67E22", "Unemployed": "#E74C3C"}
FIGURAS_DIR = os.path.join(os.path.dirname(__file__), '..', 'figuras')
os.makedirs(FIGURAS_DIR, exist_ok=True)

sns.set_theme(style="whitegrid", font_scale=1.1)
plt.rcParams.update({
    'font.family': 'DejaVu Sans',
    'axes.titleweight': 'bold',
    'figure.dpi': 150,
})

# ── Carga y limpieza ──────────────────────────────────────────────────────────
CSV = os.path.join(os.path.dirname(__file__), '..', 'BNPL_Financial_Default_Risk_Dataset.csv')
df = pd.read_csv(CSV)

# Tipos correctos
df['Default_Risk'] = pd.Categorical(df['Default_Risk'], categories=['Low', 'Medium', 'High'], ordered=True)
df['Employment_Status'] = pd.Categorical(df['Employment_Status'],
    categories=['Employed', 'Freelancer', 'Student', 'Unemployed'], ordered=False)
df['Late_Payment_History'] = df['Late_Payment_History'].map({'Yes': 1, 'No': 0})

N = len(df)
print(f"Dataset cargado: {N:,} observaciones, {df.shape[1]} variables")
print(f"Valores faltantes:\n{df.isnull().sum()[df.isnull().sum() > 0]}")


# ── Tabla de estadísticas descriptivas ───────────────────────────────────────
NUM_COLS = ['Age', 'Income_USD', 'Credit_Score',
            'Total_BNPL_Active_Loans', 'Total_BNPL_Debt_USD',
            'Average_Transaction_Value_USD']

desc = df[NUM_COLS].describe(percentiles=[.25, .5, .75]).T
desc['skew'] = df[NUM_COLS].skew()
desc['missing'] = df[NUM_COLS].isnull().sum()
desc['missing_%'] = (desc['missing'] / N * 100).round(2)
desc = desc[['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max', 'skew', 'missing', 'missing_%']]
desc.columns = ['n', 'Media', 'Std', 'Mín', 'Q1', 'Mediana', 'Q3', 'Máx', 'Sesgo', 'Faltantes', 'Faltantes_%']
desc = desc.round(2)
desc.to_csv(os.path.join(os.path.dirname(__file__), 'tabla_descriptiva.csv'))
print("\nTabla descriptiva guardada.")
print(desc.to_string())


# ─────────────────────────────────────────────────────────────────────────────
# FIGURA 1 — Distribuciones de variables continuas
# ─────────────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(2, 3, figsize=(14, 8))
fig.suptitle('Distribuciones de Variables Cuantitativas', fontsize=14, y=1.01)

configs = [
    ('Age',                       'Edad (años)',            '#5B8DB8'),
    ('Income_USD',                'Ingreso anual (USD)',     '#5BA85E'),
    ('Credit_Score',              'Puntaje crediticio',      '#C45B5B'),
    ('Total_BNPL_Active_Loans',   'Préstamos BNPL activos',  '#B07EC4'),
    ('Total_BNPL_Debt_USD',       'Deuda BNPL total (USD)',  '#C47B5B'),
    ('Average_Transaction_Value_USD', 'Valor prom. transacción (USD)', '#5BA89E'),
]

for ax, (col, label, color) in zip(axes.flat, configs):
    data = df[col].dropna()
    ax.hist(data, bins=35, color=color, alpha=0.75, edgecolor='white', linewidth=0.4)
    ax.axvline(data.mean(),   color='#2C3E50', lw=1.8, ls='--', label=f'Media: {data.mean():.1f}')
    ax.axvline(data.median(), color='#7F8C8D', lw=1.4, ls=':',  label=f'Mediana: {data.median():.1f}')
    ax.set_xlabel(label, fontsize=10)
    ax.set_ylabel('Frecuencia', fontsize=9)
    ax.legend(fontsize=8, framealpha=0.6)
    skew_val = stats.skew(data)
    ax.set_title(f'{label}\n(sesgo = {skew_val:.2f})', fontsize=10)

plt.tight_layout()
fig.savefig(os.path.join(FIGURAS_DIR, 'fig1_distribuciones_continuas.png'),
            bbox_inches='tight', dpi=150)
plt.close()
print("Figura 1 guardada.")


# ─────────────────────────────────────────────────────────────────────────────
# FIGURA 2 — Variables categóricas
# ─────────────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(14, 5))
fig.suptitle('Distribución de Variables Categóricas', fontsize=14)

# Default_Risk
dr_counts = df['Default_Risk'].value_counts().reindex(['Low', 'Medium', 'High'])
colors_dr = [PALETTE_RIESGO[c] for c in dr_counts.index]
bars = axes[0].bar(dr_counts.index, dr_counts.values, color=colors_dr, edgecolor='white', linewidth=0.5)
axes[0].set_title('Nivel de Riesgo de Incumplimiento')
axes[0].set_ylabel('Frecuencia')
for bar, v in zip(bars, dr_counts.values):
    axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50,
                 f'{v/N*100:.1f}%', ha='center', va='bottom', fontsize=9)

# Employment_Status
es_counts = df['Employment_Status'].value_counts()
colors_es = [PALETTE_EMPLEO.get(c, '#888') for c in es_counts.index]
bars2 = axes[1].bar(es_counts.index, es_counts.values, color=colors_es, edgecolor='white', linewidth=0.5)
axes[1].set_title('Estado Laboral')
axes[1].set_ylabel('Frecuencia')
axes[1].tick_params(axis='x', rotation=15)
for bar, v in zip(bars2, es_counts.values):
    axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 30,
                 f'{v/N*100:.1f}%', ha='center', va='bottom', fontsize=9)

# Shopping_Category
sc_counts = df['Shopping_Category_Most_Frequent'].value_counts()
axes[2].barh(sc_counts.index, sc_counts.values, color='#6BAED6', edgecolor='white', linewidth=0.5)
axes[2].set_title('Categoría de Compra Más Frecuente')
axes[2].set_xlabel('Frecuencia')
for i, (v, label) in enumerate(zip(sc_counts.values, sc_counts.index)):
    axes[2].text(v + 20, i, f'{v/N*100:.1f}%', va='center', fontsize=9)

plt.tight_layout()
fig.savefig(os.path.join(FIGURAS_DIR, 'fig2_categoricas.png'),
            bbox_inches='tight', dpi=150)
plt.close()
print("Figura 2 guardada.")


# ─────────────────────────────────────────────────────────────────────────────
# FIGURA 3 — Credit_Score por grupo de Default_Risk (violin + boxplot)
# ─────────────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))
fig.suptitle('Credit_Score según Nivel de Riesgo de Incumplimiento', fontsize=13)

orden = ['Low', 'Medium', 'High']
palette = [PALETTE_RIESGO[g] for g in orden]

# Violin
sns.violinplot(data=df, x='Default_Risk', y='Credit_Score', order=orden,
               hue='Default_Risk', palette=palette, inner='quartile',
               ax=axes[0], cut=0, legend=False)
axes[0].set_title('Distribucion (violin + cuartiles)')
axes[0].set_xlabel('Nivel de riesgo')
axes[0].set_ylabel('Puntaje crediticio')

# Añadir medias como puntos
medias = df.groupby('Default_Risk', observed=True)['Credit_Score'].mean()
for i, g in enumerate(orden):
    if g in medias.index:
        axes[0].scatter(i, medias[g], color='white', s=60, zorder=5, edgecolors='black', linewidth=1.2)

# Boxplot con puntos de media
sns.boxplot(data=df, x='Default_Risk', y='Credit_Score', order=orden,
            hue='Default_Risk', palette=palette, width=0.5, fliersize=2,
            ax=axes[1], legend=False)
sns.stripplot(data=df.sample(600, random_state=42), x='Default_Risk', y='Credit_Score',
              order=orden, color='#2C3E50', alpha=0.15, size=2, jitter=True, ax=axes[1])
axes[1].set_title('Boxplot con muestra de puntos')
axes[1].set_xlabel('Nivel de riesgo')
axes[1].set_ylabel('Puntaje crediticio')

# Anotar medias
for i, g in enumerate(orden):
    data_g = df.loc[df['Default_Risk'] == g, 'Credit_Score'].dropna()
    m = data_g.mean()
    axes[1].text(i, m + 8, f'μ={m:.0f}', ha='center', fontsize=9,
                 color='#2C3E50', fontweight='bold')

plt.tight_layout()
fig.savefig(os.path.join(FIGURAS_DIR, 'fig3_credit_score_por_riesgo.png'),
            bbox_inches='tight', dpi=150)
plt.close()
print("Figura 3 guardada.")


# ─────────────────────────────────────────────────────────────────────────────
# FIGURA 4 — Mapa de calor de correlaciones
# ─────────────────────────────────────────────────────────────────────────────
df_corr = df.copy()
df_corr['Default_Risk_num'] = df['Default_Risk'].cat.codes  # Low=0,Med=1,High=2
df_corr['Late_Payment'] = df['Late_Payment_History']        # ya codificado 0/1
corr_cols = ['Credit_Score', 'Income_USD', 'Age',
             'Total_BNPL_Active_Loans', 'Total_BNPL_Debt_USD',
             'Average_Transaction_Value_USD', 'Late_Payment', 'Default_Risk_num']
labels = ['Credit Score', 'Ingreso (USD)', 'Edad',
          'Préstamos activos', 'Deuda BNPL (USD)',
          'Val. transacción', 'Pago tardío', 'Riesgo (ord.)']

corr_matrix = df_corr[corr_cols].corr(numeric_only=True)

fig, ax = plt.subplots(figsize=(9, 7))
mask = np.triu(np.ones_like(corr_matrix, dtype=bool), k=1)
sns.heatmap(corr_matrix, mask=mask, annot=True, fmt='.2f', cmap='RdBu_r',
            center=0, vmin=-1, vmax=1, linewidths=0.5, linecolor='white',
            xticklabels=labels, yticklabels=labels, ax=ax, annot_kws={'size': 9})
ax.set_title('Matriz de correlaciones de Pearson (triángulo inferior)', fontsize=12)
plt.tight_layout()
fig.savefig(os.path.join(FIGURAS_DIR, 'fig4_correlaciones.png'),
            bbox_inches='tight', dpi=150)
plt.close()
print("Figura 4 guardada.")


# ─────────────────────────────────────────────────────────────────────────────
# FIGURA 5 — Income_USD por riesgo y Late_Payment por Employment_Status
# ─────────────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
fig.suptitle('Variables Clave por Grupo de Riesgo y Estado Laboral', fontsize=13)

# Income por Default_Risk
sns.boxplot(data=df, x='Default_Risk', y='Income_USD', order=orden,
            hue='Default_Risk', palette=palette, width=0.5, fliersize=2,
            ax=axes[0], legend=False)
axes[0].set_title('Ingreso anual por nivel de riesgo')
axes[0].set_xlabel('Nivel de riesgo')
axes[0].set_ylabel('Ingreso (USD)')
medias_income = df.groupby('Default_Risk', observed=True)['Income_USD'].mean()
for i, g in enumerate(orden):
    if g in medias_income.index:
        m = medias_income[g]
        axes[0].text(i, m + 800, f'μ={m/1000:.0f}k', ha='center', fontsize=9,
                     color='#2C3E50', fontweight='bold')

# Tasa de pagos tardíos por Employment_Status
late_rate = (df.groupby('Employment_Status', observed=True)['Late_Payment_History']
             .mean().reindex(['Employed', 'Freelancer', 'Student', 'Unemployed']) * 100)
colors_bar = [PALETTE_EMPLEO[c] for c in late_rate.index]
bars = axes[1].bar(late_rate.index, late_rate.values, color=colors_bar,
                    edgecolor='white', linewidth=0.5)
axes[1].set_title('Tasa de pagos tardíos por estado laboral')
axes[1].set_xlabel('Estado laboral')
axes[1].set_ylabel('% con historial de pago tardío')
axes[1].set_ylim(0, late_rate.max() * 1.25)
for bar, v in zip(bars, late_rate.values):
    axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                 f'{v:.1f}%', ha='center', va='bottom', fontsize=9)

plt.tight_layout()
fig.savefig(os.path.join(FIGURAS_DIR, 'fig5_income_y_late_payment.png'),
            bbox_inches='tight', dpi=150)
plt.close()
print("Figura 5 guardada.")

print("\nAnalisis descriptivo completado. Todas las figuras guardadas en /figuras/")
