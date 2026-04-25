# XWorld Research Log

**Central question:** Do a glacier melting and a stock market spike share the same numerical signature?

Cross-domain time series shape clustering. The hypothesis: series from completely unrelated domains share underlying dynamic shapes, detectable by a 6-feature fingerprint, blind to domain of origin.

> The domain is the costume. The dynamic is real.

---

## Where we are

**32 notebooks. 93 findings. 9 shape classes. 17 datasets across 8 unrelated domains.**

Phase 1 and 2 are complete. Phase 3 is underway: connecting shape classes to the differential equations that generate them.

The central result holds: a glacier retreating, Arctic sea ice shrinking, and global forest cover declining all produce identical 6-feature fingerprints — across three completely unrelated domains (glaciology, cryosphere, land-use). The shape class is domain-agnostic.

---

## The 9 shape classes

| # | Class | Example datasets | ODE basis |
|---|-------|-----------------|-----------|
| 1 | **burst** | COVID waves | Gaussian pulse / overdamped impulse response |
| 2 | **eco_cycle** | Lynx-hare population | Noisy oscillation with second harmonic (no clean ODE) |
| 3 | **oscillator** | Sunspot 11-year cycle | Simple harmonic ẍ + ω²x = 0 |
| 4 | **seasonal** | CO₂ seasonal residual | Forced harmonic (two-frequency superposition) |
| 5 | **trend** | CO₂ trend, CH₄ | Constant drift dx/dt = a |
| 6 | **integrated_trend** | Sea level, ocean heat | Langevin dx/dt = a + σξ |
| 7 | **irregular_osc** | VIX, ENSO, temperature | Rössler chaotic attractor (chaos ≡ noise in fingerprint space) |
| 8 | **declining_osc** | Arctic + Antarctic sea ice | Damped harmonic (green's function: exp(−γt/2)·sin(ω_d·t)) |
| 9 | **declining_monotonic** | WGMS glaciers, PIOMAS ice volume, forest cover | Langevin dx/dt = −a + σξ (mirror of integrated_trend) |

---

## Research phases

| Phase | Status | Key result |
|-------|--------|------------|
| Phase 0 — Foundation | **Complete** (nb01–13) | 6-feature fingerprint; 7 classes across 9 datasets |
| Phase 1 — Close the line | **Complete** (nb14–24) | Pairwise distances; 8 classes; VIX↔lynx-hare cross-domain match; Chronos zero-shot confirmation |
| Phase 2 — Learned embeddings | **Complete** (nb25–31) | Grokking null result; 9th class (declining_monotonic); full corpus audit |
| Phase 3 — The why | **Active** (nb32+) | ODE basis: 8/9 classes derive from a differential equation |

---

## Phase 3 findings so far

The 6-feature fingerprint is a structured projection of ODE parameter space:

- **zero_crossings ≈ f(ω)** — frequency determines ZC with Spearman ρ = 0.998
- **lag1_autocorr ≈ g(γ)** — damping determines autocorrelation (ρ = +0.943; more damping = smoother decay = higher lag1)
- **slope ≈ h(drift)** — drift rate determines slope with ρ = 1.000

The damped harmonic oscillator (*ẍ + γẋ + ω²x = 0*) transitions through shape classes as γ increases: oscillator → burst. The declining_osc class requires the green's function initial condition — a velocity kick, not a displacement. **Initial conditions determine class, not just ODE parameters.**

Deterministic chaos (Rössler attractor) and stochastic noise are fingerprint-indistinguishable: both land in irregular_osc.

---

## The corpus

17 real-world datasets, 8 unrelated domains:

| Domain | Datasets |
|--------|----------|
| Atmospheric chemistry | CO₂ seasonal, CO₂ trend, CH₄ trend |
| Cryosphere | Arctic sea ice (monthly), Antarctic sea ice, PIOMAS ice volume |
| Climate | Global temperature, ENSO, NAO, PDO, Ocean heat content |
| Finance | VIX volatility index |
| Glaciology | WGMS cumulative glacier mass balance |
| Land-use | World Bank forest cover |
| Epidemiology | COVID-19 daily cases |
| Oceanography | Global mean sea level |

---

## Navigate

- **[Findings](FINDINGS.md)** — 93 discoveries, each with claim, evidence, meaning
- **[Milestones](MILESTONES.md)** — roadmap and phase tracking
- **[Experiments](EXPERIMENTS.md)** — session-by-session log
- **[Decisions](DECISIONS.md)** — methodological choices and reasons
- **[Sessions](summary_25APR2026_nb32.md)** — most recent session summary
