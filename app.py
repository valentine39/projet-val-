import streamlit as st
import pdfplumber
import pandas as pd
import numpy as np
import io

st.set_page_config(page_title="IMF Table Extractor", layout="wide")

def clean_imf_table(df):
    """Nettoie les données typiques des rapports du FMI"""
    # Remplacer les symboles de données manquantes du FMI par NaN ou 0
    symbols_to_replace = ['—', '...', ' .', '. ', '..', '-']
    df = df.replace(symbols_to_replace, np.nan)
    
    # Supprimer les lignes et colonnes totalement vides
    df = df.dropna(how='all', axis=0).dropna(how='all', axis=1)
    
    return df

st.title("📊 Extracteur de Tableaux Article IV (FMI)")
st.info("Structure détectée : Rapports types Azerbaïdjan/Argentine. L'extraction utilise la stratégie 'Text alignment'.")

uploaded_file = st.file_uploader("Glissez le PDF de l'Article IV ici", type="pdf")

if uploaded_file:
    # Paramètres d'extraction optimisés pour le format FMI
    # On utilise "text" car le FMI n'utilise pas souvent de lignes verticales
    table_settings = {
        "vertical_strategy": "text",
        "horizontal_strategy": "lines", # ou "text" selon le rapport
        "snap_tolerance": 3,
    }

    with st.spinner('Analyse des tableaux en cours... (Cela peut prendre une minute pour les rapports longs)'):
        with pdfplumber.open(uploaded_file) as pdf:
            all_tables = []
            
            # Pour ne pas surcharger, on peut limiter ou laisser l'utilisateur choisir
            # Ici on parcourt tout le document
            for i, page in enumerate(pdf.pages):
                extracted_tables = page.extract_tables(table_settings=table_settings)
                
                for idx, table in enumerate(extracted_tables):
                    df = pd.DataFrame(table)
                    
                    if not df.empty and len(df.columns) > 1: # On ignore les mini-tableaux
                        df = clean_imf_table(df)
                        all_tables.append({
                            "page": i + 1,
                            "data": df
                        })

    if all_tables:
        st.success(f"Nombre de tableaux trouvés : {len(all_tables)}")
        
        # Barre latérale pour la navigation
        page_list = [f"Tableau {i+1} (Page {t['page']})" for i, t in enumerate(all_tables)]
        selected_table_idx = st.sidebar.selectbox("Sélectionnez un tableau", range(len(all_tables)), format_func=lambda x: page_list[x])
        
        # Affichage du tableau sélectionné
        current_table = all_tables[selected_table_idx]['data']
        
        st.subheader(f"Visualisation : {page_list[selected_table_idx]}")
        
        # Option pour définir la première ligne comme en-tête
        if st.checkbox("Utiliser la première ligne comme en-tête", value=True):
            new_header = current_table.iloc[0]
            current_table = current_table[1:]
            current_table.columns = new_header

        st.dataframe(current_table, use_container_width=True)

        # Export
        csv = current_table.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Télécharger ce tableau en CSV",
            data=csv,
            file_name=f"IMF_Table_Page_{all_tables[selected_table_idx]['page']}.csv",
            mime='text/csv',
        )
    else:
        st.error("Aucun tableau détecté. Essayez de modifier les paramètres d'extraction.")
