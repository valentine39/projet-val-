from dataclasses import dataclass, field

@dataclass
class Config:

    # ── Timor-Leste ───────────────────────────────────────────────
    COUNTRY_CODE: str = "TLS"
    COUNTRY_NAME: str = "Timor-Leste"

    # ── Cache ─────────────────────────────────────────────────────
    CACHE_TTL: int       = 3600    # 1h  → données fréquentes
    CACHE_TTL_LONG: int  = 86400   # 24h → données stables

    # ── Banque Mondiale ───────────────────────────────────────────
    BM_BASE_URL: str = "https://api.worldbank.org/v2"

    # ── Indicateurs ───────────────────────────────────────────────
    INDICATORS: dict = field(default_factory=lambda: {
        "PIB":          "NY.GDP.MKTP.CD",
        "PIB_HABITANT": "NY.GDP.PCAP.CD",
        "CROISSANCE":   "NY.GDP.MKTP.KD.ZG",
        "INFLATION":    "FP.CPI.TOTL.ZG",
        "CHOMAGE":      "SL.UEM.TOTL.ZS",
        "POPULATION":   "SP.POP.TOTL",
    })

# Instance globale
CONFIG = Config()
