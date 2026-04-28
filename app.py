import streamlit as st
import tabula
import pandas as pd
import numpy as np

st.set_page_config(page_title="Extracteur FMI Précis", layout="wide")

st.title("📊 Extracteur de Tableaux FMI (Haute Précision)")
st.write("Cette version utilise un moteur d'analyse de grille (Tabula) pour éviter les décalages de colonnes.")

uploaded_file = st.file_uploader("Déposez le rapport Article IV", type="pdf")

if uploaded_file:
    # On demande à l'utilisateur quelle page viser pour être ultra précis
    # (Exemple : Page 5 pour l'Azerbaïdjan)
    page_num = st.number_input("Numéro de la page où se trouve le tableau :", min_value=1, value=5)

    if st.button("Extraire la page"):
        with st.spinner('Analyse de la structure...'):
            try:
                # lattice=False car le FMI n'a pas de bordures de cellules
                # stream=True force l'analyse de l'alignement du texte en colonnes
                tables = tabula.read_pdf(uploaded_file, pages=page_num, stream=True, guess=True)

                if tables:
                    df = tables[0]
                    
                    # Nettoyage automatique des colonnes "Unnamed"
                    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
                    
                    # Remplacement des symboles FMI par du vide pour la clarté
                    df = df.replace(['—', '...', ' .', '-'], np.nan)

                    st.subheader(f"Tableau extrait de la page {page_num}")
                    st.dataframe(df, use_container_width=True)

                    # Export
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button("📥 Télécharger en CSV", csv, "extract.csv", "text/csv")
                else:
                    st.error("Aucun tableau trouvé sur cette page.")
            except Exception as e:
                st.error(f"Erreur : {e}")

st.divider()
st.info("💡 **Conseil :** Si les colonnes sont encore mélangées, cochez 'Stream' ou essayez une page voisine (le numéro de page PDF diffère parfois du numéro écrit sur le papier).")
