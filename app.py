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
# Liste des pays (Échantillon conservé)
# ─────────────────────────────────────────────
COUNTRY_MAPPING = {
    "afghanistan": {"name": "Afghanistan", "freedom_house_slug": "afghanistan", "world_bank_code": "AFG", "wb_url_code": "AF", "undp_code": "AFG"},
    "afrique_du_sud": {"name": "Afrique du Sud", "freedom_house_slug": "south-africa", "world_bank_code": "ZAF", "wb_url_code": "ZA", "undp_code": "ZAF"},
    "argentine": {"name": "Argentine", "freedom_house_slug": "argentina", "world_bank_code": "ARG", "wb_url_code": "AR", "undp_code": "ARG"},
    "azerbaijan": {"name": "Azerbaïdjan", "freedom_house_slug": "azerbaijan", "world_bank_code": "AZE", "wb_url_code": "AZ", "undp_code": "AZE"},
    "bresil": {"name": "Brésil", "freedom_house_slug": "brazil", "world_bank_code": "BRA", "wb_url_code": "BR", "undp_code": "BRA"},
    "senegal": {"name": "Sénégal", "freedom_house_slug": "senegal", "world_bank_code": "SEN", "wb_url_code": "SN", "undp_code": "SEN"},
}

INCOME_LABELS = {
    "LIC": "PFR — Pays à faible revenu",
    "LMC": "PRITI — Rev. intermédiaire tranche inf.",
    "UMC": "PRITS — Rev. intermédiaire tranche sup.",
    "HIC": "PRE — Pays à revenu élevé",
    "INX": "Non classifié",
}

# ─────────────────────────────────────────────
# Fonctions de collecte (Tes fonctions intactes)
# ─────────────────────────────────────────────

def fetch_freedom_house(country_slug, year=2024):
    url = f"https://freedomhouse.org/country/{country_slug}/freedom-world/{year}"
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        r = requests.get(url, timeout=30, headers=headers)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        text = re.sub(r"\s+", " ", soup.get_text(" ", strip=True))
        result = {"status": None, "score": None, "year": year, "url": url}
        if re.search(r"\bNot Free\b", text): result["status"] = "Not Free"
        elif re.search(r"\bPartly Free\b", text): result["status"] = "Partly Free"
        elif re.search(r"\bFree\b", text): result["status"] = "Free"
        m = re.search(r"(?:Total Score and Status|score)\s+(\d{1,3})\s*/?\s*100", text, re.IGNORECASE)
        if m: result["score"] = int(m.group(1))
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
        if not isinstance(data, list) or len(data) < 2 or not data[1]: return None
        c = data[1][0]
        return {
            "income_code": c.get("incomeLevel", {}).get("id", ""),
            "income_label": c.get("incomeLevel", {}).get("value", ""),
            "region": c.get("region", {}).get("value", ""),
        }
    except: return None

def make_unique_columns(df):
    df = df.copy()
    seen, new_cols = {}, []
    for col in df.columns:
        col = str(col).strip() if col is not None else "colonne"
        if col == "" or col.lower() == "none": col = "colonne"
        if col in seen:
            seen[col] += 1
            new_cols.append(f"{col}_{seen[col]}")
        else:
            seen[col] = 0
            new_cols.append(col)
    df.columns = new_cols
    return df

# ─────────────────────────────────────────────
# Article IV FMI — Extraction (Reprise et fin de ton code)
# ─────────────────────────────────────────────

def _safe_import_pdfplumber():
    try:
        import pdfplumber
        return pdfplumber, None
    except Exception as e:
        return None, str(e)

def extract_article_iv_tables(uploaded_pdf, max_tables=30):
    """Extrait les tableaux détectés dans le PDF (Ton code complété)"""
    pdfplumber, error = _safe_import_pdfplumber()
    if error: return [], f"pdfplumber indisponible : {error}"

    try:
        uploaded_pdf.seek(0)
        tables_out = []
        with pdfplumber.open(uploaded_pdf) as pdf:
            # On se limite aux 15 premières pages pour trouver les indicateurs clés vite
            for page_number, page in enumerate(pdf.pages[:15], start=1):
                # Utilisation de paramètres FMI-friendly
                tables = page.extract_tables({"vertical_strategy": "text", "horizontal_strategy": "text"}) or []
                for table_id, table in enumerate(tables, start=1):
                    if not table or len(table) < 2:
                        continue

                    # Nettoyage minimal (Ta logique exacte)
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

                    try: df = pd.DataFrame(body, columns=header)
                    except Exception: df = pd.DataFrame(cleaned)

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

def score_and_select_best_table(tables):
    """Identifie le tableau FMI le plus pertinent pour le Pilier 2"""
    table_keywords = ["gdp", "growth", "inflation", "fiscal", "current account", "exports", "reserves"]
    best_score = 0
    best_table = None
    
    for item in tables:
        df = item["data"]
        text = " ".join(df.astype(str).fillna("").values.flatten().tolist()).lower()
        score = sum(1 for kw in table_keywords if kw in text)
        if score > best_score:
            best_score = score
            best_table = df
            
    if best_table is not None:
        # Nettoyage additionnel pour le prompt (enlever colonnes vides)
        best_table = best_table.replace(['', 'None'], pd.NA).dropna(how='all', axis=1).dropna(how='all', axis=0)
        return best_table.head(25) # On prend les lignes principales
    return pd.DataFrame()

# ─────────────────────────────────────────────
# Interface & Exécution principale
# ─────────────────────────────────────────────

st.markdown('<div class="title-block">', unsafe_allow_html=True)
st.markdown("# 🌍 Outil de collecte de données — DER")
st.markdown('<p style="color:#888; font-size:13px; margin-top:-8px;">Piliers 1 & 2 : Environnement politique & Modèle de croissance</p>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Sélection pays
country_options = {info["name"]: key for key, info in COUNTRY_MAPPING.items()}
selected_name = st.selectbox("Sélectionner un pays", options=sorted(list(country_options.keys())))
country_info = COUNTRY_MAPPING[country_options[selected_name]]

uploaded_article_iv = st.file_uploader(
    "📄 Article IV FMI (Requis pour le Pilier 2)", 
    type=["pdf"], 
    help="L'app extraira automatiquement le tableau 'Selected Economic Indicators' de ce PDF."
)

if st.button("Lancer la collecte et générer le rapport"):
    
    with st.spinner("Collecte des données institutionnelles..."):
        # --- COLLECTE PILIER 1 ---
        wb_code = country_info["world_bank_code"]
        wb_info = fetch_wb_country_info(wb_code)
        
        income_code = wb_info.get("income_code", "") if wb_info else ""
        income_label = INCOME_LABELS.get(income_code, "N/D")
        
        gdp_val, gdp_year = fetch_wb_latest(wb_code, "NY.GDP.PCAP.CD")
        growth_val, growth_year = fetch_wb_latest(wb_code, "NY.GDP.MKTP.KD.ZG")
        gini_val, gini_year = fetch_wb_latest(wb_code, "SI.POV.GINI")
        fh_data = fetch_freedom_house(country_info["freedom_house_slug"])

        # --- COLLECTE PILIER 2 (PDF) ---
        fmi_table_str = "Aucun PDF FMI n'a été fourni ou aucun tableau macro pertinent n'a été détecté."
        if uploaded_article_iv:
            tables, error = extract_article_iv_tables(uploaded_article_iv)
            if not error and tables:
                best_df = score_and_select_best_table(tables)
                if not best_df.empty:
                    fmi_table_str = best_df.to_string(index=False)

    # --- AFFICHAGE DES RÉSULTATS ---
    st.markdown('<div class="section-title">📌 Pilier 1 — Environnement socio-économique</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Freedom House", fh_data.get('status', 'N/D'), f"Score: {fh_data.get('score', 'N/D')}")
    c2.metric("Statut BM", income_label)
    c3.metric("PIB/hab", f"${gdp_val:,.0f}" if gdp_val else "N/D", f"Année {gdp_year}" if gdp_year else "")
    c4.metric("Gini", f"{gini_val:.1f}" if gini_val else "N/D", f"Année {gini_year}" if gini_year else "")
    
    st.markdown('<div class="section-title">📈 Pilier 2 — Tableau Macro FMI</div>', unsafe_allow_html=True)
    if uploaded_article_iv and 'best_df' in locals() and not best_df.empty:
        st.dataframe(best_df, use_container_width=True)
    else:
        st.info(fmi_table_str)

    # --- GÉNÉRATION DU PROMPT IA ---
    st.markdown("---")
    st.markdown('<div class="section-title">🤖 Prompt IA — Fiche Pays (Prêt à copier)</div>', unsafe_allow_html=True)
    
    prompt = f"""
FICHE PAYS : {country_info['name']}
====================================================

Tu es un analyste risque pays. À partir des données vérifiées ci-dessous, rédige une analyse dense et institutionnelle couvrant les deux premiers piliers.

DONNÉES COLLECTÉES (À utiliser obligatoirement) :
- Statut Politique (Freedom House) : {fh_data.get('status', 'N/D')} (Score: {fh_data.get('score', 'N/D')})
- Classification Banque Mondiale : {income_label}
- PIB/habitant : {gdp_val} USD (Année : {gdp_year})
- Croissance PIB : {growth_val}% (Année : {growth_year})
- Indice de Gini : {gini_val} (Année : {gini_year})

EXTRAIT TABLEAU MACROÉCONOMIQUE FMI (Article IV) :
{fmi_table_str}

CONSIGNES DE RÉDACTION STRICTES :

1. Pilier 1 : Environnement politique et socioéconomique
- Rédige un premier paragraphe sur le régime politique et sa stabilité (en intégrant le score Freedom House).
- Rédige un second paragraphe socioéconomique en commentant le niveau de richesse (PIB/hab), la classification BM et les inégalités (Gini). Signale les éventuels décalages de millésimes.

2. Pilier 2 : Modèle économique et régime de croissance
- Rédige une sous-partie "Modèle économique :" caractérisant la structure productive et les vulnérabilités structurelles à l'aide des données FMI.
- Rédige une sous-partie "Régime de croissance :" qualifiant la dynamique récente, les chocs observés, et la trajectoire à court/moyen terme indiquée par les prévisions du tableau FMI.

CONTRAINTES :
- Ne pas inventer de chiffres. Si une donnée manque, signale-le.
- Pas de bullet points. Rédige des paragraphes denses et articulés.
- Distingue clairement les données observées des prévisions du FMI.
    """
    
    st.text_area("Copiez ce texte dans Claude ou ChatGPT :", value=prompt.strip(), height=500)
    st.markdown(f'<p class="source-note">📅 Données collectées et formatées le {datetime.now().strftime("%d/%m/%Y à %H:%M")}</p>', unsafe_allow_html=True)
        st.subheader("📝 Prompt à copier pour l'IA")
        st.text_area("Copie ce texte dans ChatGPT ou Claude :", prompt_final, height=450)
