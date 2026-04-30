import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from config import CONFIG
from services.data_service import DataService

st.set_page_config(
    page_title="Fondamentaux Économiques",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed"  # Pas de sidebar comme le HTML
)

# ── CSS Exact du HTML ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Lora:wght@400;600&display=swap');
    
    /* Variables CSS du HTML */
    :root {
        --bg: #f5f4f0;
        --surface: #ffffff;
        --border: #dddbd7;
        --text: #1a1916;
        --text2: #4a4843;
        --muted: #8a8780;
        --accent: #2b4a6b;
        --accent2: #1a3450;
        --red: #c0392b;
        --orange: #c0620a;
        --green: #2e7d4f;
        --gold: #8b6914;
    }
    
    /* Reset global */
    .main {
        background: var(--bg);
        font-family: 'Georgia', 'Times New Roman', serif;
        color: var(--text);
        font-size: 14px;
        line-height: 1.65;
    }
    
    /* Header style HTML */
    .main-header {
        background: var(--accent2);
        padding: 1.8rem 2.5rem;
        border-bottom: 3px solid #c8a84b;
        margin: -1rem -1rem 2rem -1rem;
    }
    
    .main-header h1 {
        font-size: 1.5rem;
        font-weight: normal;
        color: #f0ece4;
        letter-spacing: 0.3px;
        margin: 0;
    }
    
    .main-header h1 em {
        color: #c8a84b;
        font-style: normal;
        font-weight: bold;
    }
    
    .main-header p {
        color: rgba(240,236,228,0.55);
        font-size: 0.75rem;
        margin-top: 0.35rem;
        letter-spacing: 0.2px;
    }
    
    .header-badges {
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
        margin-top: 1rem;
    }
    
    .badge {
        background: rgba(255,255,255,0.07);
        border: 1px solid rgba(200,168,75,0.35);
        border-radius: 3px;
        padding: 0.25rem 0.7rem;
        font-size: 0.7rem;
        color: rgba(240,236,228,0.7);
        font-family: 'Segoe UI', sans-serif;
        letter-spacing: 0.3px;
    }
    
    .badge.warn { border-color: rgba(192,98,10,0.6); color: #e8a96a; }
    .badge.danger { border-color: rgba(192,57,43,0.6); color: #e8968c; }
    .badge.ok { border-color: rgba(46,125,79,0.6); color: #8ecfaa; }
    
    /* Navigation tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: var(--surface);
        border-bottom: 1px solid var(--border);
        gap: 0;
        position: sticky;
        top: 0;
        z-index: 100;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 0.85rem 1.3rem;
        font-size: 0.78rem;
        font-family: 'Segoe UI', sans-serif;
        font-weight: 500;
        color: var(--muted);
        border-bottom: 2px solid transparent;
        background: none;
    }
    
    .stTabs [aria-selected="true"] {
        color: var(--accent);
        border-bottom-color: var(--accent);
        font-weight: 600;
        background: none;
    }
    
    /* Section header */
    .section-header {
        display: flex;
        align-items: flex-start;
        gap: 1rem;
        margin-bottom: 1.8rem;
        padding-bottom: 1.2rem;
        border-bottom: 1px solid var(--border);
    }
    
    .section-icon {
        font-size: 1.2rem;
        opacity: 0.7;
        padding-top: 0.15rem;
    }
    
    .section-header h2 {
        font-size: 1.2rem;
        font-weight: normal;
        color: var(--accent2);
        letter-spacing: 0.2px;
        margin: 0;
    }
    
    .section-header p {
        color: var(--muted);
        font-size: 0.76rem;
        margin-top: 0.25rem;
    }
    
    /* Overview ribbon */
    .overview-ribbon {
        background: #e8eef4;
        border: 1px solid #c8d8e8;
        border-left: 3px solid var(--accent);
        border-radius: 3px;
        padding: 1rem 1.2rem;
        margin-bottom: 1.5rem;
        font-size: 0.8rem;
        color: var(--text2);
        line-height: 1.6;
    }
    
    .overview-ribbon strong {
        color: var(--accent2);
    }
    
    /* Card KPI */
    .card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 4px;
        padding: 1.2rem 1.4rem;
    }
    
    .card-title {
        font-size: 0.68rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: var(--muted);
        margin-bottom: 0.6rem;
        font-family: 'Segoe UI', sans-serif;
        font-weight: 600;
    }
    
    .kpi {
        font-size: 1.9rem;
        font-weight: bold;
        color: var(--accent2);
        line-height: 1;
    }
    
    .kpi-sub {
        font-size: 0.75rem;
        color: var(--text2);
        margin-top: 0.4rem;
    }
    
    .kpi-trend {
        display: inline-flex;
        align-items: center;
        gap: 0.25rem;
        font-size: 0.7rem;
        margin-top: 0.4rem;
        padding: 0.2rem 0.5rem;
        border-radius: 2px;
    }
    
    .trend-up { background: #eef6f1; color: var(--green); }
    .trend-down { background: #fdf0ee; color: var(--red); }
    .trend-neutral { background: #fef3e8; color: var(--orange); }
    
    .source-tag {
        font-size: 0.65rem;
        color: var(--muted);
        margin-top: 0.6rem;
        font-style: italic;
        border-top: 1px solid #e8e6e2;
        padding-top: 0.4rem;
    }
    
    /* Alert boxes */
    .alert {
        border-radius: 3px;
        padding: 0.85rem 1rem;
        font-size: 0.78rem;
        border-left: 3px solid;
        margin-bottom: 0.85rem;
        line-height: 1.55;
    }
    
    .alert-warn { background: #fef3e8; border-color: #c0620a; color: #5a3008; }
    .alert-danger { background: #fdf0ee; border-color: #c0392b; color: #5a1a14; }
    .alert-ok { background: #eef6f1; border-color: #2e7d4f; color: #15402a; }
    .alert-info { background: #eef3fa; border-color: #2563a8; color: #12305a; }
    .alert-gold { background: #faf4e6; border-color: #8b6914; color: #4a3608; }
    
    .alert strong {
        display: block;
        margin-bottom: 0.25rem;
        font-size: 0.8rem;
    }
    
    /* Sub-label */
    .sub-label {
        font-size: 0.68rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: var(--muted);
        margin-bottom: 0.8rem;
        margin-top: 1.5rem;
        font-weight: 600;
        padding-bottom: 0.4rem;
        border-bottom: 1px solid #e8e6e2;
    }
    
    /* Progress bar */
    .progress-wrap {
        margin-bottom: 0.85rem;
    }
    
    .progress-label {
        display: flex;
        justify-content: space-between;
        font-size: 0.74rem;
        margin-bottom: 0.3rem;
        color: var(--text2);
    }
    
    .progress-bar {
        height: 5px;
        background: #edecea;
        border-radius: 2px;
        overflow: hidden;
    }
    
    .progress-fill {
        height: 100%;
        border-radius: 2px;
    }
    
    /* Data table */
    .data-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.78rem;
        margin-top: 0.5rem;
    }
    
    .data-table th {
        background: #f9f8f6;
        padding: 0.5rem 0.75rem;
        text-align: left;
        color: var(--muted);
        font-weight: 600;
        font-size: 0.68rem;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        border-bottom: 1px solid var(--border);
    }
    
    .data-table td {
        padding: 0.5rem 0.75rem;
        border-bottom: 1px solid #e8e6e2;
        color: var(--text2);
    }
    
    .data-table tr:last-child td {
        border-bottom: none;
    }
    
    .data-table tr:hover td {
        background: #f9f8f6;
    }
    
    /* Pill */
    .pill {
        display: inline-block;
        padding: 0.15rem 0.5rem;
        border-radius: 2px;
        font-size: 0.68rem;
        font-weight: 600;
    }
    
    .pill-red { background: #fdf0ee; color: var(--red); }
    .pill-orange { background: #fef3e8; color: var(--orange); }
    .pill-green { background: #eef6f1; color: var(--green); }
    .pill-blue { background: #eef3fa; color: #2563a8; }
    .pill-gold { background: #faf4e6; color: var(--gold); }
    
    /* Timeline */
    .timeline {
        position: relative;
        padding-left: 1.3rem;
    }
    
    .timeline::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 1px;
        background: var(--border);
    }
    
    .timeline-item {
        position: relative;
        padding-bottom: 1rem;
    }
    
    .timeline-item::before {
        content: '';
        position: absolute;
        left: -1.45rem;
        top: 0.38rem;
        width: 8px;
        height: 8px;
        background: var(--accent);
        border-radius: 50%;
        border: 2px solid var(--surface);
    }
    
    .timeline-year {
        font-size: 0.68rem;
        color: var(--accent);
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .timeline-text {
        font-size: 0.77rem;
        color: var(--text2);
        line-height: 1.5;
    }
    
    /* Risk meter */
    .risk-meter {
        display: flex;
        flex-direction: column;
        gap: 0.6rem;
    }
    
    .risk-row {
        display: flex;
        align-items: center;
        gap: 0.8rem;
    }
    
    .risk-label {
        font-size: 0.75rem;
        color: var(--text2);
        width: 180px;
        flex-shrink: 0;
    }
    
    .risk-bar {
        flex: 1;
        height: 6px;
        background: #edecea;
        border-radius: 2px;
        overflow: hidden;
    }
    
    .risk-fill {
        height: 100%;
        border-radius: 2px;
    }
    
    .risk-val {
        font-size: 0.7rem;
        font-weight: 600;
        width: 70px;
        text-align: right;
    }
    
    /* Footer */
    footer {
        visibility: visible !important;
        text-align: center;
        padding: 2rem;
        color: var(--muted);
        font-size: 0.7rem;
        border-top: 1px solid var(--border);
        margin-top: 3rem;
        background: var(--surface);
        line-height: 1.8;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Selectbox pays */
    .stSelectbox label {
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        color: var(--accent) !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
</style>
""", unsafe_allow_html=True)

# ── Init ──────────────────────────────────────────────────────────
service = DataService()

# ── Header HTML Style ─────────────────────────────────────────────
def format_pib(val):
    if val >= 1e12:
        return f"{val/1e12:.1f} Md$"
    elif val >= 1e9:
        return f"{val/1e9:.1f} Md$"
    return f"{val/1e6:.0f} M$"

# Chargement pays
with st.spinner("⏳"):
    countries = service.get_countries_list()

if not countries:
    st.error("❌ Impossible de charger les pays")
    st.stop()

# Sélecteur pays (sidebar cachée, donc dans la page)
country_names = [c["name"] for c in countries]
default_idx = country_names.index("Timor-Leste") if "Timor-Leste" in country_names else 0

selected_name = st.selectbox(
    "🔍 Sélectionner un pays",
    options=country_names,
    index=default_idx,
    label_visibility="collapsed"
)

selected = next(c for c in countries if c["name"] == selected_name)

# Chargement données
with st.spinner(f"📡 Chargement de {selected_name}..."):
    data = service.get_country_data(selected["code"])

if not data:
    st.warning(f"⚠️ Aucune donnée pour **{selected_name}**")
    st.stop()

# Calcul des badges dynamiques
pib_val = format_pib(data.get("PIB", pd.DataFrame()).iloc[-1]["valeur"]) if "PIB" in data and not data["PIB"].empty else "N/A"
inflation = f"{data['INFLATION'].iloc[-1]['valeur']:.1f}%" if "INFLATION" in data and not data["INFLATION"].empty else "N/A"
chomage = f"{data['CHOMAGE'].iloc[-1]['valeur']:.1f}%" if "CHOMAGE" in data and not data["CHOMAGE"].empty else "N/A"

# Header
st.markdown(f"""
<div class="main-header">
    <h1>{selected_name} — <em>Fondamentaux Économiques</em></h1>
    <p>Tableau de bord analytique · Source : Banque Mondiale · Données 2010–2023</p>
    <div class="header-badges">
        <span class="badge">PIB {pib_val}</span>
        <span class="badge warn">Inflation {inflation}</span>
        <span class="badge danger">Chômage {chomage}</span>
        <span class="badge ok">🌐 {selected['region']}</span>
        <span class="badge">🏛️ {selected['capital'] or 'N/A'}</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Tabs Navigation ───────────────────────────────────────────────
tabs = st.tabs([
    "① Vue Générale",
    "② Croissance & Secteurs",
    "③ Indicateurs Sociaux",
    "④ Commerce Extérieur"
])

# ═══════════════════════════════════════════════════════════════════
# TAB 1 — VUE GÉNÉRALE
# ═══════════════════════════════════════════════════════════════════
with tabs[0]:
    st.markdown("""
    <div class="section-header">
        <div class="section-icon">🏛</div>
        <div>
            <h2>Vue Générale — Indicateurs Clés</h2>
            <p>Panorama macroéconomique et données fondamentales</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="overview-ribbon">
        <strong>{selected_name}</strong> présente un profil économique caractérisé par ses indicateurs clés. 
        Les données ci-dessous proviennent des statistiques officielles de la Banque Mondiale et sont mises à jour annuellement.
    </div>
    """, unsafe_allow_html=True)
    
    # KPIs
    kpi_indicators = ["PIB", "PIB_HABITANT", "CROISSANCE", "INFLATION", "CHOMAGE", "POPULATION"]
    kpi_labels = {
        "PIB": "PIB Total",
        "PIB_HABITANT": "PIB / Habitant",
        "CROISSANCE": "Croissance",
        "INFLATION": "Inflation",
        "CHOMAGE": "Chômage",
        "POPULATION": "Population"
    }
    
    def format_kpi_value(val, key):
        if key == "PIB":
            return format_pib(val)
        elif key == "PIB_HABITANT":
            return f"{val:,.0f} $"
        elif key == "POPULATION":
            return f"{val/1e6:.2f} M" if val >= 1e6 else f"{val/1e3:.0f} K"
        else:
            return f"{val:.1f}%"
    
    def get_trend_class(df):
        if len(df) < 2:
            return "trend-neutral", "→"
        last = df.iloc[-1]["valeur"]
        prev = df.iloc[-2]["valeur"]
        if last > prev:
            return "trend-up", "↑"
        elif last < prev:
            return "trend-down", "↓"
        return "trend-neutral", "→"
    
    cols = st.columns(6)
    
    for col, key in zip(cols, kpi_indicators):
        with col:
            if key in data and not data[key].empty:
                df_ind = data[key]
                last_row = df_ind.iloc[-1]
                value_str = format_kpi_value(last_row["valeur"], key)
                year = int(last_row["année"])
                trend_class, arrow = get_trend_class(df_ind)
                
                # Delta calculation
                if len(df_ind) >= 2:
                    last = df_ind.iloc[-1]["valeur"]
                    prev = df_ind.iloc[-2]["valeur"]
                    delta_pct = ((last - prev) / prev) * 100 if prev != 0 else 0
                    delta_str = f"{arrow} {abs(delta_pct):.1f}% vs {int(df_ind.iloc[-2]['année'])}"
                else:
                    delta_str = "—"
                
                st.markdown(f"""
                <div class="card">
                    <div class="card-title">{kpi_labels[key]} ({year})</div>
                    <div class="kpi">{value_str}</div>
                    <div class="kpi-trend {trend_class}">{delta_str}</div>
                    <div class="source-tag">Banque Mondiale</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="card">
                    <div class="card-title">{kpi_labels[key]}</div>
                    <div class="kpi">N/A</div>
                    <div class="kpi-sub">Données non disponibles</div>
                </div>
                """, unsafe_allow_html=True)
    
    # Graphiques
    st.markdown('<div class="sub-label">Évolution historique</div>', unsafe_allow_html=True)
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        if "PIB" in data and not data["PIB"].empty:
            df_pib = data["PIB"].copy()
            df_pib["valeur_md"] = df_pib["valeur"] / 1e9
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=df_pib["année"],
                y=df_pib["valeur_md"],
                marker_color="#2b4a6b",
                name="PIB (Md$)"
            ))
            fig.update_layout(
                title=dict(text=f"💰 PIB — {selected_name}", font=dict(size=14, color="#1a3450")),
                xaxis_title="Année",
                yaxis_title="Milliards $",
                template="plotly_white",
                height=320,
                font=dict(family="Georgia, serif", size=11),
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col_right:
        fig2 = go.Figure()
        
        if "CROISSANCE" in data and not data["CROISSANCE"].empty:
            fig2.add_trace(go.Scatter(
                x=data["CROISSANCE"]["année"],
                y=data["CROISSANCE"]["valeur"],
                name="Croissance",
                line=dict(color="#2b4a6b", width=2),
                mode="lines+markers"
            ))
        
        if "INFLATION" in data and not data["INFLATION"].empty:
            fig2.add_trace(go.Scatter(
                x=data["INFLATION"]["année"],
                y=data["INFLATION"]["valeur"],
                name="Inflation",
                line=dict(color="#c0620a", width=2),
                mode="lines+markers"
            ))
        
        fig2.update_layout(
            title=dict(text=f"📈 Croissance & Inflation — {selected_name}", font=dict(size=14, color="#1a3450")),
            xaxis_title="Année",
            yaxis_title="%",
            template="plotly_white",
            height=320,
            font=dict(family="Georgia, serif", size=11),
            legend=dict(orientation="h", y=-0.2),
            hovermode="x unified"
        )
        st.plotly_chart(fig2, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════
# TAB 2 — CROISSANCE & SECTEURS
# ═══════════════════════════════════════════════════════════════════
with tabs[1]:
    st.markdown("""
    <div class="section-header">
        <div class="section-icon">📈</div>
        <div>
            <h2>Modèle de Croissance</h2>
            <p>Dynamique du PIB, structure sectorielle et moteurs de la croissance</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="overview-ribbon">
        L'analyse de la croissance de <strong>{selected_name}</strong> révèle les tendances structurelles de long terme et les cycles économiques. 
        La croissance est influencée par des facteurs internes (investissement, consommation) et externes (commerce, IDE).
    </div>
    """, unsafe_allow_html=True)
    
    # Graph croissance
    if "CROISSANCE" in data and not data["CROISSANCE"].empty:
        df_cr = data["CROISSANCE"].copy()
        
        fig = go.Figure()
        colors = ['#2b4a6b' if v >= 0 else '#c0392b' for v in df_cr["valeur"]]
        
        fig.add_trace(go.Bar(
            x=df_cr["année"],
            y=df_cr["valeur"],
            marker_color=colors,
            name="Croissance PIB réel"
        ))
        
        fig.update_layout(
            title=dict(text=f"Taux de croissance du PIB réel (%) — {selected_name}", font=dict(size=14, color="#1a3450")),
            xaxis_title="Année",
            yaxis_title="%",
            template="plotly_white",
            height=380,
            font=dict(family="Georgia, serif", size=11),
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Alertes contextuelles
    st.markdown("""
    <div class="alert alert-info">
        <strong>Analyse de la croissance</strong>
        Les variations annuelles du PIB réel reflètent les chocs externes (crises financières, pandémies) 
        ainsi que les dynamiques internes (politiques budgétaires, investissements).
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# TAB 3 — INDICATEURS SOCIAUX
# ═══════════════════════════════════════════════════════════════════
with tabs[2]:
    st.markdown("""
    <div class="section-header">
        <div class="section-icon">👥</div>
        <div>
            <h2>Indicateurs Sociaux</h2>
            <p>Population, emploi, pauvreté et développement humain</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if "POPULATION" in data and not data["POPULATION"].empty:
            df_pop = data["POPULATION"].copy()
            df_pop["valeur_m"] = df_pop["valeur"] / 1e6
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_pop["année"],
                y=df_pop["valeur_m"],
                fill='tozeroy',
                line=dict(color="#2b4a6b", width=2),
                name="Population"
            ))
            fig.update_layout(
                title=dict(text=f"🌍 Population — {selected_name}", font=dict(size=14, color="#1a3450")),
                xaxis_title="Année",
                yaxis_title="Millions",
                template="plotly_white",
                height=320,
                font=dict(family="Georgia, serif", size=11),
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if "CHOMAGE" in data and not data["CHOMAGE"].empty:
            df_ch = data["CHOMAGE"].copy()
            
            fig = go.Figure()
            colors = ['#2b4a6b' if v < 10 else '#c0620a' if v < 20 else '#c0392b' for v in df_ch["valeur"]]
            
            fig.add_trace(go.Bar(
                x=df_ch["année"],
                y=df_ch["valeur"],
                marker_color=colors
            ))
            fig.update_layout(
                title=dict(text=f"👥 Taux de Chômage — {selected_name}", font=dict(size=14, color="#1a3450")),
                xaxis_title="Année",
                yaxis_title="%",
                template="plotly_white",
                height=320,
                font=dict(family="Georgia, serif", size=11),
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════
# TAB 4 — COMMERCE EXTÉRIEUR
# ═══════════════════════════════════════════════════════════════════
with tabs[3]:
    st.markdown("""
    <div class="section-header">
        <div class="section-icon">⚖️</div>
        <div>
            <h2>Commerce Extérieur</h2>
            <p>Exportations, importations et partenaires commerciaux</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="alert alert-warn">
        <strong>Données commerciales limitées</strong>
        Les statistiques de commerce détaillé ne sont pas disponibles via l'API Banque Mondiale. 
        Pour une analyse approfondie, consultez les bases COMTRADE (ONU) ou les douanes nationales.
    </div>
    """, unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────
st.markdown("""
---
<footer>
    <p><strong>Fondamentaux Économiques</strong> · Tableau de bord analytique</p>
    <p>Sources : FMI (WEO, Article IV) · Banque Mondiale (WDI, WGI) · Données 2010–2023 · Avril 2026</p>
    <p>Document à des fins analytiques et pédagogiques</p>
</footer>
""", unsafe_allow_html=True)
