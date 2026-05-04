# ── app.py ────────────────────────────────────────────────────────────────────
# Dashboard Économique Multi-Pays — Streamlit natif
# Structure : Header → Sidebar (pays + pilier + graphiques) → Pilier actif
# Graphiques : sélection dynamique par l'utilisateur via multiselect
# ─────────────────────────────────────────────────────────────────────────────

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from services.data_service import DataService
from config import (
    APP_TITLE, APP_SUBTITLE, INDICATORS, COLORS,
    PILIER_META, KPI_CODES, DATA_YEARS
)

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
    .stApp { background-color: #f5f4f0; }

    .dash-header {
        background: #1a3450;
        padding: 1.5rem 2rem;
        border-bottom: 3px solid #c8a84b;
        border-radius: 6px;
        margin-bottom: 1.5rem;
    }
    .dash-header h1 { color: #f0ece4; font-size: 1.4rem; margin: 0; font-weight: normal; }
    .dash-header h1 em { color: #c8a84b; font-style: normal; font-weight: bold; }
    .dash-header p { color: rgba(240,236,228,0.55); font-size: 0.75rem; margin: 0.4rem 0 0 0; }
    .badge-row { display: flex; gap: 0.5rem; flex-wrap: wrap; margin-top: 0.8rem; }
    .badge {
        background: rgba(255,255,255,0.07);
        border: 1px solid rgba(200,168,75,0.35);
        border-radius: 3px;
        padding: 0.2rem 0.6rem;
        font-size: 0.7rem;
        color: rgba(240,236,228,0.7);
    }

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

    .kpi-card {
        background: white;
        border: 1px solid #dddbd7;
        border-radius: 6px;
        padding: 1.2rem 1.4rem;
        height: 100%;
    }
    .kpi-label { font-size: 0.65rem; text-transform: uppercase; letter-spacing: 1px; color: #8a8780; margin-bottom: 0.5rem; font-weight: 600; }
    .kpi-value { font-size: 1.9rem; font-weight: bold; color: #1a3450; line-height: 1; }
    .kpi-unit { font-size: 0.75rem; color: #4a4843; margin-top: 0.3rem; }
    .kpi-delta-pos { color: #2e7d4f; font-size: 0.72rem; }
    .kpi-delta-neg { color: #c0392b; font-size: 0.72rem; }
    .kpi-delta-neu { color: #c0620a; font-size: 0.72rem; }
    .kpi-source { font-size: 0.62rem; color: #8a8780; margin-top: 0.5rem; border-top: 1px solid #e8e6e2; padding-top: 0.4rem; font-style: italic; }

    .sub-label { font-size: 0.68rem; text-transform: uppercase; letter-spacing: 1px; color: #8a8780; font-weight: 600; border-bottom: 1px solid #e8e6e2; padding-bottom: 0.4rem; margin: 1.5rem 0 1rem 0; }

    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# TRADUCTIONS
# ─────────────────────────────────────────────────────────────────────────────

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

def fr_revenu(s): return INCOME_LEVELS_FR.get(s, s)
def fr_region(s): return REGIONS_FR.get(s, s)


# ─────────────────────────────────────────────────────────────────────────────
# CATALOGUE DES GRAPHIQUES — source unique de vérité
# Chaque entrée décrit un graphique possible.
# pilier   : dans quel onglet il apparaît
# codes    : liste de codes WB à tracer ensemble
# type     : "bar" | "line" | "area"
# y_scale  : diviseur optionnel (ex: 1e9 pour Md$)
# y_suffix : suffixe affiché sur l'axe Y
# ─────────────────────────────────────────────────────────────────────────────

CHART_CATALOGUE = {
    # ── Pilier 1 ──────────────────────────────────────────────────────────────
    "population": {
        "title": "Population totale",
        "pilier": 1,
        "codes": ["SP.POP.TOTL"],
        "type": "area",
        "y_scale": 1e6,
        "y_suffix": " M hab.",
    },
    "esperance_vie": {
        "title": "Espérance de vie à la naissance",
        "pilier": 1,
        "codes": ["SP.DYN.LE00.IN"],
        "type": "line",
        "y_suffix": " ans",
    },
    "mortalite_infantile": {
        "title": "Mortalité infantile (‰ naissances vivantes)",
        "pilier": 1,
        "codes": ["SP.DYN.IMRT.IN"],
        "type": "bar",
        "y_suffix": " ‰",
    },
    "chomage": {
        "title": "Taux de chômage (% pop. active)",
        "pilier": 1,
        "codes": ["SL.UEM.TOTL.ZS"],
        "type": "bar",
        "y_suffix": "%",
    },
    # ── Pilier 2 ──────────────────────────────────────────────────────────────
    "pib_croissance": {
        "title": "Croissance du PIB réel (%)",
        "pilier": 2,
        "codes": ["NY.GDP.MKTP.KD.ZG"],
        "type": "bar",
        "y_suffix": "%",
    },
    "pib_habitant": {
        "title": "PIB par habitant (USD courants)",
        "pilier": 2,
        "codes": ["NY.GDP.PCAP.CD"],
        "type": "line",
        "y_suffix": " $",
    },
    "pib_nominal": {
        "title": "PIB nominal (milliards USD)",
        "pilier": 2,
        "codes": ["NY.GDP.MKTP.CD"],
        "type": "area",
        "y_scale": 1e9,
        "y_suffix": " Md$",
    },
    # ── Pilier 3 ──────────────────────────────────────────────────────────────
    "inflation": {
        "title": "Inflation — Indice des prix à la consommation (%)",
        "pilier": 3,
        "codes": ["FP.CPI.TOTL.ZG"],
        "type": "bar",
        "y_suffix": "%",
    },
    "inflation_chomage": {
        "title": "Inflation & Chômage (%)",
        "pilier": 3,
        "codes": ["FP.CPI.TOTL.ZG", "SL.UEM.TOTL.ZS"],
        "type": "line",
        "y_suffix": "%",
    },
    "solde_budgetaire": {
        "title": "Solde budgétaire (% du PIB)",
        "pilier": 3,
        "codes": ["GC.BAL.CASH.GD.ZS"],
        "type": "bar",
        "y_suffix": "% PIB",
    },
    "dette_publique": {
        "title": "Dette publique (% du PIB)",
        "pilier": 3,
        "codes": ["GC.DOD.TOTL.GD.ZS"],
        "type": "line",
        "y_suffix": "% PIB",
    },
    # ── Pilier 4 ──────────────────────────────────────────────────────────────
    "compte_courant": {
        "title": "Solde du compte courant (% du PIB)",
        "pilier": 4,
        "codes": ["BN.CAB.XOKA.GD.ZS"],
        "type": "bar",
        "y_suffix": "% PIB",
    },
    "ide": {
        "title": "Investissements directs étrangers entrants (% du PIB)",
        "pilier": 4,
        "codes": ["BX.KLT.DINV.WD.GD.ZS"],
        "type": "line",
        "y_suffix": "% PIB",
    },
    "equilibres_externes": {
        "title": "Compte courant & IDE (% du PIB)",
        "pilier": 4,
        "codes": ["BN.CAB.XOKA.GD.ZS", "BX.KLT.DINV.WD.GD.ZS"],
        "type": "line",
        "y_suffix": "% PIB",
    },
    # ── Pilier 5 ──────────────────────────────────────────────────────────────
    "credit_prive": {
        "title": "Crédit au secteur privé (% du PIB)",
        "pilier": 5,
        "codes": ["FD.AST.PRVT.GD.ZS"],
        "type": "line",
        "y_suffix": "% PIB",
    },
    "capitalisation_bancaire": {
        "title": "Ratio de fonds propres bancaires (%)",
        "pilier": 5,
        "codes": ["FB.BNK.CAPA.ZS"],
        "type": "line",
        "y_suffix": "%",
    },
    "inclusion_financiere": {
        "title": "Inclusion financière — compte bancaire (% adultes)",
        "pilier": 5,
        "codes": ["FX.OWN.TOTL.ZS"],
        "type": "bar",
        "y_suffix": "%",
    },
    # ── Pilier 6 ──────────────────────────────────────────────────────────────
    "co2_habitant": {
        "title": "Émissions CO₂ par habitant (tonnes)",
        "pilier": 6,
        "codes": ["EN.ATM.CO2E.PC"],
        "type": "line",
        "y_suffix": " t",
    },
    "co2_total": {
        "title": "Émissions CO₂ totales (kt)",
        "pilier": 6,
        "codes": ["EN.ATM.CO2E.KT"],
        "type": "area",
        "y_suffix": " kt",
    },
    "forets": {
        "title": "Couverture forestière (% du territoire)",
        "pilier": 6,
        "codes": ["AG.LND.FRST.ZS"],
        "type": "area",
        "y_suffix": "%",
    },
    "energie_renouvelable": {
        "title": "Part des énergies renouvelables dans la production électrique (%)",
        "pilier": 6,
        "codes": ["EG.ELC.RNEW.ZS"],
        "type": "line",
        "y_suffix": "%",
    },
    "aires_protegees": {
        "title": "Aires terrestres protégées (% du territoire)",
        "pilier": 6,
        "codes": ["ER.LND.PTLD.ZS"],
        "type": "bar",
        "y_suffix": "%",
    },
    "climat_nature": {
        "title": "Forêts & Aires protégées (% territoire)",
        "pilier": 6,
        "codes": ["AG.LND.FRST.ZS", "ER.LND.PTLD.ZS"],
        "type": "line",
        "y_suffix": "%",
    },
}

# KPIs affichés en haut de chaque pilier
PILIER_KPIS = {
    1: ["SP.POP.TOTL", "SL.UEM.TOTL.ZS", "SP.DYN.LE00.IN", "SP.DYN.IMRT.IN"],
    2: ["NY.GDP.MKTP.CD", "NY.GDP.PCAP.CD", "NY.GDP.MKTP.KD.ZG"],
    3: ["FP.CPI.TOTL.ZG", "GC.BAL.CASH.GD.ZS", "GC.DOD.TOTL.GD.ZS"],
    4: ["BN.CAB.XOKA.GD.ZS", "BX.KLT.DINV.WD.GD.ZS"],
    5: ["FD.AST.PRVT.GD.ZS", "FB.BNK.CAPA.ZS", "FX.OWN.TOTL.ZS"],
    6: ["EN.ATM.CO2E.PC", "AG.LND.FRST.ZS", "EG.ELC.RNEW.ZS", "ER.LND.PTLD.ZS"],
}

# Graphiques affichés par défaut à l'ouverture de chaque pilier
PILIER_DEFAULT_CHARTS = {
    1: ["population", "esperance_vie"],
    2: ["pib_croissance", "pib_habitant"],
    3: ["inflation", "solde_budgetaire"],
    4: ["compte_courant", "ide"],
    5: ["credit_prive", "inclusion_financiere"],
    6: ["co2_habitant", "energie_renouvelable"],
}


# ─────────────────────────────────────────────────────────────────────────────
# CACHE & SERVICE
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_resource
def get_service():
    return DataService()

@st.cache_data(ttl=3600, show_spinner=False)
def load_countries():
    return get_service().get_countries()

@st.cache_data(ttl=3600, show_spinner=False)
def load_all_series(country_code: str):
    return get_service().get_all_series(country_code)


# ─────────────────────────────────────────────────────────────────────────────
# FONCTIONS DE RENDU
# ─────────────────────────────────────────────────────────────────────────────

def render_kpi_card(kpi: dict):
    delta_html = ""
    if kpi["delta"] is not None:
        d = kpi["delta"]
        arrow = "↑" if d > 0 else ("↓" if d < 0 else "→")
        cls   = "pos" if d > 0 else ("neg" if d < 0 else "neu")
        sign  = "+" if d > 0 else ""
        delta_html = f'<div class="kpi-delta-{cls}">{arrow} {sign}{d:.1f}% {kpi["delta_label"]}</div>'

    year_str = f" ({kpi['year']})" if kpi["year"] else ""
    src = (f'<a href="{kpi["source_url"]}" target="_blank" style="color:#8a8780">{kpi["source"]}</a>'
           if kpi["source_url"] else kpi["source"])

    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">{kpi["label"]}</div>
        <div class="kpi-value">{kpi["value_display"]}</div>
        <div class="kpi-unit">{kpi["unit_display"]}{year_str}</div>
        {delta_html}
        <div class="kpi-source">{src}</div>
    </div>
    """, unsafe_allow_html=True)


def render_kpis_row(codes: list, all_kpis: list):
    selected = [k for k in all_kpis if k["code"] in codes]
    if not selected:
        return
    cols = st.columns(len(selected))
    for col, kpi in zip(cols, selected):
        with col:
            render_kpi_card(kpi)


def build_figure(chart_key: str, all_series: dict):
    """
    Construit un go.Figure depuis CHART_CATALOGUE.
    Retourne None si aucune donnée disponible pour ce pays.
    """
    cfg        = CHART_CATALOGUE[chart_key]
    codes      = cfg["codes"]
    chart_type = cfg["type"]
    y_suffix   = cfg.get("y_suffix", "")
    y_scale    = cfg.get("y_scale", 1)
    color_list = list(COLORS.values())

    fig      = go.Figure()
    has_data = False

    for i, code in enumerate(codes):
        df = all_series.get(code, pd.DataFrame(columns=["year", "value"]))
        if df is None or df.empty:
            continue
        df_clean = df.dropna(subset=["value"]).copy()
        if df_clean.empty:
            continue

        has_data = True
        df_clean["value"] = df_clean["value"] / y_scale
        color = color_list[i % len(color_list)]
        label = INDICATORS.get(code, {}).get("label", code)

        if chart_type == "bar":
            # Coloration positive/négative pour les indicateurs en %
            use_bicolor = (len(codes) == 1 and "%" in y_suffix)
            bar_colors = (
                [COLORS["green"] if v >= 0 else COLORS["red"] for v in df_clean["value"]]
                if use_bicolor else color
            )
            fig.add_trace(go.Bar(
                x=df_clean["year"],
                y=df_clean["value"],
                name=label,
                marker_color=bar_colors,
                marker_line_width=0,
            ))

        elif chart_type in ("line", "area"):
            fig.add_trace(go.Scatter(
                x=df_clean["year"],
                y=df_clean["value"],
                name=label,
                line=dict(color=color, width=2),
                fill="tozeroy" if chart_type == "area" else "none",
                mode="lines+markers",
                marker=dict(size=4),
                hovertemplate=f"<b>%{{y:.2f}}{y_suffix}</b><br>%{{x}}<extra>{label}</extra>",
            ))

    if not has_data:
        return None

    fig.update_layout(
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(size=11, color="#4a4843"),
        legend=dict(orientation="h", yanchor="bottom", y=-0.35, xanchor="left", x=0),
        margin=dict(l=10, r=10, t=10, b=70),
        hovermode="x unified",
        xaxis=dict(gridcolor="#e8e6e2", showgrid=True),
        yaxis=dict(gridcolor="#e8e6e2", showgrid=True, ticksuffix=y_suffix),
        height=290,
        showlegend=True,
    )
    return fig


def render_charts_grid(selected_keys: list, all_series: dict):
    """
    Affiche les graphiques sélectionnés en grille de 2 colonnes.
    Gère les données manquantes sans crash.
    """
    if not selected_keys:
        st.info("👈 Sélectionnez au moins un graphique dans le panneau latéral.")
        return

    pairs = [selected_keys[i:i+2] for i in range(0, len(selected_keys), 2)]
    for pair in pairs:
        cols = st.columns(len(pair))
        for col, key in zip(cols, pair):
            cfg = CHART_CATALOGUE[key]
            with col:
                st.markdown(f'<div class="sub-label">{cfg["title"]}</div>', unsafe_allow_html=True)
                fig = build_figure(key, all_series)
                if fig:
                    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
                    src_code = cfg["codes"][0]
                    src_url  = INDICATORS.get(src_code, {}).get("source_url", "")
                    src_lbl  = INDICATORS.get(src_code, {}).get("source", "Banque Mondiale — WDI")
                    codes_str = " · ".join(cfg["codes"])
                    caption = f"*[{src_lbl}]({src_url}) — {codes_str}*" if src_url else f"*{src_lbl} — {codes_str}*"
                    st.caption(caption)
                else:
                    st.info("📭 Données non disponibles pour ce pays.")


def ribbon(text: str):
    st.markdown(f'<div class="overview-ribbon">{text}</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 🌍 Pays")
    with st.spinner("Chargement…"):
        countries_df = load_countries()

    if countries_df.empty:
        st.error("⚠️ Impossible de charger la liste des pays.")
        st.stop()

    country_names = countries_df["name"].tolist()
    default_idx   = country_names.index("Timor-Leste") if "Timor-Leste" in country_names else 0
    selected_name = st.selectbox("Pays", country_names, index=default_idx, label_visibility="collapsed")

    row            = countries_df[countries_df["name"] == selected_name].iloc[0]
    country_code   = row["code"]
    country_region = fr_region(row.get("region", ""))
    country_income = fr_revenu(row.get("income_level", ""))

    st.markdown(f"**Code ISO :** `{country_code}`")
    if country_region: st.caption(f"📍 {country_region}")
    if country_income: st.caption(f"💰 {country_income}")

    st.markdown("---")

    # ── Navigation pilier ────────────────────────────────────────────────────
    st.markdown("### 📑 Pilier analytique")
    pilier_options = {f"{v['icon']} {k} — {v['label']}": k for k, v in PILIER_META.items()}
    selected_label = st.radio("Pilier", list(pilier_options.keys()), label_visibility="collapsed")
    active_pilier  = pilier_options[selected_label]

    st.markdown("---")

    # ── Sélection dynamique des graphiques ───────────────────────────────────
    st.markdown("### 📊 Graphiques à afficher")

    available       = {k: v for k, v in CHART_CATALOGUE.items() if v["pilier"] == active_pilier}
    available_labels = {k: v["title"] for k, v in available.items()}
    defaults        = [k for k in PILIER_DEFAULT_CHARTS.get(active_pilier, []) if k in available]

    selected_chart_keys = st.multiselect(
        "Graphiques",
        options=list(available_labels.keys()),
        default=defaults,
        format_func=lambda k: available_labels[k],
        label_visibility="collapsed",
        placeholder="Choisir des graphiques…",
    )

    st.markdown("---")
    st.caption("Phase 1 · Banque Mondiale WDI")
    st.caption("Phase 2 · FMI · Freedom House · V-Dem · WGI")


# ─────────────────────────────────────────────────────────────────────────────
# CHARGEMENT DONNÉES
# ─────────────────────────────────────────────────────────────────────────────

with st.spinner(f"Chargement — {selected_name}…"):
    all_series = load_all_series(country_code)

svc      = get_service()
all_kpis = svc.get_kpis(country_code, all_series)
summary_df = svc.get_summary_table(country_code, all_series)


# ─────────────────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────────────────

gdp_kpi  = next((k for k in all_kpis if k["code"] == "NY.GDP.MKTP.CD"), None)
pop_kpi  = next((k for k in all_kpis if k["code"] == "SP.POP.TOTL"), None)
gdp_badge = f"PIB ~{gdp_kpi['value_display']} Md$" if gdp_kpi and gdp_kpi["value_raw"] else "PIB N/D"
pop_badge = f"Pop. {pop_kpi['value_display']} M hab." if pop_kpi and pop_kpi["value_raw"] else ""

st.markdown(f"""
<div class="dash-header">
    <h1>{selected_name} — <em>Fondamentaux Économiques</em></h1>
    <p>{APP_SUBTITLE} · Fenêtre historique : {DATA_YEARS} ans</p>
    <div class="badge-row">
        <span class="badge">{gdp_badge}</span>
        {'<span class="badge">' + pop_badge + '</span>' if pop_badge else ''}
        <span class="badge">{country_region}</span>
        <span class="badge">{country_income}</span>
        <span class="badge">ISO : {country_code}</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# CONTENU PAR PILIER
# ─────────────────────────────────────────────────────────────────────────────

pm = PILIER_META[active_pilier]
st.markdown(f"### {pm['icon']} Pilier {active_pilier} — {pm['label']}")
st.caption(pm["description"])

# ── Helper pour extraire une valeur KPI ──────────────────────────────────────
def kv(code):
    k = next((x for x in all_kpis if x["code"] == code), None)
    return (k["value_display"], k["year"]) if k and k["value_raw"] else ("N/D", "")

# ── Ribbon contextuel par pilier ─────────────────────────────────────────────

if active_pilier == 1:
    pop, pop_yr = kv("SP.POP.TOTL")
    unem, _     = kv("SL.UEM.TOTL.ZS")
    life, _     = kv("SP.DYN.LE00.IN")
    ribbon(
        f"<strong>{selected_name}</strong> · Population : <strong>{pop} M hab.</strong> ({pop_yr}) · "
        f"Chômage : <strong>{unem}%</strong> · Espérance de vie : <strong>{life} ans</strong> · "
        f"Région : <strong>{country_region}</strong> · Revenu : <strong>{country_income}</strong>"
    )

elif active_pilier == 2:
    gdp, _    = kv("NY.GDP.MKTP.CD")
    growth, _ = kv("NY.GDP.MKTP.KD.ZG")
    gdppc, _  = kv("NY.GDP.PCAP.CD")
    ribbon(
        f"PIB nominal : <strong>{gdp} Md USD</strong> · "
        f"Croissance réelle : <strong>{growth}%</strong> · "
        f"PIB / habitant : <strong>{gdppc} USD</strong>"
    )

elif active_pilier == 3:
    infl, _  = kv("FP.CPI.TOTL.ZG")
    solde, _ = kv("GC.BAL.CASH.GD.ZS")
    dette, _ = kv("GC.DOD.TOTL.GD.ZS")
    ribbon(
        f"Inflation (IPC) : <strong>{infl}%</strong> · "
        f"Solde budgétaire : <strong>{solde}% du PIB</strong> · "
        f"Dette publique : <strong>{dette}% du PIB</strong>"
    )

elif active_pilier == 4:
    cab, _ = kv("BN.CAB.XOKA.GD.ZS")
    ide, _ = kv("BX.KLT.DINV.WD.GD.ZS")
    ribbon(
        f"Solde compte courant : <strong>{cab}% du PIB</strong> · "
        f"IDE entrants : <strong>{ide}% du PIB</strong>"
    )

elif active_pilier == 5:
    cred, _ = kv("FD.AST.PRVT.GD.ZS")
    incl, _ = kv("FX.OWN.TOTL.ZS")
    cap, _  = kv("FB.BNK.CAPA.ZS")
    ribbon(
        f"Crédit privé / PIB : <strong>{cred}%</strong> · "
        f"Inclusion financière : <strong>{incl}% des adultes</strong> · "
        f"Ratio fonds propres : <strong>{cap}%</strong>"
    )

elif active_pilier == 6:
    co2, _   = kv("EN.ATM.CO2E.PC")
    foret, _ = kv("AG.LND.FRST.ZS")
    renew, _ = kv("EG.ELC.RNEW.ZS")
    ribbon(
        f"CO₂ / habitant : <strong>{co2} t</strong> · "
        f"Couverture forestière : <strong>{foret}%</strong> · "
        f"Électricité renouvelable : <strong>{renew}%</strong>"
    )

# ── KPIs du pilier ────────────────────────────────────────────────────────────

st.markdown('<div class="sub-label">Indicateurs clés</div>', unsafe_allow_html=True)
render_kpis_row(PILIER_KPIS.get(active_pilier, []), all_kpis)

# ── Graphiques dynamiques ─────────────────────────────────────────────────────

st.markdown('<div class="sub-label">Séries temporelles</div>', unsafe_allow_html=True)
render_charts_grid(selected_chart_keys, all_series)


# ─────────────────────────────────────────────────────────────────────────────
# TABLEAU SOURCÉ
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("---")
st.markdown('<div class="sub-label">📋 Tableau récapitulatif — tous les indicateurs</div>', unsafe_allow_html=True)

if not summary_df.empty:
    display_df = summary_df[["Indicateur", "Valeur", "Année", "Unité", "Source"]].copy()
    display_df["Lien source"] = summary_df["Lien"]
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={"Lien source": st.column_config.LinkColumn("Lien source", display_text="🔗 Voir")},
        height=min(50 + len(display_df) * 38, 620),
    )
else:
    st.warning("Aucune donnée disponible pour ce pays.")


# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("---")
st.caption(
    f"**{APP_TITLE}** · {APP_SUBTITLE} · "
    "Données temps réel via API Banque Mondiale (WDI) · "
    "Architecture extensible Phase 2 : FMI · Freedom House · V-Dem · WGI"
)
