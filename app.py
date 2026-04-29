import streamlit as st
from config import CONFIG

st.set_page_config(
    page_title=f"{CONFIG.COUNTRY_NAME} — Fondamentaux Économiques",
    layout="wide"
)

st.title(f"🇹🇱 {CONFIG.COUNTRY_NAME}")
st.markdown("### Fondamentaux Économiques")
st.info("⚙️ Application en construction — Step 1 OK")

# Vérification config
with st.expander("🔍 Vérifier la configuration"):
    st.json({
        "Pays": CONFIG.COUNTRY_NAME,
        "Code": CONFIG.COUNTRY_CODE,
        "Cache TTL": f"{CONFIG.CACHE_TTL}s",
        "Indicateurs": CONFIG.INDICATORS
    })
