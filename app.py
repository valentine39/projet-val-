import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import os

# ─────────────────────────────────────────────
# Configuration de la page
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Outil de collecte de données - DER",
    page_icon="🌍",
    layout="wide"
)

# ─────────────────────────────────────────────
# Style visuel
# ─────────────────────────────────────────────
st.markdown("""
<style>
    html, body, [class*="css"] {
        font-family: "Century Gothic", "Trebuchet MS", Arial, sans-serif;
        color: #111111;
    }

    .stApp {
        background-color: #ffffff;
        color: #111111;
    }

    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1.5rem;
        max-width: 1200px;
    }

    h1, h2, h3 {
        font-family: "Century Gothic", "Trebuchet MS", Arial, sans-serif;
        color: #111111;
    }

    .title-block {
        margin-bottom: 24px;
    }

    .section-title {
        font-size: 20px;
        font-weight: 700;
        color: #111111;
        margin: 28px 0 4px 0;
    }

    .section-subtitle {
        font-size: 12px;
        color: #666666;
        margin-bottom: 10px;
    }

    .source-note {
        font-size: 11px;
        color: #666666;
        margin-top: 4px;
        margin-bottom: 4px;
    }

    .source-header {
        font-size: 11px;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #777777;
        border-bottom: 1px solid #dddddd;
        padding-bottom: 6px;
        margin: 14px 0 10px 0;
    }

    .metric-card {
        background: #f7f7f5;
        border: 1px solid #e1ddd6;
        border-radius: 10px;
        padding: 10px 14px;
        margin-bottom: 8px;
    }

    .metric-label {
        font-size: 9px;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #6b6b6b;
        margin-bottom: 2px;
    }

    .metric-value {
        font-size: 18px;
        font-weight: 700;
        color: #111111;
        line-height: 1.1;
    }

    .metric-sub {
        font-size: 10px;
        color: #777777;
        margin-top: 2px;
    }

    .status-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 14px;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.02em;
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
        padding: 2px 8px;
        border-radius: 14px;
        font-size: 11px;
        font-weight: 600;
        background: #eef2ff;
        color: #4b5fc7;
        border: 1px solid #d9e0ff;
    }

    .error-box {
        background: #fff4f4;
        border: 1px solid #f0c8c8;
        border-radius: 10px;
        padding: 10px 12px;
        color: #b42318;
        font-size: 12px;
        margin-bottom: 8px;
    }

    .na-box {
        background: #f8f8f8;
        border: 1px solid #e1e1e1;
        border-radius: 10px;
        padding: 8px 12px;
        color: #666666;
        font-size: 12px;
        margin-bottom: 8px;
    }

    .trend-up { color: #1f8f55; font-size: 18px; }
    .trend-down { color: #c0392b; font-size: 18px; }
    .trend-flat { color: #777777; font-size: 18px; }

    div[data-testid="stButton"] button {
        background: #111111;
        color: white;
        font-family: "Century Gothic", "Trebuchet MS", Arial, sans-serif;
        font-weight: 700;
        font-size: 13px;
        letter-spacing: 0.05em;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        width: 100%;
    }

    div[data-testid="stSelectbox"] label {
        color: #666666;
        font-size: 11px;
        letter-spacing: 0.08em;
        text-transform: uppercase;
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

VDEM_LABELS = {
    "v2x_polyarchy":      "Démocratie électorale",
    "v2x_libdem":         "Démocratie libérale",
    "v2x_partipdem":      "Démocratie participative",
    "v2x_egaldem":        "Démocratie égalitaire",
    "v2x_freexp_altinf":  "Liberté d'expression",
    "v2x_frassoc_thick":  "Liberté d'association",
    "v2x_cspart":         "Participation société civile",
    "v2x_corr":           "Corruption (index)",
    "v2x_rule":           "État de droit",
}

# ─────────────────────────────────────────────
# Chargement V-Dem
# ─────────────────────────────────────────────
@st.cache_data
def load_vdem():
    try:
        return pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "vdem_data.csv"))
    except Exception:
        return None

# ─────────────────────────────────────────────
# Freedom House
# ─────────────────────────────────────────────
def fetch_freedom_house(country_slug, year=2026):
    url = f"https://freedomhouse.org/country/{country_slug}/freedom-world/{year}"
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, timeout=30, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        text = re.sub(r"\s+", " ", soup.get_text(" ", strip=True))

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

        result["country"] = (
            soup.title.string.split(":")[0].strip()
            if soup.title and soup.title.string
            else country_slug.replace("-", " ").title()
        )

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

# ─────────────────────────────────────────────
# Banque mondiale
# ─────────────────────────────────────────────
def fetch_wb_history(country_code, indicator_code, n_years=10):
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
            "region": c.get("region", {}).get("value", "")
        }
    except Exception:
        return None

INCOME_LABELS = {
    "LIC": "PFR — Pays à faible revenu",
    "LMC": "PRITI — Rev. intermédiaire tranche inf.",
    "UMC": "PRITS — Rev. intermédiaire tranche sup.",
    "HIC": "PRE — Pays à revenu élevé",
    "INX": "Non classifié",
}

# ─────────────────────────────────────────────
# Construction mécanique des sections
# ─────────────────────────────────────────────
def build_header_table(country_name, fh, gdp_hist, wb_info):
    rows = []

    if fh and not fh.get("error"):
        rows.append({
            "Indicateur": "Freedom House — score",
            "Valeur": f"{fh['score']}/100" if fh.get("score") is not None else "N/A",
            "Année": fh.get("year"),
            "Source": "Freedom House"
        })
        rows.append({
            "Indicateur": "Freedom House — statut",
            "Valeur": fh.get("status", "N/A"),
            "Année": fh.get("year"),
            "Source": "Freedom House"
        })

    if gdp_hist:
        last = gdp_hist[-1]
        rows.append({
            "Indicateur": "PIB / habitant",
            "Valeur": f"${last['value']:,.0f}",
            "Année": last["year"],
            "Source": "Banque mondiale"
        })

    if wb_info:
        income_code = wb_info.get("income_code", "")
        income_label = INCOME_LABELS.get(income_code, wb_info.get("income_label", "Non classifié"))
        rows.append({
            "Indicateur": "Statut de revenu",
            "Valeur": income_label,
            "Année": None,
            "Source": "Banque mondiale"
        })
        rows.append({
            "Indicateur": "Région",
            "Valeur": wb_info.get("region", "N/A"),
            "Année": None,
            "Source": "Banque mondiale"
        })

    return pd.DataFrame(rows)

def build_labour_table(emp_total_hist, emp_youth_hist, emp_women_hist):
    rows = []

    if emp_total_hist:
        rows.append({
            "Indicateur": "Taux d'emploi total",
            "Valeur": f"{emp_total_hist[-1]['value']:.1f}%",
            "Année": emp_total_hist[-1]["year"],
            "Source": "Banque mondiale"
        })

    if emp_youth_hist:
        rows.append({
            "Indicateur": "Chômage des jeunes",
            "Valeur": f"{emp_youth_hist[-1]['value']:.1f}%",
            "Année": emp_youth_hist[-1]["year"],
            "Source": "Banque mondiale"
        })

    if emp_women_hist:
        rows.append({
            "Indicateur": "Taux d'emploi des femmes",
            "Valeur": f"{emp_women_hist[-1]['value']:.1f}%",
            "Année": emp_women_hist[-1]["year"],
            "Source": "Banque mondiale"
        })

    return pd.DataFrame(rows)

def build_poverty_table(gini_hist, poverty_hist):
    rows = []

    if poverty_hist:
        rows.append({
            "Indicateur": "Taux de pauvreté (< 2,15$/j)",
            "Valeur": f"{poverty_hist[-1]['value']:.1f}%",
            "Année": poverty_hist[-1]["year"],
            "Source": "Banque mondiale"
        })

    if gini_hist:
        rows.append({
            "Indicateur": "Indice de Gini",
            "Valeur": f"{gini_hist[-1]['value']:.1f}",
            "Année": gini_hist[-1]["year"],
            "Source": "Banque mondiale"
        })

    return pd.DataFrame(rows)

def build_education_table(prim_hist, sec_hist, tert_hist):
    rows = []

    if prim_hist:
        rows.append({
            "Indicateur": "Scolarisation primaire (taux brut)",
            "Valeur": f"{prim_hist[-1]['value']:.1f}%",
            "Année": prim_hist[-1]["year"],
            "Source": "Banque mondiale"
        })

    if sec_hist:
        rows.append({
            "Indicateur": "Scolarisation secondaire (taux brut)",
            "Valeur": f"{sec_hist[-1]['value']:.1f}%",
            "Année": sec_hist[-1]["year"],
            "Source": "Banque mondiale"
        })

    if tert_hist:
        rows.append({
            "Indicateur": "Scolarisation tertiaire (taux brut)",
            "Valeur": f"{tert_hist[-1]['value']:.1f}%",
            "Année": tert_hist[-1]["year"],
            "Source": "Banque mondiale"
        })

    return pd.DataFrame(rows)

def build_vdem_table(country_vdem):
    if country_vdem is None or country_vdem.empty:
        return pd.DataFrame()

    latest = country_vdem.sort_values("year").iloc[-1]
    rows = []

    for col, label in VDEM_LABELS.items():
        if col in latest and pd.notna(latest[col]):
            rows.append({
                "Indicateur": label,
                "Valeur": f"{latest[col]:.2f}",
                "Année": int(latest["year"]),
                "Source": "V-Dem"
            })

    return pd.DataFrame(rows)

# ─────────────────────────────────────────────
# Affichage
# ─────────────────────────────────────────────
def render_section_table(title, subtitle, df):
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-subtitle">{subtitle}</div>', unsafe_allow_html=True)

    if df.empty:
        st.markdown('<div class="na-box">Aucune donnée disponible pour cette section.</div>', unsafe_allow_html=True)
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────
# Interface principale
# ─────────────────────────────────────────────
vdem_df = load_vdem()

st.markdown('<div class="title-block">', unsafe_allow_html=True)
st.markdown("# 🌍 Outil de collecte de données — DER")
st.markdown('<p style="color:#6f6f6f; font-size:14px; margin-top:-8px;">Données politiques et économiques par pays</p>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

country_options = dict(sorted({info["name"]: key for key, info in COUNTRY_MAPPING.items()}.items()))
selected_name = st.selectbox("Sélectionner un pays", options=list(country_options.keys()))
selected_key = country_options[selected_name]

if st.button("Récupérer les données →"):
    country_info = COUNTRY_MAPPING[selected_key]
    wb_code = country_info["world_bank_code"]

    # Collecte
    with st.spinner("Chargement des données..."):
        fh = fetch_freedom_house(country_info["freedom_house_slug"])

        gdp_hist = fetch_wb_history(wb_code, "NY.GDP.PCAP.CD")
        wb_info = fetch_wb_country_info(wb_code)

        emp_total_hist = fetch_wb_history(wb_code, "SL.EMP.TOTL.SP.ZS")
        emp_youth_hist = fetch_wb_history(wb_code, "SL.UEM.1524.ZS")
        emp_women_hist = fetch_wb_history(wb_code, "SL.EMP.TOTL.SP.FE.ZS")

        poverty_hist = fetch_wb_history(wb_code, "SI.POV.DDAY")
        gini_hist = fetch_wb_history(wb_code, "SI.POV.GINI")

        prim_hist = fetch_wb_history(wb_code, "SE.PRM.ENRR")
        sec_hist = fetch_wb_history(wb_code, "SE.SEC.ENRR")
        tert_hist = fetch_wb_history(wb_code, "SE.TER.ENRR")

        country_vdem = None
        if vdem_df is not None and "country_name" in vdem_df.columns:
            country_vdem = vdem_df[vdem_df["country_name"] == selected_name]

    # Sections mécaniques
    header_df = build_header_table(country_info["name"], fh, gdp_hist, wb_info)
    labour_df = build_labour_table(emp_total_hist, emp_youth_hist, emp_women_hist)
    poverty_df = build_poverty_table(gini_hist, poverty_hist)
    education_df = build_education_table(prim_hist, sec_hist, tert_hist)
    vdem_table = build_vdem_table(country_vdem)

    # Affichage
    render_section_table(
        "En-tête",
        "Indicateurs synthétiques de positionnement politique et économique",
        header_df
    )

    render_section_table(
        "Marché du travail",
        "Indicateurs d’emploi et d’insertion",
        labour_df
    )

    render_section_table(
        "Pauvreté et inégalités",
        "Mesures synthétiques des conditions de vie et de la distribution",
        poverty_df
    )

    render_section_table(
        "Éducation",
        "Indicateurs de scolarisation actuellement disponibles",
        education_df
    )

    render_section_table(
        "V-Dem",
        "Indicateurs institutionnels issus du dataset V-Dem",
        vdem_table
    )

    # Notes sources
    st.markdown("---")
    st.markdown(
        f'<p class="source-note">Freedom House : <a href="{fh.get("url", "https://freedomhouse.org")}" target="_blank">voir la source</a></p>',
        unsafe_allow_html=True
    )
    st.markdown(
        f'<p class="source-note">Banque mondiale : <a href="https://data.worldbank.org/country/{country_info["wb_url_code"]}" target="_blank">voir la source</a></p>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<p class="source-note">V-Dem : <a href="https://www.v-dem.net" target="_blank">voir la source</a></p>',
        unsafe_allow_html=True
    )
