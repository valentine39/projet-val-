import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from config import CONFIG
from services.data_service import DataService

st.set_page_config(
    page_title="Économie Mondiale",
    page_icon="🌍",
    layout="wide"
)

# ── CSS ───────────────────────────────────────────────────────────
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #1e3a5f, #2d6a9f);
        border-radius: 12px;
        padding: 20px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        margin: 5px;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: bold;
        color: #f0c040;
    }
    .metric-label {
        font-size: 0.85rem;
        opacity: 0.85;
        margin-top: 5px;
    }
    .metric-delta {
        font-size: 0.75rem;
        margin-top: 8px;
        opacity: 0.7;
    }
</style>
""", unsafe_allow_html=True)

# ── Helpers ───────────────────────────────────────────────────────
def format_value(value: float, indicator: str) -> str:
    """Formate une valeur selon l'indicateur"""
    if indicator in ["PIB"]:
        if value >= 1e12:
            return f"{value/1e12:.2f} Md$"
        elif value >= 1e9:
            return f"{value/1e9:.2f} Md$"
        elif value >= 1e6:
            return f"{value/1e6:.2f} M$"
        else:
            return f"{value:,.0f} $"
    elif indicator == "PIB_HABITANT":
        return f"{value:,.0f} $"
    elif indicator == "POPULATION":
        if value >= 1e6:
            return f"{value/1e6:.2f} M"
        else:
            return f"{value/1e3:.0f} K"
    else:
        return f"{value:.1f} %"

def get_delta(df) -> str:
    """Calcule la variation entre les 2 dernières années"""
    if len(df) < 2:
        return ""
    last = df.iloc[-1]["valeur"]
    prev = df.iloc[-2]["valeur"]
    delta = ((last - prev) / prev) * 100
    arrow = "📈" if delta > 0 else "📉"
    return f"{arrow} {delta:+.1f}% vs {int(df.iloc[-2]['année'])}"

# ── Init ──────────────────────────────────────────────────────────
service = DataService()

# ── Header ────────────────────────────────────────────────────────
st.markdown("""
<div style="background: linear-gradient(135deg, #1e3a5f, #2d6a9f);
            padding: 25px 30px; border-radius: 15px; color: white; margin-bottom: 20px;">
    <h1 style="margin:0; font-size:2rem;">🌍 Fondamentaux Économiques</h1>
    <p style="margin:5px 0 0 0; opacity:0.8;">
        Données Banque Mondiale — Mise à jour quotidienne
    </p>
</div>
""", unsafe_allow_html=True)

# ── Chargement pays ───────────────────────────────────────────────
with st.spinner("Chargement des pays..."):
    countries = service.get_countries_list()

if not countries:
    st.error("❌ Impossible de charger la liste des pays")
    st.stop()

# ── Sélecteur ─────────────────────────────────────────────────────
country_names = [c["name"] for c in countries]
default_idx = country_names.index("Timor-Leste") if "Timor-Leste" in country_names else 0

col_select, col_info = st.columns([2, 3])

with col_select:
    selected_name = st.selectbox(
        "🔍 Sélectionner un pays",
        options=country_names,
        index=default_idx
    )

selected = next(c for c in countries if c["name"] == selected_name)

with col_info:
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.caption(f"🌐 **{selected['region']}**")
    c2.caption(f"🏛️ **{selected['capital'] or 'N/A'}**")
    c3.caption(f"🔑 **{selected['code']}**")

st.markdown("---")

# ── Chargement données ────────────────────────────────────────────
with st.spinner(f"📡 Chargement des données pour {selected_name}..."):
    data = service.get_country_data(selected["code"])

if not data:
    st.warning(f"⚠️ Aucune donnée disponible pour **{selected_name}**")
    st.stop()

# ── KPIs ──────────────────────────────────────────────────────────
st.markdown("### 📊 Indicateurs Clés")

kpi_indicators = ["PIB", "PIB_HABITANT", "CROISSANCE", "INFLATION", "CHOMAGE", "POPULATION"]
kpi_labels = {
    "PIB":          "PIB Total",
    "PIB_HABITANT": "PIB / Habitant",
    "CROISSANCE":   "Croissance",
    "INFLATION":    "Inflation",
    "CHOMAGE":      "Chômage",
    "POPULATION":   "Population",
}

cols = st.columns(len(kpi_indicators))

for col, key in zip(cols, kpi_indicators):
    with col:
        if key in data and not data[key].empty:
            df_ind = data[key]
            last_row = df_ind.iloc[-1]
            value_str = format_value(last_row["valeur"], key)
            delta_str = get_delta(df_ind)
            year = int(last_row["année"])

            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{value_str}</div>
                <div class="metric-label">{kpi_labels[key]}</div>
                <div class="metric-delta">{delta_str}<br>{year}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">N/A</div>
                <div class="metric-label">{kpi_labels[key]}</div>
            </div>
            """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Graphiques ────────────────────────────────────────────────────
st.markdown("### 📈 Évolution Historique")

col_left, col_right = st.columns(2)

# PIB
with col_left:
    if "PIB" in data and not data["PIB"].empty:
        df_pib = data["PIB"].copy()
        df_pib["valeur_affichee"] = df_pib["valeur"] / 1e9

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df_pib["année"],
            y=df_pib["valeur_affichee"],
            marker_color="#2d6a9f",
            name="PIB (Md$)"
        ))
        fig.update_layout(
            title=f"PIB — {selected_name}",
            xaxis_title="Année",
            yaxis_title="Milliards $",
            template="plotly_white",
            height=350
        )
        st.plotly_chart(fig, use_container_width=True)

# Croissance + Inflation
with col_right:
    fig2 = go.Figure()

    if "CROISSANCE" in data and not data["CROISSANCE"].empty:
        fig2.add_trace(go.Scatter(
            x=data["CROISSANCE"]["année"],
            y=data["CROISSANCE"]["valeur"],
            name="Croissance (%)",
            line=dict(color="#2d6a9f", width=2),
            mode="lines+markers"
        ))

    if "INFLATION" in data and not data["INFLATION"].empty:
        fig2.add_trace(go.Scatter(
            x=data["INFLATION"]["année"],
            y=data["INFLATION"]["valeur"],
            name="Inflation (%)",
            line=dict(color="#f0c040", width=2),
            mode="lines+markers"
        ))

    fig2.update_layout(
        title=f"Croissance & Inflation — {selected_name}",
        xaxis_title="Année",
        yaxis_title="%",
        template="plotly_white",
        height=350,
        legend=dict(orientation="h", y=-0.2)
    )
    st.plotly_chart(fig2, use_container_width=True)

# Population + Chômage
col_left2, col_right2 = st.columns(2)

with col_left2:
    if "POPULATION" in data and not data["POPULATION"].empty:
        df_pop = data["POPULATION"].copy()
        df_pop["valeur_affichee"] = df_pop["valeur"] / 1e6

        fig3 = px.area(
            df_pop,
            x="année",
            y="valeur_affichee",
            title=f"Population — {selected_name}",
            labels={"valeur_affichee": "Millions", "année": "Année"},
            color_discrete_sequence=["#2d6a9f"]
        )
        fig3.update_layout(template="plotly_white", height=350)
        st.plotly_chart(fig3, use_container_width=True)

with col_right2:
    if "CHOMAGE" in data and not data["CHOMAGE"].empty:
        fig4 = px.bar(
            data["CHOMAGE"],
            x="année",
            y="valeur",
            title=f"Chômage — {selected_name}",
            labels={"valeur": "%", "année": "Année"},
            color="valeur",
            color_continuous_scale=["#2d6a9f", "#f0c040", "#e63946"]
        )
        fig4.update_layout(template="plotly_white", height=350)
        st.plotly_chart(fig4, use_container_width=True)

# ── Données brutes ────────────────────────────────────────────────
st.markdown("---")
with st.expander("📋 Données brutes"):
    for nom, df in data.items():
        st.markdown(f"**{nom}**")
        st.dataframe(df, use_container_width=True)

# ── Footer ────────────────────────────────────────────────────────
st.markdown("---")
st.caption("📡 Source : Banque Mondiale API | 🔄 Cache 24h | 🛠️ Built with Streamlit")
