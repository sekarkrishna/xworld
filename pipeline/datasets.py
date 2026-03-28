"""
Dataset Registry — centralised download and management for all XWorld datasets.

Scripts call ``ensure_dataset("name")`` instead of having inline download logic.
Custom datasets registered at runtime are persisted to the settings table and
reloaded on module import.
"""

from __future__ import annotations

import json
import logging
import tempfile
import urllib.request
import zipfile
from pathlib import Path

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent.parent
DATASET_DIR = ROOT / "datasets"

# ── Built-in registry ───────────────────────────────────────────────

REGISTRY: dict[str, dict] = {
    "ecg_fivedays": {
        "url": "https://timeseriesclassification.com/aeon-toolkit/ECGFiveDays.zip",
        "method": "urllib_zip",
        "files": ["ECGFiveDays_TRAIN.ts", "ECGFiveDays_TEST.ts"],
    },
    "covid_first_wave": {
        "url": "https://covid.ourworldindata.org/data/owid-covid-data.csv",
        "method": "direct_csv",
    },
    "sunspot_cycles": {
        "url": "https://www.sidc.be/SILSO/DATA/SN_m_tot_V2.0.csv",
        "method": "direct_csv",
    },
    "lynx_hare": {
        "url": "manual",
        "method": "bundled",
    },
    "keeling_co2": {
        "url": "https://scrippsco2.ucsd.edu/assets/data/atmospheric/stations/in_situ_co2/monthly/monthly_in_situ_co2_mlo.csv",
        "method": "direct_csv",
        "preprocessing": "split into keeling_seasonal and keeling_trend",
    },
    "temperature_giss": {
        "url": "https://data.giss.nasa.gov/gistemp/station_data_v4_globe/",
        "method": "nasa_giss",
    },
    "streamflow_usgs": {
        "url": "https://waterservices.usgs.gov/nwis/dv/",
        "method": "usgs_api",
        "preprocessing": "np.log1p() transform before feature extraction",
    },
}


# ── Download helpers ────────────────────────────────────────────────


def _download_zip(url: str, dest: Path) -> None:
    """Download a ZIP file, validate with zipfile.is_zipfile(), and extract."""
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
        tmp_path = Path(tmp.name)
    try:
        logger.info("Downloading ZIP from %s", url)
        urllib.request.urlretrieve(url, str(tmp_path))
        if not zipfile.is_zipfile(tmp_path):
            raise ValueError(f"Downloaded file is not a valid ZIP: {url}")
        with zipfile.ZipFile(tmp_path) as zf:
            zf.extractall(dest)
        logger.info("Extracted ZIP to %s", dest)
    finally:
        tmp_path.unlink(missing_ok=True)


def _download_csv(url: str, dest: Path) -> None:
    """Download a CSV file directly via urllib."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    logger.info("Downloading CSV from %s", url)
    urllib.request.urlretrieve(url, str(dest))
    logger.info("Saved CSV to %s", dest)


def _download_nasa_giss(url: str, dest: Path) -> None:
    """Placeholder for NASA GISS temperature data download."""
    raise NotImplementedError(
        f"NASA GISS download not yet implemented. "
        f"Manually place data in {dest} or implement the scraper."
    )


def _download_usgs(url: str, dest: Path) -> None:
    """Placeholder for USGS streamflow API download."""
    raise NotImplementedError(
        f"USGS API download not yet implemented. "
        f"Manually place data in {dest} or implement the API client."
    )


# ── Core API ────────────────────────────────────────────────────────


def ensure_dataset(name: str) -> Path:
    """Download dataset if not present. Returns path to dataset folder.

    Raises ``ValueError`` for unknown dataset names.
    """
    if name not in REGISTRY:
        raise ValueError(
            f"Unknown dataset: {name!r}. Known: {sorted(REGISTRY.keys())}"
        )

    entry = REGISTRY[name]
    dest = DATASET_DIR / name

    # Skip if already present with files
    if dest.exists() and any(dest.iterdir()):
        return dest

    dest.mkdir(parents=True, exist_ok=True)
    method = entry["method"]

    if method == "bundled":
        # Bundled datasets must already exist on disk
        if not any(dest.iterdir()):
            raise FileNotFoundError(
                f"Bundled dataset {name!r} not found at {dest}. "
                f"Ensure the CSV is placed in {dest}/ before use."
            )
        return dest
    elif method == "urllib_zip":
        _download_zip(entry["url"], dest)
    elif method == "direct_csv":
        _download_csv(entry["url"], dest / f"{name}.csv")
    elif method == "nasa_giss":
        _download_nasa_giss(entry["url"], dest)
    elif method == "usgs_api":
        _download_usgs(entry["url"], dest)
    else:
        raise ValueError(f"Unknown download method: {method!r}")

    return dest


def register_dataset(name: str, url: str, method: str, **kwargs) -> None:
    """Add a new dataset to the runtime registry and persist to settings table."""
    REGISTRY[name] = {"url": url, "method": method, **kwargs}

    # Persist to settings table for cross-session availability
    from pipeline.graph import get_setting, set_setting

    existing = json.loads(get_setting("custom_datasets", "{}"))
    existing[name] = REGISTRY[name]
    set_setting("custom_datasets", json.dumps(existing))
    logger.info("Registered custom dataset %r (method=%s)", name, method)


# ── Load custom datasets from settings on import ───────────────────


def _load_custom_datasets() -> None:
    """Load any custom datasets persisted in the settings table."""
    try:
        from pipeline.graph import get_setting

        raw = get_setting("custom_datasets", "{}")
        custom = json.loads(raw)
        for name, entry in custom.items():
            if name not in REGISTRY:
                REGISTRY[name] = entry
                logger.debug("Loaded custom dataset %r from settings", name)
    except Exception:
        # Don't fail module import if DB isn't initialised yet
        logger.debug("Could not load custom datasets from settings (DB may not exist yet)")


_load_custom_datasets()
