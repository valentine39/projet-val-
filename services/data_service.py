# ── services/data_service.py ──────────────────────────────────────────────────
# Couche de service : orchestre les scrapers, formate les données,
# construit les structures prêtes à l'affichage.
# C'est ici qu'on ajoutera FMI, Freedom House, WGI, etc.
# ─────────────────────────────────────────────────────────────────────────────

import pandas as pd
from typing import Optional
from scrapers.banque_mondiale import BanqueMondialeScraper
from config import INDICATORS, KPI_CODES, DATA_YEARS, WB_SOURCE_LABEL


class DataService:
    """
    Service central de données.

    Responsabilités :
    - Initialiser les scrapers
    - Mettre en cache les résultats (délégué à st.cache_data dans app.py)
    - Fournir des méthodes haut niveau à app.py

    Extension future :
        self.fmi = FMIScraper()
        self.freedom_house = FreedomHouseScraper()
        etc.
    """

    def __init__(self):
        self.wb = BanqueMondialeScraper()

    # ── Pays ──────────────────────────────────────────────────────────────────

    def get_countries(self) -> pd.DataFrame:
        """Liste complète des pays (code, name, region, income_level)."""
        return self.wb.fetch_countries()

    # ── Données brutes ────────────────────────────────────────────────────────

    def get_series(
        self,
        country_code: str,
        indicator_code: str,
        years: int = DATA_YEARS,
    ) -> pd.DataFrame:
        """Série temporelle brute pour un indicateur."""
        try:
            return self.wb.fetch_indicator(country_code, indicator_code, years)
        except Exception:
            return pd.DataFrame(columns=["year", "value"])

    def get_all_series(
        self,
        country_code: str,
        years: int = DATA_YEARS,
    ) -> dict[str, pd.DataFrame]:
        """Toutes les séries définies dans config.INDICATORS."""
        codes = list(INDICATORS.keys())
        try:
            return self.wb.fetch_multiple_indicators(country_code, codes, years)
        except Exception:
            return {c: pd.DataFrame(columns=["year", "value"]) for c in codes}

    # ── KPIs formatés ─────────────────────────────────────────────────────────

    def get_kpis(
        self,
        country_code: str,
        all_series: dict[str, pd.DataFrame] = None,
    ) -> list[dict]:
        """
        Retourne une liste de KPIs prêts à l'affichage.

        Chaque KPI = {
            label, value_raw, value_display, unit_display,
            year, source, source_url, delta, delta_label
        }
        """
        if all_series is None:
            all_series = self.get_all_series(country_code)

        kpis = []
        for code in KPI_CODES:
            meta = INDICATORS.get(code, {})
            df = all_series.get(code, pd.DataFrame(columns=["year", "value"]))

            scraper = self.wb  # à généraliser selon la source
            value, year = scraper.latest_value(df)

            # Calcul de la variation sur 1 an (delta)
            delta = None
            delta_label = ""
            if value is not None and not df.empty:
                prev_df = df[df["year"] < year].dropna(subset=["value"])
                if not prev_df.empty:
                    prev_val = prev_df.sort_values("year").iloc[-1]["value"]
                    prev_year = int(prev_df.sort_values("year").iloc[-1]["year"])
                    if prev_val and prev_val != 0:
                        delta = ((value - prev_val) / abs(prev_val)) * 100
                        delta_label = f"vs {prev_year}"

            # Formatage de la valeur
            if value is not None:
                scale = meta.get("scale", 1)
                fmt = meta.get("format", ".2f")
                scaled = value / scale
                value_display = f"{scaled:{fmt}}"
            else:
                value_display = "N/D"

            kpis.append({
                "code": code,
                "label": meta.get("label", code),
                "value_raw": value,
                "value_display": value_display,
                "unit_display": meta.get("unit_display", ""),
                "unit": meta.get("unit", ""),
                "year": year,
                "source": meta.get("source", WB_SOURCE_LABEL),
                "source_url": meta.get("source_url", ""),
                "description": meta.get("description", ""),
                "delta": delta,
                "delta_label": delta_label,
            })

        return kpis

    # ── Tableau sourcé ────────────────────────────────────────────────────────

    def get_summary_table(
        self,
        country_code: str,
        all_series: dict[str, pd.DataFrame] = None,
    ) -> pd.DataFrame:
        """
        Retourne le tableau récapitulatif complet (tous les indicateurs).
        Prêt à afficher avec st.dataframe().
        """
        if all_series is None:
            all_series = self.get_all_series(country_code)

        rows = []
        for code, meta in INDICATORS.items():
            df = all_series.get(code, pd.DataFrame(columns=["year", "value"]))
            value, year = self.wb.latest_value(df)

            if value is not None:
                scale = meta.get("scale", 1)
                fmt = meta.get("format", ".2f")
                scaled = value / scale
                value_str = f"{scaled:{fmt}} {meta.get('unit_display', '')}"
            else:
                value_str = "Donnée non disponible"
                year = "—"

            rows.append({
                "Indicateur": meta.get("label", code),
                "Valeur": value_str,
                "Année": str(year) if year else "—",
                "Unité": meta.get("unit", ""),
                "Source": meta.get("source", WB_SOURCE_LABEL),
                "Lien": meta.get("source_url", ""),
            })

        return pd.DataFrame(rows)

    # ── Helpers graphiques ────────────────────────────────────────────────────

    def get_series_for_chart(
        self,
        country_code: str,
        codes: list[str],
        all_series: dict[str, pd.DataFrame] = None,
        years: int = DATA_YEARS,
    ) -> dict[str, pd.DataFrame]:
        """Retourne plusieurs séries pour un graphique multi-courbes."""
        if all_series is not None:
            return {c: all_series.get(c, pd.DataFrame(columns=["year", "value"])) for c in codes}
        return self.wb.fetch_multiple_indicators(country_code, codes, years)

