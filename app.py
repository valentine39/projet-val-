import streamlit as st
import pdfplumber
import pandas as pd
import numpy as np
import plotly.express as px
import re

st.set_page_config(page_title="IMF Data AI", layout="wide")

def solve_imf_structure(df):
    """Analyse et répare la structure du tableau sans intervention humaine"""
    # Nettoyage de base
    df = df.replace(['None', '—', '...', ' .', '-', ''], np.nan)
    
    # 1. Fusionner les colonnes de texte à gauche (souvent coupées au FMI)
    # On regarde les colonnes qui ne contiennent presque que du texte
    text_cols = []
    for col in df.columns:
        is_numeric_col = df[col].astype(str).str.contains(r'\d', na=False).sum() > (len(df) * 0.3)
        if not is_numeric_col:
            text_cols.append(col)
        else:
            break # On s'arrête dès qu'on trouve des chiffres
    
    if len(text_cols) > 1:
        new_col = df[text_cols].fillna("").astype(str).agg(" ".join, axis=1).str.strip()
        df = df.drop(columns=text_cols)
        df.insert(0, "Indicateur", new_col)
    
    # 2. Détecter l'en-tête (Années)
    header_idx = 0
    for i, row in df.iterrows():
        year_matches = sum(1 for x in row if re.match(r'^(19|20)\d{2}$', str(x).strip()))
        if year_matches >= 2:
            header_idx = i
            break
            
    df.columns = [str(c).strip() for c in df.iloc[header_idx]]
    df = df.iloc[header_idx + 1:].reset_index(drop=True)
    
    # 3. Nettoyer les lignes de notes/sources (si trop de NaN ou mots clés)
    def is_valid_row(row):
        txt = str(row.iloc[0]).lower()
        if any(w in txt for w in ["source", "note:", "1/", "prepared"]): return False
        return row.notna().sum() > 2 # Au moins 2 colonnes remplies

    df = df[df.apply(is_valid_row, axis=1)]

    # 4. Conversion numérique forcée
    for col in df.columns[1:]:
        df[col] = (df[col].astype(str)
                   .str.replace(',', '')
                   .str.replace(' ', '')
                   .str.replace(r'\((\d+\.?\d*)\)', r'-\1', regex=True))
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df

st.title("📊 IMF Automatic Table Insight")
st.write("Analyse automatique des rapports Article IV (Azerbaïdjan, Argentine, etc.)")

file = st.file_uploader("Glissez le rapport PDF ici", type="pdf")

if file:
    with st.spinner("Analyse du document..."):
        all_detected_tables = []
        with pdfplumber.open(file) as pdf:
            # On scanne les 20 premières pages pour trouver les tableaux financiers
            for page_idx, page in enumerate(pdf.pages[:20]):
                tables = page.extract_tables({"vertical_strategy": "text", "horizontal_strategy": "text", "text_x_tolerance": 3})
                for t_idx, t in enumerate(tables):
                    df_raw = pd.DataFrame(t)
                    if len(df_raw.columns) > 4 and len(df_raw) > 5:
                        try:
                            clean_df = solve_imf_structure(df_raw)
                            if not clean_df.empty:
                                name = f"Tableau Page {page_idx + 1} (Ref {t_idx+1})"
                                all_detected_tables.append({"name": name, "df": clean_df})
                        except:
                            continue

        if all_detected_tables:
            # Choix du tableau (souvent le premier est le bon)
            selected_table = st.selectbox("Tableaux détectés :", [t["name"] for t in all_detected_tables])
            final_df = next(t["df"] for t in all_detected_tables if t["name"] == selected_table)
            
            # --- Visualisation ---
            st.divider()
            col1, col2 = st.columns([1, 2])
            
            with col1:
                indicator = st.selectbox("Sélectionnez un indicateur :", final_df.iloc[:, 0].unique())
                data_row = final_df[final_df.iloc[:, 0] == indicator].iloc[0]
                
                # Petit résumé
                last_val = data_row.iloc[-1]
                prev_val = data_row.iloc[-2]
                delta = None
                if isinstance(last_val, (int, float)) and isinstance(prev_val, (int, float)):
                    delta = round(last_val - prev_val, 2)
                
                st.metric(label=indicator, value=last_val, delta=delta)
                
            with col2:
                plot_df = pd.DataFrame({
                    "Année": final_df.columns[1:],
                    "Valeur": data_row[1:].values
                }).dropna()
                
                fig = px.line(plot_df, x="Année", y="Valeur", markers=True, 
                             title=f"Evolution de : {indicator}",
                             line_shape="linear", template="plotly_white")
                st.plotly_chart(fig, use_container_width=True)

            with st.expander("Consulter les données complètes"):
                st.dataframe(final_df, use_container_width=True)
                st.download_button("Télécharger CSV", final_df.to_csv(index=False), "data_fmi.csv")
        else:
            st.error("Aucun tableau macroéconomique n'a été détecté automatiquement.")
