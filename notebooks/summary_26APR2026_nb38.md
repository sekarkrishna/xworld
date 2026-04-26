# Session Summary — 26 April 2026 (nb38)

## What was done

nb38 — Corpus Robustness Audit: Which Classifications Are Window-Earned?

**Phase 3 — Thread 4 synthesis.** Two experiments: (A) class self-recognition rates — sweep n_cycles for each of the 9 shape classes and measure what fraction of window lengths correctly classify the canonical signal; (B) corpus audit — apply observability zones to the 17 real-world datasets and assign robustness verdicts.

---

## Part A: Class Self-Recognition Rates

| Class | Self-recog | Zone | Zone width |
|---|---|---|---|
| trend | 100% | all | ∞ |
| integrated_trend | 100% | all | ∞ |
| declining_monotonic | 100% | all | ∞ |
| burst | 100% | all | ∞ |
| irregular_osc | 96% | [0.15, 8.00] | ~8 cycles |
| declining_osc | 36% | [2.54, 5.32] | 2.78 |
| oscillator | 33% | [1.14, 3.93] | 2.79 |
| eco_cycle | 30% | [1.14, 3.63] | 2.49 |
| seasonal | 30% | [4.03, 6.51] | 2.48 (narrowest) |

Prediction (eco_cycle narrowest): **wrong**. All four periodic classes cluster at 30–36% self-recognition with ~2.5-cycle zone widths. irregular_osc is effectively window-invariant (96%) because noise dominates at all n_cycles.

---

## Part B: Corpus Robustness Audit (corrected)

| Verdict | Count | Datasets |
|---|---|---|
| INVARIANT | 8 | CO2_trend, CH4_trend, Ocean_heat, Sea_level, PIOMAS_ice, Glaciers, Forest_cover, COVID |
| NOISE-ROBUST | 3 | NAO, PDO, VIX |
| EARNED | 1 | Sunspot |
| BORDERLINE | 4 | ENSO, Global_temp, Arctic_sea_ice, Antarctic_sea_ice |
| WINDOW-AWARDED | 1 | CO2_seasonal |

12/17 (71%) robustly classified. Note: an NaN-handling bug in the code initially marked NAO/PDO/VIX as WINDOW-AWARDED; corrected to NOISE-ROBUST (irregular_osc at 96% self-recognition is effectively observer-invariant).

**CO2_seasonal:** n_cycles≈3.0, below seasonal zone [4.03, 6.51]. A 4+ year window is required for robust seasonal classification.

**Sea ice datasets:** n_cycles≈2.0, just below declining_osc zone (starts at 2.54). A 30-month window would place them firmly in the zone.

---

## Key findings

**F113:** All four periodic classes have similar observability zone widths (~2.5 cycles). Eco_cycle is NOT uniquely fragile. The ~30% self-recognition rate is a universal property of the sweep range / zone width ratio, not class-specific vulnerability.

**F114:** 12/17 datasets classified robustly (71%). CO2_seasonal is the main window-awarded case (n_cycles=3 < zone minimum of 4). Arctic/Antarctic sea ice are borderline (n_cycles=2.0 vs zone start of 2.54).

**F115:** XWorld central claim is observer-invariant for the 12 trend/noise datasets. Observer-relative for the 5 periodic/quasi-periodic datasets. Thunder hypothesis final assessment: the ODE territory is observer-independent; the fingerprint map from observation to class is observer-relative for periodic dynamics.

---

## Thread 4 complete

Thread 4 (nb37–38) established:
- The 3-zone (and actually 5-zone) aliasing structure for periodic signals
- Burst kurtosis threshold: disappears at wide widths, not narrow
- Trend-type classes are window-invariant; oscillatory classes are window-sensitive
- Corpus robustness: 12/17 reliable; CO2_seasonal requires a longer window
- The XWorld claim holds for its strongest subset (trend/noise datasets) and requires window documentation for periodic datasets

## Findings added
F113–F115. Total findings: **115**.
