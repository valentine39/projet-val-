import pandas as pd
from scrapers.base_scraper import BaseScraper
from config import CONFIG

class BanqueMondialeScraper(BaseScraper):

    def __init__(self):
        super().__init__(base_url=CONFIG.BM_BASE_URL)

    def fetch(self, indicator: str, years: int = 10) -> pd.DataFrame:
        endpoint = f"/country/{CONFIG.COUNTRY_CODE}/indicator/{indicator}"
        params = {
            "format": "json",
            "per_page": years,
            "mrv": years
        }

        raw = self.get(endpoint, params=params)

        # L'API retourne [metadata, data]
        if not raw or len(raw) < 2:
            return pd.DataFrame()

        records = []
        for entry in raw[1]:
            if entry.get("value") is not None:
                records.append({
                    "année": int(entry["date"]),
                    "valeur": float(entry["value"]),
                })

        df = pd.DataFrame(records).sort_values("année").reset_index(drop=True)
        return df

    def fetch_all(self) -> dict:
        """Récupère tous les indicateurs configurés"""
        results = {}
        for nom, code in CONFIG.INDICATORS.items():
            df = self.fetch(code)
            if not df.empty:
                results[nom] = df
        return results
