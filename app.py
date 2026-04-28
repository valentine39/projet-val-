import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import os
from datetime import datetime

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


def fetch_undp_hdi(iso3):
    """Récupère IDH via l'API PNUD HDR."""
    try:
        url = f"https://api.hdr.undp.org/api/indicators/137906?iso={iso3}&latest=true"
        r = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        data = r.json()
        countries = data.get("data", {}).get("countries", [])
        if countries:
            for ind in countries[0].get("indicators", []):
                if str(ind.get("id")) == "137906":
                    return ind.get("value"), ind.get("year")
        return None, None
    except Exception:
        return None, None


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

        hdi_val, hdi_year = fetch_undp_hdi(country_info["undp_code"])

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

    if hdi_val is not None:
        section_header.append(ind("IDH — Valeur", f"{float(hdi_val):.3f}", None, hdi_year, "PNUD", undp_url))
    else:
        section_header.append(ind("IDH — Valeur", "N/D", None, None, "PNUD", undp_url, "API PNUD — vérifier le code pays"))

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

    # ══════════════════════════════════════
    # Affichage
    # ══════════════════════════════════════
    DISPLAY_COLS = ["Indicateur", "Valeur", "Unité", "Année", "Source", "Note"]

    def show_section(title, subtitle, rows, source_url=None, source_label=None):
        st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="section-subtitle">{subtitle}</div>', unsafe_allow_html=True)
        if not rows:
            st.markdown('<p class="warn-missing">Aucune donnée disponible.</p>', unsafe_allow_html=True)
            return
        df = pd.DataFrame(rows)[DISPLAY_COLS]
        st.dataframe(df, use_container_width=True, hide_index=True)
        if source_url:
            st.markdown(f'<p class="source-note">🔗 <a href="{source_url}" target="_blank">{source_label or source_url}</a></p>', unsafe_allow_html=True)

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

    show_section("🌿 Climat et environnement",
        "Émissions CO₂, forêts, mix énergétique — Source : Banque Mondiale · FAO · AIE · ND-Gain · NHM",
        section_climate, wb_url_base, "Banque Mondiale · FAO · AIE")

    # ══════════════════════════════════════
    # Prompt IA
    # ══════════════════════════════════════
    st.markdown("---")
    st.markdown('<div class="section-title">🤖 Prompt IA — prêt à copier</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Collez ce texte dans Claude, ChatGPT ou tout autre outil IA pour obtenir une analyse structurée en 3 blocs.</div>', unsafe_allow_html=True)

    all_sections_prompt = {
        "En-tête": section_header,
        "Gouvernance WGI": section_governance,
        "Marché du travail": section_labour,
        "Pauvreté et inégalités": section_poverty,
        "Éducation": section_education,
        "Climat et environnement": section_climate,
    }

    prompt_text = build_ai_prompt(selected_name, all_sections_prompt)
    st.text_area("Prompt généré", value=prompt_text, height=420,
                 help="Sélectionnez tout (Ctrl+A) puis copiez (Ctrl+C)")

    st.markdown(f'<p class="source-note">📅 Données collectées le {datetime.now().strftime("%d/%m/%Y à %H:%M")} — Toutes les valeurs proviennent de sources officielles vérifiables.</p>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# SECTION ARTICLE IV FMI — Upload et extraction mécanique
# ═══════════════════════════════════════════════════════════════

st.markdown("---")
st.markdown('<div class="section-title">📄 Article IV FMI — Extraction automatique</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-subtitle">Uploadez un Article IV du FMI pour extraire automatiquement les indicateurs clés. '
    'Note : l\'extraction mécanique fonctionne bien sur les tableaux "Selected Economic Indicators" standard. '
    'Si des données manquent, utilisez le prompt généré pour les extraire via IA.</div>',
    unsafe_allow_html=True
)

uploaded_pdf = st.file_uploader("Déposer un Article IV FMI (PDF)", type=["pdf"])

if uploaded_pdf is not None:

    with st.spinner("Extraction du texte en cours..."):
        try:
            import pdfplumber, io

            pdf_bytes = uploaded_pdf.read()
            full_text = ""
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                for page in pdf.pages:
                    t = page.extract_text()
                    if t:
                        full_text += t + "\n"

        except Exception as e:
            st.markdown(f'<div class="error-box">⚠ Erreur lecture PDF : {e}</div>', unsafe_allow_html=True)
            full_text = ""

    if full_text:

        # ── Extraction des indicateurs ──────────────────────────────
        import re

        def find_pct(pattern, text, flags=re.IGNORECASE):
            """Cherche un pattern et retourne (valeur, contexte)."""
            m = re.search(pattern, text, flags)
            return m.group(1).strip() if m else None

        # Pays / titre
        country_match = re.search(
            r"([\w\s\-]+?)\s*\n?(?:STAFF REPORT|Article IV|ARTICLE IV)",
            full_text[:3000], re.IGNORECASE
        )
        doc_country = country_match.group(1).strip() if country_match else "Pays non identifié"

        # Année de consultation
        year_match = re.search(r"(20\d{2})\s+ARTICLE IV", full_text[:3000], re.IGNORECASE)
        doc_year = year_match.group(1) if year_match else "—"

        # Croissance PIB réel
        gdp_growth = find_pct(
            r"[Rr]eal\s+(?:Non-?oil\s+)?GDP[^:]*?(?:growth|grew)[^\d]*([\-\d\.]+)\s*percent",
            full_text[:8000]
        )
        if not gdp_growth:
            gdp_growth = find_pct(
                r"growth[^.]*?rose to ([\d\.]+)\s*percent",
                full_text[:8000]
            )

        # Croissance projetée
        gdp_proj = find_pct(
            r"[Gg]rowth is (?:projected|expected)[^.]*?([\d\.]+)\s*percent",
            full_text[:8000]
        )

        # Inflation
        inflation = find_pct(
            r"[Ii]nflation[^.]*?(?:declined|fell|rose|increased)[^.]*?([\-\d\.]+)\s*percent\s+in\s+(?:20\d{2})",
            full_text[:8000]
        )
        if not inflation:
            inflation = find_pct(
                r"CPI[^.]*?(?:annual average)[^\d]*([\d\.]+)",
                full_text[:8000]
            )

        # Solde budgétaire / Déficit
        fiscal_def = find_pct(
            r"fiscal deficit[^.]*?([\d\.]+)\s*percent of",
            full_text[:10000], re.IGNORECASE
        )
        if not fiscal_def:
            fiscal_def = find_pct(
                r"[Nn]et lending/borrowing[^\d\-]*([\-\d\.]+)",
                full_text[:10000]
            )

        # Dette publique / PIB
        pub_debt = find_pct(
            r"[Pp]ublic debt[^.]*?([\d\.]+)\s*percent(?:\s+of\s+(?:GDP|non-oil))?",
            full_text[:10000]
        )

        # Compte courant
        current_account = find_pct(
            r"current account[^.]*?(?:deficit|balance)[^.]*?([\-\d\.]+)\s*percent of",
            full_text[:10000], re.IGNORECASE
        )

        # Inflation projetée
        inflation_proj = find_pct(
            r"[Ii]nflation is (?:expected|projected)[^.]*?([\d\.]+)\s*percent",
            full_text[:8000]
        )

        # Recommandations principales (cherche le Staff Appraisal)
        appraisal_match = re.search(
            r"STAFF APPRAISAL\s*([\s\S]{200,1000}?)(?:\n\n|\Z)",
            full_text, re.IGNORECASE
        )
        appraisal_text = appraisal_match.group(1).strip()[:500] if appraisal_match else None

        # ── Affichage des résultats ──────────────────────────────────
        st.markdown(
            f'<div class="section-subtitle">📋 Document identifié : <strong>{doc_country}</strong> — Consultation {doc_year}</div>',
            unsafe_allow_html=True
        )

        DISPLAY_COLS = ["Indicateur", "Valeur", "Unité", "Année", "Source", "Note"]

        rows_imf = []

        def add_row(label, val, unit="", year=doc_year, note=""):
            rows_imf.append({
                "Indicateur": label,
                "Valeur": val if val else "Non extrait",
                "Unité": unit,
                "Année": year,
                "Source": f"FMI Article IV {doc_year}",
                "Note": note if val else "Pattern non trouvé — vérifier manuellement"
            })

        add_row("Croissance PIB réel (estimé)", gdp_growth, "%")
        add_row("Croissance PIB réel (projeté)", gdp_proj, "%")
        add_row("Inflation (moyenne annuelle)", inflation, "%")
        add_row("Inflation (projetée)", inflation_proj, "%")
        add_row("Déficit budgétaire", fiscal_def, "% PIB")
        add_row("Dette publique", pub_debt, "% PIB")
        add_row("Solde compte courant", current_account, "% PIB")

        import pandas as pd
        df_imf = pd.DataFrame(rows_imf)[DISPLAY_COLS]
        st.dataframe(df_imf, use_container_width=True, hide_index=True)

        # ── Qualité d'extraction ──────────────────────────────────────
        extracted_count = sum(1 for r in rows_imf if r["Valeur"] != "Non extrait")
        total_count = len(rows_imf)
        pct = int(extracted_count / total_count * 100)

        if pct >= 70:
            quality_color = "#1f8f55"
            quality_label = f"✓ Bonne extraction ({extracted_count}/{total_count} indicateurs)"
        elif pct >= 40:
            quality_color = "#b26a00"
            quality_label = f"⚠ Extraction partielle ({extracted_count}/{total_count} indicateurs)"
        else:
            quality_color = "#c0392b"
            quality_label = f"✗ Extraction faible ({extracted_count}/{total_count} — recommandé : utiliser le prompt IA)"

        st.markdown(
            f'<p style="color:{quality_color};font-size:12px;margin-top:4px">{quality_label}</p>',
            unsafe_allow_html=True
        )

        # ── Recommandations du Staff ──────────────────────────────────
        if appraisal_text:
            with st.expander("📝 Extrait du Staff Appraisal"):
                st.markdown(
                    f'<p style="font-size:12px;color:#555;font-style:italic;line-height:1.6">{appraisal_text}...</p>',
                    unsafe_allow_html=True
                )

        # ── Prompt IA pour Article IV ──────────────────────────────────
        st.markdown("---")
        st.markdown(
            '<div class="section-subtitle">🤖 Prompt IA — Article IV complet</div>',
            unsafe_allow_html=True
        )

        # Tronquer le texte pour le prompt (les modèles IA ont une limite)
        text_for_prompt = full_text[:15000]
        nb_chars = len(full_text)
        nb_pages_est = nb_chars // 2000

        prompt_imf = f"""ARTICLE IV FMI — {doc_country} ({doc_year})
{'=' * 52}

[Texte extrait automatiquement — {nb_chars} caractères, ~{nb_pages_est} pages]

{text_for_prompt}

{'...[texte tronqué]' if len(full_text) > 15000 else ''}

{'=' * 52}
INSTRUCTIONS POUR L'IA :

À partir de ce texte d'Article IV du FMI, extrais et structure les informations suivantes :

1. TABLEAU DES INDICATEURS CLÉS
   Présente sous forme de tableau : Indicateur | Valeur | Année | Note
   Indicateurs à extraire :
   - Croissance du PIB réel (historique + projections)
   - Inflation (historique + projections)
   - Solde budgétaire / Déficit (% PIB)
   - Dette publique (% PIB)
   - Compte courant (% PIB)
   - Réserves de change (si mentionné)
   - Taux de chômage (si mentionné)

2. RÉSUMÉ EXÉCUTIF (150 mots max)
   Contexte macroéconomique, dynamiques principales, risques identifiés.

3. RECOMMANDATIONS CLÉS DU FMI
   Liste les 3-5 recommandations principales issues du Staff Appraisal.

4. POINTS D'ATTENTION
   - Données manquantes ou incertaines dans le document
   - Risques signalés explicitement par le staff
   - Écarts entre les prévisions et les réalisations

RÈGLES :
- Ne pas inventer de chiffres absents du texte
- Indiquer clairement si une valeur est une estimation ou une projection
- Citer la page ou la section source si possible"""

        st.text_area(
            "Prompt Article IV généré",
            value=prompt_imf,
            height=350,
            help="Sélectionnez tout (Ctrl+A) puis copiez (Ctrl+C)"
        )

        st.markdown(
            f'<p class="source-note">📄 PDF analysé : {uploaded_pdf.name} — '
            f'{nb_chars:,} caractères extraits sur ~{nb_pages_est} pages estimées</p>',
            unsafe_allow_html=True
        )
