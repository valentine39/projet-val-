import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from datetime import datetime
from io import BytesIO
import pdfplumber  # Indispensable pour le Pilier 2

# --- CONFIGURATION (Gardée de ton code) ---
st.set_page_config(page_title="Outil de collecte - DER Expert", layout="wide")

# --- FONCTIONS DE SCRAPING (Optimisées) ---

def fetch_wb_indicator(country_code, indicator):
    """Récupère la valeur la plus récente d'un indicateur Banque Mondiale"""
    url = f"https://api.worldbank.org/v2/country/{country_code}/indicator/{indicator}?format=json&mrnev=1"
    try:
        r = requests.get(url, timeout=10).json()
        if len(r) > 1:
            val = r[1][0]['value']
            year = r[1][0]['date']
            return val, year
    except: return None, None

def extract_fmi_indicators(uploaded_file):
    """
    EXTRACTEUR CIBLÉ PILIER 2: 
    Cherche le tableau 'Selected Economic Indicators' dans le PDF FMI.
    """
    try:
        with pdfplumber.open(uploaded_file) as pdf:
            # On cherche sur les 10 premières pages
            for page in pdf.pages[:10]:
                text = page.extract_text()
                if text and "Selected Economic" in text:
                    table = page.extract_table()
                    if table:
                        df = pd.DataFrame(table)
                        # Nettoyage : suppression des lignes vides et formatage
                        df = df.dropna(how='all').iloc[:, :6] # On prend les 6 premières colonnes (Années)
                        return df.to_string()
        return "Tableau FMI non détecté automatiquement."
    except Exception as e:
        return f"Erreur PDF: {str(e)}"

# --- LOGIQUE MÉTIER : STRUCTURATION DES PILIERS ---

def generate_expert_prompt(country_name, data_p1, data_p2):
    """Génère le prompt final basé sur tes consignes du 23/04"""
    prompt = f"""
    Rédige une fiche pays professionnelle pour : {country_name}.
    Structure ton analyse selon les deux piliers suivants, en restant dense, factuel et institutionnel.
    
    ### DONNÉES SOURCES (BRUTES) :
    PILIER 1: {data_p1}
    PILIER 2 (EXTRAITS FMI): {data_p2}
    
    ### INSTRUCTIONS DE RÉDACTION :
    
    PILIER 1 : Environnement politique et socioéconomique
    - §1: Analyse de la stabilité politique et du régime (utilise les scores Freedom House).
    - §2: Analyse quantitative (Gouvernance Banque Mondiale).
    - §3: Développement humain (PIB/hab, Gini, IDH). Mentionne les millésimes de données.
    
    PILIER 2 : Modèle économique et régime de croissance
    - Partie 'Modèle économique': Caractérise la structure productive (diversifiée, rentière, etc.). Identifie forces et fragilités.
    - Partie 'Régime de croissance': Analyse le rythme (volatilité, moteurs) et les perspectives à moyen terme. 
    - Contrainte : Pas de bullet points. Style analytique. Rattache chaque affirmation à un chiffre.
    """
    return prompt

# --- INTERFACE STREAMLIT ---

st.title("🌍 DER Intelligence - Analyse Piliers 1 & 2")
st.markdown("---")

# 1. Sélection du pays
selected_key = st.selectbox("Sélectionner un pays", list(COUNTRY_MAPPING.keys()))
country = COUNTRY_MAPPING[selected_key]

# 2. Upload PDF (Pour le Pilier 2)
uploaded_pdf = st.file_uploader("Charger le rapport Article IV FMI (PDF)", type="pdf")

if st.button("🚀 Lancer l'extraction et générer le prompt"):
    
    with st.spinner("Collecte des données en cours..."):
        # Collecte Pilier 1 (API World Bank)
        pib_pc, y1 = fetch_wb_indicator(country['world_bank_code'], "NY.GDP.PCAP.CD")
        gini, y2 = fetch_wb_indicator(country['world_bank_code'], "SI.POV.GINI")
        growth, y3 = fetch_wb_indicator(country['world_bank_code'], "NY.GDP.MKTP.KD.ZG")
        
        # Collecte Freedom House (Scraping)
        fh = fetch_freedom_house(country['freedom_house_slug'])
        
        # Collecte Pilier 2 (PDF FMI)
        fmi_context = ""
        if uploaded_pdf:
            fmi_context = extract_fmi_indicators(uploaded_pdf)
        else:
            fmi_context = "Aucun PDF fourni. Utilise tes connaissances générales pour le Pilier 2."

        # Préparation du bloc de données Pilier 1 pour l'IA
        p1_summary = {
            "PIB/hab": f"{pib_pc} ({y1})",
            "Gini": f"{gini} ({y2})",
            "Croissance": f"{growth}% ({y3})",
            "Status Politique": fh.get('status', 'N/D'),
            "Score FH": fh.get('score', 'N/D')
        }

        # Affichage des résultats bruts
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Données Pilier 1 (Vérifiées)")
            st.json(p1_summary)
        
        with col2:
            st.subheader("Données Pilier 2 (Extraites PDF)")
            if uploaded_pdf:
                st.text_area("Extrait du tableau FMI", fmi_context, height=200)
            else:
                st.warning("Manque PDF FMI pour une analyse précise du Pilier 2.")

        # GÉNÉRATION DU PROMPT
        st.markdown("---")
        st.header("📝 Prompt Expert Généré")
        final_prompt = generate_expert_prompt(country['name'], p1_summary, fmi_context)
        st.text_area("Copiez ce texte dans ChatGPT / Claude :", final_prompt, height=400)
