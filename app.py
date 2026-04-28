import streamlit as st
import pdfplumber
import pandas as pd
import numpy as np
import plotly.express as px
import re

st.set_page_config(page_title="IMF Auto-Dashboard", layout="wide")

def is_year(text):
    """Vérifie si un texte ressemble à une année (2022, 2023, etc.)"""
    return bool(re.match(r'^(19|20)\d{2}$', str(text).strip()))

def clean_and_format_imf(df):
    """Nettoyage automatique sans intervention humaine"""
    # 1. Suppression des "None" et nettoyage des espaces
    df = df.replace(['None', '—', '...', ' .', '-', ''], np.nan)
    df = df.applymap(lambda x: " ".join(str(x).split()) if pd.notnull(x) else x)
    
    # 2. Détection de la ligne des années (En-tête)
    # On cherche la ligne qui contient le plus de dates
    year_counts = df.apply(lambda row: sum(is_year(c) for c in row), axis=1)
    if year_counts.max() > 0:
        header_idx = year_counts.idxmax()
        years = df.iloc[header_idx].tolist()
        df.columns = years
        df = df.iloc[header_idx + 1:]
    
    # 3. Suppression automatique des bas de page (Sources, Notes)
    # Règle : une ligne qui n'a presque pas de chiffres est une note ou une source
    def is_data_row(row):
        text = str(row.iloc[0]).lower()
        if any(word in text for word in ["source", "1/", "note", "prepared by"]): return False
        # Si plus de 70% de la ligne est vide, c'est probablement un titre de section ou une note
        return row.count() > (len(row) * 0.3)

    df = df[df.apply(is_data_row, axis=1)]
    
    # 4. Conversion numérique automatique
    for col in df.columns[1:]:
        df[col] = df[col].apply(lambda x: str(x).replace(',', '').replace(' ', '').replace('(', '-').replace(')', ''))
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df.dropna(subset=[df.columns[0]]) # Supprime les lignes sans nom d'indicateur

st.title("🚀 Analyseur Automatique Article IV")
st.write("Déposez votre rapport, l'IA s'occupe du reste.")

file = st.file_uploader("Fichier PDF (IMF Report)", type="pdf")

if file:
    with st.spinner("Recherche et analyse automatique du tableau principal..."):
        found_df = None
        with pdfplumber.open(file) as pdf:
            # On cherche dans les 15 premières pages (le résumé est toujours au début)
            for page in pdf.pages[:15]:
                text = page.extract_text()
                if text and "Selected Economic" in text:
                    table = page.extract_table({
                        "vertical_strategy": "text", 
                        "horizontal_strategy": "text",
                        "text_x_tolerance": 3
                    })
                    if table:
                        df_raw = pd.DataFrame(table)
                        if len(df_raw.columns) > 3: # Un vrai tableau FMI a beaucoup de colonnes
                            found_df = clean_and_format_imf(df_raw)
                            break
        
        if found_df is not None:
            st.success("Tableau des indicateurs économiques détecté !")
            
            # Interface de visualisation
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.subheader("Indicateurs")
                indicator_name = found_df.columns[0]
                selected = st.selectbox("Sélectionnez une donnée :", found_df.iloc[:, 0].unique())
                
                row = found_df[found_df.iloc[:, 0] == selected]
                st.metric("Dernière valeur connue", f"{row.iloc[0, -1]}")
            
            with col2:
                # Préparation des données pour Plotly
                plot_data = pd.DataFrame({
                    "Année": found_df.columns[1:],
                    "Valeur": row.iloc[0, 1:].values
                }).dropna()
                
                fig = px.line(plot_data, x="Année", y="Valeur", markers=True, 
                             title=f"Tendance : {selected}",
                             template="plotly_white")
                st.plotly_chart(fig, use_container_width=True)
            
            with st.expander("Voir les données brutes"):
                st.dataframe(found_df, use_container_width=True)
        else:
            st.error("Impossible de localiser le tableau automatiquement. Assurez-vous que c'est un rapport standard de l'Article IV.")
