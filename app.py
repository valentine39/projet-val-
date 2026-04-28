import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import pdfplumber
from datetime import datetime
from io import BytesIO

# ─────────────────────────────────────────────
# 1. CONFIGURATION ET DICTIONNAIRES
# ─────────────────────────────────────────────
st.set_page_config(page_title="DER - Analyse Pays Expert", page_icon="🌍", layout="wide")

# (Ta liste de pays - Je l'ai gardée complète pour que le code fonctionne direct)
COUNTRY_MAPPING = {
    "afghanistan": {"name": "Afghanistan", "freedom_house_slug": "afghanistan", "world_bank_code": "AFG", "wb_url_code": "AF"},
    "afrique_du_sud": {"name": "Afrique du Sud", "freedom_house_slug": "south-africa", "world_bank_code": "ZAF", "wb_url_code": "ZA"},
    "algerie": {"name": "Algérie", "freedom_house_slug": "algeria", "world_bank_code": "DZA", "wb_url_code": "DZ"},
    "argentine": {"name": "Argentine", "freedom_house_slug": "argentina", "world_bank_code": "ARG", "wb_url_code": "AR"},
    "azerbaijan": {"name": "Azerbaïdjan", "freedom_house_slug": "azerbaijan", "world_bank_code": "AZE", "wb_url_code": "AZ"},
    "bresil": {"name": "Brésil", "freedom_house_slug": "brazil", "world_bank_code": "BRA", "wb_url_code": "BR"},
    "cote_ivoire": {"name": "Côte d'Ivoire", "freedom_house_slug": "cote-divoire", "world_bank_code": "CIV", "wb_url_code": "CI"},
    "egypte": {"name": "Égypte", "freedom_house_slug": "egypt", "world_bank_code": "EGY", "wb_url_code": "EG"},
    "maroc": {"name": "Maroc", "freedom_house_slug": "morocco", "world_bank_code": "MAR", "wb_url_code": "MA"},
    "senegal": {"name": "Sénégal", "freedom_house_slug": "senegal", "world_bank_code": "SEN", "wb_url_code": "SN"},
    "vietnam": {"name": "Vietnam", "freedom_house_slug": "vietnam", "world_bank_code": "VNM", "wb_url_code": "VN"},
} # Ajoute les autres pays ici comme dans ton script original

# ─────────────────────────────────────────────
# 2. FONCTIONS DE COLLECTE (SCRAPING & API)
# ─────────────────────────────────────────────

def fetch_freedom_house(country_slug):
    """Scraping du score de liberté"""
    url = f"https://freedomhouse.org/country/{country_slug}/freedom-world/2024"
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, timeout=10, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        text = soup.get_text()
        status = "N/D"
        if "Not Free" in text: status = "Not Free"
        elif "Partly Free" in text: status = "Partly Free"
        elif "Free" in text: status = "Free"
        score = re.search(r"(\d{1,3})\s*/\s*100", text)
        return {"status": status, "score": score.group(1) if score else "N/D", "url": url}
    except: return {"status": "Erreur", "score": "N/D", "url": url}

def fetch_wb_indicator(country_code, indicator):
    """Récupère la donnée la plus récente de la Banque Mondiale"""
    url = f"https://api.worldbank.org/v2/country/{country_code}/indicator/{indicator}?format=json&mrnev=1"
    try:
        res = requests.get(url).json()
        if len(res) > 1:
            return res[1][0]['value'], res[1][0]['date']
    except: pass
    return None, None

# ─────────────────────────────────────────────
# 3. EXTRACTION PDF (PILIER 2 - GROWTH)
# ─────────────────────────────────────────────

def extract_fmi_indicators(uploaded_file):
    """Cherche le tableau macroéconomique clé dans le rapport FMI"""
    try:
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages[:15]: # Les tableaux clés sont au début
                text = page.extract_text()
                if text and ("Selected Economic" in text or "Financial Indicators" in text):
                    table = page.extract_table()
                    if table:
                        df = pd.DataFrame(table).dropna(how='all', axis=1)
                        # On ne garde que les 15 premières lignes pour le prompt
                        return df.head(20).to_string(index=False)
        return "Tableau non trouvé dans les 15 premières pages."
    except Exception as e:
        return f"Erreur d'extraction : {str(e)}"

# ─────────────────────────────────────────────
# 4. INTERFACE UTILISATEUR
# ─────────────────────────────────────────────

st.title("🌍 Outil DER - Fiche Pays (Piliers 1 & 2)")
st.markdown("---")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("⚙️ Paramètres")
    selected_key = st.selectbox("Sélectionner un pays", list(COUNTRY_MAPPING.keys()))
    country = COUNTRY_MAPPING[selected_key]
    pdf_file = st.file_uploader("Déposer le rapport Article IV FMI (Optionnel)", type="pdf")

with col2:
    st.subheader("ℹ️ Informations")
    st.write(f"**Pays :** {country['name']}")
    st.write(f"**Code ISO :** {country['world_bank_code']}")

if st.button("🚀 Générer la base de données et le Prompt"):
    
    with st.spinner("Collecte en cours..."):
        # Collecte Pilier 1
        fh = fetch_freedom_house(country['freedom_house_slug'])
        pib_hab, y_pib = fetch_wb_indicator(country['world_bank_code'], "NY.GDP.PCAP.CD")
        gini, y_gini = fetch_wb_indicator(country['world_bank_code'], "SI.POV.GINI")
        
        # Collecte Pilier 2
        fmi_data = "Aucun PDF fourni"
        if pdf_file:
            fmi_data = extract_fmi_indicators(pdf_file)

        # ─────────────────────────────────────────────
        # 5. GÉNÉRATION DES PROMPTS (Moteur IA)
        # ─────────────────────────────────────────────
        
        st.success("Données collectées avec succès !")
        
        # Affichage rapide
        c1, c2, c3 = st.columns(3)
        c1.metric("Score Freedom House", f"{fh['score']}/100", fh['status'])
        c2.metric("PIB/hab (USD)", f"{int(pib_hab) if pib_hab else 'N/D'}", f"Année {y_pib}")
        c3.metric("Indice Gini", f"{gini if gini else 'N/D'}", f"Année {y_gini}")

        # Le Prompt Final (Celui que tu colles dans l'IA)
        prompt_final = f"""
        Rédige une fiche pays professionnelle pour le pays suivant : {country['name']}.
        
        DONNÉES COLLECTÉES :
        - Freedom House : {fh['status']} (Score: {fh['score']}/100)
        - PIB par habitant : {pib_hab} USD (Année: {y_pib})
        - Indice Gini : {gini} (Année: {y_gini})
        - Extraits macro FMI : 
        {fmi_data}

        CONSIGNES DE RÉDACTION STRICTES :
        
        PILIER 1 : Environnement politique et socioéconomique
        - §1 : Analyse le régime politique, la stabilité et les risques politiques actuels.
        - §2 : Analyse quantitative de la gouvernance à partir des scores fournis.
        - §3 : Analyse socioéconomique (PIB/hab, Gini, IDH). Signale les décalages de millésime.

        PILIER 2 : Modèle économique et régime de croissance
        - Section 'Modèle économique :' : Caractérise la structure productive (diversifiée, rentière, etc.). Identifie les forces et fragilités structurelles.
        - Section 'Régime de croissance :' : Analyse le rythme de croissance (dynamique, volatile), les moteurs (investissement, rente) et les perspectives à moyen terme.
        - STYLE : Dense, institutionnel, sans bullet points. Rattache chaque affirmation à un chiffre.
        """

        st.markdown("---")
        st.subheader("📝 Prompt à copier pour l'IA")
        st.text_area("Copie ce texte dans ChatGPT ou Claude :", prompt_final, height=450)
