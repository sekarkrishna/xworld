# Session Summary — 26 April 2026 (nb35)

## What was done

nb35 — ODE Eigenvalue Map: Shape Classes in the Complex Plane.

**Phase 3 — Thread 3.** For each point (α, ν) in the complex eigenvalue plane — where α = Re(λ) is the decay rate and ν = Im(λ)/(2π) is frequency in cycles — generate the Green's function solution x(t) = exp(α·t)·sin(2π·ν·t) and run the 9-class fingerprint classifier. Build the complete shape-class map of the complex eigenvalue plane. Supplement with the real axis (ν→0), first-order stochastic space, and noise injection experiments.

---

## Results

### Main grid (2107 points)

**Prediction:** 3 regions — oscillator, declining_osc, burst.

**Result:** 5 classes appear. The oscillator band (ν∈[1.1,4.0], α∈[−1.8,0]) is real but bounded by aliased classes on both sides:
- **ν>4.0, α≈0: seasonal** — ZC aliasing. Single-frequency sine at high frequency matches seasonal centroid better than oscillator (both have similar ZC but seasonal training band extends to 6 cycles).
- **ν<1.0, α≈0: declining_monotonic** — window aliasing. <1 cycle looks like a monotone decline to the fingerprint.
- **ν≈0.6: eco_cycle** — half-cycle produces negative skewness matching eco_cycle centroid.

### Boundary geometry

ρ(ν, α_burst) = −0.917. **Prediction confirmed:** boundary slopes with frequency. Higher ν tolerates more decay — at ν=6, the series must have α<−3.2 before bursting; at ν=1.4, α<−2.4. α_crit(ν) is approximately linear.

### Real axis (ν→0)

**Prediction:** trend at α=0, burst at α≈−1.

**Result:** integrated_trend dominates (α∈[0,−2.3]); eco_cycle at α∈[−2.3,−3.8]; declining_monotonic at α<−3.8. **Burst never appears.** The critically-damped Green's function x(t)=t·exp(α·t) has negative skewness for moderate α — always classified as a smooth trend, never as a pulse.

### First-order space

declining_monotonic 49%, integrated_trend 47%, trend 1%. Trend requires quadratic acceleration (d²x/dt²>0), not just positive drift. Linear cumsum → integrated_trend, not trend.

### Noise injection

Three different paths to irregular_osc:
- Oscillator: → eco_cycle (σ=0.12) → irregular_osc (σ=0.25)
- Burst: → declining_osc → seasonal → irregular_osc (σ=0.20); never touches eco_cycle
- All paths converge to irregular_osc by σ≈0.25 — irregular_osc is the universal noise attractor

---

## Key findings

**F101:** 5 class regions in the complex plane (not 3). Oscillator band is bounded by seasonal (high ν) and declining_monotonic (low ν) aliasing.

**F102:** ρ(ν, α_burst) = −0.917 — boundary slopes with frequency. Higher frequency tolerates more decay before bursting.

**F103:** Real eigenvalue axis → integrated_trend (not burst). Burst is inaccessible from the velocity-IC Green's function on the real axis.

**F104:** Trend class requires quadratic acceleration, not linear drift. Linear cumsum → integrated_trend or declining_monotonic.

**F105:** Three different noise paths to irregular_osc. Burst → seasonal before irregular_osc (not eco_cycle). Universal convergence at σ≈0.25.

**F106:** 9 classes split into 4 structurally isolated ODE families: (1) 2nd-order linear, (2) 1st-order stochastic + curvature, (3) two-frequency superposition, (4) irregular_osc as noise attractor. No parameter sweep within one family reaches another.

---

## Open questions for Phase 3 continuation

- Does the oscillator→seasonal boundary at ν≈4 shift if we retrain the classifier with different frequency ranges?
- Can we find a real-world dataset in the seasonal aliasing zone (single-frequency but high-cycle)?
- Is the 4-family structural isolation testable on the real corpus — are there cross-family ambiguous datasets?
- The "trend" class requires quadratic drift — what physical process generates this? (The generator uses t + a·t², which corresponds to constant acceleration.)

## Findings added
F101–F106. Total findings: **106**.
