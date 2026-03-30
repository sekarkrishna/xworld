# Session Summary — 30 March 2026

## What was done

**Phase 1c: Stability test (Notebook 18)**

Ran HDBSCAN across 15 parameter combinations (min_cluster_size ∈ [4,6,8,12,16] × min_samples ∈ [2,3,5]).

Results were very different from predictions:
- Only 2 truly granite classes: keeling_seasonal and keeling_trend (0% noise, 100% stable in all 15 runs)
- Sunspot: 100% stable but collapses INTO the COVID cluster in 73% of runs — stability borrowed, not earned
- ECG: 0% stable despite low noise (26.5%) — 884 instances fragment into many sub-clusters; ECG is a family, not one shape
- Small-n datasets (lynx_hare=26, streamflow=24, temperature=31): always noise by threshold arithmetic, not by shape
- COVID first wave: 0% stable — 202 country waves are a heterogeneous burst family
- Phase 1b (sea_level, ENSO, VIX): no parameter setting rescues them — structural gaps are real, not parametric

Findings 33–38 recorded.

---

**Infrastructure: TensorFlow installed**

Python 3.14 venv → Python 3.13 (TF requires ≤3.13). `uv python pin 3.13` + venv recreated + `uv sync` + `uv add tensorflow`. TF 2.21.0 installed; all existing packages confirmed working.

---

**Phase 2: Autoencoder (Notebook 19)**

Two Keras autoencoders trained on raw resampled series (64 pts, z-scored, n=1930):
- Dense AE: 64→32→16→8(latent)→16→32→64
- Conv AE: Conv1D encoder → Dense(8) bottleneck → Conv1D decoder

Key result — pairwise centroid distances (Conv latent vs feature space):

| Pair | Feature | Latent | Ratio |
|---|---|---|---|
| sunspot ↔ covid1 | 0.769 | 4.451 | 5.79x ↑ |
| enso ↔ sunspot | 0.859 | 6.040 | 7.03x ↑ |
| covid1 ↔ covid2 | 0.250 | 2.256 | 9.02x ↑ |
| lynx_hare ↔ vix | 0.616 | 0.944 | 1.53x ↑ |
| **temperature ↔ sea_level** | **4.607** | **0.777** | **0.17x ↓** |

Temperature-sea_level is the headline: feature space declared them maximally different; the autoencoder found them near-identical. Both are noisy upward drifts. The hand-crafted features penalized different zero_crossings and entropy; the raw waveform revealed the same underlying shape. Finding 28's "noisy directional" 8th class is now confirmed by an independent method.

Findings 39–42 recorded.

---

**Future directions recorded (memory)**
1. Mirror distortions (synthetic invariance test)
2. Audio / whale calls (predator-prey vocalizations as time series)
3. Video / amoeba chemotaxis (new extraction pipeline)

---

## Findings this session: 33–42 (10 new findings)

## Total findings to date: 42

## Notebooks completed: 01–19

---

## Open questions going into next session

1. **Spatial UMAP of latent space** — where do Phase 1b datasets sit geometrically? Do they fill the gaps between the dense cores, or are they still isolated?
2. **ECG sub-structure** — do the Conv AE sub-clusters align with UCR true labels (class 1 vs class 2)?
3. **Small-n datasets** — do lynx_hare/streamflow/temperature get meaningful latent positions without a cluster-size floor?
4. **Noisy directional class** — what other datasets belong alongside temperature and sea_level? Candidates: Arctic sea ice extent, glacier mass balance, ocean heat content.
5. **Foundation model embeddings** — Chronos (HuggingFace) as next Phase 2 step: does a model pre-trained on millions of series recover the same geometry without seeing our data?
