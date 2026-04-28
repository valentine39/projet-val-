import streamlit as st
import pdfplumber
import pandas as pd
import numpy as np
import re

st.set_page_config(page_title="IMF Final Extractor", layout="wide")

def merge_text_columns(df, num_text_cols=3):
    """Fusionne les X premières colonnes si elles contiennent du texte découpé"""
    df = df.copy()
    # On remplace les None par du vide pour la fusion
    for i in range(num_text_cols):
        df.iloc[:, i] = df.iloc[:, i].fillna("")
    
    # On crée la nouvelle colonne 0 en fusionnant les colonnes choisies
    combined = df.iloc[:, 0].astype(str)
    for i in range(1, num_text_cols):
        combined = combined + df.iloc[:, i].astype(str)
    
    # On nettoie les espaces en trop
    df.iloc[:, 0] = combined.apply(lambda x: " ".join(x.split()))
    
    # On supprime les colonnes qui ont été fusionnées
    cols_to_drop = [df.columns[i] for i in range(1, num_text_cols)]
    df = df.drop(columns=cols_to_drop)
    return df

st.title("📊 Extracteur FMI (Correction des Libellés)")

uploaded_file = st.file_uploader("Charger le PDF", type="pdf")

with st.sidebar:
    st.header("1. Réglages PDF")
    page_num = st.number_input("Page", min_value=1, value=5)
    x_tol = st.slider("Précision colonnes (x_tol)", 1, 10, 3)
    
    st.header("2. Correction Libellés")
    nb_cols_merge = st.number_input("Nb de colonnes à fusionner à gauche", min_value=1, max_value=5, value=3)
    st.info("Si 'Consumer' et 'Price' sont dans 2 colonnes différentes, augmentez ce chiffre.")

if uploaded_file:
    with pdfplumber.open(uploaded_file) as pdf:
        page = pdf.pages[page_num - 1]
        
        table_settings = {
            "vertical_strategy": "text",
            "horizontal_strategy": "text",
            "text_x_tolerance": x_tol,
            "text_y_tolerance": 3,
        }
        
        table = page.extract_table(table_settings)
        
        if table:
            df = pd.DataFrame(table)
            
            # Application de la soudure des colonnes
            df = merge_text_columns(df, num_text_cols=nb_cols_merge)
            
            # Nettoyage des lignes vides
            df = df.replace(['', 'None', None], np.nan).dropna(how='all')

            st.subheader("Visualisation du tableau corrigé")
            st.dataframe(df, use_container_width=True)

            # Export
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Télécharger CSV Corrigé", csv, "fmi_total_clean.csv")
