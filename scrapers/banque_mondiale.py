def fetch_all(self, country_code: str) -> dict:
    results = {}

    for key, meta in CONFIG.INDICATORS.items():
        df = self.fetch(meta["code"], country_code)
        results[key] = df

    return results
