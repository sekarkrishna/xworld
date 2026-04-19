# Session Summary — 19 Apr 2026 (Notebook 28)

**Notebook:** `28_declining_osc_conditions.ipynb`
**Question:** What are the minimum conditions for the declining oscillator class? Does oscillation require *both* annual periodicity AND amplitude decline, or is one sufficient alone?

---

## Setup

**Part A — WGMS glacier mass balance:** Annual global glacier mass balance 1950–2025 (76 years). Strong monotonic decline, no annual oscillation. Tests whether oscillation is a necessary condition.

**Part B — Synthetic phase diagram:** 20×20 parameter sweep: n_cycles (0.5–7.0 complete cycles in 64 steps) × decline_strength (0.0–1.5 amplitude decay). 20 synthetic instances per cell (400 cells × 20 = 8,000 instances). Each instance classified by 6-feature fingerprint; mode class assigned to cell.

---

## Predictions

- WGMS → trend class (cl5)
- Phase diagram: declining_osc basin requires n_cycles > ~2 AND decline > ~0.3
- Pure oscillator region: n_cycles high, decline ≈ 0
- Trend region: decline high, n_cycles low

---

## Results

### Part A — WGMS

| Series | Nearest class | Distance | declining_osc rank |
|--------|--------------|----------|-------------------|
| Cumulative mass balance | eco_cycle | 3.26 | 3rd (3.76) |
| Annual mass balance | irregular_osc | 3.90 | 3rd (4.83) |

Prediction: trend class. **WRONG on class; partially right on mechanism.**

WGMS cumulative has zero_crossings=0.016 (no oscillation) and lag1_autocorr=0.9997 (extremely smooth) — correctly rejected from declining_osc. But predicted trend: also wrong. The real issue: the signed fingerprint has no class for "strong monotonic decline without oscillation."

Feature comparison — WGMS cumulative vs integrated_trend centroid:

| Feature | integrated_trend | WGMS cumulative |
|---------|-----------------|----------------|
| lag1_autocorr | 1.000 | 1.000 |
| zero_crossings | 0.016 | 0.016 |
| \|slope\| | 0.054 | 0.052 |
| \|baseline_delta\| | 3.140 | 3.289 |
| slope sign | + | − |
| baseline_delta sign | + | − |

WGMS cumulative is integrated_trend's mirror in every signed feature. With absolute fingerprint it would land in integrated_trend. Under the signed fingerprint, eco_cycle is the nearest class with a negative baseline_delta.

### Part B — Phase diagram

Class distribution across 400 cells (each cell = majority class over 20 instances):

| Class | Cells | % |
|-------|-------|---|
| declining_osc | 169 | 42.2% |
| seasonal | 79 | 19.8% |
| oscillator | 68 | 17.0% |
| eco_cycle | 52 | 13.0% |
| irregular_osc | 18 | 4.5% |
| burst | 14 | 3.5% |

**Declining_osc basin:** 42.2% of parameter space, mean purity 94.2%.

By-decline threshold (averaged over all n_cycles):
- decline < 0.47 → seasonal (oscillation without decay)
- decline ~0.55 → eco_cycle (transition)
- decline > 0.63 → declining_osc

By-n_cycles threshold (averaged over all decline values):
- n_cycles < 1.5 → eco_cycle / oscillator
- n_cycles 1.87–4.6 → declining_osc (core basin)
- n_cycles 5.3–7.0 → seasonal → irregular_osc (frequency too high)

Corner: n_cycles 2.2–2.6 + decline 0.95–1.5 → burst (extreme amplitude collapse)

---

## Findings

- **F73:** WGMS → eco_cycle (cumulative), irregular_osc (annual). Oscillation confirmed necessary for declining_osc. But also reveals: the signed fingerprint has no class for strong monotonic decline — WGMS is integrated_trend's mirror with no class to land in.
- **F74:** Phase diagram: declining_osc basin is 42.2% of parameter space, purity 94.2% — the largest and purest basin. Declining oscillation is a wide, robust attractor, not a narrow special case.
- **F75:** Minimum conditions: decline > ~0.6 AND n_cycles in ~1.9–4.6 range. Three independent phase boundaries: low-decline → seasonal; low-n_cycles → eco_cycle/oscillator; high-n_cycles ceiling → seasonal (sub-cycle windows).
- **F76:** Structural gap in the signed 8-class system: no class for "declining monotonic trend." WGMS is the natural anchor. Next decision: add a 9th class or switch to absolute fingerprint.

---

## Interpretation

The phase diagram clarifies why NH Snow Cover (nb24) missed declining_osc: annual snow cover completes ~12 cycles in a 12-month window, and the high-frequency ceiling (n_cycles > 5 → seasonal) explains the miss. Arctic sea ice completes ~1–3 cycles per standard window — squarely in the declining_osc basin.

The WGMS result reveals a deeper issue: the 8-class system has directional bias inherited from the corpus. All integrated-trend datasets trend upward. The downward counterpart is an unmapped class. WGMS is not close to declining_osc (distance 3.76, zero_crossings mismatch) — it is a genuinely separate shape: smooth, monotonic, strongly declining, no oscillation.

**The signed vs absolute decision is now load-bearing.** Three datasets now motivate the absolute fingerprint (WGMS, snow cover, and the synthetic mirror result). But adopting absolute fingerprint would collapse the Arctic/Antarctic sea ice and the keeling/ch4 trend pairs, potentially reducing the 8 classes.

---

## Next

Open questions after nb28:
1. **9th class or absolute fingerprint?** WGMS deserves a class; absolute fingerprint would merge other pairs. Architectural decision.
2. **Snow cover revisited with absolute fingerprint.** Does it finally land in declining_osc?
3. **Phase 3 preparation:** The attractor basin maps (synthetic phase diagrams) are the Phase 3 tool. What physical system parameter corresponds to n_cycles × decline in each domain?
