"""
Dashboard Interactivo — Proyecto Bayesiano BNPL
===============================================
Aplicación Streamlit con 5 paneles:
  1. Panorama general (KPIs)
  2. Perfil del consumidor (filtros interactivos)
  3. Análisis bayesiano — Credit Score por grupo de riesgo
  4. Comparación de proporciones (Late Payment por empleo)
  5. Regresión bayesiana (coeficientes + predictor interactivo)

Ejecución:
  streamlit run dashboard/app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats
import os, sys

# ── Configuración de la página ────────────────────────────────────────────────
st.set_page_config(
    page_title="BNPL Default Risk — Análisis Bayesiano",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS personalizado ─────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Fuente y paleta general */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* Header principal */
    .main-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        padding: 2rem 2.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        color: white;
    }
    .main-header h1 { font-size: 1.8rem; font-weight: 700; margin: 0; }
    .main-header p  { font-size: 0.95rem; opacity: 0.8; margin-top: 0.4rem; }

    /* Tarjetas KPI */
    .kpi-card {
        background: linear-gradient(135deg, #1e3a5f, #0d2137);
        border: 1px solid rgba(100,160,255,0.25);
        border-radius: 10px;
        padding: 1.2rem 1rem;
        text-align: center;
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .kpi-value  { font-size: 2rem; font-weight: 700; color: #64b5f6; }
    .kpi-label  { font-size: 0.82rem; opacity: 0.75; margin-top: 0.3rem; }
    .kpi-delta  { font-size: 0.75rem; margin-top: 0.25rem; }

    /* Sección título */
    .section-title {
        font-size: 1.15rem; font-weight: 600;
        color: #1565c0; border-left: 4px solid #1565c0;
        padding-left: 0.8rem; margin: 1.2rem 0 0.8rem;
    }

    /* Resaltado de insight */
    .insight-box {
        background: linear-gradient(135deg, #e3f2fd, #bbdefb);
        border-left: 4px solid #1976d2;
        border-radius: 6px;
        padding: 0.9rem 1.1rem;
        margin: 0.8rem 0;
        font-size: 0.9rem;
        color: #0d47a1;
    }

    /* Footer */
    .footer {
        text-align: center; font-size: 0.75rem;
        color: #888; margin-top: 2rem; padding-top: 1rem;
        border-top: 1px solid #eee;
    }
</style>
""", unsafe_allow_html=True)

# ── Carga de datos ────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    base = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base, '..', 'BNPL_Financial_Default_Risk_Dataset.csv')
    df = pd.read_csv(csv_path)
    df['Default_Risk'] = pd.Categorical(df['Default_Risk'],
        categories=['Low', 'Medium', 'High'], ordered=True)
    df['Late_Payment_bin'] = (df['Late_Payment_History'] == 'Yes').astype(int)
    return df

@st.cache_data
def load_coeficientes():
    base = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base, '..', 'analisis', 'tabla_coeficientes_regresion.csv')
    if os.path.exists(path):
        return pd.read_csv(path)
    return None

df = load_data()
coef_df = load_coeficientes()

PALETTE_RIESGO = {"Low": "#2ECC71", "Medium": "#F39C12", "High": "#E74C3C"}
PALETTE_EMPLEO = {"Employed": "#3498DB", "Student": "#9B59B6",
                  "Freelancer": "#E67E22", "Unemployed": "#E74C3C"}
N = len(df)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>📊 Riesgo de Incumplimiento BNPL — Análisis Bayesiano</h1>
    <p>Exploración interactiva de 10 000 consumidores de servicios Buy Now Pay Later
       mediante técnicas de inferencia bayesiana (Normal-Normal · Beta-Binomial · Regresión MCMC)</p>
</div>
""", unsafe_allow_html=True)

# ── Sidebar — Filtros globales ────────────────────────────────────────────────
st.sidebar.header("🎛️ Filtros globales")
filtro_riesgo = st.sidebar.multiselect(
    "Nivel de riesgo",
    options=['Low', 'Medium', 'High'],
    default=['Low', 'Medium', 'High']
)
filtro_empleo = st.sidebar.multiselect(
    "Estado laboral",
    options=['Employed', 'Student', 'Freelancer', 'Unemployed'],
    default=['Employed', 'Student', 'Freelancer', 'Unemployed']
)
filtro_late = st.sidebar.radio(
    "Historial de pago tardío",
    options=['Todos', 'Sin pago tardío', 'Con pago tardío'],
    index=0
)

df_f = df[df['Default_Risk'].isin(filtro_riesgo) & df['Employment_Status'].isin(filtro_empleo)]
if filtro_late == 'Sin pago tardío':
    df_f = df_f[df_f['Late_Payment_History'] == 'No']
elif filtro_late == 'Con pago tardío':
    df_f = df_f[df_f['Late_Payment_History'] == 'Yes']

st.sidebar.markdown(f"**Registros seleccionados:** {len(df_f):,} / {N:,}")

# ─────────────────────────────────────────────────────────────────────────────
# PANEL 1 — KPIs y panorama general
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">📌 Panel 1 — Panorama General</div>', unsafe_allow_html=True)

n_filt = len(df_f)
pct_high = (df_f['Default_Risk'] == 'High').mean() * 100
pct_late  = df_f['Late_Payment_bin'].mean() * 100
mean_credit = df_f['Credit_Score'].mean()
mean_income = df_f['Income_USD'].mean()
mean_debt   = df_f['Total_BNPL_Debt_USD'].mean()

c1, c2, c3, c4, c5, c6 = st.columns(6)
kpis = [
    (c1, f"{n_filt:,}",      "Consumidores",          ""),
    (c2, f"{pct_high:.1f}%", "Alto riesgo",           "⚠️"),
    (c3, f"{pct_late:.1f}%", "Pagos tardíos",         "🔴"),
    (c4, f"{mean_credit:.0f}", "Credit Score promedio", ""),
    (c5, f"${mean_income/1000:.0f}k", "Ingreso medio",  ""),
    (c6, f"${mean_debt:.0f}", "Deuda BNPL media (USD)", ""),
]
for col, val, label, icon in kpis:
    with col:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{icon}{val}</div>
            <div class="kpi-label">{label}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Gráficas de distribución general
col_a, col_b = st.columns(2)

with col_a:
    dr_counts = df_f['Default_Risk'].value_counts().reindex(['Low', 'Medium', 'High'])
    fig_pie = px.pie(
        values=dr_counts.values,
        names=dr_counts.index,
        color=dr_counts.index,
        color_discrete_map=PALETTE_RIESGO,
        title="Distribución del Nivel de Riesgo",
        hole=0.42
    )
    fig_pie.update_traces(textinfo='percent+label', textfont_size=12)
    fig_pie.update_layout(showlegend=True, margin=dict(t=40, b=10))
    st.plotly_chart(fig_pie, use_container_width=True)

with col_b:
    fig_hist = px.histogram(
        df_f, x='Credit_Score', color='Default_Risk',
        color_discrete_map=PALETTE_RIESGO,
        nbins=40, barmode='overlay', opacity=0.65,
        title="Distribución del Credit Score por Nivel de Riesgo",
        labels={'Credit_Score': 'Puntaje crediticio', 'count': 'Frecuencia'}
    )
    fig_hist.update_layout(legend_title='Nivel de riesgo', margin=dict(t=40, b=10))
    st.plotly_chart(fig_hist, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# PANEL 2 — Perfil del consumidor
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">👤 Panel 2 — Perfil del Consumidor</div>', unsafe_allow_html=True)

col_l, col_r = st.columns(2)

with col_l:
    fig_box = px.box(
        df_f, x='Employment_Status', y='Credit_Score',
        color='Default_Risk', color_discrete_map=PALETTE_RIESGO,
        category_orders={'Default_Risk': ['Low', 'Medium', 'High']},
        title="Credit Score por Estado Laboral y Nivel de Riesgo",
        labels={'Employment_Status': 'Estado laboral', 'Credit_Score': 'Puntaje crediticio'}
    )
    fig_box.update_layout(margin=dict(t=40, b=10))
    st.plotly_chart(fig_box, use_container_width=True)

with col_r:
    fig_scatter = px.scatter(
        df_f.dropna(subset=['Income_USD']),
        x='Income_USD', y='Credit_Score',
        color='Default_Risk',
        color_discrete_map=PALETTE_RIESGO,
        opacity=0.4, size_max=4,
        title="Ingreso vs. Credit Score (muestra aleatoria)",
        labels={'Income_USD': 'Ingreso anual (USD)', 'Credit_Score': 'Puntaje crediticio'}
    )
    fig_scatter.update_traces(marker=dict(size=3))
    fig_scatter.update_layout(margin=dict(t=40, b=10))
    st.plotly_chart(fig_scatter, use_container_width=True)

# Tabla resumen por grupo de riesgo
resumen = df_f.groupby('Default_Risk', observed=True).agg(
    n=('Credit_Score', 'count'),
    Credit_Score_media=('Credit_Score', 'mean'),
    Income_media=('Income_USD', 'mean'),
    Deuda_media=('Total_BNPL_Debt_USD', 'mean'),
    Tasa_pago_tardio=('Late_Payment_bin', 'mean')
).round(2).reset_index()
resumen.columns = ['Nivel de riesgo', 'n', 'Credit Score (μ)', 'Ingreso (μ, USD)', 'Deuda BNPL (μ, USD)', '% Pago tardío']
resumen['% Pago tardío'] = (resumen['% Pago tardío'] * 100).round(1).astype(str) + '%'
st.dataframe(resumen, use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────────────────────────────────────
# PANEL 3 — Modelo Bayesiano Paso 1: Normal-Normal
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">🔵 Panel 3 — Modelo Bayesiano: Inferencia sobre Credit Score</div>',
            unsafe_allow_html=True)

st.markdown("""
<div class="insight-box">
<b>Modelo Normal-Normal (conjugado):</b>
Verosimilitud Y_i | μ ~ Normal(μ, σ²) con prior μ ~ Normal(650, 100²).
La solución analítica del posterior permite cuantificar la incertidumbre
sobre la media del Credit Score en cada grupo de riesgo.
</div>
""", unsafe_allow_html=True)

# Parámetros del prior (control deslizante)
col_prior1, col_prior2 = st.columns(2)
with col_prior1:
    mu_0 = st.slider("Prior μ₀ (media del prior)", 550, 750, 650, step=10)
with col_prior2:
    tau_0 = st.slider("Prior τ₀ (std del prior)", 20, 200, 100, step=10)
tau_0_sq = tau_0**2

# Cálculo interactivo del posterior
grupos = ['Low', 'Medium', 'High']
x_range = np.linspace(520, 780, 1000)
prior_y = stats.norm.pdf(x_range, mu_0, tau_0)

fig_post = go.Figure()

# Prior
fig_post.add_trace(go.Scatter(
    x=x_range, y=prior_y / prior_y.max() * 0.25,
    mode='lines', name='Prior (escalado)',
    line=dict(color='gray', width=1.5, dash='dot'),
    opacity=0.7
))

posterior_results = []
for grupo in grupos:
    data_g = df[df['Default_Risk'] == grupo]['Credit_Score'].dropna()
    n_g    = len(data_g)
    y_bar  = data_g.mean()
    sigma_sq = data_g.var(ddof=1)
    tau_n_sq = 1.0 / (1.0/tau_0_sq + n_g/sigma_sq)
    mu_n     = tau_n_sq * (mu_0/tau_0_sq + n_g*y_bar/sigma_sq)
    tau_n    = np.sqrt(tau_n_sq)
    ic_l, ic_h = stats.norm.ppf([0.025, 0.975], mu_n, tau_n)
    color = PALETTE_RIESGO[grupo]
    post_y = stats.norm.pdf(x_range, mu_n, tau_n)
    fig_post.add_trace(go.Scatter(
        x=x_range, y=post_y, mode='lines',
        name=f'{grupo} (μₙ={mu_n:.1f})',
        line=dict(color=color, width=2.5),
        fill='tozeroy', fillcolor=color.replace(')', ',0.15)').replace('rgb', 'rgba') if 'rgb' in color else color + '26'
    ))
    fig_post.add_vline(x=mu_n, line=dict(color=color, width=1.5, dash='dash'))
    posterior_results.append({
        'Grupo': grupo, 'n': n_g, 'μₙ': round(mu_n, 2),
        'τₙ': round(tau_n, 4),
        'IC 95% inf.': round(ic_l, 2), 'IC 95% sup.': round(ic_h, 2)
    })

fig_post.update_layout(
    title='Distribuciones posteriores de la media del Credit Score por grupo de riesgo',
    xaxis_title='Credit Score',
    yaxis_title='Densidad posterior',
    legend_title='Grupo de riesgo',
    height=400,
    margin=dict(t=50, b=30)
)
st.plotly_chart(fig_post, use_container_width=True)
st.dataframe(pd.DataFrame(posterior_results), use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────────────────────────────────────
# PANEL 4 — Modelo Bayesiano Paso 3: Beta-Binomial
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">🟠 Panel 4 — Comparación de Proporciones (Beta-Binomial)</div>',
            unsafe_allow_html=True)

st.markdown("""
<div class="insight-box">
<b>Modelo Beta-Binomial (conjugado):</b>
Verosimilitud X_k | π_k ~ Binomial(n_k, π_k) con prior π_k ~ Beta(1,1) = Uniforme(0,1).
Permite comparar bayesianamente la tasa de pagos tardíos entre grupos de estado laboral.
</div>
""", unsafe_allow_html=True)

GRUPOS_EMP = ['Employed', 'Freelancer', 'Student', 'Unemployed']
x_beta = np.linspace(0.10, 0.55, 500)

fig_beta = go.Figure()
beta_results = []

for grupo in GRUPOS_EMP:
    mask = df['Employment_Status'] == grupo
    n_k  = mask.sum()
    X_k  = (df.loc[mask, 'Late_Payment_History'] == 'Yes').sum()
    a_n  = 1 + X_k
    b_n  = 1 + n_k - X_k
    mu_post = a_n / (a_n + b_n)
    ic_l, ic_h = stats.beta.ppf([0.025, 0.975], a_n, b_n)
    y_beta = stats.beta.pdf(x_beta, a_n, b_n)
    color  = PALETTE_EMPLEO[grupo]
    fig_beta.add_trace(go.Scatter(
        x=x_beta, y=y_beta, mode='lines',
        name=f'{grupo} (π̄={mu_post:.3f})',
        line=dict(color=color, width=2.5),
        fill='tozeroy', fillcolor=color + '22' if len(color) == 7 else color
    ))
    beta_results.append({
        'Grupo': grupo, 'n': n_k, 'Pagos tardíos': X_k,
        'Tasa obs.': f'{X_k/n_k:.3f}',
        'π posterior (μ)': round(mu_post, 4),
        'IC 95%': f'[{ic_l:.3f}, {ic_h:.3f}]'
    })

fig_beta.update_layout(
    title='Distribuciones posteriores de la tasa de pagos tardíos por estado laboral',
    xaxis_title='π_k (proporción con pago tardío)',
    yaxis_title='Densidad posterior',
    legend_title='Estado laboral',
    height=400, margin=dict(t=50, b=30)
)
st.plotly_chart(fig_beta, use_container_width=True)
st.dataframe(pd.DataFrame(beta_results), use_container_width=True, hide_index=True)

# Monte Carlo interactivo
st.markdown("**Probabilidad bayesiana: P(π_grupo > π_Employed | datos)**")
rng_mc = np.random.default_rng(42)
N_MC   = 200_000
mc_res = []
mask_emp = df['Employment_Status'] == 'Employed'
n_emp = mask_emp.sum(); X_emp = (df.loc[mask_emp,'Late_Payment_History']=='Yes').sum()
mc_emp = rng_mc.beta(1 + X_emp, 1 + n_emp - X_emp, N_MC)

for g in ['Freelancer', 'Student', 'Unemployed']:
    mask_g = df['Employment_Status'] == g
    n_g = mask_g.sum(); X_g = (df.loc[mask_g,'Late_Payment_History']=='Yes').sum()
    mc_g = rng_mc.beta(1 + X_g, 1 + n_g - X_g, N_MC)
    prob = np.mean(mc_g > mc_emp)
    mc_res.append({'Comparación': f'π_{g} > π_Employed', 'P(posterior)': f'{prob:.4f}',
                   'Interpretación': '✅ Diferencia clara' if prob > 0.95 else
                                     ('⚠️ Evidencia moderada' if prob > 0.75 else '❌ Sin diferencia clara')})
st.dataframe(pd.DataFrame(mc_res), use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────────────────────────────────────
# PANEL 5 — Regresión bayesiana (coeficientes + predictor interactivo)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">🟢 Panel 5 — Regresión Lineal Bayesiana (MCMC)</div>',
            unsafe_allow_html=True)

if coef_df is not None:
    st.markdown("""
    <div class="insight-box">
    <b>Regresión lineal bayesiana:</b> Credit_Score ~ β₀ + β·Income + β·Age + β·Loans
    + β·AvgTransaction + β·LatePayment + β·Employment. Muestreo MCMC con NUTS (PyMC).
    </div>
    """, unsafe_allow_html=True)

    # Forest plot interactivo
    coef_plot = coef_df[coef_df['Parámetro'] != 'Intercepto (β₀)'].copy()
    coef_plot = coef_plot[coef_plot['Parámetro'] != 'Desv. típica residual (σ)'].copy()

    colors_forest = ['#E74C3C' if r < 0 else '#2ECC71'
                     for r in coef_plot['IC 95% sup.']]
    # Si IC incluye 0: gris
    colors_forest = ['#7F8C8D' if (l < 0 < u) else c
                     for c, l, u in zip(colors_forest,
                                        coef_plot['IC 95% inf.'],
                                        coef_plot['IC 95% sup.'])]

    fig_forest = go.Figure()
    fig_forest.add_vline(x=0, line_dash='dash', line_color='gray', opacity=0.5)
    for i, (_, row) in enumerate(coef_plot.iterrows()):
        color = colors_forest[i]
        fig_forest.add_trace(go.Scatter(
            x=[row['IC 95% inf.'], row['Media posterior'], row['IC 95% sup.']],
            y=[row['Parámetro']] * 3,
            mode='lines+markers',
            marker=dict(size=[6, 10, 6], color=[color, color, color]),
            line=dict(color=color, width=2),
            name=row['Parámetro'], showlegend=False,
            hovertemplate=f"<b>{row['Parámetro']}</b><br>"
                          f"Media: {row['Media posterior']:.2f}<br>"
                          f"IC 95%: [{row['IC 95% inf.']:.2f}, {row['IC 95% sup.']:.2f}]<extra></extra>"
        ))

    fig_forest.update_layout(
        title='Coeficientes bayesianos — IC 95% (referencia: Employed, sin pago tardío)',
        xaxis_title='Efecto sobre Credit Score (puntos)',
        height=420, margin=dict(t=50, l=250, b=30)
    )
    st.plotly_chart(fig_forest, use_container_width=True)
    st.dataframe(coef_df, use_container_width=True, hide_index=True)

else:
    st.info("⚙️ Ejecuta primero `modelos/03_regresion_bayesiana.py` para generar los coeficientes del modelo MCMC.")
    st.markdown("Los coeficientes se cargarán automáticamente desde `analisis/tabla_coeficientes_regresion.csv`.")

# Predictor interactivo (aproximación analítica para no requerir PyMC en vivo)
st.markdown("#### 🎯 Predictor interactivo de Credit Score")
st.markdown("*Estimación basada en los coeficientes del modelo MCMC pre-entrenado*")

col1, col2, col3 = st.columns(3)
with col1:
    p_income = st.number_input("Ingreso anual (USD)", 5000, 140000, 55000, step=1000)
    p_age    = st.number_input("Edad", 18, 64, 30)
with col2:
    p_loans  = st.number_input("Préstamos BNPL activos", 0, 10, 2)
    p_avgtx  = st.number_input("Valor prom. transacción (USD)", 10, 1420, 300, step=10)
with col3:
    p_late   = st.selectbox("Historial pago tardío", ['No', 'Sí'])
    p_empleo = st.selectbox("Estado laboral", ['Employed', 'Student', 'Freelancer', 'Unemployed'])

if coef_df is not None:
    coef_map = dict(zip(coef_df['Parámetro'], coef_df['Media posterior']))
    ic_map_l = dict(zip(coef_df['Parámetro'], coef_df['IC 95% inf.']))
    ic_map_h = dict(zip(coef_df['Parámetro'], coef_df['IC 95% sup.']))

    inc_mean = df['Income_USD'].mean(); inc_std = df['Income_USD'].std()
    age_mean = df['Age'].mean();       age_std = df['Age'].std()
    loans_mean = df['Total_BNPL_Active_Loans'].mean(); loans_std = df['Total_BNPL_Active_Loans'].std()
    av_mean = df['Average_Transaction_Value_USD'].mean(); av_std = df['Average_Transaction_Value_USD'].std()

    inc_s  = (p_income - inc_mean)   / inc_std
    age_s  = (p_age    - age_mean)   / age_std
    loan_s = (p_loans  - loans_mean) / loans_std
    av_s   = (p_avgtx  - av_mean)    / av_std
    late_v = 1 if p_late == 'Sí' else 0

    emp_keys = {'Student': 'Estado: Student (vs. Employed)',
                'Freelancer': 'Estado: Freelancer (vs. Employed)',
                'Unemployed': 'Estado: Unemployed (vs. Employed)'}

    cs_pred = (coef_map.get('Intercepto (β₀)', 650)
               + coef_map.get('Ingreso anual (estandarizado)', 0) * inc_s
               + coef_map.get('Edad (estandarizada)', 0) * age_s
               + coef_map.get('Préstamos BNPL activos (std)', 0) * loan_s
               + coef_map.get('Valor prom. transacción (std)', 0) * av_s
               + coef_map.get('Historial pago tardío (Sí=1)', 0) * late_v
               + coef_map.get(emp_keys.get(p_empleo, ''), 0))

    cs_pred = max(300, min(850, cs_pred))
    sigma_est = coef_map.get('Desv. típica residual (σ)', 70)

    st.metric(
        label="Credit Score predicho (media posterior)",
        value=f"{cs_pred:.0f}",
        delta=f"IC 95% aprox.: [{max(300, cs_pred - 1.96*sigma_est):.0f} – {min(850, cs_pred + 1.96*sigma_est):.0f}]"
    )

    # Interpretación automática
    if cs_pred >= 700:
        categoria = "bajo (≥ 700)"
        emoji = "✅"
    elif cs_pred >= 600:
        categoria = "moderado (600–699)"
        emoji = "⚠️"
    else:
        categoria = "alto (< 600)"
        emoji = "🔴"

    st.markdown(f"""
    <div class="insight-box">
    {emoji} Según el modelo bayesiano, este perfil tiene un riesgo de incumplimiento
    <b>{categoria}</b>, con un Credit Score predicho de <b>{cs_pred:.0f}</b>.
    </div>
    """, unsafe_allow_html=True)
else:
    st.info("Ejecuta primero el modelo de regresión para habilitar el predictor.")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
    Proyecto Bayesiano BNPL · ESTG1047 Estadística Bayesiana · I Semestre 2026<br>
    Datos sintéticos — 10 000 consumidores BNPL · Análisis con PyMC, ArviZ y Streamlit
</div>
""", unsafe_allow_html=True)
