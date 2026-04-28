import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
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
# Style AFD
# ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: "Open Sans", Arial, sans-serif;
        color: #1a1a1a;
    }
    .stApp { background-color: #ffffff; }
    .main .block-container { padding-top: 1rem; padding-bottom: 2rem; max-width: 1200px; }
    h1, h2, h3 { font-family: "Open Sans", Arial, sans-serif; color: #003189; }

    .afd-header {
        background-color: #003189;
        padding: 18px 24px;
        border-radius: 6px;
        margin-bottom: 24px;
    }
    .afd-header h1 {
        color: #ffffff !important;
        font-size: 22px;
        margin: 0;
        font-weight: 700;
    }
    .afd-header p {
        color: #ccd6f0;
        font-size: 12px;
        margin: 4px 0 0 0;
    }

    .pillar-title {
        font-size: 16px;
        font-weight: 700;
        color: #ffffff;
        background-color: #003189;
        padding: 10px 16px;
        border-radius: 4px;
        margin: 28px 0 4px 0;
    }
    .pillar-subtitle {
        font-size: 11px;
        color: #666666;
        margin-bottom: 10px;
        padding-left: 4px;
    }

    .prompt-title {
        font-size: 13px;
        font-weight: 700;
        color: #E3001B;
        border-left: 4px solid #E3001B;
        padding-left: 10px;
        margin: 20px 0 6px 0;
    }

    .source-note {
        font-size: 11px;
        color: #888888;
        margin-top: 4px;
    }
    .warn-missing {
        color: #999999;
        font-size: 11px;
        font-style: italic;
    }

    div[data-testid="stButton"] button {
        background: #003189;
        color: white;
        font-family: "Open Sans", Arial, sans-serif;
        font-weight: 700;
        font-size: 13px;
        border: none;
        border-radius: 6px;
        padding: 10px 24px;
        width: 100%;
        transition: background 0.2s;
    }
    div[data-testid="stButton"] button:hover {
        background: #E3001B;
    }

    div[data-testid="stSelectbox"] label {
        color: #003189;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    .footer-note {
        font-size: 11px;
        color: #aaaaaa;
        margin-top: 32px;
        border-top: 1px solid #eeeeee;
        padding-top: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Pays
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
# Fonctions utilitaires
# ─────────────────────────────────────────────

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
# Collecte des données
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


def fetch_wb_history_values(country_code, indicator_code, n_years=25):
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
    return sum(vals) / len(vals) if vals else None


def average_last_n(history, n=10):
    vals = [x["value"] for x in history[-n:]]
    return sum(vals) / len(vals) if vals else None


@st.cache_data(ttl=86400)
def load_undp_hdi_table():
    url = "https://hdr.undp.org/sites/default/files/2025_HDR/HDR25_Statistical_Annex_HDI_Table.xlsx"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,*/*",
        "Referer": "https://hdr.undp.org/data-center/documentation-and-downloads",
    }
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    df_raw = pd.read_excel(BytesIO(r.content), header=None, engine="openpyxl")
    rows = []
    for _, row in df_raw.iterrows():
        values = list(row.dropna())
        if len(values) < 3:
            continue
        try:
            rank_int = int(values[0])
            hdi_float = float(values[2])
            if 0 < hdi_float <= 1:
                rows.append({"rank": rank_int, "country": str(values[1]).strip(), "hdi": hdi_float})
        except Exception:
            continue
    return pd.DataFrame(rows)


def fetch_undp_hdi(country_name=None):
    source_url = "https://hdr.undp.org/sites/default/files/2025_HDR/HDR25_Statistical_Annex_HDI_Table.xlsx"
    aliases = {
        "Timor-Leste": ["Timor-Leste"],
        "RDC (Congo-Kinshasa)": ["Congo (Democratic Republic of the)"],
        "Congo (Brazzaville)": ["Congo"],
        "Côte d'Ivoire": ["Côte d'Ivoire", "Cote d'Ivoire"],
        "Birmanie (Myanmar)": ["Myanmar"],
        "Sao Tomé-et-Principe": ["Sao Tome and Principe", "São Tomé and Príncipe"],
        "Eswatini": ["Eswatini (Kingdom of)", "Eswatini"],
        "Tanzanie": ["Tanzania (United Republic of)"],
        "Bolivie": ["Bolivia (Plurinational State of)", "Bolivia"],
        "Laos": ["Lao People's Democratic Republic"],
        "Syrie": ["Syrian Arab Republic"],
        "Vietnam": ["Viet Nam"],
    }
    try:
        df = load_undp_hdi_table()
        if df.empty:
            return {"value": None, "rank": None, "year": 2023, "source_url": source_url, "error": "Table IDH vide."}
        possible_names = [country_name] + aliases.get(country_name, [])
        possible_names_norm = [x.lower().strip() for x in possible_names]
        row = df[df["country"].str.lower().str.strip().isin(possible_names_norm)]
        if row.empty:
            return {"value": None, "rank": None, "year": 2023, "source_url": source_url, "error": f"Pays introuvable : {country_name}"}
        first = row.iloc[0]
        return {"value": float(first["hdi"]), "rank": int(first["rank"]), "year": 2023, "source_url": source_url, "error": None}
    except Exception as e:
        return {"value": None, "rank": None, "year": 2023, "source_url": source_url, "error": str(e)}


# ─────────────────────────────────────────────
# Construction des piliers
# ─────────────────────────────────────────────

def build_pillar1(wb_code, wb_url_base, fh, wb_info, hdi):
    """Pilier 1 — Environnement politique et socioéconomique"""
    rows = []

    income_code = wb_info.get("income_code", "") if wb_info else ""
    income_label = INCOME_LABELS.get(income_code, wb_info.get("income_label", "N/D") if wb_info else "N/D")
    region = wb_info.get("region", "N/D") if wb_info else "N/D"

    # Freedom House
    if fh and not fh.get("error"):
        if fh.get("score") is not None:
            rows.append(ind("Freedom House — Score", f"{fh['score']}/100", None, fh["year"], "Freedom House", fh["url"]))
        if fh.get("status"):
            rows.append(ind("Freedom House — Statut", fh["status"], None, fh["year"], "Freedom House", fh["url"]))
        if fh.get("pr_score") is not None:
            rows.append(ind("Droits politiques", f"{fh['pr_score']}/40", None, fh["year"], "Freedom House", fh["url"]))
        if fh.get("cl_score") is not None:
            rows.append(ind("Libertés civiles", f"{fh['cl_score']}/60", None, fh["year"], "Freedom House", fh["url"]))
    else:
        rows.append(ind("Freedom House", "Indisponible", None, None, "Freedom House", "https://freedomhouse.org", "Erreur de scraping"))

    rows.append(ind("EIU — Democracy Index", "Non disponible", None, None, "EIU", "https://www.eiu.com", "Accès abonnement requis"))

    # IDH
    if hdi.get("value") is not None:
        rows.append(ind("IDH — Valeur", f"{hdi['value']:.3f}", None, hdi["year"], "PNUD / Human Development Report", hdi["source_url"]))
        if hdi.get("rank"):
            rows.append(ind("IDH — Rang mondial", str(hdi["rank"]), None, hdi["year"], "PNUD / Human Development Report", hdi["source_url"]))
    else:
        rows.append(ind("IDH", "N/D", None, None, "PNUD / Human Development Report", hdi.get("source_url", ""), hdi.get("error", "")))

    # Banque mondiale — positionnement
    rows.append(ind("Statut de revenu (BM)", income_label, None, None, "Banque mondiale", wb_url_base))
    rows.append(ind("Région BM", region, None, None, "Banque mondiale", wb_url_base))

    gdp_val, gdp_year = fetch_wb_latest(wb_code, "NY.GDP.PCAP.CD")
    if gdp_val:
        rows.append(ind("PIB / habitant", f"${gdp_val:,.0f}", "USD", gdp_year, "Banque mondiale", wb_url_base))

    gini_val, gini_year = fetch_wb_latest(wb_code, "SI.POV.GINI")
    rows.append(ind("Indice de Gini", f"{gini_val:.1f}" if gini_val else "N/D", None, gini_year, "Banque mondiale", wb_url_base,
                    None if gini_val else "Enquêtes disponibles par intermittence"))

    poverty_val, poverty_year = fetch_wb_latest(wb_code, "SI.POV.DDAY")
    rows.append(ind("Taux de pauvreté (< 2,15 $/j)", f"{poverty_val:.1f}" if poverty_val else "N/D", "%", poverty_year,
                    "Banque mondiale", wb_url_base, None if poverty_val else "Absent pour PRITS/PRE"))

    # Gouvernance WGI
    wgi_indicators = [
        ("VA.EST", "WGI — Expression & responsabilité"),
        ("PV.EST", "WGI — Stabilité politique & absence de violence"),
        ("GE.EST", "WGI — Efficacité gouvernementale"),
        ("RQ.EST", "WGI — Qualité réglementaire"),
        ("RL.EST", "WGI — État de droit"),
        ("CC.EST", "WGI — Contrôle de la corruption"),
    ]
    for code, label in wgi_indicators:
        val, year = fetch_wb_latest(wb_code, code)
        rows.append(ind(label, f"{val:.2f}" if val is not None else "N/D", "[-2.5 ; +2.5]", year,
                        "Banque mondiale (WGI)", "https://info.worldbank.org/governance/wgi/"))

    # Marché du travail
    labour = [
        ("SL.EMP.TOTL.SP.ZS", "Taux d'emploi total", "%", None),
        ("SL.UEM.1524.ZS", "Chômage des jeunes (15-24 ans)", "%", None),
        ("SL.EMP.TOTL.SP.FE.ZS", "Taux d'emploi des femmes", "%", None),
        ("SL.ISV.IFRM.ZS", "Taux d'informalité", "%", "Souvent non disponible"),
    ]
    for code, label, unit, default_note in labour:
        val, year = fetch_wb_latest(wb_code, code)
        rows.append(ind(label, f"{val:.1f}" if val is not None else "N/D", unit, year,
                        "Banque mondiale / OIT", wb_url_base, None if val is not None else default_note))

    # Éducation
    education = [
        ("SE.PRM.ENRR", "Scolarisation primaire (taux brut)", "%"),
        ("SE.SEC.ENRR", "Scolarisation secondaire (taux brut)", "%"),
        ("SE.TER.ENRR", "Scolarisation tertiaire (taux brut)", "%"),
    ]
    for code, label, unit in education:
        val, year = fetch_wb_latest(wb_code, code)
        rows.append(ind(label, f"{val:.1f}" if val is not None else "N/D", unit, year,
                        "Banque mondiale / UNESCO", wb_url_base))

    return rows


def build_pillar2(wb_code):
    """Pilier 2 — Modèle économique et régime de croissance"""
    rows = []

    wb_url = "https://data.worldbank.org/indicator/"

    indicators = [
        ("NY.GDP.MKTP.CD",     "PIB nominal total",                          "USD courants"),
        ("NY.GDP.PCAP.CD",     "PIB par habitant",                           "USD courants"),
        ("NY.GDP.MKTP.KD.ZG",  "Croissance du PIB réel — dernière obs.",     "%"),
        ("FP.CPI.TOTL.ZG",     "Inflation annuelle",                         "%"),
        ("NV.AGR.TOTL.ZS",     "Agriculture — part du PIB",                  "% du PIB"),
        ("NV.IND.TOTL.ZS",     "Industrie — part du PIB",                    "% du PIB"),
        ("NV.IND.MANF.ZS",     "Manufacturier — part du PIB",                "% du PIB"),
        ("NV.SRV.TOTL.ZS",     "Services — part du PIB",                     "% du PIB"),
        ("SL.AGR.EMPL.ZS",     "Emploi agricole",                            "% emploi total"),
        ("SL.IND.EMPL.ZS",     "Emploi industriel",                          "% emploi total"),
        ("SL.SRV.EMPL.ZS",     "Emploi dans les services",                   "% emploi total"),
        ("NE.CON.PRVT.ZS",     "Consommation privée",                        "% du PIB"),
        ("NE.CON.GOVT.ZS",     "Consommation publique",                      "% du PIB"),
        ("NE.GDI.FTOT.ZS",     "Formation brute de capital fixe",            "% du PIB"),
        ("NE.GDI.FPRV.ZS",     "Investissement privé",                       "% du PIB"),
        ("BX.KLT.DINV.WD.GD.ZS", "IDE entrants nets",                       "% du PIB"),
        ("BX.TRF.PWKR.DT.GD.ZS", "Transferts de migrants",                  "% du PIB"),
        ("FS.AST.PRVT.GD.ZS",  "Crédit domestique secteur privé",            "% du PIB"),
        ("NE.EXP.GNFS.ZS",     "Exportations biens et services",             "% du PIB"),
        ("NE.IMP.GNFS.ZS",     "Importations biens et services",             "% du PIB"),
        ("BN.CAB.XOKA.GD.ZS",  "Solde courant",                              "% du PIB"),
    ]

    growth_hist = []
    for code, label, unit in indicators:
        hist = fetch_wb_history_values(wb_code, code, n_years=25)
        val, year = latest_from_history(hist)
        v = f"{val:,.1f}" if isinstance(val, (int, float)) else "N/D"
        rows.append(ind(label, v, unit, year, "Banque mondiale", f"{wb_url}{code}"))
        if code == "NY.GDP.MKTP.KD.ZG":
            growth_hist = hist

    # Moyennes de croissance
    avg_2010 = average_since(growth_hist, 2010)
    avg_10y = average_last_n(growth_hist, 10)

    years_since_2010 = [x["year"] for x in growth_hist if x["year"] >= 2010]
    period_2010 = f"{min(years_since_2010)}-{max(years_since_2010)}" if years_since_2010 else None

    years_10y = [x["year"] for x in growth_hist[-10:]]
    period_10y = f"{years_10y[0]}-{years_10y[-1]}" if len(years_10y) >= 2 else None

    rows.append(ind(
        "Croissance moyenne PIB réel depuis 2010",
        f"{avg_2010:.1f}" if avg_2010 is not None else "N/D",
        "%", period_2010,
        "Calcul interne — Banque mondiale",
        f"{wb_url}NY.GDP.MKTP.KD.ZG",
        None if avg_2010 is not None else "Série insuffisante"
    ))
    rows.append(ind(
        "Croissance moyenne PIB réel — 10 dernières obs.",
        f"{avg_10y:.1f}" if avg_10y is not None else "N/D",
        "%", period_10y,
        "Calcul interne — Banque mondiale",
        f"{wb_url}NY.GDP.MKTP.KD.ZG",
        None if avg_10y is not None else "Série insuffisante"
    ))

    # Indicateurs à compléter manuellement
    manual_guides = [
        ("Part secteur extractif — PIB",           "Comptes nationaux détaillés / Article IV FMI / EITI"),
        ("Part secteur extractif — exportations",  "UN Comtrade / OEC / Article IV FMI"),
        ("Part secteur extractif — recettes pub.", "Article IV FMI / DSA FMI / budget national"),
        ("Part du tourisme dans le PIB",            "WTTC / UN Tourism / Article IV FMI"),
        ("Croissance potentielle FMI",              "Article IV FMI — texte ou annexes"),
        ("Prévisions FMI (année en cours / N+1)",  "Article IV FMI / WEO"),
        ("Réformes et chocs récents",               "Article IV FMI / Banque mondiale MPO"),
    ]
    for label, note in manual_guides:
        rows.append(ind(label, "À compléter", None, None, "Source sectorielle", "", note))

    return rows


# ─────────────────────────────────────────────
# Prompts IA par pilier
# ─────────────────────────────────────────────

def build_prompt_pillar1(country_name, rows):
    lines = [
        f"FICHE PAYS — {country_name.upper()}",
        "PILIER 1 : ENVIRONNEMENT POLITIQUE ET SOCIOÉCONOMIQUE",
        "=" * 70,
        "",
        "DONNÉES COLLECTÉES",
        "-" * 40,
    ]
    for r in rows:
        label = r.get("Indicateur", "")
        val = r.get("Valeur", "N/D")
        unit = r.get("Unité", "")
        year = r.get("Année", "—")
        source = r.get("Source", "")
        note = r.get("Note", "")
        unit_str = f" {unit}" if unit else ""
        year_str = f" ({year})" if year and year != "—" else ""
        note_str = f" — ⚠️ {note}" if note else ""
        lines.append(f"• {label} : {val}{unit_str}{year_str} — {source}{note_str}")

    lines += [
        "",
        "=" * 70,
        "CONSIGNE DE RÉDACTION",
        "-" * 40,
        "",
        "À partir des données ci-dessus, rédige une analyse structurée du Pilier 1.",
        "",
        "STRUCTURE ATTENDUE :",
        "",
        "1. RÉGIME POLITIQUE ET LIBERTÉS",
        "   - Caractérise le régime politique (démocratie, autoritarisme, hybride).",
        "   - Appuie-toi sur Freedom House (score, statut, droits politiques, libertés civiles).",
        "   - Signale les tendances récentes si elles ressortent des données.",
        "",
        "2. GOUVERNANCE INSTITUTIONNELLE",
        "   - Analyse les 6 indicateurs WGI : identifie les forces et faiblesses.",
        "   - Mets en évidence les écarts entre indicateurs (ex : bonne stabilité mais faible état de droit).",
        "",
        "3. DÉVELOPPEMENT HUMAIN ET INÉGALITÉS",
        "   - Commente l'IDH (valeur, rang) et son positionnement régional.",
        "   - Articule avec le Gini, le taux de pauvreté et le PIB/habitant.",
        "",
        "4. MARCHÉ DU TRAVAIL",
        "   - Commente l'emploi, le chômage des jeunes, l'emploi féminin et l'informalité.",
        "   - Identifie les tensions ou fragilités structurelles.",
        "",
        "5. CAPITAL HUMAIN (ÉDUCATION)",
        "   - Commente les taux de scolarisation par niveau.",
        "   - Signale les ruptures ou décrochages significatifs.",
        "",
        "RÈGLES :",
        "- Ne pas inventer de chiffres. Utiliser uniquement les données fournies.",
        "- Si une donnée est manquante ou ancienne, le signaler explicitement.",
        "- Style analytique, institutionnel, sans bullet points dans la rédaction finale.",
        "- Environ 400-500 mots.",
    ]
    return "\n".join(lines)


def build_prompt_pillar2(country_name, rows):
    lines = [
        f"FICHE PAYS — {country_name.upper()}",
        "PILIER 2 : MODÈLE ÉCONOMIQUE ET RÉGIME DE CROISSANCE",
        "=" * 70,
        "",
        "DONNÉES COLLECTÉES",
        "-" * 40,
    ]
    for r in rows:
        label = r.get("Indicateur", "")
        val = r.get("Valeur", "N/D")
        unit = r.get("Unité", "")
        year = r.get("Année", "—")
        source = r.get("Source", "")
        note = r.get("Note", "")
        unit_str = f" {unit}" if unit else ""
        year_str = f" ({year})" if year and year != "—" else ""
        note_str = f" — ⚠️ {note}" if note else ""
        lines.append(f"• {label} : {val}{unit_str}{year_str} — {source}{note_str}")

    lines += [
        "",
        "=" * 70,
        "CONSIGNE DE RÉDACTION",
        "-" * 40,
        "",
        "À partir des données ci-dessus, rédige une analyse structurée du Pilier 2.",
        "Le texte doit comporter deux sous-parties explicites.",
        "",
        "PARTIE 1 — MODÈLE ÉCONOMIQUE",
        "   - Caractérise la structure productive : diversifiée ou non, industrialisée, agricole,",
        "     extractive, tertiarisée, rentière, ouverte, dépendante des importations.",
        "   - Présente les principaux secteurs dans l'ordre de leur importance.",
        "   - Pour chaque secteur majeur : part dans le PIB, dans l'emploi, rôle aux exportations.",
        "   - Identifie forces structurelles et fragilités structurelles.",
        "   - Si une transformation est en cours, décris-la et évalue sa solidité.",
        "   - Conclure par le principal risque structurel du modèle.",
        "",
        "PARTIE 2 — RÉGIME DE CROISSANCE",
        "   - Qualifie le rythme de croissance sur longue période (dynamique, faible, volatile...).",
        "   - Donne la croissance moyenne sur 10 ans ou depuis 2010.",
        "   - Identifie les moteurs de croissance dominants.",
        "   - Distingue tendance longue et évolutions récentes.",
        "   - Mentionne les chocs récents documentés par les données.",
        "   - Analyse la soutenabilité de la croissance.",
        "   - Conclure sur les perspectives et risques à moyen terme.",
        "",
        "RÈGLES :",
        "- Ne pas inventer de chiffres. Les indicateurs 'À compléter' doivent être signalés comme manquants.",
        "- Style analytique, institutionnel, dense, sans bullet points dans la rédaction finale.",
        "- Environ 500-600 mots.",
    ]
    return "\n".join(lines)


# ─────────────────────────────────────────────
# Affichage
# ─────────────────────────────────────────────

DISPLAY_COLS = ["Indicateur", "Valeur", "Unité", "Année", "Source", "URL source", "Note"]


def show_pillar(title, subtitle, rows, source_label=None, source_url=None):
    st.markdown(f'<div class="pillar-title">{title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="pillar-subtitle">{subtitle}</div>', unsafe_allow_html=True)

    if not rows:
        st.markdown('<p class="warn-missing">Aucune donnée disponible.</p>', unsafe_allow_html=True)
        return

    df = pd.DataFrame(rows)
    for col in DISPLAY_COLS:
        if col not in df.columns:
            df[col] = ""
    df = df[DISPLAY_COLS]
    df["URL source"] = df["URL source"].fillna("").astype(str)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "URL source": st.column_config.LinkColumn("Lien", display_text="ouvrir")
        }
    )

    missing = df["URL source"].str.strip().eq("").sum()
    if missing > 0:
        st.markdown(
            f'<p class="source-note">⚠️ {missing} indicateur(s) sans lien direct — voir colonne Note.</p>',
            unsafe_allow_html=True
        )
    if source_url:
        st.markdown(
            f'<p class="source-note">🔗 <a href="{source_url}" target="_blank">{source_label or source_url}</a></p>',
            unsafe_allow_html=True
        )


def show_prompt(title, prompt_text):
    st.markdown(f'<div class="prompt-title">🤖 {title}</div>', unsafe_allow_html=True)
    st.text_area(
        label="",
        value=prompt_text,
        height=380,
        help="Sélectionnez tout (Ctrl+A) puis copiez (Ctrl+C) pour coller dans une IA."
    )


# ─────────────────────────────────────────────
# Interface principale
# ─────────────────────────────────────────────

st.markdown("""
<div class="afd-header">
    <h1>🌍 Outil de collecte de données — DER</h1>
    <p>Collecte automatique · Sources officielles · Prompt IA par pilier</p>
</div>
""", unsafe_allow_html=True)

country_options = dict(sorted({info["name"]: key for key, info in COUNTRY_MAPPING.items()}.items()))
selected_name = st.selectbox("Sélectionner un pays", options=list(country_options.keys()))
selected_key = country_options[selected_name]
country_info = COUNTRY_MAPPING[selected_key]
wb_code = country_info["world_bank_code"]
wb_url_base = f"https://data.worldbank.org/country/{country_info['wb_url_code']}"

st.write("")

if st.button("Récupérer les données →"):

    with st.spinner("Collecte en cours — Freedom House, Banque mondiale, PNUD..."):
        fh       = fetch_freedom_house(country_info["freedom_house_slug"])
        wb_info  = fetch_wb_country_info(wb_code)
        hdi      = fetch_undp_hdi(country_info["name"])

    with st.spinner("Construction Pilier 1..."):
        pillar1_rows = build_pillar1(wb_code, wb_url_base, fh, wb_info, hdi)

    with st.spinner("Construction Pilier 2..."):
        pillar2_rows = build_pillar2(wb_code)

    # ── Pilier 1
    show_pillar(
        "📌 Pilier 1 — Environnement politique et socioéconomique",
        "Freedom House · IDH · Statut de revenu · Gouvernance WGI · Emploi · Pauvreté · Éducation",
        pillar1_rows,
        "Freedom House · PNUD · Banque mondiale",
        "https://data.worldbank.org"
    )

    prompt1 = build_prompt_pillar1(selected_name, pillar1_rows)
    show_prompt("Prompt IA — Pilier 1", prompt1)

    st.markdown("---")

    # ── Pilier 2
    show_pillar(
        "📈 Pilier 2 — Modèle économique et régime de croissance",
        "Structure productive · Emploi sectoriel · Demande · Financement · Ouverture externe · Croissance",
        pillar2_rows,
        "Banque mondiale",
        "https://data.worldbank.org"
    )

    prompt2 = build_prompt_pillar2(selected_name, pillar2_rows)
    show_prompt("Prompt IA — Pilier 2", prompt2)

    st.markdown(
        f'<p class="footer-note">📅 Données collectées le {datetime.now().strftime("%d/%m/%Y à %H:%M")} — '
        f'Sources officielles vérifiables.</p>',
        unsafe_allow_html=True
    )
