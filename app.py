```python
import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from datetime import datetime
from io import BytesIO

st.set_page_config(
    page_title="Outil de collecte de données - DER",
    page_icon="🌍",
    layout="wide"
)

CURRENT_YEAR = datetime.now().year
OLD_DATA_THRESHOLD = 5

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: "Inter", sans-serif;
    color: #1e293b;
}
.stApp { background-color: #f1f5f9; }
.main .block-container {
    padding-top: 1.5rem;
    padding-bottom: 3rem;
    max-width: 1200px;
}

/* ── HEADER ── */
.afd-header {
    background: #003189;
    padding: 20px 28px;
    border-radius: 10px;
    margin-bottom: 28px;
}
.afd-header h1 {
    color: #fff !important;
    font-size: 19px;
    margin: 0;
    font-weight: 600;
}
.afd-header p { color: #93b4e8; font-size: 12px; margin: 5px 0 0 0; }

/* ── PILLAR TITLE ── */
.pillar-title {
    font-size: 13px;
    font-weight: 700;
    color: #003189;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin: 32px 0 14px 0;
    padding-bottom: 8px;
    border-bottom: 2px solid #003189;
}

/* ── SECTION LABEL ── */
.sec-label {
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #94a3b8;
    margin: 18px 0 6px 2px;
}

/* ── KPI CARD ── */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    gap: 10px;
    margin-bottom: 6px;
}
.kpi-card {
    background: #ffffff;
    border-radius: 10px;
    padding: 14px 16px 12px 16px;
    border-top: 3px solid #e2e8f0;
    position: relative;
}
.kpi-label {
    font-size: 10.5px;
    color: #94a3b8;
    margin-bottom: 6px;
    line-height: 1.3;
}
.kpi-value {
    font-size: 18px;
    font-weight: 700;
    line-height: 1.1;
}
.kpi-sub {
    font-size: 10px;
    color: #94a3b8;
    margin-top: 3px;
}
.kpi-trend {
    position: absolute;
    top: 12px;
    right: 14px;
    font-size: 13px;
    font-weight: 700;
}
.kpi-year {
    font-size: 9.5px;
    color: #cbd5e1;
    margin-top: 2px;
}
.kpi-note {
    font-size: 9px;
    color: #f59e0b;
    margin-top: 3px;
}

/* ── ROW TABLE ── */
.ind-table { width: 100%; border-collapse: collapse; margin-bottom: 4px; }
.ind-tr {
    background: #ffffff;
    border-radius: 7px;
    margin-bottom: 3px;
}
.ind-tr:hover { background: #f8fafc; }
.ind-td { padding: 8px 12px; }
.ind-label { font-size: 12.5px; color: #475569; }
.ind-val   { font-size: 13px; font-weight: 600; text-align: right; white-space: nowrap; }
.ind-unit  { font-size: 10.5px; color: #94a3b8; padding-left: 4px; }
.ind-yr    { font-size: 10.5px; color: #cbd5e1; text-align: center; min-width: 44px; }
.ind-arrow { font-size: 13px; font-weight: 700; text-align: center; width: 28px; }
.ind-dot   { width: 8px; height: 8px; border-radius: 50%; display: inline-block; }
.ind-src   { font-size: 10px; color: #cbd5e1; text-align: right; }
.ind-src a { color: #cbd5e1; text-decoration: none; }
.ind-src a:hover { color: #003189; }
.row-note  { font-size: 9.5px; color: #f59e0b; padding: 0 12px 5px 12px; font-style: italic; }

/* Colors */
.c-green  { color: #16a34a; }
.c-lime   { color: #65a30d; }
.c-orange { color: #d97706; }
.c-red    { color: #dc2626; }
.c-slate  { color: #64748b; }
.c-grey   { color: #94a3b8; }

.d-green  { background: #16a34a; }
.d-lime   { background: #84cc16; }
.d-orange { background: #f59e0b; }
.d-red    { background: #ef4444; }
.d-slate  { background: #94a3b8; }
.d-grey   { background: #e2e8f0; }

.t-green  { color: #16a34a; }
.t-lime   { color: #65a30d; }
.t-orange { color: #d97706; }
.t-red    { color: #dc2626; }
.t-grey   { color: #cbd5e1; }

/* border-top KPI */
.bt-green  { border-top-color: #16a34a !important; }
.bt-lime   { border-top-color: #84cc16 !important; }
.bt-orange { border-top-color: #f59e0b !important; }
.bt-red    { border-top-color: #ef4444 !important; }
.bt-slate  { border-top-color: #94a3b8 !important; }
.bt-grey   { border-top-color: #e2e8f0 !important; }

/* ── PROMPT ── */
.prompt-lbl {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #94a3b8;
    margin: 28px 0 6px 2px;
}

/* ── DIVIDER ── */
.pill-divider { height: 1px; background: #e2e8f0; margin: 30px 0; }

/* ── BUTTON ── */
div[data-testid="stButton"] button {
    background: #003189;
    color: white;
    font-family: "Inter", sans-serif;
    font-weight: 600;
    font-size: 13px;
    border: none;
    border-radius: 8px;
    padding: 10px 24px;
    width: 100%;
    transition: background 0.2s;
}
div[data-testid="stButton"] button:hover { background: #1d4ed8; }

div[data-testid="stSelectbox"] label {
    font-size: 11px;
    font-weight: 600;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.07em;
}

.footer-note {
    font-size: 11px;
    color: #cbd5e1;
    margin-top: 36px;
    text-align: center;
    border-top: 1px solid #e2e8f0;
    padding-top: 10px;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Pays
# ─────────────────────────────────────────────
COUNTRY_MAPPING = {
    "afghanistan": {"name": "Afghanistan", "freedom_house_slug": "afghanistan", "world_bank_code": "AFG", "wb_url_code": "AF"},
    "afrique_du_sud": {"name": "Afrique du Sud", "freedom_house_slug": "south-africa", "world_bank_code": "ZAF", "wb_url_code": "ZA"},
    "albanie": {"name": "Albanie", "freedom_house_slug": "albania", "world_bank_code": "ALB", "wb_url_code": "AL"},
    "algerie": {"name": "Algérie", "freedom_house_slug": "algeria", "world_bank_code": "DZA", "wb_url_code": "DZ"},
    "angola": {"name": "Angola", "freedom_house_slug": "angola", "world_bank_code": "AGO", "wb_url_code": "AO"},
    "argentine": {"name": "Argentine", "freedom_house_slug": "argentina", "world_bank_code": "ARG", "wb_url_code": "AR"},
    "armenie": {"name": "Arménie", "freedom_house_slug": "armenia", "world_bank_code": "ARM", "wb_url_code": "AM"},
    "azerbaijan": {"name": "Azerbaïdjan", "freedom_house_slug": "azerbaijan", "world_bank_code": "AZE", "wb_url_code": "AZ"},
    "bangladesh": {"name": "Bangladesh", "freedom_house_slug": "bangladesh", "world_bank_code": "BGD", "wb_url_code": "BD"},
    "benin": {"name": "Bénin", "freedom_house_slug": "benin", "world_bank_code": "BEN", "wb_url_code": "BJ"},
    "bolivie": {"name": "Bolivie", "freedom_house_slug": "bolivia", "world_bank_code": "BOL", "wb_url_code": "BO"},
    "bresil": {"name": "Brésil", "freedom_house_slug": "brazil", "world_bank_code": "BRA", "wb_url_code": "BR"},
    "burkina_faso": {"name": "Burkina Faso", "freedom_house_slug": "burkina-faso", "world_bank_code": "BFA", "wb_url_code": "BF"},
    "burundi": {"name": "Burundi", "freedom_house_slug": "burundi", "world_bank_code": "BDI", "wb_url_code": "BI"},
    "cambodge": {"name": "Cambodge", "freedom_house_slug": "cambodia", "world_bank_code": "KHM", "wb_url_code": "KH"},
    "cameroun": {"name": "Cameroun", "freedom_house_slug": "cameroon", "world_bank_code": "CMR", "wb_url_code": "CM"},
    "chili": {"name": "Chili", "freedom_house_slug": "chile", "world_bank_code": "CHL", "wb_url_code": "CL"},
    "chine": {"name": "Chine", "freedom_house_slug": "china", "world_bank_code": "CHN", "wb_url_code": "CN"},
    "colombie": {"name": "Colombie", "freedom_house_slug": "colombia", "world_bank_code": "COL", "wb_url_code": "CO"},
    "cote_ivoire": {"name": "Côte d'Ivoire", "freedom_house_slug": "cote-divoire", "world_bank_code": "CIV", "wb_url_code": "CI"},
    "egypte": {"name": "Égypte", "freedom_house_slug": "egypt", "world_bank_code": "EGY", "wb_url_code": "EG"},
    "ethiopie": {"name": "Éthiopie", "freedom_house_slug": "ethiopia", "world_bank_code": "ETH", "wb_url_code": "ET"},
    "ghana": {"name": "Ghana", "freedom_house_slug": "ghana", "world_bank_code": "GHA", "wb_url_code": "GH"},
    "guinee": {"name": "Guinée", "freedom_house_slug": "guinea", "world_bank_code": "GIN", "wb_url_code": "GN"},
    "haiti": {"name": "Haïti", "freedom_house_slug": "haiti", "world_bank_code": "HTI", "wb_url_code": "HT"},
    "inde": {"name": "Inde", "freedom_house_slug": "india", "world_bank_code": "IND", "wb_url_code": "IN"},
    "indonesie": {"name": "Indonésie", "freedom_house_slug": "indonesia", "world_bank_code": "IDN", "wb_url_code": "ID"},
    "irak": {"name": "Irak", "freedom_house_slug": "iraq", "world_bank_code": "IRQ", "wb_url_code": "IQ"},
    "kenya": {"name": "Kenya", "freedom_house_slug": "kenya", "world_bank_code": "KEN", "wb_url_code": "KE"},
    "liban": {"name": "Liban", "freedom_house_slug": "lebanon", "world_bank_code": "LBN", "wb_url_code": "LB"},
    "madagascar": {"name": "Madagascar", "freedom_house_slug": "madagascar", "world_bank_code": "MDG", "wb_url_code": "MG"},
    "mali": {"name": "Mali", "freedom_house_slug": "mali", "world_bank_code": "MLI", "wb_url_code": "ML"},
    "maroc": {"name": "Maroc", "freedom_house_slug": "morocco", "world_bank_code": "MAR", "wb_url_code": "MA"},
    "mauritanie": {"name": "Mauritanie", "freedom_house_slug": "mauritania", "world_bank_code": "MRT", "wb_url_code": "MR"},
    "mexique": {"name": "Mexique", "freedom_house_slug": "mexico", "world_bank_code": "MEX", "wb_url_code": "MX"},
    "mozambique": {"name": "Mozambique", "freedom_house_slug": "mozambique", "world_bank_code": "MOZ", "wb_url_code": "MZ"},
    "niger": {"name": "Niger", "freedom_house_slug": "niger", "world_bank_code": "NER", "wb_url_code": "NE"},
    "nigeria": {"name": "Nigéria", "freedom_house_slug": "nigeria", "world_bank_code": "NGA", "wb_url_code": "NG"},
    "pakistan": {"name": "Pakistan", "freedom_house_slug": "pakistan", "world_bank_code": "PAK", "wb_url_code": "PK"},
    "perou": {"name": "Pérou", "freedom_house_slug": "peru", "world_bank_code": "PER", "wb_url_code": "PE"},
    "philippines": {"name": "Philippines", "freedom_house_slug": "philippines", "world_bank_code": "PHL", "wb_url_code": "PH"},
    "rdc": {"name": "RDC (Congo-Kinshasa)", "freedom_house_slug": "democratic-republic-of-congo", "world_bank_code": "COD", "wb_url_code": "CD"},
    "rwanda": {"name": "Rwanda", "freedom_house_slug": "rwanda", "world_bank_code": "RWA", "wb_url_code": "RW"},
    "senegal": {"name": "Sénégal", "freedom_house_slug": "senegal", "world_bank_code": "SEN", "wb_url_code": "SN"},
    "somalie": {"name": "Somalie", "freedom_house_slug": "somalia", "world_bank_code": "SOM", "wb_url_code": "SO"},
    "soudan": {"name": "Soudan", "freedom_house_slug": "sudan", "world_bank_code": "SDN", "wb_url_code": "SD"},
    "tanzanie": {"name": "Tanzanie", "freedom_house_slug": "tanzania", "world_bank_code": "TZA", "wb_url_code": "TZ"},
    "tchad": {"name": "Tchad", "freedom_house_slug": "chad", "world_bank_code": "TCD", "wb_url_code": "TD"},
    "tunisie": {"name": "Tunisie", "freedom_house_slug": "tunisia", "world_bank_code": "TUN", "wb_url_code": "TN"},
    "turquie": {"name": "Turquie", "freedom_house_slug": "turkey", "world_bank_code": "TUR", "wb_url_code": "TR"},
    "ukraine": {"name": "Ukraine", "freedom_house_slug": "ukraine", "world_bank_code": "UKR", "wb_url_code": "UA"},
    "vietnam": {"name": "Vietnam", "freedom_house_slug": "vietnam", "world_bank_code": "VNM", "wb_url_code": "VN"},
    "yemen": {"name": "Yémen", "freedom_house_slug": "yemen", "world_bank_code": "YEM", "wb_url_code": "YE"},
    "zambie": {"name": "Zambie", "freedom_house_slug": "zambia", "world_bank_code": "ZMB", "wb_url_code": "ZM"},
    "zimbabwe": {"name": "Zimbabwe", "freedom_house_slug": "zimbabwe", "world_bank_code": "ZWE", "wb_url_code": "ZW"},
}

INCOME_LABELS = {
    "LIC":  "Faible revenu",
    "LMC":  "Rev. interm. inf.",
    "UMC":  "Rev. interm. sup.",
    "HIC":  "Revenu élevé",
    "INX":  "Non classifié",
}

# ─────────────────────────────────────────────
# Utilitaires
# ─────────────────────────────────────────────

def flag_old(year):
    if year is None:
        return ""
    try:
        age = CURRENT_YEAR - int(year)
        if age > OLD_DATA_THRESHOLD:
            return f"donnée ancienne ({age} ans)"
    except Exception:
        pass
    return ""

def ind(label, value, unit, year, source, url=None, note=None):
    age_flag = flag_old(year) if note is None else note
    return {
        "label": label,
        "value": value if value is not None else "N/D",
        "unit":  unit or "",
        "year":  str(year) if year else "—",
        "source": source,
        "url":   url or "",
        "note":  age_flag or "",
    }

# ─────────────────────────────────────────────
# Signaux
# ─────────────────────────────────────────────

def get_signal(label, value):
    """Retourne (color_key, arrow_html)
    color_key in {green, lime, orange, red, slate, grey}
    """
    NA = ("grey",  '<span class="t-grey">—</span>')
    if str(value).strip() in ["N/D", "—", "À compléter", "Non disponible", "Indisponible", ""]:
        return NA

    lbl = label.lower()
    vs  = str(value).strip()

    # Freedom House statut
    if "statut" in lbl and "freedom" in lbl:
        m = {"Free": ("green", '<span class="t-green">↑</span>'),
             "Partly Free": ("orange", '<span class="t-orange">→</span>'),
             "Not Free": ("red", '<span class="t-red">↓</span>')}
        return m.get(vs, NA)

    # FH score /100
    if "freedom house" in lbl and "score" in lbl:
        try:
            s = int(vs.split("/")[0])
            if s >= 70: return "green",  '<span class="t-green">↑</span>'
            if s >= 40: return "orange", '<span class="t-orange">→</span>'
            return "red", '<span class="t-red">↓</span>'
        except: pass

    # Droits politiques /40
    if "droits politiques" in lbl:
        try:
            s = int(vs.split("/")[0])
            if s >= 28: return "green",  '<span class="t-green">↑</span>'
            if s >= 15: return "orange", '<span class="t-orange">→</span>'
            return "red", '<span class="t-red">↓</span>'
        except: pass

    # Libertés civiles /60
    if "libertés civiles" in lbl:
        try:
            s = int(vs.split("/")[0])
            if s >= 42: return "green",  '<span class="t-green">↑</span>'
            if s >= 22: return "orange", '<span class="t-orange">→</span>'
            return "red", '<span class="t-red">↓</span>'
        except: pass

    # IDH
    if "idh" in lbl and "valeur" in lbl:
        try:
            v = float(vs)
            if v >= 0.800: return "green",  '<span class="t-green">↑</span>'
            if v >= 0.700: return "lime",   '<span class="t-lime">↑</span>'
            if v >= 0.550: return "orange", '<span class="t-orange">→</span>'
            return "red", '<span class="t-red">↓</span>'
        except: pass

    # WGI
    if "wgi" in lbl:
        try:
            v = float(vs)
            if v >= 0.5:   return "green",  '<span class="t-green">↑</span>'
            if v >= -0.3:  return "orange", '<span class="t-orange">→</span>'
            return "red", '<span class="t-red">↓</span>'
        except: pass

    # Gini (bas = bien)
    if "gini" in lbl:
        try:
            v = float(vs)
            if v < 32: return "green",  '<span class="t-green">↑</span>'
            if v < 45: return "orange", '<span class="t-orange">→</span>'
            return "red", '<span class="t-red">↓</span>'
        except: pass

    # Pauvreté (bas = bien)
    if "pauvreté" in lbl:
        try:
            v = float(vs.replace("%",""))
            if v < 5:  return "green",  '<span class="t-green">↑</span>'
            if v < 20: return "orange", '<span class="t-orange">→</span>'
            return "red", '<span class="t-red">↓</span>'
        except: pass

    # PIB/habitant
    if "pib" in lbl and "habitant" in lbl:
        try:
            v = float(vs.replace("$","").replace(",",""))
            if v > 10000: return "green",  '<span class="t-green">↑</span>'
            if v > 3000:  return "orange", '<span class="t-orange">→</span>'
            return "red", '<span class="t-red">↓</span>'
        except: pass

    # Croissance
    if "croissance" in lbl:
        try:
            v = float(vs.replace(",","."))
            if v > 5:  return "green",  '<span class="t-green">↑</span>'
            if v > 2:  return "lime",   '<span class="t-lime">↑</span>'
            if v > 0:  return "orange", '<span class="t-orange">→</span>'
            return "red", '<span class="t-red">↓</span>'
        except: pass

    # Inflation (bas = bien)
    if "inflation" in lbl:
        try:
            v = float(vs.replace(",","."))
            if v < 4:  return "green",  '<span class="t-green">↑</span>'
            if v < 10: return "orange", '<span class="t-orange">→</span>'
            return "red", '<span class="t-red">↓</span>'
        except: pass

    # Chômage (bas = bien)
    if "chômage" in lbl:
        try:
            v = float(vs.replace(",","."))
            if v < 10: return "green",  '<span class="t-green">↑</span>'
            if v < 25: return "orange", '<span class="t-orange">→</span>'
            return "red", '<span class="t-red">↓</span>'
        except: pass

    # Emploi / scolarisation (haut = bien)
    if any(k in lbl for k in ["emploi", "scolarisation"]):
        try:
            v = float(vs.replace(",","."))
            if v > 75: return "green",  '<span class="t-green">↑</span>'
            if v > 50: return "orange", '<span class="t-orange">→</span>'
            return "red", '<span class="t-red">↓</span>'
        except: pass

    return "slate", '<span class="t-grey">—</span>'


# ─────────────────────────────────────────────
# Rendu
# ─────────────────────────────────────────────

# Indicateurs affichés en KPI cards (les plus importants)
KPI_LABELS = {
    "Freedom House — Statut",
    "Freedom House — Score",
    "IDH — Valeur",
    "PIB / habitant",
    "Croissance du PIB réel",
    "Inflation annuelle",
    "Taux de pauvreté (< 2,15 $/j)",
    "Indice de Gini",
    "WGI — État de droit",
    "WGI — Contrôle corruption",
    "Croissance moyenne depuis 2010",
}

def render_kpi(r):
    ck, arrow = get_signal(r["label"], r["value"])
    val_display = str(r["value"])
    unit = r["unit"]
    # Pour PIB/hab, tronquer l'unité dans le sous-titre
    sub = unit if unit else ""
    note_html = f'<div class="kpi-note">⚠ {r["note"]}</div>' if r["note"] else ""
    yr_html   = f'<div class="kpi-year">{r["year"]}</div>' if r["year"] and r["year"] != "—" else ""
    return f"""
<div class="kpi-card bt-{ck}">
  <div class="kpi-label">{r['label']}</div>
  <div class="kpi-value c-{ck}">{val_display}</div>
  <div class="kpi-sub">{sub}</div>
  {yr_html}
  {note_html}
  <div class="kpi-trend">{arrow}</div>
</div>"""

def render_row(r):
    ck, arrow = get_signal(r["label"], r["value"])
    unit  = f'<td class="ind-td ind-unit">{r["unit"]}</td>' if r["unit"] else '<td class="ind-td"></td>'
    yr    = f'<td class="ind-td ind-yr">{r["year"]}</td>'
    src   = (f'<td class="ind-td ind-src"><a href="{r["url"]}" target="_blank">↗</a></td>'
             if r["url"] else '<td class="ind-td"></td>')
    note_row = (f'<tr class="ind-tr"><td colspan="6" class="row-note">⚠ {r["note"]}</td></tr>'
                if r["note"] else "")
    return f"""
<tr class="ind-tr">
  <td class="ind-td ind-label">{r['label']}</td>
  <td class="ind-td ind-val c-{ck}">{r['value']}</td>
  {unit}{yr}
  <td class="ind-td ind-arrow">{arrow}</td>
  {src}
</tr>{note_row}"""


def show_section(label, rows):
    kpi_rows  = [r for r in rows if r["label"] in KPI_LABELS]
    list_rows = [r for r in rows if r["label"] not in KPI_LABELS]

    st.markdown(f'<div class="sec-label">{label}</div>', unsafe_allow_html=True)

    if kpi_rows:
        cards_html = "".join(render_kpi(r) for r in kpi_rows)
        st.markdown(f'<div class="kpi-grid">{cards_html}</div>', unsafe_allow_html=True)

    if list_rows:
        rows_html = "".join(render_row(r) for r in list_rows)
        st.markdown(
            f'<table class="ind-table">{rows_html}</table>',
            unsafe_allow_html=True
        )


def show_pillar(title, sections_data):
    st.markdown(f'<div class="pillar-title">{title}</div>', unsafe_allow_html=True)
    for sec_label, rows in sections_data:
        if rows:
            show_section(sec_label, rows)


def show_prompt(title, text):
    st.markdown(f'<div class="prompt-lbl">{title}</div>', unsafe_allow_html=True)
    st.text_area("", value=text, height=300,
                 help="Ctrl+A puis Ctrl+C pour copier.")


# ─────────────────────────────────────────────
# Collecte de données
# ─────────────────────────────────────────────

def fetch_freedom_house(slug, year=2026):
    url = f"https://freedomhouse.org/country/{slug}/freedom-world/{year}"
    try:
        r = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        text = re.sub(r"\s+", " ", BeautifulSoup(r.text, "html.parser").get_text(" ", strip=True))
        res = {"status": None, "score": None, "pr_score": None, "cl_score": None, "year": year, "url": url, "error": None}
        if   re.search(r"\bNot Free\b",   text): res["status"] = "Not Free"
        elif re.search(r"\bPartly Free\b", text): res["status"] = "Partly Free"
        elif re.search(r"\bFree\b",        text): res["status"] = "Free"
        m = re.search(r"(?:Total Score and Status|score)\s+(\d{1,3})\s*/?\s*100", text, re.I)
        if m: res["score"] = int(m.group(1))
        else:
            m2 = re.search(r"\b(\d{1,3})\s*/?\s*100\b", text)
            if m2: res["score"] = int(m2.group(1))
        pr = re.search(r"Political Rights\s+(\d{1,2})\s*/?\s*40", text, re.I)
        if pr: res["pr_score"] = int(pr.group(1))
        cl = re.search(r"Civil Liberties\s+(\d{1,2})\s*/?\s*60", text, re.I)
        if cl: res["cl_score"] = int(cl.group(1))
        return res
    except Exception as e:
        return {"error": str(e), "url": url}

def fetch_wb_latest(cc, ic):
    url = f"https://api.worldbank.org/v2/country/{cc}/indicator/{ic}?format=json&per_page=20&mrv=10"
    try:
        r = requests.get(url, timeout=20); r.raise_for_status()
        data = r.json()
        if not isinstance(data, list) or len(data) < 2 or not data[1]: return None, None
        for row in data[1]:
            if row.get("value") is not None:
                return row["value"], int(row["date"])
        return None, None
    except: return None, None

def fetch_wb_country_info(cc):
    url = f"https://api.worldbank.org/v2/country/{cc}?format=json"
    try:
        r = requests.get(url, timeout=20); r.raise_for_status()
        data = r.json()
        if not isinstance(data, list) or len(data) < 2 or not data[1]: return None
        c = data[1][0]
        return {"income_code": c.get("incomeLevel",{}).get("id",""),
                "income_label": c.get("incomeLevel",{}).get("value",""),
                "region": c.get("region",{}).get("value","")}
    except: return None

def fetch_wb_history(cc, ic, n=25):
    url = f"https://api.worldbank.org/v2/country/{cc}/indicator/{ic}?format=json&per_page=200"
    try:
        r = requests.get(url, timeout=25, headers={"User-Agent":"Mozilla/5.0"}); r.raise_for_status()
        data = r.json()
        if not isinstance(data,list) or len(data)<2 or not data[1]: return []
        rows = []
        for obs in data[1]:
            if obs.get("value") is not None:
                try: rows.append({"year": int(obs["date"]), "value": float(obs["value"])})
                except: pass
        rows.sort(key=lambda x: x["year"])
        return rows[-n:]
    except: return []

def latest(hist):
    if not hist: return None, None
    return hist[-1]["value"], hist[-1]["year"]

def avg_since(hist, y0=2010):
    v = [x["value"] for x in hist if x.get("year",0) >= y0]
    return sum(v)/len(v) if v else None

def avg_last(hist, n=10):
    v = [x["value"] for x in hist[-n:]]
    return sum(v)/len(v) if v else None

@st.cache_data(ttl=86400)
def load_hdi():
    url = "https://hdr.undp.org/sites/default/files/2025_HDR/HDR25_Statistical_Annex_HDI_Table.xlsx"
    r = requests.get(url, headers={"User-Agent":"Mozilla/5.0","Referer":"https://hdr.undp.org"}, timeout=30)
    r.raise_for_status()
    df = pd.read_excel(BytesIO(r.content), header=None, engine="openpyxl")
    rows = []
    for _, row in df.iterrows():
        v = list(row.dropna())
        if len(v) < 3: continue
        try:
            ri, hv = int(v[0]), float(v[2])
            if 0 < hv <= 1: rows.append({"rank": ri, "country": str(v[1]).strip(), "hdi": hv})
        except: pass
    return pd.DataFrame(rows)

def fetch_hdi(name):
    src = "https://hdr.undp.org/sites/default/files/2025_HDR/HDR25_Statistical_Annex_HDI_Table.xlsx"
    aliases = {
        "RDC (Congo-Kinshasa)": ["Congo (Democratic Republic of the)"],
        "Congo (Brazzaville)": ["Congo"],
        "Côte d'Ivoire": ["Côte d'Ivoire","Cote d'Ivoire"],
        "Tanzanie": ["Tanzania (United Republic of)"],
        "Bolivie": ["Bolivia (Plurinational State of)","Bolivia"],
        "Laos": ["Lao People's Democratic Republic"],
        "Syrie": ["Syrian Arab Republic"],
        "Vietnam": ["Viet Nam"],
    }
    try:
        df = load_hdi()
        if df.empty: return {"value":None,"rank":None,"year":2023,"source_url":src,"error":"Table vide"}
        names = [n.lower().strip() for n in [name]+aliases.get(name,[])]
        row = df[df["country"].str.lower().str.strip().isin(names)]
        if row.empty: return {"value":None,"rank":None,"year":2023,"source_url":src,"error":f"Introuvable: {name}"}
        f = row.iloc[0]
        return {"value":float(f["hdi"]),"rank":int(f["rank"]),"year":2023,"source_url":src,"error":None}
    except Exception as e:
        return {"value":None,"rank":None,"year":2023,"source_url":src,"error":str(e)}

# ─────────────────────────────────────────────
# Construction piliers
# ─────────────────────────────────────────────

def build_p1(wb_code, wb_url, fh, wb_info, hdi):
    ic = wb_info.get("income_code","") if wb_info else ""
    income = INCOME_LABELS.get(ic, wb_info.get("income_label","N/D") if wb_info else "N/D")
    region = wb_info.get("region","N/D") if wb_info else "N/D"

    # ── Politique
    pol = []
    if fh and not fh.get("error"):
        if fh.get("score")    is not None: pol.append(ind("Freedom House — Score",  f"{fh['score']}/100",  None, fh["year"], "Freedom House", fh["url"]))
        if fh.get("status"):               pol.append(ind("Freedom House — Statut", fh["status"],           None, fh["year"], "Freedom House", fh["url"]))
        if fh.get("pr_score") is not None: pol.append(ind("Droits politiques",       f"{fh['pr_score']}/40", None, fh["year"], "Freedom House", fh["url"]))
        if fh.get("cl_score") is not None: pol.append(ind("Libertés civiles",        f"{fh['cl_score']}/60", None, fh["year"], "Freedom House", fh["url"]))
    else:
        pol.append(ind("Freedom House","Indisponible",None,None,"Freedom House","https://freedomhouse.org","Erreur scraping"))
    pol.append(ind("EIU — Democracy Index","Non disponible",None,None,"EIU","https://www.eiu.com","Abonnement requis"))

    # ── Gouvernance WGI
    wgi_list = []
    wgi_codes = [
        ("VA.EST","WGI — Expression & responsabilité"),
        ("PV.EST","WGI — Stabilité politique"),
        ("GE.EST","WGI — Efficacité gouvernementale"),
        ("RQ.EST","WGI — Qualité réglementaire"),
        ("RL.EST","WGI — État de droit"),
        ("CC.EST","WGI — Contrôle corruption"),
    ]
    for code, lbl in wgi_codes:
        v, y = fetch_wb_latest(wb_code, code)
        wgi_list.append(ind(lbl, f"{v:.2f}" if v is not None else "N/D", "[-2.5;+2.5]", y,
                            "Banque mondiale (WGI)", "https://info.worldbank.org/governance/wgi/"))

    # ── Développement & inégalités
    dev = []
    if hdi.get("value") is not None:
        dev.append(ind("IDH — Valeur",     f"{hdi['value']:.3f}", None,  hdi["year"], "PNUD", hdi["source_url"]))
        if hdi.get("rank"):
            dev.append(ind("IDH — Rang mondial", str(hdi["rank"]),   None, hdi["year"], "PNUD", hdi["source_url"]))
    else:
        dev.append(ind("IDH","N/D",None,None,"PNUD",hdi.get("source_url",""),hdi.get("error","")))
    dev.append(ind("Statut de revenu", income, None, None, "Banque mondiale", wb_url))
    dev.append(ind("Région",           region, None, None, "Banque mondiale", wb_url))
    gv, gy = fetch_wb_latest(wb_code,"NY.GDP.PCAP.CD")
    if gv: dev.append(ind("PIB / habitant", f"${gv:,.0f}", "USD", gy, "Banque mondiale", wb_url))
    giniv, giniy = fetch_wb_latest(wb_code,"SI.POV.GINI")
    dev.append(ind("Indice de Gini", f"{giniv:.1f}" if giniv else "N/D", None, giniy, "Banque mondiale", wb_url,
                   None if giniv else "Enquêtes intermittentes"))
    pov, povy = fetch_wb_latest(wb_code,"SI.POV.DDAY")
    dev.append(ind("Taux de pauvreté (< 2,15 $/j)", f"{pov:.1f}" if pov else "N/D", "%", povy,
                   "Banque mondiale", wb_url, None if pov else "Absent pour revenus élevés"))

    # ── Marché du travail
    labour = []
    for code, lbl, unit, nt in [
        ("SL.EMP.TOTL.SP.ZS",   "Taux d'emploi total",          "%", None),
        ("SL.UEM.1524.ZS",       "Chômage des jeunes (15-24 ans)","%", None),
        ("SL.EMP.TOTL.SP.FE.ZS","Taux d'emploi des femmes",      "%", None),
        ("SL.ISV.IFRM.ZS",       "Taux d'informalité",            "%", "Souvent non disponible"),
    ]:
        v, y = fetch_wb_latest(wb_code, code)
        labour.append(ind(lbl, f"{v:.1f}" if v is not None else "N/D", unit, y,
                          "Banque mondiale / OIT", wb_url, None if v is not None else nt))

    # ── Éducation
    edu = []
    for code, lbl in [("SE.PRM.ENRR","Scolarisation primaire"),
                       ("SE.SEC.ENRR","Scolarisation secondaire"),
                       ("SE.TER.ENRR","Scolarisation tertiaire")]:
        v, y = fetch_wb_latest(wb_code, code)
        edu.append(ind(lbl, f"{v:.1f}" if v is not None else "N/D", "%", y, "Banque mondiale", wb_url))

    return [
        ("Régime politique & libertés", pol),
        ("Gouvernance (WGI)",           wgi_list),
        ("Développement & inégalités",  dev),
        ("Marché du travail",           labour),
        ("Éducation",                   edu),
    ]


def build_p2(wb_code):
    wb_url = "https://data.worldbank.org/indicator/"
    macro, struct, empl, demand, ext = [], [], [], [], []

    specs = [
        ("NY.GDP.MKTP.CD",      "PIB nominal total",                 "Mds USD", "macro"),
        ("NY.GDP.PCAP.CD",      "PIB par habitant",                  "USD",     "macro"),
        ("NY.GDP.MKTP.KD.ZG",   "Croissance du PIB réel",            "%",       "macro"),
        ("FP.CPI.TOTL.ZG",      "Inflation annuelle",                "%",       "macro"),
        ("NV.AGR.TOTL.ZS",      "Agriculture — part du PIB",         "% PIB",   "struct"),
        ("NV.IND.TOTL.ZS",      "Industrie — part du PIB",           "% PIB",   "struct"),
        ("NV.IND.MANF.ZS",      "Industrie manufacturière",          "% PIB",   "struct"),
        ("NV.SRV.TOTL.ZS",      "Services — part du PIB",            "% PIB",   "struct"),
        ("SL.AGR.EMPL.ZS",      "Emploi agricole",                   "% empl.", "empl"),
        ("SL.IND.EMPL.ZS",      "Emploi industriel",                 "% empl.", "empl"),
        ("SL.SRV.EMPL.ZS",      "Emploi dans les services",          "% empl.", "empl"),
        ("NE.CON.PRVT.ZS",      "Consommation privée",               "% PIB",   "demand"),
        ("NE.CON.GOVT.ZS",      "Consommation publique",             "% PIB",   "demand"),
        ("NE.GDI.FTOT.ZS",      "Formation brute de capital fixe",   "% PIB",   "demand"),
        ("NE.GDI.FPRV.ZS",      "Investissement privé",              "% PIB",   "demand"),
        ("FS.AST.PRVT.GD.ZS",   "Crédit secteur privé",              "% PIB",   "demand"),
        ("NE.EXP.GNFS.ZS",      "Exportations biens & services",     "% PIB",   "ext"),
        ("NE.IMP.GNFS.ZS",      "Importations biens & services",     "% PIB",   "ext"),
        ("BN.CAB.XOKA.GD.ZS",   "Solde courant",                     "% PIB",   "ext"),
        ("BX.KLT.DINV.WD.GD.ZS","IDE entrants nets",                 "% PIB",   "ext"),
        ("BX.TRF.PWKR.DT.GD.ZS","Transferts de migrants",            "% PIB",   "ext"),
    ]

    growth_hist = []
    buckets = {"macro": macro, "struct": struct, "empl": empl, "demand": demand, "ext": ext}

    for code, lbl, unit, bucket in specs:
        hist = fetch_wb_history(wb_code, code, 25)
        v, y = latest(hist)
        if code == "NY.GDP.MKTP.CD" and v is not None:
            disp = f"{v/1e9:,.1f}"
        elif v is not None:
            disp = f"{v:,.1f}"
        else:
            disp = "N/D"
        buckets[bucket].append(ind(lbl, disp, unit, y, "Banque mondiale", f"{wb_url}{code}"))
        if code == "NY.GDP.MKTP.KD.ZG":
            growth_hist = hist

    # Moyennes croissance
    a10 = avg_since(growth_hist, 2010)
    a10y = avg_last(growth_hist, 10)
    y2010 = [x["year"] for x in growth_hist if x["year"] >= 2010]
    p2010 = f"{min(y2010)}-{max(y2010)}" if y2010 else None
    y10y  = [x["year"] for x in growth_hist[-10:]]
    p10y  = f"{y10y[0]}-{y10y[-1]}" if len(y10y) >= 2 else None

    macro.append(ind("Croissance moyenne depuis 2010",
                     f"{a10:.1f}" if a10 is not None else "N/D",
                     "%", p2010, "Banque mondiale (calcul)", f"{wb_url}NY.GDP.MKTP.KD.ZG",
                     None if a10 is not None else "Série insuffisante"))
    macro.append(ind("Croissance moyenne — 10 ans",
                     f"{a10y:.1f}" if a10y is not None else "N/D",
                     "%", p10y, "Banque mondiale (calcul)", f"{wb_url}NY.GDP.MKTP.KD.ZG",
                     None if a10y is not None else "Série insuffisante"))

    # Manuel
    manual_items = [
        ("Part secteur extractif — PIB",          "struct", "Comptes nationaux / FMI Art. IV"),
        ("Part secteur extractif — exportations",  "ext",    "UN Comtrade / FMI Art. IV"),
        ("Part secteur extractif — recettes pub.", "ext",    "FMI Art. IV / DSA FMI"),
        ("Part du tourisme dans le PIB",           "struct", "WTTC / UN Tourism"),
        ("Croissance potentielle FMI",             "macro",  "FMI Art. IV"),
        ("Prévisions FMI (N / N+1)",               "macro",  "FMI Art. IV / WEO"),
        ("Réformes et chocs récents",              "macro",  "FMI Art. IV / Banque mondiale MPO"),
    ]
    for lbl, bucket, note in manual_items:
        buckets[bucket].append(ind(lbl, "À compléter", None, None, "Source sectorielle", "", note))

    return [
        ("Macroéconomie & croissance",        macro),
        ("Structure productive",              struct),
        ("Emploi sectoriel",                  empl),
        ("Demande & investissement",          demand),
        ("Ouverture & financement externe",   ext),
    ]

# ─────────────────────────────────────────────
# Prompts
# ─────────────────────────────────────────────

def make_prompt(country, sections, title, instructions):
    lines = [f"FICHE PAYS — {country.upper()}", title, "="*70, "", "DONNÉES", "-"*40]
    for _, rows in sections:
        for r in rows:
            u = f" {r['unit']}" if r["unit"] else ""
            y = f" ({r['year']})" if r["year"] and r["year"] != "—" else ""
            n = f" — ⚠ {r['note']}" if r["note"] else ""
            lines.append(f"• {r['label']} : {r['value']}{u}{y} — {r['source']}{n}")
    lines += ["", "="*70, "CONSIGNE", "-"*40, ""] + instructions
    return "\n".join(lines)

def prompt_p1(country, sections):
    return make_prompt(country, sections,
        "PILIER 1 : ENVIRONNEMENT POLITIQUE ET SOCIOÉCONOMIQUE",
        ["Rédige une analyse en 5 parties :",
         "1. Régime politique & libertés  2. Gouvernance  3. Développement & inégalités",
         "4. Marché du travail  5. Éducation",
         "", "Règles : pas de chiffres inventés · style institutionnel · ~450 mots."])

def prompt_p2(country, sections):
    return make_prompt(country, sections,
        "PILIER 2 : MODÈLE ÉCONOMIQUE ET RÉGIME DE CROISSANCE",
        ["Rédige une analyse en 2 parties :",
         "Partie 1 — Modèle économique (structure, secteurs, forces/fragilités)",
         "Partie 2 — Régime de croissance (rythme, moteurs, soutenabilité)",
         "", "Règles : pas de chiffres inventés · style institutionnel dense · ~550 mots."])

# ─────────────────────────────────────────────
# Interface
# ─────────────────────────────────────────────

st.markdown("""
<div class="afd-header">
  <h1>🌍 Outil de collecte de données — DER</h1>
  <p>Collecte automatique · Sources officielles · Prompt IA par pilier</p>
</div>""", unsafe_allow_html=True)

col1, col2 = st.columns([4, 1])
with col1:
    opts = dict(sorted({v["name"]: k for k, v in COUNTRY_MAPPING.items()}.items()))
    selected = st.selectbox("Pays", options=list(opts.keys()), label_visibility="collapsed")
with col2:
    st.write(""); st.write("")
    run = st.button("Collecter →")

if run:
    ci      = COUNTRY_MAPPING[opts[selected]]
    wb_code = ci["world_bank_code"]
    wb_url  = f"https://data.worldbank.org/country/{ci['wb_url_code']}"

    with st.spinner("Collecte en cours…"):
        fh      = fetch_freedom_house(ci["freedom_house_slug"])
        wb_info = fetch_wb_country_info(wb_code)
        hdi     = fetch_hdi(ci["name"])
        s1      = build_p1(wb_code, wb_url, fh, wb_info, hdi)
        s2      = build_p2(wb_code)

    show_pillar("Pilier 1 — Environnement politique et socioéconomique", s1)
    show_prompt("Prompt IA — Pilier 1", prompt_p1(selected, s1))

    st.markdown('<div class="pill-divider"></div>', unsafe_allow_html=True)

    show_pillar("Pilier 2 — Modèle économique et régime de croissance", s2)
    show_prompt("Prompt IA — Pilier 2", prompt_p2(selected, s2))

    st.markdown(
        f'<p class="footer-note">Collecte du {datetime.now().strftime("%d/%m/%Y à %H:%M")} · AFD — Direction des Études et Recherches</p>',
        unsafe_allow_html=True)
```

---

## Ce qui change

# **Logique tableau de bord** - les indicateurs les plus importants (IDH, PIB/hab, croissance, Freedom House, inflation, pauvreté, WGI clés) s'affichent en **grandes cartes KPI** avec valeur mise en avant, couleur de bordure et flèche. Les indicateurs détaillés restent en lignes compactes en dessous.

**Sections plates** — aucun onglet, aucun menu. Tout est visible d'un seul défilement, organisé par thème avec un séparateur discret.

**Signaux cohérents** — couleur de la valeur + flèche ↑ → ↓ adaptée à chaque indicateur (inflation basse = ↑ vert, chômage bas = ↑ vert, WGI positif = ↑ vert, etc.)": "mexico", "world_bank_code": "MEX", "wb_url_code": "MX"},
    "mozambique": {"name": "Mozambique", "freedom_house_slug": "mozambique", "world_bank_code": "MOZ", "wb_url_code": "MZ"},
    "niger": {"name": "Niger", "freedom_house_slug": "niger", "world_bank_code": "NER", "wb_url_code": "NE"},
    "nigeria": {"name": "Nigéria", "freedom_house_slug": "nigeria", "world_bank_code": "NGA", "wb_url_code": "NG"},
    "pakistan": {"name": "Pakistan", "freedom_house_slug": "pakistan", "world_bank_code": "PAK", "wb_url_code": "PK"},
    "perou": {"name": "Pérou", "freedom_house_slug": "peru", "world_bank_code": "PER", "wb_url_code": "PE"},
    "philippines": {"name": "Philippines", "freedom_house_slug": "philippines", "world_bank_code": "PHL", "wb_url_code": "PH"},
    "rdc": {"name": "RDC (Congo-Kinshasa)", "freedom_house_slug": "democratic-republic-of-congo", "world_bank_code": "COD", "wb_url_code": "CD"},
    "rwanda": {"name": "Rwanda", "freedom_house_slug": "rwanda", "world_bank_code": "RWA", "wb_url_code": "RW"},
    "senegal": {"name": "Sénégal", "freedom_house_slug": "senegal", "world_bank_code": "SEN", "wb_url_code": "SN"},
    "somalie": {"name": "Somalie", "freedom_house_slug": "somalia", "world_bank_code": "SOM", "wb_url_code": "SO"},
    "soudan": {"name": "Soudan", "freedom_house_slug": "sudan", "world_bank_code": "SDN", "wb_url_code": "SD"},
    "tanzanie": {"name": "Tanzanie", "freedom_house_slug": "tanzania", "world_bank_code": "TZA", "wb_url_code": "TZ"},
    "tchad": {"name": "Tchad", "freedom_house_slug": "chad", "world_bank_code": "TCD", "wb_url_code": "TD"},
    "tunisie": {"name": "Tunisie", "freedom_house_slug": "tunisia", "world_bank_code": "TUN", "wb_url_code": "TN"},
    "turquie": {"name": "Turquie", "freedom_house_slug": "turkey", "world_bank_code": "TUR", "wb_url_code": "TR"},
    "ukraine": {"name": "Ukraine", "freedom_house_slug": "ukraine", "world_bank_code": "UKR", "wb_url_code": "UA"},
    "vietnam": {"name": "Vietnam", "freedom_house_slug": "vietnam", "world_bank_code": "VNM", "wb_url_code": "VN"},
    "yemen": {"name": "Yémen", "freedom_house_slug": "yemen", "world_bank_code": "YEM", "wb_url_code": "YE"},
    "zambie": {"name": "Zambie", "freedom_house_slug": "zambia", "world_bank_code": "ZMB", "wb_url_code": "ZM"},
    "zimbabwe": {"name": "Zimbabwe", "freedom_house_slug": "zimbabwe", "world_bank_code": "ZWE", "wb_url_code": "ZW"},
}

INCOME_LABELS = {
    "LIC": "PFR — Faible revenu",
    "LMC": "PRITI — Rev. interm. inf.",
    "UMC": "PRITS — Rev. interm. sup.",
    "HIC": "PRE — Revenu élevé",
    "INX": "Non classifié",
}

# ─────────────────────────────────────────────
# Utilitaires
# ─────────────────────────────────────────────

def flag_old(year):
    if year is None:
        return ""
    try:
        age = CURRENT_YEAR - int(year)
        if age > OLD_DATA_THRESHOLD:
            return f"donnée ancienne ({age} ans)"
    except Exception:
        pass
    return ""


def make_row(label, value, unit, year, source, url="", note=None):
    note_val = flag_old(year) if note is None else (note or "")
    return {
        "label": label,
        "value": str(value) if value is not None else "N/D",
        "unit": unit or "",
        "year": str(year) if year else "—",
        "source": source or "",
        "url": url or "",
        "note": note_val or "",
    }


# ─────────────────────────────────────────────
# Codes couleur
# ─────────────────────────────────────────────

def badge_class(label, value):
    NA_VALS = {"N/D", "—", "À compléter", "Non disponible", "Indisponible", ""}
    if str(value).strip() in NA_VALS:
        return "bg-grey"

    lbl = label.lower()
    vs = str(value).strip()

    # Freedom House statut
    if "statut" in lbl and "freedom" in lbl:
        return {"Free": "bg-green", "Partly Free": "bg-orange", "Not Free": "bg-red"}.get(vs, "bg-grey")

    # Freedom House score /100
    if "freedom house" in lbl and "score" in lbl:
        try:
            s = int(vs.split("/")[0])
            return "bg-green" if s >= 70 else ("bg-orange" if s >= 40 else "bg-red")
        except: pass

    # Droits politiques /40
    if "droits politiques" in lbl:
        try:
            s = int(vs.split("/")[0])
            return "bg-green" if s >= 28 else ("bg-orange" if s >= 15 else "bg-red")
        except: pass

    # Libertés civiles /60
    if "libertés civiles" in lbl:
        try:
            s = int(vs.split("/")[0])
            return "bg-green" if s >= 42 else ("bg-orange" if s >= 22 else "bg-red")
        except: pass

    # IDH
    if "idh" in lbl and "valeur" in lbl:
        try:
            v = float(vs)
            if v >= 0.800: return "bg-green"
            if v >= 0.700: return "bg-lgreen"
            if v >= 0.550: return "bg-orange"
            return "bg-red"
        except: pass

    # WGI
    if "wgi" in lbl:
        try:
            v = float(vs)
            return "bg-green" if v >= 0.5 else ("bg-orange" if v >= -0.3 else "bg-red")
        except: pass

    # Gini
    if "gini" in lbl:
        try:
            v = float(vs)
            return "bg-green" if v < 32 else ("bg-orange" if v < 45 else "bg-red")
        except: pass

    # Pauvreté
    if "pauvreté" in lbl:
        try:
            v = float(vs.replace("%", ""))
            return "bg-green" if v < 5 else ("bg-orange" if v < 20 else "bg-red")
        except: pass

    # PIB/habitant
    if "pib" in lbl and "habitant" in lbl:
        try:
            v = float(vs.replace("$", "").replace(",", ""))
            return "bg-green" if v > 10000 else ("bg-orange" if v > 3000 else "bg-red")
        except: pass

    # Croissance
    if "croissance" in lbl:
        try:
            v = float(vs.replace(",", "."))
            if v > 5: return "bg-green"
            if v > 2: return "bg-lgreen"
            if v > 0: return "bg-orange"
            return "bg-red"
        except: pass

    # Inflation
    if "inflation" in lbl:
        try:
            v = float(vs.replace(",", "."))
            return "bg-green" if v < 4 else ("bg-orange" if v < 10 else "bg-red")
        except: pass

    # Chômage
    if "chômage" in lbl:
        try:
            v = float(vs.replace(",", "."))
            return "bg-green" if v < 10 else ("bg-orange" if v < 25 else "bg-red")
        except: pass

    # Emploi / scolarisation
    if any(k in lbl for k in ["emploi", "scolarisation"]):
        try:
            v = float(vs.replace(",", "."))
            return "bg-green" if v > 75 else ("bg-orange" if v > 50 else "bg-red")
        except: pass

    # Catégoriel
    if any(k in lbl for k in ["statut de revenu", "région"]):
        return "bg-purple"

    # Soldes, flux
    if any(k in lbl for k in ["ide", "solde", "exportations", "importations", "transferts"]):
        return "bg-blue"

    # Tenter numérique
    try:
        float(vs.replace(",", ".").replace("$", "").replace("%", "").replace(" ", ""))
        return "bg-blue"
    except:
        return "bg-grey"


def trend_icon(label, value):
    bc = badge_class(label, value)
    return {"bg-green": "▲", "bg-lgreen": "↗", "bg-orange": "→", "bg-red": "▼"}.get(bc, "")


# ─────────────────────────────────────────────
# Groupes thématiques
# ─────────────────────────────────────────────

GROUPS_P1 = [
    ("🗳️ Régime politique & libertés", [
        "Freedom House — Score", "Freedom House — Statut", "Freedom House",
        "Droits politiques", "Libertés civiles", "EIU — Democracy Index",
    ]),
    ("🏛️ Gouvernance (WGI)", [
        "WGI — Expression & responsabilité",
        "WGI — Stabilité politique & absence de violence",
        "WGI — Efficacité gouvernementale",
        "WGI — Qualité réglementaire",
        "WGI — État de droit",
        "WGI — Contrôle de la corruption",
    ]),
    ("💰 Développement & inégalités", [
        "IDH — Valeur", "IDH — Rang mondial", "IDH",
        "Statut de revenu (BM)", "Région BM",
        "PIB / habitant", "Indice de Gini", "Taux de pauvreté (< 2,15 $/j)",
    ]),
    ("👷 Marché du travail", [
        "Taux d'emploi total", "Chômage des jeunes (15-24 ans)",
        "Taux d'emploi des femmes", "Taux d'informalité",
    ]),
    ("📚 Éducation", [
        "Scolarisation primaire (taux brut)",
        "Scolarisation secondaire (taux brut)",
        "Scolarisation tertiaire (taux brut)",
    ]),
]

GROUPS_P2 = [
    ("📊 Macroéconomie", [
        "PIB nominal total", "PIB par habitant",
        "Croissance du PIB réel — dernière obs.",
        "Croissance moyenne PIB réel depuis 2010",
        "Croissance moyenne PIB réel — 10 dernières obs.",
        "Inflation annuelle",
    ]),
    ("🏗️ Structure productive", [
        "Agriculture — part du PIB", "Industrie — part du PIB",
        "Manufacturier — part du PIB", "Services — part du PIB",
        "Part secteur extractif — PIB", "Part du tourisme dans le PIB",
    ]),
    ("👥 Emploi sectoriel", [
        "Emploi agricole", "Emploi industriel", "Emploi dans les services",
    ]),
    ("💹 Demande & investissement", [
        "Consommation privée", "Consommation publique",
        "Formation brute de capital fixe", "Investissement privé",
        "Crédit domestique secteur privé",
    ]),
    ("🌍 Ouverture externe", [
        "Exportations biens et services", "Importations biens et services",
        "Solde courant", "IDE entrants nets", "Transferts de migrants",
    ]),
    ("🔭 Perspectives", [
        "Croissance potentielle FMI",
        "Prévisions FMI (année en cours / N+1)",
        "Réformes et chocs récents",
        "Part secteur extractif — exportations",
        "Part secteur extractif — recettes pub.",
    ]),
]

THEME_COLORS = {
    "🗳️ Régime politique & libertés":      "#dc2626",
    "🏛️ Gouvernance (WGI)":                "#003189",
    "💰 Développement & inégalités":        "#059669",
    "👷 Marché du travail":                 "#d97706",
    "📚 Éducation":                         "#7c3aed",
    "📊 Macroéconomie":                     "#003189",
    "🏗️ Structure productive":              "#d97706",
    "👥 Emploi sectoriel":                  "#059669",
    "💹 Demande & investissement":          "#0891b2",
    "🌍 Ouverture externe":                 "#475569",
    "🔭 Perspectives":                      "#7c3aed",
}


def group_rows(rows, groups):
    label_to_group = {}
    for gname, labels in groups:
        for l in labels:
            label_to_group[l] = gname

    buckets = {g[0]: [] for g in groups}
    other = []
    used = set()

    for r in rows:
        lbl = r["label"]
        g = label_to_group.get(lbl)
        if g and lbl not in used:
            buckets[g].append(r)
            used.add(lbl)

    for r in rows:
        if r["label"] not in used:
            other.append(r)
            used.add(r["label"])

    result = [(g, buckets[g]) for g, _ in groups if buckets[g]]
    if other:
        result.append(("📎 Autres", other))
    return result


# ─────────────────────────────────────────────
# Collecte des données (parallélisée)
# ─────────────────────────────────────────────

def fetch_freedom_house(slug, year=2026):
    url = f"https://freedomhouse.org/country/{slug}/freedom-world/{year}"
    try:
        r = requests.get(url, timeout=20,
                         headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        text = re.sub(r"\s+", " ", BeautifulSoup(r.text, "html.parser").get_text(" ", strip=True))
        res = {"status": None, "score": None, "pr_score": None,
               "cl_score": None, "year": year, "url": url, "error": None}
        if re.search(r"\bNot Free\b", text):      res["status"] = "Not Free"
        elif re.search(r"\bPartly Free\b", text): res["status"] = "Partly Free"
        elif re.search(r"\bFree\b", text):        res["status"] = "Free"
        m = re.search(r"(?:Total Score and Status|score)\s+(\d{1,3})\s*/?\s*100", text, re.I)
        if m: res["score"] = int(m.group(1))
        else:
            m2 = re.search(r"\b(\d{1,3})\s*/?\s*100\b", text)
            if m2: res["score"] = int(m2.group(1))
        pr = re.search(r"Political Rights\s+(\d{1,2})\s*/?\s*40", text, re.I)
        if pr: res["pr_score"] = int(pr.group(1))
        cl = re.search(r"Civil Liberties\s+(\d{1,2})\s*/?\s*60", text, re.I)
        if cl: res["cl_score"] = int(cl.group(1))
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
    url = (f"https://api.worldbank.org/v2/country/{country_code}"
           f"/indicator/{indicator_code}?format=json&per_page=20&mrv=10")
    data = _wb_get(url)
    if not isinstance(data, list) or len(data) < 2 or not data[1]:
        return None, None
    for row in data[1]:
        if row.get("value") is not None:
            return row["value"], int(row["date"])
    return None, None


def fetch_wb_history(country_code, indicator_code, n=25):
    url = (f"https://api.worldbank.org/v2/country/{country_code}"
           f"/indicator/{indicator_code}?format=json&per_page=200")
    data = _wb_get(url)
    if not isinstance(data, list) or len(data) < 2 or not data[1]:
        return []
    rows = []
    for obs in data[1]:
        if obs.get("value") is not None:
            try:
                rows.append({"year": int(obs["date"]), "value": float(obs["value"])})
            except: pass
    rows.sort(key=lambda x: x["year"])
    return rows[-n:]


def fetch_wb_country_info(cc):
    data = _wb_get(f"https://api.worldbank.org/v2/country/{cc}?format=json")
    if not isinstance(data, list) or len(data) < 2 or not data[1]:
        return None
    c = data[1][0]
    return {
        "income_code":  c.get("incomeLevel", {}).get("id", ""),
        "income_label": c.get("incomeLevel", {}).get("value", ""),
        "region":       c.get("region", {}).get("value", ""),
    }


def latest(hist):
    if not hist: return None, None
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
        r = requests.get(url, timeout=30,
                         headers={"User-Agent": "Mozilla/5.0",
                                  "Referer": "https://hdr.undp.org"})
        r.raise_for_status()
        df = pd.read_excel(BytesIO(r.content), header=None, engine="openpyxl")
        rows = []
        for _, row in df.iterrows():
            v = list(row.dropna())
            if len(v) < 3: continue
            try:
                ri, hv = int(v[0]), float(v[2])
                if 0 < hv <= 1:
                    rows.append({"rank": ri, "country": str(v[1]).strip(), "hdi": hv})
            except: pass
        return pd.DataFrame(rows)
    except:
        return pd.DataFrame()


def fetch_hdi(name):
    src = "https://hdr.undp.org/data-center/human-development-index"
    aliases = {
        "RDC (Congo-Kinshasa)": ["Congo (Democratic Republic of the)"],
        "Côte d'Ivoire": ["Côte d'Ivoire", "Cote d'Ivoire"],
        "Tanzanie": ["Tanzania (United Republic of)"],
        "Bolivie": ["Bolivia (Plurinational State of)", "Bolivia"],
        "Laos": ["Lao People's Democratic Republic"],
        "Syrie": ["Syrian Arab Republic"],
        "Vietnam": ["Viet Nam"],
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


# ─────────────────────────────────────────────
# Construction des piliers (parallélisée)
# ─────────────────────────────────────────────

# Tous les codes WB à collecter pour P1
WB_CODES_P1 = [
    "NY.GDP.PCAP.CD",
    "SI.POV.GINI",
    "SI.POV.DDAY",
    "VA.EST", "PV.EST", "GE.EST", "RQ.EST", "RL.EST", "CC.EST",
    "SL.EMP.TOTL.SP.ZS", "SL.UEM.1524.ZS", "SL.EMP.TOTL.SP.FE.ZS", "SL.ISV.IFRM.ZS",
    "SE.PRM.ENRR", "SE.SEC.ENRR", "SE.TER.ENRR",
]

WB_CODES_P2_LATEST = [
    "NY.GDP.MKTP.CD", "NY.GDP.PCAP.CD", "FP.CPI.TOTL.ZG",
    "NV.AGR.TOTL.ZS", "NV.IND.TOTL.ZS", "NV.IND.MANF.ZS", "NV.SRV.TOTL.ZS",
    "SL.AGR.EMPL.ZS", "SL.IND.EMPL.ZS", "SL.SRV.EMPL.ZS",
    "NE.CON.PRVT.ZS", "NE.CON.GOVT.ZS", "NE.GDI.FTOT.ZS", "NE.GDI.FPRV.ZS",
    "BX.KLT.DINV.WD.GD.ZS", "BX.TRF.PWKR.DT.GD.ZS", "FS.AST.PRVT.GD.ZS",
    "NE.EXP.GNFS.ZS", "NE.IMP.GNFS.ZS", "BN.CAB.XOKA.GD.ZS",
]


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_all_wb(country_code):
    """Collecte parallèle de tous les indicateurs WB."""
    all_codes = list(set(WB_CODES_P1 + WB_CODES_P2_LATEST + ["NY.GDP.MKTP.KD.ZG"]))
    results = {}

    def fetch_one(code):
        # Pour la croissance, on récupère l'historique
        if code == "NY.GDP.MKTP.KD.ZG":
            hist = fetch_wb_history(country_code, code, 25)
            v, y = latest(hist)
            return code, {"value": v, "year": y, "history": hist}
        else:
            v, y = fetch_wb_indicator(country_code, code)
            return code, {"value": v, "year": y}

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(fetch_one, c): c for c in all_codes}
        for future in as_completed(futures):
            try:
                code, result = future.result(timeout=30)
                results[code] = result
            except Exception:
                results[futures[future]] = {"value": None, "year": None}

    return results


def build_pillar1(wb_code, wb_url_base, fh, wb_info, hdi, wb_data):
    rows = []
    ic = wb_info.get("income_code", "") if wb_info else ""
    income = INCOME_LABELS.get(ic, wb_info.get("income_label", "N/D") if wb_info else "N/D")
    region = wb_info.get("region", "N/D") if wb_info else "N/D"

    # Freedom House
    if fh and not fh.get("error"):
        if fh.get("score") is not None:
            rows.append(make_row("Freedom House — Score", f"{fh['score']}/100", None, fh["year"], "Freedom House", fh["url"]))
        if fh.get("status"):
            rows.append(make_row("Freedom House — Statut", fh["status"], None, fh["year"], "Freedom House", fh["url"]))
        if fh.get("pr_score") is not None:
            rows.append(make_row("Droits politiques", f"{fh['pr_score']}/40", None, fh["year"], "Freedom House", fh["url"]))
        if fh.get("cl_score") is not None:
            rows.append(make_row("Libertés civiles", f"{fh['cl_score']}/60", None, fh["year"], "Freedom House", fh["url"]))
    else:
        rows.append(make_row("Freedom House", "Indisponible", None, None, "Freedom House",
                             "https://freedomhouse.org", "Erreur scraping"))

    rows.append(make_row("EIU — Democracy Index", "Non disponible", None, None,
                         "EIU", "https://www.eiu.com", "Abonnement requis"))

    # IDH
    if hdi.get("value") is not None:
        rows.append(make_row("IDH — Valeur", f"{hdi['value']:.3f}", None, hdi["year"], "PNUD", hdi["url"]))
        if hdi.get("rank"):
            rows.append(make_row("IDH — Rang mondial", str(hdi["rank"]), None, hdi["year"], "PNUD", hdi["url"]))
    else:
        rows.append(make_row("IDH", "N/D", None, None, "PNUD", hdi.get("url", ""), hdi.get("error", "")))

    rows.append(make_row("Statut de revenu (BM)", income, None, None, "Banque mondiale", wb_url_base))
    rows.append(make_row("Région BM", region, None, None, "Banque mondiale", wb_url_base))

    # PIB/habitant
    d = wb_data.get("NY.GDP.PCAP.CD", {})
    if d.get("value"):
        rows.append(make_row("PIB / habitant", f"${d['value']:,.0f}", "USD", d.get("year"), "Banque mondiale", wb_url_base))

    # Gini
    d = wb_data.get("SI.POV.GINI", {})
    v = d.get("value")
    rows.append(make_row("Indice de Gini", f"{v:.1f}" if v else "N/D", None, d.get("year"),
                         "Banque mondiale", wb_url_base, None if v else "Enquêtes intermittentes"))

    # Pauvreté
    d = wb_data.get("SI.POV.DDAY", {})
    v = d.get("value")
    rows.append(make_row("Taux de pauvreté (< 2,15 $/j)", f"{v:.1f}" if v else "N/D", "%", d.get("year"),
                         "Banque mondiale", wb_url_base, None if v else "Absent pour revenus élevés"))

    # WGI
    wgi_map = {
        "VA.EST": "WGI — Expression & responsabilité",
        "PV.EST": "WGI — Stabilité politique & absence de violence",
        "GE.EST": "WGI — Efficacité gouvernementale",
        "RQ.EST": "WGI — Qualité réglementaire",
        "RL.EST": "WGI — État de droit",
        "CC.EST": "WGI — Contrôle de la corruption",
    }
    wgi_url = "https://info.worldbank.org/governance/wgi/"
    for code, label in wgi_map.items():
        d = wb_data.get(code, {})
        v = d.get("value")
        rows.append(make_row(label, f"{v:.2f}" if v is not None else "N/D",
                             "[-2.5;+2.5]", d.get("year"), "Banque mondiale (WGI)", wgi_url))

    # Emploi
    labour_map = {
        "SL.EMP.TOTL.SP.ZS":  ("Taux d'emploi total", "%", None),
        "SL.UEM.1524.ZS":      ("Chômage des jeunes (15-24 ans)", "%", None),
        "SL.EMP.TOTL.SP.FE.ZS":("Taux d'emploi des femmes", "%", None),
        "SL.ISV.IFRM.ZS":      ("Taux d'informalité", "%", "Souvent non disponible"),
    }
    for code, (label, unit, nt) in labour_map.items():
        d = wb_data.get(code, {})
        v = d.get("value")
        rows.append(make_row(label, f"{v:.1f}" if v is not None else "N/D", unit, d.get("year"),
                             "Banque mondiale / OIT", wb_url_base, None if v is not None else nt))

    # Éducation
    edu_map = {
        "SE.PRM.ENRR": ("Scolarisation primaire (taux brut)", "%"),
        "SE.SEC.ENRR": ("Scolarisation secondaire (taux brut)", "%"),
        "SE.TER.ENRR": ("Scolarisation tertiaire (taux brut)", "%"),
    }
    for code, (label, unit) in edu_map.items():
        d = wb_data.get(code, {})
        v = d.get("value")
        rows.append(make_row(label, f"{v:.1f}" if v is not None else "N/D", unit, d.get("year"),
                             "Banque mondiale / UNESCO", wb_url_base))

    return rows


def build_pillar2(wb_code, wb_url_base, wb_data):
    rows = []
    wb_url = "https://data.worldbank.org/indicator/"

    p2_labels = {
        "NY.GDP.MKTP.CD":       ("PIB nominal total",                    "Mds USD"),
        "NY.GDP.PCAP.CD":       ("PIB par habitant",                     "USD"),
        "FP.CPI.TOTL.ZG":       ("Inflation annuelle",                   "%"),
        "NV.AGR.TOTL.ZS":       ("Agriculture — part du PIB",            "% PIB"),
        "NV.IND.TOTL.ZS":       ("Industrie — part du PIB",              "% PIB"),
        "NV.IND.MANF.ZS":       ("Manufacturier — part du PIB",          "% PIB"),
        "NV.SRV.TOTL.ZS":       ("Services — part du PIB",               "% PIB"),
        "SL.AGR.EMPL.ZS":       ("Emploi agricole",                      "% emploi"),
        "SL.IND.EMPL.ZS":       ("Emploi industriel",                    "% emploi"),
        "SL.SRV.EMPL.ZS":       ("Emploi dans les services",             "% emploi"),
        "NE.CON.PRVT.ZS":       ("Consommation privée",                  "% PIB"),
        "NE.CON.GOVT.ZS":       ("Consommation publique",                "% PIB"),
        "NE.GDI.FTOT.ZS":       ("Formation brute de capital fixe",      "% PIB"),
        "NE.GDI.FPRV.ZS":       ("Investissement privé",                 "% PIB"),
        "BX.KLT.DINV.WD.GD.ZS":("IDE entrants nets",                    "% PIB"),
        "BX.TRF.PWKR.DT.GD.ZS":("Transferts de migrants",               "% PIB"),
        "FS.AST.PRVT.GD.ZS":    ("Crédit domestique secteur privé",      "% PIB"),
        "NE.EXP.GNFS.ZS":       ("Exportations biens et services",       "% PIB"),
        "NE.IMP.GNFS.ZS":       ("Importations biens et services",       "% PIB"),
        "BN.CAB.XOKA.GD.ZS":    ("Solde courant",                        "% PIB"),
    }

    for code, (label, unit) in p2_labels.items():
        d = wb_data.get(code, {})
        v = d.get("value")
        if code == "NY.GDP.MKTP.CD" and v is not None:
            disp = f"{v / 1e9:,.1f}"
        elif v is not None:
            disp = f"{v:,.1f}"
        else:
            disp = "N/D"
        rows.append(make_row(label, disp, unit, d.get("year"), "Banque mondiale", f"{wb_url}{code}"))

    # Croissance (historique)
    d = wb_data.get("NY.GDP.MKTP.KD.ZG", {})
    v_last = d.get("value")
    y_last = d.get("year")
    hist   = d.get("history", [])

    rows.append(make_row("Croissance du PIB réel — dernière obs.",
                         f"{v_last:.1f}" if v_last is not None else "N/D",
                         "%", y_last, "Banque mondiale", f"{wb_url}NY.GDP.MKTP.KD.ZG"))

    a10  = avg_since(hist, 2010)
    a10y = avg_last(hist, 10)
    y2010 = [x["year"] for x in hist if x["year"] >= 2010]
    p2010 = f"{min(y2010)}-{max(y2010)}" if y2010 else None
    y10y  = [x["year"] for x in hist[-10:]]
    p10y  = f"{y10y[0]}-{y10y[-1]}" if len(y10y) >= 2 else None

    rows.append(make_row("Croissance moyenne PIB réel depuis 2010",
                         f"{a10:.1f}" if a10 is not None else "N/D",
                         "%", p2010, "Banque mondiale (calcul)", f"{wb_url}NY.GDP.MKTP.KD.ZG",
                         None if a10 is not None else "Série insuffisante"))
    rows.append(make_row("Croissance moyenne PIB réel — 10 dernières obs.",
                         f"{a10y:.1f}" if a10y is not None else "N/D",
                         "%", p10y, "Banque mondiale (calcul)", f"{wb_url}NY.GDP.MKTP.KD.ZG",
                         None if a10y is not None else "Série insuffisante"))

    # Manuel
    manual = [
        ("Part secteur extractif — PIB",          "Comptes nationaux / FMI Art. IV / EITI"),
        ("Part secteur extractif — exportations",  "UN Comtrade / OEC / FMI Art. IV"),
        ("Part secteur extractif — recettes pub.", "FMI Art. IV / DSA FMI"),
        ("Part du tourisme dans le PIB",           "WTTC / UN Tourism / FMI Art. IV"),
        ("Croissance potentielle FMI",             "FMI Art. IV"),
        ("Prévisions FMI (année en cours / N+1)",  "FMI Art. IV / WEO"),
        ("Réformes et chocs récents",              "FMI Art. IV / Banque mondiale MPO"),
    ]
    for label, note in manual:
        rows.append(make_row(label, "À compléter", None, None, "Source sectorielle", "", note))

    return rows


# ─────────────────────────────────────────────
# Rendu HTML des indicateurs
# ─────────────────────────────────────────────

def render_group(group_name, rows, color):
    """Génère le HTML d'un groupe d'indicateurs."""
    lines = [f"""
<div class="theme-wrap" style="border-left-color:{color};">
<div class="theme-title" style="color:{color};">{group_name}</div>
"""]
    for r in rows:
        bc   = badge_class(r["label"], r["value"])
        icon = trend_icon(r["label"], r["value"])
        disp = f"{icon} {r['value']}" if icon else r["value"]
        unit = f'<span class="ind-unit">{r["unit"]}</span>' if r["unit"] else ""
        yr   = f'<span class="ind-year">{r["year"]}</span>' if r["year"] not in ("", "—") else ""
        src  = (f'<span class="ind-src"><a href="{r["url"]}" target="_blank">↗ {r["source"]}</a></span>'
                if r["url"] else f'<span class="ind-src">{r["source"]}</span>')
        note = f'<span class="ind-note">⚠ {r["note"]}</span>' if r["note"] else ""
        lines.append(f"""
<div class="ind-row">
  <span class="ind-lbl">{r["label"]}</span>
  <span class="ind-badge {bc}">{disp}</span>
  {unit}{yr}{src}{note}
</div>""")
    lines.append("</div>")
    return "".join(lines)


def show_summary(rows):
    total     = len(rows)
    available = sum(1 for r in rows if r["value"] not in
                    ["N/D", "—", "À compléter", "Non disponible", "Indisponible"])
    green     = sum(1 for r in rows if badge_class(r["label"], r["value"])
                    in ("bg-green", "bg-lgreen"))
    red       = sum(1 for r in rows if badge_class(r["label"], r["value"]) == "bg-red")
    pct       = int(100 * available / total) if total else 0

    st.markdown(f"""
<div class="summary-row">
  <div class="s-card">
    <div class="s-val">{total}</div>
    <div class="s-lbl">Indicateurs</div>
  </div>
  <div class="s-card" style="border-top-color:#0891b2;">
    <div class="s-val" style="color:#0891b2;">{pct}%</div>
    <div class="s-lbl">Couverture</div>
  </div>
  <div class="s-card" style="border-top-color:#059669;">
    <div class="s-val" style="color:#059669;">{green}</div>
    <div class="s-lbl">Signaux positifs</div>
  </div>
  <div class="s-card" style="border-top-color:#dc2626;">
    <div class="s-val" style="color:#dc2626;">{red}</div>
    <div class="s-lbl">Signaux d'alerte</div>
  </div>
</div>
<div class="legend">
  <div class="legend-item"><div class="ldot" style="background:#15803d;"></div>Favorable</div>
  <div class="legend-item"><div class="ldot" style="background:#16a34a;"></div>Plutôt favorable</div>
  <div class="legend-item"><div class="ldot" style="background:#c2410c;"></div>Intermédiaire</div>
  <div class="legend-item"><div class="ldot" style="background:#b91c1c;"></div>Défavorable</div>
  <div class="legend-item"><div class="ldot" style="background:#1d4ed8;"></div>Informatif</div>
  <div class="legend-item"><div class="ldot" style="background:#7c3aed;"></div>Qualitatif</div>
  <div class="legend-item"><div class="ldot" style="background:#94a3b8;"></div>Non disponible</div>
  <span style="margin-left:auto;font-size:11px;color:#f59e0b;">⚠ = donnée ancienne ou manquante</span>
</div>
""", unsafe_allow_html=True)


def show_pillar(title, subtitle, rows, groups):
    st.markdown(f'<div class="pillar-header">{title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="pillar-sub">{subtitle}</div>', unsafe_allow_html=True)

    show_summary(rows)

    grouped = group_rows(rows, groups)
    tab_names = [g[0] for g in grouped]

    if not tab_names:
        st.info("Aucune donnée disponible.")
        return

    tabs = st.tabs(tab_names)
    for tab, (gname, grows) in zip(tabs, grouped):
        with tab:
            color = THEME_COLORS.get(gname, "#003189")
            st.markdown(render_group(gname, grows, color), unsafe_allow_html=True)

    # Vue complète
    with st.expander("📋 Tableau complet", expanded=False):
        df = pd.DataFrame([{
            "Indicateur": r["label"],
            "Valeur":     r["value"],
            "Unité":      r["unit"],
            "Année":      r["year"],
            "Source":     r["source"],
            "Lien":       r["url"],
            "Note":       r["note"],
        } for r in rows])
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={"Lien": st.column_config.LinkColumn("Lien", display_text="↗")}
        )


def show_prompt(title, text):
    st.markdown(f'<div class="prompt-title">🤖 {title}</div>', unsafe_allow_html=True)
    st.text_area("", value=text, height=320,
                 help="Ctrl+A puis Ctrl+C pour copier.")


# ─────────────────────────────────────────────
# Prompts
# ─────────────────────────────────────────────

def make_prompt(country, rows, pillar_title, instructions):
    lines = [f"FICHE PAYS — {country.upper()}", pillar_title, "=" * 70,
             "", "DONNÉES COLLECTÉES", "-" * 40]
    for r in rows:
        u = f" {r['unit']}" if r["unit"] else ""
        y = f" ({r['year']})" if r["year"] not in ("", "—") else ""
        n = f" — ⚠ {r['note']}" if r["note"] else ""
        lines.append(f"• {r['label']} : {r['value']}{u}{y} — {r['source']}{n}")
    lines += ["", "=" * 70, "CONSIGNE", "-" * 40, ""] + instructions
    return "\n".join(lines)


def prompt_p1(country, rows):
    return make_prompt(country, rows,
        "PILIER 1 : ENVIRONNEMENT POLITIQUE ET SOCIOÉCONOMIQUE", [
        "Rédige une analyse en 5 parties :",
        "1. Régime politique & libertés",
        "2. Gouvernance institutionnelle (WGI)",
        "3. Développement humain & inégalités",
        "4. Marché du travail",
        "5. Capital humain & éducation",
        "",
        "Règles : pas de chiffres inventés · signaler les lacunes · style institutionnel · ~450 mots.",
    ])


def prompt_p2(country, rows):
    return make_prompt(country, rows,
        "PILIER 2 : MODÈLE ÉCONOMIQUE ET RÉGIME DE CROISSANCE", [
        "Rédige une analyse en 2 parties :",
        "Partie 1 — Modèle économique : structure, secteurs, forces/fragilités",
        "Partie 2 — Régime de croissance : rythme, moteurs, soutenabilité",
        "",
        "Règles : pas de chiffres inventés · style institutionnel dense · ~550 mots.",
    ])


# ─────────────────────────────────────────────
# Interface
# ─────────────────────────────────────────────

st.markdown("""
<div class="afd-header">
  <h1>🌍 Outil de collecte de données — DER</h1>
  <p>Collecte automatique · Sources officielles · Classification thématique · Codes couleur · Prompt IA</p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([4, 1])
with col1:
    opts = dict(sorted({v["name"]: k for k, v in COUNTRY_MAPPING.items()}.items()))
    selected = st.selectbox("🌐 Pays", options=list(opts.keys()),
                            label_visibility="visible")
with col2:
    st.write(""); st.write("")
    run = st.button("Collecter →")

if run:
    ci      = COUNTRY_MAPPING[opts[selected]]
    wb_code = ci["world_bank_code"]
    wb_url  = f"https://data.worldbank.org/country/{ci['wb_url_code']}"

    # Collecte parallèle
    prog = st.progress(0, text="Initialisation…")

    prog.progress(10, text="Freedom House…")
    fh = fetch_freedom_house(ci["freedom_house_slug"])

    prog.progress(25, text="Informations pays (Banque mondiale)…")
    wb_info = fetch_wb_country_info(wb_code)

    prog.progress(35, text="IDH — PNUD…")
    hdi = fetch_hdi(ci["name"])

    prog.progress(45, text="Indicateurs Banque mondiale (parallèle)…")
    wb_data = fetch_all_wb(wb_code)

    prog.progress(85, text="Construction des piliers…")
    p1 = build_pillar1(wb_code, wb_url, fh, wb_info, hdi, wb_data)
    p2 = build_pillar2(wb_code, wb_url, wb_data)

    prog.progress(100, text="Terminé ✓")
    prog.empty()

    # ── Pilier 1
    show_pillar(
        "📌 Pilier 1 — Environnement politique et socioéconomique",
        "Freedom House · IDH · Gouvernance WGI · Emploi · Pauvreté · Éducation",
        p1, GROUPS_P1
    )
    show_prompt("Prompt IA — Pilier 1", prompt_p1(selected, p1))

    st.markdown("---")

    # ── Pilier 2
    show_pillar(
        "📈 Pilier 2 — Modèle économique et régime de croissance",
        "Structure productive · Emploi sectoriel · Demande · Financement · Ouverture · Croissance",
        p2, GROUPS_P2
    )
    show_prompt("Prompt IA — Pilier 2", prompt_p2(selected, p2))

    st.markdown(
        f'<p class="footer-note">Collecte du {datetime.now().strftime("%d/%m/%Y à %H:%M")} '
        f'· AFD — Direction des Études et Recherches</p>',
        unsafe_allow_html=True
    )
```

---

## Pourquoi ça ne chargeait pas — et ce qui a changé

### 🔴 Problème principal : ~35 appels API séquentiels
Chaque indicateur World Bank faisait un appel séparé, l'un après l'autre. Avec 15+ indicateurs × 2 sec de latence = **30–50 secondes de blocage** avant le moindre affichage.

**✅ Fix : `ThreadPoolExecutor` avec 10 workers simultanés** — tous les indicateurs WB sont collectés en **parallèle** via `fetch_all_wb()`, réduisant le temps de ~40s à ~5s.

### 🔴 Cache manquant sur la collecte WB
**✅ Fix : `@st.cache_data(ttl=3600)`** sur `fetch_all_wb` — les données sont gardées 1h, rechargement instantané.

### 🔴 HTML complexe rendu en bloc
Des centaines de lignes HTML injectées via `st.markdown` en une fois pouvaient bloquer le rendu.  
**✅ Fix : rendu HTML allégé** par groupe, chaque onglet rendu indépendamment.

### ➕ Barre de progression
Un `st.progress()` avec étapes nommées montre l'avancement en temps réel.
