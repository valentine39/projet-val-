import streamlit as st
import pdfplumber
import pandas as pd
import numpy as np

st.set_page_config(page_title="IMF Precision Extractor", layout="wide")

st.title("🎯 Extracteur FMI : Version Finale")

uploaded_file = st.file_uploader("Charger le PDF", type="pdf")

# Réglages dans la barre latérale
st.sidebar.header("Réglages de précision")
# On baisse les valeurs par défaut car ton CSV montrait des colonnes fusionnées
x_tol = st.sidebar.slider("Finesse des colonnes (x_tol)", 1, 10, 2)
y_tol = st.sidebar.slider("Finesse des lignes (y_tol)", 1, 10, 3)
page_to_extract = st.sidebar.number_input("Page du PDF", min_value=1, value=5)

if uploaded_file:
    with pdfplumber.open(uploaded_file) as pdf:
        if page_to_extract > len(pdf.pages):
            st.error("Cette page n'existe pas dans le document.")
        else:
            page = pdf.pages[page_to_extract - 1]
            
            # Paramètres CORRIGÉS pour éviter le TypeError
            table_settings = {
                "vertical_strategy": "text",
                "horizontal_strategy": "text",
                "text_x_tolerance": x_tol, # Le nom exact est text_x_tolerance
                "text_y_tolerance": y_tol, # Le nom exact est text_y_tolerance
            }
            
            with st.spinner('Extraction en cours...'):
                table = page.extract_table(table_settings)
                
                if table:
                    df = pd.DataFrame(table)
                    
                    # Nettoyage des lignes vides
                    df = df.dropna(how='all')
                    
                    st.subheader(f"Résultat de la Page {page_to_extract}")
                    
                    # Option pour nettoyer les espaces doubles (fréquent au FMI)
                    if st.checkbox("Nettoyer les cellules (supprimer espaces inutiles)", value=True):
                        df = df.applymap(lambda x: " ".join(x.split()) if isinstance(x, str) else x)

                    st.dataframe(df, use_container_width=True)

                    # Exportation
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Télécharger ce tableau (CSV)",
                        data=csv,
                        file_name=f"IMF_Page_{page_to_extract}.csv",
                        mime='text/csv'
                    )
                else:
                    st.warning("Aucun tableau détecté. Essayez de DIMINUER la valeur de 'Finesse des colonnes'.")

st.markdown("""
---
### 💡 Comment obtenir un résultat parfait ?
1. **Si les chiffres sont collés dans une seule colonne :** Baissez `x_tol` à **1** ou **2**.
2. **Si une phrase est coupée en deux colonnes :** Augmentez légèrement `x_tol`.
3. **Si le tableau est vide :** C'est que les réglages sont trop stricts pour ce PDF.
""")
