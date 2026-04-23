import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

# ─────────────────────────────────────────────
# Configuration de la page
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Outil de collecte de données - DER",
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
        color: #111111;
    }

    h1, h2, h3 {
        font-family: 'Syne', sans-serif;
        color: #111111;
    }

    .stApp {
        background-color: #ffffff;
        color: #111111;
    }

    section[data-testid="stSidebar"] {
        background-color: #fafafa;
    }

    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    .metric-card {
        background: #f7f7f5;
        border: 1px solid #e6e3dc;
        border-radius: 14px;
        padding: 20px 24px;
        margin-bottom: 12px;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
    }

    .metric-label {
        font-size: 11px;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #6b6b6b;
        margin-bottom: 6px;
    }

    .metric-value {
        font-family: 'Syne', sans-serif;
        font-size: 24px;
        font-weight: 700;
        color: #111111;
        line-height: 1.2;
    }

    .metric-sub {
        font-size: 12px;
        color: #6f6f6f;
        margin-top: 6px;
    }

    .trend-up {
        color: #1f8f55;
    }

    .trend-down {
        color: #c0392b;
    }

    .trend-flat {
        color: #7a7a7a;
    }

    .section-title {
        font-family: 'Syne', sans-serif;
        font-size: 20px;
        font-weight: 800;
        color: #111111;
        margin: 40px 0 6px 0;
        letter-spacing: 0.01em;
    }

    .section-subtitle {
        font-size: 12px;
        color: #6f6f6f;
        margin-bottom: 16px;
        letter-spacing: 0.03em;
    }

    .source-header {
        font-family: 'Syne', sans-serif;
        font-size: 11px;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        color: #7a7a7a;
        border-bottom: 1px solid #e3dfd7;
        padding-bottom: 8px;
        margin: 20px 0 12px 0;
    }

    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 600;
        letter-spacing: 0.04em;
    }

    .badge-free {
        background: #e9f7ef;
        color: #1f8f55;
        border: 1px solid #cfead9;
    }

    .badge-partly {
        background: #fff4df;
        color: #b26a00;
        border: 1px solid #f0d7a5;
    }

    .badge-notfree {
        background: #fdecea;
        color: #c0392b;
        border: 1px solid #f3c5bf;
    }

    .income-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 600;
        background: #eef2ff;
        color: #4b5fc7;
        border: 1px solid #d9e0ff;
        letter-spacing: 0.04em;
    }

    .error-box {
        background: #fff4f4;
        border: 1px solid #f0c8c8;
        border-radius: 10px;
        padding: 14px 18px;
        color: #b42318;
        font-size: 13px;
        margin-bottom: 10px;
    }

    .na-box {
        background: #f8f8f8;
        border: 1px solid #e1e1e1;
        border-radius: 10px;
        padding: 10px 16px;
        color: #666666;
        font-size: 13px;
        margin-bottom: 10px;
    }

    div[data-testid="stButton"] button {
        background: #111111;
        color: #ffffff;
        font-family: 'Syne', sans-serif;
        font-weight: 700;
        font-size: 14px;
        letter-spacing: 0.06em;
        border: none;
        border-radius: 10px;
        padding: 12px 32px;
        width: 100%;
        transition: all 0.2s ease;
    }

    div[data-testid="stButton"] button:hover {
        background: #2a2a2a;
    }

    div[data-testid="stSelectbox"] label {
        color: #666666;
        font-size: 11px;
        letter-spacing: 0.1em;
        text-transform: uppercase;
    }

    .title-block {
        margin-bottom: 36px;
    }

    .source-note {
        font-size: 11px;
        color: #6f6f6f;
        margin-top: 6px;
        margin-bottom: 4px;
    }

    a {
        color: #4b5fc7;
        text-decoration: none;
    }

    a:hover {
        text-decoration: underline;
    }

    hr {
        border: none;
        border-top: 1px solid #e6e3dc;
        margin: 24px 0;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Liste des pays
# ─────────────────────────────────────────────
COUNTRY_MAPPING = {
    "afghanistan": {"name": "Afghanistan", "freedom_house_slug": "afghanistan", "world_bank_code": "AFG", "wb_url_code": "AF"},
    "afrique_du_sud": {"name": "Afrique du Sud", "freedom_house_slug": "south-africa", "world_bank_code": "ZAF", "wb_url_code": "ZA"},
    "albanie": {"name": "Albanie", "freedom_house_slug": "albania", "world_bank_code": "ALB", "wb_url_code": "AL"},
    "algerie": {"name": "Algérie", "freedom_house_slug": "algeria", "world_bank_code": "DZA", "wb_url_code": "DZ"},
    "angola": {"name": "Angola", "freedom_house_slug": "angola", "world_bank_code": "AGO", "wb_url_code": "AO"},
    "antigua_et_barbuda": {"name": "Antigua et Barbuda", "freedom_house_slug": "antigua-and-barbuda", "world_bank_code": "ATG", "wb_url_code": "AG"},
    "argentine": {"name": "Argentine", "freedom_house_slug": "argentina", "world_bank_code": "ARG", "wb_url_code": "AR"},
    "armenie": {"name": "Arménie", "freedom_house_slug": "armenia", "world_bank_code": "ARM", "wb_url_code": "AM"},
    "azerbaijan": {"name": "Azerbaïdjan", "freedom_house_slug": "azerbaijan", "world_bank_code": "AZE", "wb_url_code": "AZ"},
    "bangladesh": {"name": "Bangladesh", "freedom_house_slug": "bangladesh", "world_bank_code": "BGD", "wb_url_code": "BD"},
    "belize": {"name": "Belize", "freedom_house_slug": "belize", "world_bank_code": "BLZ", "wb_url_code": "BZ"},
    "benin": {"name": "Bénin", "freedom_house_slug": "benin", "world_bank_code": "BEN", "wb_url_code": "BJ"},
    "bhoutan": {"name": "Bhoutan", "freedom_house_slug": "bhutan", "world_bank_code": "BTN", "wb_url_code": "BT"},
    "bielorussie": {"name": "Biélorussie", "freedom_house_slug": "belarus", "world_bank_code": "BLR", "wb_url_code": "BY"},
    "birmanie": {"name": "Birmanie (Myanmar)", "freedom_house_slug": "myanmar", "world_bank_code": "MMR", "wb_url_code": "MM"},
    "bolivie": {"name": "Bolivie", "freedom_house_slug": "bolivia", "world_bank_code": "BOL", "wb_url_code": "BO"},
    "bosnie_herzegovine": {"name": "Bosnie-Herzégovine", "freedom_house_slug": "bosnia-and-herzegovina", "world_bank_code": "BIH", "wb_url_code": "BA"},
    "botswana": {"name": "Botswana", "freedom_house_slug": "botswana", "world_bank_code": "BWA", "wb_url_code": "BW"},
    "bresil": {"name": "Brésil", "freedom_house_slug": "brazil", "world_bank_code": "BRA", "wb_url_code": "BR"},
    "burkina_faso": {"name": "Burkina Faso", "freedom_house_slug": "burkina-faso", "world_bank_code": "BFA", "wb_url_code": "BF"},
    "burundi": {"name": "Burundi", "freedom_house_slug": "burundi", "world_bank_code": "BDI", "wb_url_code": "BI"},
    "cambodge": {"name": "Cambodge", "freedom_house_slug": "cambodia", "world_bank_code": "KHM", "wb_url_code": "KH"},
    "cameroun": {"name": "Cameroun", "freedom_house_slug": "cameroon", "world_bank_code": "CMR", "wb_url_code": "CM"},
    "cap_vert": {"name": "Cap-Vert", "freedom_house_slug": "cape-verde", "world_bank_code": "CPV", "wb_url_code": "CV"},
    "chili": {"name": "Chili", "freedom_house_slug": "chile", "world_bank_code": "CHL", "wb_url_code": "CL"},
    "chine": {"name": "Chine", "freedom_house_slug": "china", "world_bank_code": "CHN", "wb_url_code": "CN"},
    "colombie": {"name": "Colombie", "freedom_house_slug": "colombia", "world_bank_code": "COL", "wb_url_code": "CO"},
    "comores": {"name": "Comores", "freedom_house_slug": "comoros", "world_bank_code": "COM", "wb_url_code": "KM"},
    "congo": {"name": "Congo (Brazzaville)", "freedom_house_slug": "republic-of-congo", "world_bank_code": "COG", "wb_url_code": "CG"},
    "costa_rica": {"name": "Costa Rica", "freedom_house_slug": "costa-rica", "world_bank_code": "CRI", "wb_url_code": "CR"},
    "cote_ivoire": {"name": "Côte d'Ivoire", "freedom_house_slug": "cote-divoire", "world_bank_code": "CIV", "wb_url_code": "CI"},
    "cuba": {"name": "Cuba", "freedom_house_slug": "cuba", "world_bank_code": "CUB", "wb_url_code": "CU"},
    "djibouti": {"name": "Djibouti", "freedom_house_slug": "djibouti", "world_bank_code": "DJI", "wb_url_code": "DJ"},
    "dominique": {"name": "Dominique", "freedom_house_slug": "dominica", "world_bank_code": "DMA", "wb_url_code": "DM"},
    "egypte": {"name": "Égypte", "freedom_house_slug": "egypt", "world_bank_code": "EGY", "wb_url_code": "EG"},
    "equateur": {"name": "Équateur", "freedom_house_slug": "ecuador", "world_bank_code": "ECU", "wb_url_code": "EC"},
    "erythree": {"name": "Érythrée", "freedom_house_slug": "eritrea", "world_bank_code": "ERI", "wb_url_code": "ER"},
    "eswatini": {"name": "Eswatini", "freedom_house_slug": "eswatini", "world_bank_code": "SWZ", "wb_url_code": "SZ"},
    "ethiopie": {"name": "Éthiopie", "freedom_house_slug": "ethiopia", "world_bank_code": "ETH", "wb_url_code": "ET"},
    "fidji": {"name": "Fidji", "freedom_house_slug": "fiji", "world_bank_code": "FJI", "wb_url_code": "FJ"},
    "gabon": {"name": "Gabon", "freedom_house_slug": "gabon", "world_bank_code": "GAB", "wb_url_code": "GA"},
    "gambie": {"name": "Gambie", "freedom_house_slug": "gambia", "world_bank_code": "GMB", "wb_url_code": "GM"},
    "georgie": {"name": "Géorgie", "freedom_house_slug": "georgia", "world_bank_code": "GEO", "wb_url_code": "GE"},
    "ghana": {"name": "Ghana", "freedom_house_slug": "ghana", "world_bank_code": "GHA", "wb_url_code": "GH"},
    "grenade": {"name": "Grenade", "freedom_house_slug": "grenada", "world_bank_code": "GRD", "wb_url_code": "GD"},
    "guatemala": {"name": "Guatemala", "freedom_house_slug": "guatemala", "world_bank_code": "GTM", "wb_url_code": "GT"},
    "guinee": {"name": "Guinée", "freedom_house_slug": "guinea", "world_bank_code": "GIN", "wb_url_code": "GN"},
    "guinee_bissau": {"name": "Guinée-Bissau", "freedom_house_slug": "guinea-bissau", "world_bank_code": "GNB", "wb_url_code": "GW"},
    "guinee_equatoriale": {"name": "Guinée équatoriale", "freedom_house_slug": "equatorial-guinea", "world_bank_code": "GNQ", "wb_url_code": "GQ"},
    "guyana": {"name": "Guyana", "freedom_house_slug": "guyana", "world_bank_code": "GUY", "wb_url_code": "GY"},
    "haiti": {"name": "Haïti", "freedom_house_slug": "haiti", "world_bank_code": "HTI", "wb_url_code": "HT"},
    "honduras": {"name": "Honduras", "freedom_house_slug": "honduras", "world_bank_code": "HND", "wb_url_code": "HN"},
    "iles_salomon": {"name": "Îles Salomon", "freedom_house_slug": "solomon-islands", "world_bank_code": "SLB", "wb_url_code": "SB"},
    "inde": {"name": "Inde", "freedom_house_slug": "india", "world_bank_code": "IND", "wb_url_code": "IN"},
    "indonesie": {"name": "Indonésie", "freedom_house_slug": "indonesia", "world_bank_code": "IDN", "wb_url_code": "ID"},
    "irak": {"name": "Irak", "freedom_house_slug": "iraq", "world_bank_code": "IRQ", "wb_url_code": "IQ"},
    "jamaique": {"name": "Jamaïque", "freedom_house_slug": "jamaica", "world_bank_code": "JAM", "wb_url_code": "JM"},
    "jordanie": {"name": "Jordanie", "freedom_house_slug": "jordan", "world_bank_code": "JOR", "wb_url_code": "JO"},
    "kazakhstan": {"name": "Kazakhstan", "freedom_house_slug": "kazakhstan", "world_bank_code": "KAZ", "wb_url_code": "KZ"},
    "kenya": {"name": "Kenya", "freedom_house_slug": "kenya", "world_bank_code": "KEN", "wb_url_code": "KE"},
    "kirghizistan": {"name": "Kirghizistan", "freedom_house_slug": "kyrgyzstan", "world_bank_code": "KGZ", "wb_url_code": "KG"},
    "kosovo": {"name": "Kosovo", "freedom_house_slug": "kosovo", "world_bank_code": "XKX", "wb_url_code": "XK"},
    "laos": {"name": "Laos", "freedom_house_slug": "laos", "world_bank_code": "LAO", "wb_url_code": "LA"},
    "lesotho": {"name": "Lesotho", "freedom_house_slug": "lesotho", "world_bank_code": "LSO", "wb_url_code": "LS"},
    "liban": {"name": "Liban", "freedom_house_slug": "lebanon", "world_bank_code": "LBN", "wb_url_code": "LB"},
    "liberia": {"name": "Libéria", "freedom_house_slug": "liberia", "world_bank_code": "LBR", "wb_url_code": "LR"},
    "libye": {"name": "Libye", "freedom_house_slug": "libya", "world_bank_code": "LBY", "wb_url_code": "LY"},
    "macedoine_du_nord": {"name": "Macédoine du Nord", "freedom_house_slug": "north-macedonia", "world_bank_code": "MKD", "wb_url_code": "MK"},
    "madagascar": {"name": "Madagascar", "freedom_house_slug": "madagascar", "world_bank_code": "MDG", "wb_url_code": "MG"},
    "malawi": {"name": "Malawi", "freedom_house_slug": "malawi", "world_bank_code": "MWI", "wb_url_code": "MW"},
    "maldives": {"name": "Maldives", "freedom_house_slug": "maldives", "world_bank_code": "MDV", "wb_url_code": "MV"},
    "mali": {"name": "Mali", "freedom_house_slug": "mali", "world_bank_code": "MLI", "wb_url_code": "ML"},
    "maroc": {"name": "Maroc", "freedom_house_slug": "morocco", "world_bank_code": "MAR", "wb_url_code": "MA"},
    "maurice": {"name": "Maurice", "freedom_house_slug": "mauritius", "world_bank_code": "MUS", "wb_url_code": "MU"},
    "mauritanie": {"name": "Mauritanie", "freedom_house_slug": "mauritania", "world_bank_code": "MRT", "wb_url_code": "MR"},
    "mexique": {"name": "Mexique", "freedom_house_slug": "mexico", "world_bank_code": "MEX", "wb_url_code": "MX"},
    "moldavie": {"name": "Moldavie", "freedom_house_slug": "moldova", "world_bank_code": "MDA", "wb_url_code": "MD"},
    "mongolie": {"name": "Mongolie", "freedom_house_slug": "mongolia", "world_bank_code": "MNG", "wb_url_code": "MN"},
    "montenegro": {"name": "Monténégro", "freedom_house_slug": "montenegro", "world_bank_code": "MNE", "wb_url_code": "ME"},
    "mozambique": {"name": "Mozambique", "freedom_house_slug": "mozambique", "world_bank_code": "MOZ", "wb_url_code": "MZ"},
    "namibie": {"name": "Namibie", "freedom_house_slug": "namibia", "world_bank_code": "NAM", "wb_url_code": "NA"},
    "nepal": {"name": "Népal", "freedom_house_slug": "nepal", "world_bank_code": "NPL", "wb_url_code": "NP"},
    "nicaragua": {"name": "Nicaragua", "freedom_house_slug": "nicaragua", "world_bank_code": "NIC", "wb_url_code": "NI"},
    "niger": {"name": "Niger", "freedom_house_slug": "niger", "world_bank_code": "NER", "wb_url_code": "NE"},
    "nigeria": {"name": "Nigéria", "freedom_house_slug": "nigeria", "world_bank_code": "NGA", "wb_url_code": "NG"},
    "ouganda": {"name": "Ouganda", "freedom_house_slug": "uganda", "world_bank_code": "UGA", "wb_url_code": "UG"},
    "ouzbekistan": {"name": "Ouzbékistan", "freedom_house_slug": "uzbekistan", "world_bank_code": "UZB", "wb_url_code": "UZ"},
    "pakistan": {"name": "Pakistan", "freedom_house_slug": "pakistan", "world_bank_code": "PAK", "wb_url_code": "PK"},
    "panama": {"name": "Panama", "freedom_house_slug": "panama", "world_bank_code": "PAN", "wb_url_code": "PA"},
    "paraguay": {"name": "Paraguay", "freedom_house_slug": "paraguay", "world_bank_code": "PRY", "wb_url_code": "PY"},
    "perou": {"name": "Pérou", "freedom_house_slug": "peru", "world_bank_code": "PER", "wb_url_code": "PE"},
    "philippines": {"name": "Philippines", "freedom_house_slug": "philippines", "world_bank_code": "PHL", "wb_url_code": "PH"},
    "rdc": {"name": "RDC (Congo-Kinshasa)", "freedom_house_slug": "democratic-republic-of-congo", "world_bank_code": "COD", "wb_url_code": "CD"},
    "republique_dominicaine": {"name": "République dominicaine", "freedom_house_slug": "dominican-republic", "world_bank_code": "DOM", "wb_url_code": "DO"},
    "rwanda": {"name": "Rwanda", "freedom_house_slug": "rwanda", "world_bank_code": "RWA", "wb_url_code": "RW"},
    "sainte_lucie": {"name": "Sainte-Lucie", "freedom_house_slug": "saint-lucia", "world_bank_code": "LCA", "wb_url_code": "LC"},
    "saint_vincent": {"name": "Saint-Vincent-et-les-Grenadines", "freedom_house_slug": "saint-vincent-and-the-grenadines", "world_bank_code": "VCT", "wb_url_code": "VC"},
    "salvador": {"name": "Salvador", "freedom_house_slug": "el-salvador", "world_bank_code": "SLV", "wb_url_code": "SV"},
    "samoa": {"name": "Samoa", "freedom_house_slug": "samoa", "world_bank_code": "WSM", "wb_url_code": "WS"},
    "sao_tome": {"name": "Sao Tomé-et-Principe", "freedom_house_slug": "sao-tome-and-principe", "world_bank_code": "STP", "wb_url_code": "ST"},
    "senegal": {"name": "Sénégal", "freedom_house_slug": "senegal", "world_bank_code": "SEN", "wb_url_code": "SN"},
    "serbie": {"name": "Serbie", "freedom_house_slug": "serbia", "world_bank_code": "SRB", "wb_url_code": "RS"},
    "seychelles": {"name": "Seychelles", "freedom_house_slug": "seychelles", "world_bank_code": "SYC", "wb_url_code": "SC"},
    "sierra_leone": {"name": "Sierra Leone", "freedom_house_slug": "sierra-leone", "world_bank_code": "SLE", "wb_url_code": "SL"},
    "somalie": {"name": "Somalie", "freedom_house_slug": "somalia", "world_bank_code": "SOM", "wb_url_code": "SO"},
    "soudan": {"name": "Soudan", "freedom_house_slug": "sudan", "world_bank_code": "SDN", "wb_url_code": "SD"},
    "sri_lanka": {"name": "Sri Lanka", "freedom_house_slug": "sri-lanka", "world_bank_code": "LKA", "wb_url_code": "LK"},
    "suriname": {"name": "Suriname", "freedom_house_slug": "suriname", "world_bank_code": "SUR", "wb_url_code": "SR"},
    "syrie": {"name": "Syrie", "freedom_house_slug": "syria", "world_bank_code": "SYR", "wb_url_code": "SY"},
    "tadjikistan": {"name": "Tadjikistan", "freedom_house_slug": "tajikistan", "world_bank_code": "TJK", "wb_url_code": "TJ"},
    "tanzanie": {"name": "Tanzanie", "freedom_house_slug": "tanzania", "world_bank_code": "TZA", "wb_url_code": "TZ"},
    "tchad": {"name": "Tchad", "freedom_house_slug": "chad", "world_bank_code": "TCD", "wb_url_code": "TD"},
    "thailande": {"name": "Thaïlande", "freedom_house_slug": "thailand", "world_bank_code": "THA", "wb_url_code": "TH"},
    "timor_leste": {"name": "Timor-Leste", "freedom_house_slug": "timor-leste", "world_bank_code": "TLS", "wb_url_code": "TL"},
    "togo": {"name": "Togo", "freedom_house_slug": "togo", "world_bank_code": "TGO", "wb_url_code": "TG"},
    "tunisie": {"name": "Tunisie", "freedom_house_slug": "tunisia", "world_bank_code": "TUN", "wb_url_code": "TN"},
    "turquie": {"name": "Turquie", "freedom_house_slug": "turkey", "world_bank_code": "TUR", "wb_url_code": "TR"},
    "ukraine": {"name": "Ukraine", "freedom_house_slug": "ukraine", "world_bank_code": "UKR", "wb_url_code": "UA"},
    "uruguay": {"name": "Uruguay", "freedom_house_slug": "uruguay", "world_bank_code": "URY", "wb_url_code": "UY"},
    "vanuatu": {"name": "Vanuatu", "freedom_house_slug": "vanuatu", "world_bank_code": "VUT", "wb_url_code": "VU"},
    "vietnam": {"name": "Vietnam", "freedom_house_slug": "vietnam", "world_bank_code": "VNM", "wb_url_code": "VN"},
    "yemen": {"name": "Yémen", "freedom_house_slug": "yemen", "world_bank_code": "YEM", "wb_url_code": "YE"},
    "zambie": {"name": "Zambie", "freedom_house_slug": "zambia", "world_bank_code": "ZMB", "wb_url_code": "ZM"},
    "zimbabwe": {"name": "Zimbabwe", "freedom_house_slug": "zimbabwe", "world_bank_code": "ZWE", "wb_url_code": "ZW"},
}

# Traduction des catégories de revenu Banque Mondiale
INCOME_LABELS = {
    "LIC":  "PFR — Pays à faible revenu",
    "LMC":  "PRITI — Rev. intermédiaire tranche inf.",
    "UMC":  "PRITS — Rev. intermédiaire tranche sup.",
    "HIC":  "PRE — Pays à revenu élevé",
    "INX":  "Non classifié",
}


# ─────────────────────────────────────────────
# Fonctions de récupération
# ─────────────────────────────────────────────

def fetch_freedom_house(country_slug, year=2026):
    url = f"https://freedomhouse.org/country/{country_slug}/freedom-world/{year}"
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get(url, timeout=30, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        text = re.sub(r"\s+", " ", soup.get_text(" ", strip=True))

        result = {"status": None, "score": None, "pr_score": None,
                  "cl_score": None, "year": year, "url": url, "error": None}

        if re.search(r"\bNot Free\b", text):
            result["status"] = "Not Free"
        elif re.search(r"\bPartly Free\b", text):
            result["status"] = "Partly Free"
        elif re.search(r"\bFree\b", text):
            result["status"] = "Free"

        m = re.search(r"(?:Total Score and Status|score)\s+(\d{1,3})\s*/?\s*100", text, re.IGNORECASE)
        if m:
            result["score"] = int(m.group(1))
        else:
            m2 = re.search(r"\b(\d{1,3})\s*/?\s*100\b", text)
            if m2:
                result["score"] = int(m2.group(1))

        pr = re.search(r"Political Rights\s+(\d{1,2})\s*/?\s*40", text, re.IGNORECASE)
        if pr:
            result["pr_score"] = int(pr.group(1))
        cl = re.search(r"Civil Liberties\s+(\d{1,2})\s*/?\s*60", text, re.IGNORECASE)
        if cl:
            result["cl_score"] = int(cl.group(1))
        return result
    except Exception as e:
        return {"error": str(e), "url": url}


def fetch_wb_history(country_code, indicator_code, n_years=10):
    """Retourne les n dernières années avec données non nulles."""
    url = f"https://api.worldbank.org/v2/country/{country_code}/indicator/{indicator_code}?format=json&per_page=200"
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        data = r.json()
        if not isinstance(data, list) or len(data) < 2 or data[1] is None:
            return []
        rows = [{"year": int(row["date"]), "value": row["value"]}
                for row in data[1] if row["value"] is not None]
        rows.sort(key=lambda x: x["year"])
        return rows[-n_years:]
    except Exception:
        return []


def fetch_wb_country_info(country_code):
    """Récupère le statut de revenu et la région depuis l'API WB."""
    url = f"https://api.worldbank.org/v2/country/{country_code}?format=json"
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        data = r.json()
        if not isinstance(data, list) or len(data) < 2 or not data[1]:
            return None
        c = data[1][0]
        return {
            "income_code": c.get("incomeLevel", {}).get("id", ""),
            "income_label": c.get("incomeLevel", {}).get("value", ""),
            "region": c.get("region", {}).get("value", ""),
        }
    except Exception:
        return None


def compute_trend(history):
    if not history:
        return None, None, None
    current = history[-1]["value"]
    if len(history) >= 5 and current:
        old = history[-5]["value"]
        if old:
            delta = current - old
            pct = abs(delta) / abs(old) * 100 if old != 0 else 0
            if pct > 3:
                arrow = "↗" if delta > 0 else "↘"
            else:
                arrow = "→"
            return current, delta, arrow
    return current, None, None


# ─────────────────────────────────────────────
# Fonctions d'affichage
# ─────────────────────────────────────────────

def render_metric(label, value_str, sub=None, trend_arrow=None, delta_str=None):
    """Carte métrique avec tendance optionnelle."""
    if trend_arrow == "↗":
        arrow_html = f'<span class="trend-up" style="font-size:20px;margin-left:6px">↗</span>'
        delta_html = f'<span class="trend-up" style="font-size:11px;margin-left:4px">{delta_str}</span>' if delta_str else ""
    elif trend_arrow == "↘":
        arrow_html = f'<span class="trend-down" style="font-size:20px;margin-left:6px">↘</span>'
        delta_html = f'<span class="trend-down" style="font-size:11px;margin-left:4px">{delta_str}</span>' if delta_str else ""
    elif trend_arrow == "→":
        arrow_html = f'<span class="trend-flat" style="font-size:20px;margin-left:6px">→</span>'
        delta_html = ""
    else:
        arrow_html = ""
        delta_html = ""

    sub_html = f'<div class="metric-sub">{sub}</div>' if sub else ""
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value_str}{arrow_html}{delta_html}</div>
        {sub_html}
    </div>""", unsafe_allow_html=True)


def render_na(label, reason="Données non disponibles"):
    st.markdown(f'<div class="na-box">— <strong>{label}</strong> : {reason}</div>', unsafe_allow_html=True)


def render_status_badge(status):
    mapping = {
        "Free":        ("badge-free",    "● Libre"),
        "Partly Free": ("badge-partly",  "● Partiellement libre"),
        "Not Free":    ("badge-notfree", "● Non libre"),
    }
    css, label = mapping.get(status, ("", "Inconnu"))
    style = f'class="status-badge {css}"' if css else 'class="status-badge" style="background:#222;color:#888;"'
    return f'<span {style}>{label}</span>'


def format_population(v):
    if v is None: return "N/A"
    if v >= 1_000_000: return f"{v/1_000_000:.1f}M"
    if v >= 1_000: return f"{v/1_000:.0f}K"
    return str(int(v))


def show_chart(history, color, label):
    """Affiche un graphique d'évolution dans un expander."""
    if not history:
        st.markdown('<div class="na-box">Pas de données historiques disponibles</div>', unsafe_allow_html=True)
        return
    with st.expander(f"📈 Évolution sur {len(history)} ans"):
        df = pd.DataFrame(history).set_index("year").rename(columns={"value": label})
        st.line_chart(df, color=color)


def source_note(url, label="Banque Mondiale"):
    st.markdown(f'<p class="source-note">Source : <a href="{url}" style="color:#444">{label}</a></p>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Interface principale
# ─────────────────────────────────────────────
st.markdown('<div class="title-block">', unsafe_allow_html=True)
st.markdown("# 🌍 Outil de collecte de données — DER")
st.markdown('<p style="color:#444; font-size:14px; margin-top:-8px;">Données politiques et économiques par pays</p>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

country_options = dict(sorted({info["name"]: key for key, info in COUNTRY_MAPPING.items()}.items()))
selected_name = st.selectbox("Sélectionner un pays", options=list(country_options.keys()))
selected_key = country_options[selected_name]
country_info = COUNTRY_MAPPING[selected_key]
wb_code = country_info["world_bank_code"]

st.write("")

if st.button("Récupérer les données →"):

    # ══════════════════════════════════════════════════════
    # SECTION 1 — EN-TÊTE
    # ══════════════════════════════════════════════════════
    st.markdown('<div class="section-title">📋 En-tête</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Indicateurs de gouvernance et de positionnement du pays</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    # — Freedom House —
    with col1:
        st.markdown('<div class="source-header">Freedom House</div>', unsafe_allow_html=True)
        with st.spinner("Chargement..."):
            fh = fetch_freedom_house(country_info["freedom_house_slug"])
        if fh.get("error"):
            st.markdown(f'<div class="error-box">⚠ Indisponible — {fh["error"]}</div>', unsafe_allow_html=True)
        else:
            score_str = f"{fh['score']}/100" if fh.get("score") is not None else "N/A"
            render_metric("Score liberté", score_str, f"Année {fh['year']}")
            if fh.get("status"):
                badge = render_status_badge(fh["status"])
                st.markdown(f"""<div class="metric-card">
                    <div class="metric-label">Statut</div>
                    <div style="margin-top:8px">{badge}</div>
                </div>""", unsafe_allow_html=True)
            c3, c4 = st.columns(2)
            with c3:
                render_metric("Droits politiques", f"{fh['pr_score']}/40" if fh.get("pr_score") is not None else "N/A")
            with c4:
                render_metric("Libertés civiles", f"{fh['cl_score']}/60" if fh.get("cl_score") is not None else "N/A")
        source_note(fh.get("url", "https://freedomhouse.org"), "freedomhouse.org")

    # — WGI + PIB + Statut —
    with col2:
        st.markdown('<div class="source-header">Banque Mondiale</div>', unsafe_allow_html=True)
        with st.spinner("Chargement..."):
            gdp_hist    = fetch_wb_history(wb_code, "NY.GDP.PCAP.CD")
            wgi_hist    = fetch_wb_history(wb_code, "IQ.WGI.GOVS.NO.SRC")  # Governance score synthétique
            wb_info     = fetch_wb_country_info(wb_code)

        # PIB / habitant
        val, delta, arrow = compute_trend(gdp_hist)
        if val:
            delta_str = f"{'+' if delta > 0 else ''}{delta:,.0f} $ sur 5 ans" if delta else None
            render_metric("PIB / habitant", f"${val:,.0f}", f"Année {gdp_hist[-1]['year']}", arrow, delta_str)
            show_chart(gdp_hist, "#f0a500", "PIB/hab ($)")
        else:
            render_na("PIB / habitant")

        # WGI Gouvernance
        val_wgi, delta_wgi, arrow_wgi = compute_trend(wgi_hist)
        if val_wgi:
            delta_str_wgi = f"{'+' if delta_wgi > 0 else ''}{delta_wgi:.2f} sur 5 ans" if delta_wgi else None
            render_metric("Gouvernance (WGI)", f"{val_wgi:.2f}", f"Année {wgi_hist[-1]['year']}", arrow_wgi, delta_str_wgi)
            show_chart(wgi_hist, "#8888ff", "WGI Gouvernance")
        else:
            render_na("Gouvernance WGI", "Indicateur non disponible pour ce pays")

        # Statut du pays
        if wb_info:
            income_code = wb_info.get("income_code", "")
            label_fr = INCOME_LABELS.get(income_code, wb_info.get("income_label", "Non classifié"))
            st.markdown(f"""<div class="metric-card">
                <div class="metric-label">Statut de revenu</div>
                <div style="margin-top:8px"><span class="income-badge">{label_fr}</span></div>
                <div class="metric-sub" style="margin-top:8px">Région : {wb_info.get('region', '—')}</div>
            </div>""", unsafe_allow_html=True)
        else:
            render_na("Statut du pays")

        wb_url = f"https://data.worldbank.org/country/{country_info['wb_url_code']}"
        source_note(wb_url)

    # ══════════════════════════════════════════════════════
    # SECTION 2 — MARCHÉ DU TRAVAIL
    # ══════════════════════════════════════════════════════
    st.markdown('<div class="section-title">💼 Marché du travail</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Taux d\'emploi — Source : Banque Mondiale (OIT)</div>', unsafe_allow_html=True)

    with st.spinner("Chargement marché du travail..."):
        emp_total_hist  = fetch_wb_history(wb_code, "SL.EMP.TOTL.SP.ZS")   # Emploi total (% pop. active)
        emp_youth_hist  = fetch_wb_history(wb_code, "SL.UEM.1524.ZS")       # Chômage jeunes (15-24)
        emp_women_hist  = fetch_wb_history(wb_code, "SL.EMP.TOTL.SP.FE.ZS") # Emploi femmes (% pop. fém. active)

    col_e1, col_e2, col_e3 = st.columns(3)

    with col_e1:
        val, delta, arrow = compute_trend(emp_total_hist)
        if val:
            delta_str = f"{'+' if delta > 0 else ''}{delta:.1f} pts sur 5 ans" if delta else None
            render_metric("Emploi total", f"{val:.1f}%", f"Année {emp_total_hist[-1]['year']}", arrow, delta_str)
            show_chart(emp_total_hist, "#4caf7d", "Emploi total (%)")
        else:
            render_na("Emploi total")

    with col_e2:
        val, delta, arrow = compute_trend(emp_youth_hist)
        if val:
            delta_str = f"{'+' if delta > 0 else ''}{delta:.1f} pts sur 5 ans" if delta else None
            render_metric("Chômage jeunes", f"{val:.1f}%", f"15-24 ans — {emp_youth_hist[-1]['year']}", arrow, delta_str)
            show_chart(emp_youth_hist, "#f0a500", "Chômage jeunes (%)")
        else:
            render_na("Emploi jeunes")

    with col_e3:
        val, delta, arrow = compute_trend(emp_women_hist)
        if val:
            delta_str = f"{'+' if delta > 0 else ''}{delta:.1f} pts sur 5 ans" if delta else None
            render_metric("Emploi femmes", f"{val:.1f}%", f"Année {emp_women_hist[-1]['year']}", arrow, delta_str)
            show_chart(emp_women_hist, "#c084fc", "Emploi femmes (%)")
        else:
            render_na("Emploi femmes")

    source_note(f"https://data.worldbank.org/country/{country_info['wb_url_code']}")

    # ══════════════════════════════════════════════════════
    # SECTION 3 — PAUVRETÉ ET INÉGALITÉS
    # ══════════════════════════════════════════════════════
    st.markdown('<div class="section-title">📊 Pauvreté et inégalités</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Source : Banque Mondiale (PovcalNet / WDI)</div>', unsafe_allow_html=True)

    with st.spinner("Chargement pauvreté..."):
        poverty_hist = fetch_wb_history(wb_code, "SI.POV.DDAY")   # Pauvreté < 2,15$/jour
        gini_hist    = fetch_wb_history(wb_code, "SI.POV.GINI")   # Indice de Gini

    col_p1, col_p2 = st.columns(2)

    with col_p1:
        val, delta, arrow = compute_trend(poverty_hist)
        if val:
            delta_str = f"{'+' if delta > 0 else ''}{delta:.1f} pts sur 5 ans" if delta else None
            render_metric("Taux de pauvreté", f"{val:.1f}%", f"< 2,15$/j — {poverty_hist[-1]['year']}", arrow, delta_str)
            show_chart(poverty_hist, "#e05555", "Pauvreté < 2,15$/j (%)")
        else:
            render_na("Taux de pauvreté", "Souvent absent pour les pays à revenu intermédiaire")

    with col_p2:
        val, delta, arrow = compute_trend(gini_hist)
        if val:
            delta_str = f"{'+' if delta > 0 else ''}{delta:.1f} pts sur 5 ans" if delta else None
            render_metric("Indice de Gini", f"{val:.1f}", f"Année {gini_hist[-1]['year']}", arrow, delta_str)
            show_chart(gini_hist, "#f0a500", "Gini")
        else:
            render_na("Indice de Gini", "Enquêtes disponibles par intermittence")

    source_note(f"https://data.worldbank.org/country/{country_info['wb_url_code']}")

    # ══════════════════════════════════════════════════════
    # SECTION 4 — ÉDUCATION
    # ══════════════════════════════════════════════════════
    st.markdown('<div class="section-title">🎓 Éducation</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Source : Banque Mondiale / UNESCO</div>', unsafe_allow_html=True)

    with st.spinner("Chargement éducation..."):
        prim_hist  = fetch_wb_history(wb_code, "SE.PRM.ENRR")   # Scolarisation primaire (brut)
        sec_hist   = fetch_wb_history(wb_code, "SE.SEC.ENRR")   # Scolarisation secondaire (brut)
        tert_hist  = fetch_wb_history(wb_code, "SE.TER.ENRR")   # Scolarisation tertiaire (brut)

    col_s1, col_s2, col_s3 = st.columns(3)

    with col_s1:
        val, delta, arrow = compute_trend(prim_hist)
        if val:
            delta_str = f"{'+' if delta > 0 else ''}{delta:.1f} pts sur 5 ans" if delta else None
            render_metric("Scolarisation primaire", f"{val:.1f}%", f"Taux brut — {prim_hist[-1]['year']}", arrow, delta_str)
            show_chart(prim_hist, "#4caf7d", "Primaire (%)")
        else:
            render_na("Scolarisation primaire")

    with col_s2:
        val, delta, arrow = compute_trend(sec_hist)
        if val:
            delta_str = f"{'+' if delta > 0 else ''}{delta:.1f} pts sur 5 ans" if delta else None
            render_metric("Scolarisation secondaire", f"{val:.1f}%", f"Taux brut — {sec_hist[-1]['year']}", arrow, delta_str)
            show_chart(sec_hist, "#f0a500", "Secondaire (%)")
        else:
            render_na("Scolarisation secondaire")

    with col_s3:
        val, delta, arrow = compute_trend(tert_hist)
        if val:
            delta_str = f"{'+' if delta > 0 else ''}{delta:.1f} pts sur 5 ans" if delta else None
            render_metric("Scolarisation tertiaire", f"{val:.1f}%", f"Taux brut — {tert_hist[-1]['year']}", arrow, delta_str)
            show_chart(tert_hist, "#8888ff", "Tertiaire (%)")
        else:
            render_na("Scolarisation tertiaire")

    source_note(f"https://data.worldbank.org/country/{country_info['wb_url_code']}")
