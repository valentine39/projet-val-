import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import os
from datetime import datetime
from io import BytesIO

# ─────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Outil de collecte de données - DER",
    page_icon="🌍",
    layout="wide"
)

CURRENT_YEAR = datetime.now().year
OLD_DATA_THRESHOLD = 5

# ─────────────────────────────────────────────
# Style
# ─────────────────────────────────────────────
st.markdown("""
<style>
    html, body, [class*="css"] {
        font-family: "Century Gothic", "Trebuchet MS", Arial, sans-serif;
        color: #111111;
    }
    .stApp { background-color: #ffffff; color: #111111; }
    .main .block-container { padding-top: 1rem; padding-bottom: 2rem; max-width: 1200px; }
    h1, h2, h3 { font-family: "Century Gothic", "Trebuchet MS", Arial, sans-serif; color: #111111; }
    .title-block { margin-bottom: 20px; }
    .section-title {
        font-size: 17px; font-weight: 700; color: #111111;
        margin: 32px 0 2px 0; border-left: 4px solid #111111;
        padding-left: 10px;
    }
    .section-subtitle { font-size: 11px; color: #888888; margin-bottom: 8px; padding-left: 14px; }
    .source-note { font-size: 11px; color: #888888; margin-top: 4px; }
    .warn-missing { color: #999999; font-size: 11px; font-style: italic; }
    div[data-testid="stButton"] button {
        background: #111111; color: white;
        font-family: "Century Gothic", "Trebuchet MS", Arial, sans-serif;
        font-weight: 700; font-size: 13px;
        border: none; border-radius: 8px;
        padding: 10px 20px; width: 100%;
    }
    div[data-testid="stSelectbox"] label {
        color: #666666; font-size: 11px;
        letter-spacing: 0.08em; text-transform: uppercase;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Liste des pays
# ─────────────────────────────────────────────
COUNTRY_MAPPING = {
    "afghanistan": {"name": "Afghanistan", "freedom_house_slug": "afghanistan", "world_bank_code": "AFG", "wb_url_code": "AF", "undp_code": "AFG"},
    "afrique_du_sud": {"name": "Afrique du Sud", "freedom_house_slug": "south-africa", "world_bank_code": "ZAF", "wb_url_code": "ZA", "undp_code": "ZAF"},
    "albanie": {"name": "Albanie", "freedom_house_slug": "albania", "world_bank_code": "ALB", "wb_url_code": "AL", "undp_code": "ALB"},
    "algerie": {"name": "Algérie", "freedom_house_slug": "algeria", "world_bank_code": "DZA", "wb_url_code": "DZ", "undp_code": "DZA"},
    "angola": {"name": "Angola", "freedom_house_slug": "angola", "world_bank_code": "AGO", "wb_url_code": "AO", "undp_code": "AGO"},
    "antigua_et_barbuda": {"name": "Antigua et Barbuda", "freedom_house_slug": "antigua-and-barbuda", "world_bank_code": "ATG", "wb_url_code": "AG", "undp_code": "ATG"},
    "argentine": {"name": "Argentine", "freedom_house_slug": "argentina", "world_bank_code": "ARG", "wb_url_code": "AR", "undp_code": "ARG"},
    "armenie": {"name": "Arménie", "freedom_house_slug": "armenia", "world_bank_code": "ARM", "wb_url_code": "AM", "undp_code": "ARM"},
    "azerbaijan": {"name": "Azerbaïdjan", "freedom_house_slug": "azerbaijan", "world_bank_code": "AZE", "wb_url_code": "AZ", "undp_code": "AZE"},
    "bangladesh": {"name": "Bangladesh", "freedom_house_slug": "bangladesh", "world_bank_code": "BGD", "wb_url_code": "BD", "undp_code": "BGD"},
    "belize": {"name": "Belize", "freedom_house_slug": "belize", "world_bank_code": "BLZ", "wb_url_code": "BZ", "undp_code": "BLZ"},
    "benin": {"name": "Bénin", "freedom_house_slug": "benin", "world_bank_code": "BEN", "wb_url_code": "BJ", "undp_code": "BEN"},
    "bhoutan": {"name": "Bhoutan", "freedom_house_slug": "bhutan", "world_bank_code": "BTN", "wb_url_code": "BT", "undp_code": "BTN"},
    "bielorussie": {"name": "Biélorussie", "freedom_house_slug": "belarus", "world_bank_code": "BLR", "wb_url_code": "BY", "undp_code": "BLR"},
    "birmanie": {"name": "Birmanie (Myanmar)", "freedom_house_slug": "myanmar", "world_bank_code": "MMR", "wb_url_code": "MM", "undp_code": "MMR"},
    "bolivie": {"name": "Bolivie", "freedom_house_slug": "bolivia", "world_bank_code": "BOL", "wb_url_code": "BO", "undp_code": "BOL"},
    "bosnie_herzegovine": {"name": "Bosnie-Herzégovine", "freedom_house_slug": "bosnia-and-herzegovina", "world_bank_code": "BIH", "wb_url_code": "BA", "undp_code": "BIH"},
    "botswana": {"name": "Botswana", "freedom_house_slug": "botswana", "world_bank_code": "BWA", "wb_url_code": "BW", "undp_code": "BWA"},
    "bresil": {"name": "Brésil", "freedom_house_slug": "brazil", "world_bank_code": "BRA", "wb_url_code": "BR", "undp_code": "BRA"},
    "burkina_faso": {"name": "Burkina Faso", "freedom_house_slug": "burkina-faso", "world_bank_code": "BFA", "wb_url_code": "BF", "undp_code": "BFA"},
    "burundi": {"name": "Burundi", "freedom_house_slug": "burundi", "world_bank_code": "BDI", "wb_url_code": "BI", "undp_code": "BDI"},
    "cambodge": {"name": "Cambodge", "freedom_house_slug": "cambodia", "world_bank_code": "KHM", "wb_url_code": "KH", "undp_code": "KHM"},
    "cameroun": {"name": "Cameroun", "freedom_house_slug": "cameroon", "world_bank_code": "CMR", "wb_url_code": "CM", "undp_code": "CMR"},
    "cap_vert": {"name": "Cap-Vert", "freedom_house_slug": "cape-verde", "world_bank_code": "CPV", "wb_url_code": "CV", "undp_code": "CPV"},
    "chili": {"name": "Chili", "freedom_house_slug": "chile", "world_bank_code": "CHL", "wb_url_code": "CL", "undp_code": "CHL"},
    "chine": {"name": "Chine", "freedom_house_slug": "china", "world_bank_code": "CHN", "wb_url_code": "CN", "undp_code": "CHN"},
    "colombie": {"name": "Colombie", "freedom_house_slug": "colombia", "world_bank_code": "COL", "wb_url_code": "CO", "undp_code": "COL"},
    "comores": {"name": "Comores", "freedom_house_slug": "comoros", "world_bank_code": "COM", "wb_url_code": "KM", "undp_code": "COM"},
    "congo": {"name": "Congo (Brazzaville)", "freedom_house_slug": "republic-of-congo", "world_bank_code": "COG", "wb_url_code": "CG", "undp_code": "COG"},
    "costa_rica": {"name": "Costa Rica", "freedom_house_slug": "costa-rica", "world_bank_code": "CRI", "wb_url_code": "CR", "undp_code": "CRI"},
    "cote_ivoire": {"name": "Côte d'Ivoire", "freedom_house_slug": "cote-divoire", "world_bank_code": "CIV", "wb_url_code": "CI", "undp_code": "CIV"},
    "cuba": {"name": "Cuba", "freedom_house_slug": "cuba", "world_bank_code": "CUB", "wb_url_code": "CU", "undp_code": "CUB"},
    "djibouti": {"name": "Djibouti", "freedom_house_slug": "djibouti", "world_bank_code": "DJI", "wb_url_code": "DJ", "undp_code": "DJI"},
    "dominique": {"name": "Dominique", "freedom_house_slug": "dominica", "world_bank_code": "DMA", "wb_url_code": "DM", "undp_code": "DMA"},
    "egypte": {"name": "Égypte", "freedom_house_slug": "egypt", "world_bank_code": "EGY", "wb_url_code": "EG", "undp_code": "EGY"},
    "equateur": {"name": "Équateur", "freedom_house_slug": "ecuador", "world_bank_code": "ECU", "wb_url_code": "EC", "undp_code": "ECU"},
    "erythree": {"name": "Érythrée", "freedom_house_slug": "eritrea", "world_bank_code": "ERI", "wb_url_code": "ER", "undp_code": "ERI"},
    "eswatini": {"name": "Eswatini", "freedom_house_slug": "eswatini", "world_bank_code": "SWZ", "wb_url_code": "SZ", "undp_code": "SWZ"},
    "ethiopie": {"name": "Éthiopie", "freedom_house_slug": "ethiopia", "world_bank_code": "ETH", "wb_url_code": "ET", "undp_code": "ETH"},
    "fidji": {"name": "Fidji", "freedom_house_slug": "fiji", "world_bank_code": "FJI", "wb_url_code": "FJ", "undp_code": "FJI"},
    "gabon": {"name": "Gabon", "freedom_house_slug": "gabon", "world_bank_code": "GAB", "wb_url_code": "GA", "undp_code": "GAB"},
    "gambie": {"name": "Gambie", "freedom_house_slug": "gambia", "world_bank_code": "GMB", "wb_url_code": "GM", "undp_code": "GMB"},
    "georgie": {"name": "Géorgie", "freedom_house_slug": "georgia", "world_bank_code": "GEO", "wb_url_code": "GE", "undp_code": "GEO"},
    "ghana": {"name": "Ghana", "freedom_house_slug": "ghana", "world_bank_code": "GHA", "wb_url_code": "GH", "undp_code": "GHA"},
    "grenade": {"name": "Grenade", "freedom_house_slug": "grenada", "world_bank_code": "GRD", "wb_url_code": "GD", "undp_code": "GRD"},
    "guatemala": {"name": "Guatemala", "freedom_house_slug": "guatemala", "world_bank_code": "GTM", "wb_url_code": "GT", "undp_code": "GTM"},
    "guinee": {"name": "Guinée", "freedom_house_slug": "guinea", "world_bank_code": "GIN", "wb_url_code": "GN", "undp_code": "GIN"},
    "guinee_bissau": {"name": "Guinée-Bissau", "freedom_house_slug": "guinea-bissau", "world_bank_code": "GNB", "wb_url_code": "GW", "undp_code": "GNB"},
    "guinee_equatoriale": {"name": "Guinée équatoriale", "freedom_house_slug": "equatorial-guinea", "world_bank_code": "GNQ", "wb_url_code": "GQ", "undp_code": "GNQ"},
    "guyana": {"name": "Guyana", "freedom_house_slug": "guyana", "world_bank_code": "GUY", "wb_url_code": "GY", "undp_code": "GUY"},
    "haiti": {"name": "Haïti", "freedom_house_slug": "haiti", "world_bank_code": "HTI", "wb_url_code": "HT", "undp_code": "HTI"},
    "honduras": {"name": "Honduras", "freedom_house_slug": "honduras", "world_bank_code": "HND", "wb_url_code": "HN", "undp_code": "HND"},
    "iles_salomon": {"name": "Îles Salomon", "freedom_house_slug": "solomon-islands", "world_bank_code": "SLB", "wb_url_code": "SB", "undp_code": "SLB"},
    "inde": {"name": "Inde", "freedom_house_slug": "india", "world_bank_code": "IND", "wb_url_code": "IN", "undp_code": "IND"},
    "indonesie": {"name": "Indonésie", "freedom_house_slug": "indonesia", "world_bank_code": "IDN", "wb_url_code": "ID", "undp_code": "IDN"},
    "irak": {"name": "Irak", "freedom_house_slug": "iraq", "world_bank_code": "IRQ", "wb_url_code": "IQ", "undp_code": "IRQ"},
    "jamaique": {"name": "Jamaïque", "freedom_house_slug": "jamaica", "world_bank_code": "JAM", "wb_url_code": "JM", "undp_code": "JAM"},
    "jordanie": {"name": "Jordanie", "freedom_house_slug": "jordan", "world_bank_code": "JOR", "wb_url_code": "JO", "undp_code": "JOR"},
    "kazakhstan": {"name": "Kazakhstan", "freedom_house_slug": "kazakhstan", "world_bank_code": "KAZ", "wb_url_code": "KZ", "undp_code": "KAZ"},
    "kenya": {"name": "Kenya", "freedom_house_slug": "kenya", "world_bank_code": "KEN", "wb_url_code": "KE", "undp_code": "KEN"},
    "kirghizistan": {"name": "Kirghizistan", "freedom_house_slug": "kyrgyzstan", "world_bank_code": "KGZ", "wb_url_code": "KG", "undp_code": "KGZ"},
    "kosovo": {"name": "Kosovo", "freedom_house_slug": "kosovo", "world_bank_code": "XKX", "wb_url_code": "XK", "undp_code": "XKX"},
    "laos": {"name": "Laos", "freedom_house_slug": "laos", "world_bank_code": "LAO", "wb_url_code": "LA", "undp_code": "LAO"},
    "lesotho": {"name": "Lesotho", "freedom_house_slug": "lesotho", "world_bank_code": "LSO", "wb_url_code": "LS", "undp_code": "LSO"},
    "liban": {"name": "Liban", "freedom_house_slug": "lebanon", "world_bank_code": "LBN", "wb_url_code": "LB", "undp_code": "LBN"},
    "liberia": {"name": "Libéria", "freedom_house_slug": "liberia", "world_bank_code": "LBR", "wb_url_code": "LR", "undp_code": "LBR"},
    "libye": {"name": "Libye", "freedom_house_slug": "libya", "world_bank_code": "LBY", "wb_url_code": "LY", "undp_code": "LBY"},
    "macedoine_du_nord": {"name": "Macédoine du Nord", "freedom_house_slug": "north-macedonia", "world_bank_code": "MKD", "wb_url_code": "MK", "undp_code": "MKD"},
    "madagascar": {"name": "Madagascar", "freedom_house_slug": "madagascar", "world_bank_code": "MDG", "wb_url_code": "MG", "undp_code": "MDG"},
    "malawi": {"name": "Malawi", "freedom_house_slug": "malawi", "world_bank_code": "MWI", "wb_url_code": "MW", "undp_code": "MWI"},
    "maldives": {"name": "Maldives", "freedom_house_slug": "maldives", "world_bank_code": "MDV", "wb_url_code": "MV", "undp_code": "MDV"},
    "mali": {"name": "Mali", "freedom_house_slug": "mali", "world_bank_code": "MLI", "wb_url_code": "ML", "undp_code": "MLI"},
    "maroc": {"name": "Maroc", "freedom_house_slug": "morocco", "world_bank_code": "MAR", "wb_url_code": "MA", "undp_code": "MAR"},
    "maurice": {"name": "Maurice", "freedom_house_slug": "mauritius", "world_bank_code": "MUS", "wb_url_code": "MU", "undp_code": "MUS"},
    "mauritanie": {"name": "Mauritanie", "freedom_house_slug": "mauritania", "world_bank_code": "MRT", "wb_url_code": "MR", "undp_code": "MRT"},
    "mexique": {"name": "Mexique", "freedom_house_slug": "mexico", "world_bank_code": "MEX", "wb_url_code": "MX", "undp_code": "MEX"},
    "moldavie": {"name": "Moldavie", "freedom_house_slug": "moldova", "world_bank_code": "MDA", "wb_url_code": "MD", "undp_code": "MDA"},
    "mongolie": {"name": "Mongolie", "freedom_house_slug": "mongolia", "world_bank_code": "MNG", "wb_url_code": "MN", "undp_code": "MNG"},
    "montenegro": {"name": "Monténégro", "freedom_house_slug": "montenegro", "world_bank_code": "MNE", "wb_url_code": "ME", "undp_code": "MNE"},
    "mozambique": {"name": "Mozambique", "freedom_house_slug": "mozambique", "world_bank_code": "MOZ", "wb_url_code": "MZ", "undp_code": "MOZ"},
    "namibie": {"name": "Namibie", "freedom_house_slug": "namibia", "world_bank_code": "NAM", "wb_url_code": "NA", "undp_code": "NAM"},
    "nepal": {"name": "Népal", "freedom_house_slug": "nepal", "world_bank_code": "NPL", "wb_url_code": "NP", "undp_code": "NPL"},
    "nicaragua": {"name": "Nicaragua", "freedom_house_slug": "nicaragua", "world_bank_code": "NIC", "wb_url_code": "NI", "undp_code": "NIC"},
    "niger": {"name": "Niger", "freedom_house_slug": "niger", "world_bank_code": "NER", "wb_url_code": "NE", "undp_code": "NER"},
    "nigeria": {"name": "Nigéria", "freedom_house_slug": "nigeria", "world_bank_code": "NGA", "wb_url_code": "NG", "undp_code": "NGA"},
    "ouganda": {"name": "Ouganda", "freedom_house_slug": "uganda", "world_bank_code": "UGA", "wb_url_code": "UG", "undp_code": "UGA"},
    "ouzbekistan": {"name": "Ouzbékistan", "freedom_house_slug": "uzbekistan", "world_bank_code": "UZB", "wb_url_code": "UZ", "undp_code": "UZB"},
    "pakistan": {"name": "Pakistan", "freedom_house_slug": "pakistan", "world_bank_code": "PAK", "wb_url_code": "PK", "undp_code": "PAK"},
    "panama": {"name": "Panama", "freedom_house_slug": "panama", "world_bank_code": "PAN", "wb_url_code": "PA", "undp_code": "PAN"},
    "paraguay": {"name": "Paraguay", "freedom_house_slug": "paraguay", "world_bank_code": "PRY", "wb_url_code": "PY", "undp_code": "PRY"},
    "perou": {"name": "Pérou", "freedom_house_slug": "peru", "world_bank_code": "PER", "wb_url_code": "PE", "undp_code": "PER"},
    "philippines": {"name": "Philippines", "freedom_house_slug": "philippines", "world_bank_code": "PHL", "wb_url_code": "PH", "undp_code": "PHL"},
    "rdc": {"name": "RDC (Congo-Kinshasa)", "freedom_house_slug": "democratic-republic-of-congo", "world_bank_code": "COD", "wb_url_code": "CD", "undp_code": "COD"},
    "republique_dominicaine": {"name": "République dominicaine", "freedom_house_slug": "dominican-republic", "world_bank_code": "DOM", "wb_url_code": "DO", "undp_code": "DOM"},
    "rwanda": {"name": "Rwanda", "freedom_house_slug": "rwanda", "world_bank_code": "RWA", "wb_url_code": "RW", "undp_code": "RWA"},
    "sainte_lucie": {"name": "Sainte-Lucie", "freedom_house_slug": "saint-lucia", "world_bank_code": "LCA", "wb_url_code": "LC", "undp_code": "LCA"},
    "saint_vincent": {"name": "Saint-Vincent-et-les-Grenadines", "freedom_house_slug": "saint-vincent-and-the-grenadines", "world_bank_code": "VCT", "wb_url_code": "VC", "undp_code": "VCT"},
    "salvador": {"name": "Salvador", "freedom_house_slug": "el-salvador", "world_bank_code": "SLV", "wb_url_code": "SV", "undp_code": "SLV"},
    "samoa": {"name": "Samoa", "freedom_house_slug": "samoa", "world_bank_code": "WSM", "wb_url_code": "WS", "undp_code": "WSM"},
    "sao_tome": {"name": "Sao Tomé-et-Principe", "freedom_house_slug": "sao-tome-and-principe", "world_bank_code": "STP", "wb_url_code": "ST", "undp_code": "STP"},
    "senegal": {"name": "Sénégal", "freedom_house_slug": "senegal", "world_bank_code": "SEN", "wb_url_code": "SN", "undp_code": "SEN"},
    "serbie": {"name": "Serbie", "freedom_house_slug": "serbia", "world_bank_code": "SRB", "wb_url_code": "RS", "undp_code": "SRB"},
    "seychelles": {"name": "Seychelles", "freedom_house_slug": "seychelles", "world_bank_code": "SYC", "wb_url_code": "SC", "undp_code": "SYC"},
    "sierra_leone": {"name": "Sierra Leone", "freedom_house_slug": "sierra-leone", "world_bank_code": "SLE", "wb_url_code": "SL", "undp_code": "SLE"},
    "somalie": {"name": "Somalie", "freedom_house_slug": "somalia", "world_bank_code": "SOM", "wb_url_code": "SO", "undp_code": "SOM"},
    "soudan": {"name": "Soudan", "freedom_house_slug": "sudan", "world_bank_code": "SDN", "wb_url_code": "SD", "undp_code": "SDN"},
    "sri_lanka": {"name": "Sri Lanka", "freedom_house_slug": "sri-lanka", "world_bank_code": "LKA", "wb_url_code": "LK", "undp_code": "LKA"},
    "suriname": {"name": "Suriname", "freedom_house_slug": "suriname", "world_bank_code": "SUR", "wb_url_code": "SR", "undp_code": "SUR"},
    "syrie": {"name": "Syrie", "freedom_house_slug": "syria", "world_bank_code": "SYR", "wb_url_code": "SY", "undp_code": "SYR"},
    "tadjikistan": {"name": "Tadjikistan", "freedom_house_slug": "tajikistan", "world_bank_code": "TJK", "wb_url_code": "TJ", "undp_code": "TJK"},
    "tanzanie": {"name": "Tanzanie", "freedom_house_slug": "tanzania", "world_bank_code": "TZA", "wb_url_code": "TZ", "undp_code": "TZA"},
    "tchad": {"name": "Tchad", "freedom_house_slug": "chad", "world_bank_code": "TCD", "wb_url_code": "TD", "undp_code": "TCD"},
    "thailande": {"name": "Thaïlande", "freedom_house_slug": "thailand", "world_bank_code": "THA", "wb_url_code": "TH", "undp_code": "THA"},
    "timor_leste": {"name": "Timor-Leste", "freedom_house_slug": "timor-leste", "world_bank_code": "TLS", "wb_url_code": "TL", "undp_code": "TLS"},
    "togo": {"name": "Togo", "freedom_house_slug": "togo", "world_bank_code": "TGO", "wb_url_code": "TG", "undp_code": "TGO"},
    "tunisie": {"name": "Tunisie", "freedom_house_slug": "tunisia", "world_bank_code": "TUN", "wb_url_code": "TN", "undp_code": "TUN"},
    "turquie": {"name": "Turquie", "freedom_house_slug": "turkey", "world_bank_code": "TUR", "wb_url_code": "TR", "undp_code": "TUR"},
    "ukraine": {"name": "Ukraine", "freedom_house_slug": "ukraine", "world_bank_code": "UKR", "wb_url_code": "UA", "undp_code": "UKR"},
    "uruguay": {"name": "Uruguay", "freedom_house_slug": "uruguay", "world_bank_code": "URY", "wb_url_code": "UY", "undp_code": "URY"},
    "vanuatu": {"name": "Vanuatu", "freedom_house_slug": "vanuatu", "world_bank_code": "VUT", "wb_url_code": "VU", "undp_code": "VUT"},
    "vietnam": {"name": "Vietnam", "freedom_house_slug": "vietnam", "world_bank_code": "VNM", "wb_url_code": "VN", "undp_code": "VNM"},
    "yemen": {"name": "Yémen", "freedom_house_slug": "yemen", "world_bank_code": "YEM", "wb_url_code": "YE", "undp_code": "YEM"},
    "zambie": {"name": "Zambie", "freedom_house_slug": "zambia", "world_bank_code": "ZMB", "wb_url_code": "ZM", "undp_code": "ZMB"},
    "zimbabwe": {"name": "Zimbabwe", "freedom_house_slug": "zimbabwe", "world_bank_code": "ZWE", "wb_url_code": "ZW", "undp_code": "ZWE"},
}

INCOME_LABELS = {
    "LIC": "PFR — Pays à faible revenu",
    "LMC": "PRITI — Rev. intermédiaire tranche inf.",
    "UMC": "PRITS — Rev. intermédiaire tranche sup.",
    "HIC": "PRE — Pays à revenu élevé",
    "INX": "Non classifié",
}

# ─────────────────────────────────────────────
# Fonctions de collecte
# ─────────────────────────────────────────────

def fetch_freedom_house(country_slug, year=2026):
    url = f"https://freedomhouse.org/country/{country_slug}/freedom-world/{year}"
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        r = requests.get(url, timeout=30, headers=headers)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        text = re.sub(r"\s+", " ", soup.get_text(" ", strip=True))
        result = {"status": None, "score": None, "pr_score": None,
                  "cl_score": None, "year": year, "url": url, "error": None}
        if re.search(r"\bNot Free\b", text): result["status"] = "Not Free"
        elif re.search(r"\bPartly Free\b", text): result["status"] = "Partly Free"
        elif re.search(r"\bFree\b", text): result["status"] = "Free"
        m = re.search(r"(?:Total Score and Status|score)\s+(\d{1,3})\s*/?\s*100", text, re.IGNORECASE)
        if m: result["score"] = int(m.group(1))
        else:
            m2 = re.search(r"\b(\d{1,3})\s*/?\s*100\b", text)
            if m2: result["score"] = int(m2.group(1))
        pr = re.search(r"Political Rights\s+(\d{1,2})\s*/?\s*40", text, re.IGNORECASE)
        if pr: result["pr_score"] = int(pr.group(1))
        cl = re.search(r"Civil Liberties\s+(\d{1,2})\s*/?\s*60", text, re.IGNORECASE)
        if cl: result["cl_score"] = int(cl.group(1))
        return result
    except Exception as e:
        return {"error": str(e), "url": url}


def fetch_wb_latest(country_code, indicator_code):
    url = f"https://api.worldbank.org/v2/country/{country_code}/indicator/{indicator_code}?format=json&per_page=20&mrv=10"
    try:
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        data = r.json()
        if not isinstance(data, list) or len(data) < 2 or not data[1]:
            return None, None
        for row in data[1]:
            if row.get("value") is not None:
                return row["value"], int(row["date"])
        return None, None
    except Exception:
        return None, None


def fetch_wb_country_info(country_code):
    url = f"https://api.worldbank.org/v2/country/{country_code}?format=json"
    try:
        r = requests.get(url, timeout=20)
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


@st.cache_data(ttl=86400)
def load_undp_hdi_table():
    """
    Télécharge le fichier Excel officiel du Human Development Report 2025
    et extrait mécaniquement les lignes pays : rang, pays, valeur IDH.
    La fonction ne dépend pas des noms de colonnes, souvent instables dans les annexes Excel.
    """
    url = "https://hdr.undp.org/sites/default/files/2025_HDR/HDR25_Statistical_Annex_HDI_Table.xlsx"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/octet-stream,*/*",
        "Referer": "https://hdr.undp.org/data-center/documentation-and-downloads",
    }

    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()

    excel_file = BytesIO(r.content)
    df_raw = pd.read_excel(excel_file, header=None, engine="openpyxl")

    rows = []
    for _, row in df_raw.iterrows():
        values = list(row.dropna())

        if len(values) < 3:
            continue

        rank = values[0]
        country = values[1]
        hdi = values[2]

        try:
            rank_int = int(rank)
            hdi_float = float(hdi)

            if 0 < hdi_float <= 1:
                rows.append({
                    "rank": rank_int,
                    "country": str(country).strip(),
                    "hdi": hdi_float
                })
        except Exception:
            continue

    return pd.DataFrame(rows)


def fetch_undp_hdi(iso3=None, country_name=None):
    """
    Récupère la valeur d'IDH et le rang mondial depuis l'annexe Excel officielle du HDR 2025.
    Retourne un dictionnaire stable pour éviter les erreurs de déballage.
    """
    source_url = "https://hdr.undp.org/sites/default/files/2025_HDR/HDR25_Statistical_Annex_HDI_Table.xlsx"

    aliases = {
        "Timor-Leste": ["Timor-Leste"],
        "RDC (Congo-Kinshasa)": ["Congo (Democratic Republic of the)", "Democratic Republic of the Congo"],
        "Congo (Brazzaville)": ["Congo"],
        "Côte d'Ivoire": ["Côte d'Ivoire", "Cote d'Ivoire"],
        "Birmanie (Myanmar)": ["Myanmar"],
        "Sao Tomé-et-Principe": ["Sao Tome and Principe", "São Tomé and Príncipe"],
        "Eswatini": ["Eswatini (Kingdom of)", "Eswatini"],
        "Tanzanie": ["Tanzania (United Republic of)", "United Republic of Tanzania"],
        "Bolivie": ["Bolivia (Plurinational State of)", "Bolivia"],
        "Venezuela": ["Venezuela (Bolivarian Republic of)", "Venezuela"],
        "Laos": ["Lao People's Democratic Republic"],
        "Iran": ["Iran (Islamic Republic of)"],
        "Syrie": ["Syrian Arab Republic"],
        "Vietnam": ["Viet Nam"],
    }

    try:
        df = load_undp_hdi_table()

        if df.empty:
            return {
                "value": None,
                "rank": None,
                "year": 2023,
                "source_url": source_url,
                "error": "Table IDH vide ou structure Excel non reconnue."
            }

        row = pd.DataFrame()

        possible_names = []
        if country_name:
            possible_names.append(country_name)
            possible_names.extend(aliases.get(country_name, []))

        possible_names_norm = [x.lower().strip() for x in possible_names]

        if possible_names_norm:
            row = df[df["country"].str.lower().str.strip().isin(possible_names_norm)]

        if row.empty:
            return {
                "value": None,
                "rank": None,
                "year": 2023,
                "source_url": source_url,
                "error": f"Pays introuvable dans la table IDH : {country_name}"
            }

        first = row.iloc[0]
        return {
            "value": float(first["hdi"]),
            "rank": int(first["rank"]),
            "year": 2023,
            "source_url": source_url,
            "error": None
        }

    except Exception as e:
        return {
            "value": None,
            "rank": None,
            "year": 2023,
            "source_url": source_url,
            "error": str(e)
        }


def flag_old(year):
    if year is None:
        return ""
    try:
        age = CURRENT_YEAR - int(year)
        if age > OLD_DATA_THRESHOLD:
            return f"⚠️ donnée ancienne ({age} ans)"
    except Exception:
        pass
    return ""


def ind(label, value, unit, year, source, url=None, note=None):
    age_flag = flag_old(year) if note is None else note
    return {
        "Indicateur": label,
        "Valeur": value if value is not None else "N/D",
        "Unité": unit or "",
        "Année": str(year) if year else "—",
        "Source": source,
        "URL source": url or "",
        "Note": age_flag,
    }



def make_unique_columns(df):
    """
    Streamlit / PyArrow refuse les DataFrames avec noms de colonnes dupliqués.
    Les tableaux PDF FMI ont souvent des colonnes vides ou répétées : on les renomme proprement.
    """
    df = df.copy()
    seen = {}
    new_cols = []

    for col in df.columns:
        col = str(col).strip() if col is not None else "colonne"
        if col == "" or col.lower() == "none":
            col = "colonne"

        if col in seen:
            seen[col] += 1
            new_cols.append(f"{col}_{seen[col]}")
        else:
            seen[col] = 0
            new_cols.append(col)

    df.columns = new_cols
    return df


# ─────────────────────────────────────────────
# Article IV FMI — extraction depuis PDF uploadé
# ─────────────────────────────────────────────

ARTICLE_IV_THEMES = {
    "Croissance et activité": [
        "growth", "real gdp", "gdp growth", "output", "economic activity",
        "domestic demand", "consumption", "investment", "recovery", "potential growth"
    ],
    "Inflation et politique monétaire": [
        "inflation", "consumer prices", "monetary policy", "policy rate",
        "central bank", "exchange rate", "real interest", "liquidity"
    ],
    "Finances publiques": [
        "fiscal", "budget", "overall balance", "primary balance", "revenue",
        "tax", "expenditure", "wage bill", "subsidies", "public investment"
    ],
    "Dette publique et soutenabilité": [
        "public debt", "debt sustainability", "debt-to-gdp", "debt service",
        "interest payments", "arrears", "dsf", "dsa", "sovereign"
    ],
    "Comptes externes": [
        "current account", "trade balance", "exports", "imports", "remittances",
        "foreign direct investment", "fdi", "external financing", "balance of payments"
    ],
    "Liquidité externe et réserves": [
        "international reserves", "foreign reserves", "reserve coverage",
        "months of imports", "external debt", "short-term debt", "gross reserves"
    ],
    "Système financier et banques": [
        "financial sector", "banking sector", "capital adequacy", "npl",
        "nonperforming loans", "loan-to-deposit", "profitability", "roe", "roa",
        "credit growth", "private sector credit", "liquidity ratio"
    ],
    "Risques et recommandations FMI": [
        "risks", "downside risks", "policy recommendations", "staff recommends",
        "authorities should", "structural reforms", "outlook", "vulnerabilities"
    ],
    "Climat et vulnérabilités structurelles": [
        "climate", "natural disaster", "resilience", "adaptation", "mitigation",
        "food security", "energy", "commodity prices", "fragility"
    ],
}


def _safe_import_pdfplumber():
    try:
        import pdfplumber
        return pdfplumber, None
    except Exception as e:
        return None, str(e)


def extract_article_iv_pages(uploaded_pdf):
    """
    Extrait le texte page par page d'un PDF Article IV.
    Fonctionne surtout pour les PDFs FMI numériques. Les PDFs scannés nécessitent de l'OCR.
    """
    pdfplumber, error = _safe_import_pdfplumber()
    if error:
        return [], f"pdfplumber indisponible : {error}. Ajoutez pdfplumber dans requirements.txt."

    try:
        uploaded_pdf.seek(0)
        pages = []
        with pdfplumber.open(uploaded_pdf) as pdf:
            for page_number, page in enumerate(pdf.pages, start=1):
                text = page.extract_text(x_tolerance=1, y_tolerance=3) or ""
                if text.strip():
                    pages.append({"page": page_number, "text": text})
        return pages, None
    except Exception as e:
        return [], f"Erreur extraction texte PDF : {e}"


def extract_article_iv_tables(uploaded_pdf, max_tables=30):
    """
    Extrait les tableaux détectés dans le PDF. Les tableaux FMI complexes peuvent nécessiter
    une vérification manuelle : cette extraction sert surtout à repérer les tableaux utiles.
    """
    pdfplumber, error = _safe_import_pdfplumber()
    if error:
        return [], f"pdfplumber indisponible : {error}. Ajoutez pdfplumber dans requirements.txt."

    try:
        uploaded_pdf.seek(0)
        tables_out = []
        with pdfplumber.open(uploaded_pdf) as pdf:
            for page_number, page in enumerate(pdf.pages, start=1):
                tables = page.extract_tables() or []
                for table_id, table in enumerate(tables, start=1):
                    if not table or len(table) < 2:
                        continue

                    # Nettoyage minimal
                    cleaned = []
                    for row in table:
                        cleaned.append([
                            re.sub(r"\s+", " ", str(cell)).strip() if cell is not None else ""
                            for cell in row
                        ])

                    header = cleaned[0]
                    body = cleaned[1:]

                    # Évite les tableaux illisibles vides
                    non_empty_cells = sum(1 for row in cleaned for cell in row if cell)
                    if non_empty_cells < 6:
                        continue

                    try:
                        df = pd.DataFrame(body, columns=header)
                    except Exception:
                        df = pd.DataFrame(cleaned)

                    df = make_unique_columns(df)

                    tables_out.append({
                        "page": page_number,
                        "table_id": table_id,
                        "data": df
                    })

                    if len(tables_out) >= max_tables:
                        return tables_out, None

        return tables_out, None
    except Exception as e:
        return [], f"Erreur extraction tableaux PDF : {e}"


def _extract_relevant_excerpt(text, keyword, window=900):
    text_norm = re.sub(r"\s+", " ", text)
    idx = text_norm.lower().find(keyword.lower())
    if idx == -1:
        return text_norm[:window]
    start = max(0, idx - window // 2)
    end = min(len(text_norm), idx + window // 2)
    return text_norm[start:end].strip()


def find_article_iv_theme_mentions(pages, max_hits_per_theme=4):
    """
    Repère les pages et extraits associés à chaque thème. On travaille par thèmes, pas par
    indicateur strict, parce que les Article IV n'ont pas un format parfaitement standardisé.
    """
    rows = []

    for theme, keywords in ARTICLE_IV_THEMES.items():
        hits = []
        for page in pages:
            text_lower = page["text"].lower()
            found_keyword = None
            for kw in keywords:
                if kw.lower() in text_lower:
                    found_keyword = kw
                    break

            if found_keyword:
                hits.append({
                    "Thème": theme,
                    "Page": page["page"],
                    "Mot-clé détecté": found_keyword,
                    "Extrait": _extract_relevant_excerpt(page["text"], found_keyword, window=1000)
                })

            if len(hits) >= max_hits_per_theme:
                break

        rows.extend(hits)

    return pd.DataFrame(rows)


def find_article_iv_numeric_sentences(pages, max_rows=80):
    """
    Repère des phrases utiles contenant des chiffres macro (% du PIB, points, USD, mois d'importations, etc.).
    Ce n'est pas une extraction définitive : c'est une aide au repérage.
    """
    macro_words = [
        "gdp", "growth", "inflation", "debt", "deficit", "balance", "current account",
        "revenue", "expenditure", "reserves", "imports", "exports", "credit", "npl",
        "capital adequacy", "fiscal", "primary", "public", "external"
    ]

    numeric_pattern = re.compile(
        r"(\d+(?:[.,]\d+)?\s?(?:percent|per cent|%|percentage points|pp|months|billion|million|usd|us\$))",
        re.IGNORECASE
    )

    rows = []
    for page in pages:
        text = re.sub(r"\s+", " ", page["text"])
        sentences = re.split(r"(?<=[.!?])\s+", text)

        for sent in sentences:
            sent_lower = sent.lower()
            if numeric_pattern.search(sent) and any(w in sent_lower for w in macro_words):
                rows.append({
                    "Page": page["page"],
                    "Phrase avec donnée chiffrée": sent.strip()[:700]
                })

            if len(rows) >= max_rows:
                return pd.DataFrame(rows)

    return pd.DataFrame(rows)


def score_article_iv_tables(tables):
    """
    Classe les tableaux extraits selon leur probabilité d'intérêt macro.
    """
    table_keywords = [
        "gdp", "growth", "inflation", "fiscal", "revenue", "expenditure",
        "debt", "current account", "exports", "imports", "reserves",
        "balance", "bank", "credit", "npl", "capital", "external"
    ]

    rows = []
    for item in tables:
        df = item["data"]
        text = " ".join(df.astype(str).fillna("").values.flatten().tolist()).lower()
        score = sum(1 for kw in table_keywords if kw in text)

        if score > 0:
            preview = " | ".join(df.head(3).astype(str).fillna("").values.flatten().tolist())
            rows.append({
                "Page": item["page"],
                "Table": item["table_id"],
                "Score pertinence": score,
                "Aperçu": preview[:500]
            })

    if not rows:
        return pd.DataFrame()

    return pd.DataFrame(rows).sort_values("Score pertinence", ascending=False)


def build_article_iv_prompt(country_name, mentions_df, numeric_df, table_scores_df):
    """
    Construit un prompt IA distinct du prompt de données quantitatives.
    Il demande une extraction prudente et vérifiable à partir du PDF.
    """
    lines = [
        f"ARTICLE IV FMI — {country_name}",
        "=" * 60,
        "",
        "Tu es un analyste risque pays. À partir des extraits d'un rapport Article IV du FMI,",
        "identifie les informations macroéconomiques saillantes et les points d'attention.",
        "",
        "RÈGLES :",
        "- Ne pas inventer de chiffres.",
        "- Si une donnée n'est pas explicitement présente dans les extraits, dire qu'elle n'est pas disponible.",
        "- Citer les pages mentionnées dans les extraits.",
        "- Distinguer données observées, prévisions FMI et recommandations FMI lorsque c'est possible.",
        "- Ne pas chercher une précision illusoire : les tableaux PDF peuvent être mal extraits.",
        "",
        "FORMAT ATTENDU :",
        "1. Croissance, inflation et régime de croissance",
        "2. Finances publiques et dette",
        "3. Comptes externes et réserves",
        "4. Système financier",
        "5. Risques principaux et recommandations du FMI",
        "",
        "=" * 60,
        "",
    ]

    if mentions_df is not None and not mentions_df.empty:
        lines.append("EXTRAITS PAR THÈME")
        for _, row in mentions_df.head(30).iterrows():
            lines.append(
                f"- {row['Thème']} | page {row['Page']} | mot-clé : {row['Mot-clé détecté']}\n"
                f"  Extrait : {row['Extrait']}"
            )
        lines.append("")

    if numeric_df is not None and not numeric_df.empty:
        lines.append("PHRASES AVEC DONNÉES CHIFFRÉES")
        for _, row in numeric_df.head(40).iterrows():
            lines.append(f"- Page {row['Page']} : {row['Phrase avec donnée chiffrée']}")
        lines.append("")

    if table_scores_df is not None and not table_scores_df.empty:
        lines.append("TABLEAUX POTENTIELLEMENT UTILES")
        for _, row in table_scores_df.head(15).iterrows():
            lines.append(
                f"- Page {row['Page']}, tableau {row['Table']} "
                f"(score {row['Score pertinence']}) : {row['Aperçu']}"
            )
        lines.append("")

    return "\n".join(lines)


# ─────────────────────────────────────────────
# Piliers consolidés — socio-politique et croissance
# ─────────────────────────────────────────────

def fetch_wb_history_values(country_code, indicator_code, n_years=25):
    """
    Récupère une série historique Banque mondiale et renvoie les observations non nulles,
    triées par année croissante. Sert aux moyennes de croissance et tendances longues.
    """
    url = f"https://api.worldbank.org/v2/country/{country_code}/indicator/{indicator_code}?format=json&per_page=200"
    try:
        r = requests.get(url, timeout=25, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        data = r.json()
        if not isinstance(data, list) or len(data) < 2 or not data[1]:
            return []
        rows = []
        for obs in data[1]:
            if obs.get("value") is not None:
                try:
                    rows.append({"year": int(obs["date"]), "value": float(obs["value"])})
                except Exception:
                    continue
        rows.sort(key=lambda x: x["year"])
        return rows[-n_years:]
    except Exception:
        return []


def latest_from_history(history):
    if not history:
        return None, None
    last = history[-1]
    return last.get("value"), last.get("year")


def average_since(history, start_year=2010):
    vals = [x["value"] for x in history if x.get("year") is not None and x["year"] >= start_year]
    if not vals:
        return None
    return sum(vals) / len(vals)


def average_last_n(history, n=10):
    vals = [x["value"] for x in history[-n:]]
    if not vals:
        return None
    return sum(vals) / len(vals)


def add_wb_indicator(rows, label, value, year, unit, wb_indicator_code, note=None):
    url = f"https://data.worldbank.org/indicator/{wb_indicator_code}" if wb_indicator_code else None
    v = "N/D" if value is None else (f"{value:,.1f}" if isinstance(value, (int, float)) else value)
    rows.append(ind(label, v, unit, year, "Banque mondiale", url, note))


def build_sociopo_section(section_header, section_governance, section_labour, section_poverty, section_education):
    """
    Rassemble les données sociopolitiques dans un seul bloc lisible.
    """
    rows = []
    rows.extend(section_header)
    rows.extend(section_governance)
    rows.extend(section_labour)
    rows.extend(section_poverty)
    rows.extend(section_education)
    return rows


def build_growth_section(wb_code):
    """
    Bloc 'Modèle économique et régime de croissance'.
    Les données quantitatives viennent prioritairement de la Banque mondiale.
    Les informations non standardisées sont signalées comme à chercher dans l'Article IV.
    """
    rows = []

    # Séries principales
    indicators = {
        "NY.GDP.MKTP.CD": ("PIB nominal total", "USD courants"),
        "NY.GDP.PCAP.CD": ("PIB par habitant", "USD courants"),
        "NY.GDP.MKTP.KD.ZG": ("Croissance du PIB réel — dernière observation", "%"),
        "FP.CPI.TOTL.ZG": ("Inflation annuelle", "%"),
        "NV.AGR.TOTL.ZS": ("Agriculture — part du PIB", "% du PIB"),
        "NV.IND.TOTL.ZS": ("Industrie — part du PIB", "% du PIB"),
        "NV.IND.MANF.ZS": ("Manufacturier — part du PIB", "% du PIB"),
        "NV.SRV.TOTL.ZS": ("Services — part du PIB", "% du PIB"),
        "SL.AGR.EMPL.ZS": ("Emploi agricole", "% de l'emploi total"),
        "SL.IND.EMPL.ZS": ("Emploi industriel", "% de l'emploi total"),
        "SL.SRV.EMPL.ZS": ("Emploi dans les services", "% de l'emploi total"),
        "NE.CON.PRVT.ZS": ("Consommation privée", "% du PIB"),
        "NE.CON.GOVT.ZS": ("Consommation publique", "% du PIB"),
        "NE.GDI.FTOT.ZS": ("Formation brute de capital fixe", "% du PIB"),
        "NE.GDI.FPRV.ZS": ("Investissement privé", "% du PIB"),
        "BX.KLT.DINV.WD.GD.ZS": ("IDE entrants nets", "% du PIB"),
        "BX.TRF.PWKR.DT.GD.ZS": ("Transferts de migrants", "% du PIB"),
        "FS.AST.PRVT.GD.ZS": ("Crédit domestique au secteur privé", "% du PIB"),
        "NE.EXP.GNFS.ZS": ("Exportations de biens et services", "% du PIB"),
        "NE.IMP.GNFS.ZS": ("Importations de biens et services", "% du PIB"),
        "BN.CAB.XOKA.GD.ZS": ("Solde courant", "% du PIB"),
    }

    histories = {}
    for code, (label, unit) in indicators.items():
        hist = fetch_wb_history_values(wb_code, code, n_years=25)
        histories[code] = hist
        val, year = latest_from_history(hist)
        add_wb_indicator(rows, label, val, year, unit, code)

    # Moyennes de croissance
    growth_hist = histories.get("NY.GDP.MKTP.KD.ZG", [])
    avg_2010 = average_since(growth_hist, 2010)
    avg_10y = average_last_n(growth_hist, 10)

    rows.append(ind(
        "Croissance moyenne du PIB réel depuis 2010",
        f"{avg_2010:.1f}" if avg_2010 is not None else "N/D",
        "%",
        f"{min([x['year'] for x in growth_hist if x['year'] >= 2010], default='—')}-{max([x['year'] for x in growth_hist], default='—')}" if avg_2010 is not None else None,
        "Calcul interne à partir de Banque mondiale",
        "https://data.worldbank.org/indicator/NY.GDP.MKTP.KD.ZG",
        None if avg_2010 is not None else "Série insuffisante pour calculer la moyenne"
    ))

    rows.append(ind(
        "Croissance moyenne du PIB réel — 10 dernières observations",
        f"{avg_10y:.1f}" if avg_10y is not None else "N/D",
        "%",
        f"{growth_hist[-10]['year']}-{growth_hist[-1]['year']}" if len(growth_hist) >= 10 else None,
        "Calcul interne à partir de Banque mondiale",
        "https://data.worldbank.org/indicator/NY.GDP.MKTP.KD.ZG",
        None if avg_10y is not None else "Série insuffisante pour calculer la moyenne"
    ))

    # Indicateurs non standardisés : guider l'IA vers Article IV / sources sectorielles
    qualitative_guides = [
        ("Part du secteur extractif dans le PIB", "À rechercher dans l'Article IV FMI, les comptes nationaux détaillés ou les autorités statistiques."),
        ("Part du secteur extractif dans les exportations", "À rechercher dans l'Article IV FMI, UN Comtrade/OEC ou les autorités douanières."),
        ("Part du secteur extractif dans les recettes publiques", "À rechercher dans l'Article IV FMI, DSA FMI, EITI ou budget national."),
        ("Part du tourisme dans le PIB", "À rechercher dans l'Article IV FMI, WTTC, UN Tourism ou autorités nationales."),
        ("Part de la construction, immobilier ou finance dans le PIB", "À rechercher dans les comptes nationaux détaillés ou l'Article IV."),
        ("Décomposition sectorielle fine de la croissance", "À rechercher dans l'Article IV FMI, rapport banque centrale ou comptes nationaux."),
        ("Contribution consommation/investissement/exportations à la croissance", "À rechercher dans l'Article IV FMI ou les tableaux de comptes nationaux."),
        ("Croissance potentielle FMI", "À rechercher dans l'Article IV FMI, généralement dans le texte ou les annexes."),
        ("Prévisions FMI année en cours et année suivante", "À rechercher dans l'Article IV FMI, WEO ou World Bank MPO."),
        ("Révisions des prévisions FMI/Banque mondiale", "À rechercher dans WEO/MPO et dans les communiqués récents."),
        ("Réserves, durée de vie des ressources, fonds souverain", "À rechercher dans l'Article IV FMI, rapports sectoriels ou fonds souverain national."),
        ("Réformes économiques récentes et chocs récents", "À rechercher dans l'Article IV FMI et les rapports Banque mondiale/MPO."),
    ]

    for label, note in qualitative_guides:
        rows.append(ind(label, "À rechercher", None, None, "Article IV FMI / source sectorielle", "", note))

    return rows


def build_model_growth_prompt(country_name, growth_rows, article_iv_prompt_text=None):
    """
    Prompt spécifique pour produire le paragraphe 'Modèle économique et régime de croissance'.
    """
    lines = [
        f"PAYS : {country_name}",
        "",
        "DONNÉES QUANTITATIVES DISPONIBLES — BLOC MODÈLE ÉCONOMIQUE ET RÉGIME DE CROISSANCE",
        "=" * 80,
    ]

    for r in growth_rows:
        label = r.get("Indicateur", "")
        val = r.get("Valeur", "N/D")
        unit = r.get("Unité", "")
        year = r.get("Année", "—")
        source = r.get("Source", "")
        note = r.get("Note", "")
        unit_str = f" {unit}" if unit else ""
        year_str = f" ({year})" if year and year != "—" else ""
        note_str = f" — Note : {note}" if note else ""
        lines.append(f"- {label} : {val}{unit_str}{year_str} — Source : {source}{note_str}")

    if article_iv_prompt_text:
        lines += [
            "",
            "=" * 80,
            "ÉLÉMENTS EXTRAITS DE L'ARTICLE IV FMI",
            "=" * 80,
            article_iv_prompt_text[:18000],
        ]

    lines += [
        "",
        "=" * 80,
        "CONSIGNE DE RÉDACTION",
        "=" * 80,
        "À partir des données fournies, rédige un paragraphe intitulé « Modèle économique et régime de croissance », en respectant strictement le style, la structure et le niveau d’analyse des exemples fournis.",
        "",
        "Le texte doit être divisé en deux sous-parties explicites : « Modèle économique : » puis « Régime de croissance : ». Il doit être rédigé en paragraphes denses, sans bullet points, dans un style analytique, synthétique et institutionnel. Le ton doit être celui d’une fiche pays professionnelle : précis, nuancé, factuel, mais interprétatif. Ne fais pas de généralités vagues. Chaque affirmation analytique doit être rattachée à un chiffre, une tendance ou un mécanisme économique.",
        "",
        "Partie 1 — Modèle économique : commence par caractériser la structure productive du pays. Indique si l’économie est diversifiée ou non, industrialisée ou non, agricole, extractive, manufacturière, tertiarisée, rentière, ouverte, dépendante des importations ou tirée par la demande interne. Présente ensuite les principaux secteurs dans l’ordre de leur importance économique ou stratégique. Pour chaque secteur important, indique si possible sa part dans le PIB, sa part dans l’emploi, sa contribution aux exportations ou son rôle dans l’investissement. Ne te contente pas de lister les secteurs : explique ce que cette structure révèle du modèle économique.",
        "",
        "Identifie les forces structurelles du pays si elles sont directement appuyées par les données ou par l’Article IV : ressources naturelles, base industrielle, position exportatrice, capital humain, marché intérieur, intégration régionale, avantage comparatif, fonds souverain, tourisme, diaspora, agriculture productive. Identifie aussi les fragilités structurelles : faible diversification, dépendance à une rente, faiblesse du secteur privé formel, faible productivité, informalité, enclavement, déficit d’infrastructures, insuffisance du capital humain, exposition climatique, environnement des affaires dégradé, dépendance aux importations, faible transformation locale, surcapacités, désindustrialisation, crise immobilière, capture de rente, dépendance à un partenaire commercial dominant.",
        "",
        "Si une transformation structurelle est en cours, décris-la clairement : industrialisation, tertiarisation, re-primarisation, montée en gamme, libéralisation, intervention accrue de l’État, diversification, intégration aux chaînes de valeur, transition verte, développement extractif. Précise si cette transformation paraît solide, incomplète, contrainte ou risquée. Termine cette partie par une appréciation synthétique du modèle : ce qu’il permet, ce qu’il bloque, et le principal risque structurel qui en découle.",
        "",
        "Partie 2 — Régime de croissance : commence par qualifier le rythme de croissance sur longue période : dynamique, faible, volatile, résilient, ralenti, artificiellement soutenu, cyclique, dépendant des matières premières. Donne si possible la croissance moyenne sur 10 ans ou depuis 2010. Explique ensuite les moteurs de la croissance : consommation privée, investissement public, investissement privé, exportations, dépenses publiques, crédit, rente extractive, tourisme, agriculture, immobilier, transferts de migrants, aide extérieure, IDE, grands projets d’infrastructures, politique industrielle.",
        "",
        "Distingue clairement la tendance longue des évolutions récentes. Mentionne les chocs récents pertinents lorsque les données ou l’Article IV les documentent : Covid, guerre, coup d’État, crise immobilière, choc climatique, choc énergétique, sanctions, tensions commerciales, changement de gouvernement, réformes, ajustement budgétaire, baisse de l’aide, adhésion à une organisation régionale. Analyse la soutenabilité de la croissance : croissance forte mais peu inclusive, tirée par les dépenses publiques, dépendante du crédit, portée par un effet de base, vulnérable aux prix mondiaux, sans gains de productivité, ou faible malgré des atouts structurels.",
        "",
        "Termine par les perspectives et risques à moyen terme : demande externe, prix des matières premières, épuisement d’une rente, immobilier, endettement, instabilité politique, climat, conflit, fragmentation commerciale, baisse de l’aide, faiblesse du secteur privé, démographie, tensions sociales, insécurité, dépendance énergétique.",
        "",
        "Contraintes : ne pas inventer de chiffres. Si une donnée manque, ne pas la remplacer par une supposition. Tu peux formuler une inférence prudente, mais elle doit être explicitement fondée sur les données disponibles. Si une information ne peut être trouvée que dans l’Article IV et qu’aucun PDF n’a été fourni, signale qu’elle doit être vérifiée dans l’Article IV plutôt que de l’inventer.",
    ]

    return "\n".join(lines)

# ─────────────────────────────────────────────
# Construction du prompt IA
# ─────────────────────────────────────────────

def build_ai_prompt(country_name, all_sections):
    lines = [f"FICHE PAYS : {country_name}", "=" * 52, ""]
    for section_name, rows in all_sections.items():
        if not rows:
            continue
        lines.append(f"── {section_name.upper()} ──")
        for r in rows:
            val = r.get("Valeur", "N/D")
            year = r.get("Année", "")
            note = r.get("Note", "")
            unit = r.get("Unité", "")
            src = r.get("Source", "")
            label = r.get("Indicateur", "")
            year_str = f" ({year})" if year and year != "—" else ""
            unit_str = f" {unit}" if unit else ""
            note_str = f"  [{note}]" if note else ""
            lines.append(f"• {label} : {val}{unit_str}{year_str} — {src}{note_str}")
        lines.append("")

    lines += [
        "=" * 52, "",
        "INSTRUCTIONS POUR L'IA :", "",
        "À partir de ces données collectées automatiquement depuis des sources officielles,",
        "réalise une analyse structurée en 3 blocs :", "",
        "1. SYNTHÈSE (150 mots max)",
        "   Rédige une synthèse de l'environnement politique et socioéconomique.",
        "   Identifie les points saillants et les tensions apparentes entre indicateurs.", "",
        "2. POINTS D'ATTENTION",
        "   - Signale les données anciennes (>5 ans) qui limitent l'interprétation",
        "   - Signale les valeurs extrêmes ou incohérences entre indicateurs",
        "   - Signale les données manquantes importantes", "",
        "3. PISTES DE RECHERCHE COMPLÉMENTAIRES",
        "   Propose 3 questions ou axes d'investigation prioritaires.", "",
        "RÈGLES :",
        "- Ne modifie jamais les données sources",
        "- Ne remplace jamais une donnée manquante par une supposition",
        "- Distingue clairement ce qui vient des sources et ce que tu infères",
    ]
    return "\n".join(lines)


# ─────────────────────────────────────────────
# Interface
# ─────────────────────────────────────────────

st.markdown('<div class="title-block">', unsafe_allow_html=True)
st.markdown("# 🌍 Outil de collecte de données — DER")
st.markdown('<p style="color:#888; font-size:13px; margin-top:-8px;">Collecte automatique · Sources officielles · Prompt IA généré</p>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

country_options = dict(sorted({info["name"]: key for key, info in COUNTRY_MAPPING.items()}.items()))
selected_name = st.selectbox("Sélectionner un pays", options=list(country_options.keys()))
selected_key = country_options[selected_name]
country_info = COUNTRY_MAPPING[selected_key]
wb_code = country_info["world_bank_code"]
wb_url_base = f"https://data.worldbank.org/country/{country_info['wb_url_code']}"
undp_url = f"https://hdr.undp.org/data-center/specific-country-data#/countries/{country_info['undp_code']}"

uploaded_article_iv = st.file_uploader(
    "Article IV FMI (optionnel) — déposer un PDF",
    type=["pdf"],
    help="Ajoutez ici un rapport Article IV du FMI. L'app extraira le texte, les passages macro et les tableaux détectables."
)

st.write("")

if st.button("Récupérer les données →"):

    with st.spinner("Collecte en cours — Freedom House, Banque Mondiale, PNUD..."):

        fh = fetch_freedom_house(country_info["freedom_house_slug"])
        wb_info = fetch_wb_country_info(wb_code)
        income_code = wb_info.get("income_code", "") if wb_info else ""
        income_label = INCOME_LABELS.get(income_code, wb_info.get("income_label", "N/D") if wb_info else "N/D")
        region = wb_info.get("region", "N/D") if wb_info else "N/D"

        gdp_val, gdp_year           = fetch_wb_latest(wb_code, "NY.GDP.PCAP.CD")
        gini_val, gini_year         = fetch_wb_latest(wb_code, "SI.POV.GINI")
        emp_tot_val, emp_tot_year   = fetch_wb_latest(wb_code, "SL.EMP.TOTL.SP.ZS")
        emp_youth_val, emp_youth_year = fetch_wb_latest(wb_code, "SL.UEM.1524.ZS")
        emp_fem_val, emp_fem_year   = fetch_wb_latest(wb_code, "SL.EMP.TOTL.SP.FE.ZS")
        informal_val, informal_year = fetch_wb_latest(wb_code, "SL.ISV.IFRM.ZS")
        poverty_val, poverty_year   = fetch_wb_latest(wb_code, "SI.POV.DDAY")
        prim_val, prim_year         = fetch_wb_latest(wb_code, "SE.PRM.ENRR")
        sec_val, sec_year           = fetch_wb_latest(wb_code, "SE.SEC.ENRR")
        tert_val, tert_year         = fetch_wb_latest(wb_code, "SE.TER.ENRR")

        wgi_voice_val, wgi_voice_year     = fetch_wb_latest(wb_code, "VA.EST")
        wgi_polstab_val, wgi_polstab_year = fetch_wb_latest(wb_code, "PV.EST")
        wgi_goveff_val, wgi_goveff_year   = fetch_wb_latest(wb_code, "GE.EST")
        wgi_regqual_val, wgi_regqual_year = fetch_wb_latest(wb_code, "RQ.EST")
        wgi_rulelaw_val, wgi_rulelaw_year = fetch_wb_latest(wb_code, "RL.EST")
        wgi_corrupt_val, wgi_corrupt_year = fetch_wb_latest(wb_code, "CC.EST")

        co2_val, co2_year             = fetch_wb_latest(wb_code, "EN.ATM.CO2E.PC")
        forests_val, forests_year     = fetch_wb_latest(wb_code, "AG.LND.FRST.ZS")
        renewable_val, renewable_year = fetch_wb_latest(wb_code, "EG.FEC.RNEW.ZS")

        hdi = fetch_undp_hdi(country_info["undp_code"], country_info["name"])

    # ── Section 1 : En-tête ──
    section_header = []
    if fh and not fh.get("error"):
        if fh.get("score") is not None:
            section_header.append(ind("Freedom House — Score", f"{fh['score']}/100", None, fh["year"], "Freedom House", fh["url"]))
        if fh.get("status"):
            section_header.append(ind("Freedom House — Statut", fh["status"], None, fh["year"], "Freedom House", fh["url"]))
        if fh.get("pr_score") is not None:
            section_header.append(ind("Droits politiques", f"{fh['pr_score']}/40", None, fh["year"], "Freedom House", fh["url"]))
        if fh.get("cl_score") is not None:
            section_header.append(ind("Libertés civiles", f"{fh['cl_score']}/60", None, fh["year"], "Freedom House", fh["url"]))
    else:
        section_header.append(ind("Freedom House", "Indisponible", None, None, "Freedom House", "https://freedomhouse.org", "Erreur de scraping"))

    section_header.append(ind("EIU — Democracy Index", "Non disponible", None, None, "EIU", "https://www.eiu.com", "Accès abonnement requis"))

    if hdi.get("value") is not None:
        section_header.append(ind("IDH — Valeur", f"{hdi['value']:.3f}", None, hdi["year"], "PNUD / Human Development Report", hdi["source_url"]))
        if hdi.get("rank") is not None:
            section_header.append(ind("IDH — Rang mondial", str(hdi["rank"]), None, hdi["year"], "PNUD / Human Development Report", hdi["source_url"]))
    else:
        section_header.append(ind("IDH", "N/D", None, None, "PNUD / Human Development Report", hdi.get("source_url", undp_url), hdi.get("error", "Donnée indisponible")))

    section_header.append(ind("Statut de revenu (BM)", income_label, None, None, "Banque Mondiale", wb_url_base, ""))
    section_header.append(ind("Région BM", region, None, None, "Banque Mondiale", wb_url_base, ""))
    if gdp_val:
        section_header.append(ind("PIB / habitant", f"${gdp_val:,.0f}", "USD", gdp_year, "Banque Mondiale", wb_url_base))
    if gini_val:
        section_header.append(ind("Indice de Gini", f"{gini_val:.1f}", None, gini_year, "Banque Mondiale", wb_url_base))

    # ── Section 2 : Gouvernance WGI ──
    section_governance = []
    wgi_list = [
        ("Expression & responsabilité", wgi_voice_val, wgi_voice_year),
        ("Stabilité politique & absence de violence", wgi_polstab_val, wgi_polstab_year),
        ("Efficacité gouvernementale", wgi_goveff_val, wgi_goveff_year),
        ("Qualité réglementaire", wgi_regqual_val, wgi_regqual_year),
        ("État de droit", wgi_rulelaw_val, wgi_rulelaw_year),
        ("Contrôle de la corruption", wgi_corrupt_val, wgi_corrupt_year),
    ]
    for label, val, year in wgi_list:
        v = f"{val:.2f}" if val is not None else "N/D"
        section_governance.append(ind(f"WGI — {label}", v, "[-2.5 ; +2.5]", year, "Banque Mondiale (WGI)", "https://info.worldbank.org/governance/wgi/"))

    # ── Section 3 : Marché du travail ──
    section_labour = []
    labour_list = [
        ("Taux d'emploi total", emp_tot_val, emp_tot_year, "%"),
        ("Chômage des jeunes (15-24 ans)", emp_youth_val, emp_youth_year, "%"),
        ("Taux d'emploi des femmes", emp_fem_val, emp_fem_year, "%"),
        ("Taux d'informalité", informal_val, informal_year, "%"),
    ]
    notes_labour = ["", "", "", "Souvent non disponible pour de nombreux pays"]
    for (label, val, year, unit), note in zip(labour_list, notes_labour):
        v = f"{val:.1f}" if val is not None else "N/D"
        n = note if val is None else None
        section_labour.append(ind(label, v, unit, year, "Banque Mondiale / OIT", wb_url_base, n))

    # ── Section 4 : Pauvreté & Inégalités ──
    section_poverty = []
    pov_v = f"{poverty_val:.1f}" if poverty_val is not None else "N/D"
    pov_n = None if poverty_val is not None else "Absent pour PRITS/PRE"
    section_poverty.append(ind("Taux de pauvreté (< 2,15 $/j)", pov_v, "%", poverty_year, "Banque Mondiale", wb_url_base, pov_n))
    gini_v = f"{gini_val:.1f}" if gini_val is not None else "N/D"
    gini_n = None if gini_val is not None else "Enquêtes disponibles par intermittence"
    section_poverty.append(ind("Indice de Gini", gini_v, None, gini_year, "Banque Mondiale", wb_url_base, gini_n))

    # ── Section 5 : Éducation ──
    section_education = []
    for label, val, year in [
        ("Scolarisation primaire (taux brut)", prim_val, prim_year),
        ("Scolarisation secondaire (taux brut)", sec_val, sec_year),
        ("Scolarisation tertiaire (taux brut)", tert_val, tert_year),
    ]:
        v = f"{val:.1f}" if val is not None else "N/D"
        section_education.append(ind(label, v, "%", year, "Banque Mondiale / UNESCO", wb_url_base))

    # ── Section 6 : Climat & Environnement ──
    section_climate = []
    co2_v = f"{co2_val:.2f}" if co2_val is not None else "N/D"
    section_climate.append(ind("Émissions CO₂ par habitant", co2_v, "t/hab", co2_year, "Banque Mondiale", wb_url_base))
    for_v = f"{forests_val:.1f}" if forests_val is not None else "N/D"
    section_climate.append(ind("Couvert forestier", for_v, "% superficie", forests_year, "Banque Mondiale / FAO", wb_url_base))
    ren_v = f"{renewable_val:.1f}" if renewable_val is not None else "N/D"
    section_climate.append(ind("Énergie renouvelable (% mix énergétique)", ren_v, "%", renewable_year, "Banque Mondiale / AIE", wb_url_base))
    section_climate.append(ind("ND-Gain Index", "N/D", None, None, "Notre Dame Global Adaptation Initiative", "https://gain.nd.edu/our-work/country-index/", "Téléchargement manuel requis — gain.nd.edu"))
    section_climate.append(ind("Biodiversity Intactness Index", "N/D", None, None, "UK Natural History Museum", "https://www.nhm.ac.uk/our-science/data/biodiversity-indicators/", "Téléchargement manuel requis — nhm.ac.uk"))

    # ── Pilier 1 : Environnement politique et socioéconomique consolidé ──
    pillar_sociopo = build_sociopo_section(
        section_header,
        section_governance,
        section_labour,
        section_poverty,
        section_education
    )

    # ── Pilier 2 : Modèle économique et régime de croissance ──
    with st.spinner("Construction du bloc Modèle économique et régime de croissance..."):
        pillar_growth = build_growth_section(wb_code)

    # ══════════════════════════════════════
    # Affichage
    # ══════════════════════════════════════
    DISPLAY_COLS = ["Indicateur", "Valeur", "Unité", "Année", "Source", "URL source", "Note"]

    def show_section(title, subtitle, rows, source_url=None, source_label=None):
        st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="section-subtitle">{subtitle}</div>', unsafe_allow_html=True)

        if not rows:
            st.markdown('<p class="warn-missing">Aucune donnée disponible.</p>', unsafe_allow_html=True)
            return

        df = pd.DataFrame(rows)

        # Garantit que toutes les colonnes attendues existent, même si une ligne est incomplète.
        for col in DISPLAY_COLS:
            if col not in df.columns:
                df[col] = ""

        df = df[DISPLAY_COLS]

        # Évite les valeurs None dans la colonne de liens.
        df["URL source"] = df["URL source"].fillna("").astype(str)

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "URL source": st.column_config.LinkColumn(
                    "Lien vérifiable",
                    display_text="ouvrir"
                )
            }
        )

        missing_links = df["URL source"].str.strip().eq("").sum()
        if missing_links > 0:
            st.markdown(
                f'<p class="source-note">⚠️ {missing_links} indicateur(s) sans lien vérifiable direct : voir la colonne Note.</p>',
                unsafe_allow_html=True
            )

        if source_url:
            st.markdown(
                f'<p class="source-note">🔗 <a href="{source_url}" target="_blank">{source_label or source_url}</a></p>',
                unsafe_allow_html=True
            )

    show_section("📌 Pilier 1 — Environnement politique et socioéconomique",
        "Bloc consolidé : Freedom House, IDH, statut de revenu, Gini, pauvreté, emploi, éducation et gouvernance WGI",
        pillar_sociopo, "https://data.worldbank.org", "Freedom House · PNUD · Banque mondiale · WGI")

    with st.expander("Voir le détail des sous-sections socio-politiques"):
        show_section("📋 En-tête",
            "Gouvernance politique, positionnement économique, IDH — Sources : Freedom House · PNUD · Banque Mondiale",
            section_header, "https://freedomhouse.org", "Freedom House · PNUD · Banque Mondiale")

        show_section("🏛️ Gouvernance (WGI)",
            "6 indicateurs de gouvernance mondiale — échelle de −2,5 (mauvais) à +2,5 (bon)",
            section_governance, "https://info.worldbank.org/governance/wgi/", "Banque Mondiale — Worldwide Governance Indicators")

        show_section("💼 Marché du travail",
            "Taux d'emploi, chômage jeunes, emploi féminin, informalité — Source : Banque Mondiale / OIT",
            section_labour, wb_url_base, "Banque Mondiale")

        show_section("📊 Pauvreté et inégalités",
            "Seuil de pauvreté extrême et distribution des revenus — Source : Banque Mondiale",
            section_poverty, wb_url_base, "Banque Mondiale")

        show_section("🎓 Éducation",
            "Taux de scolarisation bruts par niveau — Source : Banque Mondiale / UNESCO",
            section_education, wb_url_base, "Banque Mondiale / UNESCO")

    show_section("📈 Pilier 2 — Modèle économique et régime de croissance",
        "Structure productive, emploi sectoriel, demande, financement, ouverture externe et croissance — Sources : Banque mondiale ; compléments à chercher dans l’Article IV",
        pillar_growth, "https://data.worldbank.org", "Banque mondiale · Article IV FMI pour les informations non standardisées")

    show_section("🌿 Climat et environnement",
        "Émissions CO₂, forêts, mix énergétique — Source : Banque Mondiale · FAO · AIE · ND-Gain · NHM",
        section_climate, wb_url_base, "Banque Mondiale · FAO · AIE")

    # ══════════════════════════════════════
    # Article IV FMI — PDF uploadé
    # ══════════════════════════════════════
    article_iv_prompt_text = None

    st.markdown("---")
    st.markdown('<div class="section-title">📄 Article IV FMI — extraction depuis PDF</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">Déposez un rapport Article IV pour repérer les passages macro, les phrases chiffrées et les tableaux utiles. '
        'L’extraction reste indicative : les PDFs FMI ne sont pas parfaitement standardisés.</div>',
        unsafe_allow_html=True
    )

    if uploaded_article_iv is None:
        st.markdown(
            '<p class="warn-missing">Aucun PDF Article IV déposé. Cette section est optionnelle.</p>',
            unsafe_allow_html=True
        )
    else:
        st.success(f"PDF chargé : {uploaded_article_iv.name}")

        pages_text, text_error = extract_article_iv_pages(uploaded_article_iv)

        if text_error:
            st.error(text_error)
        else:
            st.write("Pages avec texte extrait :", len(pages_text))

            mentions_df = find_article_iv_theme_mentions(pages_text)
            numeric_df = find_article_iv_numeric_sentences(pages_text)

            uploaded_article_iv.seek(0)
            tables, table_error = extract_article_iv_tables(uploaded_article_iv)
            if table_error:
                st.warning(table_error)
                tables = []

            table_scores_df = score_article_iv_tables(tables)

            col_pdf_1, col_pdf_2, col_pdf_3 = st.columns(3)
            with col_pdf_1:
                st.metric("Pages texte", len(pages_text))
            with col_pdf_2:
                st.metric("Tableaux détectés", len(tables))
            with col_pdf_3:
                st.metric("Passages thématiques", 0 if mentions_df.empty else len(mentions_df))

            st.markdown("### Passages macro détectés")
            if mentions_df.empty:
                st.markdown('<p class="warn-missing">Aucun passage macro détecté automatiquement.</p>', unsafe_allow_html=True)
            else:
                st.dataframe(mentions_df, use_container_width=True, hide_index=True)

            st.markdown("### Phrases chiffrées à vérifier")
            if numeric_df.empty:
                st.markdown('<p class="warn-missing">Aucune phrase chiffrée détectée automatiquement.</p>', unsafe_allow_html=True)
            else:
                st.dataframe(numeric_df, use_container_width=True, hide_index=True)

            st.markdown("### Tableaux probablement utiles")
            if table_scores_df.empty:
                st.markdown('<p class="warn-missing">Aucun tableau macro clairement détecté.</p>', unsafe_allow_html=True)
            else:
                st.dataframe(table_scores_df, use_container_width=True, hide_index=True)

            with st.expander("Voir les tableaux extraits du PDF"):
                if not tables:
                    st.write("Aucun tableau extrait.")
                else:
                    for item in tables[:15]:
                        st.markdown(f"**Page {item['page']} — Tableau {item['table_id']}**")
                        st.dataframe(make_unique_columns(item["data"]), use_container_width=True)

            with st.expander("Voir le texte extrait du PDF"):
                full_text = "\n\n".join(
                    [f"--- Page {p['page']} ---\n{p['text']}" for p in pages_text]
                )
                st.text_area("Texte extrait", value=full_text[:50000], height=420)

            article_iv_prompt_text = build_article_iv_prompt(
                selected_name,
                mentions_df,
                numeric_df,
                table_scores_df
            )

            st.markdown("### Prompt IA — Article IV")
            st.text_area(
                "Prompt Article IV généré",
                value=article_iv_prompt_text,
                height=360,
                help="Copiez ce prompt dans une IA pour obtenir une extraction structurée du rapport FMI."
            )

    # ══════════════════════════════════════
    # Prompt IA
    # ══════════════════════════════════════
    st.markdown("---")
    st.markdown('<div class="section-title">🤖 Prompt IA — prêt à copier</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Collez ce texte dans Claude, ChatGPT ou tout autre outil IA pour obtenir une analyse structurée en 3 blocs.</div>', unsafe_allow_html=True)

    all_sections_prompt = {
        "Pilier 1 — Environnement politique et socioéconomique": pillar_sociopo,
        "Pilier 2 — Modèle économique et régime de croissance": pillar_growth,
        "Climat et environnement": section_climate,
    }

    prompt_text = build_ai_prompt(selected_name, all_sections_prompt)

    if article_iv_prompt_text:
        prompt_text = (
            prompt_text
            + "\n\n"
            + "=" * 52
            + "\n"
            + "COMPLÉMENT ARTICLE IV FMI\n"
            + "=" * 52
            + "\n\n"
            + article_iv_prompt_text
        )

    st.text_area("Prompt généré", value=prompt_text, height=420,
                 help="Sélectionnez tout (Ctrl+A) puis copiez (Ctrl+C)")

    growth_prompt_text = build_model_growth_prompt(
        selected_name,
        pillar_growth,
        article_iv_prompt_text
    )

    st.markdown("### Prompt spécialisé — Modèle économique et régime de croissance")
    st.text_area(
        "Prompt croissance généré",
        value=growth_prompt_text,
        height=520,
        help="Prompt dédié pour rédiger précisément la section « Modèle économique et régime de croissance »."
    )

    st.markdown(f'<p class="source-note">📅 Données collectées le {datetime.now().strftime("%d/%m/%Y à %H:%M")} — Toutes les valeurs proviennent de sources officielles vérifiables.</p>', unsafe_allow_html=True)
