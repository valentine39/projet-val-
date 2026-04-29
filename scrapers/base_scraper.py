import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseScraper:

    def __init__(self, base_url: str, timeout: int = 10):
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (compatible; TimorDashboard/1.0)"
        })

    def get(self, endpoint: str, params: dict = None) -> dict:
        try:
            url = f"{self.base_url}{endpoint}"
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            logger.info(f"✅ Succès : {url}")
            return response.json()

        except requests.exceptions.Timeout:
            logger.error(f"⏱️ Timeout : {url}")
            return {}
        except requests.exceptions.HTTPError as e:
            logger.error(f"❌ HTTP Error {e.response.status_code}")
            return {}
        except Exception as e:
            logger.error(f"❌ Erreur : {e}")
            return {}
