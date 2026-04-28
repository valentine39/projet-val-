# VERSION AVEC LIENS VÉRIFIABLES INTÉGRÉS

import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

def ind(label, value, unit=None, year=None, source=None, url=None, note=None):
    return {
        "Indicateur": label,
        "Valeur": value,
        "Unité": unit,
        "Année": year,
        "Source": source,
        "URL source": url,
        "Note": note
    }

def show_section(title, subtitle, rows, source_url=None, source_label=None):
    st.markdown(f"## {title}")
    st.markdown(subtitle)

    if not rows:
        st.warning("Aucune donnée disponible")
        return

    DISPLAY_COLS = ["Indicateur", "Valeur", "Unité", "Année", "Source", "URL source", "Note"]
    df = pd.DataFrame(rows)[DISPLAY_COLS]

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "URL source": st.column_config.LinkColumn(
                "Lien vérifiable",
                display_text="ouvrir"
            )
        }
    )

    if source_url:
        st.markdown(f"[Source globale]({source_url})")

# EXEMPLE

rows = [
    ind("PIB nominal", 1865608515, "USD", 2024, "Banque mondiale", "https://data.worldbank.org/indicator/NY.GDP.MKTP.CD"),
    ind("Croissance PIB", -9.1, "%", 2024, "Banque mondiale", "https://data.worldbank.org/indicator/NY.GDP.MKTP.KD.ZG"),
    ind("Inflation", 2.1, "%", 2024, "Banque mondiale", "https://data.worldbank.org/indicator/FP.CPI.TOTL.ZG")
]

show_section(
    "Bloc exemple",
    "Test avec liens cliquables",
    rows
)
