import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from datetime import datetime
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor, as_completed
import plotly.graph_objects as go
import plotly.express as px
from fpdf import FPDF

st.set_page_config(
    page_title="Dashboard pays - DER",
    page_icon="🌍",
    layout="wide"
)

CURRENT_YEAR = datetime.now().year
OLD_DATA_THRESHOLD = 5

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

* {
    font-family: "Inter", sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
}

/* HEADER */
.main-header {
    background: linear-gradient(135deg, #003189 0%, #0047bb 100%);
    padding: 32px 40px;
    border-radius: 16px;
    margin-bottom: 32px;
    box-shadow: 0 8px 24px rgba(0,49,137,0.15);
}
.main-header h1 {
    color: white !important;
    font-size: 28px;
    font-weight: 700;
    margin: 0 0 8px 0;
}
.main-header p {
    color: #93b4e8;
    font-size: 14px;
    margin: 0;
}

/* COUNTRY CARD */
.country-card {
    background: white;
    padding: 24px;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    margin-bottom: 32px;
}
.country-name {
    font-size: 32px;
    font-weight: 700;
    color: #003189;
    margin-bottom: 12px;
}
.country-meta {
    display: flex;
    gap: 24px;
    flex-wrap: wrap;
    font-size: 14px;
    color: #64748b;
}
.country-meta-item {
    display: flex;
    align-items: center;
    gap: 8px;
}
.country-meta-label {
    font-weight: 600;
    color: #475569;
}

/* PILLAR */
.pillar-divider {
    background: white;
    padding: 20px 32px;
    border-radius: 12px;
    margin: 48px 0 32px 0;
    border-left: 6px solid #003189;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}
.pillar-title {
    font-size: 24px;
    font-weight: 700;
    color: #003189;
    margin: 0 0 8px 0;
}
.pillar-subtitle {
    font-size: 14px;
    color: #64748b;
    margin: 0;
}
.pillar-stats {
    display: flex;
    gap: 32px;
    margin-top: 16px;
    font-size: 13px;
}
.pillar-stat {
    display: flex;
    align-items: center;
    gap: 8px;
}
.pillar-stat-val {
    font-weight: 700;
    font-size: 18px;
}

/* SECTION */
.section-header {
    font-size: 18px;
    font-weight: 700;
    color: #1e293b;
    margin: 32px 0 16px 0;
    padding-bottom: 8px;
    border-bottom: 2px solid #e2e8f0;
}

/* KPI CARDS */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 16px;
    margin-bottom: 32px;
}
.kpi-card {
    background: white;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    border-top: 4px solid #e2e8f0;
    position: relative;
}
.kpi-card.green { border-top-color: #10b981; }
.kpi-card.orange { border-top-color: #f59e0b; }
.kpi-card.red { border-top-color: #ef4444; }
.kpi-card.grey { border-top-color: #94a3b8; }

.kpi-label {
    font-size: 12px;
    color: #64748b;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 12px;
}
.kpi-value {
    font-size: 32px;
    font-weight: 700;
    line-height: 1;
    margin-bottom: 8px;
}
.kpi-value.green { color: #10b981; }
.kpi-value.orange { color: #f59e0b; }
.kpi-value.red { color: #ef4444; }
.kpi-value.grey { color: #94a3b8; }

.kpi-unit {
    font-size: 13px;
    color: #94a3b8;
    font-weight: 500;
}
.kpi-meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px solid #f1f5f9;
    font-size: 11px;
    color: #94a3b8;
}
.kpi-trend {
    font-weight: 700;
    font-size: 14px;
}
.kpi-comparison {
    font-size: 11px;
    color: #64748b;
    margin-top: 8px;
    padding: 6px 10px;
    background: #f8fafc;
    border-radius: 6px;
}

/* GAUGE */
.gauge-container {
    background: white;
    padding: 16px 20px;
    border-radius: 10px;
    margin-bottom: 12px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.gauge-label {
    font-size: 13px;
    font-weight: 600;
    color: #475569;
    margin-bottom: 8px;
}
.gauge-bar {
    position: relative;
    height: 32px;
    background: #f1f5f9;
    border-radius: 8px;
    overflow: hidden;
}
.gauge-fill {
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: flex-end;
    padding-right: 12px;
    font-weight: 700;
    font-size: 13px;
    color: white;
    transition: width 0.6s ease;
}
.gauge-fill.green { background: linear-gradient(90deg, #10b981, #059669); }
.gauge-fill.orange { background: linear-gradient(90deg, #f59e0b, #d97706); }
.gauge-fill.red { background: linear-gradient(90deg, #ef4444, #dc2626); }
.gauge-fill.grey { background: linear-gradient(90deg, #94a3b8, #64748b); }

.gauge-compare {
    position: absolute;
    top: 0;
    height: 100%;
    width: 2px;
    background: #1e293b;
    opacity: 0.4;
}
.gauge-compare::after {
    content: attr(data-label);
    position: absolute;
    top: -20px;
    left: 50%;
    transform: translateX(-50%);
    font-size: 10px;
    color: #64748b;
    white-space: nowrap;
}

/* TOGGLE */
.toggle-container {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 24px;
    padding: 12px 16px;
    background: white;
    border-radius: 10px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.toggle-label {
    font-size: 13px;
    font-weight: 600;
    color: #475569;
}

/* PROMPT */
.prompt-box {
    background: white;
    padding: 24px;
    border-radius: 12px;
    margin: 32px 0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}
.prompt-title {
    font-size: 16px;
    font-weight: 700;
    color: #003189;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.prompt-text {
    background: #f8fafc;
    padding: 16px;
    border-radius: 8px;
    font-family: 'Courier New', monospace;
    font-size: 12px;
    color: #1e293b;
    max-height: 400px;
    overflow-y: auto;
    white-space: pre-wrap;
    border: 1px solid #e2e8f0;
}

/* BUTTONS */
.export-buttons {
    display: flex;
    gap: 16px;
    justify-content: center;
    margin: 48px 0;
}
.export-btn {
    background: linear-gradient(135deg, #003189, #0047bb);
    color: white;
    padding: 14px 32px;
    border-radius: 10px;
    font-weight: 600;
    font-size: 14px;
    border: none;
    cursor: pointer;
    box-shadow: 0 4px 12px rgba(0,49,137,0.2);
    transition: all 0.3s;
}
.export-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(0,49,137,0.3);
}

/* FOOTER */
.footer {
    text-align: center;
    padding: 24px;
    color: #94a3b8;
    font-size: 12px;
    border-top: 1px solid #e2e8f0;
    margin-top: 48px;
}

/* CHART CONTAINER */
.chart-container {
    background: white;
    padding: 24px;
    border-radius: 12px;
    margin-bottom: 24px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}
.chart-title {
    font-size: 16px;
    font-weight: 700;
    color: #1e293b;
    margin-bottom: 16px;
}

/* LOADING */
.loading {
    text-align: center;
    padding: 48px;
    color: #64748b;
}
</style>
""", unsafe_allow_html=True)

# Pays
COUNTRY_MAPPING = {
    "afghanistan": {"name": "Afghanistan", "freedom_house_slug": "afghanistan", "world_bank_code": "AFG", "wb_url_code": "AF", "flag": "🇦🇫"},
    "afrique_du_sud": {"name": "Afrique du Sud", "freedom_house_slug": "south-africa", "world_bank_code": "ZAF", "wb_url_code": "ZA", "flag": "🇿🇦"},
    "algerie": {"name": "Algérie", "freedom_house_slug": "algeria", "world_bank_code": "DZA", "wb_url_code": "DZ", "flag": "🇩🇿"},
    "benin": {"name": "Bénin", "freedom_house_slug": "benin", "world_bank_code": "BEN", "wb_url_code": "BJ", "flag": "🇧🇯"},
    "burkina_faso": {"name": "Burkina Faso", "freedom_house_slug": "burkina-faso", "world_bank_code": "BFA", "wb_url_code": "BF", "flag": "🇧🇫"},
    "cameroun": {"name": "Cameroun", "freedom_house_slug": "cameroon", "world_bank_code": "CMR", "wb_url_code": "CM", "flag": "🇨🇲"},
    "cote_ivoire": {"name": "Côte d'Ivoire", "freedom_house_slug": "cote-divoire", "world_bank_code": "CIV", "wb_url_code": "CI", "flag": "🇨🇮"},
    "egypte": {"name": "Égypte", "freedom_house_slug": "egypt", "world_bank_code": "EGY", "wb_url_code": "EG", "flag": "🇪🇬"},
    "ethiopie": {"name": "Éthiopie", "freedom_house_slug": "ethiopia", "world_bank_code": "ETH", "wb_url_code": "ET", "flag": "🇪🇹"},
    "ghana": {"name": "Ghana", "freedom_house_slug": "ghana", "world_bank_code": "GHA", "wb_url_code": "GH", "flag": "🇬🇭"},
    "kenya": {"name": "Kenya", "freedom_house_slug": "kenya", "world_bank_code": "KEN", "wb_url_code": "KE", "flag": "🇰🇪"},
    "madagascar": {"name": "Madagascar", "freedom_house_slug": "madagascar", "world_bank_code": "MDG", "wb_url_code": "MG", "flag": "🇲🇬"},
    "mali": {"name": "Mali", "freedom_house_slug": "mali", "world_bank_code": "MLI", "wb_url_code": "ML", "flag": "🇲🇱"},
    "maroc": {"name": "Maroc", "freedom_house_slug": "morocco", "world_bank_code": "MAR", "wb_url_code": "MA", "flag": "🇲🇦"},
    "niger": {"name": "Niger", "freedom_house_slug": "niger", "world_bank_code": "NER", "wb_url_code": "NE", "flag": "🇳🇪"},
    "nigeria": {"name": "Nigéria", "freedom_house_slug": "nigeria", "world_bank_code": "NGA", "wb_url_code": "NG", "flag": "🇳🇬"},
    "senegal": {"name": "Sénégal", "freedom_house_slug": "senegal", "world_bank_code": "SEN", "wb_url_code": "SN", "flag": "🇸🇳"},
    "tanzanie": {"name": "Tanzanie", "freedom_house_slug": "tanzania", "world_bank_code": "TZA", "wb_url_code": "TZ", "flag": "🇹🇿"},
    "tchad": {"name": "Tchad", "freedom_house_slug": "chad", "world_bank_code": "TCD", "wb_url_code": "TD", "flag": "🇹🇩"},
    "tunisie": {"name": "Tunisie", "freedom_house_slug": "tunisia", "world_bank_code": "TUN", "wb_url_code": "TN", "flag": "🇹🇳"},
}

INCOME_LABELS = {
    "LIC": "Faible revenu",
    "LMC": "Revenu intermédiaire inférieur",
    "UMC": "Revenu intermédiaire supérieur",
    "HIC": "Revenu élevé",
    "INX": "Non classifié",
}

# Moyennes régionales (exemples - à ajuster)
REGIONAL_AVERAGES = {
    "Sub-Saharan Africa": {
        "gdp_growth": 3.5,
        "inflation": 8.2,
        "unemployment": 7.5,
        "hdi": 0.547,
        "gini": 43.5,
        "poverty": 35.2,
        "primary_school": 95.0,
        "secondary_school": 48.0,
        "tertiary_school": 9.0,
        "agriculture_gdp": 16.5,
        "industry_gdp": 26.8,
        "services_gdp": 56.7,
        "agriculture_emp": 52.0,
        "industry_emp": 11.0,
        "services_emp": 37.0,
        "consumption_private": 68.0,
        "consumption_public": 14.0,
        "investment": 22.0,
        "credit_private": 35.0,
        "exports": 28.0,
        "imports": 32.0,
        "fdi": 2.5,
        "remittances": 3.2,
    },
    "Middle East & North Africa": {
        "gdp_growth": 2.8,
        "inflation": 12.5,
        "unemployment": 11.2,
        "hdi": 0.703,
        "gini": 37.5,
        "poverty": 5.5,
        "primary_school": 98.0,
        "secondary_school": 78.0,
        "tertiary_school": 35.0,
        "agriculture_gdp": 8.5,
        "industry_gdp": 38.2,
        "services_gdp": 53.3,
        "agriculture_emp": 25.0,
        "industry_emp": 28.0,
        "services_emp": 47.0,
        "consumption_private": 58.0,
        "consumption_public": 18.0,
        "investment": 26.0,
        "credit_private": 55.0,
        "exports": 35.0,
        "imports": 38.0,
        "fdi": 1.8,
        "remittances": 4.5,
    },
}

# Utilitaires
def flag_old(year):
    if year is None:
        return ""
    try:
        age = CURRENT_YEAR - int(year)
        if age > OLD_DATA_THRESHOLD:
            return f"Donnée ancienne ({age} ans)"
    except:
        pass
    return ""

def get_signal(value, thresholds):
    """
    thresholds = {"high": X, "low": Y, "reverse": bool}
    reverse=True : valeur basse = bon (ex: inflation, chômage)
    """
    if value is None or str(value).strip() in ["N/D", "—", "À compléter", "Non disponible", "Indisponible", ""]:
        return "grey"
    
    try:
        v = float(str(value).replace("$", "").replace(",", "").replace("%", ""))
        high = thresholds.get("high")
        low = thresholds.get("low")
        reverse = thresholds.get("reverse", False)
        
        if reverse:
            if v < low: return "green"
            if v < high: return "orange"
            return "red"
        else:
            if v >= high: return "green"
            if v >= low: return "orange"
            return "red"
    except:
        return "grey"

def get_trend_icon(value, prev_value, reverse=False):
    """Retourne ↑ ↓ → selon évolution"""
    if value is None or prev_value is None:
        return "→"
    try:
        v = float(str(value).replace("$", "").replace(",", "").replace("%", ""))
        pv = float(str(prev_value).replace("$", "").replace(",", "").replace("%", ""))
        diff = v - pv
        
        if abs(diff) < 0.1:
            return "→"
        
        if reverse:
            return "↓" if diff > 0 else "↑"
        else:
            return "↑" if diff > 0 else "↓"
    except:
        return "→"

# Collecte données
def fetch_freedom_house(slug, year=2026):
    url = f"https://freedomhouse.org/country/{slug}/freedom-world/{year}"
    try:
        r = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        text = re.sub(r"\s+", " ", BeautifulSoup(r.text, "html.parser").get_text(" ", strip=True))
        res = {"status": None, "score": None, "pr_score": None, "cl_score": None, "year": year, "url": url, "error": None}
        
        if re.search(r"\bNot Free\b", text):
            res["status"] = "Not Free"
        elif re.search(r"\bPartly Free\b", text):
            res["status"] = "Partly Free"
        elif re.search(r"\bFree\b", text):
            res["status"] = "Free"
        
        m = re.search(r"(?:Total Score and Status|score)\s+(\d{1,3})\s*/?\s*100", text, re.I)
        if m:
            res["score"] = int(m.group(1))
        
        pr = re.search(r"Political Rights\s+(\d{1,2})\s*/?\s*40", text, re.I)
        if pr:
            res["pr_score"] = int(pr.group(1))
        
        cl = re.search(r"Civil Liberties\s+(\d{1,2})\s*/?\s*60", text, re.I)
        if cl:
            res["cl_score"] = int(cl.group(1))
        
        return res
    except Exception as e:
        return {"error": str(e), "url": url}

def _wb_get(url):
    try:
        r = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        return r.json()
    except:
        return None

def fetch_wb_indicator(country_code, indicator_code):
    url = f"https://api.worldbank.org/v2/country/{country_code}/indicator/{indicator_code}?format=json&per_page=20&mrv=10"
    data = _wb_get(url)
    if not isinstance(data, list) or len(data) < 2 or not data[1]:
        return None, None
    for row in data[1]:
        if row.get("value") is not None:
            return row["value"], int(row["date"])
    return None, None

def fetch_wb_history(country_code, indicator_code, n=25):
    url = f"https://api.worldbank.org/v2/country/{country_code}/indicator/{indicator_code}?format=json&per_page=200"
    data = _wb_get(url)
    if not isinstance(data, list) or len(data) < 2 or not data[1]:
        return []
    rows = []
    for obs in data[1]:
        if obs.get("value") is not None:
            try:
                rows.append({"year": int(obs["date"]), "value": float(obs["value"])})
            except:
                pass
    rows.sort(key=lambda x: x["year"])
    return rows[-n:]

def fetch_wb_country_info(cc):
    data = _wb_get(f"https://api.worldbank.org/v2/country/{cc}?format=json")
    if not isinstance(data, list) or len(data) < 2 or not data[1]:
        return None
    c = data[1][0]
    return {
        "income_code": c.get("incomeLevel", {}).get("id", ""),
        "income_label": c.get("incomeLevel", {}).get("value", ""),
        "region": c.get("region", {}).get("value", ""),
    }

def latest(hist):
    if not hist:
        return None, None
    return hist[-1]["value"], hist[-1]["year"]

def avg_since(hist, y0=2010):
    v = [x["value"] for x in hist if x.get("year", 0) >= y0]
    return sum(v) / len(v) if v else None

def avg_last(hist, n=10):
    v = [x["value"] for x in hist[-n:]]
    return sum(v) / len(v) if v else None

@st.cache_data(ttl=86400, show_spinner=False)
def load_hdi_table():
    url = "https://hdr.undp.org/sites/default/files/2025_HDR/HDR25_Statistical_Annex_HDI_Table.xlsx"
    try:
        r = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://hdr.undp.org"})
        r.raise_for_status()
        df = pd.read_excel(BytesIO(r.content), header=None, engine="openpyxl")
        rows = []
        for _, row in df.iterrows():
            v = list(row.dropna())
            if len(v) < 3:
                continue
            try:
                ri, hv = int(v[0]), float(v[2])
                if 0 < hv <= 1:
                    rows.append({"rank": ri, "country": str(v[1]).strip(), "hdi": hv})
            except:
                pass
        return pd.DataFrame(rows)
    except:
        return pd.DataFrame()

def fetch_hdi(name):
    src = "https://hdr.undp.org/data-center/human-development-index"
    aliases = {
        "RDC (Congo-Kinshasa)": ["Congo (Democratic Republic of the)"],
        "Côte d'Ivoire": ["Côte d'Ivoire", "Cote d'Ivoire"],
        "Tanzanie": ["Tanzania (United Republic of)"],
    }
    try:
        df = load_hdi_table()
        if df.empty:
            return {"value": None, "rank": None, "year": 2023, "url": src, "error": "Table vide"}
        names = [n.lower().strip() for n in [name] + aliases.get(name, [])]
        row = df[df["country"].str.lower().str.strip().isin(names)]
        if row.empty:
            return {"value": None, "rank": None, "year": 2023, "url": src, "error": f"Introuvable: {name}"}
        f = row.iloc[0]
        return {"value": float(f["hdi"]), "rank": int(f["rank"]), "year": 2023, "url": src, "error": None}
    except Exception as e:
        return {"value": None, "rank": None, "year": 2023, "url": src, "error": str(e)}

WB_CODES = {
    "NY.GDP.PCAP.CD": "PIB/hab",
    "NY.GDP.MKTP.KD.ZG": "Croissance",
    "FP.CPI.TOTL.ZG": "Inflation",
    "SI.POV.GINI": "Gini",
    "SI.POV.DDAY": "Pauvreté",
    "SL.UEM.TOTL.ZS": "Chômage",
    "VA.EST": "WGI Voice",
    "PV.EST": "WGI Stability",
    "GE.EST": "WGI Effectiveness",
    "RQ.EST": "WGI Regulatory",
    "RL.EST": "WGI Rule of Law",
    "CC.EST": "WGI Corruption",
    "SL.EMP.TOTL.SP.ZS": "Emploi total",
    "SL.UEM.1524.ZS": "Chômage jeunes",
    "SL.EMP.TOTL.SP.FE.ZS": "Emploi femmes",
    "SL.ISV.IFRM.ZS": "Informalité",
    "SE.PRM.ENRR": "Primaire",
    "SE.SEC.ENRR": "Secondaire",
    "SE.TER.ENRR": "Tertiaire",
    "NV.AGR.TOTL.ZS": "Agriculture PIB",
    "NV.IND.TOTL.ZS": "Industrie PIB",
    "NV.SRV.TOTL.ZS": "Services PIB",
    "SL.AGR.EMPL.ZS": "Agriculture emploi",
    "SL.IND.EMPL.ZS": "Industrie emploi",
    "SL.SRV.EMPL.ZS": "Services emploi",
    "NE.CON.PRVT.ZS": "Conso privée",
    "NE.CON.GOVT.ZS": "Conso publique",
    "NE.GDI.FTOT.ZS": "Investissement",
    "FS.AST.PRVT.GD.ZS": "Crédit privé",
    "NE.EXP.GNFS.ZS": "Exportations",
    "NE.IMP.GNFS.ZS": "Importations",
    "BN.CAB.XOKA.GD.ZS": "Solde courant",
    "BX.KLT.DINV.WD.GD.ZS": "IDE",
    "BX.TRF.PWKR.DT.GD.ZS": "Transferts",
}

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_all_wb(country_code):
    results = {}
    
    def fetch_one(code):
        if code == "NY.GDP.MKTP.KD.ZG":
            hist = fetch_wb_history(country_code, code, 25)
            v, y = latest(hist)
            return code, {"value": v, "year": y, "history": hist}
        else:
            v, y = fetch_wb_indicator(country_code, code)
            return code, {"value": v, "year": y}
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(fetch_one, c): c for c in WB_CODES.keys()}
        for future in as_completed(futures):
            try:
                code, result = future.result(timeout=30)
                results[code] = result
            except:
                results[futures[future]] = {"value": None, "year": None}
    
    return results

# Composants UI
def render_kpi_card(label, value, unit, signal, year=None, comparison=None, trend=None):
    year_text = f"<div class='kpi-meta'><span>{year}</span>{f'<span class=\"kpi-trend\">{trend}</span>' if trend else ''}</div>" if year else ""
    comparison_text = f"<div class='kpi-comparison'>📊 Moyenne régionale: {comparison}</div>" if comparison else ""
    
    return f"""
    <div class="kpi-card {signal}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value {signal}">{value}</div>
        <div class="kpi-unit">{unit}</div>
        {year_text}
        {comparison_text}
    </div>
    """

def render_gauge(label, value, min_val, max_val, signal, comparison=None):
    if value is None:
        width = 0
        display_val = "N/D"
    else:
        width = ((value - min_val) / (max_val - min_val)) * 100
        width = max(0, min(100, width))
        display_val = f"{value:.2f}"
    
    compare_html = ""
    if comparison is not None:
        compare_pos = ((comparison - min_val) / (max_val - min_val)) * 100
        compare_pos = max(0, min(100, compare_pos))
        compare_html = f'<div class="gauge-compare" style="left:{compare_pos}%;" data-label="Région"></div>'
    
    return f"""
    <div class="gauge-container">
        <div class="gauge-label">{label}</div>
        <div class="gauge-bar">
            <div class="gauge-fill {signal}" style="width:{width}%;">{display_val}</div>
            {compare_html}
        </div>
    </div>
    """

def create_pie_chart(values, labels, title):
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        marker=dict(colors=['#10b981', '#f59e0b', '#3b82f6']),
        textinfo='label+percent',
        textposition='auto'
    )])
    fig.update_layout(
        title=title,
        showlegend=True,
        height=350,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

def create_line_chart(data, title, y_label, show_regional=False, regional_avg=None):
    fig = go.Figure()
    
    # Ligne principale
    fig.add_trace(go.Scatter(
        x=[d["year"] for d in data],
        y=[d["value"] for d in data],
        mode='lines+markers',
        name='Pays',
        line=dict(color='#003189', width=3),
        marker=dict(size=6)
    ))
    
    # Moyenne depuis 2010
    data_2010 = [d for d in data if d["year"] >= 2010]
    if data_2010:
        avg = sum(d["value"] for d in data_2010) / len(data_2010)
        fig.add_hline(
            y=avg,
            line_dash="dash",
            line_color="#64748b",
            annotation_text=f"Moyenne 2010-présent: {avg:.1f}%",
            annotation_position="right"
        )
    
    # Moyenne régionale
    if show_regional and regional_avg is not None:
        fig.add_hline(
            y=regional_avg,
            line_dash="dot",
            line_color="#f59e0b",
            annotation_text=f"Moyenne régionale: {regional_avg:.1f}%",
            annotation_position="left"
        )
    
    # Zone de récession
    for d in data:
        if d["value"] < 0:
            fig.add_vrect(
                x0=d["year"]-0.5,
                x1=d["year"]+0.5,
                fillcolor="red",
                opacity=0.1,
                line_width=0
            )
    
    fig.update_layout(
        title=title,
        xaxis_title="Année",
        yaxis_title=y_label,
        hovermode='x unified',
        height=400,
        margin=dict(l=40, r=40, t=60, b=40)
    )
    
    return fig

def create_bar_chart(categories, values, comparison_values, title, y_label):
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=categories,
        y=values,
        name='Pays',
        marker_color='#003189'
    ))
    
    if comparison_values:
        fig.add_trace(go.Bar(
            x=categories,
            y=comparison_values,
            name='Moyenne régionale',
            marker_color='#94a3b8',
            opacity=0.6
        ))
    
    fig.update_layout(
        title=title,
        yaxis_title=y_label,
        barmode='group',
        height=350,
        margin=dict(l=40, r=40, t=60, b=40)
    )
    
    return fig

def create_stacked_bar(categories, values_country, values_region, title):
    fig = go.Figure()
    
    colors = ['#10b981', '#f59e0b', '#3b82f6']
    
    for i, cat in enumerate(categories):
        fig.add_trace(go.Bar(
            y=['Pays'],
            x=[values_country[i]],
            name=cat,
            orientation='h',
            marker_color=colors[i % len(colors)]
        ))
    
    if values_region:
        for i, cat in enumerate(categories):
            fig.add_trace(go.Bar(
                y=['Région'],
                x=[values_region[i]],
                name=cat,
                orientation='h',
                marker_color=colors[i % len(colors)],
                opacity=0.6,
                showlegend=False
            ))
    
    fig.update_layout(
        title=title,
        barmode='stack',
        height=200,
        margin=dict(l=100, r=40, t=60, b=40),
        xaxis_title="% du total"
    )
    
    return fig

# Interface principale
st.markdown("""
<div class="main-header">
    <h1>🌍 Dashboard Pays — Direction des Études et Recherches</h1>
    <p>Collecte automatisée · Visualisations · Comparaisons régionales · Export PDF/Excel</p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([3, 1])
with col1:
    opts = dict(sorted({v["name"]: k for k, v in COUNTRY_MAPPING.items()}.items()))
    selected = st.selectbox("🌐 Sélectionner un pays", options=list(opts.keys()))

with col2:
    st.write("")
    st.write("")
    run = st.button("🚀 Collecter les données", use_container_width=True)

if run:
    ci = COUNTRY_MAPPING[opts[selected]]
    wb_code = ci["world_bank_code"]
    
    # Progress
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    status_text.text("🔍 Collecte Freedom House...")
    progress_bar.progress(10)
    fh = fetch_freedom_house(ci["freedom_house_slug"])
    
    status_text.text("🏦 Collecte Banque mondiale...")
    progress_bar.progress(30)
    wb_info = fetch_wb_country_info(wb_code)
    
    status_text.text("📊 Collecte IDH...")
    progress_bar.progress(50)
    hdi = fetch_hdi(ci["name"])
    
    status_text.text("📈 Collecte indicateurs économiques...")
    progress_bar.progress(70)
    wb_data = fetch_all_wb(wb_code)
    
    status_text.text("✅ Traitement des données...")
    progress_bar.progress(90)
    
    # Déterminer la région pour comparaisons
    region_name = wb_info.get("region", "") if wb_info else ""
    regional_data = None
    for key in REGIONAL_AVERAGES:
        if key in region_name:
            regional_data = REGIONAL_AVERAGES[key]
            break
    
    progress_bar.progress(100)
    status_text.text("✅ Collecte terminée!")
    
    # Toggle comparaisons
    show_comparisons = st.checkbox("📊 Afficher les comparaisons régionales", value=False)
    
    # Carte pays
    flag = ci.get("flag", "")
    income_label = INCOME_LABELS.get(wb_info.get("income_code", "") if wb_info else "", "Non disponible")
    
    st.markdown(f"""
    <div class="country-card">
        <div class="country-name">{flag} {ci['name']}</div>
        <div class="country-meta">
            <div class="country-meta-item">
                <span class="country-meta-label">Région:</span>
                <span>{region_name}</span>
            </div>
            <div class="country-meta-item">
                <span class="country-meta-label">Revenu:</span>
                <span>{income_label}</span>
            </div>
            <div class="country-meta-item">
                <span class="country-meta-label">Collecte:</span>
                <span>{datetime.now().strftime("%d/%m/%Y %H:%M")}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ============================================
    # PILIER 1 : ENVIRONNEMENT POLITIQUE & SOCIO
    # ============================================
    
    total_p1 = 20
    available_p1 = 0
    
    st.markdown("""
    <div class="pillar-divider">
        <div class="pillar-title">🏛️ PILIER 1 : Environnement politique et socioéconomique</div>
        <div class="pillar-subtitle">Régime politique · Gouvernance · Développement humain · Emploi · Éducation</div>
    </div>
    """, unsafe_allow_html=True)
    
    # 1.1 Vue d'ensemble P1
    st.markdown('<div class="section-header">📌 Vue d\'ensemble</div>', unsafe_allow_html=True)
    
    kpi_html = '<div class="kpi-grid">'
    
    # Freedom House
    fh_score = fh.get("score") if fh and not fh.get("error") else None
    fh_status = fh.get("status") if fh and not fh.get("error") else "N/D"
    fh_signal = get_signal(fh_score, {"high": 70, "low": 40, "reverse": False})
    if fh_score:
        available_p1 += 1
    kpi_html += render_kpi_card(
        "Freedom House",
        f"{fh_score}/100" if fh_score else "N/D",
        fh_status,
        fh_signal,
        fh.get("year") if fh and not fh.get("error") else None
    )
    
    # IDH
    hdi_val = hdi.get("value")
    hdi_rank = hdi.get("rank")
    hdi_signal = get_signal(hdi_val, {"high": 0.800, "low": 0.550, "reverse": False})
    hdi_comparison = f"{regional_data['hdi']:.3f}" if show_comparisons and regional_data else None
    if hdi_val:
        available_p1 += 1
    kpi_html += render_kpi_card(
        "Indice de Développement Humain",
        f"{hdi_val:.3f}" if hdi_val else "N/D",
        f"Rang mondial: {hdi_rank}" if hdi_rank else "",
        hdi_signal,
        hdi.get("year"),
        hdi_comparison
    )
    
    # Pauvreté
    poverty_val = wb_data.get("SI.POV.DDAY", {}).get("value")
    poverty_year = wb_data.get("SI.POV.DDAY", {}).get("year")
    poverty_signal = get_signal(poverty_val, {"high": 20, "low": 5, "reverse": True})
    poverty_comparison = f"{regional_data['poverty']:.1f}%" if show_comparisons and regional_data else None
    if poverty_val:
        available_p1 += 1
    kpi_html += render_kpi_card(
        "Taux de pauvreté",
        f"{poverty_val:.1f}" if poverty_val else "N/D",
        "% pop. < 2,15$/jour",
        poverty_signal,
        poverty_year,
        poverty_comparison
    )
    
    # Gini
    gini_val = wb_data.get("SI.POV.GINI", {}).get("value")
    gini_year = wb_data.get("SI.POV.GINI", {}).get("year")
    gini_signal = get_signal(gini_val, {"high": 45, "low": 32, "reverse": True})
    gini_comparison = f"{regional_data['gini']:.1f}" if show_comparisons and regional_data else None
    if gini_val:
        available_p1 += 1
    kpi_html += render_kpi_card(
        "Indice de Gini",
        f"{gini_val:.1f}" if gini_val else "N/D",
        "Inégalités",
        gini_signal,
        gini_year,
        gini_comparison
    )
    
    kpi_html += '</div>'
    st.markdown(kpi_html, unsafe_allow_html=True)
    
    # 1.2 Gouvernance WGI
    st.markdown('<div class="section-header">⚖️ Gouvernance institutionnelle (WGI)</div>', unsafe_allow_html=True)
    
    wgi_codes = {
        "VA.EST": "Expression & responsabilité",
        "PV.EST": "Stabilité politique",
        "GE.EST": "Efficacité gouvernementale",
        "RQ.EST": "Qualité réglementaire",
        "RL.EST": "État de droit",
        "CC.EST": "Contrôle de la corruption",
    }
    
    wgi_html = ""
    for code, label in wgi_codes.items():
        val = wb_data.get(code, {}).get("value")
        if val:
            available_p1 += 1
        signal = get_signal(val, {"high": 0.5, "low": -0.3, "reverse": False})
        wgi_html += render_gauge(label, val, -2.5, 2.5, signal, 0 if show_comparisons else None)
    
    st.markdown(wgi_html, unsafe_allow_html=True)
    
    # 1.3 Marché du travail
    st.markdown('<div class="section-header">👷 Marché du travail</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        emp_total = wb_data.get("SL.EMP.TOTL.SP.ZS", {}).get("value")
        if emp_total:
            available_p1 += 1
        emp_signal = get_signal(emp_total, {"high": 75, "low": 50, "reverse": False})
        st.markdown(render_gauge(
            "Taux d'emploi total",
            emp_total,
            0, 100,
            emp_signal
        ), unsafe_allow_html=True)
        
        unemp_youth = wb_data.get("SL.UEM.1524.ZS", {}).get("value")
        if unemp_youth:
            available_p1 += 1
        unemp_signal = get_signal(unemp_youth, {"high": 25, "low": 10, "reverse": True})
        st.markdown(render_gauge(
            "Chômage des jeunes (15-24 ans)",
            unemp_youth,
            0, 100,
            unemp_signal
        ), unsafe_allow_html=True)
    
    with col2:
        emp_female = wb_data.get("SL.EMP.TOTL.SP.FE.ZS", {}).get("value")
        if emp_female:
            available_p1 += 1
        emp_f_signal = get_signal(emp_female, {"high": 75, "low": 50, "reverse": False})
        st.markdown(render_gauge(
            "Taux d'emploi des femmes",
            emp_female,
            0, 100,
            emp_f_signal
        ), unsafe_allow_html=True)
        
        informal = wb_data.get("SL.ISV.IFRM.ZS", {}).get("value")
        if informal:
            available_p1 += 1
        informal_signal = get_signal(informal, {"high": 50, "low": 25, "reverse": True})
        st.markdown(render_gauge(
            "Taux d'informalité",
            informal,
            0, 100,
            informal_signal
        ), unsafe_allow_html=True)
    
    # 1.4 Éducation
    st.markdown('<div class="section-header">📚 Capital humain & éducation</div>', unsafe_allow_html=True)
    
    primary = wb_data.get("SE.PRM.ENRR", {}).get("value")
    secondary = wb_data.get("SE.SEC.ENRR", {}).get("value")
    tertiary = wb_data.get("SE.TER.ENRR", {}).get("value")
    
    if primary:
        available_p1 += 1
    if secondary:
        available_p1 += 1
    if tertiary:
        available_p1 += 1
    
    edu_comparison = None
    if show_comparisons and regional_data:
        edu_comparison = [
            regional_data.get("primary_school"),
            regional_data.get("secondary_school"),
            regional_data.get("tertiary_school")
        ]
    
    if primary or secondary or tertiary:
        fig = create_bar_chart(
            ["Primaire", "Secondaire", "Tertiaire"],
            [primary or 0, secondary or 0, tertiary or 0],
            edu_comparison,
            "Taux de scolarisation (taux brut)",
            "% de la population"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Prompt P1
    st.markdown("""
    <div class="prompt-box">
        <div class="prompt-title">🤖 Prompt IA — Pilier 1</div>
    """, unsafe_allow_html=True)
    
    prompt_p1 = f"""FICHE PAYS — {ci['name'].upper()}
PILIER 1 : ENVIRONNEMENT POLITIQUE ET SOCIOÉCONOMIQUE
{'='*70}

DONNÉES COLLECTÉES
{'-'*40}
• Freedom House Score: {fh_score}/100 ({fh_status}) — {fh.get('year') if fh and not fh.get('error') else 'N/D'}
• IDH: {hdi_val:.3f if hdi_val else 'N/D'} (Rang: {hdi_rank if hdi_rank else 'N/D'}) — 2023
• Pauvreté: {poverty_val:.1f if poverty_val else 'N/D'}% — {poverty_year or 'N/D'}
• Gini: {gini_val:.1f if gini_val else 'N/D'} — {gini_year or 'N/D'}

WGI Gouvernance:
{chr(10).join(f'• {label}: {wb_data.get(code, {}).get("value"):.2f if wb_data.get(code, {}).get("value") else "N/D"}' for code, label in wgi_codes.items())}

Marché du travail:
• Emploi total: {emp_total:.1f if emp_total else 'N/D'}%
• Chômage jeunes: {unemp_youth:.1f if unemp_youth else 'N/D'}%
• Emploi femmes: {emp_female:.1f if emp_female else 'N/D'}%
• Informalité: {informal:.1f if informal else 'N/D'}%

Éducation:
• Primaire: {primary:.1f if primary else 'N/D'}%
• Secondaire: {secondary:.1f if secondary else 'N/D'}%
• Tertiaire: {tertiary:.1f if tertiary else 'N/D'}%

{'='*70}
CONSIGNE
{'-'*40}
Rédige une analyse structurée en 5 parties:

1. Régime politique & libertés (Freedom House, tendances)
2. Gouvernance institutionnelle (analyse WGI)
3. Développement humain & inégalités (IDH, pauvreté, Gini)
4. Marché du travail (emploi, chômage, informalité)
5. Capital humain (scolarisation, perspectives)

Règles:
- Pas de chiffres inventés
- Signaler les lacunes de données
- Style institutionnel, analytique
- ~450 mots
"""
    
    st.text_area("", value=prompt_p1, height=400, key="prompt_p1")
    if st.button("📋 Copier le prompt", key="copy_p1"):
        st.success("✅ Copié! (Ctrl+A puis Ctrl+C)")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # ============================================
    # PILIER 2 : MODÈLE ÉCO & RÉGIME DE CROISSANCE
    # ============================================
    
    total_p2 = 25
    available_p2 = 0
    
    st.markdown("""
    <div class="pillar-divider">
        <div class="pillar-title">📈 PILIER 2 : Modèle économique et régime de croissance</div>
        <div class="pillar-subtitle">Structure productive · Dynamique de croissance · Demande · Ouverture externe</div>
    </div>
    """, unsafe_allow_html=True)
    
    # 2.1 Vue d'ensemble P2
    st.markdown('<div class="section-header">📌 Vue d\'ensemble</div>', unsafe_allow_html=True)
    
    kpi_html = '<div class="kpi-grid">'
    
    # PIB/hab
    gdp_pc = wb_data.get("NY.GDP.PCAP.CD", {}).get("value")
    gdp_pc_year = wb_data.get("NY.GDP.PCAP.CD", {}).get("year")
    gdp_signal = get_signal(gdp_pc, {"high": 10000, "low": 3000, "reverse": False})
    if gdp_pc:
        available_p2 += 1
    kpi_html += render_kpi_card(
        "PIB par habitant",
        f"${gdp_pc:,.0f}" if gdp_pc else "N/D",
        "USD",
        gdp_signal,
        gdp_pc_year
    )
    
    # Croissance
    growth = wb_data.get("NY.GDP.MKTP.KD.ZG", {}).get("value")
    growth_year = wb_data.get("NY.GDP.MKTP.KD.ZG", {}).get("year")
    growth_signal = get_signal(growth, {"high": 5, "low": 2, "reverse": False})
    growth_comparison = f"{regional_data['gdp_growth']:.1f}%" if show_comparisons and regional_data else None
    if growth:
        available_p2 += 1
    kpi_html += render_kpi_card(
        "Croissance du PIB",
        f"{growth:.1f}" if growth else "N/D",
        "% annuel",
        growth_signal,
        growth_year,
        growth_comparison
    )
    
    # Inflation
    inflation = wb_data.get("FP.CPI.TOTL.ZG", {}).get("value")
    inflation_year = wb_data.get("FP.CPI.TOTL.ZG", {}).get("year")
    inflation_signal = get_signal(inflation, {"high": 10, "low": 4, "reverse": True})
    inflation_comparison = f"{regional_data['inflation']:.1f}%" if show_comparisons and regional_data else None
    if inflation:
        available_p2 += 1
    kpi_html += render_kpi_card(
        "Inflation",
        f"{inflation:.1f}" if inflation else "N/D",
        "% annuel",
        inflation_signal,
        inflation_year,
        inflation_comparison
    )
    
    # Solde courant
    current_acc = wb_data.get("BN.CAB.XOKA.GD.ZS", {}).get("value")
    current_acc_year = wb_data.get("BN.CAB.XOKA.GD.ZS", {}).get("year")
    current_signal = "green" if current_acc and current_acc > 0 else ("orange" if current_acc and current_acc > -5 else "red")
    if current_acc:
        available_p2 += 1
    kpi_html += render_kpi_card(
        "Solde courant",
        f"{current_acc:.1f}" if current_acc else "N/D",
        "% du PIB",
        current_signal,
        current_acc_year
    )
    
    kpi_html += '</div>'
    st.markdown(kpi_html, unsafe_allow_html=True)
    
    # 2.2 Structure productive
    st.markdown('<div class="section-header">🏗️ Structure productive</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-title">Composition du PIB</div>', unsafe_allow_html=True)
        agri_gdp = wb_data.get("NV.AGR.TOTL.ZS", {}).get("value")
        ind_gdp = wb_data.get("NV.IND.TOTL.ZS", {}).get("value")
        serv_gdp = wb_data.get("NV.SRV.TOTL.ZS", {}).get("value")
        
        if agri_gdp:
            available_p2 += 1
        if ind_gdp:
            available_p2 += 1
        if serv_gdp:
            available_p2 += 1
        
        if agri_gdp and ind_gdp and serv_gdp:
            fig = create_pie_chart(
                [agri_gdp, ind_gdp, serv_gdp],
                ["Agriculture", "Industrie", "Services"],
                ""
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown('<div class="chart-title">Composition de l\'emploi</div>', unsafe_allow_html=True)
        agri_emp = wb_data.get("SL.AGR.EMPL.ZS", {}).get("value")
        ind_emp = wb_data.get("SL.IND.EMPL.ZS", {}).get("value")
        serv_emp = wb_data.get("SL.SRV.EMPL.ZS", {}).get("value")
        
        if agri_emp:
            available_p2 += 1
        if ind_emp:
            available_p2 += 1
        if serv_emp:
            available_p2 += 1
        
        emp_country = [agri_emp or 0, ind_emp or 0, serv_emp or 0]
        emp_region = None
        if show_comparisons and regional_data:
            emp_region = [
                regional_data.get("agriculture_emp"),
                regional_data.get("industry_emp"),
                regional_data.get("services_emp")
            ]
        
        if any(emp_country):
            fig = create_stacked_bar(
                ["Agriculture", "Industrie", "Services"],
                emp_country,
                emp_region,
                ""
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # 2.3 Dynamique de croissance
    st.markdown('<div class="section-header">📊 Dynamique de croissance</div>', unsafe_allow_html=True)
    
    growth_hist = wb_data.get("NY.GDP.MKTP.KD.ZG", {}).get("history", [])
    if growth_hist:
        regional_avg = regional_data.get("gdp_growth") if show_comparisons and regional_data else None
        fig = create_line_chart(
            growth_hist,
            "Croissance du PIB réel (15 dernières années)",
            "% annuel",
            show_comparisons,
            regional_avg
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Tableau récapitulatif
        avg_2010 = avg_since(growth_hist, 2010)
        avg_10 = avg_last(growth_hist, 10)
        
        recap_df = pd.DataFrame({
            "Période": ["Depuis 2010", "10 dernières observations"],
            "Croissance moyenne pays": [
                f"{avg_2010:.1f}%" if avg_2010 else "N/D",
                f"{avg_10:.1f}%" if avg_10 else "N/D"
            ],
            "Croissance moyenne région": [
                f"{regional_avg:.1f}%" if show_comparisons and regional_avg else "—",
                f"{regional_avg:.1f}%" if show_comparisons and regional_avg else "—"
            ]
        })
        st.dataframe(recap_df, use_container_width=True, hide_index=True)
    
    # 2.4 Demande & financement
    st.markdown('<div class="section-header">💹 Demande & investissement</div>', unsafe_allow_html=True)
    
    demand_items = {
        "NE.CON.PRVT.ZS": ("Consommation privée", "consumption_private"),
        "NE.CON.GOVT.ZS": ("Consommation publique", "consumption_public"),
        "NE.GDI.FTOT.ZS": ("Investissement (FBCF)", "investment"),
        "FS.AST.PRVT.GD.ZS": ("Crédit au secteur privé", "credit_private"),
    }
    
    demand_html = ""
    for code, (label, regional_key) in demand_items.items():
        val = wb_data.get(code, {}).get("value")
        if val:
            available_p2 += 1
        signal = get_signal(val, {"high": 75, "low": 40, "reverse": False})
        comparison = regional_data.get(regional_key) if show_comparisons and regional_data else None
        demand_html += render_gauge(label, val, 0, 100, signal, comparison)
    
    st.markdown(demand_html, unsafe_allow_html=True)
    
    # 2.5 Ouverture externe
    st.markdown('<div class="section-header">🌍 Ouverture externe</div>', unsafe_allow_html=True)
    
    exports = wb_data.get("NE.EXP.GNFS.ZS", {}).get("value")
    imports = wb_data.get("NE.IMP.GNFS.ZS", {}).get("value")
    fdi = wb_data.get("BX.KLT.DINV.WD.GD.ZS", {}).get("value")
    remittances = wb_data.get("BX.TRF.PWKR.DT.GD.ZS", {}).get("value")
    
    if exports:
        available_p2 += 1
    if imports:
        available_p2 += 1
    if fdi:
        available_p2 += 1
    if remittances:
        available_p2 += 1
    
    external_comparison = None
    if show_comparisons and regional_data:
        external_comparison = [
            regional_data.get("exports"),
            regional_data.get("imports"),
            regional_data.get("fdi"),
            regional_data.get("remittances")
        ]
    
    if any([exports, imports, fdi, remittances]):
        fig = create_bar_chart(
            ["Exportations", "Importations", "IDE", "Transferts migrants"],
            [exports or 0, imports or 0, fdi or 0, remittances or 0],
            external_comparison,
            "Ouverture externe (% du PIB)",
            "% du PIB"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # 2.6 Indicateurs à compléter
    st.markdown('<div class="section-header">⚠️ Indicateurs à compléter manuellement</div>', unsafe_allow_html=True)
    
    manual_indicators = [
        "Part du secteur extractif dans le PIB",
        "Part du secteur extractif dans les exportations",
        "Part du secteur extractif dans les recettes publiques",
        "Part du tourisme dans le PIB",
        "Croissance potentielle (FMI)",
        "Prévisions FMI (année en cours / N+1)",
        "Réformes et chocs récents"
    ]
    
    st.info("📝 " + " · ".join(manual_indicators))
    
    # Prompt P2
    st.markdown("""
    <div class="prompt-box">
        <div class="prompt-title">🤖 Prompt IA — Pilier 2</div>
    """, unsafe_allow_html=True)
    
    prompt_p2 = f"""FICHE PAYS — {ci['name'].upper()}
PILIER 2 : MODÈLE ÉCONOMIQUE ET RÉGIME DE CROISSANCE
{'='*70}

DONNÉES COLLECTÉES
{'-'*40}
Vue d'ensemble:
• PIB/habitant: ${gdp_pc:,.0f if gdp_pc else 'N/D'} — {gdp_pc_year or 'N/D'}
• Croissance: {growth:.1f if growth else 'N/D'}% — {growth_year or 'N/D'}
• Inflation: {inflation:.1f if inflation else 'N/D'}% — {inflation_year or 'N/D'}
• Solde courant: {current_acc:.1f if current_acc else 'N/D'}% PIB — {current_acc_year or 'N/D'}

Structure du PIB:
• Agriculture: {agri_gdp:.1f if agri_gdp else 'N/D'}%
• Industrie: {ind_gdp:.1f if ind_gdp else 'N/D'}%
• Services: {serv_gdp:.1f if serv_gdp else 'N/D'}%

Structure de l'emploi:
• Agriculture: {agri_emp:.1f if agri_emp else 'N/D'}%
• Industrie: {ind_emp:.1f if ind_emp else 'N/D'}%
• Services: {serv_emp:.1f if serv_emp else 'N/D'}%

Croissance:
• Moyenne depuis 2010: {avg_2010:.1f if avg_2010 else 'N/D'}%
• Moyenne 10 dernières obs.: {avg_10:.1f if avg_10 else 'N/D'}%

Demande:
• Consommation privée: {wb_data.get('NE.CON.PRVT.ZS', {}).get('value'):.1f if wb_data.get('NE.CON.PRVT.ZS', {}).get('value') else 'N/D'}% PIB
• Consommation publique: {wb_data.get('NE.CON.GOVT.ZS', {}).get('value'):.1f if wb_data.get('NE.CON.GOVT.ZS', {}).get('value') else 'N/D'}% PIB
• Investissement: {wb_data.get('NE.GDI.FTOT.ZS', {}).get('value'):.1f if wb_data.get('NE.GDI.FTOT.ZS', {}).get('value') else 'N/D'}% PIB
• Crédit privé: {wb_data.get('FS.AST.PRVT.GD.ZS', {}).get('value'):.1f if wb_data.get('FS.AST.PRVT.GD.ZS', {}).get('value') else 'N/D'}% PIB

Ouverture:
• Exportations: {exports:.1f if exports else 'N/D'}% PIB
• Importations: {imports:.1f if imports else 'N/D'}% PIB
• IDE: {fdi:.1f if fdi else 'N/D'}% PIB
• Transferts: {remittances:.1f if remittances else 'N/D'}% PIB

{'='*70}
CONSIGNE
{'-'*40}
Rédige une analyse structurée en 2 parties:

Partie 1 — Modèle économique:
- Structure productive (secteurs, poids relatifs)
- Spécialisation et diversification
- Forces et fragilités structurelles

Partie 2 — Régime de croissance:
- Rythme de croissance (historique, tendances)
- Moteurs de la croissance (demande, investissement, export)
- Soutenabilité (déséquilibres, vulnérabilités)

Règles:
- Pas de chiffres inventés
- Style institutionnel dense
- ~550 mots
"""
    
    st.text_area("", value=prompt_p2, height=400, key="prompt_p2")
    if st.button("📋 Copier le prompt", key="copy_p2"):
        st.success("✅ Copié! (Ctrl+A puis Ctrl+C)")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Statistiques finales
    total_indicators = total_p1 + total_p2
    total_available = available_p1 + available_p2
    coverage = int(100 * total_available / total_indicators) if total_indicators else 0
    
    st.markdown(f"""
    <div class="pillar-divider">
        <div class="pillar-title">📊 Bilan de la collecte</div>
        <div class="pillar-stats">
            <div class="pillar-stat">
                <span>Total indicateurs:</span>
                <span class="pillar-stat-val">{total_indicators}</span>
            </div>
            <div class="pillar-stat">
                <span>Indicateurs disponibles:</span>
                <span class="pillar-stat-val" style="color:#10b981;">{total_available}</span>
            </div>
            <div class="pillar-stat">
                <span>Taux de couverture:</span>
                <span class="pillar-stat-val" style="color:{'#10b981' if coverage > 70 else '#f59e0b' if coverage > 50 else '#ef4444'};">{coverage}%</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Boutons export
    st.markdown('<div class="export-buttons">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 Télécharger PDF", key="export_pdf", use_container_width=True):
            st.warning("🚧 Fonction PDF en développement")
    
    with col2:
        # Export Excel
        export_data = {
            "Indicateur": [],
            "Valeur": [],
            "Année": [],
            "Source": []
        }
        
        # Pilier 1
        for name, code in [("FH Score", None), ("IDH", None), ("Pauvreté", "SI.POV.DDAY"), ("Gini", "SI.POV.GINI")]:
            if code:
                val = wb_data.get(code, {}).get("value")
                year = wb_data.get(code, {}).get("year")
            else:
                val = fh_score if name == "FH Score" else (hdi_val if name == "IDH" else None)
                year = fh.get("year") if name == "FH Score" else (hdi.get("year") if name == "IDH" else None)
            
            export_data["Indicateur"].append(name)
            export_data["Valeur"].append(val if val else "N/D")
            export_data["Année"].append(year if year else "N/D")
            export_data["Source"].append("Freedom House" if name == "FH Score" else ("PNUD" if name == "IDH" else "Banque mondiale"))
        
        # Pilier 2
        for name, code in [("PIB/hab", "NY.GDP.PCAP.CD"), ("Croissance", "NY.GDP.MKTP.KD.ZG"), ("Inflation", "FP.CPI.TOTL.ZG")]:
            val = wb_data.get(code, {}).get("value")
            year = wb_data.get(code, {}).get("year")
            export_data["Indicateur"].append(name)
            export_data["Valeur"].append(val if val else "N/D")
            export_data["Année"].append(year if year else "N/D")
            export_data["Source"].append("Banque mondiale")
        
        df_export = pd.DataFrame(export_data)
        
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df_export.to_excel(writer, index=False, sheet_name='Données')
        
        st.download_button(
            label="📊 Exporter Excel",
            data=buffer.getvalue(),
            file_name=f"dashboard_{ci['name'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.ms-excel",
            use_container_width=True
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown(f"""
    <div class="footer">
        Dashboard généré le {datetime.now().strftime("%d/%m/%Y à %H:%M")} · 
        AFD — Direction des Études et Recherches · 
        Sources: Freedom House, PNUD, Banque mondiale
    </div>
    """, unsafe_allow_html=True)
