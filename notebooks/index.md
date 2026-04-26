# XWorld Research Log

**Central question:** Do a glacier melting and a stock market spike share the same numerical signature?

Cross-domain time series shape clustering. The hypothesis: series from completely unrelated domains share underlying dynamic shapes, detectable by a 6-feature fingerprint, blind to domain of origin.

> The domain is the costume. The dynamic is real.

---

## Where we are

**38 notebooks. 115 findings. 9 shape classes. 17 datasets across 8 unrelated domains.**

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
| Phase 3 — The why | **Active** (nb32+) | ODE basis: 8/9 classes derive from a differential equation; eco_cycle has no ODE or real-world anchor |

---

## Phase 3 findings so far

The 6-feature fingerprint is a structured projection of ODE parameter space:

- **zero_crossings ≈ f(ω)** — frequency determines ZC with Spearman ρ = 0.998
- **lag1_autocorr ≈ g(γ)** — damping determines autocorrelation (ρ = +0.943; more damping = smoother decay = higher lag1)
- **slope ≈ h(drift)** — drift rate determines slope with ρ = 1.000

The damped harmonic oscillator (*ẍ + γẋ + ω²x = 0*) transitions through shape classes as γ increases: oscillator → burst. The declining_osc class requires the green's function initial condition — a velocity kick, not a displacement. **Initial conditions determine class, not just ODE parameters.**

Deterministic chaos (Rössler attractor) and stochastic noise are fingerprint-indistinguishable: both land in irregular_osc. But not all chaos does: **Lorenz x classifies as eco_cycle** (nb36, F107) — the two-lobed butterfly creates slow cross-wing oscillation (high lag1, low ZC) that lands in a completely different fingerprint region. Projection matters: the Lorenz z-axis → irregular_osc; the x-axis → eco_cycle. Three projections of the same attractor land in three different classes.

**eco_cycle has no real-world anchor.** The real lynx-hare dataset (the source of the class name) classifies as burst/declining_osc — zero eco_cycle occurrences. eco_cycle is a mathematical waveform region (negative skewness, second-harmonic distortion) that exists in the parameter space but is not produced by actual ecological oscillations. Better name: noisy_asymmetric_oscillator.

**Geometric navigation requires full information encoding.** A Blackjack experiment (nb33) confirmed that a partial structural embedding (hit-transition topology without terminal payoffs) has near-zero correlation with game-theoretic value (|ρ|=0.175). XWorld's 6-feature fingerprint is a full encoding: it captures both dynamics and boundary structure, which is why the geometric space is navigable.

**The 9 classes map to 4 structurally isolated ODE families (nb35).** The complex eigenvalue plane (decay rate α vs frequency ν) splits into 5 class regions, not 3 as predicted — seasonal appears at high frequency (ZC aliasing) and declining_monotonic at low frequency (window aliasing). The boundary between oscillator and burst slopes with frequency (Spearman ρ=−0.917), and irregular_osc is the universal noise attractor for all classes at σ≥0.25.

**Van der Pol limit cycles never reach irregular_osc (nb36, F108).** Nonlinearity alone is insufficient — stochastic forcing is required to enter the irregular_osc basin. At large μ, the relaxation oscillator period exceeds the window length → window aliasing into declining_monotonic (same mechanism as F101). The path to irregular_osc is through noise, not nonlinearity.

**Shape classes are observer-relative for periodic signals (nb37, F112).** Trend-type signals (trend, integrated_trend, declining_monotonic) are window-invariant — they classify identically regardless of how long the observation window is. All oscillatory signals are window-sensitive: a pure sinusoid traverses 6 different shape classes as the window length varies from 0.1 to 8 cycles. The thunder hypothesis is supported: for periodic dynamics, the class depends on the (signal, observer) pair, not the signal alone.

**Corpus robustness audit (nb38): 12/17 datasets classified robustly.** All four periodic classes have similar observability zones (~2.5 cycles wide). Trend/noise/burst classes are window-invariant (100% self-recognition). CO2_seasonal is the main window-awarded case (requires a 4+ year window, not 3). Arctic/Antarctic sea ice are borderline. The XWorld central claim holds for its 12 window-invariant datasets — the ODE territory is observer-independent; only the fingerprint map is observer-relative.

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

- **[Findings](FINDINGS.md)** — 115 discoveries, each with claim, evidence, meaning
- **[Milestones](MILESTONES.md)** — roadmap and phase tracking
- **[Experiments](EXPERIMENTS.md)** — session-by-session log
- **[Decisions](DECISIONS.md)** — methodological choices and reasons
- **[Sessions](summary_26APR2026_nb38.md)** — most recent session summary
