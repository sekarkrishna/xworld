# XWorld — Settled Decisions

Methodological choices that have been made and why. Update here when a decision is revisited.

---

## What XWorld is

A cross-domain time series shape clustering experiment. The central hypothesis: series from completely unrelated domains (epidemiology, astronomy, ecology, climate, cardiology) share underlying dynamic shapes that are mathematically similar — and that this similarity is detectable and clusters across domain boundaries.

Inspired by the philosophical question explored in `random_chats_x_world.txt`: does a glacier melting and a turtle breathing share the same numerical signature? Can you read the nature of a system from the shape of its ripple?

---

## Feature representation

**Decision:** 5 features extracted per time series after z-score normalisation.

| Feature | What it captures |
|---|---|
| `skewness` | Asymmetry of the distribution |
| `kurtosis` | Tail heaviness / peakedness |
| `lag1_autocorr` | Short-term memory, periodicity proxy |
| `zero_crossings` | Oscillation frequency |
| `slope` | Directional drift (linear trend) |

**Why these:** They separate the three main shape families we care about — directional bursts (high slope, low zero_crossings), oscillatory (high zero_crossings, low slope), and slow drifts (moderate slope, high autocorr). Kept deliberately minimal to avoid overfitting to specific domains.

---

## Normalisation

**Decision:** Z-score normalise each series before feature extraction.

**Why:** We are comparing shape, not magnitude. A COVID wave in India and Norway have very different case counts but the same dynamic shape. Normalising removes amplitude so only the temporal pattern remains.

---

## Keeling CO2 treated as two datasets

**Decision:** Decompose Keeling into `keeling_seasonal` and `keeling_trend`.

**Why:** The raw series contains two genuinely different dynamics superimposed — a ~1ppm seasonal oscillation and a long-run rising trend. They have different shapes and should be allowed to cluster differently.

---

## Clustering: UMAP + HDBSCAN

**Decision:** UMAP for dimensionality reduction, HDBSCAN for density clustering.

**Why UMAP over PCA:** Preserves local structure — series that are close in feature space stay close in the embedding. PCA optimises for global variance which can compress meaningful local shape differences.

**Why HDBSCAN over k-means:** Number of shape clusters is unknown a priori. HDBSCAN finds clusters of arbitrary shape and handles noise explicitly (label `-1`).

**Current parameters (as of 2026-03-24):**
- UMAP: `n_neighbors=15, min_dist=0.1, n_components=2, random_state=42`
- HDBSCAN: `min_cluster_size=8, min_samples=3, metric='euclidean'`

**Parameter history:**
- `min_cluster_size=3` → 76 micro-clusters, 31% noise, COVID majority was noise. Too fragmented.
- `min_cluster_size=15` → cleaner macro clusters, but temperature (26 points) physically cannot form a cluster and goes 100% noise.
- `min_cluster_size=8` → allows small but cohesive datasets (≥8 points) to form their own cluster.

---

## Observed shape taxonomy (empirical, as of 2026-03-28)

Six shape classes from 5-feature clustering, refined by 6-feature analysis:

| Shape class | Datasets | Primary discriminators |
|---|---|---|
| Right-skewed burst (with residue) | covid_first_wave, covid_second_wave | skewness≈0.95, lag1≈0.95, zc≈0.02, baseline_delta≈+0.4–0.6 |
| Permanent accumulation | keeling_trend | baseline_delta=3.1, lag1=1.0, skewness≈0, slope>>0 — most isolated cluster |
| Moderate dynamics — lower memory | temperature, lynx_hare, keeling_seasonal | No feature extremes; baseline_delta spans −0.3 to +1.0 |
| Moderate dynamics — higher memory | streamflow (log) | lag1≈0.70, baseline_delta≈+0.2 |
| Spike dynamics | ecg | kurtosis extreme; baseline_delta≈−0.15 |
| Slow periodic / burst-like | sunspot_cycle | Joins COVID cluster in 6-feature space — high autocorr, right-skewed, low zc, baseline_delta≈0 |

**Key update from notebook 11:** COVID waves are event-WITH-memory (baseline_delta=+0.61, not ≈0). The epidemic plateaued above its starting level — endemic floor persisted. The original "burst returns to baseline" hypothesis was wrong.

**Key update from notebook 11:** baseline_delta is independent of slope for non-monotone series. COVID: slope≈0, delta=+0.61. These diverge completely for burst shapes.

---

## Observed shape taxonomy (empirical, as of 2026-03-24)

Six shape classes identified across 8 datasets. No single feature drives all separations — the combination matters.

| Shape class | Datasets | Primary discriminators |
|---|---|---|
| Right-skewed burst | covid_first_wave, covid_second_wave | skewness≈0.95, lag1≈0.95, zc≈0.02 |
| Symmetric steady climb | keeling_trend | skewness≈0, lag1=1.0, zc≈0.01 |
| Moderate dynamics | temperature, lynx_hare | No feature extremes — all moderate |
| Left-skewed periodic | keeling_seasonal | skewness=-0.16, flat kurtosis |
| Right-skewed slow periodic | sunspot_cycle | skewness=0.49, lower zc |
| Spike dynamics | ecg | kurtosis=15.165 — uniquely extreme |
| Mod. dynamics — lower memory | temperature, lynx_hare | lag1≈0.50–0.68, kurtosis<0, zc≈0.17–0.28 |
| Mod. dynamics — higher memory | streamflow (log) | lag1≈0.70, kurtosis≈-0.3, zc≈0.22 |

**Key finding:** "Moderate dynamics" is a genuine shape region (not a catch-all), with internal sub-structure resolved by `lag1_autocorr`. Catchment buffering (streamflow) produces slightly higher memory than interannual climate/ecological variability (temperature, lynx_hare).

**Preprocessing note:** Log-transform discharge before feature extraction. Raw discharge is log-normal; flood spikes inflate skewness (2.09) and kurtosis (6.93) out of the moderate range. `np.log1p()` collapses the tail while preserving all temporal dynamics.

Key lesson: "directional" and "periodic" are not single shape classes. Skewness subdivides directional; kurtosis and zc subdivide periodic.

## Scoring / validation

**Decision:** Use COVID first wave majority (real, non-noise) cluster as the directional-burst reference. Test predictions against it.

**Why COVID first wave:** 202 countries, all showing the same basic burst shape — the largest and cleanest directional dataset. A natural anchor for the "directional burst" cluster.

**Important:** Always skip cluster `-1` (noise) when determining the reference cluster and when determining each dataset's majority cluster. Noise is not a shape.

---

## Download strategy for UCR datasets

**Decision:** Use `urllib.request` not `requests` for timeseriesclassification.com.

**Why:** `requests` silently receives HTML (possibly a redirect or bot-detection page) with HTTP 200, which passes the status check but fails at zip extraction. `urllib` behaves consistently with `curl`. Always validate with `zipfile.is_zipfile()` before extracting.

---

## Temperature source — Berkeley Earth as primary, NASA GISS as fallback

**Decision:** Primary source is Berkeley Earth S3 (`berkeley-earth-temperature.s3.amazonaws.com/Global/Land_and_Ocean_summary.txt`). NASA GISS is tried as fallback. Parse cell auto-detects format (`%` comments = Berkeley Earth, `Year`/`J-D` header = NASA).

**Why:** NASA GISS (`data.giss.nasa.gov`) goes down periodically. Berkeley Earth provides equivalent global land-ocean anomaly data, same shape, same 1850s-present range, publicly hosted on S3 (more reliable). The two datasets are highly correlated — the 20-yr window shape features will be indistinguishable for the purposes of this experiment.

---

## NASA GISS temperature — do not force-delete cache

**Decision:** Use the same `if not dest.exists()` guard as all other datasets. Do not unconditionally delete and re-download.

**Why:** NASA GISS is occasionally unreachable. The original notebook 07 forced a fresh download every run (`dest.unlink()`) to pick up updates, but that causes a hard failure when the server is down. The data changes slowly enough that a cached copy is fine.

---

## NOAA Keeling CSV — force numeric before filtering

**Decision:** After `pd.read_csv(..., comment='#', header=None)`, coerce `year`, `month`, `average` to numeric with `pd.to_numeric(..., errors='coerce')` and `dropna()` before any comparison.

**Why:** The NOAA file contains a stray non-comment header row with string values. Without coercion, `co2['average'] > 0` raises `TypeError: '>' not supported between instances of 'str' and 'int'` in pandas 2.x (stricter type enforcement). Coercing to numeric first turns the stray row into NaN, which `dropna()` removes cleanly.

---

## pandas 2.x compatibility — fillna

**Decision:** Use `.bfill().ffill()` chained on the Series, not `fillna(method='bfill')`.

**Why:** The `method` keyword argument was removed from `fillna()` in pandas 2.x. Raises `TypeError` at runtime. Direct `.bfill()` / `.ffill()` methods are the correct replacement and work across all pandas versions.

---
