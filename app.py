import streamlit as st
from config import CONFIG
from scrapers.banque_mondiale import BanqueMondialeScraper

st.set_page_config(
    page_title=f"{CONFIG.COUNTRY_NAME} — Fondamentaux Économiques",
    layout="wide"
)

st.title(f"🇹🇱 {CONFIG.COUNTRY_NAME}")
st.markdown("### Fondamentaux Économiques")

# ── Test du scraper ───────────────────────────────────────────────
st.markdown("---")
st.markdown("### 🧪 Test Scraper Banque Mondiale")

scraper = BanqueMondialeScraper()

with st.spinner("🔄 Connexion à l'API Banque Mondiale..."):
    data = scraper.fetch_all()

# ── Résultats ─────────────────────────────────────────────────────
if data:
    st.success(f"✅ {len(data)} indicateurs récupérés !")

    for nom, df in data.items():
        with st.expander(f"📊 {nom} — {len(df)} années de données"):
            col1, col2 = st.columns([2, 1])

            with col1:
                st.dataframe(df, use_container_width=True)

            with col2:
                if not df.empty:
                    derniere = df.iloc[-1]
                    st.metric(
                        label=f"Dernière valeur ({int(derniere['année'])})",
                        value=f"{derniere['valeur']:,.2f}"
                    )
else:
    st.error("❌ Aucune donnée récupérée — Vérifiez votre connexion")
