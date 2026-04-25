# Session Summary — 25 April 2026 (nb32)

## What was done

nb32 — Phase 3 opener: ODE basis for the 9 shape classes.

**Hypothesis:** Each shape class is the fingerprint signature of a specific class of differential equation. If we integrate the natural ODE for each class and run the fingerprint, each should land in its predicted class.

**Result: 8/9 correct.**

---

## ODE → class mapping

| ODE | Result |
|---|---|
| Simple harmonic ẍ + ω²x = 0 | oscillator ✓ |
| Damped harmonic impulse response exp(−γt/2)·sin(ω_d·t) | declining_osc ✓ |
| Lotka-Volterra prey | oscillator ✗ (eco_cycle failure — see below) |
| Forced harmonic sin(ωt)+0.25·sin(2ωt) | seasonal ✓ |
| Gaussian pulse | burst ✓ |
| Constant drift dx/dt = a | trend ✓ |
| Langevin dx/dt = a + σξ | integrated_trend ✓ |
| Langevin dx/dt = −a + σξ | declining_monotonic ✓ |
| Rössler chaotic attractor | irregular_osc ✓ |

---

## Key findings

**F89:** 8/9 ODEs land correctly. The fingerprint features map onto ODE parameters: ZC≈f(ω), lag1≈g(γ), slope≈h(drift). The taxonomy has a basis in differential equation theory.

**F90 (γ sweep — unexpected):** Increasing damping from 0 → 3×critical does NOT produce oscillator → declining_osc → declining_monotonic. The actual transition is: oscillator → eco_cycle → burst (stays burst forever). Reason: starting from displacement x(0)=1 produces smooth monotone decay → burst fingerprint. Declining_osc requires the GREEN'S FUNCTION initial condition (x(0)=0, ẋ(0)=ω). Initial conditions determine shape class, not just ODE parameters.

**F91 (eco_cycle failure — significant):** Lotka-Volterra prey series has positive skewness (+0.48). eco_cycle centroid has *negative* skewness (−0.135). LV produces the wrong sign. The eco_cycle class cannot be derived from a simple deterministic ODE. It is noise-dependent — the same harmonic superposition sin(ωt)+0.4sin(2ωt) classifies as oscillator without noise, eco_cycle with noise σ=0.12. The class name is physically misleading. eco_cycle is the only class in the 9-class taxonomy without a clean ODE basis.

**F92:** ODE parameters map to features: ρ(ω, ZC)=0.998; ρ(γ, lag1)=+0.943 (higher damping → higher lag1, counterintuitive); ρ(drift, slope)=1.000.

**F93:** Rössler (deterministic chaos) classifies as irregular_osc 12/12 windows. The class captures both chaos and stochastic noise — they are fingerprint-indistinguishable.

---

## Open questions for Phase 3 continuation

- Can we recover declining_osc from the damped harmonic ODE by choosing different initial conditions? ✓ (Yes — green's function solution works)
- What ODE (if any) correctly produces eco_cycle? Is there a stochastic ODE that works?
- Does the Lorenz system (different chaotic attractor) also land in irregular_osc?
- Can we build a Phase 3 "ODE dictionary" that maps the 9 classes to eigenvalue regions?

---

## Findings added
F89–F93.
