# ── scrapers/banque_mondiale.py ───────────────────────────────────────────────
# Scraper pour l'API publique de la Banque Mondiale (World Bank Open Data).
# Documentation : https://datahelpdesk.worldbank.org/knowledgebase/articles/889392
# ─────────────────────────────────────────────────────────────────────────────

import pandas as pd
from typing import Optional
from .base_scraper import BaseScraper


class BanqueMondialeScraper(BaseScraper):
    """
    Interface vers l'API World Development Indicators (WDI) de la Banque Mondiale.

    Endpoints utilisés :
      - /country            → liste des pays
      - /country/{cc}/indicator/{code} → série temporelle
    """

    SOURCE_NAME = "Banque Mondiale"
    BASE_URL = "https://api.worldbank.org/v2"

    def fetch_countries(self) -> pd.DataFrame:
        """
        Récupère tous les pays reconnus par la Banque Mondiale.
        Filtre : type == 'Country' (exclut agrégats régionaux).
        """
        url = f"{self.BASE_URL}/country"
        params = {
            "format": "json",
            "per_page": 300,
            "page": 1,
        }

        all_countries = []
        while True:
            data = self._get(url, params)
            if not data or len(data) < 2:
                break

            meta, countries = data[0], data[1]
            if not countries:
                break

            for c in countries:
                # Garder uniquement les vrais pays (pas les agrégats)
                if c.get("region", {}).get("id") != "NA":
                    all_countries.append({
                        "code": c["id"],
                        "name": c["name"],
                        "region": c.get("region", {}).get("value", ""),
                        "income_level": c.get("incomeLevel", {}).get("value", ""),
                    })

            if meta.get("page", 1) >= meta.get("pages", 1):
                break
            params["page"] += 1

        df = pd.DataFrame(all_countries)
        if df.empty:
            return df

        df = df.sort_values("name").reset_index(drop=True)
        return df

    def fetch_indicator(
        self,
        country_code: str,
        indicator_code: str,
        years: int = 30,
    ) -> pd.DataFrame:
        """
        Récupère une série temporelle depuis l'API WDI.

        Args:
            country_code : code ISO-2 du pays (ex : "TL", "FR", "KM")
            indicator_code : code WDI (ex : "NY.GDP.MKTP.CD")
            years : nombre d'années à récupérer

        Returns:
            DataFrame [year: int, value: float] trié par année croissante.
            Retourne un DataFrame vide si aucune donnée.
        """
        url = f"{self.BASE_URL}/country/{country_code}/indicator/{indicator_code}"
        params = {
            "format": "json",
            "per_page": years,
            "mrv": years,          # most recent values
        }

        data = self._get(url, params)

        if not data or len(data) < 2 or not data[1]:
            return pd.DataFrame(columns=["year", "value"])

        records = []
        for entry in data[1]:
            year_str = entry.get("date", "")
            value = entry.get("value")

            # Ignorer les dates non-annuelles (ex : "2022Q3")
            if not year_str.isdigit():
                continue

            records.append({
                "year": int(year_str),
                "value": float(value) if value is not None else None,
            })

        if not records:
            return pd.DataFrame(columns=["year", "value"])

        df = pd.DataFrame(records).sort_values("year").reset_index(drop=True)
        return df

    def fetch_multiple_indicators(
        self,
        country_code: str,
        indicator_codes: list[str],
        years: int = 30,
    ) -> dict[str, pd.DataFrame]:
        """
        Récupère plusieurs indicateurs en une seule passe.

        Returns:
            Dict { indicator_code → DataFrame }
        """
        results = {}
        for code in indicator_codes:
            try:
                results[code] = self.fetch_indicator(country_code, code, years)
            except Exception as e:
                # Donnée manquante = DataFrame vide, pas un crash
                results[code] = pd.DataFrame(columns=["year", "value"])
        return results

