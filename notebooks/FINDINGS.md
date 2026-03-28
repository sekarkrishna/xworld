# XWorld — Findings

Cumulative record of what has been discovered, in the order it was discovered. Each finding is stated as a claim, the evidence that supports it, and what it means.

---

## Session 1–2 — 23–24 March 2026

### Finding 1: Cross-domain shape clustering works

**Claim:** Time series from completely unrelated domains cluster by dynamic shape, not by domain of origin.

**Evidence:** Nine datasets from epidemiology, astronomy, ecology, climate science, hydrology, and cardiology. After z-score normalisation and extraction of 5 shape features, HDBSCAN finds clusters that span domain boundaries. COVID first wave and second wave cluster together (confirmed, 55–67% cohesion). Temperature and lynx-hare cluster together despite being a climate anomaly record and a predator-prey population count from the 1800s.

**What it means:** The domain is the costume. The shape is real and detectable with simple math.

---

### Finding 2: "Directional" is not one shape class — skewness is the burst discriminator

**Claim:** A fast asymmetric burst and a slow symmetric climb are mathematically distinct shapes, separated primarily by skewness.

**Evidence:** COVID first wave (skewness ≈ 0.95) and Keeling CO2 trend (skewness ≈ 0.07) both have high lag1-autocorrelation (~0.95–1.0) and very low zero-crossings (~0.02). In 5-feature space they were nearly touching (L2 distance = 0.975). Skewness alone separates them: COVID rises fast and falls asymmetrically; Keeling trend rises smoothly without a return.

**What it means:** Skewness captures the asymmetry of the burst — whether energy accumulates and releases unevenly. A symmetric rise is a different physical process from an asymmetric one.

---

### Finding 3: "Periodic" is not one shape class — three periodic datasets land in three different clusters

**Claim:** Periodicity is not a single shape. Keeling seasonal, sunspot cycles, and lynx-hare are all roughly periodic but genuinely distinct shapes.

**Evidence:** In 5-feature clustering: keeling_seasonal → Cluster 0 (100%). Sunspot → own cluster. Lynx-hare → Cluster 1 with temperature. All three avoided the COVID burst cluster as predicted, but did not cluster together.

**Discriminating features:**
- Keeling seasonal: skewness = −0.16 (left-skewed), consistent 12-month rhythm
- Sunspot: skewness = +0.49 (right-skewed), ~132-month cycle, rises faster than it falls
- Lynx-hare: moderate skewness, moderate autocorr (0.68), moderate zero crossings — lands in the "moderate dynamics" region, not a "periodic" class

**What it means:** The label "periodic" describes recurrence. It says nothing about shape. The asymmetry of the cycle, the memory between cycles, and the ratio of rise to fall time all vary independently of whether something repeats.

---

### Finding 4: ECG is distinguished by kurtosis, not oscillation frequency

**Claim:** ECG heartbeat segments are isolated in feature space by extreme kurtosis (15.165), not by high zero crossings as originally assumed.

**Evidence:** ECG zero crossings = 0.078 — actually lower than keeling_seasonal (0.167) and lynx-hare (0.172). The QRS spike on a flat isoelectric baseline produces extreme kurtosis. The clustering correctly isolated ECG but for a different reason than assumed.

**What it means:** A sharp impulse on a flat baseline is a fundamentally different shape from an oscillation. Kurtosis captures the ratio of spike height to baseline flatness. The feature set found the right discriminator without being told what to look for.

---

### Finding 5: "Moderate dynamics" is a genuine shape region, not a catch-all

**Claim:** The cluster containing temperature and lynx-hare is not noise or a residual bin — it is a real shape class, confirmed by independent prediction.

**Evidence:** River streamflow was predicted before clustering to have moderate features (lag1 ≈ 0.5–0.7, zero crossings ≈ 0.15–0.25, flat kurtosis). All four features landed in range after log-transformation. Streamflow formed its own density peak adjacent to temperature/lynx-hare — same region, but slightly higher autocorrelation (0.70 vs 0.50–0.68). Two sub-classes within the moderate region, separated by memory.

**What it means:** "Moderate dynamics" means no single physical forcing dominates. Temperature, ecology, and hydrology all produce moderate-memory moderate-oscillation series — for different physical reasons, but with the same mathematical fingerprint. Catchment memory (streamflow) is slightly stronger than ecological or interannual climate memory.

---

### Finding 6: The HDBSCAN calibration finding — the measurement tool's baseline is a variable

**Claim:** The choice of clustering parameters is itself a finding, not just a technical detail.

**Evidence:** `min_cluster_size=3` produced 76 clusters and 31% noise. `min_cluster_size=8` produced coherent macro shape clusters. `min_cluster_size=15` caused temperature (26 points) to go 100% noise even when internally tight. The algorithm's definition of "enough density to count as a cluster" was the variable — not the shape of the data.

**What it means:** Any measurement of structure is partly a measurement of the tool's sensitivity. The calibration of the tool must be reported alongside the result.

---

## Session 3 — 28 March 2026

### Finding 7: COVID waves are event-with-memory — "burst returns to baseline" was wrong

**Claim:** The COVID epidemic burst did not return to its starting level. It ended at a new elevated floor. Epidemics leave a residue.

**Evidence:** baseline_delta (mean last 10% − mean first 10% of normalized series): COVID first wave = +0.610, COVID second wave = +0.392. Slope ≈ 0 for both. These two features diverge completely — slope says no directional trend; baseline_delta says the endpoint is 0.6 SD above the start. The series rises, partially falls, then plateaus.

**What it means:** The original hypothesis that a burst is "event-without-memory" was wrong for this domain. Epidemics do not fully resolve — endemic transmission persists at a new floor. More generally: whether a burst returns to baseline or settles at a new level is a real physical distinction, and baseline_delta captures it where slope cannot.

---

### Finding 8: baseline_delta is genuinely independent of slope for non-monotone series

**Claim:** baseline_delta and slope are not redundant features. They measure different things for series that are not monotone.

**Evidence:** COVID first wave: slope ≈ −0.001, baseline_delta = +0.610. Zero slope, significant positive delta. For keeling_trend (monotone): slope = +0.029, baseline_delta = +3.111 — these are proportional as expected. For COVID (non-monotone burst): they completely diverge. Per-dataset correlations confirm the pattern.

**What it means:** Slope measures the average rate of change across the full window. baseline_delta measures where the series ended relative to where it started. For a series that rises and partially falls, these are orthogonal. The 6th feature is not redundant.

---

### Finding 9: baseline_delta tripled the distance between COVID and keeling_trend

**Claim:** Adding baseline_delta as a 6th feature dramatically increased the separation between the two most confusable shape classes.

**Evidence:** L2 distance in standardized feature space:

| Pair | 5-feature | 6-feature |
|---|---|---|
| COVID ↔ keeling_trend | 0.975 | 2.810 |
| COVID ↔ temperature | 6.315 | 6.329 |
| keeling_trend ↔ temperature | 6.649 | 7.012 |

COVID and keeling_trend were nearly touching at 0.975 — the smallest inter-class distance in the taxonomy. Adding baseline_delta tripled it to 2.810.

**What it means:** The 6th feature did exactly the job it was designed for. The two series that shared high autocorrelation, low zero crossings, and low slope are now clearly separated because they have fundamentally different residue profiles (0.61 vs 3.11).

---

### Finding 10: Sunspot cycles lost their independent cluster when baseline_delta was added

**Claim:** The sunspot cluster that existed in 5-feature space was fragile — it collapsed into the COVID cluster when a 6th feature was added.

**Evidence:** In 5-feature clustering, sunspot had its own cluster. In 6-feature clustering, sunspot joined COVID's Cluster 13 (100% of sunspot points). Sunspot baseline_delta = +0.055 — close to zero, unlike COVID's +0.488 cluster mean. But the other 5 features (high autocorr, right-skewed, low zero crossings) made it too similar to COVID for the density-based algorithm to separate them.

**What it means:** The sunspot-COVID separation in 5-feature space was a density artefact — a borderline case that sat just far enough from the COVID mass to form a separate cluster under those specific parameters. This is an open question for the observer-independence test (notebook 12): if spectral features also fail to separate sunspot from COVID, the two shapes may genuinely be close.

---

### Finding 11: keeling_trend forms the most isolated cluster in the entire taxonomy

**Claim:** Permanent monotone accumulation is the most distinct shape class — no other dataset approaches it in feature space.

**Evidence:** Cluster 12 in 6-feature clustering: 100% keeling_trend (58 points), mean baseline_delta = 3.106, lag1 = 1.000, slope = 0.028, skewness ≈ 0. The cluster is pure, tight, and maximally separated from all other classes.

**What it means:** A system that only accumulates and never releases — CO2 building in the atmosphere — has a unique mathematical signature. No other natural process in this dataset produces that combination of features. Permanence is detectable.

---

---

## Session 3 continued — Notebook 12: Observer Independence

### Finding 12: Observer-independence holds — cross-frame ARI = 0.484

**Claim:** The shape taxonomy is a property of the data, not an artefact of the time-domain feature frame. A completely different measurement approach (spectral features) reproduces the same major structural groupings.

**Evidence:** 5 spectral features (dominant_freq, spectral_entropy, power_low, power_mid, power_high) computed via FFT on 1526 series. Clustered independently. Cross-frame ARI between spectral and time-domain assignments = 0.484. Well above the 0.3 meaningful-agreement threshold. 4 of 5 key structural tests passed independently.

**What it means:** The domain is the costume; the dynamic is real — and it's detectable with more than one kind of ruler. The classes aren't a mathematical hallucination produced by the choice of five time-domain statistics.

---

### Finding 13: The sunspot-COVID collapse was a frame limitation — sunspot separates in spectral space

**Claim:** Sunspot cycles and COVID waves are genuinely different shapes. Their collapse into the same cluster in 6-feature time-domain space (Finding 10) was because the time-domain features couldn't see the distinction, not because the shapes are similar.

**Evidence:** In spectral space: sunspot spectral_entropy = 0.081 (power highly concentrated — near-pure periodic signal). COVID spectral_entropy = 0.330 (more broadband — energy spread across frequencies by the rise and fall of the burst). L2 distance COVID ↔ sunspot in spectral space = 1.052. They land in different clusters.

**What it means:** A periodic signal and a one-time burst look similar when you measure autocorrelation and slope — both are smooth, both have low zero crossings. But in frequency space they're completely different: the periodic signal has a sharp spectral peak; the burst spreads its energy across many frequencies. The shape distinction is real; the time-domain frame had a blind spot.

---

### Finding 14: keeling_seasonal is the most spectrally pure signal in the dataset

**Claim:** The annual CO2 seasonal cycle is the closest thing to a perfect sine wave in the entire 9-dataset corpus.

**Evidence:** Cluster 25 in spectral clustering: 100% keeling_seasonal (68/68 points), spectral_entropy = 0.045 (lowest of any dataset), power_low = 0.9995. The 12-month atmospheric CO2 cycle driven by Northern Hemisphere photosynthesis and respiration is an extraordinarily regular signal — nearly all its power concentrated at a single frequency.

**What it means:** The biosphere has a clock. It runs at exactly 1 year, almost without variation. No other system in this dataset — not the heartbeat, not the sunspot cycle, not the predator-prey oscillation — produces as concentrated a spectral signature.

---

### Finding 15: Sunspot and keeling_seasonal look nearly identical in spectral space — the inverse problem

**Claim:** Two datasets that are well-separated in time-domain space are nearly indistinguishable in spectral space.

**Evidence:** L2 distance sunspot ↔ keeling_seasonal in spectral space = 0.141 — the smallest inter-class distance in the spectral taxonomy. Both have very low spectral entropy and near-unity power_low. In time-domain space they were clearly separated (different kurtosis, skewness, zero crossings).

**What it means:** No single feature frame separates everything cleanly. The time-domain frame separates sunspot from keeling_seasonal (they have different skewness and kurtosis profiles) but confuses sunspot with COVID. The spectral frame separates sunspot from COVID but makes sunspot and keeling_seasonal look similar. The full shape taxonomy requires both frames together. This is evidence that shape is multi-dimensional in a way that neither frame alone covers completely.

---

### Finding 16: Spectral features are sensitive to series length before interpolation — a methodological limit

**Claim:** The 100-point interpolation used before FFT does not preserve correct relative frequencies across series of very different lengths.

**Evidence:** Streamflow dominant_freq = 0.3533 — by far the highest of any dataset, pushing it into a high-frequency cluster completely disconnected from its actual dynamics. Streamflow has ~480 monthly observations. The annual cycle (period = 12 months) maps to 12/480 × 100 = 2.5 interpolated points → normalized frequency ≈ 0.4. This is correct math, but it places the annual cycle at a completely different spectral position than keeling_seasonal, which uses 12-point series where the annual cycle is at frequency = 1/12.

**What it means:** The spectral feature extraction needs length-aware frequency normalization to be fully comparable across series of different durations. The current approach is valid for comparing series of similar lengths but conflates "short series with high-frequency oscillation" with "long series with low-frequency oscillation." This is a design note for the next version of the spectral feature set.

---

---

## Session 3 continued — Notebook 13: Combined Feature Frame

### Finding 17: Combining feature frames does not improve on time-domain alone — spectral features add noise

**Claim:** For this dataset composition, the 6 time-domain features are more discriminative than either the 5 spectral features or the 11-feature combination.

**Evidence:** ARI — time-domain 6f: 0.165, spectral-fixed 5f: 0.144, combined 11f: 0.133. Combined ARI is the lowest. Cross-frame ARI combined↔td = 0.871 — the 11-feature clustering is 87% similar to the 6-feature time-domain clustering. Adding spectral features neither changed the topology meaningfully nor improved domain alignment.

**Why:** The spectral features have high within-class variance for ECG (884 segments, spectrally diverse) and COVID (202 countries, varying burst shapes). This within-class variance inflates the feature space and destabilizes the density-based clustering. The time-domain features happen to capture the class-separating structure more cleanly for this particular dataset composition.

**What it means:** Observer-independence (Finding 12) showed the classes are real. This finding clarifies that the time-domain frame is a more efficient ruler for this dataset — not that the spectral frame is wrong, but that it adds more noise than signal here. The right feature set is not always more features.

---

### Finding 18: Sunspot-COVID collapse is persistent across all time-domain-weighted frames

**Claim:** Sunspot cycles and COVID waves share a time-domain fingerprint strong enough to override spectral separation when both frames are combined.

**Evidence:** In all three runs: time-domain alone → sunspot joins COVID. Spectral alone → sunspot separates. Combined 11f → sunspot joins COVID (96% of points in Cluster 24 with COVID). The combined frame cross-ARI with time-domain = 0.871. The 6 time-domain features have more weight in the 11-dimensional space than the 5 spectral features, so the time-domain signal dominates.

**What it means:** The question "are sunspot and COVID the same shape?" has a frame-dependent answer. In the time-domain: yes — both are smooth, high-memory, right-skewed, low-oscillation signals that rise and fall. In frequency space: no — sunspot is a near-pure periodic signal; COVID is a broadband burst. They are genuinely similar in one dimension of shape and genuinely different in another. There is no single true answer; the answer depends on which aspect of shape you are measuring.

---

### Finding 19: The spectral interpolation fix correctly placed streamflow with lynx_hare

**Claim:** With the 100-point interpolation artefact removed, streamflow groups with lynx_hare (moderate dynamics), not in an isolated high-frequency bin.

**Evidence:** Fixed dominant_freq for streamflow = 0.0799 (was 0.353 in nb12). In combined clustering: Cluster 2 = 15 lynx_hare + 22 streamflow. The moderate dynamics pairing (both have annual-ish cycles, moderate memory, no trend) correctly emerges once the spectral features reflect actual signal content.

**What it means:** The spectral feature set is valid — the streamflow result in nb12 was a measurement error, not a shape finding. When correctly measured, the annual cycle in streamflow and the oscillation structure in lynx_hare look similar in frequency space, consistent with their time-domain similarity.

---

### Finding 20: keeling_seasonal and keeling_trend are the two most robustly isolated shape classes

**Claim:** The symmetric steady climb (keeling_trend) and the left-skewed annual cycle (keeling_seasonal) are perfectly isolated in every single frame tested.

**Evidence:** Across all three runs in nb13, and in nb11 and nb12:
- keeling_seasonal: 100% in one cluster, in every frame
- keeling_trend: 100% in one cluster, in every frame

No other dataset achieves this across all frames.

**What it means:** These two shapes are the most structurally distinct in the corpus. Permanent monotone accumulation (keeling_trend) and the most spectrally pure oscillation in the dataset (keeling_seasonal) are maximally separated from everything else regardless of how you hold the ruler. They represent the two extremes of the taxonomy — one never returns, one returns perfectly.

---

## Open Questions (as of 28 March 2026)

1. **The sunspot-COVID duality** — they share a time-domain fingerprint but not a spectral one. They are the same shape in one dimension and different shapes in another. The question "are they the same shape class?" has no single answer. This might be the correct finding: shape is multi-dimensional, and two series can be simultaneously similar and different depending on the axis. The right framing may be shape distance as a vector, not a scalar.

2. **Why does combining frames lower ARI?** The spectral features add within-class variance (particularly ECG and COVID) that destabilizes HDBSCAN. A weighted combination — down-weighting noisy spectral features — might recover the improvement. Or a different clustering algorithm (e.g. Gaussian mixture) that handles variable-density clusters better.

3. **What is the right number of shape classes?** It depends on the frame and the parameters. keeling_seasonal and keeling_trend are always perfectly isolated (2 stable classes). COVID + COVID2 are always together (1 stable class). Everything else is resolution-dependent. The taxonomy is not a fixed object — it is a projection of continuous shape space at a particular resolution.

4. **Sunspot and keeling_seasonal are spectrally near-identical** (L2=0.141 in nb12). Two physically unrelated periodic systems with nearly the same spectral signature. Is this a coincidence of their observation window lengths, or a genuine shape similarity at the frequency-domain level?

5. **Runner vs substrate** — is the shape in the participant or in the exchange relationship between them? Requires designing a new dataset around an interaction rather than a system variable.
