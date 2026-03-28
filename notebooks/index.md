# XWorld Research Log

**Central question:** Do a glacier melting and a turtle breathing share the same numerical signature?

Cross-domain time series shape clustering experiment. The hypothesis: series from completely unrelated domains share underlying dynamic shapes, detectable by a feature fingerprint, blind to domain of origin.

> The domain is the costume. The dynamic is real.

---

## What has been found

Seven shape classes confirmed across nine datasets from seven unrelated domains. A 6-feature time-domain fingerprint (skewness, kurtosis, lag1_autocorr, zero_crossings, slope, baseline_delta) clusters them reliably. The taxonomy survives a completely different measurement frame (spectral features, ARI=0.484) — the classes are not a feature-frame artefact.

Shape similarity turns out to be a vector, not a scalar. Sunspot and COVID share a time-domain shape but differ spectrally. Neither frame alone captures the full picture.

**[20 findings documented →](FINDINGS.md)**

---

## Research phases

| Phase | Status | Focus |
|-------|--------|-------|
| Phase 0 — Foundation | **Complete** | Feature fingerprint, 7 classes, observer-independence |
| Phase 1 — Close the line | Active | Pairwise distances, new datasets, stability test |
| Phase 2 — Learned embeddings | Upcoming | Autoencoder, TimesFM/Chronos zero-shot |
| Phase 3 — The why | Future | Connect shape class to system feedback structure |

**[Full roadmap →](MILESTONES.md)**

---

## Datasets (9 across 7 domains)

| Dataset | Domain | Shape class |
|---------|--------|-------------|
| COVID first wave | Epidemiology | Burst (event-with-memory) |
| COVID second wave | Epidemiology | Burst (event-with-memory) |
| Sunspot cycle | Astrophysics | Smooth periodic |
| Lynx-hare cycle | Ecology | Oscillating predator-prey |
| Keeling (seasonal) | Atmospheric chemistry | Periodic seasonal |
| Keeling (trend) | Atmospheric chemistry | Monotone accumulation |
| Temperature anomaly | Climatology | Noisy upward drift |
| ECG segments | Physiology | Rapid oscillation |
| Streamflow | Hydrology | Moderate annual cycle |

---

## Navigate

- **[Findings](FINDINGS.md)** — cumulative discoveries, each with claim, evidence, meaning
- **[Milestones](MILESTONES.md)** — where this is going and why
- **[Experiments](EXPERIMENTS.md)** — session-by-session log
- **[Decisions](DECISIONS.md)** — methodological choices and the reasons behind them
