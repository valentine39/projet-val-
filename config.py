from dataclasses import dataclass, field

@dataclass
class Config:

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

    # ── Labels UI ─────────────────────────────────────────────────
    LABELS: dict = field(default_factory=lambda: {
        "PIB":          {"emoji": "📈", "label": "PIB Total", "unit": "Md$"},
        "PIB_HABITANT": {"emoji": "👤", "label": "PIB/Habitant", "unit": "$"},
        "CROISSANCE":   {"emoji": "📊", "label": "Croissance", "unit": "%"},
        "INFLATION":    {"emoji": "💰", "label": "Inflation", "unit": "%"},
        "CHOMAGE":      {"emoji": "💼", "label": "Chômage", "unit": "%"},
        "POPULATION":   {"emoji": "👥", "label": "Population", "unit": "M"},
    })

CONFIG = Config()
