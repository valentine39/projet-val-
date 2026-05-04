# ── scrapers/climat_scraper.py ───────────────────────────────────────────────
# Scraper données climatiques spécialisées — entièrement dynamique (tout pays).
#
#  Source 1 — Climate Watch (CAIT)
#    API publique JSON, pas d'authentification requise.
#    Docs : https://www.climatewatchdata.org/api/v1/data/historical_emissions
#
#  Source 2 — ND-GAIN Country Index (Notre Dame University)
#    CSV téléchargeables publiquement sur GitHub officiel ND-GAIN.
#    Repo : https://github.com/GAIN-ND/ND-GAIN-Country-Index
#
#  Source 3 — IEA (International Energy Agency)
#    API publique partielle : https://api.iea.org/stats
#
# ─────────────────────────────────────────────────────────────────────────────

import io
import requests
import pandas as pd
from typing import Optional

TIMEOUT = 20
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/csv, */*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def _get_json(url: str, params: dict = None) -> Optional[any]:
    try:
        r = requests.get(url, params=params, headers=HEADERS, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


def _get_text(url: str, params: dict = None) -> Optional[str]:
    try:
        r = requests.get(url, params=params, headers=HEADERS, timeout=TIMEOUT)
        r.raise_for_status()
        return r.text
    except Exception:
        return None


# ═════════════════════════════════════════════════════════════════════════════
# SOURCE 1 — CLIMATE WATCH (CAIT GHG)
# ═════════════════════════════════════════════════════════════════════════════

_CW_BASE = "https://www.climatewatchdata.org/api/v1/data"

_CW_SECTOR_FR = {
    "Total excluding LUCF":        "Total GES (hors UTCATF)",
    "Total including LUCF":        "Total GES (avec UTCATF)",
    "Energy":                       "Énergie",
    "Agriculture":                  "Agriculture",
    "Land-Use Change and Forestry": "UTCATF",
    "Waste":                        "Déchets",
    "Industrial Processes":         "Procédés industriels",
    "Other Fuel Combustion":        "Autre combustion",
    "Fugitive Emissions":           "Émissions fugitives",
    "Transport":                    "Transport",
    "Electricity/Heat":             "Électricité/Chaleur",
    "Manufacturing/Construction":   "Industrie manufacturière",
    "Buildings":                    "Bâtiments",
}


def fetch_cw_emissions(iso3: str) -> dict:
    """
    Série temporelle d'émissions GES totales (CAIT, tous GES, avec UTCATF).
    """
    result = {
        "series": [], "value": None, "year": None,
        "unit": "MtCO₂eq",
        "source": "Climate Watch — CAIT GHG Emissions",
        "source_url": f"https://www.climatewatchdata.org/countries/{iso3}",
    }

    params = {
        "regions[]": iso3,
        "source_ids[]": 1,
        "gas_ids[]": 1,
        "start_year": 1990,
        "end_year": 2022,
    }
    data = _get_json(f"{_CW_BASE}/historical_emissions", params)

    records = []
    if isinstance(data, dict):
        records = data.get("data", [])
    elif isinstance(data, list):
        records = data

    best_series = []
    found_including = False

    for rec in records:
        if not isinstance(rec, dict):
            continue
        sector = rec.get("sector", {})
        sector_name = sector.get("name", "") if isinstance(sector, dict) else str(sector)

        is_including = "Total including LUCF" in sector_name
        is_excluding = "Total excluding LUCF" in sector_name
        if not is_including and not is_excluding:
            continue
        if found_including and not is_including:
            continue

        emissions = rec.get("emissions", {})
        if not emissions:
            continue

        series = []
        for yr_str, val in emissions.items():
            if str(yr_str).isdigit() and val is not None:
                try:
                    series.append({"year": int(yr_str), "value": float(val)})
                except (ValueError, TypeError):
                    pass

        series = sorted([s for s in series if s["value"] is not None], key=lambda x: x["year"])
        if series:
            best_series = series
            if is_including:
                found_including = True
                break

    if best_series:
        result["series"] = best_series
        result["value"] = best_series[-1]["value"]
        result["year"] = best_series[-1]["year"]

    return result


def fetch_cw_emissions_by_sector(iso3: str) -> list:
    """
    Émissions par secteur (dernière année disponible) — pour graphique donut.
    """
    params = {
        "regions[]": iso3,
        "source_ids[]": 1,
        "gas_ids[]": 1,
        "start_year": 2015,
        "end_year": 2022,
    }
    data = _get_json(f"{_CW_BASE}/historical_emissions", params)
    records = []
    if isinstance(data, dict):
        records = data.get("data", [])
    elif isinstance(data, list):
        records = data

    sectors = {}
    for rec in records:
        if not isinstance(rec, dict):
            continue
        sector = rec.get("sector", {})
        name = sector.get("name", "") if isinstance(sector, dict) else str(sector)
        if not name or "Total" in name:
            continue
        emissions = rec.get("emissions", {})
        if not emissions:
            continue
        valid = {}
        for k, v in emissions.items():
            if str(k).isdigit() and v is not None:
                try:
                    valid[int(k)] = float(v)
                except (ValueError, TypeError):
                    pass
        if valid:
            yr = max(valid.keys())
            sectors[name] = {"value": valid[yr], "year": yr}

    result = [
        {"sector": _CW_SECTOR_FR.get(k, k), "value": round(v["value"], 3), "year": v["year"]}
        for k, v in sectors.items()
        if v["value"] > 0
    ]
    return sorted(result, key=lambda x: x["value"], reverse=True)


def fetch_cw_ndc(iso3: str) -> dict:
    """
    Engagements NDC depuis Climate Watch.
    """
    result = {
        "unconditional_target": None,
        "conditional_target": None,
        "has_ndc": False,
        "source": "Climate Watch — NDC Tracker",
        "source_url": f"https://www.climatewatchdata.org/ndc-tracker/{iso3.lower()}",
    }

    data = _get_json(
        "https://www.climatewatchdata.org/api/v1/ndcs",
        params={"countries[]": iso3},
    )
    if not data:
        data = _get_json(f"{_CW_BASE}/ndc_texts", params={"countries[]": iso3})

    if not data:
        return result

    records = data if isinstance(data, list) else data.get("data", [])
    if records:
        result["has_ndc"] = True

    for rec in records[:5]:
        if not isinstance(rec, dict):
            continue
        for key, val in rec.items():
            if not val or not isinstance(val, str):
                continue
            kl = key.lower()
            if "unconditional" in kl and result["unconditional_target"] is None:
                result["unconditional_target"] = val[:300]
            elif "conditional" in kl and result["conditional_target"] is None:
                result["conditional_target"] = val[:300]

    return result


# ═════════════════════════════════════════════════════════════════════════════
# SOURCE 2 — ND-GAIN COUNTRY INDEX
# CSVs publics sur GitHub officiel : github.com/GAIN-ND/ND-GAIN-Country-Index
# ═════════════════════════════════════════════════════════════════════════════

_NDGAIN_RAW = "https://raw.githubusercontent.com/GAIN-ND/ND-GAIN-Country-Index/master/src"

_NDGAIN_VULN_FILES = {
    "food":      "Alimentation",
    "water":     "Eau",
    "health":    "Santé",
    "ecosystem": "Écosystèmes",
    "human":     "Habitat humain",
    "infrastruc": "Infrastructure",
}
_NDGAIN_READ_FILES = {
    "economic":   "Économique",
    "governance": "Gouvernance",
    "social":     "Social",
}


def _load_ndgain_csv(path: str) -> Optional[pd.DataFrame]:
    text = _get_text(f"{_NDGAIN_RAW}/{path}")
    if not text:
        return None
    try:
        return pd.read_csv(io.StringIO(text))
    except Exception:
        return None


def _ndgain_id_col(df: pd.DataFrame) -> Optional[str]:
    for c in df.columns:
        if c.strip().upper() in ("ISO3", "ISO", "CODE", "COUNTRY ISO3", "ISO_3"):
            return c
        if "iso" in c.lower() and "3" in c.lower():
            return c
    return None


def _ndgain_series(df: Optional[pd.DataFrame], iso3: str) -> list:
    if df is None or df.empty:
        return []
    id_col = _ndgain_id_col(df)
    if not id_col:
        return []
    row = df[df[id_col].str.upper() == iso3.upper()]
    if row.empty:
        return []
    row = row.iloc[0]
    series = []
    for col in df.columns:
        col_s = str(col).strip()
        if col_s.isdigit() and 1990 <= int(col_s) <= 2030:
            try:
                val = float(row[col])
                if pd.notna(val):
                    series.append({"year": int(col_s), "value": round(val, 4)})
            except (ValueError, TypeError):
                pass
    return sorted(series, key=lambda x: x["year"])


def fetch_ndgain(iso3: str) -> dict:
    """
    Score ND-GAIN complet pour n'importe quel pays (ISO-3).
    """
    result = {
        "score": None, "vulnerability": None, "readiness": None,
        "rank": None, "_total": 185, "year": None,
        "series_overall": [],
        "series_vulnerability": [],
        "series_readiness": [],
        "vulnerability_components": {},
        "readiness_components": {},
        "source": "ND-GAIN Country Index — Notre Dame University",
        "source_url": f"https://gain-new.crc.nd.edu/country/{iso3.lower()}",
    }

    # Score global
    df_gain = _load_ndgain_csv("gain/gain.csv")
    series_gain = _ndgain_series(df_gain, iso3)
    if series_gain:
        result["series_overall"] = series_gain
        latest = series_gain[-1]
        result["score"] = latest["value"]
        result["year"] = latest["year"]
        # Calcul du rang
        if df_gain is not None:
            id_col = _ndgain_id_col(df_gain)
            yr_col = str(latest["year"])
            if id_col and yr_col in df_gain.columns:
                try:
                    all_vals = pd.to_numeric(df_gain[yr_col], errors="coerce")
                    result["rank"] = int((all_vals > latest["value"]).sum()) + 1
                    result["_total"] = int(all_vals.notna().sum())
                except Exception:
                    pass

    # Vulnérabilité
    df_vuln = _load_ndgain_csv("vulnerability/vulnerability.csv")
    sv = _ndgain_series(df_vuln, iso3)
    if sv:
        result["series_vulnerability"] = sv
        result["vulnerability"] = sv[-1]["value"]

    # Readiness
    df_read = _load_ndgain_csv("readiness/readiness.csv")
    sr = _ndgain_series(df_read, iso3)
    if sr:
        result["series_readiness"] = sr
        result["readiness"] = sr[-1]["value"]

    # Sous-scores vulnérabilité
    vuln_comp = {}
    for fkey, label in _NDGAIN_VULN_FILES.items():
        df_sub = _load_ndgain_csv(f"vulnerability/{fkey}.csv")
        sub = _ndgain_series(df_sub, iso3)
        if sub:
            vuln_comp[label] = sub[-1]["value"]
    if vuln_comp:
        result["vulnerability_components"] = vuln_comp

    # Sous-scores readiness
    read_comp = {}
    for fkey, label in _NDGAIN_READ_FILES.items():
        df_sub = _load_ndgain_csv(f"readiness/{fkey}.csv")
        sub = _ndgain_series(df_sub, iso3)
        if sub:
            read_comp[label] = sub[-1]["value"]
    if read_comp:
        result["readiness_components"] = read_comp

    return result


# ═════════════════════════════════════════════════════════════════════════════
# SOURCE 3 — IEA (International Energy Agency)
# ═════════════════════════════════════════════════════════════════════════════

_IEA_BASE = "https://api.iea.org/stats"

# Correspondance ISO-3 → code IEA (généralement ISO-2)
_ISO3_TO_IEA = {
    "TLS": "TL", "FRA": "FR", "DEU": "DE", "GBR": "GB", "USA": "US",
    "CHN": "CN", "JPN": "JP", "IND": "IN", "BRA": "BR", "RUS": "RU",
    "KOR": "KR", "AUS": "AU", "CAN": "CA", "ESP": "ES", "ITA": "IT",
    "MEX": "MX", "IDN": "ID", "NLD": "NL", "SAU": "SA", "TUR": "TR",
    "ZAF": "ZA", "ARG": "AR", "POL": "PL", "BEL": "BE", "SWE": "SE",
    "NOR": "NO", "DNK": "DK", "FIN": "FI", "PRT": "PT", "GRC": "GR",
    "CZE": "CZ", "ROU": "RO", "HUN": "HU", "ARE": "AE", "MYS": "MY",
    "THA": "TH", "VNM": "VN", "PHL": "PH", "COL": "CO", "CHL": "CL",
    "EGY": "EG", "NGA": "NG", "KEN": "KE", "MAR": "MA", "ETH": "ET",
    "GHA": "GH", "COM": "KM", "MUS": "MU", "MDG": "MG", "SEN": "SN",
    "KHM": "KH", "MMR": "MM", "BGD": "BD", "PAK": "PK", "LKA": "LK",
    "MNG": "MN", "KAZ": "KZ", "UZB": "UZ", "AZE": "AZ", "GEO": "GE",
    "ALB": "AL", "MNE": "ME", "SRB": "RS", "HRV": "HR", "BGR": "BG",
    "SVK": "SK", "SVN": "SI", "LTU": "LT", "LVA": "LV", "EST": "EE",
    "ISL": "IS", "IRL": "IE", "LUX": "LU", "AUT": "AT", "CHE": "CH",
    "UKR": "UA", "BLR": "BY", "MDA": "MD", "MKD": "MK",
}


def _to_iea_code(iso3: str) -> str:
    return _ISO3_TO_IEA.get(iso3.upper(), iso3[:2].upper())


def _iea_series(indicator: str, iea_code: str) -> list:
    data = _get_json(f"{_IEA_BASE}/indicator/{indicator}", params={"country": iea_code})
    if not data:
        return []
    records = data if isinstance(data, list) else data.get("data", data.get("value", []))
    if not isinstance(records, list):
        return []
    series = []
    for rec in records:
        if not isinstance(rec, dict):
            continue
        yr = rec.get("year") or rec.get("Year") or rec.get("TIME_PERIOD")
        val = rec.get("value") or rec.get("Value") or rec.get("OBS_VALUE")
        if yr is not None and val is not None:
            try:
                series.append({"year": int(yr), "value": float(val)})
            except (ValueError, TypeError):
                pass
    return sorted(series, key=lambda x: x["year"])


def _iea_electricity_mix(iea_code: str) -> dict:
    """Mix de production électrique depuis l'API IEA."""
    for indicator in ("ELECGEN", "ELEC", "ELECPROD"):
        data = _get_json(f"{_IEA_BASE}/indicator/{indicator}", params={"country": iea_code})
        if not data:
            continue
        records = data if isinstance(data, list) else data.get("data", data.get("value", []))
        if not isinstance(records, list) or not records:
            continue
        # Grouper par source, dernière année
        by_year = {}
        for rec in records:
            if not isinstance(rec, dict):
                continue
            try:
                yr = int(rec.get("year") or rec.get("Year") or 0)
                val = float(rec.get("value") or rec.get("Value") or 0)
            except (ValueError, TypeError):
                continue
            source = (
                rec.get("product") or rec.get("Product") or
                rec.get("source") or rec.get("Source") or "Autre"
            )
            if yr not in by_year:
                by_year[yr] = {}
            existing = by_year[yr].get(str(source), 0)
            by_year[yr][str(source)] = existing + val

        if by_year:
            latest_yr = max(by_year.keys())
            raw = by_year[latest_yr]
            total = sum(raw.values())
            if total > 0:
                return {k: round(v / total * 100, 1) for k, v in raw.items() if v > 0}
    return {}


def fetch_iea(iso3: str) -> dict:
    """
    Données IEA pour n'importe quel pays (ISO-3).
    """
    iea_code = _to_iea_code(iso3)

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
        "source_url": f"https://www.iea.org/countries/{iso3.lower()}",
    }

    # CO₂ énergie
    sc = _iea_series("CO2", iea_code)
    if sc:
        result["series_co2_energy"] = sc
        result["co2_energy_mt"] = sc[-1]["value"]
        result["year"] = sc[-1]["year"]

    # Part renouvelables
    sr = _iea_series("RENEWSHARE", iea_code)
    if not sr:
        sr = _iea_series("RENEWPCT", iea_code)
    if sr:
        result["series_renewable"] = sr
        result["renewable_share"] = sr[-1]["value"]
        if result["year"] is None:
            result["year"] = sr[-1]["year"]

    # Approvisionnement total
    st = _iea_series("TPES", iea_code)
    if st:
        result["total_supply_mtoe"] = st[-1]["value"]

    # Accès électricité
    sa = _iea_series("ELECACC", iea_code)
    if sa:
        result["electricity_access"] = sa[-1]["value"]

    # Mix électrique
    mix = _iea_electricity_mix(iea_code)
    if mix:
        result["mix_electricity"] = mix

    return result
