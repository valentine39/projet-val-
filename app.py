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
@import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: "Open Sans", Arial, sans-serif;
    color: #1a1a1a;
}
.stApp { background-color: #f4f6fb; }
.main .block-container { padding-top: 1rem; padding-bottom: 2rem; max-width: 1300px; }
h1, h2, h3 { font-family: "Open Sans", Arial, sans-serif; color: #003189; }

/* HEADER */
.afd-header {
    background: linear-gradient(135deg, #003189 0%, #0047c8 100%);
    padding: 22px 28px;
    border-radius: 10px;
    margin-bottom: 28px;
    box-shadow: 0 4px 15px rgba(0,49,137,0.25);
}
.afd-header h1 {
    color: #ffffff !important;
    font-size: 24px;
    margin: 0;
    font-weight: 700;
    letter-spacing: -0.3px;
}
.afd-header p {
    color: #a8c0f0;
    font-size: 13px;
    margin: 6px 0 0 0;
}

/* SECTION HEADERS */
.section-header {
    display: flex;
    align-items: center;
    gap: 10px;
    background: linear-gradient(90deg, #003189 0%, #0a3fa8 100%);
    padding: 12px 18px;
    border-radius: 8px;
    margin: 24px 0 6px 0;
    box-shadow: 0 2px 8px rgba(0,49,137,0.2);
}
.section-header h3 {
    color: #ffffff !important;
    font-size: 15px;
    margin: 0;
    font-weight: 700;
}
.section-subtitle {
    font-size: 11px;
    color: #777;
    margin-bottom: 12px;
    padding-left: 4px;
    font-style: italic;
}

/* THEMATIC GROUP CARDS */
.theme-card {
    background: white;
    border-radius: 10px;
    padding: 16px;
    margin-bottom: 14px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.07);
    border-left: 5px solid #003189;
    transition: box-shadow 0.2s;
}
.theme-card:hover {
    box-shadow: 0 4px 16px rgba(0,0,0,0.12);
}
.theme-card-title {
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 12px;
    color: #003189;
}

/* INDICATOR ROWS */
.indicator-row {
    display: flex;
    align-items: center;
    padding: 7px 10px;
    border-radius: 6px;
    margin-bottom: 5px;
    background: #f8f9fd;
    transition: background 0.15s;
}
.indicator-row:hover { background: #eef1fa; }
.indicator-label {
    flex: 1;
    font-size: 12.5px;
    color: #333;
    font-weight: 400;
}
.indicator-value {
    font-size: 13px;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 20px;
    min-width: 90px;
    text-align: center;
    margin: 0 8px;
}
.indicator-meta {
    font-size: 10.5px;
    color: #999;
    min-width: 80px;
    text-align: right;
}
.indicator-source {
    font-size: 10px;
    color: #aaa;
    text-align: right;
    min-width: 120px;
    padding-left: 8px;
}
.indicator-note {
    font-size: 10px;
    color: #e07c00;
    font-style: italic;
    margin-left: 6px;
}

/* COLOR BADGES */
.badge-green {
    background: #d4f0e0;
    color: #1a7a45;
    border: 1px solid #a8dfc0;
}
.badge-lightgreen {
    background: #e6f7ee;
    color: #2e8b57;
    border: 1px solid #b8e6cc;
}
.badge-orange {
    background: #fff3e0;
    color: #c17000;
    border: 1px solid #ffd180;
}
.badge-red {
    background: #fde8e8;
    color: #c0392b;
    border: 1px solid #f5b7b1;
}
.badge-grey {
    background: #f0f0f0;
    color: #888;
    border: 1px solid #ddd;
}
.badge-blue {
    background: #e8eeff;
    color: #003189;
    border: 1px solid #b8c8f5;
}
.badge-purple {
    background: #f0e8ff;
    color: #6b21a8;
    border: 1px solid #d8b4fe;
}

/* LEGEND */
.legend-bar {
    display: flex;
    gap: 14px;
    flex-wrap: wrap;
    margin: 6px 0 18px 0;
    padding: 10px 14px;
    background: white;
    border-radius: 8px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.legend-item {
    display: flex;
    align-items: center;
    gap: 5px;
    font-size: 11px;
    color: #555;
}
.legend-dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
}

/* PROMPT */
.prompt-title {
    font-size: 13px;
    font-weight: 700;
    color: #E3001B;
    border-left: 4px solid #E3001B;
    padding-left: 10px;
    margin: 20px 0 6px 0;
}

/* SUMMARY METRICS */
.summary-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin: 16px 0;
}
.summary-card {
    background: white;
    border-radius: 8px;
    padding: 14px 16px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.07);
    text-align: center;
    border-top: 3px solid #003189;
}
.summary-card .s-label {
    font-size: 10.5px;
    color: #888;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 6px;
}
.summary-card .s-value {
    font-size: 20px;
    font-weight: 700;
    color: #003189;
}
.summary-card .s-sub {
    font-size: 10px;
    color: #aaa;
    margin-top: 2px;
}

/* BUTTONS */
div[data-testid="stButton"] button {
    background: linear-gradient(135deg, #003189 0%, #0047c8 100%);
    color: white;
    font-family: "Open Sans", Arial, sans-serif;
    font-weight: 700;
    font-size: 14px;
    border: none;
    border-radius: 8px;
    padding: 12px 28px;
    width: 100%;
    transition: all 0.2s;
    box-shadow: 0 3px 12px rgba(0,49,137,0.3);
}
div[data-testid="stButton"] button:hover {
    background: linear-gradient(135deg, #E3001B 0%, #ff2020 100%);
    box-shadow: 0 4px 16px rgba(227,0,27,0.35);
    transform: translateY(-1px);
}

div[data-testid="stSelectbox"] label {
    color: #003189;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

/* EXPANDER */
.streamlit-expanderHeader {
    background: #f0f4ff !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
    color: #003189 !important;
}

/* TABS */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: white;
    padding: 6px;
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.07);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 6px;
    padding: 8px 16px;
    font-size: 12.5px;
    font-weight: 600;
}
.stTabs [aria-selected="true"] {
    background-color: #003189 !important;
    color: white !important;
}

.footer-note {
    font-size: 11px;
    color: #aaa;
    margin-top: 32px;
    border-top: 1px solid #e8e8e8;
    padding-top: 10px;
    text-align: center;
}

/* WARN */
.warn-missing {
    color: #999;
    font-size: 11px;
    font-style: italic;
}
.source-note {
    font-size: 11px;
    color: #888;
    margin-top: 4px;
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
    "argentine": {"name": "Argentine", "freedom_house_slug": "argentina", "world_bank_code": "ARG", "wb_url_code": "AR", "undp_code": "ARG"},
    "armenie": {"name": "Arménie", "freedom_house_slug": "armenia", "world_bank_code": "ARM", "wb_url_code": "AM", "undp_code": "ARM"},
    "azerbaijan": {"name": "Azerbaïdjan", "freedom_house_slug": "azerbaijan", "world_bank_code": "AZE", "wb_url_code": "AZ", "undp_code": "AZE"},
    "bangladesh": {"name": "Bangladesh", "freedom_house_slug": "bangladesh", "world_bank_code": "BGD", "wb_url_code": "BD", "undp_code": "BGD"},
    "benin": {"name": "Bénin", "freedom_house_slug": "benin", "world_bank_code": "BEN", "wb_url_code": "BJ", "undp_code": "BEN"},
    "bolivie": {"name": "Bolivie", "freedom_house_slug": "bolivia", "world_bank_code": "BOL", "wb_url_code": "BO", "undp_code": "BOL"},
    "bresil": {"name": "Brésil", "freedom_house_slug": "brazil", "world_bank_code": "BRA", "wb_url_code": "BR", "undp_code": "BRA"},
    "burkina_faso": {"name": "Burkina Faso", "freedom_house_slug": "burkina-faso", "world_bank_code": "BFA", "wb_url_code": "BF", "undp_code": "BFA"},
    "burundi": {"name": "Burundi", "freedom_house_slug": "burundi", "world_bank_code": "BDI", "wb_url_code": "BI", "undp_code": "BDI"},
    "cambodge": {"name": "Cambodge", "freedom_house_slug": "cambodia", "world_bank_code": "KHM", "wb_url_code": "KH", "undp_code": "KHM"},
    "cameroun": {"name": "Cameroun", "freedom_house_slug": "cameroon", "world_bank_code": "CMR", "wb_url_code": "CM", "undp_code": "CMR"},
    "chili": {"name": "Chili", "freedom_house_slug": "chile", "world_bank_code": "CHL", "wb_url_code": "CL", "undp_code": "CHL"},
    "chine": {"name": "Chine", "freedom_house_slug": "china", "world_bank_code": "CHN", "wb_url_code": "CN", "undp_code": "CHN"},
    "colombie": {"name": "Colombie", "freedom_house_slug": "colombia", "world_bank_code": "COL", "wb_url_code": "CO", "undp_code": "COL"},
    "cote_ivoire": {"name": "Côte d'Ivoire", "freedom_house_slug": "cote-divoire", "world_bank_code": "CIV", "wb_url_code": "CI", "undp_code": "CIV"},
    "egypte": {"name": "Égypte", "freedom_house_slug": "egypt", "world_bank_code": "EGY", "wb_url_code": "EG", "undp_code": "EGY"},
    "ethiopie": {"name": "Éthiopie", "freedom_house_slug": "ethiopia", "world_bank_code": "ETH", "wb_url_code": "ET", "undp_code": "ETH"},
    "ghana": {"name": "Ghana", "freedom_house_slug": "ghana", "world_bank_code": "GHA", "wb_url_code": "GH", "undp_code": "GHA"},
    "guinee": {"name": "Guinée", "freedom_house_slug": "guinea", "world_bank_code": "GIN", "wb_url_code": "GN", "undp_code": "GIN"},
    "haiti": {"name": "Haïti", "freedom_house_slug": "haiti", "world_bank_code": "HTI", "wb_url_code": "HT", "undp_code": "HTI"},
    "inde": {"name": "Inde", "freedom_house_slug": "india", "world_bank_code": "IND", "wb_url_code": "IN", "undp_code": "IND"},
    "indonesie": {"name": "Indonésie", "freedom_house_slug": "indonesia", "world_bank_code": "IDN", "wb_url_code": "ID", "undp_code": "IDN"},
    "irak": {"name": "Irak", "freedom_house_slug": "iraq", "world_bank_code": "IRQ", "wb_url_code": "IQ", "undp_code": "IRQ"},
    "kenya": {"name": "Kenya", "freedom_house_slug": "kenya", "world_bank_code": "KEN", "wb_url_code": "KE", "undp_code": "KEN"},
    "liban": {"name": "Liban", "freedom_house_slug": "lebanon", "world_bank_code": "LBN", "wb_url_code": "LB", "undp_code": "LBN"},
    "madagascar": {"name": "Madagascar", "freedom_house_slug": "madagascar", "world_bank_code": "MDG", "wb_url_code": "MG", "undp_code": "MDG"},
    "mali": {"name": "Mali", "freedom_house_slug": "mali", "world_bank_code": "MLI", "wb_url_code": "ML", "undp_code": "MLI"},
    "maroc": {"name": "Maroc", "freedom_house_slug": "morocco", "world_bank_code": "MAR", "wb_url_code": "MA", "undp_code": "MAR"},
    "mauritanie": {"name": "Mauritanie", "freedom_house_slug": "mauritania", "world_bank_code": "MRT", "wb_url_code": "MR", "undp_code": "MRT"},
    "mexique": {"name": "Mexique", "freedom_house_slug": "mexico", "world_bank_code": "MEX", "wb_url_code": "MX", "undp_code": "MEX"},
    "mozambique": {"name": "Mozambique", "freedom_house_slug": "mozambique", "world_bank_code": "MOZ", "wb_url_code": "MZ", "undp_code": "MOZ"},
    "niger": {"name": "Niger", "freedom_house_slug": "niger", "world_bank_code": "NER", "wb_url_code": "NE", "undp_code": "NER"},
    "nigeria": {"name": "Nigéria", "freedom_house_slug": "nigeria", "world_bank_code": "NGA", "wb_url_code": "NG", "undp_code": "NGA"},
    "pakistan": {"name": "Pakistan", "freedom_house_slug": "pakistan", "world_bank_code": "PAK", "wb_url_code": "PK", "undp_code": "PAK"},
    "perou": {"name": "Pérou", "freedom_house_slug": "peru", "world_bank_code": "PER", "wb_url_code": "PE", "undp_code": "PER"},
    "philippines": {"name": "Philippines", "freedom_house_slug": "philippines", "world_bank_code": "PHL", "wb_url_code": "PH", "undp_code": "PHL"},
    "rdc": {"name": "RDC (Congo-Kinshasa)", "freedom_house_slug": "democratic-republic-of-congo", "world_bank_code": "COD", "wb_url_code": "CD", "undp_code": "COD"},
    "rwanda": {"name": "Rwanda", "freedom_house_slug": "rwanda", "world_bank_code": "RWA", "wb_url_code": "RW", "undp_code": "RWA"},
    "senegal": {"name": "Sénégal", "freedom_house_slug": "senegal", "world_bank_code": "SEN", "wb_url_code": "SN", "undp_code": "SEN"},
    "somalie": {"name": "Somalie", "freedom_house_slug": "somalia", "world_bank_code": "SOM", "wb_url_code": "SO", "undp_code": "SOM"},
    "soudan": {"name": "Soudan", "freedom_house_slug": "sudan", "world_bank_code": "SDN", "wb_url_code": "SD", "undp_code": "SDN"},
    "tanzanie": {"name": "Tanzanie", "freedom_house_slug": "tanzania", "world_bank_code": "TZA", "wb_url_code": "TZ", "undp_code": "TZA"},
    "tchad": {"name": "Tchad", "freedom_house_slug": "chad", "world_bank_code": "TCD", "wb_url_code": "TD", "undp_code": "TCD"},
    "tunisie": {"name": "Tunisie", "freedom_house_slug": "tunisia", "world_bank_code": "TUN", "wb_url_code": "TN", "undp_code": "TUN"},
    "turquie": {"name": "Turquie", "freedom_house_slug": "turkey", "world_bank_code": "TUR", "wb_url_code": "TR", "undp_code": "TUR"},
    "ukraine": {"name": "Ukraine", "freedom_house_slug": "ukraine", "world_bank_code": "UKR", "wb_url_code": "UA", "undp_code": "UKR"},
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
# Système de coloration intelligente
# ─────────────────────────────────────────────

def get_color_badge(label, value, unit):
    """Retourne la classe CSS du badge selon la logique de l'indicateur."""
    if value in ["N/D", "—", "À compléter", "Non disponible", "Indisponible", None, ""]:
        return "badge-grey"

    label_lower = label.lower()
    val_str = str(value).strip()

    # ── Freedom House statut
    if "statut" in label_lower and "freedom" in label_lower:
        if "Free" == val_str:
            return "badge-green"
        elif "Partly Free" == val_str:
            return "badge-orange"
        elif "Not Free" == val_str:
            return "badge-red"
        return "badge-grey"

    # ── Freedom House score /100
    if "freedom house" in label_lower and "score" in label_lower:
        try:
            score = int(val_str.split("/")[0])
            if score >= 70: return "badge-green"
            elif score >= 40: return "badge-orange"
            else: return "badge-red"
        except: return "badge-grey"

    # ── Droits politiques /40
    if "droits politiques" in label_lower:
        try:
            score = int(val_str.split("/")[0])
            if score >= 28: return "badge-green"
            elif score >= 15: return "badge-orange"
            else: return "badge-red"
        except: return "badge-grey"

    # ── Libertés civiles /60
    if "libertés civiles" in label_lower:
        try:
            score = int(val_str.split("/")[0])
            if score >= 42: return "badge-green"
            elif score >= 22: return "badge-orange"
            else: return "badge-red"
        except: return "badge-grey"

    # ── IDH
    if "idh" in label_lower and "valeur" in label_lower:
        try:
            v = float(val_str)
            if v >= 0.800: return "badge-green"
            elif v >= 0.700: return "badge-lightgreen"
            elif v >= 0.550: return "badge-orange"
            else: return "badge-red"
        except: return "badge-grey"

    # ── WGI [-2.5 ; +2.5]
    if "wgi" in label_lower:
        try:
            v = float(val_str)
            if v >= 0.5: return "badge-green"
            elif v >= -0.3: return "badge-orange"
            else: return "badge-red"
        except: return "badge-grey"

    # ── Gini (inégalités — plus c'est bas, mieux c'est)
    if "gini" in label_lower:
        try:
            v = float(val_str)
            if v < 32: return "badge-green"
            elif v < 45: return "badge-orange"
            else: return "badge-red"
        except: return "badge-grey"

    # ── Taux de pauvreté
    if "pauvreté" in label_lower or "pauvrete" in label_lower:
        try:
            v = float(val_str.replace("%", "").replace(",", "."))
            if v < 5: return "badge-green"
            elif v < 20: return "badge-orange"
            else: return "badge-red"
        except: return "badge-grey"

    # ── PIB/habitant
    if "pib" in label_lower and "habitant" in label_lower:
        try:
            v = float(val_str.replace("$", "").replace(",", "").replace(" ", ""))
            if v > 10000: return "badge-green"
            elif v > 3000: return "badge-orange"
            else: return "badge-red"
        except: return "badge-grey"

    # ── Croissance
    if "croissance" in label_lower:
        try:
            v = float(val_str.replace("%", "").replace(",", "."))
            if v > 5: return "badge-green"
            elif v > 2: return "badge-lightgreen"
            elif v > 0: return "badge-orange"
            else: return "badge-red"
        except: return "badge-grey"

    # ── Inflation
    if "inflation" in label_lower:
        try:
            v = float(val_str.replace("%", "").replace(",", "."))
            if v < 4: return "badge-green"
            elif v < 10: return "badge-orange"
            else: return "badge-red"
        except: return "badge-grey"

    # ── Chômage des jeunes
    if "chômage" in label_lower or "chomage" in label_lower:
        try:
            v = float(val_str.replace("%", "").replace(",", "."))
            if v < 10: return "badge-green"
            elif v < 25: return "badge-orange"
            else: return "badge-red"
        except: return "badge-grey"

    # ── Taux d'emploi / scolarisation (plus c'est haut, mieux c'est)
    if any(k in label_lower for k in ["emploi", "scolarisation"]):
        try:
            v = float(val_str.replace("%", "").replace(",", "."))
            if v > 75: return "badge-green"
            elif v > 50: return "badge-orange"
            else: return "badge-red"
        except: return "badge-grey"

    # ── IDE, solde courant — informationnel
    if any(k in label_lower for k in ["ide", "solde courant", "exportations", "importations"]):
        return "badge-blue"

    # ── Statut de revenu
    if "statut de revenu" in label_lower or "région" in label_lower:
        return "badge-purple"

    # ── Défaut
    try:
        float(str(value).replace(",", ".").replace("$", "").replace("%", "").replace(" ", ""))
        return "badge-blue"
    except:
        return "badge-grey"


def get_trend_icon(label, value):
    """Icône de tendance contextuelle."""
    badge = get_color_badge(label, value, "")
    if badge == "badge-green": return "▲"
    elif badge == "badge-lightgreen": return "↗"
    elif badge == "badge-orange": return "→"
    elif badge == "badge-red": return "▼"
    return ""


# ─────────────────────────────────────────────
# Groupes thématiques
# ─────────────────────────────────────────────

# Mapping indicateur → groupe thématique
THEMATIC_GROUPS_P1 = {
    "🗳️ Régime politique & libertés": [
        "Freedom House — Score",
        "Freedom House — Statut",
        "Freedom House",
        "Droits politiques",
        "Libertés civiles",
        "EIU — Democracy Index",
    ],
    "🏛️ Gouvernance institutionnelle": [
        "WGI — Expression & responsabilité",
        "WGI — Stabilité politique & absence de violence",
        "WGI — Efficacité gouvernementale",
        "WGI — Qualité réglementaire",
        "WGI — État de droit",
        "WGI — Contrôle de la corruption",
    ],
    "💰 Développement économique & inégalités": [
        "IDH — Valeur",
        "IDH — Rang mondial",
        "IDH",
        "Statut de revenu (BM)",
        "Région BM",
        "PIB / habitant",
        "Indice de Gini",
        "Taux de pauvreté (< 2,15 $/j)",
    ],
    "👷 Marché du travail": [
        "Taux d'emploi total",
        "Chômage des jeunes (15-24 ans)",
        "Taux d'emploi des femmes",
        "Taux d'informalité",
    ],
    "📚 Capital humain & éducation": [
        "Scolarisation primaire (taux brut)",
        "Scolarisation secondaire (taux brut)",
        "Scolarisation tertiaire (taux brut)",
    ],
}

THEMATIC_GROUPS_P2 = {
    "📊 Macroéconomie & revenus": [
        "PIB nominal total",
        "PIB par habitant",
        "Croissance du PIB réel — dernière obs.",
        "Croissance moyenne PIB réel depuis 2010",
        "Croissance moyenne PIB réel — 10 dernières obs.",
        "Inflation annuelle",
    ],
    "🏗️ Structure productive": [
        "Agriculture — part du PIB",
        "Industrie — part du PIB",
        "Manufacturier — part du PIB",
        "Services — part du PIB",
        "Part secteur extractif — PIB",
        "Part du tourisme dans le PIB",
    ],
    "👥 Emploi sectoriel": [
        "Emploi agricole",
        "Emploi industriel",
        "Emploi dans les services",
    ],
    "💹 Demande intérieure & investissement": [
        "Consommation privée",
        "Consommation publique",
        "Formation brute de capital fixe",
        "Investissement privé",
        "Crédit domestique secteur privé",
    ],
    "🌍 Ouverture & financement externe": [
        "Exportations biens et services",
        "Importations biens et services",
        "Solde courant",
        "IDE entrants nets",
        "Transferts de migrants",
    ],
    "🔭 Perspectives & éléments qualitatifs": [
        "Croissance potentielle FMI",
        "Prévisions FMI (année en cours / N+1)",
        "Réformes et chocs récents",
        "Part secteur extractif — exportations",
        "Part secteur extractif — recettes pub.",
    ],
}


def group_rows(rows, groups):
    """Groupe les lignes selon le mapping thématique."""
    grouped = {g: [] for g in groups}
    other = []
    used = set()

    for label_key, group_name in [(l, g) for g, labels in groups.items() for l in labels]:
        for r in rows:
            if r["Indicateur"] == label_key and r["Indicateur"] not in used:
                grouped[group_name].append(r)
                used.add(r["Indicateur"])

    for r in rows:
        if r["Indicateur"] not in used:
            other.append(r)

    if other:
        grouped["📎 Autres indicateurs"] = other

    return {k: v for k, v in grouped.items() if v}


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
        "User-Agent": "Mozilla/5.0",
        "Accept": "*/*",
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
    rows = []
    income_code = wb_info.get("income_code", "") if wb_info else ""
    income_label = INCOME_LABELS.get(income_code, wb_info.get("income_label", "N/D") if wb_info else "N/D")
    region = wb_info.get("region", "N/D") if wb_info else "N/D"

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

    if hdi.get("value") is not None:
        rows.append(ind("IDH — Valeur", f"{hdi['value']:.3f}", None, hdi["year"], "PNUD / Human Development Report", hdi["source_url"]))
        if hdi.get("rank"):
            rows.append(ind("IDH — Rang mondial", str(hdi["rank"]), None, hdi["year"], "PNUD / Human Development Report", hdi["source_url"]))
    else:
        rows.append(ind("IDH", "N/D", None, None, "PNUD / Human Development Report", hdi.get("source_url", ""), hdi.get("error", "")))

    rows.append(ind("Statut de revenu (BM)", income_label, None, None, "Banque mondiale", wb_url_base))
    rows.append(ind("Région BM", region, None, None, "Banque mondiale", wb_url_base))

    gdp_val, gdp_year = fetch_wb_latest(wb_code, "NY.GDP.PCAP.CD")
    if gdp_val:
        rows.append(ind("PIB / habitant", f"${gdp_val:,.0f}", "USD", gdp_year, "Banque mondiale", wb_url_base))

    gini_val, gini_year = fetch_wb_latest(wb_code, "SI.POV.GINI")
    rows.append(ind("Indice de Gini", f"{gini_val:.1f}" if gini_val else "N/D", None, gini_year,
                    "Banque mondiale", wb_url_base, None if gini_val else "Enquêtes disponibles par intermittence"))

    poverty_val, poverty_year = fetch_wb_latest(wb_code, "SI.POV.DDAY")
    rows.append(ind("Taux de pauvreté (< 2,15 $/j)", f"{poverty_val:.1f}" if poverty_val else "N/D", "%", poverty_year,
                    "Banque mondiale", wb_url_base, None if poverty_val else "Absent pour PRITS/PRE"))

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
    rows = []
    wb_url = "https://data.worldbank.org/indicator/"

    indicators = [
        ("NY.GDP.MKTP.CD", "PIB nominal total", "USD courants"),
        ("NY.GDP.PCAP.CD", "PIB par habitant", "USD courants"),
        ("NY.GDP.MKTP.KD.ZG", "Croissance du PIB réel — dernière obs.", "%"),
        ("FP.CPI.TOTL.ZG", "Inflation annuelle", "%"),
        ("NV.AGR.TOTL.ZS", "Agriculture — part du PIB", "% du PIB"),
        ("NV.IND.TOTL.ZS", "Industrie — part du PIB", "% du PIB"),
        ("NV.IND.MANF.ZS", "Manufacturier — part du PIB", "% du PIB"),
        ("NV.SRV.TOTL.ZS", "Services — part du PIB", "% du PIB"),
        ("SL.AGR.EMPL.ZS", "Emploi agricole", "% emploi total"),
        ("SL.IND.EMPL.ZS", "Emploi industriel", "% emploi total"),
        ("SL.SRV.EMPL.ZS", "Emploi dans les services", "% emploi total"),
        ("NE.CON.PRVT.ZS", "Consommation privée", "% du PIB"),
        ("NE.CON.GOVT.ZS", "Consommation publique", "% du PIB"),
        ("NE.GDI.FTOT.ZS", "Formation brute de capital fixe", "% du PIB"),
        ("NE.GDI.FPRV.ZS", "Investissement privé", "% du PIB"),
        ("BX.KLT.DINV.WD.GD.ZS", "IDE entrants nets", "% du PIB"),
        ("BX.TRF.PWKR.DT.GD.ZS", "Transferts de migrants", "% du PIB"),
        ("FS.AST.PRVT.GD.ZS", "Crédit domestique secteur privé", "% du PIB"),
        ("NE.EXP.GNFS.ZS", "Exportations biens et services", "% du PIB"),
        ("NE.IMP.GNFS.ZS", "Importations biens et services", "% du PIB"),
        ("BN.CAB.XOKA.GD.ZS", "Solde courant", "% du PIB"),
    ]

    growth_hist = []
    for code, label, unit in indicators:
        hist = fetch_wb_history_values(wb_code, code, n_years=25)
        val, year = latest_from_history(hist)
        v = f"{val:,.1f}" if isinstance(val, (int, float)) else "N/D"
        rows.append(ind(label, v, unit, year, "Banque mondiale", f"{wb_url}{code}"))
        if code == "NY.GDP.MKTP.KD.ZG":
            growth_hist = hist

    avg_2010 = average_since(growth_hist, 2010)
    avg_10y = average_last_n(growth_hist, 10)

    years_since_2010 = [x["year"] for x in growth_hist if x["year"] >= 2010]
    period_2010 = f"{min(years_since_2010)}-{max(years_since_2010)}" if years_since_2010 else None

    years_10y = [x["year"] for x in growth_hist[-10:]]
    period_10y = f"{years_10y[0]}-{years_10y[-1]}" if len(years_10y) >= 2 else None

    rows.append(ind(
        "Croissance moyenne PIB réel depuis 2010",
        f"{avg_2010:.1f}" if avg_2010 is not None else "N/D",
        "%", period_2010, "Calcul interne — Banque mondiale",
        f"{wb_url}NY.GDP.MKTP.KD.ZG",
        None if avg_2010 is not None else "Série insuffisante"
    ))
    rows.append(ind(
        "Croissance moyenne PIB réel — 10 dernières obs.",
        f"{avg_10y:.1f}" if avg_10y is not None else "N/D",
        "%", period_10y, "Calcul interne — Banque mondiale",
        f"{wb_url}NY.GDP.MKTP.KD.ZG",
        None if avg_10y is not None else "Série insuffisante"
    ))

    manual_guides = [
        ("Part secteur extractif — PIB", "Comptes nationaux détaillés / Article IV FMI / EITI"),
        ("Part secteur extractif — exportations", "UN Comtrade / OEC / Article IV FMI"),
        ("Part secteur extractif — recettes pub.", "Article IV FMI / DSA FMI / budget national"),
        ("Part du tourisme dans le PIB", "WTTC / UN Tourism / Article IV FMI"),
        ("Croissance potentielle FMI", "Article IV FMI — texte ou annexes"),
        ("Prévisions FMI (année en cours / N+1)", "Article IV FMI / WEO"),
        ("Réformes et chocs récents", "Article IV FMI / Banque mondiale MPO"),
    ]
    for label, note in manual_guides:
        rows.append(ind(label, "À compléter", None, None, "Source sectorielle", "", note))

    return rows


# ─────────────────────────────────────────────
# Prompts IA
# ─────────────────────────────────────────────

def build_prompt_pillar1(country_name, rows):
    lines = [
        f"FICHE PAYS — {country_name.upper()}",
        "PILIER 1 : ENVIRONNEMENT POLITIQUE ET SOCIOÉCONOMIQUE",
        "=" * 70, "",
        "DONNÉES COLLECTÉES", "-" * 40,
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
        "", "=" * 70, "CONSIGNE DE RÉDACTION", "-" * 40, "",
        "À partir des données ci-dessus, rédige une analyse structurée du Pilier 1.",
        "", "STRUCTURE ATTENDUE :",
        "", "1. RÉGIME POLITIQUE ET LIBERTÉS",
        "2. GOUVERNANCE INSTITUTIONNELLE",
        "3. DÉVELOPPEMENT HUMAIN ET INÉGALITÉS",
        "4. MARCHÉ DU TRAVAIL",
        "5. CAPITAL HUMAIN (ÉDUCATION)",
        "", "RÈGLES :",
        "- Ne pas inventer de chiffres. Utiliser uniquement les données fournies.",
        "- Si une donnée est manquante ou ancienne, le signaler explicitement.",
        "- Style analytique, institutionnel, sans bullet points.",
        "- Environ 400-500 mots.",
    ]
    return "\n".join(lines)


def build_prompt_pillar2(country_name, rows):
    lines = [
        f"FICHE PAYS — {country_name.upper()}",
        "PILIER 2 : MODÈLE ÉCONOMIQUE ET RÉGIME DE CROISSANCE",
        "=" * 70, "",
        "DONNÉES COLLECTÉES", "-" * 40,
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
        "", "=" * 70, "CONSIGNE DE RÉDACTION", "-" * 40, "",
        "À partir des données ci-dessus, rédige une analyse structurée du Pilier 2.",
        "", "PARTIE 1 — MODÈLE ÉCONOMIQUE",
        "PARTIE 2 — RÉGIME DE CROISSANCE",
        "", "RÈGLES :",
        "- Ne pas inventer de chiffres.",
        "- Style analytique, institutionnel, dense, sans bullet points.",
        "- Environ 500-600 mots.",
    ]
    return "\n".join(lines)


# ─────────────────────────────────────────────
# Affichage thématique enrichi
# ─────────────────────────────────────────────

THEME_COLORS = {
    "🗳️ Régime politique & libertés": "#e8001b",
    "🏛️ Gouvernance institutionnelle": "#003189",
    "💰 Développement économique & inégalités": "#1a7a45",
    "👷 Marché du travail": "#c17000",
    "📚 Capital humain & éducation": "#6b21a8",
    "📊 Macroéconomie & revenus": "#003189",
    "🏗️ Structure productive": "#c17000",
    "👥 Emploi sectoriel": "#1a7a45",
    "💹 Demande intérieure & investissement": "#0e7a8a",
    "🌍 Ouverture & financement externe": "#4a5568",
    "🔭 Perspectives & éléments qualitatifs": "#6b21a8",
    "📎 Autres indicateurs": "#555",
}


def render_indicator_card(row):
    """Génère le HTML d'une ligne indicateur."""
    label = row.get("Indicateur", "")
    value = str(row.get("Valeur", "N/D"))
    unit = row.get("Unité", "")
    year = row.get("Année", "—")
    source = row.get("Source", "")
    url = row.get("URL source", "")
    note = row.get("Note", "")

    badge_class = get_color_badge(label, value, unit)
    unit_str = f" {unit}" if unit else ""
    year_str = f"({year})" if year and year != "—" else ""

    source_html = f'<a href="{url}" target="_blank" style="color:#aaa;text-decoration:none;">🔗 {source}</a>' if url else f'<span style="color:#aaa;">{source}</span>'
    note_html = f'<span class="indicator-note">⚠️ {note}</span>' if note else ""

    return f"""
    <div class="indicator-row">
        <span class="indicator-label">{label}</span>
        <span class="indicator-value {badge_class}">{value}{unit_str}</span>
        <span class="indicator-meta">{year_str}</span>
        <span class="indicator-source">{source_html}</span>
        {note_html}
    </div>
    """


def render_theme_group(theme_name, rows, color):
    """Génère le HTML d'un groupe thématique."""
    cards_html = "".join(render_indicator_card(r) for r in rows)
    return f"""
    <div class="theme-card" style="border-left-color: {color};">
        <div class="theme-card-title" style="color: {color};">{theme_name}</div>
        {cards_html}
    </div>
    """


def compute_summary(rows, pillar_num):
    """Calcule des métriques résumé pour affichage en haut du pilier."""
    total = len(rows)
    available = sum(1 for r in rows if str(r.get("Valeur", "N/D")) not in ["N/D", "—", "À compléter", "Non disponible", "Indisponible"])
    alerts = sum(1 for r in rows if r.get("Note", ""))
    green = sum(1 for r in rows if get_color_badge(r["Indicateur"], str(r.get("Valeur", "")), r.get("Unité", "")) in ["badge-green", "badge-lightgreen"])
    red = sum(1 for r in rows if get_color_badge(r["Indicateur"], str(r.get("Valeur", "")), r.get("Unité", "")) == "badge-red")
    return total, available, green, red, alerts


def show_legend():
    st.markdown("""
    <div class="legend-bar">
        <div class="legend-item"><div class="legend-dot" style="background:#1a7a45;"></div> Favorable</div>
        <div class="legend-item"><div class="legend-dot" style="background:#2e8b57;"></div> Plutôt favorable</div>
        <div class="legend-item"><div class="legend-dot" style="background:#c17000;"></div> Intermédiaire</div>
        <div class="legend-item"><div class="legend-dot" style="background:#c0392b;"></div> Défavorable</div>
        <div class="legend-item"><div class="legend-dot" style="background:#003189;"></div> Informatif</div>
        <div class="legend-item"><div class="legend-dot" style="background:#6b21a8;"></div> Qualitatif</div>
        <div class="legend-item"><div class="legend-dot" style="background:#888;"></div> Non disponible</div>
        <div class="legend-item" style="margin-left:auto;color:#e07c00;">⚠️ = donnée ancienne ou manquante</div>
    </div>
    """, unsafe_allow_html=True)


def show_pillar_v2(pillar_title, pillar_subtitle, rows, groups_map):
    """Affiche un pilier avec groupes thématiques, métriques et onglets."""

    # ── Header
    st.markdown(f"""
    <div class="section-header">
        <h3>{pillar_title}</h3>
    </div>
    <div class="section-subtitle">{pillar_subtitle}</div>
    """, unsafe_allow_html=True)

    # ── Métriques résumé
    total, available, green, red, alerts = compute_summary(rows, 1)
    coverage_pct = int(100 * available / total) if total > 0 else 0

    st.markdown(f"""
    <div class="summary-grid">
        <div class="summary-card" style="border-top-color:#003189;">
            <div class="s-label">Indicateurs</div>
            <div class="s-value">{total}</div>
            <div class="s-sub">collectés</div>
        </div>
        <div class="summary-card" style="border-top-color:#1a7a45;">
            <div class="s-label">Couverture</div>
            <div class="s-value">{coverage_pct}%</div>
            <div class="s-sub">{available} / {total} disponibles</div>
        </div>
        <div class="summary-card" style="border-top-color:#1a7a45;">
            <div class="s-label">Signaux positifs</div>
            <div class="s-value" style="color:#1a7a45;">{green}</div>
            <div class="s-sub">indicateurs favorables</div>
        </div>
        <div class="summary-card" style="border-top-color:#c0392b;">
            <div class="s-label">Signaux d'alerte</div>
            <div class="s-value" style="color:#c0392b;">{red}</div>
            <div class="s-sub">indicateurs défavorables</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Légende
    show_legend()

    # ── Groupes thématiques
    grouped = group_rows(rows, groups_map)

    tab_labels = list(grouped.keys())

    if len(tab_labels) <= 1:
        for theme, theme_rows in grouped.items():
            color = THEME_COLORS.get(theme, "#003189")
            st.markdown(render_theme_group(theme, theme_rows, color), unsafe_allow_html=True)
    else:
        tabs = st.tabs(tab_labels)
        for tab, (theme, theme_rows) in zip(tabs, grouped.items()):
            with tab:
                color = THEME_COLORS.get(theme, "#003189")
                st.markdown(render_theme_group(theme, theme_rows, color), unsafe_allow_html=True)

    # ── Vue tableau complète (expandeur)
    with st.expander("📋 Voir tous les indicateurs en tableau", expanded=False):
        df = pd.DataFrame(rows)
        DISPLAY_COLS = ["Indicateur", "Valeur", "Unité", "Année", "Source", "URL source", "Note"]
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


def show_prompt(title, prompt_text):
    st.markdown(f'<div class="prompt-title">🤖 {title}</div>', unsafe_allow_html=True)
    st.text_area(
        label="",
        value=prompt_text,
        height=340,
        help="Sélectionnez tout (Ctrl+A) puis copiez (Ctrl+C) pour coller dans une IA."
    )


# ─────────────────────────────────────────────
# Interface principale
# ─────────────────────────────────────────────

st.markdown("""
<div class="afd-header">
    <h1>🌍 Outil de collecte de données — DER</h1>
    <p>Collecte automatique · Sources officielles · Indicateurs classifiés · Codes couleur · Prompt IA par pilier</p>
</div>
""", unsafe_allow_html=True)

col_sel, col_btn = st.columns([3, 1])
with col_sel:
    country_options = dict(sorted({info["name"]: key for key, info in COUNTRY_MAPPING.items()}.items()))
    selected_name = st.selectbox("🌐 Sélectionner un pays", options=list(country_options.keys()))
with col_btn:
    st.write("")
    st.write("")
    run = st.button("Récupérer les données →")

selected_key = country_options[selected_name]
country_info = COUNTRY_MAPPING[selected_key]
wb_code = country_info["world_bank_code"]
wb_url_base = f"https://data.worldbank.org/country/{country_info['wb_url_code']}"

if run:
    with st.spinner("⏳ Collecte en cours — Freedom House, Banque mondiale, PNUD..."):
        fh = fetch_freedom_house(country_info["freedom_house_slug"])
        wb_info = fetch_wb_country_info(wb_code)
        hdi = fetch_undp_hdi(country_info["name"])

    with st.spinner("⚙️ Construction Pilier 1..."):
        pillar1_rows = build_pillar1(wb_code, wb_url_base, fh, wb_info, hdi)

    with st.spinner("⚙️ Construction Pilier 2..."):
        pillar2_rows = build_pillar2(wb_code)

    # ── PILIER 1
    show_pillar_v2(
        "📌 Pilier 1 — Environnement politique et socioéconomique",
        "Freedom House · IDH · Gouvernance WGI · Emploi · Pauvreté · Éducation",
        pillar1_rows,
        THEMATIC_GROUPS_P1
    )
    prompt1 = build_prompt_pillar1(selected_name, pillar1_rows)
    show_prompt("Prompt IA — Pilier 1", prompt1)

    st.markdown("---")

    # ── PILIER 2
    show_pillar_v2(
        "📈 Pilier 2 — Modèle économique et régime de croissance",
        "Structure productive · Emploi sectoriel · Demande · Financement · Ouverture · Croissance",
        pillar2_rows,
        THEMATIC_GROUPS_P2
    )
    prompt2 = build_prompt_pillar2(selected_name, pillar2_rows)
    show_prompt("Prompt IA — Pilier 2", prompt2)

    st.markdown(
        f'<p class="footer-note">📅 Données collectées le {datetime.now().strftime("%d/%m/%Y à %H:%M")} '
        f'· Sources officielles vérifiables · AFD — Direction des Études et Recherches</p>',
        unsafe_allow_html=True
    )
