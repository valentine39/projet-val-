from dataclasses import dataclass, field

@dataclass
class Config:

    # ── Pays par défaut ───────────────────────────────────────────
    COUNTRY_CODE: str = "TLS"
    COUNTRY_NAME: str = "Timor-Leste"

    # ── Cache ─────────────────────────────────────────────────────
    CACHE_TTL: int      = 3600
    CACHE_TTL_LONG: int = 86400

    # ── API ───────────────────────────────────────────────────────
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

    # ── Style ─────────────────────────────────────────────────────
    PRIMARY_COLOR: str   = "#1e3a5f"
    SECONDARY_COLOR: str = "#2d6a9f"
    ACCENT_COLOR: str    = "#f0c040"

CONFIG = Config()
