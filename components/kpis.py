import streamlit as st
import pandas as pd

def format_value(valeur: float, nom: str) -> str:
    """Formate la valeur selon le type d'indicateur"""
    if nom == "PIB":
        if valeur >= 1e12:
            return f"{valeur/1e12:.2f} T$"
        elif valeur >= 1e9:
            return f"{valeur/1e9:.2f} Md$"
        elif valeur >= 1e6:
            return f"{valeur/1e6:.1f} M$"
        return f"{valeur:,.0f} $"
    elif nom == "POPULATION":
        if valeur >= 1e9:
            return f"{valeur/1e9:.2f} Md"
        elif valeur >= 1e6:
            return f"{valeur/1e6:.1f} M"
        return f"{valeur:,.0f}"
    elif nom in ("PIB_HABITANT",):
        return f"{valeur:,.0f} $"
    else:
        return f"{valeur:.1f} %"

def get_delta(df: pd.DataFrame) -> str:
    """Calcule la variation entre les 2 dernières années"""
    if len(df) < 2:
        return None
    avant_dernier = df.iloc[-2]["valeur"]
    dernier = df.iloc[-1]["valeur"]
    if avant_dernier == 0:
        return None
    delta = ((dernier - avant_dernier) / abs(avant_dernier)) * 100
    signe = "+" if delta > 0 else ""
    return f"{signe}{delta:.1f}%"

def render_kpis(data: dict):
    """Affiche les cartes KPI"""

    kpi_config = {
        "PIB":          ("💰", "PIB Total"),
        "PIB_HABITANT": ("👤", "PIB / Habitant"),
        "CROISSANCE":   ("📈", "Croissance"),
        "INFLATION":    ("🔥", "Inflation"),
        "CHOMAGE":      ("💼", "Chômage"),
        "POPULATION":   ("👥", "Population"),
    }

    cols = st.columns(len(kpi_config))

    for col, (nom, (icone, label)) in zip(cols, kpi_config.items()):
        with col:
            df = data.get(nom)
            if df is not None and not df.empty:
                derniere = df.iloc[-1]
                annee = int(derniere["année"])
                valeur_fmt = format_value(derniere["valeur"], nom)
                delta = get_delta(df)
                st.metric(
                    label=f"{icone} {label}",
                    value=valeur_fmt,
                    delta=delta,
                    help=f"Dernière année disponible : {annee}"
                )
            else:
                st.metric(label=f"{icone} {label}", value="N/D")
