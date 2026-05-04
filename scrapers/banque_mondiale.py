# ── scrapers/banque_mondiale.py ───────────────────────────────────────────────

import pandas as pd
from .base_scraper import BaseScraper


class BanqueMondialeScraper(BaseScraper):

    SOURCE_NAME = "Banque Mondiale"
    BASE_URL = "https://api.worldbank.org/v2"

    def fetch_countries(self) -> pd.DataFrame:
        """Récupère la liste des pays. Sécurisé contre les boucles infinies."""
        url = f"{self.BASE_URL}/country"
        all_countries = []
        max_pages = 10  # sécurité : jamais plus de 10 pages

        for page in range(1, max_pages + 1):
            params = {"format": "json", "per_page": 300, "page": page}
            try:
                data = self._get(url, params)
            except Exception:
                break

            if not data or len(data) < 2 or not data[1]:
                break

            meta, countries = data[0], data[1]

            for c in countries:
                if c.get("region", {}).get("id") != "NA":
                    all_countries.append({
                        "code": c["id"],
                        "name": c["name"],
                        "region": c.get("region", {}).get("value", ""),
                        "income_level": c.get("incomeLevel", {}).get("value", ""),
                    })

            if page >= meta.get("pages", 1):
                break

        if not all_countries:
            return pd.DataFrame(columns=["code", "name", "region", "income_level"])

        return pd.DataFrame(all_countries).sort_values("name").reset_index(drop=True)

    def fetch_indicator(
        self,
        country_code: str,
        indicator_code: str,
        years: int = 30,
    ) -> pd.DataFrame:
        """Récupère une série temporelle. Retourne DataFrame vide si échec."""
        url = f"{self.BASE_URL}/country/{country_code}/indicator/{indicator_code}"
        params = {"format": "json", "per_page": years, "mrv": years}

        try:
            data = self._get(url, params)
        except Exception:
            return pd.DataFrame(columns=["year", "value"])

        if not data or len(data) < 2 or not data[1]:
            return pd.DataFrame(columns=["year", "value"])

        records = []
        for entry in data[1]:
            year_str = entry.get("date", "")
            value = entry.get("value")
            if not year_str.isdigit():
                continue
            records.append({
                "year": int(year_str),
                "value": float(value) if value is not None else None,
            })

        if not records:
            return pd.DataFrame(columns=["year", "value"])

        return pd.DataFrame(records).sort_values("year").reset_index(drop=True)

    def fetch_multiple_indicators(
        self,
        country_code: str,
        indicator_codes: list,
        years: int = 30,
    ) -> dict:
        """Récupère plusieurs indicateurs. Chaque échec = DataFrame vide, pas de crash."""
        results = {}
        for code in indicator_codes:
            try:
                results[code] = self.fetch_indicator(country_code, code, years)
            except Exception:
                results[code] = pd.DataFrame(columns=["year", "value"])
        return results
