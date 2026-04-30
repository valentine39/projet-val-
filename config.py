from dataclasses import dataclass, field

@dataclass
class Config:
    BM_BASE_URL: str = "https://api.worldbank.org/v2"

    INDICATORS: dict = field(default_factory=lambda: {
        "PIB": {
            "code": "NY.GDP.MKTP.CD",
            "label": "PIB nominal",
            "unit": "USD courants",
            "source": "Banque mondiale",
            "url": "https://data.worldbank.org/indicator/NY.GDP.MKTP.CD"
        },
        "PIB_HABITANT": {
            "code": "NY.GDP.PCAP.CD",
            "label": "PIB par habitant",
            "unit": "USD courants",
            "source": "Banque mondiale",
            "url": "https://data.worldbank.org/indicator/NY.GDP.PCAP.CD"
        },
        "CROISSANCE": {
            "code": "NY.GDP.MKTP.KD.ZG",
            "label": "Croissance du PIB réel",
            "unit": "% annuel",
            "source": "Banque mondiale",
            "url": "https://data.worldbank.org/indicator/NY.GDP.MKTP.KD.ZG"
        },
        "INFLATION": {
            "code": "FP.CPI.TOTL.ZG",
            "label": "Inflation",
            "unit": "% annuel",
            "source": "Banque mondiale",
            "url": "https://data.worldbank.org/indicator/FP.CPI.TOTL.ZG"
        },
        "CHOMAGE": {
            "code": "SL.UEM.TOTL.ZS",
            "label": "Chômage",
            "unit": "% de la population active",
            "source": "Banque mondiale",
            "url": "https://data.worldbank.org/indicator/SL.UEM.TOTL.ZS"
        },
        "POPULATION": {
            "code": "SP.POP.TOTL",
            "label": "Population totale",
            "unit": "personnes",
            "source": "Banque mondiale",
            "url": "https://data.worldbank.org/indicator/SP.POP.TOTL"
        },
    })

CONFIG = Config()
