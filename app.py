import streamlit as st
import pdfplumber
import pandas as pd
import requests
import re
import plotly.express as px

# --- CONFIGURATION & STYLE ---
st.set_page_config(page_title="Expert Pays - Pilier 1 & 2", layout="wide")
st.markdown("""<style> .stMetric { background-color: #f8f9fa; padding: 10px; border-radius: 10px; } </style>""", unsafe_allow_html=True)

# --- FONCTIONS DE COLLECTE (PILIER 1) ---
def get_world_bank_data(country_code):
    indicators = {
        'NY.GDP.PCAP.CD': 'PIB/hab (USD)',
        'SI.POV.GINI': 'Indice Gini',
        'NY.GDP.MKTP.KD.ZG': 'Croissance PIB (%)'
    }
    data = {}
    for code, name in indicators.items():
        try:
            url = f"https://api.worldbank.org/v2/country/{country_code}/indicator/{code}?format=json&per_page=1"
            res = requests.get(url).json()
            data[name] = res[1][0]['value'], res[1][0]['date']
        except: data[name] = ("N/A", "N/A")
    return data

# --- FONCTION D'EXTRACTION PDF (PILIER 2 - ZERO CONFIG) ---
def extract_imf_table(file):
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages[:15]: # Scan auto des 15 premières pages
            text = page.extract_text()
            if text and "Selected Economic" in text:
                table = page.extract_table({"vertical_strategy": "text", "horizontal_strategy": "text", "text_x_tolerance": 3})
                if table:
                    df = pd.DataFrame(table)
                    # Nettoyage automatique des "None" et suture des titres
                    df = df.replace(['None', '—', '...', ''], np.nan).dropna(how='all', axis=1)
                    return df
    return None

# --- INTERFACE ---
st.title("🌍 Générateur de Fiche Pays (Piliers 1 & 2)")
col_a, col_b = st.columns(2)

with col_a:
    country_name = st.text_input("Nom du pays (ex: Azerbaijan, Argentina)", "Azerbaijan")
    country_iso = st.text_input("Code ISO (2 lettres - ex: AZ, AR)", "AZ")

with col_b:
    pdf_file = st.file_uploader("Déposer le rapport Article IV (PDF)", type="pdf")

if st.button("Lancer l'analyse complète"):
    # 1. RÉCUPÉRATION PILIER 1
    st.subheader("📊 Pilier 1 : Données Socio-économiques (API)")
    wb_data = get_world_bank_data(country_iso)
    c1, c2, c3 = st.columns(3)
    c1.metric("PIB/hab", f"{wb_data['PIB/hab (USD)'][0]} $", f"Année: {wb_data['PIB/hab (USD)'][1]}")
    c2.metric("Gini", wb_data['Indice Gini'][0], f"Année: {wb_data['Indice Gini'][1]}")
    c3.metric("Croissance", f"{wb_data['Croissance PIB (%)'][0]} %")

    # 2. RÉCUPÉRATION PILIER 2
    st.subheader("🏗️ Pilier 2 : Modèle de croissance (PDF)")
    if pdf_file:
        df_imf = extract_imf_table(pdf_file)
        if df_imf is not None:
            st.success("Tableau FMI détecté et structuré.")
            st.dataframe(df_imf.head(10), use_container_width=True)
            
            # --- GÉNÉRATION DU PROMPT FINAL ---
            st.divider()
            st.subheader("📝 Prompt IA pour la Fiche Pays")
            
            prompt = f"""
            Tu es un expert en analyse macroéconomique. Rédige une analyse pour : {country_name}.
            
            DONNÉES DISPONIBLES :
            - PIB/hab : {wb_data['PIB/hab (USD)'][0]} (Source: BM)
            - Gini : {wb_data['Indice Gini'][0]}
            - Extraits FMI : {df_imf.iloc[:10, :5].to_string()}
            
            CONSIGNES :
            1. Rédige le Pilier 1 (Environnement politique) en 3 paragraphes : Politique brute, Analyse Gouvernance (V-Dem/BM), et Socio-éco.
            2. Rédige le Pilier 2 (Modèle de croissance) avec deux sections explicites : "Modèle économique :" et "Régime de croissance :". 
            Respecte un style institutionnel, dense, sans bullet points. Rattache chaque analyse à un chiffre.
            """
            st.text_area("Copiez ce prompt dans votre IA :", prompt, height=300)
        else:
            st.warning("Tableau FMI non trouvé. Vérifiez que le PDF est bien un rapport Article IV.")
    else:
        st.info("Veuillez charger un PDF pour compléter le Pilier 2.")
