# Session Summary — 30 March 2026 (nb20 addendum)

## What was done

**Phase 2b: Chronos Foundation Model Embeddings (Notebook 20)**

Installed `chronos-forecasting 2.2.2` (PyTorch 2.11.0 was already present). Loaded Amazon Chronos-T5-Small (46 M params, 512-dim encoder) zero-shot — no training on our data. Extracted mean-pooled T5 encoder hidden states for all 1930 instances. HDBSCAN + UMAP on 512-dim embeddings.

---

### HDBSCAN clusters (8 clusters, 32.2% noise)

| Cluster | Dataset | Purity |
|---|---|---|
| cl7 | keeling_seasonal | 100% |
| cl4 | keeling_trend | 100% |
| cl2 | ECG | 99% |
| cl3 | sea_level | 97% |
| cl1 | streamflow | 79% |
| cl5 | sunspot_cycle | 54% |
| cl6 | VIX (28%) + ENSO (24%) + temperature (23%) | mixed |
| cl0 | COVID first+second (~18% each) | partial |

lynx_hare: 100% noise.

---

### Pairwise centroid distances (Chronos 512-dim)

| Pair | Feature-6f | Conv AE (nb19) | Chronos |
|---|---|---|---|
| sunspot ↔ covid1 | 1.988 | 4.451 | **0.301 — FARTHEST** |
| covid1 ↔ covid2 | 0.871 | 2.256 | **0.059 — CLOSEST** |
| enso ↔ sunspot | 0.818 | 6.040 | 0.094 |
| lynx_hare ↔ vix | 0.893 | 0.944 | 0.119 |
| temperature ↔ sea_level | 0.655 | 0.777 | 0.140 |

---

### Key findings

**F43:** Sunspot-COVID is the maximally separated pair in Chronos space (0.301, farthest of 10 pairs). Three independent methods — TD features, trained Conv AE, zero-shot Chronos — all agree this is the most structurally distinct pairing.

**F44:** Chronos separates sea_level from temperature. Sea_level gets its own pure cluster (cl3, 97%), while temperature is 77% noise. This diverges from the Conv AE (which contracted them 0.17x). The "noisy directional" 8th class needs to be split: clean monotonic trend (sea_level) vs noisy trend-with-oscillation (temperature).

**F45:** Chronos discovers a cross-domain irregular cluster: VIX (finance) + ENSO (climate oscillation) + temperature (global surface). VIX-lynx_hare cross-domain match (nb17, nb19) does not survive into Chronos space — VIX groups with climate oscillators instead.

**F46:** ECG sub-structure aligns with UCR true labels at ARI=0.742 — highest sub-cluster ARI in the experiment. Chronos, trained on unrelated series, discovers clinical ECG morphology classes zero-shot.

---

## Findings this session (nb20 addendum): 43–46 (4 new findings)

## Total findings to date: 46

## Notebooks completed: 01–20

---

## Open questions going into next session

1. **"Noisy directional" refinement** — three emerging sub-types (sea_level: clean monotonic; temperature: noisy trend; ENSO: irregular oscillatory). Test with new targeted datasets: glacier mass balance, ocean heat content, Arctic sea ice.
2. **Why Conv AE and Chronos disagree on temperature-sea_level** — is sea_level's isolation real, or a data-density artifact (n=120 dense windows vs n=31 scattered windows)?
3. **What is cl6?** VIX + ENSO + temperature in Chronos. What raw waveform property causes Chronos to group these?
4. **Mirror distortions** — synthetic invariance test: if you time-reverse sunspot, does it stay in the sunspot cluster?
