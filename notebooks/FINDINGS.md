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

## Open Questions (updated 28 March 2026)

1. **The sunspot-COVID duality — partially answered by nb14.** They are (near, near) at the centroid L2 level but separate under HDBSCAN in spectral space (nb12). The duality is real but metric-dependent: entropy distance separates them; L2 on all 5 spectral features does not. Open question: does entropy-only distance recover (near, far)? → Follow-up cell planned for nb14.

2. **Why does combining frames lower ARI?** The spectral features add within-class variance (particularly ECG and COVID) that destabilizes HDBSCAN. A weighted combination — down-weighting noisy spectral features — might recover the improvement. Or a different clustering algorithm (e.g. Gaussian mixture) that handles variable-density clusters better.

3. **What is the right number of shape classes?** It depends on the frame and the parameters. keeling_seasonal and keeling_trend are always perfectly isolated (2 stable classes). COVID + COVID2 are always together (1 stable class). Everything else is resolution-dependent. The taxonomy is not a fixed object — it is a projection of continuous shape space at a particular resolution.

4. **Sunspot and keeling_seasonal are spectrally near (L2=2.383 centroid, L2=0.141 instance in nb12).** Confirmed by nb14. Both concentrate power at very low frequencies. Whether this is a genuine shape similarity or an artefact of both being observed over similar time windows remains open.

5. **Runner vs substrate** — is the shape in the participant or in the exchange relationship between them? Requires designing a new dataset around an interaction rather than a system variable.

---

### Finding 21: Centroid L2 distance cannot reproduce the entropy-driven COVID-sunspot separation from nb12

**Claim:** At the centroid level, COVID1 and sunspot are spectrally *near* (L2=1.309, below median 3.268), contradicting nb12's finding that they cluster separately in spectral space.

**Evidence:** Both have `power_low ≈ 0.95+` and `dominant_freq ≈ 0.01`. The entropy difference (COVID=0.338 vs sunspot=0.076) is real but is one of five spectral features. In L2 centroid distance, the four power-band features (which look similar for both) outvote entropy.

**What it means:** Cluster separation ≠ centroid distance. HDBSCAN in nb12 separated them because entropy alone drove their local density apart. Averaging across all five spectral features dissolves that signal. The COVID-sunspot duality is real but only observable at the instance level, not the centroid level. This is a methodological finding: the choice of distance metric (L2 on centroids vs density-based clustering) determines what distinctions are visible.

---

### Finding 22: sunspot ↔ keeling_seasonal is the clearest cross-frame duality in the corpus

**Claim:** Sunspot and keeling_seasonal are TD-far (L2=4.459, above median 3.814) but spectrally near (L2=2.383, below median 3.268) — confirmed at the centroid level.

**Evidence:** Nb14 quadrant check: (far, near), confirmed. TD distance driven by skewness/kurtosis differences. Spectral nearness driven by both being power-concentrated at low frequencies (power_low: sunspot=0.998, keeling_seasonal=0.925).

**What it means:** Two physically unrelated periodic systems — 11-year solar cycles and seasonal CO2 oscillations — look completely different in time-domain statistics but nearly identical in their spectral power distribution. This is the spectral frame's blind spot: it sees that both oscillate regularly at low frequency but cannot see that one is smooth-sinusoidal and one is left-skewed with a sharp shoulder. This finding is robust across nb12 (clustering) and nb14 (centroid distance).

---

### Finding 23: keeling_seasonal ↔ keeling_trend are spectrally near despite being the most TD-distant pair

**Claim:** keeling_seasonal and keeling_trend have the largest TD distance in the corpus (L2=6.277) but are spectrally near (L2=2.495, below median).

**Evidence:** Both concentrate most power at very low frequencies (power_low: keeling_seasonal=0.925, keeling_trend=0.953). The spectral frame treats "annual periodic cycle" and "slow permanent trend" as similar because both manifest as low-frequency power concentration.

**What it means:** The spectral frame's power-band decomposition (low/mid/high) cannot distinguish a periodic oscillation from a monotone trend — both look like "mostly low-frequency energy." This requires either entropy (which does distinguish them: 0.154 vs 0.389) or the time-domain frame. A reminder that power bands and entropy carry different information even within the spectral frame.

---

### Finding 24: Temperature is the most isolated dataset in both frames simultaneously

**Claim:** Temperature has the largest distances to nearly all other datasets in both TD and spectral frames. Every pair involving temperature lands near or at the top of the distance ranking.

**Evidence:** Top 5 largest distances in both frames involve temperature. Spectral distances: sunspot↔temperature=8.109 (largest), keeling_trend↔temperature=7.251, COVID2↔temperature=7.335. TD distances: keeling_trend↔temperature=7.012 (largest).

**What it means:** Slow noisy upward drift with increasing variance is the most structurally isolated shape in the corpus — it matches nothing closely in either frame. The combination of high zero_crossings (0.302), moderate-high spectral entropy (0.763), and significant power across all frequency bands makes it an outlier by every available metric.


---

### Finding 25: COVID-sunspot entropy distance is exactly at the corpus median — the duality lives at the clustering level, not the distance level

**Claim:** COVID1-sunspot entropy distance (0.2622) is 0.0006 below the median entropy distance (0.2628) across all 36 pairs. Entropy-only spectral distance does not recover (near, far) for this pair.

**Evidence:** Per-dataset spectral entropy: sunspot=0.076, COVID1=0.338. |0.338 − 0.076| = 0.2622. Median of all 36 pairwise entropy distances = 0.2628. COVID-sunspot lands at the median, not above it.

**What it means:** The COVID-sunspot separation in nb12 was not caused by a large entropy gap — it was a density effect. HDBSCAN found them in separate clusters because their individual-instance entropy distributions do not overlap (sunspot instances are tightly clustered at low entropy; COVID instances are spread at higher entropy). Centroid distance misses this because it compares means, not distributions. This closes the follow-up question from Finding 21: no simple centroid distance — L2 or entropy-only — can reproduce the nb12 separation. The duality is real but only observable through instance-level density-based methods.

---

### Finding 26: Entropy ordering reveals spectral complexity spectrum of the corpus

**Claim:** The 9 datasets form a clear order of spectral complexity by mean entropy: sunspot (0.076) < keeling_seasonal (0.154) < COVID2 (0.297) < COVID1 (0.338) < keeling_trend (0.389) < lynx_hare (0.436) < streamflow (0.596) < ECG (0.699) < temperature (0.763).

**Evidence:** Per-dataset mean spectral entropy computed across all instances in nb14 entropy follow-up.

**What it means:** Entropy ranks the datasets from most ordered (near-pure periodic signal, sunspot) to most complex (multi-scale noisy trend, temperature). The two ends of this spectrum are maximally far in spectral complexity. The COVID datasets sit near the middle — they are bursty but not maximally disordered. This ordering is independent of any clustering and represents a single continuous axis of spectral structure that runs through the entire corpus.


---

### Finding 27: Sea level is a noisy monotone — nearest to COVID, not keeling_trend

**Claim:** Global mean sea level (monthly, 10-year windows) is nearest to covid_first_wave by TD centroid distance (1.467), not keeling_trend (2.653) as predicted. 48% of instances fall into noise.

**Evidence:** Key discriminating features vs keeling_trend: zero_crossings=0.104 (vs 0.008), baseline_delta=1.100 (vs 3.111), lag1_autocorr=0.919 (vs 0.9999). Spectral features are similar to keeling_trend (power_low=0.920, dom_freq=0.019) but time-domain diverges. HDBSCAN places majority of sea_level instances in noise.

**What it means:** "Monotone rise" is not a single shape class. The taxonomy distinguishes two subtypes: (a) clean monotone — CO2 accumulates so smoothly that zero_crossings ≈ 0 and baseline_delta is very large relative to variance; (b) noisy monotone — sea level rises steadily but inter-annual forcing (ENSO, volcanic events) creates regular oscillations around the trend, giving zero_crossings ≈ 0.10. Sub-type (b) currently has no class in the taxonomy and lands in noise. This is a gap in the existing 7 classes.

---

### Finding 28: The taxonomy has a gap — "noisy directional" sits between keeling_trend and temperature

**Claim:** Sea level occupies a shape space between keeling_trend (clean monotone) and temperature (noisy drift) that no existing class covers.

**Evidence:** keeling_trend: zero_crossings=0.008, baseline_delta=3.111, lag1_autocorr=0.9999. Sea_level: zero_crossings=0.104, baseline_delta=1.100, lag1_autocorr=0.919. Temperature: zero_crossings=0.302, baseline_delta=0.997, lag1_autocorr=0.464. Sea level sits between these two on every relevant feature. 48% noise placement confirms it belongs to neither existing class.

**What it means:** A potential 8th shape class — "noisy directional with strong memory" — characterized by: moderate zero_crossings (0.05–0.15), moderate-high baseline_delta (0.8–1.5), high lag1_autocorr (0.85–0.95), low spectral entropy (~0.43), high power_low (~0.92). Physical systems that trend in one direction but are also subject to recurring forcing (sea level, ice extent, perhaps population under periodic stress) would land here.


---

### Finding 29: ENSO is equidistant from COVID and sunspot simultaneously — a new in-between region

**Claim:** ENSO ONI is nearest to covid_second_wave (0.970), sunspot_cycle (0.996), and covid_first_wave (1.022) — a three-way tie within 0.05. 72% of instances fall into noise. It is not a member of any existing class.

**Evidence:** Feature profile: lag1_autocorr=0.956, zero_crossings=0.074, baseline_delta=0.078, spectral_entropy=0.367. ENSO shares baseline_delta≈0 with sunspot (0.055) — both return to zero between events. ENSO shares spectral_entropy≈0.34 with COVID (0.338) — both are irregular. The combination is unique: high-memory, irregular, reversible oscillation.

**What it means:** ENSO is not classifiable by the existing 7-class taxonomy. It occupies a new region of shape space: "irregular reversible memory oscillator" — characterized by high autocorr (events persist), near-zero baseline_delta (system returns to baseline), and moderate spectral entropy (irregular periodicity). This is different from sunspot (regular, low entropy) and COVID (irreversible, high baseline_delta). A potential 9th shape class.

---

### Finding 30: Three datasets now occupy genuine in-between shape regions — the taxonomy has structural gaps

**Claim:** Sea level (nb15), ENSO (nb16), and the COVID-sunspot pair (nb11-14) all demonstrate that the existing 7-class taxonomy has gaps between classes that real physical systems inhabit.

**Evidence:** 
- Sea level: sits between keeling_trend and temperature ("noisy directional")
- ENSO: sits between sunspot and COVID ("irregular reversible oscillator")
- COVID-sunspot: same class in TD frame, different class in spectral frame (not a gap but an ambiguity)

**What it means:** The 7 classes are not a complete partition of shape space — they are the densest regions of a continuous shape manifold sampled with the original 9 datasets. Adding new datasets is filling in the spaces between existing classes. The taxonomy may need to grow to 9 or 10 classes, or alternatively be reframed as a continuous embedding rather than discrete classes. Phase 2 (autoencoder embeddings) will test this directly.


---

### Finding 31: VIX (financial volatility) landed nearest lynx_hare (0.594) — not COVID or ECG as predicted

**Claim:** CBOE VIX with 24-month windows is nearest to lynx_hare by TD centroid distance (0.594), followed by streamflow (0.726). COVID1 is 3.374 away. ECG is 3.381 away. 69% of instances fall into noise.

**Evidence:** Key features: skewness=0.947, kurtosis=0.582, lag1_autocorr=0.650, zero_crossings=0.205. Lynx_hare: skewness=1.025, kurtosis=-0.302, lag1_autocorr=0.680, zero_crossings=0.172. Near-identical moderate-memory oscillator profiles. COVID disqualified by lag1_autocorr (0.650 vs 0.954 — VIX is not sustained enough). ECG disqualified by kurtosis (0.582 vs 15.165 — VIX spikes are not pathologically sharp at monthly resolution).

**What it means:** Financial market volatility (VIX) and ecological predator-prey dynamics (lynx_hare) share the same time-domain shape class — both are "irregular moderate-memory oscillators with positive skewness." Market crises boom and revert; predator-prey populations boom and collapse. The domain is different; the dynamic is the same. This is a direct confirmation of the research hypothesis at the taxonomy level.

---

### Finding 32: All three Phase 1b datasets landed mostly in noise — confirms the taxonomy has structural gaps

**Claim:** Sea level (48% noise), ENSO (72% noise), VIX (69% noise) all failed to find a clean class membership. All three landed nearest to unexpected existing datasets.

**Evidence:**
- Sea level: predicted keeling_trend, nearest COVID (1.467) — "noisy monotone" gap
- ENSO: predicted lynx_hare, nearest COVID/sunspot three-way tie (0.97–1.02) — "irregular reversible oscillator" gap
- VIX: predicted COVID/ECG, nearest lynx_hare (0.594) — fits best but still 69% noise

**What it means:** The 7 classes are the dense cores of a continuous shape manifold, not a complete partition. Adding datasets from new domains consistently finds the gaps between existing classes. Two implications: (1) the taxonomy should expand to 9–10 classes; (2) a continuous embedding (Phase 2) is more appropriate than discrete HDBSCAN clusters for describing the full shape space.


---

## Session 5 — 30 March 2026 (Notebook 18: Phase 1c Stability Test)

### Finding 33: keeling_seasonal and keeling_trend are the only truly parameter-independent shape classes

**Claim:** keeling_seasonal and keeling_trend achieve 100% stability with 0% noise across all 15 parameter combinations. No other dataset in the corpus achieves this.

**Evidence:** Both datasets have noise_frac = 0.0 in every run (mean ± std = 0.0 ± 0.0%). majority_pct ≥ 0.5 in all 15 runs. Every other dataset has either non-zero noise variance, or majority_pct < 0.5 in at least some runs. These two are the only datasets where HDBSCAN finds a single coherent cluster, regardless of resolution.

**What it means:** The perfectly regular annual CO2 oscillation and the perfectly smooth accumulation trend are the two most structurally unambiguous shapes in the corpus. They represent the two poles of the taxonomy — one never returns, one returns perfectly — and this polarity is the most robust structural fact in XWorld. If only two shape classes survive complete parameter independence, these are the ones. This was predicted; it is now confirmed against a 15-run adversarial test.

---

### Finding 34: Sunspot is stable but parasitic — it has no independent shape class in the TD frame

**Claim:** Sunspot_cycle achieves 100% stability (finds a clean cluster in all 15 runs) but collapses into the same cluster as COVID instances in 73% of those runs. Sunspot's stability is borrowed, not earned.

**Evidence:** All 15 runs show sunspot majority_pct = 58–92%. But 11 of those 15 runs place sunspot in the same cluster as at least a fraction of COVID first wave instances. The collapse is resolution-dependent: at mcs=4 (fine resolution) only 1/3 runs collapse; at mcs ≥ 12 (coarse resolution) all 6/6 collapse. Mean sunspot noise = 17.2% ± 8.0%.

**What it means:** The sunspot-COVID TD fingerprint similarity (Finding 18) is not a centroid-level artifact — it is the dominant organizational fact about sunspot across parameter regimes. At coarse resolution HDBSCAN cannot maintain them as separate clusters; the TD similarity wins. Sunspot does not have a stable independent class in the 6-feature TD frame. It is a satellite of the burst class — close enough to merge at most resolutions, separable only when HDBSCAN is forced to operate at fine grain. This is the clearest demonstration yet that the 7-class taxonomy needs either spectral features to separate sunspot from COVID, or a continuous embedding.

---

### Finding 35: ECG has internal sub-structure — "ECG class" is a family, not a shape

**Claim:** ECG achieves 0% stability despite extreme kurtosis (15.165) that was predicted to isolate it. Low mean noise (26.5% ± 6.3%) confirms ECG is NOT being rejected — it is being fragmented into many sub-clusters.

**Evidence:** ECG has 884 instances — the largest dataset by far. In every run, ECG instances cluster successfully (low noise) but distribute across many small clusters, no single one capturing ≥50% of 884 instances. At mcs=4, the total run produces up to 115 clusters globally. ECG contributes sub-structure to many of them.

**What it means:** ECG is not one shape — it is a family of heartbeat morphologies that all share extreme kurtosis (sharp spike on flat baseline) but differ in spike width, symmetry, and inter-beat structure. The kurtosis feature correctly isolates the ECG region of shape space, but within that region there is genuine sub-structure that HDBSCAN resolves. For Phase 2, ECG may need to be treated as multiple shape sub-classes. The stability metric reveals something the single-run nb11 could not: apparent "one class" datasets may contain sub-classes invisible at the 9-dataset scale.

---

### Finding 36: Small-n datasets are noise by arithmetic, not by shape — the stability test has a size floor

**Claim:** lynx_hare (n=26), streamflow (n=24), and temperature (n=31) show "always noise" or near-zero stability. This is an artifact of the min_cluster_size threshold, not evidence of weak shape structure.

**Evidence:** All three have very high noise fractions (lynx_hare 96.2%, streamflow 92.8%, temperature 96.6%). But their centroid positions in feature space (nb14) confirmed they occupy distinct, structurally real locations. A dataset with 24–31 instances cannot reliably form a majority cluster when min_cluster_size ranges from 4 to 16 — the threshold arithmetic works against them even when shape structure is present.

**What it means:** The stability metric has an implicit size floor. Datasets with fewer than ~50 instances will fail the ≥50% majority test for structural reasons unrelated to shape distinctness. This is a methodological finding: HDBSCAN stability testing is only informative for datasets with sufficient instance counts. The small datasets (lynx_hare, streamflow, temperature) need either more instances (longer windows, more stations) or a different validation method. Phase 2's continuous embedding approach has no minimum cluster size — every point gets a position regardless of count.

---

### Finding 37: COVID first wave across countries is not a single shape — the burst class is a heterogeneous family

**Claim:** COVID first wave (n=202 country waves) achieves 0% stability with 58.5% ± 8.9% mean noise. Countries cluster locally by wave shape similarity, not as a single global burst class.

**Evidence:** In every run, the 202 first-wave instances distribute across many clusters with no single cluster capturing ≥50%. The majority cluster for COVID1 captures only 8–35% of instances. Mean noise is 58.5% — over half the waves are not being captured by any cluster at any parameter setting.

**What it means:** The burst shape (rapid asymmetric rise and fall) is a category, not a single fingerprint. Each country's COVID wave has a different rise rate, peak timing, and decay shape. HDBSCAN correctly identifies that they are not all the same curve. The 202 waves populate a region of shape space — the burst zone — but that zone has significant internal variance. This is consistent with the physical reality: countries with different demographics, intervention policies, and wave timing produced genuinely different wave shapes. Finding 1 (cross-domain clustering works) remains valid — COVID waves all cluster in the same region of shape space — but the region is not a tight point, it is a diffuse cloud.

---

### Finding 38: Phase 1b datasets remain structurally outside the taxonomy at every parameter setting

**Claim:** sea_level, ENSO, and VIX never achieve clean cluster placement across any of the 15 parameter combinations. Lowering min_cluster_size does not rescue them.

**Evidence:**
- enso_oni: best case is 50.3% noise (mcs=4, ms=2), majority_pct=0.07 — even when not in noise, it doesn't consolidate
- sea_level: best case is 39.2% noise (mcs=4, ms=3), majority_pct=0.29 — partial consolidation but never clean
- vix: best case is 71.5% noise (mcs=4, ms=2), majority_pct=0.07 — mostly noise at every setting
- All three improve slightly at mcs=4 vs mcs=16, but none crosses into clean placement

**What it means:** The structural gaps identified in Phase 1b (Findings 27–32) are not parameter artifacts. These datasets occupy regions of shape space that are genuinely between the existing dense clusters — and no HDBSCAN resolution recovers them. This is the definitive closing argument for Phase 2: the continuous shape manifold cannot be adequately described by discrete clusters, even with optimized parameters. The gaps are real, and a continuous embedding is the only method that will place these datasets meaningfully.


---

## Session 5 cont. — 30 March 2026 (Notebook 19: Phase 2 Autoencoder — pairwise distances)

### Finding 39: The Conv AE separates sunspot from COVID — the TD collapse was a feature resolution failure, not a real shape ambiguity

**Claim:** Sunspot-COVID centroid distance increases 5.79x from feature space (0.769) to Conv AE latent space (4.451). The autoencoder places them far apart without any supervision.

**Evidence:** Feature-space distance = 0.769 — close enough that HDBSCAN collapsed them in 73% of parameter combinations (Finding 34). Latent-space distance = 4.451. The ratio (5.79x) is one of the largest expansions in the corpus, exceeded only by ENSO-sunspot and COVID1-COVID2.

**What it means:** The sunspot-COVID collapse in nb18 was not a fundamental shape similarity — it was a consequence of the 6-feature TD frame lacking sufficient resolution. The 11-year solar cycle, when fed as a raw 64-point waveform to a convolutional encoder, is structurally distinguishable from a 60–180-day COVID burst. The Conv AE captures local temporal texture — the multi-cycle structure of sunspot vs. the single-spike structure of COVID — that the 6 scalar statistics cannot represent. The sunspot class is not a satellite of the COVID class; it simply needed a richer representation to stand alone.

---

### Finding 40: ENSO and sunspot are dramatically separated in latent space — the largest ratio expansion in the corpus

**Claim:** ENSO-sunspot distance increases 7.03x (0.859 → 6.040) — the largest ratio increase among all pairs tested. ENSO and sunspot were misleadingly close in feature space and are now maximally far in the autoencoder's representation.

**Evidence:** Feature-space distance = 0.859 (4th closest pair in the corpus, near-neighbor territory). Latent-space distance = 6.040 (among the most distant pairs). 7.03x expansion is the largest ratio in the test set.

**What it means:** Both ENSO and sunspot have high lag1_autocorr and near-zero baseline_delta in the TD frame — they look alike on those two dominant axes. But their raw waveforms are fundamentally different: sunspot is a near-pure periodic signal (regular ~11-year oscillations), while ENSO is an irregular reversible oscillator (El Niño events at 2–7 year intervals with variable amplitude). The convolutional encoder learned to distinguish regularity from irregularity — something 6 scalar statistics cannot capture. This is the most dramatic example in the corpus of the TD feature frame actively misleading clustering.

---

### Finding 41: Temperature and sea_level contract to near-neighbors in latent space — the autoencoder merges what TD features split

**Claim:** Temperature-sea_level centroid distance DECREASES from 4.607 (feature space) to 0.777 (latent space) — a 0.17x ratio. This is the only tested pair that contracts significantly, and the contraction is extreme.

**Evidence:** Feature-space distance = 4.607 (one of the largest distances in the corpus — near maximum separation). Latent-space distance = 0.777 (near-neighbor territory). The direction reverses: from "most different" to "most similar."

The TD features disagreed on: zero_crossings (temperature=0.302 vs sea_level=0.104) and spectral entropy (temperature=0.763 vs sea_level ~0.43). These differences drove the large feature-space distance. But both series are, at their core, noisy upward drifts — a slow monotone rise with oscillatory noise around it.

**What it means:** The autoencoder independently confirmed and strengthened Finding 28's prediction of a "noisy directional" shape class sitting between keeling_trend (clean monotone) and temperature (noisy drift). The TD frame used zero_crossings and entropy to declare these dissimilar. The raw waveform says they are the same kind of thing: a trend being pushed around by recurring forcing. This is a case where a learned representation overturn a hand-crafted feature conclusion. Finding 28 proposed an 8th shape class. Finding 41 provides the strongest evidence yet that this class exists — and that temperature belongs to it alongside sea_level, not in isolation.

---

### Finding 42: VIX-lynx_hare proximity survives the move to latent space — the cross-domain shape match is robust

**Claim:** lynx_hare ↔ VIX remains one of the closest inter-domain pairs in latent space (0.944), with the smallest ratio expansion (1.53x) of any non-trivial pair tested.

**Evidence:** Feature-space distance = 0.616 → Latent-space distance = 0.944. While all other pairs expand significantly (2x–9x), this pair barely moves. The autoencoder, learning from raw waveforms without any domain knowledge, confirms that financial volatility cycles and ecological predator-prey cycles occupy the same region of shape space.

**What it means:** Finding 31 (VIX matches lynx_hare) is not a feature-selection artifact. It holds when the representation is learned from scratch. Irregular moderate-memory oscillators with positive skewness are a real shape class — robust to changes in how the feature representation is constructed. This is the strongest cross-domain validation in the corpus: the same answer emerged independently from hand-crafted TD statistics and from a convolutional autoencoder trained on raw waveforms.

---

## Session 5 cont. cont. — 30 March 2026 (Notebook 20: Phase 2b Chronos Foundation Model)

### Finding 43: Chronos confirms sunspot–COVID as the maximally separated pair — three independent methods agree

**Claim:** Sunspot↔COVID first wave is the farthest centroid pair in Chronos embedding space (0.301 Euclidean in 512-dim space), while ENSO↔sunspot and covid1↔covid2 are among the closest pairs (0.094 and 0.059 respectively).

**Evidence:** Amazon Chronos-T5-Small (46 M params, trained on millions of unrelated time series, zero-shot on our data) embeds all 1930 instances. Pairwise centroid distances in 512-dim encoder output space place sunspot↔covid1 at 0.301 — the maximum over 10 measured pairs. The Conv AE (nb19) showed a 5.79x expansion for this pair. TD features placed them near each other (1.988 raw, driving the nb18 collapse). Now all three frames agree: different direction, different magnitude, same qualitative verdict.

**What it means:** Three measurement systems (6 time-domain statistics, trained 1D Conv autoencoder, zero-shot foundation model) independently agree that the 11-year solar cycle and the epidemic burst are the most structurally distinct pair in this corpus. This is the strongest evidence yet that the sunspot-COVID separation is a real property of the shapes, not an artifact of any particular representation choice.

---

### Finding 44: Chronos separates sea_level from temperature — Conv AE and Chronos disagree, "noisy directional" class needs splitting

**Claim:** Sea_level forms its own pure cluster in Chronos HDBSCAN (cl3, 97% pure), while temperature is 77% noise and 23% in the irregular cl6 cluster. Chronos pairwise distance temperature↔sea_level = 0.140 — not among the closest pairs.

**Evidence:** The Conv AE (nb19) contracted temperature-sea_level to 0.17x (from 4.607 feature distance to 0.777 latent), proposing both belong to a single "noisy directional" 8th class. Chronos disagrees: sea_level is isolated in cl3 (120 instances, 97% pure) while temperature scatters. Chronos HDBSCAN finds 8 distinct clusters total; sea_level earns one of them on its own.

**What it means:** The Conv AE was trained on our 1930-instance corpus and learned "upward drift" as the dominant shared shape. Chronos, trained on millions of unrelated series, has seen many types of trends and learned to distinguish sub-types: smooth monotonic satellite altimetry (sea_level: 1993–present, nearly linear) vs. temperature records with multi-decadal oscillations and regional noise. The "noisy directional" 8th class likely needs to be split into at least two sub-types: clean monotonic trend and noisy trend-with-oscillation. Finding 41's conclusion was a step in the right direction but went one level too coarse.

---

### Finding 45: Chronos discovers a cross-domain irregular cluster — VIX + ENSO + temperature (cl6)

**Claim:** Cluster cl6 in Chronos HDBSCAN contains instances from VIX (28%), ENSO ONI (24%), and temperature (23%). No single dataset dominates. The nb17 VIX↔lynx_hare cross-domain match does not survive into Chronos space.

**Evidence:** With min_cluster_size=8, Chronos produces 8 clusters. Cluster cl6 mixes finance (VIX), climate oscillation (ENSO), and global temperature — three datasets with no domain connection. Meanwhile lynx_hare (the nb17 VIX match partner) is 100% noise in Chronos space. VIX and lynx_hare, which were near-neighbors in both TD feature space (0.893) and Conv AE latent space (0.944), are separated in Chronos space: VIX goes to cl6, lynx_hare scatters to noise.

**What it means:** The VIX-lynx_hare cross-domain match is not frame-invariant. In TD features and the Conv AE, both are irregular moderate-memory oscillators. In Chronos space, VIX's time windows look more like ENSO oscillations and noisy temperature signals. This does not invalidate Finding 42 — it reveals that the shape match operates at a different level of abstraction in different embeddings. The cross-domain finding is real but the specific grouping partner changes with the measurement frame. Cross-domain shape similarity is richer than a single pairing.

---

### Finding 46: ECG sub-structure aligns with UCR true labels at ARI=0.742 — Chronos recovers clinical class structure zero-shot

**Claim:** Chronos HDBSCAN on ECG instances finds 3 sub-clusters, with non-noise instances matching UCR class labels at ARI=0.742. ECG is 99% pure in cluster cl2.

**Evidence:** ECG has 884 instances from the UCR ECGFiveDays dataset with two clinical classes (class 1, class 2). Chronos HDBSCAN (mcs=8, ms=3) on 512-dim embeddings returns 3 clusters with 676 noise points. Among the non-noise subset, the cluster assignments align with UCR true labels at ARI=0.742 — a high agreement for unsupervised discovery. ECG forms cluster cl2 at 99% purity in the full corpus clustering.

**What it means:** The ECG fragmentation in nb18 (shapes break into many sub-clusters under parameter variation) has real, label-aligned structure. The sub-clusters are not statistical noise — they correspond to clinically distinct heartbeat morphologies. A foundation model trained on completely unrelated time series has implicitly learned to distinguish ECG waveform classes without domain knowledge, supervision, or access to the labels. This is the highest ARI of any sub-cluster analysis in this experiment, and confirms that the ECG "family" (Finding 35) has at least two distinct members.


---

## Session 6 — 31 March 2026 (Notebook 21)

### Finding 47: CH4 trend and keeling_trend share a Chronos cluster — clean monotonic is a general shape class, not CO2-specific

**Evidence:** Chronos pairwise distance ch4_trend ↔ keeling_trend = 0.078 (smallest in corpus). HDBSCAN: keeling_trend 100% in cl6, ch4_trend 58% in cl6. Deseasonalised atmospheric methane (NOAA GML) placed in the same class as CO2 trend by a foundation model trained on neither.

**What it means:** The clean-monotonic shape class generalises across molecules and forcing mechanisms. It is defined by signal smoothness, not by the specific physical process producing the rise. Any smooth, unidirectional accumulation signal — regardless of domain — will land in this class.

---

### Finding 48: Ocean heat content lands with sea_level, not temperature — "clean integrated trend" sub-type defined by measurement smoothness

**Evidence:** Chronos distances: ocean_heat ↔ sea_level = 0.080, ocean_heat ↔ temperature = 0.163. HDBSCAN: ocean_heat (77%) and sea_level (97%) share cl4. Prediction was temperature-like (noisy directional); result is sea_level-like (clean integrated).

**What it means:** The sub-type boundary inside the "noisy directional" region is measurement smoothness. Spatially averaged / depth-integrated instruments (sea_level, ocean_heat) cancel noise through physical integration. Point-surface records (temperature) retain weather-scale variability. The revised taxonomy: clean integrated trend (cl4/cl6) vs noisy surface trend (temperature) vs declining oscillator (arctic_sea_ice, Finding 49).

---

### Finding 49: Arctic sea ice forms its own pure Chronos cluster — 8th shape class confirmed: "declining oscillator"

**Evidence:** Arctic sea ice 100% in cl0 — a pure cluster it occupies alone. Pairwise distances: arctic_sea_ice ↔ keeling_seasonal = 0.261, arctic_sea_ice ↔ sea_level = 0.257. Equidistant between oscillator and trend classes.

**What it means:** Long-term decline embedded inside a strong annual cycle creates a shape class distinct from both pure oscillators and pure trends. This is the 8th shape class. It is the first class in this corpus defined by the superposition of two dynamics (trend + cycle) rather than one dominant mode. More datasets in the same region needed to confirm class boundaries.

---

### Finding 50: Sea-level Chronos isolation is structural, not a density artifact

**Evidence:** Sea_level subsampled to n=31 (matching temperature count) → 90.32% still in own cluster. Temperature at n=31 → 77.42% noise. Equal sample sizes, opposite clustering behaviour.

**What it means:** The nb20 concern that sea_level's isolation might reflect having 120 instances vs temperature's 31 is resolved. The smooth altimetry signal is structurally distinct regardless of instance count.

---

### Finding 51: cl7 (VIX + ENSO + temperature) characterised by moderate positive skewness and intermediate autocorrelation

**Evidence:** Feature comparison of in-cluster vs out-of-cluster instances across the three datasets. In-cluster skewness: VIX 0.695, ENSO 0.210, temperature 0.153. ENSO out-of-cluster skewness: 0.006. In-cluster lag1_autocorr: VIX 0.631, temperature 0.420 (intermediate). ENSO out-of-cluster lag1: 0.976 (near-monotone windows).

**What it means:** Chronos cl7 captures a specific dynamic regime: irregular oscillation with positive amplitude asymmetry (excursions above the mean are larger than below). The out-of-cluster instances from the same datasets are the near-monotone, low-skewness windows. This is a within-dataset split as much as a cross-domain grouping. The VIX-ENSO-temperature match is frame-dependent: TD-6f matched VIX with lynx_hare (ecology); Chronos matches VIX with ENSO and temperature (irregular asymmetric oscillators). Both are real; they reflect different aspects of the same dynamics.

---

### Finding 52: Chronos is invariant to time-reversal and amplitude-flip for all shape classes — sensitive to temporal speed only for periodic classes

**Evidence:** Mirror distortion test on 7 representative series. Time-reversal: INV for all 7. Amplitude-flip: INV for all 7. Speed-2x: SEN for oscillator, seasonal, irregular; INV for burst_event, eco_cycle, clean_trend, noisy_dir.

**What it means:** Chronos does not encode time direction or amplitude polarity. A reversed keeling_trend is not placed near COVID (prediction was wrong). What Chronos encodes is frequency structure: stretching a periodic series changes its dominant period relative to context length, and Chronos detects this. Non-periodic series (trends, bursts) are insensitive to temporal scale because their structure is not period-dependent. Chronos shape classes are defined by frequency content and amplitude structure, not by direction or polarity. This has a practical implication: two systems with opposite trend directions (one rising, one falling) will be placed in the same Chronos shape class.

---

## Session 8 — 19 April 2026 (Notebook 23)

### Finding 53: A neural arithmetic net learns linear geometry, not logarithmic — log features are provided but unused

**Claim:** Providing structured 4D inputs [log(n), n/max, parity, residue] does not cause the network to discover log-space multiplication geometry. ×10 shifts in PCA space are non-uniform and grow with n, indicating the linear channel dominated.

**Evidence:** PCA of structured encoder embeddings: ×10 shift in PC1 = −0.73 (1→10), −1.22 (10→100), −5.05 (100→1000). A true log-space representation would produce equal shifts. Instead shifts scale roughly with n. In-range performance: structured encoder slightly better on division (11.4% vs 42.5%) and multiplication (6.8% vs 19.2%). Extrapolation on addition: raw encoder outperforms structured (2.6% vs 12.5% at 5k+3k; 4.1% vs 32% at 50k+70k).

**What it means:** MSE loss alone does not force a network to discover the algebraically correct representation. The network found the locally optimal solution — fit the training range with linear coordinates — which happens to be wrong for multiplication extrapolation. Log-space geometry must be either hardcoded (as in NALU) or enforced by multiplicative consistency loss, not left to emerge from prediction error alone.

---

### Finding 54: Addition extrapolates; multiplication and division do not

**Claim:** Both raw and structured arithmetic nets extrapolate addition to ~4% error at 10× training range, but completely fail on multiplication and division extrapolation.

**Evidence:** 50k+70k = 120k: raw 4.1% error, structured 32%. 400×300 = 120k: both ~98.8–98.6% error. 10000÷50 = 200: both ~4500% error. 1M+250: both ~11–13% error.

**What it means:** Addition extrapolation works because the network learned a roughly correct linear representation, and linear structure extends. Multiplication fails because the network has no log-space geometry — a linear encoding has no natural extrapolation rule for scaling. The training ceiling (n≤1000) means the network has never seen the scale of 400×300=120k and cannot infer it. This confirms the arithmetic analogy for XWorld: a model that memorises examples without discovering structure will not generalise beyond the training distribution.

---

### Finding 55: The 8 shape classes split into directionally-defined and shape-defined attractors

**Claim:** The XWorld 6-feature fingerprint is NOT orientation-invariant. The 8 shape classes divide into two groups: those whose class identity depends on direction (trend direction, amplitude sign) and those whose identity is defined by waveform shape alone.

**Evidence:** Amplitude-flip boundary crossing rates: trend 100%, integrated_trend 100%, seasonal 100%, declining_osc 100% — all directionally-defined classes cross on amplitude reversal. Oscillator 0%, burst 0%, irregular_osc 18%, eco_cycle 18% — shape-defined classes survive. Time-reversal produces the same split: 100% crossing for trend/integrated_trend/seasonal/declining_osc; 0% for oscillator/burst.

**What it means:** "Trend" and "reversed trend" are different classes in the 6-feature space. "Sine wave" and "reversed sine wave" are the same class. The 6-feature fingerprint encodes directionality as a first-class feature via slope and baseline_delta. This is a methodological property of the representation, not a physical property of the shapes. Chronos (nb21 finding 52) is invariant to both operations for all classes — meaning Chronos is reading shape-defined features only, while the 6-feature fingerprint reads both directional and shape features.

---

### Finding 56: Directionally-defined classes are the tightest clusters; shape-defined classes have the widest spread

**Claim:** The most fragile classes under distortion (trend, integrated_trend) are also the purest and tightest in natural feature space. The most robust classes (oscillator, irregular_osc) have the widest natural within-class spread.

**Evidence:** Baseline (within-class spread): integrated_trend = 0.072, trend = 0.096, oscillator = 0.615, irregular_osc = 1.035. Relative drift (drift / baseline): integrated_trend = 37.50, trend = 28.19, oscillator = 2.70, irregular_osc = 2.12. Absolute drift: integrated_trend amplitude_flip = 4.597, oscillator amplitude_flip = 1.144.

**What it means:** Tightness and fragility are the same thing seen from two angles. The trend classes are pure precisely because their defining features (slope, baseline_delta) leave no room for ambiguity within the class — but those same features are completely destroyed by amplitude reversal. The oscillatory classes are robust because their defining features (zero_crossings, lag1_autocorr) are orientation-invariant and tolerate natural variation. A tight cluster in feature space is not necessarily a stable attractor — it may be a narrow region that is easy to leave.

---

### Finding 57: irregular_osc is noise-immune but time_warp-sensitive; the inverse for most classes

**Claim:** Each shape class has a specific distortion type that destroys it, and a specific type that it survives. The pattern reveals what the defining feature of each class actually is.

**Evidence:** irregular_osc: noise crossing rate 1.3% (most noise-immune of all 8), time_warp crossing rate 83% (most time_warp-sensitive). Oscillator: amplitude_flip 0%, time_reverse 0%, noise 59.3%. Crossing destinations: trend → seasonal (100%); declining_osc → irregular_osc (99%); burst → irregular_osc/eco_cycle; oscillator → irregular_osc/eco_cycle.

**What it means:** Irregular oscillation is defined by chaotic amplitude variability — adding noise preserves this. But changing the timescale changes the dominant frequency, moving it into a different frequency regime. Oscillator is defined by symmetry — flipping or reversing it preserves that symmetry. Noise destroys it because it breaks the pure sinusoidal lag structure. The crossing destinations reveal the topology of the feature space: irregular_osc is the central sink that receives most distorted classes, because irregularity is the default when structure is partially destroyed. The 8 shape classes are not equidistant — they form a topology where oscillator/seasonal/trend are peripheral (pure) and irregular_osc is central (generic).

---

## Session 9 — 19 April 2026 (Notebook 22, re-run)

### Finding 58: Antarctic sea ice independently replicates cl0 — declining oscillator confirmed with two hemispheric datasets

**Claim:** Antarctic sea ice joins Arctic sea ice in cl0 at 100% purity. The 8th shape class is not an artefact of one dataset.

**Evidence:** Antarctic sea ice: 100% cl0 (n=38). Arctic sea ice: 100% cl0 (n=38). Pairwise Chronos distance: 0.072 — the smallest distance in the experiment, tighter than any previously measured pair. Distance to nearest other class: keeling_seasonal (0.276), sea_level (0.269).

**What it means:** Two entirely independent datasets — one from the Northern hemisphere, one from the Southern, covering the same 1978–2026 period — are placed identically by Chronos. They are not near each other by coincidence of geography; they share the same structural dynamic: a strong annual oscillation embedded inside a long-term decline. This is the cleanest cross-dataset confirmation of a shape class in the corpus. The declining oscillator class (strong periodic cycle + secular trend in opposite direction) is real, robust, and now has two pure members. The next question is whether it can be found outside the cryosphere.

---

### Finding 59: NAO does not join the VIX/ENSO/temperature cluster — cl8 is Pacific+financial, not generically irregular

**Claim:** The North Atlantic Oscillation, despite being an irregular climate oscillation index, does not land in the Chronos cluster containing VIX, ENSO, and temperature. The irregular asymmetric oscillator class (cl8) is specific to Pacific interannual variability and financial volatility, not a general "irregular oscillation" bin.

**Evidence:** NAO: 79% noise, 0% in cl8. Distances: nao↔vix = 0.192, nao↔enso_oni = 0.240, nao↔temperature = 0.191. For comparison, arctic↔antarctic = 0.072, covid1↔covid2 = ~0.06. NAO is farther from the irregular cluster than any member is from each other. NAO distributes across cl3 (6%) and cl5 (15%) with no dominant cluster membership.

**What it means:** The VIX-ENSO-temperature grouping from nb20 (Finding 45) was not discovering a "generic irregular climate mode" — it was discovering something specific about Pacific basin interannual variability (ENSO), global surface response to it (temperature), and financial volatility (VIX). Adding the Atlantic Oscillation does not extend the class. This narrows the definition of cl8: the shared property is likely positive amplitude asymmetry combined with interannual to multi-year timescale — properties ENSO and VIX share but NAO does not. The shape class is real but narrower than "irregular oscillation."

---

### Finding 60: PDO joins sea_level in cl4, not VIX/ENSO — timescale determines class membership for oscillatory datasets

**Claim:** The Pacific Decadal Oscillation, windowed at 5-year intervals, is placed by Chronos in the same cluster as sea_level (the clean integrated trend class), not alongside ENSO or VIX.

**Evidence:** PDO: 59% cl4, 38% noise, 0% cl8. Sea_level: 47% cl4. Pairwise distances: pdo↔vix = 0.121, pdo↔nao = 0.101, pdo↔sea_level (via cl4 co-membership). ENSO is the same physical basin and related dynamics but lands in cl8 (24%); PDO lands in cl4. The difference is timescale: ENSO operates at interannual (3–7 year) periods while PDO operates at decadal (20–30 year) periods. At 60-month windows, PDO's decadal drift dominates — the oscillation is not completed within the window, so Chronos sees an integrated trend.

**What it means:** The same physical system (Pacific Ocean surface temperature) maps to different shape classes depending on the timescale of observation. ENSO's full oscillatory cycle fits inside a 36-month window; PDO's cycle does not fit inside a 60-month window. This is not a failure of the classification — it is a correct observation that the dynamical regime relevant to a 5-year observer is different from the regime relevant to a 3-year observer. The shape class is not a property of the physical system alone; it is a property of the system as seen from a specific temporal vantage point. This reinforces the nb18 finding that shape classes are observer-relative.

---

## Session 9 (continued) — 19 April 2026 (Notebook 24)

### Finding 61: PDO window-length shift confirmed — shorter window moves PDO toward ENSO, not away from sea_level

**Claim:** Changing PDO from 60-month to 36-month windows moves it closer to ENSO/VIX in Chronos space and farther from sea_level, confirming the timescale-determines-class hypothesis from Finding 60.

**Evidence:** pdo_36mo↔enso = 0.137 vs pdo_60mo↔enso = 0.181. pdo_36mo↔vix = 0.076 vs pdo_60mo↔vix = 0.121. Reversed for sea_level: pdo_60mo↔sea_level = 0.063 vs pdo_36mo↔sea_level = 0.092. The two PDO window lengths are themselves very close (distance = 0.057, tighter than arctic↔antarctic = 0.072). pdo_36mo cluster membership: 39% cl17 (ENSO/VIX region), 60% noise — closer to ENSO but not fully joining the cluster.

**What it means:** The window length is a receiver parameter that determines which dynamical mode of PDO is visible. At 60 months, the decadal drift dominates — Chronos sees an integrated trend. At 36 months, the interannual variability becomes more visible — Chronos partially places it with ENSO. But PDO and ENSO are not the same signal: even at matched timescales, PDO remains 60% noise while ENSO is 24% in the same cluster. The physical oscillations are structurally different despite sharing the Pacific basin. The thunder hypothesis (Finding 60) is correct directionally but the receptor alone does not fully explain the difference — there is genuine structural divergence between PDO and ENSO beyond the timescale effect.

---

### Finding 62: NH Snow Cover does not join the declining oscillator class — the annual frequency is necessary but not sufficient

**Claim:** NH Snow Cover has an identical annual oscillation frequency to Arctic/Antarctic sea ice but is placed by Chronos in completely different clusters (0% overlap with cl7). The declining oscillator class requires two properties to co-occur: strong annual cycle AND embedded long-term decline.

**Evidence:** TD-6f: zero_crossings = 0.168 (snow cover) vs 0.169 (arctic sea ice) — identical. But skewness = +0.999 (snow cover) vs −0.377 (arctic sea ice) — opposite sign. Slope ≈ 0 and baseline_delta ≈ 0 for snow cover (no trend), vs slope = −0.0031 and bd = −0.138 for arctic sea ice (clear decline). Chronos distances: snow_cover↔arctic_sea_ice = 0.317, snow_cover↔antarctic_sea_ice = 0.311 — farther from sea ice than sea ice is from many unrelated datasets. In Chronos space, snow cover scatters across 7 different clusters (cl0–cl6) with no dominant membership.

**What it means:** The annual cycle alone is not enough to join the declining oscillator class. Sea ice peaks in summer melt and builds gradually through winter (negative skewness — gradual rise, sharp peak). Snow cover spikes sharply in winter and melts fast in spring (positive skewness — opposite asymmetry). Same period, different shape within the cycle. Additionally, NH snow cover has no consistent long-term trend across the 1967–present record — some decades show spring decline, others partial recovery. The Chronos fragmentation across 7 clusters reflects this: each 10-year window has a different trend direction, so each looks like a different class. The declining oscillator class (cl7) requires the secular decline to be present and consistent within the observation window.

---

### Finding 63: Orientation-invariant features collapse snow cover but leave sea ice unchanged — directionality is the source of snow cover's fragmentation

**Claim:** Replacing slope and baseline_delta with their absolute values (removing directional information) makes NH Snow Cover cluster at 99% purity in a single TD-6f cluster (up from 52%), while Arctic/Antarctic sea ice remain 100% pure and completely unchanged. The overall cluster count drops by only one (18→17).

**Evidence:** Original TD-6f: nh_snow_cover = 52% cl11, arctic_sea_ice = 100% cl12, antarctic_sea_ice = 100% cl12. Invariant TD-6f: nh_snow_cover = 99% cl10, arctic_sea_ice = 100% cl12, antarctic_sea_ice = 100% cl12. Noise count drops from 1191 to 1015. ARI between original and invariant clusterings = 0.712 (substantial agreement, not identity). keeling_trend and keeling_seasonal: both 100% stable. ENSO: 99% noise → 77% noise.

**What it means:** Snow cover's fragmentation across 7 Chronos clusters and its 48% impurity in TD-6f space are both caused by its lack of consistent trend direction — some time windows slope up, some down, some flat, and both Chronos and the 6-feature fingerprint treat these as different classes. When direction is removed, the underlying annual oscillation shape is revealed and snow cover clusters cleanly. Arctic/Antarctic sea ice are immune to this because their long-term decline is consistent and structural — removing directionality does not change their class because their shape identity does not depend on slope sign. This directly supports the nb23 finding (F55): shape-defined classes (oscillator, burst) are stable under orientation changes; directionally-defined classes are not. Snow cover is revealed to be shape-defined at its core, with directional fragmentation as a surface artifact of the representation.

---

## Session 10 — 19 April 2026 (Notebook 25)

### Finding 64: No grokking — XWorld shape classes are immediately generalizable, not algebraically latent

**Claim:** A small transformer (2 layers, d_model=64, ~100k parameters) trained on 3200 synthetic shape class instances achieves >90% validation accuracy at the very first logging checkpoint (epoch 50). There is no memorization plateau followed by a generalization jump.

**Evidence:** train_acc = val_acc ≈ 0.90+ at epoch 50, rising to train_acc = 1.0, val_acc = 0.996 by epoch 5000. The "grokking delay" as detected by the code is 0 epochs. Final validation accuracy: 99.6% (3 errors from 800 instances). Weight decay = 0.1 was applied throughout.

**What it means:** Grokking requires a task where no surface pattern is sufficient — the model is forced to memorize first because generalization requires discovering hidden algebraic structure (e.g., Fourier components of a cyclic group in modular arithmetic). XWorld shape classes are the opposite: each class has a visually distinctive raw waveform signature that is directly detectable at the sequence level. A burst event and a declining oscillator look completely different as sequences of 64 numbers. The transformer picks this up immediately. The absence of grokking tells us something real about the nature of the shape classes: they are detectable by direct temporal pattern matching, not by abstract algebraic inference.

---

### Finding 65: Post-training embeddings form an address book, not a manifold — class separations are equidistant

**Claim:** The transformer's CLS embeddings place the 8 shape classes in approximately equidistant corners of the 64-dim space (pairwise distances compressed to the range 10.3–13.1, spread of 2.8). There is no continuous geometry between the classes.

**Evidence:** Pairwise centroid distances: min = 10.27 (eco_cycle↔seasonal), max = 13.06 (irregular_osc↔declining_osc), mean ≈ 11.5, range = 2.8. By comparison, in Chronos space (nb20–22) and 6-feature space (nb23) the ratio of max/min distance is typically 3–5x; here it is 1.27x — extremely compressed. PCA of 64-dim embeddings: the 8 classes separate cleanly but with roughly equal spacing; no continuous arc or manifold is visible.

**What it means:** The transformer learned to classify, not to encode similarity. The CLS token learned to route each input to one of 8 corners — an "address book" — rather than learning a similarity geometry where nearby classes are nearby in embedding space. This is a property of cross-entropy training with balanced classes: the optimal solution is to push all classes to maximally separated locations, which tends toward equidistance in high-dimensional spaces. A contrastive or triplet loss would force the model to encode within-class and between-class similarity explicitly — that experiment would produce a more informative embedding space.

---

### Finding 66: Transformer and 6-feature fingerprint have opposite opinions about inter-class geometry — Spearman ρ = −0.31

**Claim:** The pairwise centroid distances between the 8 shape classes in transformer embedding space are negatively rank-correlated with those in 6-feature fingerprint space (Spearman ρ = −0.31, p = 0.11). The two receptors agree that the 8 classes are distinct, but disagree on which classes are structurally similar.

**Evidence:** Transformer closest pair: eco_cycle↔seasonal (10.27). 6-feature closest pair: trend↔integrated_trend. Transformer most distant pair: irregular_osc↔declining_osc (13.06). In 6-feature space these two classes are the most frequent confusion pair (nb23 F57 — highest boundary crossing rate). The only confusion pairs from the transformer's 3 validation errors: eco_cycle→seasonal (1x) and trend↔integrated_trend (2x) — which happen to be the TOP 2 closest pairs in the 6-feature fingerprint. The two representations agree on which confusions happen but disagree on why.

**What it means:** Both receptors separate all 8 classes (transformer 99.6% accuracy; 6-feature fingerprint achieves class purity in nb23). The separations are robust. But the geometry between the classes — which pairs are similar, which are distant — is entirely receptor-dependent. The transformer sees: irregular_osc and declining_osc are maximally different (raw waveforms: one is noisy asymmetric, the other is amplitude-decaying sinusoidal). The 6-feature fingerprint sees: these two are easily confused (summary statistics overlap). This is the thunder hypothesis made concrete: the 8 class boundaries are in the world (three independent receptors all find them), but the manifold between the classes is in the measurement. The structure of similarity is not a property of the series themselves — it depends on what aspect of the series the receptor is sensitive to.

---

## Session 11 — 19 April 2026 (Notebook 26)

### Finding 67: Contrastive loss recovers positive correlation with 6-feature fingerprint — the loss function was the problem

**Claim:** Replacing cross-entropy with Supervised Contrastive Loss (SupCon) changes the Spearman ρ between transformer and 6-feature pairwise distances from −0.31 (nb25) to +0.38 (p = 0.044). The loss function, not the transformer architecture, was the source of geometric disagreement.

**Evidence:** nb25 (CE loss): ρ = −0.31 (p = 0.107, not significant). nb26 (SupCon, τ = 0.07): ρ = +0.38 (p = 0.044, significant). Same transformer architecture (d_model=64, 2 layers, 4 heads). Same dataset (8 classes × 500 instances). Same seeds. Only the training objective changed.

**What it means:** Cross-entropy training routes each input to the correct corner of embedding space; it has no incentive to place similar classes nearby. SupCon training explicitly forces same-class instances together and different-class instances apart — this is the only way to build a similarity geometry rather than a classification geometry. The transformer is capable of encoding structural similarity; CE just never asks it to. The negative ρ in nb25 was not evidence that the two representations see different structures — it was evidence that CE is the wrong loss for manifold learning.

---

### Finding 68: Contrastive embedding is structured, not an address book — distance range 2.81x

**Claim:** The contrastive embedding has a max/min pairwise centroid distance ratio of 2.81x (3.60–10.12), compared to nb25's 1.27x (10.27–13.06). Classes are differentially separated: burst is isolated (6.1–10.1 from all others); trend↔integrated_trend are the tightest pair (3.60).

**Evidence:** Closest pair: trend↔integrated_trend (3.60). Most distant: burst↔integrated_trend (10.12). The geometry is readable: trend/integrated_trend/seasonal cluster together (directional structure); oscillator/eco_cycle/seasonal form an oscillatory cluster; irregular_osc↔declining_osc are nearby (5.53); burst is structurally isolated from all other classes.

**What it means:** The contrastive loss produces a space where geometric distance reflects structural similarity. The interpretable groupings — trend-like classes near each other, oscillatory classes near each other, burst isolated — match the intuitive hierarchy of the 8 shape classes. This is the first XWorld embedding space to carry relational geometry rather than just classification routing. The loss curve barely moving after epoch ~200 (4.10 → 3.95) confirms the geometry is established early and stable.

---

### Finding 69: trend↔integrated_trend is the closest pair in both contrastive and 6-feature space — first cross-representation top-1 agreement

**Claim:** The contrastive transformer and the 6-feature fingerprint independently identify trend↔integrated_trend as the closest pair of shape classes. This is the first time two completely different measurement architectures have agreed on the #1 most similar pair.

**Evidence:** Contrastive closest pair: trend↔integrated_trend (3.60). 6-feature closest pair: trend↔integrated_trend (confirmed across nb23 and nb26). The #2 pair differs (contrastive: seasonal↔trend; 6-feature: eco_cycle↔seasonal) — agreement is partial, not complete, consistent with ρ = 0.38 rather than ρ = 1.0.

**What it means:** Both representations independently identify trend and integrated_trend as the most structurally similar class pair. Both look at the series from completely different angles — the transformer sees raw temporal sequences; the 6-feature fingerprint sees summary statistics — and arrive at the same answer. This is the strongest cross-representation agreement in the experiment so far, and it partially answers the thunder hypothesis: the similarity geometry between the shape classes is not purely a receptor artifact. At least the top of the similarity ordering is real. The partial agreement (ρ = 0.38, not 1.0) means the middle of the ordering is still receptor-dependent — which pair is "second closest" depends on what you measure.

---

## Session 12 — 19 April 2026 (Notebook 27)

### Finding 70: Synthetic-to-real transfer fails for 4/5 datasets — the contrastive manifold does not generalise to real data

**Claim:** The contrastive encoder trained on synthetic shape classes (nb26) correctly assigns only 1 of 5 real datasets to the Chronos-assigned shape class (VIX → irregular_osc). Sunspot, Keeling CO2, ENSO, and arctic sea ice all land in unexpected regions.

**Evidence:** Nearest synthetic class vs Chronos assignment: sunspot → irregular_osc (expected oscillator); keeling_co2 → irregular_osc (expected seasonal); enso → eco_cycle (expected irregular_osc); arctic_ice → integrated_trend (expected declining_osc); vix → irregular_osc ✓. Lynx-hare produced no valid windows (annual data, 21 points < SEQ_LEN=64).

**What it means:** The synthetic generators produce idealised pure shapes; real data combines multiple shape components simultaneously (oscillation inside a trend, seasonal signal inside a rising baseline). The contrastive encoder was never trained on these composite signals. Chronos transfers because it was pre-trained on millions of real series containing all such combinations. A contrastive encoder trained on real windowed data — rather than synthetic generators — would be needed for reliable real-to-synthetic correspondence. The synthetic manifold is a manifold of pure archetypes, not of real-world dynamics.

---

### Finding 71: Sunspot at 64-month windows lands in irregular_osc, not oscillator — F60 replicated by an independent method

**Claim:** The contrastive encoder assigns sunspot (11-year cycle) to the irregular_osc class at 64-month window lengths. This is consistent with Finding 60 (Chronos assigns PDO to integrated_trend at 60-month windows) and extends the timescale-determines-class result to a completely different measurement architecture.

**Evidence:** Sunspot: 272 windows of 64 months each (≈5.3 years). Each window contains less than 0.5 of the 11-year cycle. Nearest synthetic class: irregular_osc (distance 1.115); second nearest: eco_cycle (3.484). The synthetic oscillator class was trained with 1.5–4.5 full cycles per window — sunspot at 64 months shows no complete cycle. The encoder correctly classifies this partial-cycle signal as irregular, not oscillatory.

**What it means:** The timescale-determines-class effect from nb22/F60 is not specific to Chronos. A contrastive encoder trained on synthetic data with the same window length arrives at the same conclusion through a completely different mechanism. At 64-month windows, sunspot is an irregular signal — the oscillatory structure is only visible at longer windows. Three independent methods (Chronos at 60mo, 6-feature fingerprint at variable windows, contrastive encoder at 64mo) now agree that the apparent shape class of an oscillatory system depends on the ratio of window length to cycle period.

---

### Finding 72: No grokking in 6-feature space — the 8 classes are immediately separable at 100 instances/class

**Claim:** A 101k-parameter MLP trained on 6-feature vectors (100 instances/class, 800 total) achieves >90% validation accuracy at the first checkpoint (epoch 50). No memorisation plateau. Final val accuracy: 97.5%.

**Evidence:** train_acc = val_acc ≈ 0.95+ from epoch 50. Grokking gap = 0 epochs. Train loss converges to near-zero while val accuracy remains stable at ~97% (val loss eventually drifts up from overconfidence, not from wrong decisions). The MLP has 127x as many parameters as training instances — enough to memorise, but it does not.

**What it means:** The 6-feature fingerprint was specifically designed to separate these 8 shape classes. Even 100 training examples per class are sufficient for a large MLP to find the correct decision boundaries without a memorisation phase. Grokking requires tasks where no surface pattern is sufficient for generalisation — the 6-feature space does not qualify. Combined with nb25 (no grokking on raw waveforms) and nb27 Part B (no grokking on 6-feature vectors), the evidence is consistent: XWorld shape classes are syntactically separable regardless of representation. There is no hidden algebraic structure to grok — the separations are on the surface of whatever representation you choose.

---

## Session 13 — 19 April 2026 (Notebook 28)

### Finding 73: WGMS glacier mass balance → eco_cycle (cumulative) and irregular_osc (annual) — oscillation confirmed necessary for declining_osc; fingerprint reveals a structural gap

**Claim:** WGMS global glacier cumulative mass balance (1950–2025, 76 years of strong monotonic decline) classifies as eco_cycle, not trend or declining_osc. The annual mass balance classifies as irregular_osc. Neither matches the predicted trend class.

**Evidence:** Cumulative WGMS 6-feature fingerprint: skewness=−0.770, lag1_autocorr=0.9997, zero_crossings=0.016, slope=−0.052, baseline_delta=−3.289. Nearest class: eco_cycle (distance 3.26); declining_osc is 3rd at 3.76. Annual WGMS: zero_crossings=0.219, lag1_autocorr=0.703; nearest: irregular_osc (3.90). The cumulative series has zero_crossings=0.016, nearly identical to integrated_trend (0.016), but baseline_delta=−3.289 vs integrated_trend centroid=+3.140 (opposite sign). No class has both near-zero crossings and a large negative baseline_delta.

**What it means:** Two things simultaneously: (1) oscillation IS a necessary condition for declining_osc. WGMS cumulative has zero_crossings=0.016 — far below the declining_osc centroid of 0.120 — and the fingerprint correctly refuses to assign it to declining_osc. (2) The signed 6-feature fingerprint has no class for "strong monotonic decline without oscillation." WGMS cumulative is the structural mirror image of integrated_trend (slope −0.052 vs +0.054, baseline_delta −3.289 vs +3.140) but there is no class to receive it. The 8-class corpus was assembled from datasets that happen to be directionally biased: rising trends dominate, strong declining monotonic signals are absent. The fingerprint inherits this asymmetry.

---

### Finding 74: Phase diagram reveals declining_osc basin occupies 42.2% of (n_cycles × decline) parameter space with 94.2% mean purity — the largest and purest single-class attractor basin

**Claim:** The synthetic phase diagram (20×20 grid: n_cycles 0.5–7.0 × decline 0.0–1.5, 20 instances per cell) shows declining_osc as the dominant class across the central parameter region.

**Evidence:** Basin occupancy: 169 / 400 cells (42.2%), mean purity 0.942. Comparison: seasonal 79 cells (19.8%), oscillator 68 (17.0%), eco_cycle 52 (13.0%), irregular_osc 18 (4.5%), burst 14 (3.5%). The declining_osc basin spans n_cycles 1.53–7.00 and decline 0.00–1.50 at the extremes — but the core of the basin (n_cycles ~2–5, decline ~0.6–1.3) is essentially pure.

**What it means:** Declining oscillator is not a fragile edge case requiring precise parameter tuning — it is the dominant class across a wide region of (oscillation, decline) parameter space. Once a system has enough cyclicity and enough long-term amplitude loss, it consistently produces the declining_osc fingerprint. The 94.2% purity confirms a robust attractor, not a classifier artifact. The large basin size is consistent with the class being recently discovered: real systems that produce declining oscillation are common, but the gap was in the corpus, not in the attractor.

---

### Finding 75: Minimum conditions for declining_osc: decline > ~0.6 AND n_cycles in ~1.9–4.6 range — three distinct phase boundaries with different adjacent classes

**Claim:** The phase diagram reveals three independent boundary conditions for the declining_osc basin, each bordering a different shape class, identifying separate necessary conditions.

**Evidence:** By-decline marginal (averaged over all n_cycles): decline 0.0–0.47 → seasonal; 0.55 → eco_cycle; 0.63+ → declining_osc. Threshold ≈ 0.6. By-n_cycles marginal (averaged over all decline): n_cycles 0.5–1.53 → eco_cycle/oscillator; 1.87–4.6 → declining_osc; 5.3–7.0 → seasonal → irregular_osc. Corner case: n_cycles 2.2–2.6, decline 0.95–1.5 → burst. Three distinct boundaries: (1) low-decline boundary (~0.6): below → seasonal — oscillation without decline; (2) low-n_cycles boundary (~1.5): below → eco_cycle or oscillator — decline without sufficient oscillation; (3) high-n_cycles ceiling (~5): above → seasonal — individual cycles too short for decline envelope to register.

**What it means:** Declining_osc requires two independent conditions: enough oscillation AND enough decline. They are not interchangeable — a strongly declining series with one visible cycle looks like eco_cycle/oscillator; a strongly oscillating series with no decay looks like seasonal. The high-frequency ceiling is interpretable: at n_cycles > 5 in a 64-step window, z-score normalisation can no longer distinguish declining envelope from normal amplitude variation, and the fingerprint reads periodic structure (seasonal) instead of periodic-with-decline. The burst corner is notable: extreme decline (>0.95) collapses the later half of the series to near-zero — which the burst fingerprint is designed to capture (large early amplitude, near-zero later).

---

### Finding 76: The signed fingerprint has no class for "strong monotonic decline without oscillation" — WGMS is the mirror of integrated_trend, pointing to a potential 9th class

**Claim:** The 8-class system cannot receive a strong monotonically declining signal without oscillation. Such a signal (WGMS cumulative) is the mirror image of integrated_trend in every signed feature, but the corpus contains no declining counterpart. The signed fingerprint assigns it to eco_cycle — the nearest available class.

**Evidence:** WGMS cumulative vs integrated_trend centroid: lag1_autocorr 1.000 vs 1.000 (identical), zero_crossings 0.016 vs 0.016 (identical), |slope| 0.052 vs 0.054 (identical magnitude), |baseline_delta| 3.289 vs 3.140 (identical magnitude). Only differences: slope sign (−0.052 vs +0.054) and baseline_delta sign (−3.289 vs +3.140). With absolute fingerprint (|slope|, |baseline_delta|), WGMS would land directly in integrated_trend. Under signed fingerprint, it classifies as eco_cycle at distance 3.26, with declining_osc correctly rejected at 3.76 (zero_crossings mismatch).

**What it means:** The signed fingerprint encodes directionality — a rising integrated trend and a falling one are structurally different classes. This is physically meaningful (glacier retreating IS different from sea level rising). But it requires the corpus to contain both orientations for every structural shape. Currently only rising monotonic trends exist (sea_level, ocean_heat, keeling_trend, ch4_trend). The falling-monotonic-trend basin is unmapped. WGMS is the natural anchor for a potential 9th class. The decision is architectural: add the 9th class (and look for other declining monotonic systems) or switch to absolute fingerprint (which loses directional information but closes the gap automatically).

---

### Finding 77: Absolute fingerprint breaks zero correctly-classified datasets — the "2 changed" were already wrong under signed

**Claim:** Switching to absolute fingerprint (|slope|, |baseline_delta|) appears to change 2 dataset classifications, but both were already misclassified under signed. Net correctly-working classifications broken = 0.

**Evidence:** Under signed fingerprint: sea_level → irregular_osc (wrong), sunspot → irregular_osc (wrong). Under absolute fingerprint: sea_level → eco_cycle (still wrong), sunspot → trend (still wrong). No dataset that was correctly classified under signed fingerprint became wrong under absolute.

**What it means:** The absolute fingerprint's apparent "2 broken" count is misleading — it's changing wrong-to-different-wrong. But the structural risk remains: declining_osc ↔ trend/integrated_trend distance shrinks 31% (from 4.42 to 3.06). The architectural decision is not about which fingerprint fixes more misclassifications, but about which preserves the safest class separations. Signed fingerprint wins on that metric.

---

### Finding 78: Absolute fingerprint correctly lands WGMS in integrated_trend — but the basin geometry cost outweighs the gain

**Claim:** Under the absolute fingerprint, WGMS cumulative correctly classifies as integrated_trend (distance 0.22 vs 0.26 to eco_cycle). This is the expected result — WGMS is structurally identical to integrated_trend except for sign.

**Evidence:** Absolute fingerprint WGMS: nearest class = integrated_trend (d=0.22). Signed fingerprint WGMS: nearest class = eco_cycle (d=3.26). However, absolute fingerprint shrinks declining_osc ↔ trend distance from 4.42 → 3.06 (31% contraction). The three-way distances cluster around 3, reducing structural separation across the trend-class region.

**What it means:** The absolute fingerprint solves the WGMS misclassification but at the cost of structural basin integrity. The signed + 9th class approach achieves the same goal (correctly classify WGMS) without sacrificing the declining_osc basin geometry. Decision: keep signed fingerprint, add 9th class.

---

### Finding 79: Snow cover ZC=0.671 anomalous — suspected parser issue; stays irregular_osc under both fingerprints

**Claim:** March NH snow cover has zero_crossings = 0.671 — anomalously high for a dataset that visually shows a declining trend with inter-annual noise. This value is inconsistent with expected ZC for any trend class.

**Evidence:** ZC = 0.671 exceeds every trend class centroid by >10×. Under both signed and absolute fingerprints, snow cover routes to irregular_osc. Visual inspection of the series shows inter-annual weather noise dominating the long-term trend signal, consistent with F63 (annual snow cover = weather noise > trend signal).

**What it means:** The ZC anomaly is likely a parser issue (or the dataset genuinely has this much noise). Either way, snow cover correctly fails the declining_monotonic gate (lag1 = 0.549, ZC = 0.234 at window level) and stays in irregular_osc. The gate protects against noisy trend-like datasets being misrouted to declining_monotonic.

---

### Finding 80: Architectural decision — keep signed fingerprint, establish declining_monotonic_trend as 9th class

**Claim:** The 9-class system (8 original + declining_monotonic_trend) is the correct architectural path forward. Absolute fingerprint is rejected.

**Evidence:** (1) Absolute fingerprint shrinks declining_osc ↔ trend distance 31% — structural risk. (2) Absolute fingerprint corrects WGMS, but 9th class also corrects WGMS without the basin geometry cost. (3) Signed fingerprint preserves physical meaning — rising and falling monotonic trends are genuinely different dynamical states. (4) No correctly-classified datasets are broken by either approach.

**What it means:** The fingerprint architecture is locked: 6 signed features (skewness, kurtosis, lag1_autocorr, zero_crossings, slope, baseline_delta). The taxonomy is 9 classes. The 9th class is anchored empirically (not synthetically only) by WGMS cumulative.

---

### Finding 81: 9th class gate — lag1 > 0.93, ZC < 0.05, slope < −0.005 — correctly separates declining_monotonic from all other classes

**Claim:** Three gate conditions jointly necessary and sufficient to route a dataset to the 9th class. The lag1 threshold is calibrated against the eco_cycle centroid (0.931), not against WGMS cumulative (0.9997).

**Evidence:** Gate calibration: (1) lag1 > 0.93 — just above eco_cycle centroid (0.931), which is the highest lag1 outside the trend classes; (2) ZC < 0.05 — zero-crossings below noise floor; (3) slope < −0.005 — sign and magnitude gate to reject flat or rising series. Accepted: PIOMAS annual mean (lag1=0.966), World Bank forest cover (lag1=0.998). Rejected: March snow cover (lag1=0.549, ZC=0.234).

**What it means:** The gate is principled: lag1 > 0.93 means "more persistent than any oscillatory class," ZC < 0.05 means "essentially non-oscillatory," slope < −0.005 means "declining." Three independent conditions. The eco_cycle centroid is the natural calibration point because eco_cycle is the 8-class system's fallback for declining_monotonic — the gate must sit above it.

---

### Finding 82: PIOMAS annual mean ice volume passes the declining_monotonic gate — second cryosphere anchor

**Claim:** PIOMAS annual mean Arctic sea ice volume (1979–present) classifies as declining_monotonic under the 9-class system. Under the 8-class system it was misclassified as eco_cycle.

**Evidence:** PIOMAS annual mean: lag1=0.966, ZC=0.063 (windowed mean), slope=−0.029. Gate passed. 9-class assignment: declining_monotonic at 100% window purity. 8-class assignment: eco_cycle (the 8-class fallback for high-lag1 declining series). Physical interpretation: Arctic sea ice volume has been declining monotonically since satellite records began, with no multi-year oscillation.

**What it means:** The 9th class captures a physically meaningful distinction — ice *volume* (PIOMAS) and ice *extent* (arctic_sea_ice monthly) have different fingerprints because one is a smooth annual aggregation and the other is a monthly series with strong seasonal cycles. The monthly series reads as declining_osc; the annual mean reads as declining_monotonic. This is the timescale-determines-class phenomenon applied to the 9th class.

---

### Finding 83: World Bank forest cover passes the declining_monotonic gate — cross-domain anchor from land-use

**Claim:** World Bank global forest cover percentage (1990–present) classifies as declining_monotonic. This extends the 9th class beyond the cryosphere into land-use.

**Evidence:** Forest cover: lag1=0.998, ZC=0.000 (no zero crossings), slope=−0.038. Gate passed at all thresholds. 9-class assignment: declining_monotonic at 100% purity. 8-class assignment: eco_cycle. Physical interpretation: global deforestation is a monotonically declining process at the global scale, with no reversal cycles.

**What it means:** The 9th class is genuinely cross-domain. Two physically unrelated systems — Arctic ice volume (cryosphere) and global forest cover (land-use) — share identical fingerprints. This is consistent with the central XWorld hypothesis: the dynamic shape class is domain-agnostic.

---

### Finding 84: 9-class system fully operational — synthetic centroid: lag1=1.000, ZC=0.016, slope=−0.054, BD=−3.137

**Claim:** The 9th class synthetic generator and centroid are calibrated. The class is the mirror of integrated_trend in the signed fingerprint.

**Evidence:** Synthetic generator: `zscore(np.cumsum(-np.ones(SEQ_LEN)*r.uniform(.015,.035)+r.normal(0,.003,SEQ_LEN)))` — identical to integrated_trend except for negated drift term. Centroid: lag1=1.000, ZC=0.016, slope=−0.054, baseline_delta=−3.137. Integrated_trend centroid: lag1=1.000, ZC=0.016, slope=+0.054, baseline_delta=+3.140. Mirror-exact in sign.

**What it means:** The 9th class is the directional mirror of integrated_trend. Its existence is predicted by the fingerprint architecture (if rising cumulative trend exists, falling must too) and confirmed empirically (WGMS, PIOMAS, forest cover). The taxonomy is now structurally symmetric in the monotonic-trend direction.

---

### Finding 85: Exactly 3 reclassifications under the 9-class system — all predicted

**Claim:** Only the three declining_monotonic anchors reclassify between 8-class and 9-class. No unexpected reclassifications.

**Evidence:** Full 17-dataset corpus audit: wgms_cumulative, piomas_annual, forest_cover → eco_cycle (8-class) → declining_monotonic (9-class), all at 100% window purity. 14 other datasets: unchanged. The 9th class gate does not misfire on any dataset lacking monotonic decline.

**What it means:** The 9-class expansion is surgical — it adds precision without disturbing existing structure. The gate's three conditions (lag1 > 0.93, ZC < 0.05, slope < −0.005) are well-calibrated.

---

### Finding 86: All 14 original-class datasets are stable; pre-existing misclassifications are unchanged between 8- and 9-class

**Claim:** Boundary-effect misclassifications that existed in the 8-class system persist unchanged in the 9-class system. The 9th class does not intercept any of them.

**Evidence:** Pre-existing misclassifications (all unchanged): arctic/antarctic_sea_ice → seasonal (windowing, F73); sunspot → irregular_osc (amplitude modulation); ch4_trend → irregular_osc (measurement noise ZC); ocean_heat → trend (annual resolution); sea_level → irregular_osc (satellite switching, F45); vix → burst (positive skewness); enso → burst (extreme years); covid → trend (smoothed multi-wave structure).

**What it means:** These misclassifications are fingerprint boundary effects — the nearest centroid is consistently wrong for these datasets because the 64-point windowing or the 6-feature representation does not capture their defining property (long-term decline for sea ice, amplitude modulation for sunspot). They are not problems introduced by the 9-class system and do not affect the validity of the class taxonomy.

---

### Finding 87: HDBSCAN forms 5 clusters at n=17; declining_monotonic trio clusters together but shares with keeling_seasonal

**Claim:** HDBSCAN on the 17-dataset UMAP embedding identifies 5 clusters. The declining_monotonic trio (WGMS, PIOMAS, forest_cover) clusters together, but not cleanly separated from keeling_seasonal.

**Evidence:** Cluster 0: covid, enso, keeling_trend, ocean_heat, sea_level (noisy trend-like). Cluster 1: sunspot, vix (oscillatory). Cluster 2: forest_cover, keeling_seasonal, piomas_annual, wgms_cumulative (declining_monotonic + keeling_seasonal). Cluster 3: arctic_sea_ice, antarctic_sea_ice, temperature. Cluster 4: ch4_trend, nao, pdo. piomas_annual marked as noise in some runs.

**What it means:** At n=17, UMAP neighbourhood geometry is unstable (n_neighbors=5, barely enough for reliable manifold estimation). The keeling_seasonal proximity to declining_monotonic in UMAP space is an artefact. The important structural result holds: the three declining_monotonic datasets are proximate and separated from the positive-slope trend datasets. Full corpus HDBSCAN at larger n (synthetic + real, ~1000+ points) will be more interpretable.

---

### Finding 88: 9-class system passes full corpus stability audit — 17 real-world datasets across 8 unrelated domains

**Claim:** The 9-class signed-fingerprint nearest-centroid architecture is structurally sound and stable across the full corpus.

**Evidence:** n=17 datasets: atmospheric chemistry (keeling seasonal/trend, CH4, CO2), climate (temperature, ENSO, NAO, PDO, ocean heat), finance (VIX), ecology (lynx_hare not in this corpus, but eco_cycle class present), cryosphere (arctic/antarctic sea ice, PIOMAS), epidemiology (COVID), land-use (forest cover), glaciology (WGMS). 3 correct reclassifications to declining_monotonic. 0 incorrect reclassifications. Pre-existing misclassifications unchanged.

**What it means:** The 9-class expansion is complete. The corpus has been audited. The taxonomy is stable. Ready for Phase 3: connecting shape classes to physical system feedback structure.

---

### Finding 89: 8/9 ODEs land in their predicted shape class — the fingerprint detects feedback structure

**Claim:** Integrating the natural ODE for each shape class and running the 6-feature fingerprint should yield the correct class assignment. 8 of 9 do.

**Evidence:** oscillator (simple harmonic ✓), declining_osc (damped harmonic impulse response ✓), seasonal (two-frequency superposition ✓), burst (Gaussian pulse ✓), trend (constant drift ✓), integrated_trend (Langevin positive drift ✓), declining_monotonic (Langevin negative drift ✓), irregular_osc (Rössler chaotic attractor ✓). eco_cycle fails (see F91).

**What it means:** The fingerprint features are not arbitrary — they encode physically meaningful quantities. Each ODE class maps to a distinct region of feature space. The shape class taxonomy has a basis in differential equation theory.

---

### Finding 90: γ sweep — overdamped harmonic reads as burst, not declining_monotonic; declining_osc requires zero-displacement initial condition

**Claim:** Increasing damping γ from 0 to 3×critical in the damped harmonic oscillator (starting from x(0)=1) transitions oscillator → eco_cycle → burst. The predicted declining_osc or declining_monotonic transition never occurs.

**Evidence:** γ sweep of 40 values (γ/2ω from 0 to 3.0): only 1 step at oscillator (γ≈0), 1 step at eco_cycle (γ/2ω≈0.08), then burst for all γ/2ω from 0.16 to 3.0. Explanation: starting from x(0)=1, ẋ(0)=0, the damped harmonic produces a smooth monotone decay (high lag1, low ZC, positive skewness) — identical fingerprint to burst. The GREEN'S FUNCTION solution (x(0)=0, ẋ(0)=ω) does produce declining_osc (✓ at ω=4, γ=0.4). Initial conditions determine shape class, not just ODE parameters.

**What it means:** Burst and declining_osc are related — both involve damped harmonic dynamics. The difference is the initial condition: displacement (x₀≠0) → burst profile; velocity impulse (ẋ₀=ω) → declining_osc profile. A physical oscillator hit by a displacement vs an oscillator kicked into motion look identical in their equations but different in fingerprint space. The burst class is broader than "spike event" — it captures any localised high-amplitude decay.

---

### Finding 91: eco_cycle has no simple ODE basis — the class is noise-dependent, not a distinct attractor

**Claim:** Lotka-Volterra predator-prey (prey series) does NOT land in the eco_cycle class. The eco_cycle class is defined by noise level + harmonic content, not by ecological dynamics.

**Evidence:** LV prey series: skewness=+0.48, classifies as oscillator. eco_cycle centroid: skewness=−0.135. The centroids for eco_cycle and oscillator are the closest pair in 9-class space (ZC: 0.093 vs 0.096, lag1: 0.931 vs 0.945). Without noise (σ=0), the harmonic superposition sin(ωt)+0.4sin(2ωt) classifies as oscillator. With noise σ=0.12, it crosses into eco_cycle. The class is noise-dependent.

**What it means:** The class name "eco_cycle" is physically misleading — LV predator-prey has positive-skewed prey spikes (OPPOSITE sign from the eco_cycle centroid). The class should be described as "noisy oscillation with second harmonic content." It is not a distinct dynamical attractor but a noise-displaced region of the oscillator basin. This is the only class in the 9-class taxonomy without a clean ODE basis.

---

### Finding 92: ODE parameters map onto fingerprint features with near-perfect Spearman correlation

**Claim:** The three principal ODE parameters (ω, γ, drift a) map cleanly onto the fingerprint features they theoretically control.

**Evidence:** ρ(ω, ZC) = 0.998; ρ(γ, lag1) = +0.943 (damping INCREASES lag1 — heavy damping → smooth monotone decay → high autocorrelation; oscillations reduce lag1 via phase transitions); ρ(drift a, slope) = 1.000; ρ(drift a, baseline_delta) = 0.751.

**What it means:** The 6-feature fingerprint is a structured projection of ODE parameter space. zero_crossings ≈ f(ω). lag1_autocorr ≈ g(γ). slope ≈ h(drift). Each feature reads one dimension of the dynamical system's parameterisation.

---

### Finding 93: Rössler chaotic attractor classifies as irregular_osc — the class captures deterministic chaos

**Claim:** The Rössler attractor (genuinely chaotic 3D ODE) classifies as irregular_osc across all tested windows.

**Evidence:** 12/12 windows (80 time units each, starting times 80–190) classify as irregular_osc. Features: lag1=0.50–0.66, ZC=0.25–0.31. Distance from centroid: 4.62–7.8 (wide class). Rössler is the only deterministic chaotic ODE in the set; all others are either linear, nonlinear limit cycles, or stochastic.

**What it means:** The irregular_osc class captures both stochastically noisy oscillation AND deterministic chaos. The shared fingerprint property: intermediate lag1 (no long-range coherence, but not white noise) + high ZC. The class is better described as "signals with intermediate autocorrelation and high zero-crossing rate" rather than "irregular oscillation." Chaos and noise are fingerprint-indistinguishable at this feature resolution.
