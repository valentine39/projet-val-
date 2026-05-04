j'ai ce scrapper qui marche bien pour le timor leste. Comment je peux l'étendre à tous les pays : # ── scrapers/climat_scraper.py ───────────────────────────────────────────────
# Scraper pour les données climatiques spécialisées :
#   - Climate Watch (CAIT) → émissions GES par secteur / gaz
#   - ND-GAIN Index        → scores vulnérabilité & adaptation
#   - IEA                  → mix énergétique, intensité carbone
#
# Ces sources ne disposent pas d'API JSON non-authentifiée fiable ;
# on utilise donc requests + BeautifulSoup avec plusieurs stratégies
# (HTML parsing, endpoints JSON embarqués, fallback CDN).
#
# Toutes les méthodes retournent un dict avec :
#   { "value": float|str|None, "year": int|None,
#     "label": str, "source": str, "source_url": str }
# ─────────────────────────────────────────────────────────────────────────────

import re
import json
import requests
from typing import Optional

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


def _get(url: str, params: dict = None, json_mode: bool = False) -> Optional[dict | str]:
    try:
        r = requests.get(url, params=params, headers=HEADERS, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json() if json_mode else r.text
    except Exception:
        return None


# ─────────────────────────────────────────────────────────────────────────────
# CLIMATE WATCH — CAIT GHG Emissions API
# Docs : https://www.climatewatchdata.org/api/v1/data/historical_emissions
# ─────────────────────────────────────────────────────────────────────────────

CW_BASE = "https://www.climatewatchdata.org/api/v1/data"
CW_SOURCE_URL = "https://www.climatewatchdata.org/countries/TLS"

# Mapping secteur CAIT → label FR
CW_SECTOR_LABELS = {
    "Total excluding LUCF": "Total GES (hors UTCATF)",
    "Total including LUCF": "Total GES (avec UTCATF)",
    "Energy": "Énergie",
    "Agriculture": "Agriculture",
    "Land-Use Change and Forestry": "Utilisation des terres (UTCATF)",
    "Waste": "Déchets",
    "Industrial Processes": "Procédés industriels",
}

# Mapping gaz CAIT
CW_GAS_LABELS = {
    "All GHG": "Tous GES (MtCO₂eq)",
    "CO2": "CO₂ (MtCO₂)",
    "CH4": "CH₄ (MtCO₂eq)",
    "N2O": "N₂O (MtCO₂eq)",
}


def fetch_cw_emissions(
    iso3: str = "TLS",
    sector: str = "Total including LUCF",
    gas: str = "All GHG",
) -> dict:
    """
    Récupère les émissions GES historiques depuis l'API Climate Watch (CAIT).
    Retourne la dernière valeur connue + la série complète.
    """
    result = {
        "label": f"Émissions GES — {CW_SECTOR_LABELS.get(sector, sector)} ({CW_GAS_LABELS.get(gas, gas)})",
        "value": None,
        "year": None,
        "series": [],
        "unit": "MtCO₂eq",
        "source": "Climate Watch — CAIT GHG Emissions",
        "source_url": CW_SOURCE_URL,
    }

    try:
        data = _get(
            f"{CW_BASE}/historical_emissions",
            params={
                "regions[]": iso3,
                "source_ids[]": 1,       # CAIT
                "gas_ids[]": 1 if gas == "All GHG" else 2,
                "sector_ids[]": None,
            },
            json_mode=True,
        )

        # Fallback : endpoint alternatif avec paramètres nommés
        if not data:
            data = _get(
                f"{CW_BASE}/historical_emissions",
                params={
                    "regions": iso3,
                    "source": "CAIT",
                    "gas": gas,
                    "sector": sector,
                    "start_year": 1990,
                    "end_year": 2022,
                },
                json_mode=True,
            )

        if not data:
            return result

        # Parser la réponse (structure : {"data": [{"emissions": {year: value, ...}}]})
        records = data if isinstance(data, list) else data.get("data", [])
        for record in records:
            if not isinstance(record, dict):
                continue

            emissions = record.get("emissions", {})
            if not emissions:
                continue

            series = []
            for yr_str, val in emissions.items():
                try:
                    series.append({
                        "year": int(yr_str),
                        "value": float(val) if val is not None else None,
                    })
                except (ValueError, TypeError):
                    continue

            series = sorted(
                [s for s in series if s["value"] is not None],
                key=lambda x: x["year"],
            )
            if series:
                result["series"] = series
                latest = series[-1]
                result["value"] = latest["value"]
                result["year"] = latest["year"]
                break

    except Exception:
        pass

    return result


def fetch_cw_emissions_by_sector(iso3: str = "TLS") -> list:
    """
    Récupère les émissions par secteur (dernière année disponible).
    Utile pour un graphique en donut.
    """
    try:
        data = _get(
            f"{CW_BASE}/historical_emissions",
            params={
                "regions": iso3,
                "source": "CAIT",
                "gas": "All GHG",
                "start_year": 2018,
                "end_year": 2022,
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

            # Garder uniquement les secteurs principaux (pas "Total")
            if "Total" in sector_name or not sector_name:
                continue

            emissions = record.get("emissions", {})
            if not emissions:
                continue

            # Prendre la valeur la plus récente
            valid = {int(k): v for k, v in emissions.items() if v is not None}
            if valid:
                latest_yr = max(valid.keys())
                sectors[sector_name] = {"value": valid[latest_yr], "year": latest_yr}

        return [
            {
                "sector": CW_SECTOR_LABELS.get(k, k),
                "value": v["value"],
                "year": v["year"],
            }
            for k, v in sectors.items()
            if v["value"] > 0
        ]

    except Exception:
        return []


def fetch_cw_ndc(iso3: str = "TLS") -> dict:
    """
    Récupère les engagements NDC (Nationally Determined Contributions)
    depuis Climate Watch.
    """
    result = {
        "unconditional_target": None,
        "conditional_target": None,
        "base_year": None,
        "net_zero_year": None,
        "source": "Climate Watch — NDC Tracker",
        "source_url": f"https://www.climatewatchdata.org/ndc-tracker/{iso3.lower()}",
    }

    try:
        data = _get(
            f"{CW_BASE}/ndc_texts",
            params={"countries[]": iso3},
            json_mode=True,
        )

        # Endpoint alternatif
        if not data:
            data = _get(
                "https://www.climatewatchdata.org/api/v1/ndcs",
                params={"countries[]": iso3, "source": "NDC"},
                json_mode=True,
            )

        if data:
            records = data if isinstance(data, list) else data.get("data", [])
            for rec in records[:3]:
                if not isinstance(rec, dict):
                    continue
                for key, val in rec.items():
                    skey = str(key).lower()
                    if "unconditional" in skey and result["unconditional_target"] is None:
                        result["unconditional_target"] = str(val)[:200] if val else None
                    elif "conditional" in skey and result["conditional_target"] is None:
                        result["conditional_target"] = str(val)[:200] if val else None

    except Exception:
        pass

    return result


# ─────────────────────────────────────────────────────────────────────────────
# ND-GAIN — Notre Dame Global Adaptation Initiative
# https://gain.nd.edu/our-work/country-index/
# ─────────────────────────────────────────────────────────────────────────────

NDGAIN_SOURCE_URL = "https://gain-new.crc.nd.edu/country/timor-leste"

# Données ND-GAIN brutes pour Timor-Leste (série historique 1995–2021)
# Source : Notre Dame Global Adaptation Initiative — données publiques téléchargeables
# https://gain.nd.edu/our-work/country-index/download-data/
NDGAIN_TLS_STATIC = {
    "overall": [
        (1995, 29.9), (1996, 30.1), (1997, 30.0), (1998, 29.5), (1999, 29.3),
        (2000, 30.5), (2001, 31.2), (2002, 32.1), (2003, 33.0), (2004, 33.8),
        (2005, 34.5), (2006, 35.2), (2007, 35.8), (2008, 36.4), (2009, 36.9),
        (2010, 37.3), (2011, 37.8), (2012, 38.2), (2013, 38.6), (2014, 38.9),
        (2015, 39.2), (2016, 39.4), (2017, 39.6), (2018, 39.8), (2019, 40.0),
        (2020, 40.1), (2021, 40.3),
    ],
    "vulnerability": [
        (1995, 0.612), (1998, 0.608), (2000, 0.598), (2005, 0.579),
        (2010, 0.560), (2015, 0.530), (2018, 0.510), (2020, 0.498), (2021, 0.493),
    ],
    "readiness": [
        (1995, 0.148), (2000, 0.162), (2005, 0.188), (2010, 0.215),
        (2015, 0.245), (2018, 0.268), (2020, 0.278), (2021, 0.283),
    ],
    # Sous-scores vulnérabilité (2021)
    "vulnerability_components": {
        "Alimentation": 0.68,
        "Eau": 0.72,
        "Santé": 0.61,
        "Écosystèmes": 0.59,
        "Habitat humain": 0.55,
        "Infrastructure": 0.63,
    },
    # Sous-scores readiness (2021)
    "readiness_components": {
        "Économique": 0.21,
        "Gouvernance": 0.31,
        "Social": 0.38,
    },
    "rank_2021": 140,
    "total_countries": 185,
    "source_note": "ND-GAIN Country Index — Notre Dame University (2021)",
}


def fetch_ndgain(iso3: str = "TLS") -> dict:
    """
    Récupère le score ND-GAIN. Tente l'API publique, sinon utilise
    les données statiques pour Timor-Leste (TLS).
    """
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
        "source_url": NDGAIN_SOURCE_URL,
    }

    try:
        raw = _get(
            f"https://gain-new.crc.nd.edu/api/countries/{iso3.lower()}",
            json_mode=True,
        )

        if raw and isinstance(raw, dict):
            result["score"]         = raw.get("gain_score") or raw.get("overall")
            result["vulnerability"] = raw.get("vulnerability")
            result["readiness"]     = raw.get("readiness")
            result["rank"]          = raw.get("rank")
            result["year"]          = raw.get("year", 2021)
        else:
            # Fallback données statiques TLS uniquement
            if iso3.upper() == "TLS":
                static = NDGAIN_TLS_STATIC
                if static["overall"]:
                    last = static["overall"][-1]
                    result["score"] = last[1]
                    result["year"]  = last[0]
                if static["vulnerability"]:
                    result["vulnerability"] = static["vulnerability"][-1][1]
                if static["readiness"]:
                    result["readiness"] = static["readiness"][-1][1]
                result["rank"] = static["rank_2021"]
                result["series_overall"] = [
                    {"year": y, "value": v} for y, v in static["overall"]
                ]
                result["series_vulnerability"] = [
                    {"year": y, "value": v} for y, v in static["vulnerability"]
                ]
                result["series_readiness"] = [
                    {"year": y, "value": v} for y, v in static["readiness"]
                ]
                result["vulnerability_components"] = static["vulnerability_components"]
                result["readiness_components"]     = static["readiness_components"]
                result["source"] = static["source_note"]

    except Exception:
        pass

    return result


# ─────────────────────────────────────────────────────────────────────────────
# IEA — International Energy Agency
# API ouverte : https://api.iea.org/stats/
# ─────────────────────────────────────────────────────────────────────────────

IEA_BASE = "https://api.iea.org/stats"
IEA_SOURCE_URL = "https://www.iea.org/countries/timor-leste"

# Données IEA statiques pour Timor-Leste (2022)
# Source : IEA World Energy Balances — données publiques résumées
IEA_TLS_STATIC = {
    "mix_electricity_2022": {
        "Pétrole/Diesel": 84.5,
        "Solaire PV": 9.8,
        "Hydroélectricité": 3.9,
        "Bioénergie": 1.4,
        "Autre": 0.4,
    },
    "total_energy_supply_2022_mtoe": 0.49,
    "co2_energy_2022_mt": 0.62,
    "co2_per_gdp_2022": None,
    "electricity_access_pct": 82.0,
    "renewable_share_2022": 15.5,
    "energy_intensity": None,
    "series_renewable": [
        (2010, 4.2),  (2012, 5.8),  (2014, 7.2),  (2016, 9.0),
        (2018, 11.5), (2019, 12.8), (2020, 13.9), (2021, 14.6), (2022, 15.5),
    ],
    "series_co2_energy": [
        (2010, 0.28), (2012, 0.35), (2014, 0.44), (2016, 0.50),
        (2018, 0.55), (2019, 0.57), (2020, 0.54), (2021, 0.59), (2022, 0.62),
    ],
    "source_note": "IEA World Energy Balances 2023 — Timor-Leste",
}

# ── Table de correspondance ISO3 → ISO2 ──────────────────────────────────────
# Évite de tronquer aveuglément cc[:2] ce qui donne des codes incorrects
# (ex : "DEU"[:2] = "DE" ✓ mais "NLD"[:2] = "NL" ✓ vs "NZL"[:2] = "NZ" ✓,
#  en revanche "PRK"[:2] = "PR" ✗ au lieu de "KP")
ISO3_TO_ISO2 = {
    # Asie-Pacifique
    "TLS": "TL", "CHN": "CN", "JPN": "JP", "KOR": "KR", "PRK": "KP",
    "IND": "IN", "PAK": "PK", "BGD": "BD", "LKA": "LK", "NPL": "NP",
    "AFG": "AF", "MMR": "MM", "THA": "TH", "VNM": "VN", "KHM": "KH",
    "LAO": "LA", "MYS": "MY", "SGP": "SG", "IDN": "ID", "PHL": "PH",
    "TWN": "TW", "HKG": "HK", "MAC": "MO", "MNG": "MN", "KAZ": "KZ",
    "UZB": "UZ", "TKM": "TM", "KGZ": "KG", "TJK": "TJ", "AZE": "AZ",
    "ARM": "AM", "GEO": "GE",
    # Océanie
    "AUS": "AU", "NZL": "NZ", "PNG": "PG", "FJI": "FJ", "SLB": "SB",
    "VUT": "VU", "WSM": "WS", "TON": "TO", "KIR": "KI", "FSM": "FM",
    "PLW": "PW", "MHL": "MH", "NRU": "NR", "TUV": "TV",
    # Europe
    "FRA": "FR", "DEU": "DE", "GBR": "GB", "ITA": "IT", "ESP": "ES",
    "PRT": "PT", "NLD": "NL", "BEL": "BE", "CHE": "CH", "AUT": "AT",
    "SWE": "SE", "NOR": "NO", "DNK": "DK", "FIN": "FI", "ISL": "IS",
    "IRL": "IE", "LUX": "LU", "MLT": "MT", "CYP": "CY", "GRC": "GR",
    "POL": "PL", "CZE": "CZ", "SVK": "SK", "HUN": "HU", "ROU": "RO",
    "BGR": "BG", "HRV": "HR", "SVN": "SI", "EST": "EE", "LVA": "LV",
    "LTU": "LT", "UKR": "UA", "BLR": "BY", "MDA": "MD", "RUS": "RU",
    "SRB": "RS", "BIH": "BA", "MNE": "ME", "MKD": "MK", "ALB": "AL",
    "XKX": "XK", "AND": "AD", "MCO": "MC", "SMR": "SM", "LIE": "LI",
    "VAT": "VA",
    # Amériques
    "USA": "US", "CAN": "CA", "MEX": "MX", "BRA": "BR", "ARG": "AR",
    "COL": "CO", "VEN": "VE", "PER": "PE", "CHL": "CL", "ECU": "EC",
    "BOL": "BO", "PRY": "PY", "URY": "UY", "GUY": "GY", "SUR": "SR",
    "TTO": "TT", "JAM": "JM", "HTI": "HT", "DOM": "DO", "CUB": "CU",
    "PRI": "PR", "GTM": "GT", "HND": "HN", "SLV": "SV", "NIC": "NI",
    "CRI": "CR", "PAN": "PA", "BLZ": "BZ",
    # Moyen-Orient & Afrique du Nord
    "SAU": "SA", "IRN": "IR", "IRQ": "IQ", "ARE": "AE", "QAT": "QA",
    "KWT": "KW", "BHR": "BH", "OMN": "OM", "YEM": "YE", "JOR": "JO",
    "LBN": "LB", "SYR": "SY", "ISR": "IL", "PSE": "PS", "TUR": "TR",
    "MAR": "MA", "DZA": "DZ", "TUN": "TN", "LBY": "LY", "EGY": "EG",
    # Afrique subsaharienne
    "NGA": "NG", "ZAF": "ZA", "ETH": "ET", "COD": "CD", "TZA": "TZ",
    "KEN": "KE", "GHA": "GH", "MOZ": "MZ", "MDG": "MG", "CMR": "CM",
    "CIV": "CI", "NER": "NE", "MLI": "ML", "BFA": "BF", "SEN": "SN",
    "TCD": "TD", "GIN": "GN", "RWA": "RW", "BEN": "BJ", "SOM": "SO",
    "ZMB": "ZM", "ZWE": "ZW", "MWI": "MW", "UGA": "UG", "AGO": "AO",
    "SDN": "SD", "SSD": "SS", "CAF": "CF", "COG": "CG", "GAB": "GA",
    "GNB": "GW", "GNQ": "GQ", "SLE": "SL", "LBR": "LR", "MRT": "MR",
    "GMB": "GM", "CPV": "CV", "STP": "ST", "COM": "KM", "DJI": "DJ",
    "ERI": "ER", "LSO": "LS", "SWZ": "SZ", "BWA": "BW", "NAM": "NA",
    "MUS": "MU", "SYC": "SC", "SWZ": "SZ",
}


def _iso3_to_iso2(iso3: str) -> str:
    """
    Convertit un code ISO3 en ISO2.
    Utilise la table de correspondance, fallback sur les 2 premiers caractères.
    """
    return ISO3_TO_ISO2.get(iso3.upper(), iso3[:2].upper())


def fetch_iea(country_iso2: str = "TL", iso3: str = "TLS") -> dict:
    """
    Récupère les données IEA pour un pays.
    - Tente l'API publique IEA (endpoint non-authentifié)
    - Si échec et pays = TLS → données statiques embarquées
    - Sinon → retourne un résultat vide sans lever d'exception
    """
    result = {
        "mix_electricity": {},
        "renewable_share": None,
        "co2_energy_mt": None,
        "total_supply_mtoe": None,
        "electricity_access": None,
        "series_renewable": [],
        "series_co2_energy": [],
        "year": 2022,
        "source": "IEA — World Energy Balances",
        "source_url": IEA_SOURCE_URL,
    }

    try:
        # Tentative API IEA (endpoint public non-authentifié)
        api_data = _get(
            f"{IEA_BASE}/indicator/CO2",
            params={"country": country_iso2},
            json_mode=True,
        )

        if api_data and isinstance(api_data, (list, dict)):
            records = api_data if isinstance(api_data, list) else api_data.get("data", [])
            series = []
            for rec in records:
                if isinstance(rec, dict):
                    yr  = rec.get("year")  or rec.get("Year")
                    val = rec.get("value") or rec.get("Value")
                    if yr and val:
                        try:
                            series.append({"year": int(yr), "value": float(val)})
                        except (ValueError, TypeError):
                            continue
            if series:
                series.sort(key=lambda x: x["year"])
                result["series_co2_energy"] = series
                result["co2_energy_mt"]     = series[-1]["value"]
                result["year"]              = series[-1]["year"]
                return result

        # Fallback données statiques — Timor-Leste uniquement
        if iso3.upper() == "TLS":
            static = IEA_TLS_STATIC
            result["mix_electricity"]   = static["mix_electricity_2022"]
            result["renewable_share"]   = static["renewable_share_2022"]
            result["co2_energy_mt"]     = static["co2_energy_2022_mt"]
            result["total_supply_mtoe"] = static["total_energy_supply_2022_mtoe"]
            result["electricity_access"] = static["electricity_access_pct"]
            result["series_renewable"]  = [
                {"year": y, "value": v} for y, v in static["series_renewable"]
            ]
            result["series_co2_energy"] = [
                {"year": y, "value": v} for y, v in static["series_co2_energy"]
            ]
            result["source"] = static["source_note"]

    except Exception:
        # Ne jamais laisser une exception remonter depuis un scraper
        pass

    return result
