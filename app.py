import streamlit as st
import pdfplumber
import pandas as pd
import numpy as np

st.set_page_config(page_title="IMF Table Extractor", layout="wide")

st.title("📊 Extracteur de Tableaux Article IV")

uploaded_file = st.file_uploader("Glissez le PDF ici", type="pdf")

if uploaded_file:
    with st.spinner('Analyse...'):
        with pdfplumber.open(uploaded_file) as pdf:
            all_tables = []
            for i, page in enumerate(pdf.pages):
                tables = page.extract_tables()
                for idx, table in enumerate(tables):
                    df = pd.DataFrame(table)
                    if not df.empty:
                        all_tables.append({"page": i + 1, "data": df})

    if all_tables:
        page_list = [f"Tableau {i+1} (Page {t['page']})" for i, t in enumerate(all_tables)]
        selected_idx = st.sidebar.selectbox("Tableau", range(len(all_tables)), format_func=lambda x: page_list[x])
        
        df = all_tables[selected_idx]['data'].copy()

        if st.checkbox("Utiliser la première ligne comme en-tête", value=True):
            # Gestion des doublons de colonnes
            cols = df.iloc[0].fillna("SansNom").astype(str).values
            new_cols = []
            counts = {}
            for c in cols:
                suffix = counts.get(c, 0)
                if suffix > 0:
                    new_cols.append(f"{c}_{suffix}")
                else:
                    new_cols.append(c)
                counts[c] = suffix + 1
            
            df.columns = new_cols
            df = df[1:]

        # Nettoyage final des symboles FMI
        df = df.replace(['—', '...', ' .', '-'], np.nan)
        
        st.dataframe(df, use_container_width=True)
        st.download_button("Télécharger CSV", df.to_csv(index=False), "export.csv")
