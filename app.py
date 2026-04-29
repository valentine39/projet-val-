import streamlit as st
from config import CONFIG
from services.data_service import DataService
from components.kpis import render_kpis
from components.charts import render_pib_chart, render_inflation_chomage

st.set_page_config(
    page_title="Fondamentaux Économiques Mondiaux",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS ───────────────────────────────────────────────────────────
st.markdown("""
<style>
    .header-box {
        background: linear-gradient(135deg, #1e3a5f 0%, #2d6a9f 100%);
        padding: 24px 30px;
        border-radius: 12px;
        color: white;
        margin-bottom: 20px;
    }
    .header-box h1 { margin: 0; font-size: 2rem; }
    .header-box p  { margin: 4px 0 0 0; opacity: 0.85; }
    [data-testid="stMetricValue"] { font-size: 1.4rem; }
</style>
""", unsafe_allow_html=True)

# ── Init ──────────────────────────────────────────────────────────
service = DataService()

# ── Sidebar : Sélecteur de Pays ───────────────────────────────────
with st.sidebar:
    st.markdown("## 🌍 Sélection du Pays")

    with st.spinner("Chargement des pays..."):
        countries = service.get_countries_list()

    if not countries:
        st.error("Impossible de charger la liste des pays")
        st.stop()

    # Filtre par région
    regions = sorted(set(c["region"] for c in countries if c["region"]))
    region_choice = st.selectbox("Filtrer par région", ["Toutes"] + regions)

    # Liste filtrée
    filtered = countries if region_choice == "Toutes" else [
        c for c in countries if c["region"] == region_choice
    ]

    country_names = [c["name"] for c in filtered]

    # Pré-sélectionner Timor-Leste si dispo
    default_idx = next(
        (i for i, c in enumerate(filtered) if c["code"] == CONFIG.COUNTRY_CODE),
        0
    )

    selected_name = st.selectbox("Pays", country_names, index=default_idx)
    selected = next(c for c in filtered if c["name"] == selected_name)

    st.markdown("---")
    st.markdown(f"**Code :** `{selected['code']}`")
    st.markdown(f"**Région :** {selected['region']}")
    if selected.get("capital"):
        st.markdown(f"**Capitale :** {selected['capital']}")

    st.markdown("---")
    if st.button("🔄 Forcer la mise à jour"):
        st.cache_data.clear()
        st.rerun()

    st.markdown("**Source :** Banque Mondiale")
    st.markdown("**Mise à jour :** cache 24h")

# ── Header ────────────────────────────────────────────────────────
st.markdown(f"""
<div class="header-box">
    <h1>🌍 {selected_name}</h1>
    <p>Fondamentaux Économiques — Données Banque Mondiale</p>
</div>
""", unsafe_allow_html=True)

# ── Chargement Données ────────────────────────────────────────────
with st.spinner(f"Chargement des données pour {selected_name}..."):
    data = service.get_country_data(selected["code"])

if not data:
    st.warning(f"⚠️ Aucune donnée disponible pour **{selected_name}**.")
    st.stop()

# ── KPIs ──────────────────────────────────────────────────────────
render_kpis(data)

st.markdown("---")

# ── Graphiques ────────────────────────────────────────────────────
col1, col2 = st.columns([3, 2])

with col1:
    render_pib_chart(
        data.get("PIB"),
        data.get("CROISSANCE"),
        selected_name
    )

with col2:
    render_inflation_chomage(
        data.get("INFLATION"),
        data.get("CHOMAGE")
    )

# ── Données brutes ────────────────────────────────────────────────
with st.expander("📋 Données brutes"):
    for nom, df in data.items():
        st.markdown(f"**{nom}**")
        st.dataframe(df, use_container_width=True)
