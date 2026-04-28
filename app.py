import streamlit as st
import pdfplumber
import pandas as pd
import numpy as np
import plotly.express as px
import re

st.set_page_config(page_title="IMF Auto-Dashboard", layout="wide")

def clean_and_format_imf(df):
    """Nettoyage automatique haute précision pour les rapports FMI"""
    # 1. Correction du bug applymap -> map (compatibilité Pandas 2.x)
    if hasattr(df, 'map'):
        df = df.map(lambda x: " ".join(str(x).split()) if pd.notnull(x) else x)
    else:
        df = df.applymap(lambda x: " ".join(str(x).split()) if pd.notnull(x) else x)
    
    df = df.replace(['None', '—', '...', ' .', '-', ''], np.nan)

    # 2. SUTURE DES LIGNES : Recoller les titres coupés en deux
    # Si une ligne n'a pas de chiffres mais que la suivante en a, on les fusionne
    new_rows = []
    temp_title = ""
    for i in range(len(df)):
        row = df.iloc[i]
        # On compte les chiffres dans la ligne
        has_data = row.iloc[1:].notna().any()
        
        if not has_data:
            temp_title += " " + str(row.iloc[0])
        else:
            row.iloc[0] = (temp_title + " " + str(row.iloc[0])).strip()
            new_rows.append(row)
            temp_title = ""
    
    df = pd.DataFrame(new_rows)

    # 3. DETECTION AUTO DE L'EN-TETE (ANNEES)
    # On cherche la ligne qui contient le plus de chiffres à 4 chiffres (dates)
    def count_years(row):
        return sum(1 for x in row if re.match(r'^(19|20)\d{2}$', str(x).strip()))
    
    year_counts = df.apply(count_years, axis=1)
    if year_counts.max() > 0:
        header_idx = year_counts.idxmax()
        # On nettoie les noms de colonnes (années)
        cols = ["Indicateur"] + [str(x) for x in df.iloc[header_idx, 1:]]
        df.columns = cols
        df = df.iloc[header_idx + 1:]

    # 4. NETTOYAGE DES CHIFFRES
    for col in df.columns[1:]:
        df[col] = df[col].astype(str).str.replace(',', '').str.replace(' ', '')
        df[col] = df[col].str.replace(r'\((\d+)\)', r'-\1', regex=True) # (1.2) -> -1.2
        df[col] = pd.to_numeric(df[col], errors='coerce')

    return df.dropna(subset=[df.columns[0]])

st.title("📊 IMF Data Vision")
st.write("Glissez votre rapport PDF. L'extraction et l'analyse sont automatiques.")

file = st.file_uploader("Rapport Article IV", type="pdf")

if file:
    with st.spinner("Analyse intelligente du document..."):
        found_df = None
        with pdfplumber.open(file) as pdf:
            # Scan des 15 premières pages pour trouver le tableau "Selected Indicators"
            for page in pdf.pages[:15]:
                text = page.extract_text()
                if text and "Selected Economic" in text:
                    table = page.extract_table({"vertical_strategy": "text", "horizontal_strategy": "text", "text_x_tolerance": 3})
                    if table:
                        df_raw = pd.DataFrame(table)
                        if len(df_raw.columns) > 3:
                            found_df = clean_and_format_imf(df_raw)
                            break

        if found_df is not None:
            # --- DASHBOARD AUTO ---
            st.success("Tableau macroéconomique identifié.")
            
            indicator = st.selectbox("Choisir un indicateur", found_df.iloc[:, 0].unique())
            
            # Préparation data pour graphique
            data_row = found_df[found_df.iloc[:, 0] == indicator].iloc[0]
            plot_df = pd.DataFrame({
                "Année": found_df.columns[1:],
                "Valeur": data_row[1:].values
            }).dropna()

            fig = px.line(plot_df, x="Année", y="Valeur", markers=True, title=indicator)
            st.plotly_chart(fig, use_container_width=True)

            with st.expander("Accéder au tableau complet"):
                st.dataframe(found_df, use_container_width=True)
        else:
            st.error("Ce PDF ne semble pas suivre le format standard du FMI.")
