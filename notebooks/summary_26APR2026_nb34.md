# Session Summary — 25 April 2026 (nb34)

## What was done

nb34 — ODE Anomaly Resolution.

**Phase 3 continuation.** Two open anomalies from nb32 resolved in order.

**Part A — eco_cycle anomaly (F91):** LV predator-prey prey classifies as oscillator (skew=+0.476), not eco_cycle (centroid skew=−0.135). Three sub-questions: (1) What does actual lynx-hare classify as? (2) What (harmonic_amplitude × noise) parameter space generates eco_cycle? (3) Is eco_cycle a genuine dynamical class or a noise artifact?

**Part B — γ sweep IC dependence (F90):** Displacement IC always goes to burst, not declining_osc. What IC angle boundary separates them? Can any sweep traverse oscillator → declining_osc → declining_monotonic?

---

## Results

### Part A — eco_cycle anomaly

All three original predictions were wrong.

| Question | Prediction | Result |
|---|---|---|
| Lynx-hare real data → eco_cycle | eco_cycle | **declining_osc / burst** (zero eco_cycle) |
| Phase diagram: needs BOTH harmonic AND noise | both required | **noise alone (σ≥0.12) is sufficient** |
| eco_cycle boundary = skewness sign-flip | ✓ | **CORRECT** |

Real lynx-hare (1900–1920, 21 years) is one population peak-and-collapse. Dominant fingerprint: large positive-skew peak followed by decline → burst/declining_osc. eco_cycle centroid skewness = −0.136; real hare/lynx = +0.72 to +0.96. Signs are opposite. eco_cycle has no real-world anchor in the dataset that named it.

Phase diagram (8 harm_amp × 6 noise levels, 50 instances per cell): noise alone at σ=0.12 reaches 38% eco_cycle; σ=0.20 reaches 46% (dominant). Harmonic content extends the basin into low-noise conditions but is not required. eco_cycle = the negative-skewness region of oscillatory parameter space.

### Part B — IC angle sweep

| Prediction | Result |
|---|---|
| Displacement IC → burst (all damping) | **WRONG** — at light damping θ=0° → eco_cycle |
| Transition at θ≈60–80° | **WRONG** — transition at θ≈5° |
| Heavy damping → burst (IC-independent) | **CORRECT** |
| Decay sweep reaches declining_monotonic | **WRONG** — d=1.0 → burst; declining_monotonic unreachable |

Three damping regimes: (1) Light (γ/(2ω)=0.05) — θ=0° displacement IC sits at a 3-way class junction with margin=0.012; any 5° velocity component resolves to declining_osc. (2) Medium (0.08) — all declining_osc. (3) Heavy (0.12) — all burst.

Decay envelope sweep: oscillator→declining_osc at d≈0.42; declining_osc→burst at d≈0.92. declining_monotonic unreachable from oscillatory ODE — ZC never drops to the monotone threshold regardless of decay strength. The monotone classes are a structurally separate subspace requiring a drift term to suppress oscillation entirely.

---

## Key findings

**F97:** Real lynx-hare classifies as burst/declining_osc — zero eco_cycle occurrences. eco_cycle has no real-world anchor. Better name: **noisy_asymmetric_oscillator**.

**F98:** eco_cycle basin is noise-driven at σ≥0.12 without any harmonic content. Harmonic distortion extends the basin to low-noise conditions. eco_cycle = negative-skewness region of oscillatory space, not a distinct dynamical attractor.

**F99:** IC angle governing class depends on damping regime. Light damping: sharp 5° transition (not 60–80° as predicted). Displacement IC at θ=0° lands at eco_cycle boundary (margin=0.012) — a 3-way class junction visible in 6D fingerprint space. Heavy damping: IC-independent, all burst.

**F100:** Amplitude-decay sweep traverses oscillator→declining_osc→burst; declining_monotonic unreachable from an oscillatory ODE. The oscillatory and monotone subspaces are structurally separate in 6D fingerprint space, connected only by adding a drift term that fully suppresses oscillation.

---

## Open questions for Phase 3 continuation

- Does the Lorenz attractor (different chaotic attractor than Rössler) also land in irregular_osc?
- Can we build a Phase 3 "ODE dictionary" mapping the 9 classes to eigenvalue regions (real/complex, stable/unstable)?
- What stochastic ODE (if any) correctly produces eco_cycle's negative skewness deterministically?
- Is the 3-way junction at light-damping displacement IC a true triple point in 6D fingerprint space?

## Findings added
F97–F100. Total findings: **100**.
