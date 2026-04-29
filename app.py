import streamlit as st
import plotly.graph_objects as go
from config import CONFIG
from services.data_service import DataService

# ── Config ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Économie Mondiale",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS Custom ────────────────────────────────────────────────────
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #1e3a5f, #2d6a9f);
        border-radius: 12px;
        padding: 20px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        height: 140px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .metric-emoji {
        font-size: 2.5rem;
        margin-bottom: 8px;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: bold;
        color: #f0c040;
    }
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.85;
        margin-top: 5px;
    }
</style>
""", unsafe_allow_html=True)

# ── Init ──────────────────────────────────────────────────────────
service = DataService()

# ── Sidebar ───────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🌍 Sélection du Pays")
    
    with st.spinner("Chargement des pays..."):
        countries = service.get_countries_list()
    
    if not countries:
        st.error("❌ Impossible de charger les pays")
        st.stop()
    
    # Recherche pays
    search = st.text_input("🔍 Rechercher", placeholder="Ex: France, Timor...")
    
    if search:
        filtered = [c for c in countries if search.lower() in c["name"].lower()]
    else:
        filtered = countries
    
    if filtered:
        country_names = [c["name"] for c in filtered]
        selected_name = st.selectbox("Pays", country_names, label_visibility="collapsed")
        
        selected_country = next(c for c in countries if c["name"] == selected_name)
    else:
        st.warning("Aucun pays trouvé")
        st.stop()
    
    st.markdown("---")
    st.markdown(f"""
    **Code ISO** : `{selected_country['code']}`  
    **Région** : {selected_country['region']}  
    **Capitale** : {selected_country.get('capital', 'N/A')}
    """)

# ── Chargement Données ────────────────────────────────────────────
st.markdown(f"# 🌍 {selected_name}")

with st.spinner(f"Chargement des données pour {selected_name}..."):
    data = service.get_country_data(selected_country["code"])

if not data:
    st.error(f"❌ Aucune donnée disponible pour {selected_name}")
    st.stop()

st.success(f"✅ Données chargées — Dernière année : {data['PIB'].iloc[-1]['année']}")

# ── KPIs ──────────────────────────────────────────────────────────
st.markdown("## 📊 Indicateurs Clés")

cols = st.columns(len(CONFIG.LABELS))

for col, (key, meta) in zip(cols, CONFIG.LABELS.items()):
    if key in data and not data[key].empty:
        df = data[key]
        last = df.iloc[-1]
        
        # Formatage selon l'unité
        if meta["unit"] == "Md$":
            value = f"{last['valeur']/1e9:.1f} Md$"
        elif meta["unit"] == "M":
            value = f"{last['valeur']/1e6:.1f} M"
        elif key == "PIB_HABITANT":
            value = f"{last['valeur']:,.0f} $"
        else:
            value = f"{last['valeur']:.1f}%"
        
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-emoji">{meta['emoji']}</div>
                <div class="metric-value">{value}</div>
                <div class="metric-label">{meta['label']}</div>
            </div>
            """, unsafe_allow_html=True)

# ── Graphiques ────────────────────────────────────────────────────
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📈 Évolution du PIB")
    
    if "PIB" in data and not data["PIB"].empty:
        df_pib = data["PIB"].copy()
        df_pib["PIB_Md"] = df_pib["valeur"] / 1e9
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df_pib["année"],
            y=df_pib["PIB_Md"],
            marker_color="#2d6a9f",
            name="PIB (Md$)"
        ))
        
        fig.update_layout(
            template="plotly_white",
            yaxis_title="PIB (Milliards $)",
            xaxis_title="Année",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("### 📊 Croissance Économique")
    
    if "CROISSANCE" in data and not data["CROISSANCE"].empty:
        df_crois = data["CROISSANCE"]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_crois["année"],
            y=df_crois["valeur"],
            mode="lines+markers",
            line=dict(color="#f0c040", width=3),
            marker=dict(size=8),
            name="Croissance (%)"
        ))
        
        fig.add_hline(y=0, line_dash="dash", line_color="red", opacity=0.5)
        
        fig.update_layout(
            template="plotly_white",
            yaxis_title="Croissance (%)",
            xaxis_title="Année",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)

# ── Tableau de données brutes ─────────────────────────────────────
with st.expander("📋 Voir les données brutes"):
    tabs = st.tabs(list(CONFIG.LABELS.keys()))
    
    for tab, key in zip(tabs, CONFIG.LABELS.keys()):
        with tab:
            if key in data:
                st.dataframe(data[key], use_container_width=True)
