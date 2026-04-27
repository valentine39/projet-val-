import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from io import BytesIO

# ─────────────────────────────
# CONFIG
# ─────────────────────────────
st.set_page_config(
    page_title="Outil de collecte de données - DER",
    layout="centered"
)

st.title("🌍 Outil de collecte de données - DER")

# ─────────────────────────────
# COUNTRY MAPPING (simplifié)
# ─────────────────────────────
COUNTRY_MAPPING = {
    "France": {
        "freedom_house_slug": "france",
        "world_bank_code": "FRA",
        "undp_code": "FRA"
    },
    "Timor-Leste": {
        "freedom_house_slug": "timor-leste",
        "world_bank_code": "TLS",
        "undp_code": "TLS"
    },
    "Kenya": {
        "freedom_house_slug": "kenya",
        "world_bank_code": "KEN",
        "undp_code": "KEN"
    }
}

# ─────────────────────────────
# FREEDOM HOUSE
# ─────────────────────────────
def fetch_freedom_house(slug):
    url = f"https://freedomhouse.org/country/{slug}/freedom-world/2026"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        r = requests.get(url, headers=headers, timeout=20)
        soup = BeautifulSoup(r.text, "html.parser")
        text = soup.get_text(" ", strip=True)

        score = re.search(r"(\d{1,3})\s*/\s*100", text)
        status = re.search(r"(Free|Partly Free|Not Free)", text)

        return {
            "score": int(score.group(1)) if score else None,
            "status": status.group(1) if status else None,
            "url": url
        }
    except:
        return {"score": None, "status": None, "url": url}

# ─────────────────────────────
# WORLD BANK
# ─────────────────────────────
def fetch_wb(code, indicator):
    url = f"https://api.worldbank.org/v2/country/{code}/indicator/{indicator}?format=json"

    try:
        r = requests.get(url, timeout=20).json()
        data = r[1]
        for d in data:
            if d["value"] is not None:
                return d["value"], d["date"]
    except:
        return None, None

    return None, None

# ─────────────────────────────
# UNDP HDI (FIX 403)
# ─────────────────────────────
@st.cache_data(ttl=86400)
def load_hdi_table():

    url = "https://hdr.undp.org/sites/default/files/2025_HDR/HDR25_Statistical_Annex_HDI_Table.xlsx"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://hdr.undp.org/"
    }

    r = requests.get(url, headers=headers)
    r.raise_for_status()

    file = BytesIO(r.content)

    df_raw = pd.read_excel(file, header=None)

    header_row = None
    for i in range(20):
        if "human development index" in str(df_raw.iloc[i]).lower():
            header_row = i
            break

    file.seek(0)
    df = pd.read_excel(file, header=header_row)

    df.columns = [str(c).strip() for c in df.columns]

    return df

def fetch_hdi(iso3):
    df = load_hdi_table()

    # colonne pays
    country_col = [c for c in df.columns if "country" in c.lower()][0]
    hdi_col = [c for c in df.columns if "human development index" in c.lower()][0]
    rank_col = [c for c in df.columns if "rank" in c.lower()][0]

    row = df[df[country_col].str.upper().str.contains(iso3)]

    if row.empty:
        return None, None

    return float(row.iloc[0][hdi_col]), int(row.iloc[0][rank_col])

# ─────────────────────────────
# UI
# ─────────────────────────────
country = st.selectbox("Choisir un pays", list(COUNTRY_MAPPING.keys()))

if st.button("Récupérer les données"):

    info = COUNTRY_MAPPING[country]

    # ───────── FREEDOM HOUSE
    st.subheader("Freedom House")

    fh = fetch_freedom_house(info["freedom_house_slug"])
    st.write("Score :", fh["score"])
    st.write("Statut :", fh["status"])
    st.markdown(f"[Source]({fh['url']})")

    # ───────── WORLD BANK
    st.subheader("Banque mondiale")

    gdp, year = fetch_wb(info["world_bank_code"], "NY.GDP.PCAP.CD")
    st.write("PIB/habitant :", gdp, "(", year, ")")

    # ───────── HDI
    st.subheader("IDH (UNDP)")

    try:
        hdi, rank = fetch_hdi(info["undp_code"])
        st.write("IDH :", hdi)
        st.write("Rang :", rank)
    except Exception as e:
        st.error("Erreur IDH : " + str(e))
   
