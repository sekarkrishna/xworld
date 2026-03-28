"""
pipeline/extract.py
Feature extraction for time series — refactored from notebooks 01-09.
5 features per series after z-score normalisation.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats


def zscore(series: np.ndarray) -> np.ndarray:
    s = np.array(series, dtype=float)
    mu, sigma = s.mean(), s.std()
    if sigma == 0:
        return np.zeros_like(s)
    return (s - mu) / sigma


def extract_features(series: np.ndarray) -> dict:
    """
    Extract 5 shape features from a z-score normalised time series.
    Input does NOT need to be pre-normalised — this function normalises first.
    """
    s = zscore(np.array(series, dtype=float))

    skewness = float(stats.skew(s))
    kurtosis = float(stats.kurtosis(s))  # excess kurtosis (Fisher)

    if len(s) > 1:
        lag1 = float(np.corrcoef(s[:-1], s[1:])[0, 1])
    else:
        lag1 = 0.0

    mean_val = s.mean()
    zero_crossings = float(np.sum(np.diff(np.sign(s - mean_val)) != 0) / len(s))

    if len(s) > 1:
        x = np.arange(len(s))
        slope, *_ = np.polyfit(x, s, 1)
        slope = float(slope)
    else:
        slope = 0.0

    return {
        "skewness": skewness,
        "kurtosis": kurtosis,
        "lag1_autocorr": lag1,
        "zero_crossings": zero_crossings,
        "slope": slope,
    }


def extract_features_df(df: pd.DataFrame, id_col: str, value_col: str) -> pd.DataFrame:
    """
    Extract features for each unique series in a long-format DataFrame.
    id_col identifies the series, value_col is the measurement.
    """
    records = []
    for series_id, group in df.groupby(id_col):
        values = group[value_col].dropna().values
        if len(values) < 5:
            continue
        feats = extract_features(values)
        feats[id_col] = series_id
        records.append(feats)
    return pd.DataFrame(records)
