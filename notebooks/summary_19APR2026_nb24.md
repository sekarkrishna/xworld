# Session Summary — 19 April 2026 (Notebook 24)

## What was done

**Notebook 24: PDO window test + NH Snow Cover + orientation-invariant features**

Three targeted follow-ups from nb22 open questions. 20 datasets total — 18 from nb22 + pdo_36mo + nh_snow_cover.

---

## Part A — PDO window-length test

**Question:** Does PDO at 36-month windows migrate from the sea_level cluster toward ENSO?

| Pair | Chronos distance |
|---|---|
| pdo_36mo ↔ enso_oni | **0.137** |
| pdo_60mo ↔ enso_oni | 0.181 |
| pdo_36mo ↔ sea_level | 0.224 |
| pdo_60mo ↔ sea_level | 0.181 |

Shorter window → PDO moves toward ENSO, away from sea_level. The window-length effect is confirmed: at 60-month windows the decadal drift dominates and PDO presents as an integrated trend; at 36-month windows the interannual oscillatory component becomes visible and PDO approaches ENSO.

However, pdo_36mo does not fully join the ENSO cluster (distance 0.137 vs 0.072 for arctic↔antarctic). The shift is real but incomplete — PDO has genuine decadal structure that no window length fully removes.

---

## Part B — NH Snow Cover Extent (Rutgers, 1967–present)

**Question:** Does snow cover join Arctic/Antarctic sea ice in the declining oscillator class?

| Feature | Arctic sea ice | NH Snow Cover |
|---|---|---|
| Annual cycle | Yes | Yes |
| Long-term decline | Yes — ~35% loss | No — stable or slight increase |
| Skewness | Negative | **Positive** |

Snow cover cluster: **52% in irregular oscillator cluster (cl7), 0% in cl0 (declining oscillator).**

Prediction was wrong. Annual cycle frequency is necessary but not sufficient. The declining oscillator class requires a long-term trend in amplitude, not just seasonal periodicity. Snow cover's flat or slightly increasing baseline + positive skewness places it in the asymmetric oscillator class with VIX/ENSO/temperature.

---

## Part C — Orientation-invariant 6-feature fingerprint

**Question:** Does replacing slope + baseline_delta with |slope| + |baseline_delta| improve or degrade class structure?

Results: snow cover purity rises from 52% → **99% pure** in a single cluster. Sea ice purity is unchanged. The orientation-invariant fingerprint correctly identifies snow cover as seasonally-dominated (matching Chronos invariance finding from nb21 F52) without the directional component that splits directionally-defined classes.

Implication: the 6-feature fingerprint contains two logically separable pieces:
1. **Shape features** (skewness, kurtosis, lag1_autocorr, zero_crossings) — orientation-independent
2. **Direction features** (slope, baseline_delta) — orientation-sensitive

Using |slope|, |baseline_delta| gives a receptor that matches Chronos orientation-invariance. Using signed values gives a receptor sensitive to decline vs growth direction.

Both are valid. They answer different questions.

---

## Pre-run predictions vs results

| Test | Prediction | Result |
|---|---|---|
| pdo_36mo ↔ enso distance | Smaller than pdo_60mo ↔ enso | **CORRECT** — 0.137 vs 0.181 |
| NH Snow Cover cluster | cl0 (declining oscillator) | **WRONG** — 52% cl7, 0% cl0 |
| Orientation-invariant clustering | Fewer clusters; directional pairs collapse | **PARTIAL** — snow cover collapses to 99% pure; sea ice unchanged |

---

## Open questions arising

1. **Can declining oscillator be found outside the cryosphere?** Greenland ice mass and glacier area remain untested. Snow cover rules out "anything with an annual cycle and a cryospheric signal."
2. **What is the minimal condition for declining oscillator class?** Current evidence: needs (1) strong annual periodicity AND (2) long-term amplitude decline. Snow cover has (1) but not (2).
3. **|slope|, |baseline_delta| as the default fingerprint?** The orientation-invariant version matches Chronos and would give more stable clustering. But it loses the directional signal that distinguishes declining oscillator from regular oscillator — which is the key finding. Decision needed for Phase 3.
4. **HDBSCAN parameter sensitivity** as n grows (now 20 datasets). Still unresolved.

---

## Findings this session: 61–63 (3 new findings)

| Finding | Summary |
|---|---|
| F61 | PDO at 36-month window moves closer to ENSO (0.137 vs 0.181) — window-length effect confirmed but incomplete |
| F62 | NH Snow Cover does not join declining oscillator — annual cycle necessary but not sufficient; no long-term decline, positive skewness |
| F63 | Orientation-invariant \|slope\|+\|baseline_delta\| collapses snow cover to 99% pure; sea ice unchanged |

## Total findings to date: 63

## Notebooks completed: 01–24 (all complete)
