import streamlit as st
from services.data_service import DataService

st.set_page_config(
    page_title="Économie Mondiale",
    page_icon="🌍",
    layout="wide"
)

# ── Init ──────────────────────────────────────────────────────────
service = DataService()

# ── Header ────────────────────────────────────────────────────────
st.title("🌍 Fondamentaux Économiques")
st.markdown("Sélectionnez un pays pour afficher ses indicateurs clés.")
st.markdown("---")

# ── Chargement liste pays ─────────────────────────────────────────
with st.spinner("Chargement des pays..."):
    countries = service.get_countries_list()

if not countries:
    st.error("❌ Impossible de charger la liste des pays")
    st.stop()

# ── Sélecteur ─────────────────────────────────────────────────────
country_names = [c["name"] for c in countries]

selected_name = st.selectbox(
    "🔍 Rechercher un pays",
    options=country_names,
    index=country_names.index("Timor-Leste") if "Timor-Leste" in country_names else 0,
    placeholder="Tapez un nom de pays..."
)

# Récupérer le pays sélectionné
selected = next(c for c in countries if c["name"] == selected_name)

# ── Infos du pays ─────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)
with col1:
    st.caption(f"🌐 Région : **{selected['region']}**")
with col2:
    st.caption(f"🏛️ Capitale : **{selected['capital']}**")
with col3:
    st.caption(f"🔑 Code : **{selected['code']}**")

st.markdown("---")

# ── Chargement des données ────────────────────────────────────────
with st.spinner(f"📡 Chargement des données pour {selected_name}..."):
    data = service.get_country_data(selected["code"])

if not data:
    st.warning(f"⚠️ Aucune donnée disponible pour {selected_name}")
    st.stop()

# ── Affichage brut (temporaire) ───────────────────────────────────
st.success(f"✅ {len(data)} indicateurs chargés pour **{selected_name}**")

for nom, df in data.items():
    with st.expander(f"📊 {nom}"):
        st.dataframe(df, use_container_width=True)
