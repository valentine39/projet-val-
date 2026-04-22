import streamlit as st
import requests
from bs4 import BeautifulSoup
import re

# ─────────────────────────────────────────────
# Configuration de la page
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Country Data Explorer",
    page_icon="🌍",
    layout="centered"
)

# ─────────────────────────────────────────────
# Style visuel
# ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Sans:wght@300;400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    h1, h2, h3 {
        font-family: 'Syne', sans-serif;
    }

    .main { background-color: #0f0f0f; }

    .stApp {
        background-color: #0f0f0f;
        color: #f0ede6;
    }

    .metric-card {
        background: #1a1a1a;
        border: 1px solid #2a2a2a;
        border-radius: 12px;
        padding: 20px 24px;
        margin-bottom: 12px;
    }

    .metric-label {
        font-size: 11px;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #888;
        margin-bottom: 6px;
    }

    .metric-value {
        font-family: 'Syne', sans-serif;
        font-size: 28px;
        font-weight: 700;
        color: #f0ede6;
    }

    .metric-sub {
        font-size: 12px;
        color: #555;
        margin-top: 4px;
    }

    .source-header {
        font-family: 'Syne', sans-serif;
        font-size: 13px;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        color: #555;
        border-bottom: 1px solid #222;
        padding-bottom: 10px;
        margin: 28px 0 16px 0;
    }

    .status-badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 500;
        letter-spacing: 0.05em;
    }

    .badge-free { background: #1a3a2a; color: #4caf7d; }
    .badge-partly { background: #3a2a0a; color: #f0a500; }
    .badge-notfree { background: #3a0a0a; color: #e05555; }

    .error-box {
        background: #1a0a0a;
        border: 1px solid #3a1a1a;
        border-radius: 10px;
        padding: 16px 20px;
        color: #e05555;
        font-size: 14px;
    }

    div[data-testid="stButton"] button {
        background: #f0ede6;
        color: #0f0f0f;
        font-family: 'Syne', sans-serif;
        font-weight: 700;
        font-size: 14px;
        letter-spacing: 0.08em;
        border: none;
        border-radius: 8px;
        padding: 12px 32px;
        width: 100%;
        cursor: pointer;
        transition: opacity 0.2s;
    }

    div[data-testid="stButton"] button:hover {
        opacity: 0.85;
    }

    div[data-testid="stSelectbox"] label {
        color: #888;
        font-size: 11px;
        letter-spacing: 0.1em;
        text-transform: uppercase;
    }

    .title-block {
        margin-bottom: 40px;
    }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Données : liste des pays
# ─────────────────────────────────────────────
COUNTRY_MAPPING = {
    "timor_leste": {
        "name": "Timor-Leste",
        "freedom_house_slug": "timor-leste",
        "world_bank_code": "TLS"
    },
    "france": {
        "name": "France",
        "freedom_house_slug": "france",
        "world_bank_code": "FRA"
    }
}


# ─────────────────────────────────────────────
# Fonctions de récupération (votre code original)
# ─────────────────────────────────────────────
def fetch_freedom_house(country_slug, year=2026):
    url = f"https://freedomhouse.org/country/{country_slug}/freedom-world/{year}"
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text(" ", strip=True)
        text = re.sub(r"\s+", " ", text)

        result = {
            "country": None,
            "status": None,
            "score": None,
            "pr_score": None,
            "cl_score": None,
            "year": year,
            "url": url,
            "error": None
        }

        if soup.title and soup.title.string:
            result["country"] = soup.title.string.split(":")[0].strip()
        else:
            result["country"] = country_slug.replace("-", " ").title()

        status_match = re.search(r"\b(Free|Partly Free|Not Free)\b", text)
        if status_match:
            result["status"] = status_match.group(1)

        global_match = re.search(r"(?:Total Score and Status|score)\s+(\d{1,3})\s*/?\s*100", text, re.IGNORECASE)
        if global_match:
            result["score"] = int(global_match.group(1))
        else:
            fallback = re.search(r"\b(\d{1,3})\s*/?\s*100\b", text)
            if fallback:
                result["score"] = int(fallback.group(1))

        pr_match = re.search(r"Political Rights\s+(\d{1,2})\s*/?\s*40", text, re.IGNORECASE)
        if pr_match:
            result["pr_score"] = int(pr_match.group(1))

        cl_match = re.search(r"Civil Liberties\s+(\d{1,2})\s*/?\s*60", text, re.IGNORECASE)
        if cl_match:
            result["cl_score"] = int(cl_match.group(1))

        return result

    except Exception as e:
        return {"error": str(e), "url": url}


def fetch_world_bank_indicator(country_code, indicator_code):
    url = f"https://api.worldbank.org/v2/country/{country_code}/indicator/{indicator_code}?format=json&per_page=200"
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, list) or len(data) < 2 or data[1] is None:
            return None
        for row in data[1]:
            if row["value"] is not None:
                return {"value": row["value"], "year": row["date"]}
        return None
    except Exception:
        return None


def fetch_world_bank_data(country_code):
    population = fetch_world_bank_indicator(country_code, "SP.POP.TOTL")
    gini = fetch_world_bank_indicator(country_code, "SI.POV.GINI")
    gdp = fetch_world_bank_indicator(country_code, "NY.GDP.PCAP.CD")
    return {
        "population": population,
        "gini": gini,
        "gdp_per_capita": gdp
    }


# ─────────────────────────────────────────────
# Fonctions d'affichage
# ─────────────────────────────────────────────
def render_metric(label, value, sub=None):
    sub_html = f'<div class="metric-sub">{sub}</div>' if sub else ""
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {sub_html}
    </div>
    """, unsafe_allow_html=True)


def render_status_badge(status):
    if status == "Free":
        return f'<span class="status-badge badge-free">● Free</span>'
    elif status == "Partly Free":
        return f'<span class="status-badge badge-partly">● Partly Free</span>'
    elif status == "Not Free":
        return f'<span class="status-badge badge-notfree">● Not Free</span>'
    return f'<span class="status-badge" style="background:#222;color:#888;">Unknown</span>'


def format_population(value):
    if value is None:
        return "N/A"
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if value >= 1_000:
        return f"{value / 1_000:.0f}K"
    return str(int(value))


# ─────────────────────────────────────────────
# Interface principale
# ─────────────────────────────────────────────
st.markdown('<div class="title-block">', unsafe_allow_html=True)
st.markdown("# 🌍 Country Data Explorer")
st.markdown('<p style="color:#555; font-size:15px; margin-top:-8px;">Données politiques et économiques par pays</p>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Sélecteur de pays
country_options = {info["name"]: key for key, info in COUNTRY_MAPPING.items()}
selected_name = st.selectbox("Sélectionner un pays", options=list(country_options.keys()))
selected_key = country_options[selected_name]

st.write("")  # espace

if st.button("Récupérer les données →"):

    country_info = COUNTRY_MAPPING[selected_key]

    # ── Freedom House ──
    st.markdown('<div class="source-header">Freedom House — Freedom in the World</div>', unsafe_allow_html=True)

    with st.spinner("Chargement Freedom House..."):
        fh = fetch_freedom_house(country_info["freedom_house_slug"])

    if fh.get("error"):
        st.markdown(f'<div class="error-box">⚠ Source indisponible — {fh["error"]}</div>', unsafe_allow_html=True)
    else:
        col1, col2 = st.columns(2)
        with col1:
            score_display = f"{fh['score']}/100" if fh.get("score") is not None else "N/A"
            render_metric("Score global", score_display, f"Année {fh['year']}")
        with col2:
            badge = render_status_badge(fh.get("status"))
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Statut</div>
                <div style="margin-top:8px">{badge}</div>
            </div>
            """, unsafe_allow_html=True)

        col3, col4 = st.columns(2)
        with col3:
            pr = f"{fh['pr_score']}/40" if fh.get("pr_score") is not None else "N/A"
            render_metric("Droits politiques", pr)
        with col4:
            cl = f"{fh['cl_score']}/60" if fh.get("cl_score") is not None else "N/A"
            render_metric("Libertés civiles", cl)

        st.markdown(f'<p style="font-size:11px;color:#444;margin-top:4px;">Source : <a href="{fh["url"]}" style="color:#555">{fh["url"]}</a></p>', unsafe_allow_html=True)

    # ── Banque Mondiale ──
    st.markdown('<div class="source-header">Banque Mondiale</div>', unsafe_allow_html=True)

    with st.spinner("Chargement Banque Mondiale..."):
        wb = fetch_world_bank_data(country_info["world_bank_code"])

    wb_has_data = any(v is not None for v in wb.values())

    if not wb_has_data:
        st.markdown('<div class="error-box">⚠ Source indisponible — Aucune donnée retournée</div>', unsafe_allow_html=True)
    else:
        col5, col6, col7 = st.columns(3)
        with col5:
            pop = wb.get("population")
            render_metric(
                "Population",
                format_population(pop["value"]) if pop else "N/A",
                f"Année {pop['year']}" if pop else ""
            )
        with col6:
            gdp = wb.get("gdp_per_capita")
            gdp_val = f"${gdp['value']:,.0f}" if gdp and gdp["value"] else "N/A"
            render_metric(
                "PIB / habitant",
                gdp_val,
                f"Année {gdp['year']}" if gdp else ""
            )
        with col7:
            gini = wb.get("gini")
            gini_val = f"{gini['value']:.1f}" if gini and gini["value"] else "N/A"
            render_metric(
                "Indice de Gini",
                gini_val,
                f"Année {gini['year']}" if gini else ""
            )

        wb_url = f"https://data.worldbank.org/country/{country_info['world_bank_code']}"
        st.markdown(f'<p style="font-size:11px;color:#444;margin-top:4px;">Source : <a href="{wb_url}" style="color:#555">{wb_url}</a></p>', unsafe_allow_html=True)
