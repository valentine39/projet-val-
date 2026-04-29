import streamlit as st
from config import CONFIG
from services.data_service import DataService

st.set_page_config(
    page_title="Économie Mondiale",
    layout="wide"
)

# ── Init ──────────────────────────────────────────────────────────
service = DataService()

st.title("🌍 Fondamentaux Économiques")

# ── Test liste des pays ───────────────────────────────────────────
st.markdown("### 🧪 Test Liste des Pays")

with st.spinner("Chargement des pays..."):
    countries = service.get_countries_list()

if countries:
    st.success(f"✅ {len(countries)} pays disponibles")

    # Sélecteur test
    country_names = [c["name"] for c in countries]
    selected_name = st.selectbox("Choisir un pays", country_names)

    # Retrouver le code du pays sélectionné
    selected = next(c for c in countries if c["name"] == selected_name)
    st.info(f"Code : `{selected['code']}` | Région : {selected['region']}")

    # ── Test chargement données ───────────────────────────────────
    if st.button("📊 Charger les données"):
        with st.spinner(f"Chargement des données pour {selected_name}..."):
            data = service.get_country_data(selected["code"])

        if data:
            st.success(f"✅ {len(data)} indicateurs récupérés !")
            for nom, df in data.items():
                with st.expander(f"📈 {nom}"):
                    st.dataframe(df, use_container_width=True)
        else:
            st.warning("⚠️ Aucune donnée disponible pour ce pays")
else:
    st.error("❌ Impossible de charger la liste des pays")
