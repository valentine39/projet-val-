import streamlit as st
import pdfplumber
import pandas as pd
import numpy as np

st.set_page_config(page_title="IMF Data Extractor Pro", layout="wide")

def is_real_table(df):
    """Vérifie si le tableau ressemble à un vrai tableau de données (min 3 colonnes et 3 lignes)"""
    return df.shape[1] > 2 and df.shape[0] > 2

def clean_column_names(columns):
    """Dédoublonne et nettoie les noms de colonnes pour éviter les erreurs Arrow"""
    cols = [str(c).replace('\n', ' ').strip() if c else f"Col_{i}" for i, c in enumerate(columns)]
    new_cols = []
    counts = {}
    for c in cols:
        if c in counts:
            counts[c] += 1
            new_cols.append(f"{c}_{counts[c]}")
        else:
            counts[c] = 0
            new_cols.append(c)
    return new_cols

st.title("📊 Extracteur Ciblé : Rapports Article IV")
st.markdown("Cette version filtre les éléments de mise en page pour ne garder que les tableaux de données.")

uploaded_file = st.file_uploader("Charger un rapport FMI (PDF)", type="pdf")

if uploaded_file:
    # On stocke les tableaux dans le 'session_state' pour éviter de re-scanner le PDF à chaque clic
    if 'all_tables' not in st.session_state:
        with st.spinner('Analyse approfondie du rapport...'):
            extracted = []
            with pdfplumber.open(uploaded_file) as pdf:
                for i, page in enumerate(pdf.pages):
                    # Stratégie hybride pour le FMI
                    tables = page.extract_tables({
                        "vertical_strategy": "text",
                        "horizontal_strategy": "lines",
                        "snap_tolerance": 3,
                    })
                    
                    for idx, table in enumerate(tables):
                        df = pd.DataFrame(table)
                        # FILTRE : On ne garde que les "vrais" tableaux
                        if is_real_table(df):
                            # Nettoyage des caractères FMI
                            df = df.replace(['—', '...', ' .', '-', 'None', None], np.nan)
                            extracted.append({
                                "page": i + 1,
                                "data": df,
                                "id": f"Page {i+1} - Table {idx+1}"
                            })
            st.session_state.all_tables = extracted

    if st.session_state.all_tables:
        st.sidebar.header("Navigation")
        options = [t['id'] for t in st.session_state.all_tables]
        selection = st.sidebar.selectbox("Sélectionner un tableau de données", options)
        
        # Récupération du tableau choisi
        table_data = next(t for t in st.session_state.all_tables if t['id'] == selection)
        df_to_show = table_data['data'].copy()

        st.subheader(f"Extraction : {selection}")

        col1, col2 = st.columns([3, 1])
        
        with col2:
            st.write("**Paramètres**")
            use_header = st.checkbox("Première ligne = En-tête", value=True)
            drop_empty = st.checkbox("Supprimer lignes vides", value=True)

        if use_header:
            df_to_show.columns = clean_column_names(df_to_show.iloc[0])
            df_to_show = df_to_show[1:]

        if drop_empty:
            df_to_show = df_to_show.dropna(how='all')

        # Affichage
        st.dataframe(df_to_show, use_container_width=True)

        # Download
        csv = df_to_show.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Télécharger CSV", csv, f"{selection.replace(' ', '_')}.csv", "text/csv")
    else:
        st.warning("Aucun tableau de données significatif n'a été trouvé. Vérifiez que le PDF n'est pas un scan (image).")

if st.button("Réinitialiser"):
    st.session_state.clear()
    st.rerun()
