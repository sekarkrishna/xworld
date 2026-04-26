# Session Summary — 26 April 2026 (nb37)

## What was done

nb37 — Window Aliasing and Observer-Relative Shape Classes.

**Phase 3 — Thread 4.** Three experiments on how observation window length determines shape class assignment: (A) sinusoid window sweep across n_cycles 0.10–8.0, (B) multi-signal aliasing map for oscillatory vs trend-type signals, (C) Gaussian burst window expansion.

---

## Part A: Sinusoid Window Sweep

**Prediction:** 3 clean zones (declining_monotonic, oscillator, seasonal) with transitions at n_cycles ≈ 1 and ≈ 4.

**Result:** 5-zone structure. Prediction approximately right about boundaries, wrong about smoothness.

| n_cycles | Class (σ=0) | Mechanism |
|----------|-------------|-----------|
| < 0.50 | integrated_trend | <½ cycle → monotone curve with curvature |
| 0.50–0.63 | eco_cycle | ½ cycle → asymmetric half-sine (negative skew) |
| 0.63–1.10 | declining_monotonic | <1 full cycle → window aliasing |
| 1.10–4.02 | oscillator | optimal zone (eco_cycle excursion at 1.43–1.69) |
| 4.02–7.87 | seasonal | >4 cycles → ZC aliasing |
| > 7.87 | irregular_osc | ZC collapses fingerprint into noise |

Eco_cycle appears as a transitional band: at n_cycles≈0.5 (half-cycle asymmetry) and at n_cycles≈1.5 (1.5-cycle resonance, left-skewness). It is the fingerprint landing zone for distorted oscillatory shapes.

Noise fragility: σ=0.10 changes 32.5% of window assignments; σ=0.20 changes 91.7%.

---

## Part B: Multi-signal Aliasing Map

**Result: Prediction confirmed exactly.**

| Signal type | Distinct classes | Verdict |
|---|---|---|
| linear_trend | 1 (integrated_trend 100%) | Window-INVARIANT |
| cumsum_pos | 1 (integrated_trend 100%) | Window-INVARIANT |
| cumsum_neg | 1 (declining_monotonic 100%) | Window-INVARIANT |
| sinusoid | 6 classes | Window-SENSITIVE |
| two_freq | 7 classes | Window-SENSITIVE |
| damped_sinusoid | 8 classes (all except trend) | Window-SENSITIVE |
| noisy_sinusoid | 4 classes | Window-SENSITIVE |

The damped sinusoid traverses 8 of the 9 shape classes as window length varies — the full shape-class atlas is accessible via window length alone.

---

## Part C: Burst Window Expansion

**Prediction:** Burst disappears at small burst_width (<0.10 of window) when spike is too narrow. Prediction reversed.

**Result:**
- Burst class maintained for burst_width ∈ [0.020, 0.134] — narrowest spike tested still classifies as burst (kurtosis=15.5).
- Above 0.134: centered → oscillator; left-biased (center=0.25) → declining_monotonic.
- Discriminator: kurtosis. Narrow spike → leptokurtic → burst. Wide bell → platykurtic → oscillator.
- ZC and lag1 do not change at the transition — kurtosis alone determines the class boundary.

---

## Key findings

**F110:** 5-zone aliasing structure for sinusoids (not 3). Eco_cycle appears as a transitional band at n_cycles≈0.5 and 1.5. Noise collapses the structure fast: 91.7% of windows change class at σ=0.20.

**F111:** Burst fingerprint disappears at LARGE widths (>0.134), not small. Prediction reversed. The discriminator is kurtosis crossing zero — leptokurtic (spike) → burst; platykurtic (bell) → oscillator.

**F112:** Trend-type signals are window-invariant; oscillatory signals are window-sensitive. Confirmed exactly. Thunder hypothesis supported: for periodic dynamics, the shape class is a property of the (signal, observer window) pair.

---

## Open questions

- Does the 5-zone sinusoid structure shift if the classifier is retrained on a different n_cycles range? (The oscillator→seasonal boundary at n_cycles≈4 tracks the training boundary of the seasonal generator.)
- Can the burst kurtosis threshold (≈0) be used as a diagnostic to check whether a "burst" finding is robust to window length?
- For the real-world corpus, which datasets are in the "window-sensitive zone"? Any real-world oscillatory dataset might classify differently under a different observation timescale.

## Findings added
F110–F112. Total findings: **112**.
