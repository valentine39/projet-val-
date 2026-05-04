# ── scrapers/climat_scraper.py ───────────────────────────────────────────────
# Scraper climat multi-pays
#
# Sources :
#   - Climate Watch / CAIT : émissions GES, secteurs, NDC
#   - ND-GAIN             : vulnérabilité / readiness climatique
#   - IEA                 : données énergie quand accessibles
#
# Principe :
#   - Toutes les fonctions prennent un code ISO3 : TLS, FRA, IDN, ZAF, etc.
#   - Aucune donnée Timor-Leste n'est utilisée pour les autres pays.
#   - Si une source échoue, on retourne un objet vide mais stable.
# ─────────────────────────────────────────────────────────────────────────────

import requests
from typing import Optional, Any

TIMEOUT = 20

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/json,*/*;q=0.8",
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
}


# ─────────────────────────────────────────────────────────────────────────────
# OUTILS GÉNÉRIQUES
# ─────────────────────────────────────────────────────────────────────────────

def _get(
    url: str,
    params: Optional[dict] = None,
    json_mode: bool = False,
) -> Optional[Any]:
    """
    Requête GET robuste.
    Retourne None si la source ne répond pas ou si le format est invalide.
    """
    try:
        response = requests.get(
            url,
            params=params,
            headers=HEADERS,
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        return response.json() if json_mode else response.text
    except Exception:
        return None


ISO3_TO_ISO2 = {
    "TLS": "TL", "FRA": "FR", "DEU": "DE", "GBR": "GB", "USA": "US",
    "CHN": "CN", "JPN": "JP", "KOR": "KR", "PRK": "KP", "IND": "IN",
    "IDN": "ID", "VNM": "VN", "THA": "TH", "PHL": "PH", "MYS": "MY",
    "SGP": "SG", "KHM": "KH", "LAO": "LA", "MMR": "MM",

    "AUS": "AU", "NZL": "NZ", "PNG": "PG", "FJI": "FJ",

    "ITA": "IT", "ESP": "ES", "PRT": "PT", "NLD": "NL", "BEL": "BE",
    "CHE": "CH", "AUT": "AT", "SWE": "SE", "NOR": "NO", "DNK": "DK",
    "FIN": "FI", "IRL": "IE", "POL": "PL", "CZE": "CZ", "SVK": "SK",
    "HUN": "HU", "ROU": "RO", "BGR": "BG", "GRC": "GR", "UKR": "UA",
    "RUS": "RU",

    "CAN": "CA", "MEX": "MX", "BRA": "BR", "ARG": "AR", "COL": "CO",
    "PER": "PE", "CHL": "CL", "ECU": "EC", "BOL": "BO", "URY": "UY",
    "PRY": "PY", "VEN": "VE",

    "MAR": "MA", "DZA": "DZ", "TUN": "TN", "EGY": "EG", "TUR": "TR",
    "SAU": "SA", "ARE": "AE", "QAT": "QA", "KWT": "KW", "IRN": "IR",
    "IRQ": "IQ", "ISR": "IL", "JOR": "JO", "LBN": "LB",

    "ZAF": "ZA", "NGA": "NG", "ETH": "ET", "KEN": "KE", "GHA": "GH",
    "SEN": "SN", "CIV": "CI", "CMR": "CM", "COD": "CD", "COG": "CG",
    "GAB": "GA", "AGO": "AO", "MOZ": "MZ", "TZA": "TZ", "UGA": "UG",
    "RWA": "RW", "MDG": "MG", "MLI": "ML", "NER": "NE", "BFA": "BF",
    "BEN": "BJ", "TGO": "TG", "GIN": "GN", "GNB": "GW", "LBR": "LR",
    "SLE": "SL", "MRT": "MR", "COM": "KM", "DJI": "DJ", "ZMB": "ZM",
    "ZWE": "ZW", "MWI": "MW", "NAM": "NA", "BWA": "BW", "MUS": "MU",
    "SYC": "SC",
}


def _iso3_to_iso2(iso3: str) -> str:
    """
    Convertit ISO3 → ISO2.
    Important pour éviter les erreurs du type PRK → PR au lieu de KP.
    """
    if not iso3:
        return ""
    iso3 = iso3.upper()
    return ISO3_TO_ISO2.get(iso3, iso3[:2])


# ─────────────────────────────────────────────────────────────────────────────
# CLIMATE WATCH — CAIT
# ─────────────────────────────────────────────────────────────────────────────

CW_BASE = "https://www.climatewatchdata.org/api/v1/data"

CW_SECTOR_LABELS = {
    "Total excluding LUCF": "Total GES (hors UTCATF)",
    "Total including LUCF": "Total GES (avec UTCATF)",
    "Energy": "Énergie",
    "Agriculture": "Agriculture",
    "Land-Use Change and Forestry": "Utilisation des terres (UTCATF)",
    "Waste": "Déchets",
    "Industrial Processes": "Procédés industriels",
}

CW_GAS_LABELS = {
    "All GHG": "Tous GES",
    "CO2": "CO₂",
    "CH4": "CH₄",
    "N2O": "N₂O",
}


def fetch_cw_emissions(
    iso3: str = "TLS",
    sector: str = "Total including LUCF",
    gas: str = "All GHG",
) -> dict:
    """
    Récupère la série historique d'émissions GES depuis Climate Watch / CAIT.
    Retourne la dernière valeur disponible + la série complète.
    """

    iso3 = iso3.upper()

    result = {
        "label": (
            f"Émissions GES — "
            f"{CW_SECTOR_LABELS.get(sector, sector)} "
            f"({CW_GAS_LABELS.get(gas, gas)})"
        ),
        "value": None,
        "year": None,
        "series": [],
        "unit": "MtCO₂eq",
        "source": "Climate Watch — CAIT GHG Emissions",
        "source_url": f"https://www.climatewatchdata.org/countries/{iso3}",
    }

    data = _get(
        f"{CW_BASE}/historical_emissions",
        params={
            "regions": iso3,
            "source": "CAIT",
            "gas": gas,
            "sector": sector,
            "start_year": 1990,
            "end_year": 2023,
        },
        json_mode=True,
    )

    if not data:
        data = _get(
            f"{CW_BASE}/historical_emissions",
            params={
                "regions[]": iso3,
                "source_ids[]": 1,
                "gas_ids[]": 1,
            },
            json_mode=True,
        )

    if not data:
        return result

    records = data if isinstance(data, list) else data.get("data", [])

    for record in records:
        if not isinstance(record, dict):
            continue

        record_sector = record.get("sector", {})
        if isinstance(record_sector, dict):
            record_sector = record_sector.get("name", "")

        record_gas = record.get("gas", {})
        if isinstance(record_gas, dict):
            record_gas = record_gas.get("name", "")

        if sector and record_sector and record_sector != sector:
            continue

        if gas and record_gas and record_gas != gas:
            continue

        emissions = record.get("emissions", {})
        if not isinstance(emissions, dict):
            continue

        series = []
        for year_str, value in emissions.items():
            try:
                if value is not None:
                    series.append({
                        "year": int(year_str),
                        "value": float(value),
                    })
            except Exception:
                continue

        series = sorted(series, key=lambda x: x["year"])

        if series:
            result["series"] = series
            result["value"] = series[-1]["value"]
            result["year"] = series[-1]["year"]
            return result

    return result


def fetch_cw_emissions_by_sector(iso3: str = "TLS") -> list[dict]:
    """
    Récupère les émissions par secteur pour la dernière année disponible.
    Sert à construire un graphique de répartition sectorielle.
    """

    iso3 = iso3.upper()

    data = _get(
        f"{CW_BASE}/historical_emissions",
        params={
            "regions": iso3,
            "source": "CAIT",
            "gas": "All GHG",
            "start_year": 2018,
            "end_year": 2023,
        },
        json_mode=True,
    )

    if not data:
        return []

    records = data if isinstance(data, list) else data.get("data", [])
    sectors = {}

    for record in records:
        if not isinstance(record, dict):
            continue

        sector_obj = record.get("sector", {})
        sector_name = (
            sector_obj.get("name", "")
            if isinstance(sector_obj, dict)
            else str(sector_obj)
        )

        if not sector_name or "Total" in sector_name:
            continue

        emissions = record.get("emissions", {})
        if not isinstance(emissions, dict):
            continue

        valid_values = {}
        for year_str, value in emissions.items():
            try:
                if value is not None:
                    valid_values[int(year_str)] = float(value)
            except Exception:
                continue

        if valid_values:
            latest_year = max(valid_values)
            latest_value = valid_values[latest_year]

            if latest_value > 0:
                sectors[sector_name] = {
                    "value": latest_value,
                    "year": latest_year,
                }

    return [
        {
            "sector": CW_SECTOR_LABELS.get(sector_name, sector_name),
            "value": item["value"],
            "year": item["year"],
        }
        for sector_name, item in sectors.items()
    ]


def fetch_cw_ndc(iso3: str = "TLS") -> dict:
    """
    Récupère les informations NDC depuis Climate Watch quand disponibles.
    """

    iso3 = iso3.upper()

    result = {
        "unconditional_target": None,
        "conditional_target": None,
        "base_year": None,
        "net_zero_year": None,
        "source": "Climate Watch — NDC Tracker",
        "source_url": f"https://www.climatewatchdata.org/ndc-tracker/{iso3.lower()}",
    }

    data = _get(
        f"{CW_BASE}/ndc_texts",
        params={"countries[]": iso3},
        json_mode=True,
    )

    if not data:
        data = _get(
            "https://www.climatewatchdata.org/api/v1/ndcs",
            params={"countries[]": iso3, "source": "NDC"},
            json_mode=True,
        )

    if not data:
        return result

    records = data if isinstance(data, list) else data.get("data", [])

    for record in records:
        if not isinstance(record, dict):
            continue

        for key, value in record.items():
            key_lower = str(key).lower()

            if value in [None, "", []]:
                continue

            value_str = str(value)[:250]

            if (
                "unconditional" in key_lower
                and result["unconditional_target"] is None
            ):
                result["unconditional_target"] = value_str

            elif (
                "conditional" in key_lower
                and "unconditional" not in key_lower
                and result["conditional_target"] is None
            ):
                result["conditional_target"] = value_str

            elif "base" in key_lower and "year" in key_lower:
                result["base_year"] = value_str

            elif "net" in key_lower and "zero" in key_lower:
                result["net_zero_year"] = value_str

    return result


# ─────────────────────────────────────────────────────────────────────────────
# ND-GAIN
# ─────────────────────────────────────────────────────────────────────────────

def fetch_ndgain(iso3: str = "TLS") -> dict:
    """
    Récupère le score ND-GAIN quand l'endpoint répond.
    Si l'endpoint ne répond pas, retourne un résultat vide.
    """

    iso3 = iso3.upper()

    result = {
        "score": None,
        "vulnerability": None,
        "readiness": None,
        "rank": None,
        "year": None,
        "series_overall": [],
        "series_vulnerability": [],
        "series_readiness": [],
        "vulnerability_components": {},
        "readiness_components": {},
        "source": "ND-GAIN Country Index — Notre Dame University",
        "source_url": f"https://gain-new.crc.nd.edu/country/{iso3.lower()}",
    }

    raw = _get(
        f"https://gain-new.crc.nd.edu/api/countries/{iso3.lower()}",
        json_mode=True,
    )

    if not raw or not isinstance(raw, dict):
        return result

    result["score"] = (
        raw.get("gain_score")
        or raw.get("overall")
        or raw.get("score")
    )
    result["vulnerability"] = raw.get("vulnerability")
    result["readiness"] = raw.get("readiness")
    result["rank"] = raw.get("rank")
    result["year"] = raw.get("year")

    series = raw.get("series") or raw.get("data") or []

    if isinstance(series, list):
        for item in series:
            if not isinstance(item, dict):
                continue

            year = item.get("year")
            try:
                year = int(year)
            except Exception:
                continue

            if item.get("gain_score") is not None:
                result["series_overall"].append({
                    "year": year,
                    "value": float(item["gain_score"]),
                })

            if item.get("vulnerability") is not None:
                result["series_vulnerability"].append({
                    "year": year,
                    "value": float(item["vulnerability"]),
                })

            if item.get("readiness") is not None:
                result["series_readiness"].append({
                    "year": year,
                    "value": float(item["readiness"]),
                })

    result["series_overall"].sort(key=lambda x: x["year"])
    result["series_vulnerability"].sort(key=lambda x: x["year"])
    result["series_readiness"].sort(key=lambda x: x["year"])

    return result


# ─────────────────────────────────────────────────────────────────────────────
# IEA
# ─────────────────────────────────────────────────────────────────────────────

IEA_BASE = "https://api.iea.org/stats"


def fetch_iea(
    country_iso2: Optional[str] = None,
    iso3: str = "TLS",
) -> dict:
    """
    Récupère les données énergie IEA quand l'API publique répond.
    Pour les pays non couverts ou si l'API change, retourne un résultat vide.
    """

    iso3 = iso3.upper()
    country_iso2 = country_iso2 or _iso3_to_iso2(iso3)

    result = {
        "mix_electricity": {},
        "renewable_share": None,
        "co2_energy_mt": None,
        "total_supply_mtoe": None,
        "electricity_access": None,
        "series_renewable": [],
        "series_co2_energy": [],
        "year": None,
        "source": "IEA — World Energy Balances",
        "source_url": f"https://www.iea.org/countries/{country_iso2.lower()}",
    }

    co2_data = _get(
        f"{IEA_BASE}/indicator/CO2",
        params={"country": country_iso2},
        json_mode=True,
    )

    if not co2_data:
        return result

    records = co2_data if isinstance(co2_data, list) else co2_data.get("data", [])

    series = []

    for record in records:
        if not isinstance(record, dict):
            continue

        year = record.get("year") or record.get("Year")
        value = record.get("value") or record.get("Value")

        try:
            if year is not None and value is not None:
                series.append({
                    "year": int(year),
                    "value": float(value),
                })
        except Exception:
            continue

    series.sort(key=lambda x: x["year"])

    if series:
        result["series_co2_energy"] = series
        result["co2_energy_mt"] = series[-1]["value"]
        result["year"] = series[-1]["year"]

    return result


# ─────────────────────────────────────────────────────────────────────────────
# AGRÉGATEUR OPTIONNEL
# ─────────────────────────────────────────────────────────────────────────────

def fetch_all_climate_data(iso3: str = "TLS") -> dict:
    """
    Fonction pratique : récupère toutes les données climat pour un pays.
    Tu peux l'utiliser directement dans Streamlit.
    """

    iso3 = iso3.upper()
    iso2 = _iso3_to_iso2(iso3)

    return {
        "ndgain": fetch_ndgain(iso3),
        "iea": fetch_iea(iso2, iso3),
        "cw_total": fetch_cw_emissions(iso3),
        "cw_sectors": fetch_cw_emissions_by_sector(iso3),
        "cw_ndc": fetch_cw_ndc(iso3),
    }
