# ── app.py ────────────────────────────────────────────────────────────────────
# Application Streamlit — Dashboard Économique Multi-Pays
# Inspiré de la structure du dashboard HTML Timor-Leste :
#   Header → Navigation (piliers) → Overview ribbon → KPIs → Graphiques → Tableau
# ─────────────────────────────────────────────────────────────────────────────

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

from services.data_service import DataService
from config import (
    APP_TITLE, APP_SUBTITLE, INDICATORS, COLORS,
    CHART_SERIES, PILIER_META, KPI_CODES, DATA_YEARS
)

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION STREAMLIT
# ─────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS global — cohérent avec la palette du HTML source
st.markdown("""
<style>
    /* Police et fond général */
    .stApp { background-color: #f5f4f0; }
    
    /* Header custom */
    .dash-header {
        background: #1a3450;
        padding: 1.5rem 2rem;
        border-bottom: 3px solid #c8a84b;
        border-radius: 6px;
        margin-bottom: 1.5rem;
    }
    .dash-header h1 {
        color: #f0ece4;
        font-size: 1.4rem;
        margin: 0;
        font-weight: normal;
    }
    .dash-header h1 em {
        color: #c8a84b;
        font-style: normal;
        font-weight: bold;
    }
    .dash-header p {
        color: rgba(240,236,228,0.55);
        font-size: 0.75rem;
        margin: 0.4rem 0 0 0;
    }

    /* Badges */
    .badge-row { display: flex; gap: 0.5rem; flex-wrap: wrap; margin-top: 0.8rem; }
    .badge {
        background: rgba(255,255,255,0.07);
        border: 1px solid rgba(200,168,75,0.35);
        border-radius: 3px;
        padding: 0.2rem 0.6rem;
        font-size: 0.7rem;
        color: rgba(240,236,228,0.7);
    }

    /* Overview ribbon */
    .overview-ribbon {
        background: #e8eef4;
        border: 1px solid #c8d8e8;
        border-left: 4px solid #2b4a6b;
        border-radius: 4px;
        padding: 1rem 1.2rem;
        margin-bottom: 1.5rem;
        font-size: 0.85rem;
        color: #4a4843;
        line-height: 1.6;
    }

    /* KPI cards */
    .kpi-card {
        background: white;
        border: 1px solid #dddbd7;
        border-radius: 6px;
        padding: 1.2rem 1.4rem;
    }
    .kpi-label {
        font-size: 0.65rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #8a8780;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }
    .kpi-value {
        font-size: 2rem;
        font-weight: bold;
        color: #1a3450;
        line-height: 1;
    }
    .kpi-unit {
        font-size: 0.75rem;
        color: #4a4843;
        margin-top: 0.3rem;
    }
    .kpi-delta-pos { color: #2e7d4f; font-size: 0.72rem; }
    .kpi-delta-neg { color: #c0392b; font-size: 0.72rem; }
    .kpi-delta-neu { color: #c0620a; font-size: 0.72rem; }
    .kpi-source {
        font-size: 0.62rem;
        color: #8a8780;
        margin-top: 0.5rem;
        border-top: 1px solid #e8e6e2;
        padding-top: 0.4rem;
        font-style: italic;
    }

    /* Section title */
    .sub-label {
        font-size: 0.68rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #8a8780;
        font-weight: 600;
        border-bottom: 1px solid #e8e6e2;
        padding-bottom: 0.4rem;
        margin: 1.5rem 0 1rem 0;
    }

    /* Masquer le menu hamburger Streamlit */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #f5f4f0;
        border-right: 1px solid #dddbd7;
    }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SERVICE & CACHE
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_resource
def get_service() -> DataService:
    return DataService()


@st.cache_data(ttl=3600, show_spinner=False)
def load_countries() -> pd.DataFrame:
    svc = get_service()
    return svc.get_countries()


@st.cache_data(ttl=3600, show_spinner=False)
def load_all_series(country_code: str) -> dict:
    svc = get_service()
    return svc.get_all_series(country_code)


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS DE RENDU
# ─────────────────────────────────────────────────────────────────────────────

def render_kpi_card(kpi: dict):
    """Affiche une card KPI avec valeur, unité, delta et source."""
    delta_html = ""
    if kpi["delta"] is not None:
        d = kpi["delta"]
        if d > 0:
            delta_html = f'<div class="kpi-delta-pos">↑ +{d:.1f}% {kpi["delta_label"]}</div>'
        elif d < 0:
            delta_html = f'<div class="kpi-delta-neg">↓ {d:.1f}% {kpi["delta_label"]}</div>'
        else:
            delta_html = f'<div class="kpi-delta-neu">→ stable {kpi["delta_label"]}</div>'

    year_str = f" ({kpi['year']})" if kpi["year"] else ""
    src_link = f'<a href="{kpi["source_url"]}" target="_blank" style="color:#8a8780">{kpi["source"]}</a>' if kpi["source_url"] else kpi["source"]

    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">{kpi["label"]}</div>
        <div class="kpi-value">{kpi["value_display"]}</div>
        <div class="kpi-unit">{kpi["unit_display"]}{year_str}</div>
        {delta_html}
        <div class="kpi-source">{src_link}</div>
    </div>
    """, unsafe_allow_html=True)


def make_line_chart(
    series_dict: dict[str, pd.DataFrame],
    labels: dict[str, str],
    title: str = "",
    y_suffix: str = "",
    fill: bool = False,
) -> go.Figure:
    """Graphique linéaire multi-séries."""
    fig = go.Figure()
    color_list = list(COLORS.values())

    for i, (code, df) in enumerate(series_dict.items()):
        if df is None or df.empty:
            continue
        df_clean = df.dropna(subset=["value"])
        color = color_list[i % len(color_list)]
        fig.add_trace(go.Scatter(
            x=df_clean["year"],
            y=df_clean["value"],
            name=labels.get(code, code),
            line=dict(color=color, width=2),
            fill="tozeroy" if fill else "none",
            fillcolor=color.replace(")", ",0.08)").replace("rgb", "rgba") if fill else None,
            mode="lines+markers",
            marker=dict(size=4),
            hovertemplate=f"<b>%{{y:.2f}}{y_suffix}</b><br>%{{x}}<extra>{labels.get(code, code)}</extra>",
        ))

    fig.update_layout(
        title=title,
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(size=11, color="#4a4843"),
        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="left", x=0),
        margin=dict(l=10, r=10, t=30, b=60),
        hovermode="x unified",
        xaxis=dict(gridcolor="#e8e6e2", showgrid=True),
        yaxis=dict(gridcolor="#e8e6e2", showgrid=True, ticksuffix=y_suffix),
        height=280,
    )
    return fig


def make_bar_chart(
    df: pd.DataFrame,
    code: str,
    label: str,
    y_suffix: str = "",
    color: str = "#2563a8",
) -> go.Figure:
    """Graphique en barres pour une série."""
    if df is None or df.empty:
        return go.Figure()

    df_clean = df.dropna(subset=["value"])
    fig = go.Figure(go.Bar(
        x=df_clean["year"],
        y=df_clean["value"],
        name=label,
        marker_color=[
            COLORS["green"] if v >= 0 else COLORS["red"]
            for v in df_clean["value"]
        ] if y_suffix == "%" else color,
        marker_line_width=0,
    ))
    fig.update_layout(
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(size=11, color="#4a4843"),
        legend=dict(orientation="h", yanchor="bottom", y=-0.35, xanchor="left", x=0),
        margin=dict(l=10, r=10, t=20, b=65),
        xaxis=dict(gridcolor="#e8e6e2"),
        yaxis=dict(gridcolor="#e8e6e2", ticksuffix=y_suffix),
        height=280,
        showlegend=True,
    )
    return fig


def no_data_placeholder(label: str = ""):
    st.info(f"📭 Donnée non disponible{' : ' + label if label else ''} pour ce pays.")


# ── Traduction des termes Banque Mondiale en français ────────────────────────

INCOME_LEVELS_FR = {
    "Low income": "Faible revenu",
    "Lower middle income": "Revenu intermédiaire inférieur",
    "Upper middle income": "Revenu intermédiaire supérieur",
    "High income": "Revenu élevé",
    "Not classified": "Non classifié",
}

REGIONS_FR = {
    "East Asia & Pacific": "Asie de l'Est & Pacifique",
    "Europe & Central Asia": "Europe & Asie centrale",
    "Latin America & Caribbean": "Amérique latine & Caraïbes",
    "Middle East & North Africa": "Moyen-Orient & Afrique du Nord",
    "North America": "Amérique du Nord",
    "South Asia": "Asie du Sud",
    "Sub-Saharan Africa": "Afrique subsaharienne",
}

def traduire_revenu(label: str) -> str:
    """Traduit le niveau de revenu Banque Mondiale en français."""
    return INCOME_LEVELS_FR.get(label, label)

def traduire_region(label: str) -> str:
    """Traduit la région Banque Mondiale en français."""
    return REGIONS_FR.get(label, label)


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 🌍 Sélection du pays")

    with st.spinner("Chargement des pays…"):
        countries_df = load_countries()

    if countries_df.empty:
        st.error("⚠️ Impossible de charger la liste des pays. Vérifiez votre connexion.")
        st.stop()

    # Sélecteur
    country_names = countries_df["name"].tolist()
    default_idx = country_names.index("Timor-Leste") if "Timor-Leste" in country_names else 0
    selected_name = st.selectbox(
        "Pays",
        country_names,
        index=default_idx,
        label_visibility="collapsed",
    )

    selected_row = countries_df[countries_df["name"] == selected_name].iloc[0]
    country_code = selected_row["code"]
    country_region = traduire_region(selected_row.get("region", ""))
    country_income = traduire_revenu(selected_row.get("income_level", ""))

    st.markdown("---")
    st.markdown(f"**Code ISO :** `{country_code}`")
    if country_region:
        st.markdown(f"**Région :** {country_region}")
    if country_income:
        st.markdown(f"**Niveau de revenu :** {country_income}")

    st.markdown("---")

    # Navigation piliers
    st.markdown("### 📑 Navigation")
    pilier_options = {
        f"{v['icon']} Pilier {k} — {v['label']}": k
        for k, v in PILIER_META.items()
    }
    selected_pilier_label = st.radio(
        "Section",
        list(pilier_options.keys()),
        label_visibility="collapsed",
    )
    active_pilier = pilier_options[selected_pilier_label]

    st.markdown("---")
    st.caption("Sources · Phase 1 : Banque Mondiale WDI")
    st.caption("Phase 2 : FMI · Freedom House · V-Dem · WGI")


# ─────────────────────────────────────────────────────────────────────────────
# CHARGEMENT DONNÉES
# ─────────────────────────────────────────────────────────────────────────────

with st.spinner(f"Chargement des données pour {selected_name}…"):
    all_series = load_all_series(country_code)

svc = get_service()
kpis = svc.get_kpis(country_code, all_series)
summary_df = svc.get_summary_table(country_code, all_series)


# ─────────────────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────────────────

# Trouver le PIB pour le badge
gdp_kpi = next((k for k in kpis if k["code"] == "NY.GDP.MKTP.CD"), None)
gdp_badge = f"PIB ~{gdp_kpi['value_display']} Md$" if gdp_kpi and gdp_kpi["value_raw"] else "PIB N/D"

pop_kpi = next((k for k in kpis if k["code"] == "SP.POP.TOTL"), None)
pop_badge = f"Pop. {pop_kpi['value_display']} M" if pop_kpi and pop_kpi["value_raw"] else ""

income_short = country_income

st.markdown(f"""
<div class="dash-header">
    <h1>{selected_name} — <em>Fondamentaux Économiques</em></h1>
    <p>{APP_SUBTITLE} · Données {DATA_YEARS} dernières années</p>
    <div class="badge-row">
        <span class="badge">{gdp_badge}</span>
        {'<span class="badge">' + pop_badge + '</span>' if pop_badge else ''}
        <span class="badge">{country_region}</span>
        <span class="badge">{income_short}</span>
        <span class="badge">Code : {country_code}</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# PILIER 1 — CADRE SOCIOÉCONOMIQUE & POLITIQUE
# ─────────────────────────────────────────────────────────────────────────────

if active_pilier == 1:
    pm = PILIER_META[1]
    st.markdown(f"### {pm['icon']} Pilier 1 — {pm['label']}")
    st.caption(pm["description"])

    # Overview ribbon
    pop_val = next((k["value_display"] for k in kpis if k["code"] == "SP.POP.TOTL"), "N/D")
    pop_year = next((k["year"] for k in kpis if k["code"] == "SP.POP.TOTL"), "")
    unem_val = next((k["value_display"] for k in kpis if k["code"] == "SL.UEM.TOTL.ZS"), "N/D")

    st.markdown(f"""
    <div class="overview-ribbon">
        <strong>{selected_name}</strong> — Population : <strong>{pop_val} M hab.</strong> ({pop_year}).
        Taux de chômage : <strong>{unem_val}%</strong> (modélisation OIT).
        Région : <strong>{country_region}</strong> · Niveau de revenu : <strong>{country_income}</strong>.
        Les données ci-dessous sont récupérées en temps réel depuis la Banque Mondiale (WDI).
    </div>
    """, unsafe_allow_html=True)

    # ── KPIs sociaux ──
    st.markdown('<div class="sub-label">Indicateurs clés</div>', unsafe_allow_html=True)
    social_codes = ["SP.POP.TOTL", "SL.UEM.TOTL.ZS", "SP.DYN.LE00.IN", "SP.DYN.IMRT.IN"]
    social_kpis = [k for k in kpis if k["code"] in social_codes]

    cols = st.columns(len(social_kpis) if social_kpis else 1)
    for col, kpi in zip(cols, social_kpis):
        with col:
            render_kpi_card(kpi)

    # ── Graphiques démographiques ──
    st.markdown('<div class="sub-label">Démographie & emploi</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        df_pop = all_series.get("SP.POP.TOTL", pd.DataFrame())
        if not df_pop.empty:
            df_pop_scaled = df_pop.copy()
            df_pop_scaled["value"] = df_pop_scaled["value"] / 1e6
            fig = make_line_chart(
                {"SP.POP.TOTL": df_pop_scaled},
                {"SP.POP.TOTL": "Population (millions)"},
                fill=True,
                y_suffix=" M",
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            st.caption("*Source : Banque Mondiale WDI — SP.POP.TOTL*")
        else:
            no_data_placeholder("Population")

    with col2:
        df_unem = all_series.get("SL.UEM.TOTL.ZS", pd.DataFrame())
        if not df_unem.empty:
            fig = make_bar_chart(df_unem, "SL.UEM.TOTL.ZS", "Chômage (%)", y_suffix="%", color=COLORS["orange"])
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            st.caption("*Source : Banque Mondiale WDI — SL.UEM.TOTL.ZS (modélisation OIT)*")
        else:
            no_data_placeholder("Chômage")

    # ── Espérance de vie ──
    df_life = all_series.get("SP.DYN.LE00.IN", pd.DataFrame())
    df_mort = all_series.get("SP.DYN.IMRT.IN", pd.DataFrame())

    if not df_life.empty or not df_mort.empty:
        col3, col4 = st.columns(2)
        with col3:
            if not df_life.empty:
                fig = make_line_chart(
                    {"SP.DYN.LE00.IN": df_life},
                    {"SP.DYN.LE00.IN": "Espérance de vie"},
                    y_suffix=" ans",
                )
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
                st.caption("*Source : Banque Mondiale WDI — SP.DYN.LE00.IN*")
        with col4:
            if not df_mort.empty:
                fig = make_bar_chart(df_mort, "SP.DYN.IMRT.IN", "Mortalité infantile (‰)", color=COLORS["red"])
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
                st.caption("*Source : Banque Mondiale WDI — SP.DYN.IMRT.IN*")


# ─────────────────────────────────────────────────────────────────────────────
# PILIER 2 — MODÈLE DE CROISSANCE
# ─────────────────────────────────────────────────────────────────────────────

elif active_pilier == 2:
    pm = PILIER_META[2]
    st.markdown(f"### {pm['icon']} Pilier 2 — {pm['label']}")
    st.caption(pm["description"])

    # KPIs croissance
    gdp_kpi = next((k for k in kpis if k["code"] == "NY.GDP.MKTP.CD"), None)
    gdp_val = gdp_kpi["value_display"] if gdp_kpi and gdp_kpi["value_raw"] else "N/D"
    growth_kpi = next((k for k in kpis if k["code"] == "NY.GDP.MKTP.KD.ZG"), None)
    growth_val = growth_kpi["value_display"] if growth_kpi and growth_kpi["value_raw"] else "N/D"

    st.markdown(f"""
    <div class="overview-ribbon">
        <strong>PIB nominal</strong> : <strong>{gdp_val} Md USD</strong>.
        <strong>Croissance réelle</strong> : <strong>{growth_val}%</strong> (dernière année disponible).
        Données dynamiques récupérées depuis la Banque Mondiale — World Development Indicators.
    </div>
    """, unsafe_allow_html=True)

    # ── KPIs ──
    st.markdown('<div class="sub-label">Indicateurs macroéconomiques</div>', unsafe_allow_html=True)
    macro_codes = ["NY.GDP.MKTP.CD", "NY.GDP.PCAP.CD", "NY.GDP.MKTP.KD.ZG"]
    macro_kpis = [k for k in kpis if k["code"] in macro_codes]

    cols = st.columns(len(macro_kpis) if macro_kpis else 1)
    for col, kpi in zip(cols, macro_kpis):
        with col:
            render_kpi_card(kpi)

    # ── Graphiques PIB ──
    st.markdown('<div class="sub-label">Dynamique de croissance</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        df_growth = all_series.get("NY.GDP.MKTP.KD.ZG", pd.DataFrame())
        if not df_growth.empty:
            fig = make_bar_chart(
                df_growth, "NY.GDP.MKTP.KD.ZG",
                "Croissance PIB réel (%)", y_suffix="%",
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            st.caption("*Banque Mondiale — NY.GDP.MKTP.KD.ZG · Barres vertes = croissance positive*")
        else:
            no_data_placeholder("Croissance du PIB")

    with col2:
        df_gdppc = all_series.get("NY.GDP.PCAP.CD", pd.DataFrame())
        if not df_gdppc.empty:
            fig = make_line_chart(
                {"NY.GDP.PCAP.CD": df_gdppc},
                {"NY.GDP.PCAP.CD": "PIB/hab. (USD)"},
                y_suffix=" $",
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            st.caption("*Banque Mondiale — NY.GDP.PCAP.CD*")
        else:
            no_data_placeholder("PIB par habitant")

    # ── PIB nominal en milliards ──
    st.markdown('<div class="sub-label">PIB nominal (Md USD)</div>', unsafe_allow_html=True)
    df_gdp = all_series.get("NY.GDP.MKTP.CD", pd.DataFrame())
    if not df_gdp.empty:
        df_gdp_scaled = df_gdp.copy()
        df_gdp_scaled["value"] = df_gdp_scaled["value"] / 1e9
        fig = make_line_chart(
            {"NY.GDP.MKTP.CD": df_gdp_scaled},
            {"NY.GDP.MKTP.CD": "PIB nominal (Md USD)"},
            fill=True,
            y_suffix=" Md$",
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.caption("*Banque Mondiale — NY.GDP.MKTP.CD (milliards USD courants)*")
    else:
        no_data_placeholder("PIB nominal")


# ─────────────────────────────────────────────────────────────────────────────
# PILIER 3 — FINANCES PUBLIQUES & PRIX
# ─────────────────────────────────────────────────────────────────────────────

elif active_pilier == 3:
    pm = PILIER_META[3]
    st.markdown(f"### {pm['icon']} Pilier 3 — {pm['label']}")
    st.caption(pm["description"])

    infl_kpi = next((k for k in kpis if k["code"] == "FP.CPI.TOTL.ZG"), None)
    infl_val = infl_kpi["value_display"] if infl_kpi and infl_kpi["value_raw"] else "N/D"

    st.markdown(f"""
    <div class="overview-ribbon">
        <strong>Inflation (IPC)</strong> : <strong>{infl_val}%</strong> (dernière année disponible).
        Indicateurs de finances publiques et de stabilité des prix.
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sub-label">Prix & finances publiques</div>', unsafe_allow_html=True)
    fin_codes = ["FP.CPI.TOTL.ZG", "GC.BAL.CASH.GD.ZS", "GC.DOD.TOTL.GD.ZS"]
    fin_kpis = [k for k in kpis if k["code"] in fin_codes]

    cols = st.columns(max(len(fin_kpis), 1))
    for col, kpi in zip(cols, fin_kpis):
        with col:
            render_kpi_card(kpi)

    # ── Inflation ──
    st.markdown('<div class="sub-label">Évolution de l\'inflation</div>', unsafe_allow_html=True)
    df_infl = all_series.get("FP.CPI.TOTL.ZG", pd.DataFrame())
    df_debt = all_series.get("GC.DOD.TOTL.GD.ZS", pd.DataFrame())
    df_bal = all_series.get("GC.BAL.CASH.GD.ZS", pd.DataFrame())

    col1, col2 = st.columns(2)
    with col1:
        if not df_infl.empty:
            fig = make_bar_chart(df_infl, "FP.CPI.TOTL.ZG", "Inflation IPC (%)", y_suffix="%", color=COLORS["orange"])
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            st.caption("*Banque Mondiale — FP.CPI.TOTL.ZG*")
        else:
            no_data_placeholder("Inflation")

    with col2:
        if not df_infl.empty and not df_bal.empty:
            fig = make_line_chart(
                {"FP.CPI.TOTL.ZG": df_infl, "GC.BAL.CASH.GD.ZS": df_bal},
                {"FP.CPI.TOTL.ZG": "Inflation (%)", "GC.BAL.CASH.GD.ZS": "Solde budgétaire (% PIB)"},
                y_suffix="%",
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            st.caption("*Banque Mondiale — FP.CPI.TOTL.ZG + GC.BAL.CASH.GD.ZS*")
        elif not df_debt.empty:
            fig = make_line_chart(
                {"GC.DOD.TOTL.GD.ZS": df_debt},
                {"GC.DOD.TOTL.GD.ZS": "Dette publique (% PIB)"},
                y_suffix="%",
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            st.caption("*Banque Mondiale — GC.DOD.TOTL.GD.ZS*")
        else:
            no_data_placeholder("Solde / dette publique")


# ─────────────────────────────────────────────────────────────────────────────
# PILIER 4 — ÉQUILIBRES EXTERNES
# ─────────────────────────────────────────────────────────────────────────────

elif active_pilier == 4:
    pm = PILIER_META[4]
    st.markdown(f"### {pm['icon']} Pilier 4 — {pm['label']}")
    st.caption(pm["description"])

    cab_kpi = next((k for k in kpis if k["code"] == "BN.CAB.XOKA.GD.ZS"), None)
    ide_kpi = next((k for k in kpis if k["code"] == "BX.KLT.DINV.WD.GD.ZS"), None)

    cab_val = cab_kpi["value_display"] if cab_kpi and cab_kpi["value_raw"] else "N/D"
    ide_val = ide_kpi["value_display"] if ide_kpi and ide_kpi["value_raw"] else "N/D"

    st.markdown(f"""
    <div class="overview-ribbon">
        <strong>Solde compte courant</strong> : <strong>{cab_val}% du PIB</strong>.
        <strong>IDE entrants</strong> : <strong>{ide_val}% du PIB</strong>.
        Indicateurs d'ouverture et d'équilibre externe.
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sub-label">Indicateurs externes</div>', unsafe_allow_html=True)
    ext_codes = ["BN.CAB.XOKA.GD.ZS", "BX.KLT.DINV.WD.GD.ZS"]
    ext_kpis = [k for k in kpis if k["code"] in ext_codes]

    cols = st.columns(max(len(ext_kpis), 1))
    for col, kpi in zip(cols, ext_kpis):
        with col:
            render_kpi_card(kpi)

    col1, col2 = st.columns(2)
    df_cab = all_series.get("BN.CAB.XOKA.GD.ZS", pd.DataFrame())
    df_ide = all_series.get("BX.KLT.DINV.WD.GD.ZS", pd.DataFrame())

    with col1:
        if not df_cab.empty:
            fig = make_bar_chart(df_cab, "BN.CAB.XOKA.GD.ZS", "Compte courant (% PIB)", y_suffix="%")
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            st.caption("*Banque Mondiale — BN.CAB.XOKA.GD.ZS*")
        else:
            no_data_placeholder("Solde compte courant")

    with col2:
        if not df_ide.empty:
            fig = make_line_chart(
                {"BX.KLT.DINV.WD.GD.ZS": df_ide},
                {"BX.KLT.DINV.WD.GD.ZS": "IDE entrants (% PIB)"},
                y_suffix="%",
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            st.caption("*Banque Mondiale — BX.KLT.DINV.WD.GD.ZS*")
        else:
            no_data_placeholder("IDE")



# ─────────────────────────────────────────────────────────────────────────────
# PILIER 5 — SYSTÈME FINANCIER & MONÉTAIRE
# ─────────────────────────────────────────────────────────────────────────────

elif active_pilier == 5:
    pm = PILIER_META[5]
    st.markdown(f"### {pm['icon']} Pilier 5 — {pm['label']}")
    st.caption(pm["description"])

    # Valeurs pour le ribbon
    credit_kpi = next((k for k in kpis if k["code"] == "FD.AST.PRVT.GD.ZS"), None)
    dom_kpi    = next((k for k in kpis if k["code"] == "FS.AST.DOMS.GD.ZS"), None)
    lend_kpi   = next((k for k in kpis if k["code"] == "FR.INR.LEND"), None)
    incl_kpi   = next((k for k in kpis if k["code"] == "FB.BNK.CAPA.ZS"), None)

    credit_val = credit_kpi["value_display"] if credit_kpi and credit_kpi["value_raw"] else "N/D"
    lend_val   = lend_kpi["value_display"]   if lend_kpi   and lend_kpi["value_raw"]   else "N/D"
    incl_val   = incl_kpi["value_display"]   if incl_kpi   and incl_kpi["value_raw"]   else "N/D"

    st.markdown(f"""
    <div class="overview-ribbon">
        <strong>Crédit au secteur privé</strong> : <strong>{credit_val}% du PIB</strong>.
        <strong>Taux débiteur</strong> : <strong>{lend_val}%</strong>.
        <strong>Inclusion financière</strong> (adultes avec compte) : <strong>{incl_val}%</strong>.
        Profondeur et accessibilité du système financier — données Banque Mondiale WDI.
    </div>
    """, unsafe_allow_html=True)

    # ── KPIs ──
    st.markdown('<div class="sub-label">Indicateurs clés du système financier</div>', unsafe_allow_html=True)
    fin_codes = ["FD.AST.PRVT.GD.ZS", "FS.AST.DOMS.GD.ZS", "FR.INR.LEND", "FB.BNK.CAPA.ZS"]
    fin_kpis  = [k for k in kpis if k["code"] in fin_codes]

    cols = st.columns(max(len(fin_kpis), 1))
    for col, kpi in zip(cols, fin_kpis):
        with col:
            render_kpi_card(kpi)

    # ── Crédit privé & crédit domestique ──
    st.markdown('<div class="sub-label">Profondeur financière</div>', unsafe_allow_html=True)
    df_credit = all_series.get("FD.AST.PRVT.GD.ZS", pd.DataFrame())
    df_dom    = all_series.get("FS.AST.DOMS.GD.ZS", pd.DataFrame())
    df_lend   = all_series.get("FR.INR.LEND", pd.DataFrame())
    df_incl   = all_series.get("FB.BNK.CAPA.ZS", pd.DataFrame())

    col1, col2 = st.columns(2)
    with col1:
        series_depth = {}
        labels_depth = {}
        if not df_credit.empty:
            series_depth["FD.AST.PRVT.GD.ZS"] = df_credit
            labels_depth["FD.AST.PRVT.GD.ZS"] = "Crédit privé (% PIB)"
        if not df_dom.empty:
            series_depth["FS.AST.DOMS.GD.ZS"] = df_dom
            labels_depth["FS.AST.DOMS.GD.ZS"] = "Crédit domestique total (% PIB)"

        if series_depth:
            fig = make_line_chart(series_depth, labels_depth, y_suffix="%")
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            st.caption("*Banque Mondiale — FD.AST.PRVT.GD.ZS · FS.AST.DOMS.GD.ZS*")
        else:
            no_data_placeholder("Crédit / profondeur financière")

    with col2:
        if not df_lend.empty:
            fig = make_bar_chart(df_lend, "FR.INR.LEND", "Taux d'intérêt débiteur (%)",
                                 y_suffix="%", color=COLORS["orange"])
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            st.caption("*Banque Mondiale — FR.INR.LEND*")
        else:
            no_data_placeholder("Taux d'intérêt débiteur")

    # ── Inclusion financière ──
    st.markdown('<div class="sub-label">Inclusion financière</div>', unsafe_allow_html=True)
    if not df_incl.empty:
        fig = make_line_chart(
            {"FB.BNK.CAPA.ZS": df_incl},
            {"FB.BNK.CAPA.ZS": "Adultes avec compte bancaire (%)"},
            fill=True,
            y_suffix="%",
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.caption("*Banque Mondiale — FB.BNK.CAPA.ZS · Enquête Findex (jalons)*")
    else:
        # Afficher un message contextuel si la série est vide (fréquent — données Findex tri-annuelles)
        st.info(
            "📭 Les données d'inclusion financière (% adultes avec compte) ne sont pas disponibles "
            "en série annuelle continue via la Banque Mondiale pour ce pays. "
            "Source alternative : Enquête Global Findex (BDMF) — publication tri-annuelle."
        )




# ─────────────────────────────────────────────────────────────────────────────
elif active_pilier == 6:

    pm = PILIER_META[6]
    st.markdown(f"### {pm['icon']} Pilier 6 — {pm['label']}")
    st.caption(pm["description"])

    # ─────────────────────────────────────────────────────────────
    # CHARGEMENT DONNÉES
    # ─────────────────────────────────────────────────────────────
    with st.spinner("Chargement des données climatiques spécialisées…"):
        clim = load_climate_data(country_code)

    ndgain = clim.get("ndgain", {})
    iea = clim.get("iea", {})
    cw_tot = clim.get("cw_total", {})
    cw_sec = clim.get("cw_sectors", [])
    cw_ndc = clim.get("cw_ndc", {})

    # ─────────────────────────────────────────────────────────────
    # OVERVIEW
    # ─────────────────────────────────────────────────────────────
    ndgain_score = ndgain.get("score")
    ndgain_rank = ndgain.get("rank")

    co2_energy = iea.get("co2_energy_mt")
    renewable = iea.get("renewable_share")

    ges_value = cw_tot.get("value")

    st.markdown(f"""
    <div class="overview-ribbon">
        <strong>Score ND-GAIN</strong> : <strong>{ndgain_score if ndgain_score else "N/D"}</strong>
        (rang {ndgain_rank if ndgain_rank else "N/D"}).<br>
        <strong>Émissions énergie</strong> : <strong>{co2_energy if co2_energy else "N/D"} Mt CO₂</strong>.<br>
        <strong>Part renouvelables</strong> : <strong>{renewable if renewable else "N/D"}%</strong>.<br>
        <strong>GES totales</strong> : <strong>{ges_value if ges_value else "N/D"} MtCO₂eq</strong>.
    </div>
    """, unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────
    # KPIs
    # ─────────────────────────────────────────────────────────────
    st.markdown('<div class="sub-label">Indicateurs clés</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("ND-GAIN", ndgain_score if ndgain_score else "N/D")

    with col2:
        st.metric("CO₂ énergie", co2_energy if co2_energy else "N/D")

    with col3:
        st.metric("Renouvelables (%)", renewable if renewable else "N/D")

    with col4:
        st.metric("GES totales", ges_value if ges_value else "N/D")

    # ─────────────────────────────────────────────────────────────
    # GRAPHIQUE ÉMISSIONS (série temporelle)
    # ─────────────────────────────────────────────────────────────
    st.markdown('<div class="sub-label">Émissions GES (série historique)</div>', unsafe_allow_html=True)

    series = cw_tot.get("series", [])

    if series:
        df = pd.DataFrame(series)

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["year"],
            y=df["value"],
            mode="lines+markers",
            name="GES",
        ))

        fig.update_layout(
            height=300,
            margin=dict(l=10, r=10, t=20, b=40),
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("📭 Pas de données émissions disponibles")

    # ─────────────────────────────────────────────────────────────
    # RÉPARTITION PAR SECTEUR
    # ─────────────────────────────────────────────────────────────
    st.markdown('<div class="sub-label">Répartition des émissions par secteur</div>', unsafe_allow_html=True)

    if cw_sec:
        df_sec = pd.DataFrame(cw_sec)

        fig = px.pie(
            df_sec,
            values="value",
            names="sector",
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("📭 Pas de données sectorielles")

    # ─────────────────────────────────────────────────────────────
    # NDC
    # ─────────────────────────────────────────────────────────────
    st.markdown('<div class="sub-label">Engagements climatiques (NDC)</div>', unsafe_allow_html=True)

    if cw_ndc.get("unconditional_target"):
        st.write("**Objectif non conditionnel :**")
        st.write(cw_ndc["unconditional_target"])

    if cw_ndc.get("conditional_target"):
        st.write("**Objectif conditionnel :**")
        st.write(cw_ndc["conditional_target"])

    if not cw_ndc.get("unconditional_target") and not cw_ndc.get("conditional_target"):
        st.info("📭 Informations NDC indisponibles")




# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("---")
st.caption(
    f"**{APP_TITLE}** · {APP_SUBTITLE} · "
    "Données récupérées en temps réel via API publique · "
    "Architecture extensible : FMI, Freedom House, V-Dem, WGI (Phase 2)"
)
