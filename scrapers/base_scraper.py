# ── scrapers/base_scraper.py ─────────────────────────────────────────────────
# Classe de base abstraite pour tous les scrapers de sources de données.
# Chaque source (Banque Mondiale, FMI, Freedom House…) hérite de cette classe.
# ─────────────────────────────────────────────────────────────────────────────

from abc import ABC, abstractmethod
import requests
import pandas as pd
from typing import Optional


class BaseScraper(ABC):
    """
    Classe de base pour les scrapers de données économiques.

    Pour ajouter une nouvelle source :
    1. Créer scrapers/nouvelle_source.py
    2. Hériter de BaseScraper
    3. Implémenter fetch_indicator() et fetch_countries()
    4. Enregistrer dans services/data_service.py
    """

    SOURCE_NAME: str = ""
    BASE_URL: str = ""
    TIMEOUT: int = 15

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "DashboardEco/1.0 (educational project)",
            "Accept": "application/json",
        })

    def _get(self, url: str, params: dict = None) -> Optional[dict]:
        """GET sécurisé avec gestion d'erreur."""
        try:
            resp = self.session.get(url, params=params, timeout=self.TIMEOUT)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.Timeout:
            raise ConnectionError(f"[{self.SOURCE_NAME}] Timeout sur {url}")
        except requests.exceptions.HTTPError as e:
            raise ConnectionError(f"[{self.SOURCE_NAME}] HTTP {e.response.status_code}")
        except requests.exceptions.ConnectionError:
            raise ConnectionError(f"[{self.SOURCE_NAME}] Impossible de joindre l'API")
        except Exception as e:
            raise RuntimeError(f"[{self.SOURCE_NAME}] Erreur inattendue : {e}")

    @abstractmethod
    def fetch_indicator(
        self,
        country_code: str,
        indicator_code: str,
        years: int = 25,
    ) -> pd.DataFrame:
        """
        Récupère une série temporelle pour un pays et un indicateur.

        Returns:
            DataFrame avec colonnes : year (int), value (float)
        """
        pass

    @abstractmethod
    def fetch_countries(self) -> pd.DataFrame:
        """
        Retourne la liste des pays disponibles.

        Returns:
            DataFrame avec colonnes : code (str), name (str)
        """
        pass

    def latest_value(self, df: pd.DataFrame) -> tuple[Optional[float], Optional[int]]:
        """Extrait la valeur et l'année les plus récentes (non-nulles)."""
        if df is None or df.empty:
            return None, None
        valid = df.dropna(subset=["value"]).sort_values("year", ascending=False)
        if valid.empty:
            return None, None
        row = valid.iloc[0]
        return float(row["value"]), int(row["year"])

