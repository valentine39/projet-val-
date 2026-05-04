# ── config.py ────────────────────────────────────────────────────────────────
# Centralise tous les indicateurs, labels, unités et métadonnées sources.
# Ajouter ici un nouvel indicateur = disponible partout dans l'app.
# ─────────────────────────────────────────────────────────────────────────────

APP_TITLE = "Fondamentaux Économiques"
APP_SUBTITLE = "Sources : Banque Mondiale · FMI (phase 1)"
DATA_YEARS = 30  # fenêtre historique pour les séries temporelles

# ── Banque Mondiale ───────────────────────────────────────────────────────────
WB_BASE_URL = "https://api.worldbank.org/v2"
WB_SOURCE_LABEL = "Banque Mondiale — World Development Indicators"
WB_SOURCE_URL = "https://data.worldbank.org/indicator/{code}"

INDICATORS = {
    # code WB : métadonnées complètes
    "NY.GDP.MKTP.CD": {
        "label": "PIB nominal",
        "unit": "USD courants",
        "unit_display": "Md USD",
        "scale": 1e9,
        "format": ".2f",
        "pilier": 2,
        "description": "Produit Intérieur Brut en valeur nominale (USD courants)",
        "source": WB_SOURCE_LABEL,
        "source_url": WB_SOURCE_URL.format(code="NY.GDP.MKTP.CD"),
    },
    "NY.GDP.PCAP.CD": {
        "label": "PIB par habitant",
        "unit": "USD courants",
        "unit_display": "USD",
        "scale": 1,
        "format": ",.0f",
        "pilier": 2,
        "description": "PIB divisé par la population totale (USD courants)",
        "source": WB_SOURCE_LABEL,
        "source_url": WB_SOURCE_URL.format(code="NY.GDP.PCAP.CD"),
    },
    "NY.GDP.MKTP.KD.ZG": {
        "label": "Croissance du PIB réel",
        "unit": "%",
        "unit_display": "%",
        "scale": 1,
        "format": ".1f",
        "pilier": 2,
        "description": "Taux de croissance annuel du PIB en volume (prix constants)",
        "source": WB_SOURCE_LABEL,
        "source_url": WB_SOURCE_URL.format(code="NY.GDP.MKTP.KD.ZG"),
    },
    "FP.CPI.TOTL.ZG": {
        "label": "Inflation (IPC)",
        "unit": "% annuel",
        "unit_display": "%",
        "scale": 1,
        "format": ".1f",
        "pilier": 3,
        "description": "Variation annuelle de l'indice des prix à la consommation",
        "source": WB_SOURCE_LABEL,
        "source_url": WB_SOURCE_URL.format(code="FP.CPI.TOTL.ZG"),
    },
    "SL.UEM.TOTL.ZS": {
        "label": "Chômage",
        "unit": "% de la pop. active",
        "unit_display": "%",
        "scale": 1,
        "format": ".1f",
        "pilier": 1,
        "description": "Taux de chômage (% de la population active totale, modélisation OIT)",
        "source": WB_SOURCE_LABEL,
        "source_url": WB_SOURCE_URL.format(code="SL.UEM.TOTL.ZS"),
    },
    "SP.POP.TOTL": {
        "label": "Population totale",
        "unit": "habitants",
        "unit_display": "M hab.",
        "scale": 1e6,
        "format": ".2f",
        "pilier": 1,
        "description": "Population totale (estimation en milieu d'année)",
        "source": WB_SOURCE_LABEL,
        "source_url": WB_SOURCE_URL.format(code="SP.POP.TOTL"),
    },
    # ── Indicateurs sociaux supplémentaires (pilier 1) ──────────────────────
    "SP.DYN.LE00.IN": {
        "label": "Espérance de vie",
        "unit": "années",
        "unit_display": "ans",
        "scale": 1,
        "format": ".1f",
        "pilier": 1,
        "description": "Espérance de vie à la naissance (années)",
        "source": WB_SOURCE_LABEL,
        "source_url": WB_SOURCE_URL.format(code="SP.DYN.LE00.IN"),
    },
    "SP.DYN.IMRT.IN": {
        "label": "Mortalité infantile",
        "unit": "‰ naissances vivantes",
        "unit_display": "‰",
        "scale": 1,
        "format": ".1f",
        "pilier": 1,
        "description": "Taux de mortalité des enfants de moins de 5 ans (pour 1 000 naissances vivantes)",
        "source": WB_SOURCE_LABEL,
        "source_url": WB_SOURCE_URL.format(code="SP.DYN.IMRT.IN"),
    },
    "SE.ADT.LITR.ZS": {
        "label": "Taux d'alphabétisation adulte",
        "unit": "%",
        "unit_display": "%",
        "scale": 1,
        "format": ".1f",
        "pilier": 1,
        "description": "% des adultes (15+) sachant lire et écrire",
        "source": WB_SOURCE_LABEL,
        "source_url": WB_SOURCE_URL.format(code="SE.ADT.LITR.ZS"),
    },
    # ── Finances publiques (pilier 3) ────────────────────────────────────────
    "GC.BAL.CASH.GD.ZS": {
        "label": "Solde budgétaire",
        "unit": "% du PIB",
        "unit_display": "% PIB",
        "scale": 1,
        "format": ".1f",
        "pilier": 3,
        "description": "Solde net de caisse des administrations publiques (% du PIB)",
        "source": WB_SOURCE_LABEL,
        "source_url": WB_SOURCE_URL.format(code="GC.BAL.CASH.GD.ZS"),
    },
    "GC.DOD.TOTL.GD.ZS": {
        "label": "Dette publique",
        "unit": "% du PIB",
        "unit_display": "% PIB",
        "scale": 1,
        "format": ".1f",
        "pilier": 3,
        "description": "Dette brute des administrations centrales (% du PIB)",
        "source": WB_SOURCE_LABEL,
        "source_url": WB_SOURCE_URL.format(code="GC.DOD.TOTL.GD.ZS"),
    },
    # ── Équilibres externes (pilier 4) ────────────────────────────────────────
    "BN.CAB.XOKA.GD.ZS": {
        "label": "Solde compte courant",
        "unit": "% du PIB",
        "unit_display": "% PIB",
        "scale": 1,
        "format": ".1f",
        "pilier": 4,
        "description": "Balance du compte courant (% du PIB)",
        "source": WB_SOURCE_LABEL,
        "source_url": WB_SOURCE_URL.format(code="BN.CAB.XOKA.GD.ZS"),
    },
    "BX.KLT.DINV.WD.GD.ZS": {
        "label": "IDE entrants",
        "unit": "% du PIB",
        "unit_display": "% PIB",
        "scale": 1,
        "format": ".1f",
        "pilier": 4,
        "description": "Flux d'investissements directs étrangers entrants (% du PIB)",
        "source": WB_SOURCE_LABEL,
        "source_url": WB_SOURCE_URL.format(code="BX.KLT.DINV.WD.GD.ZS"),
    },
}

# ── KPIs à afficher en tête de dashboard ─────────────────────────────────────
KPI_CODES = [
    "SP.POP.TOTL",
    "NY.GDP.MKTP.CD",
    "NY.GDP.PCAP.CD",
    "NY.GDP.MKTP.KD.ZG",
    "FP.CPI.TOTL.ZG",
    "SL.UEM.TOTL.ZS",
]

# ── Séries temporelles à tracer (Pilier 2) ───────────────────────────────────
CHART_SERIES = {
    "pib_croissance": {
        "title": "Croissance du PIB réel (%)",
        "description": "Taux de croissance annuel du PIB en volume",
        "codes": ["NY.GDP.MKTP.KD.ZG"],
        "type": "bar",
        "pilier": 2,
    },
    "pib_habitant": {
        "title": "PIB par habitant (USD courants)",
        "description": "Évolution sur 20 ans",
        "codes": ["NY.GDP.PCAP.CD"],
        "type": "line",
        "pilier": 2,
    },
    "inflation_chomage": {
        "title": "Inflation & Chômage (%)",
        "description": "Double indicateur de tension macroéconomique",
        "codes": ["FP.CPI.TOTL.ZG", "SL.UEM.TOTL.ZS"],
        "type": "line",
        "pilier": 3,
    },
    "population": {
        "title": "Population totale (millions)",
        "description": "Évolution démographique",
        "codes": ["SP.POP.TOTL"],
        "type": "area",
        "pilier": 1,
    },
}

# ── Couleurs Plotly cohérentes avec le HTML source ────────────────────────────
COLORS = {
    "blue": "#2563a8",
    "red": "#c0392b",
    "green": "#2e7d4f",
    "orange": "#c0620a",
    "gold": "#8b6914",
    "accent": "#1a3450",
    "teal": "#0e7490",
}

PILIER_META = {
    1: {"icon": "🏛", "label": "Cadre Socioéconomique & Politique",
        "description": "Population, développement humain, gouvernance, emploi"},
    2: {"icon": "📈", "label": "Modèle de Croissance",
        "description": "Structure du PIB, secteurs porteurs, dynamique de croissance"},
    3: {"icon": "💰", "label": "Finances Publiques",
        "description": "Solde budgétaire, dette, inflation, politique fiscale"},
    4: {"icon": "⚖️", "label": "Équilibres Externes",
        "description": "Balance courante, commerce extérieur, IDE"},
    5: {"icon": "🏦", "label": "Système Financier & Politique Monétaire",
        "description": "Secteur bancaire, inclusion financière, crédit privé"},
    6: {"icon": "🌿", "label": "Risques Climat & Nature",
        "description": "Vulnérabilité climatique, émissions CO₂, forêts, énergie"},
}

# ── Indicateurs Pilier 5 & 6 (ajoutés à INDICATORS) ─────────────────────────
INDICATORS_P5 = {
    "FD.AST.PRVT.GD.ZS": {
        "label": "Crédit privé / PIB",
        "unit": "% du PIB",
        "unit_display": "% PIB",
        "scale": 1, "format": ".1f", "pilier": 5,
        "description": "Crédit intérieur au secteur privé (% du PIB)",
        "source": WB_SOURCE_LABEL,
        "source_url": WB_SOURCE_URL.format(code="FD.AST.PRVT.GD.ZS"),
    },
    "FB.BNK.CAPA.ZS": {
        "label": "Ratio fonds propres bancaires",
        "unit": "% actifs pondérés",
        "unit_display": "%",
        "scale": 1, "format": ".1f", "pilier": 5,
        "description": "Ratio de fonds propres réglementaires sur actifs pondérés du risque",
        "source": WB_SOURCE_LABEL,
        "source_url": WB_SOURCE_URL.format(code="FB.BNK.CAPA.ZS"),
    },
    "FX.OWN.TOTL.ZS": {
        "label": "Inclusion financière — compte bancaire",
        "unit": "% adultes (15+)",
        "unit_display": "%",
        "scale": 1, "format": ".1f", "pilier": 5,
        "description": "Part des adultes (15+) possédant un compte dans une institution financière",
        "source": WB_SOURCE_LABEL,
        "source_url": WB_SOURCE_URL.format(code="FX.OWN.TOTL.ZS"),
    },
}

INDICATORS_P6 = {
    "EN.ATM.CO2E.PC": {
        "label": "Émissions CO₂ par habitant",
        "unit": "tonnes / habitant",
        "unit_display": "t CO₂/hab.",
        "scale": 1, "format": ".2f", "pilier": 6,
        "description": "Émissions de CO₂ par habitant (tonnes métriques)",
        "source": WB_SOURCE_LABEL,
        "source_url": WB_SOURCE_URL.format(code="EN.ATM.CO2E.PC"),
    },
    "AG.LND.FRST.ZS": {
        "label": "Couverture forestière",
        "unit": "% du territoire",
        "unit_display": "%",
        "scale": 1, "format": ".1f", "pilier": 6,
        "description": "Superficie des forêts en pourcentage du territoire total",
        "source": WB_SOURCE_LABEL,
        "source_url": WB_SOURCE_URL.format(code="AG.LND.FRST.ZS"),
    },
    "EG.ELC.RNEW.ZS": {
        "label": "Électricité renouvelable",
        "unit": "% de la production totale",
        "unit_display": "%",
        "scale": 1, "format": ".1f", "pilier": 6,
        "description": "Part des énergies renouvelables dans la production d'électricité",
        "source": WB_SOURCE_LABEL,
        "source_url": WB_SOURCE_URL.format(code="EG.ELC.RNEW.ZS"),
    },
    "ER.LND.PTLD.ZS": {
        "label": "Aires terrestres protégées",
        "unit": "% du territoire",
        "unit_display": "%",
        "scale": 1, "format": ".1f", "pilier": 6,
        "description": "Superficie des aires terrestres protégées (% du territoire total)",
        "source": WB_SOURCE_LABEL,
        "source_url": WB_SOURCE_URL.format(code="ER.LND.PTLD.ZS"),
    },
    "EN.ATM.CO2E.KT": {
        "label": "Émissions CO₂ totales",
        "unit": "kt CO₂",
        "unit_display": "kt",
        "scale": 1, "format": ",.0f", "pilier": 6,
        "description": "Émissions totales de CO₂ (kilotonnes)",
        "source": WB_SOURCE_LABEL,
        "source_url": WB_SOURCE_URL.format(code="EN.ATM.CO2E.KT"),
    },
}

# Fusionner dans INDICATORS
INDICATORS.update(INDICATORS_P5)
INDICATORS.update(INDICATORS_P6)
