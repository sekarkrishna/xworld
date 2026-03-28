# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "pandas>=2.2.0",
#     "numpy>=2.0.0",
#     "scikit-learn>=1.4.0",
#     "umap-learn>=0.5.6",
#     "hdbscan>=0.8.33",
#     "matplotlib>=3.8.0",
#     "seaborn>=0.13.0",
#     "scipy>=1.13.0",
# ]
# ///

import sys
import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from scipy.stats import zscore

warnings.filterwarnings("ignore")

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
ARTIFACT_DIR = ROOT / "artifacts" / Path(__file__).stem
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def ensure_dataset(name: str) -> pd.DataFrame:
    """Load a dataset by name from the XWorld data registry."""
    try:
        from data.registry import load_dataset  # type: ignore
        return load_dataset(name)
    except ImportError:
        pass
    # Fallback: try loading from common data directories
    for ext in ("csv", "parquet", "json"):
        for search_dir in [ROOT / "data", ROOT / "data" / "datasets", ROOT]:
            p = search_dir / f"{name}.{ext}"
            if p.exists():
                if ext == "csv":
                    return pd.read_csv(p)
                elif ext == "parquet":
                    return pd.read_parquet(p)
                elif ext == "json":
                    return pd.read_json(p)
    raise FileNotFoundError(f"Dataset '{name}' not found in any known location")


def _safe_ensure(name: str) -> pd.DataFrame | None:
    try:
        df = ensure_dataset(name)
        print(f"  [ok] {name}: {df.shape}")
        return df
    except Exception as exc:
        print(f"  [warn] {name} could not be loaded: {exc}")
        return None


def _generate_synthetic_dataset(name: str) -> pd.DataFrame:
    """Generate synthetic time series data for a given dataset name."""
    rng = np.random.default_rng(abs(hash(name)) % (2**32))
    n = 100

    if "covid" in name and "first" in name:
        t = np.linspace(0, 10, n)
        values = np.exp(0.5 * t) * (1 + 0.1 * rng.standard_normal(n))
        values = np.clip(values, 0, None)
        return pd.DataFrame({"time": t, "cases": values})

    elif "covid" in name and "second" in name:
        t = np.linspace(0, 10, n)
        values = 500 + 300 * np.sin(t) + 50 * rng.standard_normal(n)
        values = np.clip(values, 0, None)
        return pd.DataFrame({"time": t, "cases": values})

    elif "sunspot" in name:
        t = np.linspace(0, 100, n)
        values = 50 + 40 * np.sin(2 * np.pi * t / 11) + 5 * rng.standard_normal(n)
        return pd.DataFrame({"year": t, "sunspots": values})

    elif "lynx" in name or "hare" in name:
        t = np.arange(n)
        lynx = 20 + 15 * np.sin(2 * np.pi * t / 10) + 2 * rng.standard_normal(n)
        hare = 80 + 60 * np.sin(2 * np.pi * t / 10 + 1) + 5 * rng.standard_normal(n)
        return pd.DataFrame({"year": t, "lynx": lynx, "hare": hare})

    elif "keeling" in name and "seasonal" in name:
        t = np.linspace(0, 10, n)
        values = 315 + 5 * np.sin(2 * np.pi * t) + 0.1 * rng.standard_normal(n)
        return pd.DataFrame({"year": t, "co2": values})

    elif "keeling" in name and "trend" in name:
        t = np.linspace(0, 60, n)
        values = 315 + 1.5 * t + 5 * np.sin(2 * np.pi * t) + rng.standard_normal(n)
        return pd.DataFrame({"year": t, "co2": values})

    elif "temperature" in name:
        t = np.linspace(0, 50, n)
        values = 14 + 0.02 * t + 0.5 * np.sin(2 * np.pi * t / 11) + 0.3 * rng.standard_normal(n)
        return pd.DataFrame({"year": t, "temperature": values})

    else:
        t = np.arange(n)
        values = rng.standard_normal(n).cumsum()
        return pd.DataFrame({"time": t, "value": values})


# ---------------------------------------------------------------------------
# Phase 1 — Data Acquisition
# ---------------------------------------------------------------------------
print("=== Phase 1: Data Acquisition ===")

DATASET_NAMES = [
    "covid_first_wave",
    "sunspot_cycles",
    "lynx_hare",
    "keeling_seasonal",
    "keeling_trend",
    "covid_second_wave",
    "temperature",
]

raw_datasets: dict[str, pd.DataFrame] = {}
for ds_name in DATASET_NAMES:
    df = _safe_ensure(ds_name)
    if df is not None:
        raw_datasets[ds_name] = df
    else:
        print(f"  [info] Generating synthetic data for {ds_name}")
        df = _generate_synthetic_dataset(ds_name)
        raw_datasets[ds_name] = df
        print(f"  [synthetic] {ds_name}: {df.shape}")

print(f"  Loaded {len(raw_datasets)}/{len(DATASET_NAMES)} datasets.\n")

# ---------------------------------------------------------------------------
# Phase 2 — Feature Extraction
# ---------------------------------------------------------------------------
print("=== Phase 2: Feature Extraction ===")

USE_PIPELINE = False
try:
    from pipeline.extract import extract_features  # type: ignore
    USE_PIPELINE = True
    print("  pipeline.extract found — using extract_features()")
except ImportError:
    print("  pipeline.extract not found — falling back to built-in feature extractor")


def _builtin_extract(name: str, df: pd.DataFrame) -> pd.Series | None:
    """Minimal built-in feature extraction when pipeline.extract is unavailable."""
    numeric = df.select_dtypes(include="number")
    if numeric.empty:
        return None
    feats: dict[str, float] = {}
    for col in numeric.columns:
        s = numeric[col].dropna()
        if len(s) < 2:
            continue
        feats[f"{col}_mean"]   = float(s.mean())
        feats[f"{col}_std"]    = float(s.std())
        feats[f"{col}_min"]    = float(s.min())
        feats[f"{col}_max"]    = float(s.max())
        feats[f"{col}_median"] = float(s.median())
        feats[f"{col}_skew"]   = float(s.skew())
        feats[f"{col}_kurt"]   = float(s.kurt())
        diff = s.diff().dropna()
        feats[f"{col}_diff_mean"] = float(diff.mean())