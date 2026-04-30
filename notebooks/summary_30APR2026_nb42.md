# Session Summary — 30 April 2026 (nb42)

## Notebook 42 — Dominant Process Test

**Session goal:** Test the revised hypothesis from nb41 F124: classification quality (centroid distance d_min) tracks the coherence of the dominant physical process, not sensory category.

**The test:** Add the purest single-process signal available — a tidal gauge (gravitational forcing from Moon+Sun) — and compare its d_min to signals with competing processes at the same temporal scale.

---

## Experiment design

| Signal | Dominant process | Coherence score | Expected d_min |
|---|---|---|---|
| Tidal gauge (1-wk/1-mo/1-yr) | Gravitational (Moon+Sun) | 1 | < 1.5 |
| CO2 trend (Keeling) | Anthropogenic emissions | 2 | < 2.0 |
| ENSO MEI v2 | Pacific thermodynamic oscillation | 2 | ≈ 1.9 (confirmed nb41) |
| Thermistor hourly (1-wk) | Diurnal solar + HVAC + occupancy | 3 | 2.0–4.0 |
| Wave height daily | Wind-sea + swell + storm surge | 4 | > 4.0 (confirmed nb41) |
| VIX monthly | Collective cognition (no physics) | 5 | > 10 (confirmed nb41) |

---

## Predictions

- **F125:** Tidal → oscillator or seasonal, d_min < 1.5, same class at all temporal scales
- **F126:** d_tidal < d_thermistor at 1-week / 168-hour scale
- **F127:** Spearman ρ(coherence score, d_min) > 0.7 across all 9 signals

---

## Results

### Part A — NOAA CO-OPS tidal gauge (The Battery, NYC, 2023)

| Scale | n_pts | Class | d_min |
|---|---|---|---|
| 1-week | 168 | seasonal | **0.724** |
| 1-month | 720 | seasonal | **0.910** |
| 1-year | 8,760 | seasonal | **0.818** |

Scale-consistent: **True** — all three scales → seasonal. This is the lowest centroid distance of any real-world signal in the corpus. Fingerprint: skewness≈0, kurtosis=−1.21 (pure-sine platykurtosis), lag1=0.882, ZC=0.160.

### Part B — Thermistor hourly 1-week (same 168-pt scale as tidal)

| Feature | Tidal | Thermistor | Diff |
|---|---|---|---|
| skewness | 0.070 | 0.996 | +0.926 |
| kurtosis | −1.213 | 1.653 | +2.866 |
| lag1_autocorr | 0.882 | 0.882 | ≈0 |
| zero_crossings | 0.161 | 0.149 | −0.012 |

Thermistor → burst, d=**3.610** (5× messier). Lag1 and ZC are identical — the 5× gap is entirely skewness+kurtosis from HVAC and occupancy spikes.

### Part C — Dominant process ranking (full corpus)

| Signal | Coherence | Class | d_min |
|---|---|---|---|
| Tidal 1-week | 1 | seasonal | 0.724 |
| Tidal 1-month | 1 | seasonal | 0.910 |
| Tidal 1-year | 2 | seasonal | 0.818 |
| CO2 trend (Keeling) | 2 | trend | 1.619 |
| ENSO MEI v2 | 2 | burst | 1.910 |
| Thermistor hourly 1-wk | 3 | burst | 3.610 |
| GISS temperature 145yr | 3 | burst | 1.962 |
| Wave height daily | 4 | burst | 6.609 |
| VIX monthly | 5 | burst | 11.505 |

**Spearman ρ = 0.932, p = 0.000** — hypothesis confirmed, well above the ρ > 0.7 prediction.

---

## Findings

**F125 (confirmed, exceeded):** Tidal gauge → seasonal d=0.724 at 1-week; scale-consistent across 1-week/1-month/1-year. Lowest d_min in corpus.

**F126 (confirmed):** d_tidal = 0.724 < d_thermistor = 3.610 at same 168-hour scale. Gap driven by skewness+kurtosis from competing HVAC/occupancy processes, not temporal scale.

**F127 (confirmed, exceeded):** Spearman ρ = 0.932 across 9 signals. The dominant-process hypothesis is the correct framing for Phase 2.

Total findings after nb42: **127**

---

## What it means — revised hypothesis

> **Classification quality (d_min) is determined by the number of competing physical processes active at the observation scale, and by whether the dominant process has had sufficient time to average over noise.**

This is the Phase 2 anchor finding. The 8-class vocabulary works precisely because most natural phenomena are dominated by a single process at the scale of observation. VIX fails (d=11.5) not because it is cognitive but because it has *no* dominant process. Tidal succeeds (d=0.724) not because it is physical but because it has *one*.

---

## Errors encountered and fixed

1. **NOAA CO-OPS 400 Bad Request:** URL used `product=water_level&interval=h` — wrong product name. Fixed to `product=hourly_height`.
2. **CO2 CSV ValueError:** `header=None` caused the header row ("deseasonalized") to be parsed as data. Fixed by using `pd.read_csv(io.BytesIO(raw_co2), comment='#')` — pandas auto-reads the header after skipping `#`-prefixed comment lines.

---

## Next experiment candidates

1. **nb43 — Multi-scale dominant process:** For a signal with two competing processes (e.g. tidal + storm surge), can we identify the scale at which the secondary process becomes visible (d_min inflection)?
2. **nb44 — Synthetic process competition:** Programmatically add noise processes to the pure tidal signal. Measure d_min as a function of noise amplitude. Gives a calibration curve: "x% competing noise = y increase in d_min."
3. **nb45 — Grokking experiment:** Train a transformer on the 8-class synthetic corpus. Watch for grokking transition. Probe whether post-grokking representations are domain-agnostic (cf. F117, grokking transfer hypothesis).
