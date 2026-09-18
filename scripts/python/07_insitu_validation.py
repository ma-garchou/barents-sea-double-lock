"""Step 7 - In-situ validation against the 15 % ice threshold (thesis §4.2, Graph 2, workflow Part III).

The in-situ archives are not redistributed here (see data/README.md). This
script documents the processing applied to them:

  Nansen Legacy   station database, 2017-2021, stations NLEG01-NLEG12
                  -> geolocate, keep the 75-80°N frontier band (21,876 station-day records)
  ASSIST IceWatch shipborne visual observations, 2021
                  -> skip the metadata header, rescale total concentration
                     from tenths (0-10) to percent (0-100)

Thesis results (Nansen Legacy, 75-80°N, 2017-2021)
  57.1 % of records below 15 % sea-ice concentration
  54.6 % of records with no ice at all (0 %)
  83.8 % below 15 % in the June-September window

Column names differ between archive versions, so adjust the COLS mapping if needed.
Usage:  python scripts/python/07_insitu_validation.py
"""
import sys

import pandas as pd

import config as C

COLS = {
    "nansen": {"lat": "Latitude", "lon": "Longitude", "date": "Date", "sic": "SIC"},  # SIC in %
    "icewatch": {"lat": "LAT", "lon": "LON", "date": "Date", "tc": "TC"},  # TC = total concentration (tenths)
}


def nansen():
    if not C.RAW_NANSEN.exists():
        print(f"skip: {C.RAW_NANSEN.name} not found")
        return None
    c = COLS["nansen"]
    df = pd.read_csv(C.RAW_NANSEN)
    df = df.dropna(subset=[c["lat"], c["lon"]])
    band = df[(df[c["lat"]] >= 75) & (df[c["lat"]] <= 80)].copy()
    print(f"Nansen Legacy: {len(df):,} geolocated records, {len(band):,} in the 75-80°N band")
    if c["sic"] in band.columns:
        sic = pd.to_numeric(band[c["sic"]], errors="coerce")
        month = pd.to_datetime(band[c["date"]], errors="coerce").dt.month
        summer = month.between(6, 9)
        print(f"   below 15 %            : {100 * (sic < C.SIC_EXTENT_THRESHOLD).mean():.1f} %")
        print(f"   ice-free (0 %)        : {100 * (sic == 0).mean():.1f} %")
        print(f"   below 15 %, Jun-Sep   : {100 * (sic[summer] < C.SIC_EXTENT_THRESHOLD).mean():.1f} %")
    return band


def icewatch():
    if not C.RAW_ICEWATCH.exists():
        print(f"skip: {C.RAW_ICEWATCH.name} not found")
        return None
    c = COLS["icewatch"]
    # IceWatch exports start with free-text metadata lines: find the header row
    with open(C.RAW_ICEWATCH, encoding="utf-8", errors="ignore") as fh:
        skip = next(i for i, line in enumerate(fh) if line.startswith(c["date"]) or f",{c['lat']}," in line)
    df = pd.read_csv(C.RAW_ICEWATCH, skiprows=skip)
    df["sic_pct"] = pd.to_numeric(df[c["tc"]], errors="coerce") * 10.0
    edge = df[(df["sic_pct"] >= 10) & (df["sic_pct"] <= 20)]
    print(f"IceWatch 2021: {len(df):,} observations, {len(edge):,} reported at 10-20 % concentration (edge zone)")
    return df


if __name__ == "__main__":
    a, b = nansen(), icewatch()
    if a is None and b is None:
        sys.exit("No in-situ files found in data/raw/.")
