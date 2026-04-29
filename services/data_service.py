import streamlit as st
from scrapers.banque_mondiale import BanqueMondialeScraper

class DataService:

    def __init__(self):
        self.scraper = BanqueMondialeScraper()

    @st.cache_data(ttl=86400, show_spinner=False)
    def get_country_data(_self, country_code: str) -> dict:
        """
        Récupère tous les indicateurs pour un pays
        Mis en cache 24h par pays
        """
        return _self.scraper.fetch_all(country_code)

    @st.cache_data(ttl=86400, show_spinner=False)
    def get_countries_list(_self) -> list:
        """
        Récupère la liste complète des pays 
        disponibles sur la Banque Mondiale
        """
        raw = _self.scraper.get("/country", params={
            "format": "json",
            "per_page": 300
        })

        if not raw or len(raw) < 2:
            return []

        countries = []
        for c in raw[1]:
            # Filtrer uniquement les vrais pays
            # (exclure régions, agrégats, etc.)
            if c.get("region", {}).get("id") != "NA":
                countries.append({
                    "code": c["id"],
                    "name": c["name"],
                    "region": c.get("region", {}).get("value", ""),
                    "capital": c.get("capitalCity", ""),
                })

        return sorted(countries, key=lambda x: x["name"])
