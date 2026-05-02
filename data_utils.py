"""
Dataset caching utility for XWorld notebooks.

Resolution order for each dataset:
  1. Local  — notebooks/data/<filename>          (fastest, works offline)
  2. GitHub — raw.githubusercontent.com/.../data/<filename>  (after first commit)
  3. Origin — original source URL                (fallback, may timeout)

Usage in notebooks:
    import sys; sys.path.insert(0, '..')
    from data_utils import get_dataset

    raw = get_dataset('co2_mm_mlo.csv', fetch_co2)   # fetch_co2 returns bytes
    df  = pd.read_csv(io.BytesIO(raw), ...)
"""

from pathlib import Path
import requests

DATA_DIR   = Path(__file__).parent / 'data'
GITHUB_RAW = 'https://raw.githubusercontent.com/sekarkrishna/xworld/main/notebooks/data'


def get_dataset(filename: str, download_fn) -> bytes:
    """Return raw bytes for dataset, caching locally on first fetch."""
    local = DATA_DIR / filename

    if local.exists():
        return local.read_bytes()

    # Try GitHub (works once the file has been committed)
    try:
        r = requests.get(f'{GITHUB_RAW}/{filename}', timeout=15)
        if r.status_code == 200 and len(r.content) > 100:
            DATA_DIR.mkdir(exist_ok=True)
            local.write_bytes(r.content)
            print(f'  [{filename}] fetched from GitHub')
            return r.content
    except Exception:
        pass

    # Download from original source
    content = download_fn()
    DATA_DIR.mkdir(exist_ok=True)
    local.write_bytes(content)
    print(f'  [{filename}] downloaded from origin, saved locally')
    return content
