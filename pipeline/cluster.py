"""
pipeline/cluster.py
UMAP + HDBSCAN clustering — refactored from notebooks 05, 09.
Settled parameters from DECISIONS.md.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


# Settled parameters (see DECISIONS.md)
UMAP_PARAMS = dict(n_neighbors=15, min_dist=0.1, n_components=2, random_state=42)
HDBSCAN_PARAMS = dict(min_cluster_size=8, min_samples=3, metric="euclidean")

FEATURE_COLS = ["skewness", "kurtosis", "lag1_autocorr", "zero_crossings", "slope"]


def run_clustering(
    features_df: pd.DataFrame,
    umap_params: dict | None = None,
    hdbscan_params: dict | None = None,
) -> pd.DataFrame:
    """
    Run UMAP + HDBSCAN on a features DataFrame.
    Expects columns: skewness, kurtosis, lag1_autocorr, zero_crossings, slope.
    Returns the input DataFrame with added columns: umap_x, umap_y, cluster.
    """
    from umap import UMAP
    from hdbscan import HDBSCAN
    from sklearn.preprocessing import StandardScaler

    up = umap_params or UMAP_PARAMS
    hp = hdbscan_params or HDBSCAN_PARAMS

    X = features_df[FEATURE_COLS].values
    X_scaled = StandardScaler().fit_transform(X)

    embedding = UMAP(**up).fit_transform(X_scaled)
    labels = HDBSCAN(**hp).fit_predict(X_scaled)

    result = features_df.copy()
    result["umap_x"] = embedding[:, 0]
    result["umap_y"] = embedding[:, 1]
    result["cluster"] = labels
    return result


def cluster_profiles(clustered_df: pd.DataFrame) -> pd.DataFrame:
    """Mean feature values per cluster (excluding noise)."""
    df = clustered_df[clustered_df["cluster"] != -1]
    return df.groupby("cluster")[FEATURE_COLS].mean().round(3)


def majority_cluster(series_df: pd.DataFrame, skip_noise: bool = True) -> int:
    """Most common cluster label in a subset, optionally skipping noise (-1)."""
    counts = series_df["cluster"].value_counts()
    if skip_noise and -1 in counts.index:
        counts = counts.drop(-1)
    if counts.empty:
        return -1
    return int(counts.idxmax())
