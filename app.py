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
# PILIER 6 — RISQUES CLIMAT & NATURE
# Sources : Banque Mondiale WDI · Climate Watch (CAIT) · ND-GAIN · IEA
# ─────────────────────────────────────────────────────────────────────────────

elif active_pilier == 6:
    from scrapers.climat_scraper import fetch_ndgain, fetch_iea, fetch_cw_emissions, fetch_cw_emissions_by_sector, fetch_cw_ndc

    pm = PILIER_META[6]
    st.markdown(f"### {pm['icon']} Pilier 6 — {pm['label']}")
    st.caption(pm["description"])

    # ── Chargement des données spécialisées (avec cache) ──────────────────────
    @st.cache_data(ttl=86400, show_spinner=False)
    def load_climate_data(cc: str) -> dict:
        return {
            "ndgain":       fetch_ndgain(cc),
            "iea":          fetch_iea(cc[:2].upper() if len(cc) == 3 else cc, cc),
            "cw_total":     fetch_cw_emissions(cc),
            "cw_sectors":   fetch_cw_emissions_by_sector(cc),
            "cw_ndc":       fetch_cw_ndc(cc),
        }

    with st.spinner("Chargement des données climatiques spécialisées…"):
        clim = load_climate_data(country_code)

    ndgain  = clim["ndgain"]
    iea     = clim["iea"]
    cw_tot  = clim["cw_total"]
    cw_sec  = clim["cw_sectors"]
    cw_ndc  = clim["cw_ndc"]

    # ── Valeurs pour le ribbon ─────────────────────────────────────────────────
    co2pc_kpi  = next((k for k in kpis if k["code"] == "EN.ATM.CO2E.PC"), None)
    forest_kpi = next((k for k in kpis if k["code"] == "AG.LND.FRST.ZS"), None)
    renew_kpi  = next((k for k in kpis if k["code"] == "EG.ELC.RNEW.ZS"), None)

    co2pc_val  = co2pc_kpi["value_display"]  if co2pc_kpi  and co2pc_kpi["value_raw"]  else "N/D"
    forest_val = forest_kpi["value_display"] if forest_kpi and forest_kpi["value_raw"] else "N/D"
    ndgain_score = f"{ndgain['score']:.1f}" if ndgain.get("score") else "N/D"
    ndgain_rank  = f"{ndgain['rank']}" if ndgain.get("rank") else "N/D"
    renew_iea   = f"{iea['renewable_share']:.1f}" if iea.get("renewable_share") else (
        renew_kpi["value_display"] if renew_kpi and renew_kpi["value_raw"] else "N/D"
    )

    st.markdown(f"""
    <div class="overview-ribbon">
        <strong>Émissions CO₂</strong> : <strong>{co2pc_val} t/hab.</strong> (Banque Mondiale).
        <strong>Renouvelables</strong> dans le mix électrique : <strong>{renew_iea}%</strong> (IEA {iea.get('year', '')}).
        <strong>Couverture forestière</strong> : <strong>{forest_val}%</strong> du territoire.
        <strong>Score ND-GAIN</strong> : <strong>{ndgain_score}/100</strong>
        (rang <strong>{ndgain_rank}/{ndgain.get('_total', 185)}</strong> — vulnérabilité climatique & capacité d'adaptation).
    </div>
    """, unsafe_allow_html=True)

    # ── SECTION 1 : KPIs Banque Mondiale ──────────────────────────────────────
    st.markdown('<div class="sub-label">Indicateurs environnementaux — Banque Mondiale WDI</div>', unsafe_allow_html=True)
    clim_codes = ["EN.ATM.CO2E.PC", "EG.ELC.RNEW.ZS", "AG.LND.FRST.ZS", "EG.USE.PCAP.KG.OE"]
    clim_kpis  = [k for k in kpis if k["code"] in clim_codes]

    cols = st.columns(max(len(clim_kpis), 1))
    for col, kpi in zip(cols, clim_kpis):
        with col:
            render_kpi_card(kpi)

    df_co2pc  = all_series.get("EN.ATM.CO2E.PC",    pd.DataFrame())
    df_co2kt  = all_series.get("EN.ATM.CO2E.KT",    pd.DataFrame())
    df_forest = all_series.get("AG.LND.FRST.ZS",    pd.DataFrame())
    df_renew  = all_series.get("EG.ELC.RNEW.ZS",    pd.DataFrame())

    col1, col2 = st.columns(2)
    with col1:
        if not df_co2pc.empty:
            fig = make_line_chart(
                {"EN.ATM.CO2E.PC": df_co2pc},
                {"EN.ATM.CO2E.PC": "CO₂ / habitant (t)"},
                fill=True, y_suffix=" t",
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            st.caption("*Banque Mondiale — EN.ATM.CO2E.PC*")
        else:
            no_data_placeholder("CO₂ / habitant")
    with col2:
        if not df_forest.empty:
            fig = make_line_chart(
                {"AG.LND.FRST.ZS": df_forest},
                {"AG.LND.FRST.ZS": "Couverture forestière (%)"},
                fill=True, y_suffix="%",
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            st.caption("*Banque Mondiale — AG.LND.FRST.ZS*")
        else:
            no_data_placeholder("Couverture forestière")

    # ── SECTION 2 : CLIMATE WATCH — Émissions GES ────────────────────────────
    st.markdown('<div class="sub-label">🌡️ Émissions de gaz à effet de serre — Climate Watch (CAIT)</div>', unsafe_allow_html=True)

    col3, col4 = st.columns(2)

    with col3:
        # Série temporelle émissions totales GES
        cw_series = cw_tot.get("series", [])
        if cw_series:
            df_cw = pd.DataFrame(cw_series).dropna(subset=["value"])
            fig = go.Figure(go.Scatter(
                x=df_cw["year"], y=df_cw["value"],
                fill="tozeroy",
                line=dict(color=COLORS["orange"], width=2),
                fillcolor="rgba(192,98,10,0.1)",
                name="GES totaux (MtCO₂eq)",
                hovertemplate="<b>%{y:.2f} MtCO₂eq</b><br>%{x}<extra></extra>",
            ))
            fig.update_layout(
                paper_bgcolor="white", plot_bgcolor="white",
                font=dict(size=11, color="#4a4843"),
                margin=dict(l=10, r=10, t=30, b=40),
                height=280,
                xaxis=dict(gridcolor="#e8e6e2"),
                yaxis=dict(gridcolor="#e8e6e2", ticksuffix=" Mt"),
                title=dict(text="Émissions GES totales (MtCO₂eq)", font=dict(size=12), x=0),
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            st.caption(f"*{cw_tot.get('source', 'Climate Watch — CAIT')} · [{cw_tot.get('source_url', '')}]({cw_tot.get('source_url', '')})*")
        elif not df_co2kt.empty:
            # Fallback Banque Mondiale si CW indisponible
            df_co2mt = df_co2kt.copy()
            df_co2mt["value"] = df_co2mt["value"] / 1000
            fig = make_bar_chart(df_co2mt, "EN.ATM.CO2E.KT", "CO₂ total (Mt)", y_suffix=" Mt", color=COLORS["orange"])
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            st.caption("*Banque Mondiale — EN.ATM.CO2E.KT (fallback)*")
        else:
            no_data_placeholder("Émissions GES Climate Watch")

    with col4:
        # Émissions par secteur (donut)
        if cw_sec:
            labels_sec = [s["sector"] for s in cw_sec]
            values_sec = [s["value"] for s in cw_sec]
            yr_sec = cw_sec[0].get("year", "") if cw_sec else ""
            palette = [COLORS["blue"], COLORS["orange"], COLORS["green"],
                       COLORS["red"], COLORS["gold"], COLORS["teal"]]
            fig = go.Figure(go.Pie(
                labels=labels_sec, values=values_sec,
                hole=0.42,
                marker=dict(colors=palette[:len(labels_sec)], line=dict(color="white", width=2)),
                textinfo="label+percent",
                textfont=dict(size=10),
                hovertemplate="<b>%{label}</b><br>%{value:.2f} MtCO₂eq<br>%{percent}<extra></extra>",
            ))
            fig.update_layout(
                paper_bgcolor="white",
                font=dict(size=10, color="#4a4843"),
                margin=dict(l=10, r=10, t=30, b=10),
                height=280,
                showlegend=False,
                title=dict(text=f"GES par secteur ({yr_sec})", font=dict(size=12), x=0),
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            st.caption(f"*Climate Watch — CAIT · [climatewatchdata.org](https://www.climatewatchdata.org/countries/{country_code})*")
        else:
            # Afficher les engagements NDC à la place
            ndc = cw_ndc
            st.markdown(f"""
            <div class="overview-ribbon">
                <strong>Engagements NDC — {selected_name}</strong><br>
                Données de répartition sectorielle non disponibles via l'API Climate Watch pour ce pays.<br>
                <a href="{ndc.get('source_url', 'https://www.climatewatchdata.org/')}" target="_blank">
                → Consulter le profil complet sur Climate Watch
                </a>
            </div>
            """, unsafe_allow_html=True)

    # ── Engagements NDC ────────────────────────────────────────────────────────
    if cw_ndc.get("unconditional_target") or cw_ndc.get("conditional_target"):
        st.markdown('<div class="sub-label">Engagements climatiques NDC — Climate Watch</div>', unsafe_allow_html=True)
        col_ndc1, col_ndc2 = st.columns(2)
        with col_ndc1:
            if cw_ndc.get("unconditional_target"):
                st.markdown(f"""
                <div class="overview-ribbon" style="border-left-color:#2e7d4f">
                    <strong>🎯 Objectif inconditionnel (NDC)</strong><br>
                    {cw_ndc['unconditional_target']}
                </div>
                """, unsafe_allow_html=True)
        with col_ndc2:
            if cw_ndc.get("conditional_target"):
                st.markdown(f"""
                <div class="overview-ribbon" style="border-left-color:#2563a8">
                    <strong>🎯 Objectif conditionnel (NDC)</strong><br>
                    {cw_ndc['conditional_target']}
                </div>
                """, unsafe_allow_html=True)

    # ── SECTION 3 : ND-GAIN — Vulnérabilité & Adaptation ─────────────────────
    st.markdown('<div class="sub-label">🛡️ Vulnérabilité climatique & Capacité d\'adaptation — ND-GAIN Index</div>', unsafe_allow_html=True)

    col5, col6 = st.columns(2)

    with col5:
        # Score ND-GAIN global historique
        ndg_series = ndgain.get("series_overall", [])
        vuln_series = ndgain.get("series_vulnerability", [])
        read_series = ndgain.get("series_readiness", [])

        if ndg_series:
            fig = go.Figure()
            df_ndg = pd.DataFrame(ndg_series)
            fig.add_trace(go.Scatter(
                x=df_ndg["year"], y=df_ndg["value"],
                name="Score ND-GAIN global",
                line=dict(color=COLORS["blue"], width=2.5),
                fill="tozeroy", fillcolor="rgba(37,99,168,0.07)",
                hovertemplate="<b>%{y:.1f}/100</b><br>%{x}<extra>ND-GAIN Global</extra>",
            ))
            if read_series:
                df_read = pd.DataFrame(read_series)
                fig.add_trace(go.Scatter(
                    x=df_read["year"], y=df_read["value"] * 100,
                    name="Readiness (×100)",
                    line=dict(color=COLORS["green"], width=1.5, dash="dot"),
                    hovertemplate="<b>%{y:.1f}</b><br>%{x}<extra>Readiness ×100</extra>",
                ))
            fig.update_layout(
                paper_bgcolor="white", plot_bgcolor="white",
                font=dict(size=11, color="#4a4843"),
                legend=dict(orientation="h", yanchor="bottom", y=-0.35, x=0),
                margin=dict(l=10, r=10, t=30, b=65),
                height=280,
                hovermode="x unified",
                xaxis=dict(gridcolor="#e8e6e2"),
                yaxis=dict(gridcolor="#e8e6e2"),
                title=dict(text="Score ND-GAIN (0–100) — tendance historique", font=dict(size=12), x=0),
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            st.caption(f"*{ndgain.get('source', 'ND-GAIN')} · [gain-new.crc.nd.edu](https://gain-new.crc.nd.edu/country/timor-leste)*")
        else:
            # KPIs ND-GAIN en fallback
            col_ng1, col_ng2, col_ng3 = st.columns(3)
            with col_ng1:
                score_str = f"{ndgain['score']:.1f}/100" if ndgain.get("score") else "N/D"
                st.markdown(f"""<div class="kpi-card"><div class="kpi-label">Score ND-GAIN ({ndgain.get('year','—')})</div>
                <div class="kpi-value">{score_str}</div></div>""", unsafe_allow_html=True)
            with col_ng2:
                rank_str = f"{ndgain['rank']}/185" if ndgain.get("rank") else "N/D"
                st.markdown(f"""<div class="kpi-card"><div class="kpi-label">Rang mondial</div>
                <div class="kpi-value">{rank_str}</div></div>""", unsafe_allow_html=True)
            with col_ng3:
                vuln_str = f"{ndgain['vulnerability']:.3f}" if ndgain.get("vulnerability") else "N/D"
                st.markdown(f"""<div class="kpi-card"><div class="kpi-label">Score vulnérabilité</div>
                <div class="kpi-value">{vuln_str}</div></div>""", unsafe_allow_html=True)

    with col6:
        # Radar sous-scores vulnérabilité
        vuln_comp = ndgain.get("vulnerability_components", {})
        read_comp = ndgain.get("readiness_components", {})

        if vuln_comp:
            cats = list(vuln_comp.keys())
            vals = [vuln_comp[c] for c in cats]
            vals_closed = vals + [vals[0]]
            cats_closed = cats + [cats[0]]
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=vals_closed, theta=cats_closed,
                fill="toself",
                fillcolor="rgba(192,57,43,0.12)",
                line=dict(color=COLORS["red"], width=2),
                name="Vulnérabilité (0–1)",
            ))
            if read_comp:
                # Représenter readiness sur les 3 premières dimensions
                r_cats = list(read_comp.keys())
                r_vals = [read_comp[c] for c in r_cats]
                # Aligner sur les cats vulnérabilité (3 premières)
                r_vals_full = r_vals[:3] + [None] * (len(cats) - len(r_vals[:3]))
                r_closed = r_vals_full + [r_vals_full[0]]
                r_cats_c = cats_closed
                fig.add_trace(go.Scatterpolar(
                    r=r_closed, theta=r_cats_c,
                    fill="toself",
                    fillcolor="rgba(46,125,79,0.08)",
                    line=dict(color=COLORS["green"], width=1.5, dash="dot"),
                    name="Readiness (partiel)",
                ))
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 1], gridcolor="#e8e6e2"),
                    angularaxis=dict(gridcolor="#e8e6e2"),
                    bgcolor="white",
                ),
                paper_bgcolor="white",
                font=dict(size=10, color="#4a4843"),
                legend=dict(orientation="h", yanchor="bottom", y=-0.15, x=0),
                margin=dict(l=30, r=30, t=40, b=50),
                height=280,
                title=dict(text="Composantes vulnérabilité & readiness ND-GAIN", font=dict(size=12), x=0),
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            st.caption(f"*{ndgain.get('source', 'ND-GAIN')} · Scores normalisés 0–1*")
        else:
            st.info("📭 Données de décomposition ND-GAIN non disponibles pour ce pays.")

    # ── SECTION 4 : IEA — Mix énergétique & transition ───────────────────────
    st.markdown('<div class="sub-label">⚡ Mix énergétique & transition — IEA World Energy Balances</div>', unsafe_allow_html=True)

    col7, col8 = st.columns(2)

    with col7:
        # Donut mix électrique
        mix = iea.get("mix_electricity", {})
        if mix:
            labels_mix = list(mix.keys())
            values_mix = list(mix.values())
            colors_mix = [COLORS["red"], COLORS["gold"], COLORS["blue"],
                          COLORS["green"], COLORS["teal"], COLORS["orange"]]
            fig = go.Figure(go.Pie(
                labels=labels_mix, values=values_mix,
                hole=0.42,
                marker=dict(colors=colors_mix[:len(labels_mix)], line=dict(color="white", width=2)),
                textinfo="label+percent",
                textfont=dict(size=10),
                hovertemplate="<b>%{label}</b><br>%{value:.1f}%<extra></extra>",
            ))
            fig.update_layout(
                paper_bgcolor="white",
                font=dict(size=10, color="#4a4843"),
                margin=dict(l=10, r=10, t=30, b=10),
                height=280,
                showlegend=False,
                title=dict(text=f"Mix de production électrique ({iea.get('year', '')})", font=dict(size=12), x=0),
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            st.caption(f"*{iea.get('source', 'IEA')} · [iea.org](https://www.iea.org/countries/timor-leste)*")
        else:
            # Fallback série Banque Mondiale renouvelables
            df_renew = all_series.get("EG.ELC.RNEW.ZS", pd.DataFrame())
            if not df_renew.empty:
                fig = make_line_chart(
                    {"EG.ELC.RNEW.ZS": df_renew},
                    {"EG.ELC.RNEW.ZS": "Part renouvelables (%)"},
                    fill=True, y_suffix="%",
                )
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
                st.caption("*Banque Mondiale — EG.ELC.RNEW.ZS (fallback)*")
            else:
                no_data_placeholder("Mix électrique IEA")

    with col8:
        # Évolution de la part renouvelable (IEA) vs émissions énergie
        iea_renew = iea.get("series_renewable", [])
        iea_co2e  = iea.get("series_co2_energy", [])

        if iea_renew or iea_co2e:
            fig = go.Figure()
            if iea_renew:
                df_ir = pd.DataFrame(iea_renew)
                fig.add_trace(go.Scatter(
                    x=df_ir["year"], y=df_ir["value"],
                    name="Renouvelables (% mix élec.)",
                    line=dict(color=COLORS["green"], width=2),
                    yaxis="y1",
                    hovertemplate="<b>%{y:.1f}%</b><br>%{x}<extra>Renouvelables</extra>",
                ))
            if iea_co2e:
                df_ic = pd.DataFrame(iea_co2e)
                fig.add_trace(go.Scatter(
                    x=df_ic["year"], y=df_ic["value"],
                    name="CO₂ énergie (Mt)",
                    line=dict(color=COLORS["orange"], width=2, dash="dot"),
                    yaxis="y2",
                    hovertemplate="<b>%{y:.2f} Mt</b><br>%{x}<extra>CO₂ énergie</extra>",
                ))
            fig.update_layout(
                paper_bgcolor="white", plot_bgcolor="white",
                font=dict(size=11, color="#4a4843"),
                legend=dict(orientation="h", yanchor="bottom", y=-0.35, x=0),
                margin=dict(l=10, r=55, t=30, b=65),
                height=280,
                hovermode="x unified",
                xaxis=dict(gridcolor="#e8e6e2"),
                yaxis=dict(gridcolor="#e8e6e2", ticksuffix="%", title="% renouvelable"),
                yaxis2=dict(overlaying="y", side="right", showgrid=False,
                            ticksuffix=" Mt", title="CO₂ énergie"),
                title=dict(text="Transition énergétique — tendance", font=dict(size=12), x=0),
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            st.caption(f"*{iea.get('source', 'IEA')} · [iea.org](https://www.iea.org/countries/timor-leste)*")
        else:
            no_data_placeholder("Transition énergétique IEA")

    # ── KPIs IEA complémentaires ───────────────────────────────────────────────
    if any([iea.get("renewable_share"), iea.get("co2_energy_mt"),
            iea.get("total_supply_mtoe"), iea.get("electricity_access")]):
        st.markdown('<div class="sub-label">Indicateurs IEA clés</div>', unsafe_allow_html=True)
        iea_kpi_data = [
            ("Part renouvelables", f"{iea['renewable_share']:.1f}%" if iea.get("renewable_share") else "N/D",
             f"Mix électrique {iea.get('year', '')}"),
            ("CO₂ lié à l'énergie", f"{iea['co2_energy_mt']:.2f} Mt" if iea.get("co2_energy_mt") else "N/D",
             f"Émissions secteur énergie {iea.get('year', '')}"),
            ("Approvisionnement énergie", f"{iea['total_supply_mtoe']:.2f} Mtep" if iea.get("total_supply_mtoe") else "N/D",
             "Total primary energy supply"),
            ("Accès électricité", f"{iea['electricity_access']:.1f}%" if iea.get("electricity_access") else "N/D",
             "Population avec accès"),
        ]
        iea_cols = st.columns(4)
        for col, (lbl, val, sub) in zip(iea_cols, iea_kpi_data):
            with col:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">{lbl}</div>
                    <div class="kpi-value" style="font-size:1.5rem">{val}</div>
                    <div class="kpi-unit">{sub}</div>
                    <div class="kpi-source"><a href="{iea.get('source_url','https://www.iea.org')}" target="_blank">{iea.get('source','IEA')}</a></div>
                </div>
                """, unsafe_allow_html=True)





# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("---")
st.caption(
    f"**{APP_TITLE}** · {APP_SUBTITLE} · "
    "Données récupérées en temps réel via API publique · "
    "Architecture extensible : FMI, Freedom House, V-Dem, WGI (Phase 2)"
)
