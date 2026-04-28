import streamlit as st
import pdfplumber
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="IMF Data Intelligence", layout="wide")

# --- FONCTIONS DE NETTOYAGE ---
def clean_data(df, rows_to_drop):
    # 1. Supprimer les colonnes totalement vides
    df = df.dropna(how='all', axis=1)
    
    # 2. Remplacer les "None" et symboles par du vide
    df = df.replace(['None', '—', '...', ' .', '-', ''], np.nan)
    
    # 3. Supprimer les lignes de sources (53, 55, 56 par ex)
    # On ajuste l'index car Python commence à 0
    indices_to_drop = [i-1 for i in rows_to_drop if i-1 < len(df)]
    df = df.drop(df.index[indices_to_drop], errors='ignore')
    
    return df

st.title("📈 Analyseur d'Indicateurs FMI")

uploaded_file = st.file_uploader("Charger le PDF Article IV", type="pdf")

if uploaded_file:
    with pdfplumber.open(uploaded_file) as pdf:
        # Configuration Sidebar
        page_num = st.sidebar.number_input("Page du tableau", min_value=1, value=5)
        st.sidebar.subheader("Nettoyage")
        footer_rows = st.sidebar.text_input("Lignes à supprimer (ex: 53, 55, 56)", "53, 55, 56")
        
        # Extraction
        page = pdf.pages[page_num - 1]
        table = page.extract_table({"vertical_strategy": "text", "horizontal_strategy": "text", "text_x_tolerance": 3})
        
        if table:
            raw_df = pd.DataFrame(table)
            
            # Application du nettoyage
            to_drop = [int(x.strip()) for x in footer_rows.split(",") if x.strip().isdigit()]
            df = clean_data(raw_df, to_drop)
            
            # --- INTERACTION ---
            st.subheader("1. Aperçu des données extraites")
            st.dataframe(df, use_container_width=True)

            # Préparation pour le graphique
            # On suppose que la col 0 = indicateurs et les autres = années
            if st.checkbox("Activer l'analyse graphique"):
                try:
                    # On définit la ligne des années (souvent la ligne 1 ou 2)
                    header_row_idx = st.number_input("Index de la ligne contenant les années", 0, 5, 1)
                    years = df.iloc[header_row_idx, 1:].values
                    
                    # Sélection de l'indicateur
                    indicators = df.iloc[header_row_idx+1:, 0].dropna().unique()
                    selected_ind = st.selectbox("Sélectionnez un indicateur pour voir l'évolution", indicators)
                    
                    # Extraction des valeurs pour l'indicateur choisi
                    row_data = df[df.iloc[:, 0] == selected_ind].iloc[0, 1:].values
                    
                    # Conversion en numérique (on enlève les virgules et espaces)
                    clean_values = [float(str(x).replace(',', '').replace(' ', '')) if pd.notnull(x) else np.nan for x in row_data]
                    
                    # Création du DataFrame pour le graph
                    chart_df = pd.DataFrame({
                        "Année": years,
                        selected_ind: clean_values
                    }).dropna()

                    # Affichage du graphique
                    fig = px.line(chart_df, x="Année", y=selected_ind, markers=True, title=f"Évolution de : {selected_ind}")
                    st.plotly_chart(fig, use_container_width=True)
                    
                except Exception as e:
                    st.warning(f"Ajustez les lignes d'en-tête pour activer le graphique. Erreur : {e}")
