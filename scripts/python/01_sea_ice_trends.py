"""Step 1 - Sea-ice trends (thesis Figure 2 and the March SIC check in §6).

(a) Barents Sea March maximum vs September minimum extent, 2000-2024, with OLS
    trends, from the NSIDC Sea Ice Index v3 regional monthly workbook.
    Thesis result: March -0.16 Mkm²/decade, September -0.07 Mkm²/decade.

(b) Mean March sea-ice concentration over the study frame, 1990-2024, from the
    daily NOAA OISST v2.1 'ice' band exported from Google Earth Engine
    (scripts/gee/03_march_sic_timeseries.js -> data/processed/tables/).
    Thesis result: slope not significant (p = 0.51, R² = 0.01).

Usage:  python scripts/python/01_sea_ice_trends.py
"""
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

import config as C


def march_sic_trend():
    df = pd.read_csv(C.TAB / "oisst_march_sic_daily_1990_2024.csv", parse_dates=["date"])
    annual = df.groupby(df["date"].dt.year)["sic_mean_pct"].mean()
    fit = stats.linregress(annual.index, annual.values)
    print("(b) OISST March SIC over the study frame, 1990-2024")
    print(f"    slope = {fit.slope * 10:+.2f} % per decade | p = {fit.pvalue:.2f} | R² = {fit.rvalue ** 2:.2f}")
    return annual, fit


def load_nsidc_barents():
    """Return a DataFrame indexed by year with 'march' and 'september' extent in million km²."""
    csv_fallback = C.RAW / "nsidc_barents_monthly.csv"  # optional: columns year,march,september (Mkm²)
    if csv_fallback.exists():
        return pd.read_csv(csv_fallback, index_col="year")
    if not C.RAW_NSIDC_REGIONAL.exists():
        return None
    xls = pd.ExcelFile(C.RAW_NSIDC_REGIONAL)
    sheet = next(s for s in xls.sheet_names if s.lower().startswith("barents") and "extent" in s.lower())
    raw = xls.parse(sheet)
    raw = raw.rename(columns={raw.columns[0]: "year"}).dropna(subset=["year"])
    raw["year"] = raw["year"].astype(int)
    cols = {c.lower(): c for c in raw.columns if isinstance(c, str)}
    out = pd.DataFrame({
        "march": pd.to_numeric(raw[cols["march"]], errors="coerce"),
        "september": pd.to_numeric(raw[cols["september"]], errors="coerce"),
    })
    out.index = raw["year"]
    if out["march"].max() > 100:  # workbook is in km²
        out = out / 1e6
    return out


def extent_trends(ext):
    ext = ext.loc[2000:2024]
    fig, ax = plt.subplots(figsize=(11, 7))
    styles = {"march": ("#1f4e79", "o", "March (winter maximum)"),
              "september": ("#b03a2e", "s", "September (summer minimum)")}
    print("(a) NSIDC Barents Sea extent, 2000-2024")
    for col, (colour, marker, label) in styles.items():
        fit = stats.linregress(ext.index, ext[col])
        print(f"    {col:<9} trend = {fit.slope * 10:+.2f} Mkm²/decade (p = {fit.pvalue:.3f})")
        ax.plot(ext.index, ext[col], marker=marker, color=colour, lw=2, label=label)
        ax.plot(ext.index, fit.intercept + fit.slope * ext.index, "--", color=colour,
                label=f"{label.split(' ')[0]} trend: {fit.slope * 10:+.2f} Mkm²/decade")
    ax.set(xlabel="Year", ylabel="Sea-ice extent (million km²)", ylim=(0, 1.05),
           title="Barents Sea ice extent, March maximum vs September minimum (2000-2024)")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.text(0.01, 0.01, "Data: NSIDC Sea Ice Index v3.0 (Barents sector). OLS trends.", fontsize=8)
    fig.savefig(C.OUT / "fig02_barents_ice_extent_trends.png", dpi=200, bbox_inches="tight")
    print(f"    figure -> {C.OUT / 'fig02_barents_ice_extent_trends.png'}")


if __name__ == "__main__":
    march_sic_trend()
    ext = load_nsidc_barents()
    if ext is None:
        sys.exit("(a) skipped: download the NSIDC regional monthly workbook into data/raw/ (see data/README.md)")
    extent_trends(ext)
