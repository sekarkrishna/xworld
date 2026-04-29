# Session Summary — 29 Apr 2026 (nb40)

**Notebook:** `40_eco_cycle_verdict.ipynb`
**Topic:** The eco_cycle Verdict — Distinct Attractor or Noise-Displaced Oscillator?
**Findings added:** F119–F121 (total: 121)

---

## What was tested

Three tests to deliver a verdict on whether eco_cycle deserves to remain a first-class shape category.

**Part A — Noise continuum:** Pure oscillator + noise sweep from σ=0 to 0.50 (25 steps, 100 instances each). Tracking oscillator / eco_cycle / irregular_osc fraction at each step.

**Part B — Harmonic × noise phase diagram:** 6×8 grid: harmonic amplitude [0.0, 0.1, 0.2, 0.4, 0.6, 0.8] × noise σ [0.00, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40]. 50 instances per cell.

**Part C — Retire test:** Reclassify 200 eco_cycle instances under 8-class system (eco_cycle removed). Compare 9-class vs 8-class ARI on 900-instance test set. Verify zero corpus datasets change class.

---

## Results

### F119 — Gradual transition confirmed

eco_cycle fraction rises from 3% at σ=0 to a peak of 53% at σ=0.167 with no sharp step on the entry side. Max adjacent-step change = 0.240 (mean = 0.045), but this occurs on the *exit* side (eco_cycle→irregular_osc), not the entry. No sharp basin boundary exists. eco_cycle is a statistical intermediate region, not a distinct attractor.

### F120 — Multi-target reclassification; zero corpus impact

Prediction of >90% oscillator absorption was overconfident: 58% go to oscillator, 27.5% to declining_osc, 8% to seasonal, 6% to irregular_osc. The three-way split reveals eco_cycle occupies a boundary region near three class centroids, not a subdivision of oscillator alone. ARI drop from 9-class to 8-class: Δ = −0.038. Zero corpus datasets change class (confirmed: none were ever eco_cycle).

### F121 — Verdict: eco_cycle retired as first-class category

All eight criteria met:

| Evidence | Status |
|---|---|
| No ODE basis | Confirmed (nb32, F88) |
| No real-world anchor | Confirmed (nb34, F97) |
| Noise-sufficient generation | Confirmed (nb34, F98; nb40 Part B) |
| Gradual basin boundary | Confirmed (nb40 Part A) |
| Multi-target reclassification | Confirmed (58% osc / 27.5% decl_osc / 14% other) |
| Zero corpus impact | Confirmed (nb40 Part C3) |
| Small ARI penalty (Δ=−0.038) | Confirmed (nb40 Part C2) |
| TDA+RQA purity 17% (weakest) | Confirmed (nb39, F118) |

**The XWorld taxonomy becomes 8 classes from nb40 onward:**
oscillator · seasonal · declining_osc · irregular_osc · burst · trend · integrated_trend · declining_monotonic

eco_cycle is retained as a transition-zone label only — a descriptor for signals in the noise-harmonic intermediate region between oscillator and irregular_osc.

---

## Artifact

`artifacts/nb40_eco_cycle_verdict.png` — 4-panel figure: (A) noise continuum curves, (B) harmonic×noise phase diagram heatmap, (C) reclassification bar chart, (D) eco_cycle vs oscillator in skewness×zero_crossings feature space.
