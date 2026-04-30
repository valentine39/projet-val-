import pandas as pd

def build_summary_table(data: dict) -> pd.DataFrame:
    rows = []

    for key, df in data.items():
        meta = CONFIG.INDICATORS[key]

        if df is None or df.empty:
            rows.append({
                "Indicateur": meta["label"],
                "Valeur": "N/D",
                "Année": "N/D",
                "Unité": meta["unit"],
                "Source": meta["source"],
                "Lien": meta["url"],
            })
        else:
            last = df.iloc[-1]
            rows.append({
                "Indicateur": meta["label"],
                "Valeur": last["valeur"],
                "Année": int(last["année"]),
                "Unité": meta["unit"],
                "Source": meta["source"],
                "Lien": meta["url"],
            })

    return pd.DataFrame(rows)
