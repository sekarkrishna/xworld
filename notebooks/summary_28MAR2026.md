# XWorld — Progress Summary
**Date:** 28 March 2026
**Covers:** Session 3 — resuming after UI detour

---

## Context

Resumed from the 24 March state. The UI exploration was set aside. Back to core research.
Clean reinstall — no data files exist, notebooks are the source of truth.

Where we left off: seven shape classes confirmed across nine datasets from seven completely unrelated domains. Four open questions queued. Today begins with question 1, then question 3.

---

## Session 3 — 28 March 2026

### Direction 1: `baseline_delta` as residue detector (Notebook 11)

**The question**: does a time series end where it started, or does it leave a trace?

`baseline_delta = mean(last 10% of normalized series) − mean(first 10%)`

- Near zero: the system returned to its original state (event-without-memory)
- Large positive: the system accumulated something and didn't return (event-with-memory)

**Pre-run structural question**: is this just tracking `slope` (already in the 5-feature set), or is it genuinely independent? For smooth monotone series they should be proportional. For noisy or non-monotone series (COVID burst, temperature anomalies) they may diverge.

**Pre-run predictions**:
- COVID: baseline_delta ≈ 0 (burst rises and falls)
- keeling_trend: baseline_delta >> 0 (CO2 permanent accumulation)
- temperature: baseline_delta > 0 (warming residue, noisy)
- All cyclical datasets: baseline_delta ≈ 0

### Results

**baseline_delta predictions:** 6/9 confirmed, 3 unexpected.

| Dataset | Predicted | Actual | Status |
|---|---|---|---|
| covid_first_wave | ≈ 0 | +0.610 | UNEXPECTED |
| covid_second_wave | ≈ 0 | +0.392 | UNEXPECTED |
| keeling_trend | >> 0 | +3.111 | CONFIRMED |
| temperature | > 0 | +0.997 | CONFIRMED |
| keeling_seasonal | ≈ 0 | -0.337 | UNEXPECTED |
| sunspot_cycle | ≈ 0 | +0.055 | CONFIRMED |
| lynx_hare | ≈ 0 | -0.100 | CONFIRMED |
| ecg | ≈ 0 | -0.155 | CONFIRMED |
| streamflow | ≈ 0 | +0.194 | CONFIRMED |

**The most important finding: COVID is not event-without-memory.**

slope ≈ 0 but baseline_delta = +0.610. These diverge. The burst did not return to its starting level — it ended 0.6 SD above it. The epidemic plateaued at a new floor. This is real: endemic transmission persisted after the first and second waves. The assumption that "burst = returns to baseline" was wrong.

**baseline_delta IS independent of slope** — COVID proves it. Zero slope, significant positive delta. For non-monotone series they measure fundamentally different things.

**keeling_trend separated from COVID — structural success:**
In 5-feature space COVID ↔ keeling_trend distance = 0.975 (nearly touching). In 6-feature space = 2.810. The 6th feature tripled the distance between the two series that were most confusable.

**Sunspot collapsed into COVID cluster — unexpected regression:**
Sunspot was its own cluster in 5-feature space. In 6-feature space it joined COVID's cluster (100% of sunspot points). Sunspot baseline_delta = 0.055 — not enough to push it out when the other 5 features are already similar (high autocorr, low zero crossings, right-skewed). The sunspot-COVID separation that existed before was fragile — it was a density artefact in 5-feature space, not a robust shape distinction.

**Clustering improved overall:** 31→22 clusters, 29.8%→25.5% noise, ARI 0.121→0.165.

**Temperature and keeling_trend did NOT merge** — still in separate clusters. The 6th feature increased their distance slightly (6.649→7.012).

**Verdict on 6th feature:** Genuinely adds information. Not redundant with slope. Tripled COVID↔keeling_trend separation. Improved overall topology. But also collapsed the sunspot cluster — introduced one regression alongside the improvements.

---

### Direction 3: Combined feature frame (Notebook 13)

**ARI: combined (0.133) < time-domain (0.165) < expected.** Combining frames did not improve on time-domain alone.

**Streamflow fixed**: dom_freq=0.0799 after removing 100-pt interpolation artefact. Streamflow now correctly groups with lynx_hare (Cluster 2: moderate dynamics with annual cycles). The fix worked.

**Sunspot collapses into COVID again** in combined frame. Combined clustering is 87% similar to time-domain (cross-ARI=0.871). The 6 time-domain features dominate the 11-feature space. Spectral separation of sunspot from COVID is overridden.

**Two shape classes are perfectly stable across all five runs** (nb11 td-5f, nb11 td-6f, nb12 spectral, nb13 spectral-fixed, nb13 combined): keeling_seasonal (100% isolated, every run) and keeling_trend (100% isolated, every run). These are the two most structurally distinct shapes in the corpus.

**Core finding from today's three notebooks:** The time-domain 6-feature set is the most efficient discriminator for this dataset composition. Spectral features add within-class noise that lowers ARI. Observer-independence holds (ARI=0.484 cross-frame), but the frames are not equally good — the time-domain frame is the better ruler for this particular corpus.

**The sunspot-COVID problem** is now the central open question. They share a time-domain fingerprint (both smooth, high-memory, right-skewed, low-oscillation) but differ spectrally (sunspot is periodic, COVID is a broadband burst). The answer to "are they the same shape?" is genuinely frame-dependent. This may be the correct finding: shape similarity is a vector, not a scalar.

### Direction 2: Observer-independence (Notebook 12)

**Cross-frame ARI: 0.484.** Observer-independence holds.

Key results:

**Sunspot separates from COVID in spectral space** — the time-domain collapse (Finding 10) was a frame limitation. Sunspot spectral_entropy = 0.081 (near-pure periodic signal). COVID spectral_entropy = 0.330 (broadband burst). L2 distance = 1.052. The shapes are genuinely different — the time-domain frame had a blind spot: both look smooth with low zero crossings, so autocorrelation and skewness couldn't separate them.

**COVID1 + COVID2 split in spectral space** — landed in adjacent clusters (C27/C26), not the same one. This is HDBSCAN over-fragmentation (37 total clusters). Their spectral profiles are nearly identical. Not a genuine shape difference.

**keeling_seasonal is the most spectrally pure signal** — entropy = 0.045, power_low = 0.9995. 100% of 68 points in one cluster. The annual CO2 cycle is the closest thing to a perfect sine wave in the dataset.

**Sunspot and keeling_seasonal are spectrally near-identical** — L2 = 0.141 (smallest inter-class distance). The two frames have inverse blind spots: time-domain confuses sunspot with COVID, spectral confuses sunspot with keeling_seasonal. Neither frame alone covers the full shape space.

**Streamflow misplaced by interpolation** — dominant_freq = 0.3533 due to 480-month series being compressed to 100 points. Annual cycle mapped to near-Nyquist frequency. Methodological limit: 100-point interpolation doesn't preserve relative frequencies across series of very different lengths.

**COVID ↔ keeling_trend**: close in spectral space (L2 = 0.328), far in 6-feature time-domain space (L2 = 2.810). The two frames disagree on this pair. baseline_delta was the key discriminator; spectral features can't see it.

**Verdict:** The shape taxonomy is real, not a feature-frame artefact. But no single frame captures it completely. The next logical step is combining both frames.

**The question**: are the 7 shape classes a property of reality, or an artefact of the specific 5-feature measurement frame? If we measure with completely different features (spectral/wavelet), do the same groupings appear?

**Plan**:
- Compute spectral features: dominant frequency, spectral entropy, power in low/mid/high bands
- Cluster independently
- Compare cluster assignments: do the same cross-domain pairings emerge?
- If keeling_seasonal still lands with a periodic class and COVID still lands with a burst class using completely different math — observer-independence holds.

---

## Key question for this session

Does the taxonomy discovered so far reflect something real about how energy moves through constrained systems — or does it reflect the choice of ruler?
