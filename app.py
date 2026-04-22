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
# Liste des pays
# ─────────────────────────────────────────────
COUNTRY_MAPPING = {
    "afghanistan": {"name": "Afghanistan", "freedom_house_slug": "afghanistan", "world_bank_code": "AFG"},
    "afrique_du_sud": {"name": "Afrique du Sud", "freedom_house_slug": "south-africa", "world_bank_code": "ZAF"},
    "albanie": {"name": "Albanie", "freedom_house_slug": "albania", "world_bank_code": "ALB"},
    "algerie": {"name": "Algérie", "freedom_house_slug": "algeria", "world_bank_code": "DZA"},
    "angola": {"name": "Angola", "freedom_house_slug": "angola", "world_bank_code": "AGO"},
    "antigua_et_barbuda": {"name": "Antigua et Barbuda", "freedom_house_slug": "antigua-and-barbuda", "world_bank_code": "ATG"},
    "argentine": {"name": "Argentine", "freedom_house_slug": "argentina", "world_bank_code": "ARG"},
    "armenie": {"name": "Arménie", "freedom_house_slug": "armenia", "world_bank_code": "ARM"},
    "azerbaijan": {"name": "Azerbaïdjan", "freedom_house_slug": "azerbaijan", "world_bank_code": "AZE"},
    "bangladesh": {"name": "Bangladesh", "freedom_house_slug": "bangladesh", "world_bank_code": "BGD"},
    "belize": {"name": "Belize", "freedom_house_slug": "belize", "world_bank_code": "BLZ"},
    "benin": {"name": "Bénin", "freedom_house_slug": "benin", "world_bank_code": "BEN"},
    "bhoutan": {"name": "Bhoutan", "freedom_house_slug": "bhutan", "world_bank_code": "BTN"},
    "bielorussie": {"name": "Biélorussie", "freedom_house_slug": "belarus", "world_bank_code": "BLR"},
    "birmanie": {"name": "Birmanie (Myanmar)", "freedom_house_slug": "myanmar", "world_bank_code": "MMR"},
    "bolivie": {"name": "Bolivie", "freedom_house_slug": "bolivia", "world_bank_code": "BOL"},
    "bosnie_herzegovine": {"name": "Bosnie-Herzégovine", "freedom_house_slug": "bosnia-and-herzegovina", "world_bank_code": "BIH"},
    "botswana": {"name": "Botswana", "freedom_house_slug": "botswana", "world_bank_code": "BWA"},
    "bresil": {"name": "Brésil", "freedom_house_slug": "brazil", "world_bank_code": "BRA"},
    "burkina_faso": {"name": "Burkina Faso", "freedom_house_slug": "burkina-faso", "world_bank_code": "BFA"},
    "burundi": {"name": "Burundi", "freedom_house_slug": "burundi", "world_bank_code": "BDI"},
    "cambodge": {"name": "Cambodge", "freedom_house_slug": "cambodia", "world_bank_code": "KHM"},
    "cameroun": {"name": "Cameroun", "freedom_house_slug": "cameroon", "world_bank_code": "CMR"},
    "cap_vert": {"name": "Cap-Vert", "freedom_house_slug": "cape-verde", "world_bank_code": "CPV"},
    "chili": {"name": "Chili", "freedom_house_slug": "chile", "world_bank_code": "CHL"},
    "chine": {"name": "Chine", "freedom_house_slug": "china", "world_bank_code": "CHN"},
    "colombie": {"name": "Colombie", "freedom_house_slug": "colombia", "world_bank_code": "COL"},
    "comores": {"name": "Comores", "freedom_house_slug": "comoros", "world_bank_code": "COM"},
    "congo": {"name": "Congo (Brazzaville)", "freedom_house_slug": "republic-of-congo", "world_bank_code": "COG"},
    "costa_rica": {"name": "Costa Rica", "freedom_house_slug": "costa-rica", "world_bank_code": "CRI"},
    "cote_ivoire": {"name": "Côte d'Ivoire", "freedom_house_slug": "cote-divoire", "world_bank_code": "CIV"},
    "cuba": {"name": "Cuba", "freedom_house_slug": "cuba", "world_bank_code": "CUB"},
    "djibouti": {"name": "Djibouti", "freedom_house_slug": "djibouti", "world_bank_code": "DJI"},
    "dominique": {"name": "Dominique", "freedom_house_slug": "dominica", "world_bank_code": "DMA"},
    "egypte": {"name": "Égypte", "freedom_house_slug": "egypt", "world_bank_code": "EGY"},
    "equateur": {"name": "Équateur", "freedom_house_slug": "ecuador", "world_bank_code": "ECU"},
    "erythree": {"name": "Érythrée", "freedom_house_slug": "eritrea", "world_bank_code": "ERI"},
    "eswatini": {"name": "Eswatini", "freedom_house_slug": "eswatini", "world_bank_code": "SWZ"},
    "ethiopie": {"name": "Éthiopie", "freedom_house_slug": "ethiopia", "world_bank_code": "ETH"},
    "fidji": {"name": "Fidji", "freedom_house_slug": "fiji", "world_bank_code": "FJI"},
    "gabon": {"name": "Gabon", "freedom_house_slug": "gabon", "world_bank_code": "GAB"},
    "gambie": {"name": "Gambie", "freedom_house_slug": "gambia", "world_bank_code": "GMB"},
    "georgie": {"name": "Géorgie", "freedom_house_slug": "georgia", "world_bank_code": "GEO"},
    "ghana": {"name": "Ghana", "freedom_house_slug": "ghana", "world_bank_code": "GHA"},
    "grenade": {"name": "Grenade", "freedom_house_slug": "grenada", "world_bank_code": "GRD"},
    "guatemala": {"name": "Guatemala", "freedom_house_slug": "guatemala", "world_bank_code": "GTM"},
    "guinee": {"name": "Guinée", "freedom_house_slug": "guinea", "world_bank_code": "GIN"},
    "guinee_bissau": {"name": "Guinée-Bissau", "freedom_house_slug": "guinea-bissau", "world_bank_code": "GNB"},
    "guinee_equatoriale": {"name": "Guinée équatoriale", "freedom_house_slug": "equatorial-guinea", "world_bank_code": "GNQ"},
    "guyana": {"name": "Guyana", "freedom_house_slug": "guyana", "world_bank_code": "GUY"},
    "haiti": {"name": "Haïti", "freedom_house_slug": "haiti", "world_bank_code": "HTI"},
    "honduras": {"name": "Honduras", "freedom_house_slug": "honduras", "world_bank_code": "HND"},
    "iles_salomon": {"name": "Îles Salomon", "freedom_house_slug": "solomon-islands", "world_bank_code": "SLB"},
    "inde": {"name": "Inde", "freedom_house_slug": "india", "world_bank_code": "IND"},
    "indonesie": {"name": "Indonésie", "freedom_house_slug": "indonesia", "world_bank_code": "IDN"},
    "irak": {"name": "Irak", "freedom_house_slug": "iraq", "world_bank_code": "IRQ"},
    "jamaique": {"name": "Jamaïque", "freedom_house_slug": "jamaica", "world_bank_code": "JAM"},
    "jordanie": {"name": "Jordanie", "freedom_house_slug": "jordan", "world_bank_code": "JOR"},
    "kazakhstan": {"name": "Kazakhstan", "freedom_house_slug": "kazakhstan", "world_bank_code": "KAZ"},
    "kenya": {"name": "Kenya", "freedom_house_slug": "kenya", "world_bank_code": "KEN"},
    "kirghizistan": {"name": "Kirghizistan", "freedom_house_slug": "kyrgyzstan", "world_bank_code": "KGZ"},
    "kosovo": {"name": "Kosovo", "freedom_house_slug": "kosovo", "world_bank_code": "XKX"},
    "laos": {"name": "Laos", "freedom_house_slug": "laos", "world_bank_code": "LAO"},
    "lesotho": {"name": "Lesotho", "freedom_house_slug": "lesotho", "world_bank_code": "LSO"},
    "liban": {"name": "Liban", "freedom_house_slug": "lebanon", "world_bank_code": "LBN"},
    "liberia": {"name": "Libéria", "freedom_house_slug": "liberia", "world_bank_code": "LBR"},
    "libye": {"name": "Libye", "freedom_house_slug": "libya", "world_bank_code": "LBY"},
    "macedoine_du_nord": {"name": "Macédoine du Nord", "freedom_house_slug": "north-macedonia", "world_bank_code": "MKD"},
    "madagascar": {"name": "Madagascar", "freedom_house_slug": "madagascar", "world_bank_code": "MDG"},
    "malawi": {"name": "Malawi", "freedom_house_slug": "malawi", "world_bank_code": "MWI"},
    "maldives": {"name": "Maldives", "freedom_house_slug": "maldives", "world_bank_code": "MDV"},
    "mali": {"name": "Mali", "freedom_house_slug": "mali", "world_bank_code": "MLI"},
    "maroc": {"name": "Maroc", "freedom_house_slug": "morocco", "world_bank_code": "MAR"},
    "maurice": {"name": "Maurice", "freedom_house_slug": "mauritius", "world_bank_code": "MUS"},
    "mauritanie": {"name": "Mauritanie", "freedom_house_slug": "mauritania", "world_bank_code": "MRT"},
    "mexique": {"name": "Mexique", "freedom_house_slug": "mexico", "world_bank_code": "MEX"},
    "moldavie": {"name": "Moldavie", "freedom_house_slug": "moldova", "world_bank_code": "MDA"},
    "mongolie": {"name": "Mongolie", "freedom_house_slug": "mongolia", "world_bank_code": "MNG"},
    "montenegro": {"name": "Monténégro", "freedom_house_slug": "montenegro", "world_bank_code": "MNE"},
    "mozambique": {"name": "Mozambique", "freedom_house_slug": "mozambique", "world_bank_code": "MOZ"},
    "namibie": {"name": "Namibie", "freedom_house_slug": "namibia", "world_bank_code": "NAM"},
    "nepal": {"name": "Népal", "freedom_house_slug": "nepal", "world_bank_code": "NPL"},
    "nicaragua": {"name": "Nicaragua", "freedom_house_slug": "nicaragua", "world_bank_code": "NIC"},
    "niger": {"name": "Niger", "freedom_house_slug": "niger", "world_bank_code": "NER"},
    "nigeria": {"name": "Nigéria", "freedom_house_slug": "nigeria", "world_bank_code": "NGA"},
    "ouganda": {"name": "Ouganda", "freedom_house_slug": "uganda", "world_bank_code": "UGA"},
    "ouzbekistan": {"name": "Ouzbékistan", "freedom_house_slug": "uzbekistan", "world_bank_code": "UZB"},
    "pakistan": {"name": "Pakistan", "freedom_house_slug": "pakistan", "world_bank_code": "PAK"},
    "panama": {"name": "Panama", "freedom_house_slug": "panama", "world_bank_code": "PAN"},
    "paraguay": {"name": "Paraguay", "freedom_house_slug": "paraguay", "world_bank_code": "PRY"},
    "perou": {"name": "Pérou", "freedom_house_slug": "peru", "world_bank_code": "PER"},
    "philippines": {"name": "Philippines", "freedom_house_slug": "philippines", "world_bank_code": "PHL"},
    "rdc": {"name": "RDC (Congo-Kinshasa)", "freedom_house_slug": "democratic-republic-of-congo", "world_bank_code": "COD"},
    "republique_dominicaine": {"name": "République dominicaine", "freedom_house_slug": "dominican-republic", "world_bank_code": "DOM"},
    "rwanda": {"name": "Rwanda", "freedom_house_slug": "rwanda", "world_bank_code": "RWA"},
    "sainte_lucie": {"name": "Sainte-Lucie", "freedom_house_slug": "saint-lucia", "world_bank_code": "LCA"},
    "saint_vincent": {"name": "Saint-Vincent-et-les-Grenadines", "freedom_house_slug": "saint-vincent-and-the-grenadines", "world_bank_code": "VCT"},
    "salvador": {"name": "Salvador", "freedom_house_slug": "el-salvador", "world_bank_code": "SLV"},
    "samoa": {"name": "Samoa", "freedom_house_slug": "samoa", "world_bank_code": "WSM"},
    "sao_tome": {"name": "Sao Tomé-et-Principe", "freedom_house_slug": "sao-tome-and-principe", "world_bank_code": "STP"},
    "senegal": {"name": "Sénégal", "freedom_house_slug": "senegal", "world_bank_code": "SEN"},
    "serbie": {"name": "Serbie", "freedom_house_slug": "serbia", "world_bank_code": "SRB"},
    "seychelles": {"name": "Seychelles", "freedom_house_slug": "seychelles", "world_bank_code": "SYC"},
    "sierra_leone": {"name": "Sierra Leone", "freedom_house_slug": "sierra-leone", "world_bank_code": "SLE"},
    "somalie": {"name": "Somalie", "freedom_house_slug": "somalia", "world_bank_code": "SOM"},
    "soudan": {"name": "Soudan", "freedom_house_slug": "sudan", "world_bank_code": "SDN"},
    "sri_lanka": {"name": "Sri Lanka", "freedom_house_slug": "sri-lanka", "world_bank_code": "LKA"},
    "suriname": {"name": "Suriname", "freedom_house_slug": "suriname", "world_bank_code": "SUR"},
    "syrie": {"name": "Syrie", "freedom_house_slug": "syria", "world_bank_code": "SYR"},
    "tadjikistan": {"name": "Tadjikistan", "freedom_house_slug": "tajikistan", "world_bank_code": "TJK"},
    "tanzanie": {"name": "Tanzanie", "freedom_house_slug": "tanzania", "world_bank_code": "TZA"},
    "tchad": {"name": "Tchad", "freedom_house_slug": "chad", "world_bank_code": "TCD"},
    "thailande": {"name": "Thaïlande", "freedom_house_slug": "thailand", "world_bank_code": "THA"},
    "timor_leste": {"name": "Timor-Leste", "freedom_house_slug": "timor-leste", "world_bank_code": "TLS"},
    "togo": {"name": "Togo", "freedom_house_slug": "togo", "world_bank_code": "TGO"},
    "tunisie": {"name": "Tunisie", "freedom_house_slug": "tunisia", "world_bank_code": "TUN"},
    "turquie": {"name": "Turquie", "freedom_house_slug": "turkey", "world_bank_code": "TUR"},
    "ukraine": {"name": "Ukraine", "freedom_house_slug": "ukraine", "world_bank_code": "UKR"},
    "uruguay": {"name": "Uruguay", "freedom_house_slug": "uruguay", "world_bank_code": "URY"},
    "vanuatu": {"name": "Vanuatu", "freedom_house_slug": "vanuatu", "world_bank_code": "VUT"},
    "vietnam": {"name": "Vietnam", "freedom_house_slug": "vietnam", "world_bank_code": "VNM"},
    "yemen": {"name": "Yémen", "freedom_house_slug": "yemen", "world_bank_code": "YEM"},
    "zambie": {"name": "Zambie", "freedom_house_slug": "zambia", "world_bank_code": "ZMB"},
    "zimbabwe": {"name": "Zimbabwe", "freedom_house_slug": "zimbabwe", "world_bank_code": "ZWE"},
}


# ─────────────────────────────────────────────
# Fonctions de récupération
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
            "country": None, "status": None, "score": None,
            "pr_score": None, "cl_score": None,
            "year": year, "url": url, "error": None
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
    return {"population": population, "gini": gini, "gdp_per_capita": gdp}


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
        return '<span class="status-badge badge-free">● Free</span>'
    elif status == "Partly Free":
        return '<span class="status-badge badge-partly">● Partly Free</span>'
    elif status == "Not Free":
        return '<span class="status-badge badge-notfree">● Not Free</span>'
    return '<span class="status-badge" style="background:#222;color:#888;">Unknown</span>'


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

# Sélecteur de pays (trié alphabétiquement)
country_options = dict(sorted(
    {info["name"]: key for key, info in COUNTRY_MAPPING.items()}.items()
))
selected_name = st.selectbox("Sélectionner un pays", options=list(country_options.keys()))
selected_key = country_options[selected_name]

st.write("")

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
            render_metric("PIB / habitant", gdp_val, f"Année {gdp['year']}" if gdp else "")
        with col7:
            gini = wb.get("gini")
            gini_val = f"{gini['value']:.1f}" if gini and gini["value"] else "N/A"
            render_metric("Indice de Gini", gini_val, f"Année {gini['year']}" if gini else "")

        wb_url = f"https://data.worldbank.org/country/{country_info['world_bank_code']}"
        st.markdown(f'<p style="font-size:11px;color:#444;margin-top:4px;">Source : <a href="{wb_url}" style="color:#555">{wb_url}</a></p>', unsafe_allow_html=True)
