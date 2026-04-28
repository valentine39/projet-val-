import streamlit as st
import pdfplumber
import pandas as pd
import numpy as np

st.set_page_config(page_title="IMF Precision Extractor", layout="wide")

st.title("🎯 Extracteur de Tableaux FMI : Mode Précision")
st.markdown("""
Les rapports du FMI n'ont pas de lignes verticales. 
Utilisez les curseurs à gauche pour aligner les colonnes si elles sont 'explosées'.
""")

uploaded_file = st.file_uploader("Charger le PDF (Azerbaïdjan/Argentine)", type="pdf")

# Paramètres de précision dans la barre latérale
st.sidebar.header("Réglages de détection")
x_tol = st.sidebar.slider("Tolérance Horizontale (x_tolerance)", 1, 15, 3, help="Augmentez si les mots d'une même cellule sont séparés.")
y_tol = st.sidebar.slider("Tolérance Verticale (y_tolerance)", 1, 15, 3, help="Augmentez si une ligne est coupée en deux.")
page_to_extract = st.sidebar.number_input("Page du PDF", min_value=1, value=5)

if uploaded_file:
    with pdfplumber.open(uploaded_file) as pdf:
        page = pdf.pages[page_to_extract - 1]
        
        # Stratégie de détection par texte (Indispensable pour le FMI)
        table_settings = {
            "vertical_strategy": "text",
            "horizontal_strategy": "text",
            "x_tolerance": x_tol,
            "y_tolerance": y_tol,
        }
        
        with st.spinner('Extraction...'):
            table = page.extract_table(table_settings)
            
            if table:
                df = pd.DataFrame(table)
                
                # --- NETTOYAGE CRUCIAL POUR LE FMI ---
                # 1. On enlève les lignes complètement vides
                df = df.dropna(how='all')
                
                # 2. On essaie de fusionner les deux premières lignes si c'est des en-têtes (ex: Projections + 2025)
                st.subheader("Aperçu des données brutes")
                st.dataframe(df, use_container_width=True)

                # Bouton pour nettoyer et exporter
                if st.button("Nettoyer et Préparer l'export"):
                    # Remplacement des tirets et points FMI
                    df = df.replace(['—', '...', ' .', '-', 'None', ''], np.nan)
                    
                    # On définit la ligne 0 comme header mais on garde le reste
                    df.columns = [f"Col_{i}" for i in range(len(df.columns))]
                    
                    st.success("Tableau prêt !")
                    st.dataframe(df)
                    
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button("📥 Télécharger CSV Propre", csv, "fmi_export.csv", "text/csv")
            else:
                st.error("Aucun tableau détecté sur cette page avec ces réglages. Augmentez les tolérances.")

st.info("💡 **Astuce pour l'Azerbaïdjan (Page 5) :** Si les chiffres sont collés au texte, diminuez 'x_tolerance'. S'ils sont trop éparpillés, augmentez-la.")
