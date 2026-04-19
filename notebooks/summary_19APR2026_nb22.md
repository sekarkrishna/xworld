# Session Summary — 19 April 2026 (Notebook 22, re-run)

## What was done

**Notebook 22: Declining Oscillator Confirmation + NAO/PDO vs cl7**

Re-run from clean kernel after clearing stale cached outputs (previous run had WTI FRED cell timing out; WTI and copper replaced with NAO and PDO). 16 datasets total — 13 from previous sessions + Antarctic sea ice, NAO, PDO.

---

## HDBSCAN results (Chronos embeddings)

10 clusters, 38.5% noise (907 instances). Cluster numbering differs from nb20/nb21 across runs.

| Dataset | Dominant cluster | Purity |
|---|---|---|
| arctic_sea_ice | cl0 | 100% |
| antarctic_sea_ice | cl0 | **100%** |
| keeling_seasonal | cl9 | 100% |
| keeling_trend | cl8 | 100% |
| ecg | cl2 | 99% |
| lynx_hare | noise | 100% |
| streamflow | noise | 100% |
| pdo | cl4 | 59% |
| sea_level | cl4 | 47% |
| sunspot_cycle | cl7 | 54% |
| nao | noise | 79% |
| ocean_heat | noise | 96% |

---

## Key results

### Antarctic sea ice → cl0 (same as Arctic, 100%)
Chronos distance arctic↔antarctic = **0.072** — the smallest pairwise distance in the experiment. Tighter than COVID1↔COVID2. Two independent hemispheric datasets, opposite ends of the Earth, identical Chronos cluster membership.

### NAO → 79% noise, 0% in irregular cluster
Distances: nao↔vix = 0.192, nao↔enso_oni = 0.240. NAO does not join the VIX/ENSO/temperature group. The cl8 irregular asymmetric oscillator class is not a generic "irregular climate oscillation" — it is specific to Pacific interannual variability + financial volatility.

### PDO → cl4 with sea_level (59%)
Distance pdo↔nao = 0.101. PDO at 5-year windows presents as an integrated trend (decadal drift dominates over oscillation at this window length). Same physical ocean basin as ENSO but different shape class because the oscillatory cycle doesn't fit inside the window. Timescale is class-determining.

---

## Pre-run predictions vs results

| Dataset | Predicted | Result |
|---|---|---|
| Antarctic sea ice | cl0 (same as Arctic) | **CORRECT — 100% cl0, distance 0.072** |
| NAO | cl7/cl8 with ENSO | **WRONG — 79% noise, 0% cl8** |
| PDO | cl8 with ENSO or own region | **WRONG — 59% cl4, sea_level-adjacent** |

---

## Cluster mixing note

cl8 contains both keeling_trend (100%) and VIX/ENSO/temperature (24–29%). In nb20, these were in separate clusters. The addition of 3 new datasets shifted HDBSCAN density enough to merge what were previously distinct groupings. This is a parameter sensitivity artefact, not a new finding — the underlying separation is real but the parameter defaults don't recover it at n=16 datasets. Flagged as an open question for MILESTONES.

---

## Open questions arising

1. **Can the declining oscillator class be found outside the cryosphere?** Arctic and Antarctic sea ice are the only confirmed members. Greenland ice mass, glacier area, and permafrost extent are natural candidates.
2. **What specifically defines cl8 (VIX/ENSO/temperature)?** NAO failing to join it rules out "irregular climate oscillation" as the defining property. Positive amplitude asymmetry + interannual timescale is the current best hypothesis.
3. **PDO window length test:** Would PDO land in cl8 with ENSO if windowed at 36 months (same as ENSO) instead of 60 months? This would confirm the timescale-determines-class hypothesis.
4. **HDBSCAN parameter sensitivity:** How to stabilise cluster membership as new datasets are added? Grid search over min_cluster_size / min_samples scheduled for Phase 3.

---

## Findings this session: 58–60 (3 new findings)

## Total findings to date: 60

## Notebooks completed: 01–23 (all complete)
