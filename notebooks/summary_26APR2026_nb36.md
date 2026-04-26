# Session Summary — 26 April 2026 (nb36)

## What was done

nb36 — Chaos Survey and 3-Way Junction.

**Phase 3 — Thread 3 (continuation).** Two experiments: (A) compare Lorenz and Van der Pol attractors against the Rössler reference (F93); (B) map the eco_cycle/declining_osc/oscillator junction region to determine whether a true triple point exists.

---

## Part A: Chaos Survey

### Lorenz attractor

**Prediction:** All three components (x, y, z) → irregular_osc. Attractor geometry invisible to 6-feature fingerprint.

**Result: Prediction refuted.**

| Component | 1st class | 2nd class | lag1 | ZC |
|-----------|-----------|-----------|------|----|
| x | eco_cycle (75%) | burst (17%) | 0.899 | 0.087 |
| y | irregular_osc (71%) | burst (17%) | 0.833 | 0.125 |
| z | irregular_osc (100%) | — | 0.762 | 0.206 |

Rössler reference (F93): lag1=0.50–0.66, ZC=0.25–0.31, 100% irregular_osc.

Lorenz x is NOT fingerprint-equivalent to Rössler. The x-axis slow oscillation between the two butterfly wings creates long persistence (lag1=0.899) and low ZC (0.087) → eco_cycle. The z-axis (always positive, rapidly varying) matches Rössler → irregular_osc. Three projections of the same attractor land in three different fingerprint regions.

### Van der Pol oscillator

**Prediction:** Small μ → oscillator; large μ (≥3) → irregular_osc or burst.

**Result: Prediction partially refuted.**

| μ | Dominant class | P(oscillator) | P(irregular_osc) |
|---|---------------|---------------|-----------------|
| 0.1 | oscillator | 1.00 | 0.00 |
| 0.5 | oscillator | 1.00 | 0.00 |
| 1.0 | oscillator | 0.88 | 0.00 |
| 2.0 | oscillator | 0.69 | 0.00 |
| 3.0 | oscillator | 0.94 | 0.00 |
| 5.0 | oscillator | 1.00 | 0.00 |
| 8.0 | declining_monotonic | 0.19 | 0.00 |

Van der Pol never produces irregular_osc. At μ=8, period T ≈ 1.61×8 = 12.9 ≈ T_WIN (4π ≈ 12.6) — window aliasing collapses ZC → declining_monotonic (same mechanism as F101). Nonlinearity alone does not create irregular_osc; stochastic forcing is required.

---

## Part B: 3-Way Junction

**Prediction:** Not a true triple point. Confirmed.

Fine (γ, θ) grid: 26×41=1066 points. γ∈[0.30,0.80] (ratio 0.038–0.10 at ω=4), θ∈[0°,20°].

**Result:** 868 declining_osc, 198 eco_cycle, 0 oscillator.

Best triple-point candidate: γ=0.300, θ=8.5°: d_eco=0.805, d_dosc=1.003, d_osc=1.003. Spread=0.198.

The oscillator class requires γ<0.30 at ω=4 — it does not appear anywhere in the parameter region explored. The junction (F99) is a 1D eco_cycle/declining_osc boundary; the oscillator centroid sits on the far side of eco_cycle and is never approached. No triple point exists.

---

## Key findings

**F107:** Lorenz attractor geometry IS fingerprint-visible. Three projections of the same attractor land in three different classes: x→eco_cycle (high lag1, low ZC), y→irregular_osc (majority), z→irregular_osc. Prediction refuted: the two-lobed structure creates slow cross-wing oscillation visible to the fingerprint.

**F108:** Van der Pol never produces irregular_osc across μ∈[0.1,8.0]. Small μ → oscillator (confirmed). Large μ → window aliasing into declining_monotonic, not chaos. Nonlinearity without stochastic forcing cannot enter the irregular_osc basin.

**F109:** No eco/dosc/oscillator triple point. The junction is a 1D eco_cycle/declining_osc boundary; oscillator is absent from the γ∈[0.30,0.80] region entirely. Prediction confirmed.

---

## Open questions

- At what damping ratio γ/(2ω) does the oscillator class first appear? The sweep started at γ=0.30; the lower boundary is uncharted.
- Can Lorenz x be pushed from eco_cycle into irregular_osc by adding noise? (Its lag1=0.899 is very high — the irregular_osc centroid is in a different region of feature space.)
- Is there any deterministic system (no stochastic forcing) that produces irregular_osc? Rössler and Lorenz z both do — what is the sufficient condition?

## Findings added
F107–F109. Total findings: **109**.
