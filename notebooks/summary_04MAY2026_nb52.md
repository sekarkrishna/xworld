# Session Summary — 4 May 2026 — nb52

## What happened

Opened Thread 3 (audio/whale calls) with nb52: Audio Time Series — Predator-Prey Vocalizations. First non-numerical receiver test in the project.

Two timescales tested. Signal scale: synthesized three representative killer whale call types and fingerprinted their Hilbert amplitude envelopes. Ecological scale: SRKW annual census (1976–2023, CWR) and Fraser River Chinook salmon escapement (1975–2022, DFO) fingerprinted and placed in corpus space.

Also updated FINDINGS.md to add F151–F179 (from nb48–nb51), which had only been recorded in EXPERIMENTS.md.

## Key results

**Signal scale:**
- N-type (FM sweep): oscillator (d=1.573) — confirmed
- S-type (harmonic): oscillator (d=1.715) — refuted (predicted eco_cycle); smooth amplitude envelopes converge regardless of carrier
- Click train: irregular_osc (d=9.381) — refuted; taxonomically foreign (highest distance ever)

**Ecological scale:**
- SRKW (1976–2023): declining_osc (d=1.823) — NOT eco_cycle
- Chinook (1975–2022): declining_osc (d=2.082)
- Predator and prey co-classified. Neither shows eco_cycle under human pressure.

**Windowing SRKW:**
- Growth (1976–1995): trend (d=3.453)
- Crash-recovery (1996–2010): seasonal (d=3.943)
- Decline (2011–2023): declining_monotonic (d=6.705)
- All three phases have high distances — short ecological windows (<30 yr) fingerprint unreliably

## Key findings

**F187 (emergent):** Smooth amplitude envelopes converge to oscillator regardless of carrier, harmonic content, or modulation rate. The burst class requires sharp kurtosis; smooth envelopes cannot produce it.

**F188 (emergent):** The declining_osc class now clusters arctic_sea_ice, antarctic_sea_ice, SRKW, and Chinook — cryosphere and marine ecosystem decline share the same fingerprint. Declining_osc is a cross-domain marker of external stress on a periodic system.

5/7 predictions confirmed. Total findings: **188**.

## Next session

nb53: deeper audio experiment with real acoustic data, or extend the ecological analysis. Two candidates:
1. Bat echolocation call rates (insect-predator dynamics) — cleaner eco-cycle candidate
2. Humpback whale song complexity time series (vocal learning dynamics over decades)
3. Revisit echo_cycle with real lynx_hare data from the cache and compare to my hardcoded version (the hardcoded version classified as irregular_osc, not eco_cycle — a data quality issue worth resolving)
