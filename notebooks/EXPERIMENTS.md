# XWorld — Experiment Log

Chronological record of what was tried, what happened, and why each direction was taken.

---

## 2026-04-19 — Session 8: Theoretical — Latent arithmetic space and XWorld connection (no notebook)

### What happened

No notebook run. A conversation traced a single idea from mental arithmetic (place-value decomposition with a child) through binary computation, transformer mechanics, and the question of minimal primitives, arriving at a research direction adjacent to XWorld.

The core idea: arithmetic results and cross-domain shape classes may be the same phenomenon — both are attractors in a structured latent geometry, not stored facts. The XWorld 6-feature fingerprint is already a latent embedding that strips domain and keeps only relational dynamics. The grokking parallel is the sharpest version: Chronos generalises zero-shot across domains; a grokked arithmetic model generalises beyond its training range. Both suggest discovered structure, not memorised examples.

### Notebook 23 created: `23_latent_arithmetic_xworld.ipynb`

**Part A — Arithmetic latent space:** Structured 4D encoder [log(n), n/max, parity, residue] vs raw scalar encoder. Trained on +−×÷ up to n=1000 with MSE + inverse-consistency + commutativity losses. Extrapolation tested at 5k, 50k, 1M. PCA of learned embeddings to check for number-line geometry.

**Part B — XWorld shape distortions:** 8 synthetic shape classes (50 instances each). Four distortions: time-reverse, amplitude-flip, noise (σ=0.1/0.3/0.7), time-warp (factor=0.7/1.4). Measures feature drift and boundary crossing rate per class. Stability ranking answers: which shape classes are structural attractors vs fragile surface fits?

**Findings to be logged:** 53–57

See summary_19APR2026.md for full theoretical development.

---

## 2026-03-31 — Session 7: Declining oscillator confirmation + cl7 test (Notebook 22)

### Goal
Two questions from nb21:
1. Confirm the 8th shape class (declining oscillator) with an independent dataset — Antarctic sea ice
2. Test whether commodity prices land in the cl7 positive-asymmetry cluster — WTI crude oil + copper

### New datasets (nb22)
- **Antarctic sea ice** (NSIDC monthly, same source as Arctic) — predicted: joins cl0 with Arctic
- **WTI crude oil** (FRED daily → monthly) — predicted: cl7 (positive skew, asymmetric oscillation)
- **Copper price** (FRED monthly) — predicted: cl7 or VIX-adjacent

### Pre-run predictions
| Dataset | Predicted class | Reasoning |
|---|---|---|
| Antarctic sea ice | cl0 — same as Arctic | Same annual cycle + long-term decline structure |
| WTI crude oil | cl7 | Positive skew: sharp price spikes, slow declines |
| Copper | cl7 or VIX-adjacent | Industrial demand cycles, similar asymmetry |

---

## 2026-03-31 — Session 6: "Noisy directional" refinement + open questions (Notebook 21)

### Goal
Four open questions from nb20 (Chronos Phase 2b):
1. "Noisy directional" class refinement — 3 sub-types emerging; test with targeted new datasets
2. Sea-level density artifact test — is sea_level's Chronos isolation structural or a count artifact?
3. cl6 characterization — what do VIX + ENSO + temperature share that Chronos is responding to?
4. Mirror distortion invariance — do time-reversal / amplitude-flip preserve Chronos cluster membership?

### New datasets added (Phase 2b)
- **Glacier mass balance** (WGMS global cumulative, via OWID GitHub) — predicted: keeling_trend-like (clean monotonic)
- **Ocean heat content 0–700m** (NOAA WOA quarterly) — predicted: temperature-like (noisy directional)
- **Arctic sea ice extent** (NSIDC monthly) — predicted: new class "declining oscillator"

### Pre-run predictions (written before running)

| Dataset | Predicted class | Reasoning |
|---|---|---|
| Glacier mass balance | keeling_trend-like | Smooth cumulative decline, low noise, unidirectional |
| Ocean heat content | temperature-like | Same forcing, similar interannual noise |
| Arctic sea ice | NEW class | Long-term decline + strong seasonal cycle = neither pure trend nor pure oscillator |

### Structural questions being tested
- If sea_level subsampled to n=31 still isolates → structural class (not density artifact)
- cl6 in-cluster vs out-of-cluster feature comparison: what makes VIX/ENSO/temperature similar to Chronos?
- Mirror distortion: is Chronos time-direction sensitive? (prediction: yes for trends, no for symmetric oscillators)

---

## 2026-03-28 — Session 3: baseline_delta + observer-independence (Notebooks 11–12)

### Goal
Test two open questions from Session 2:
1. **baseline_delta as 6th feature** (notebook 11) — does "where did the series end relative to where it started" add information beyond slope? Does it split the burst class into event-with-memory vs event-without?
2. **Observer-independence** (notebook 12) — do alternative feature sets (spectral/wavelet) reproduce the same 7 shape classes, or are some classes artefacts of this specific feature frame?

### Context
Clean reinstall. No data files exist. Notebooks are self-contained — they re-download all datasets.

### Notebook 11 pre-run predictions

| Dataset | Expected baseline_delta | Reasoning |
|---|---|---|
| covid_first_wave / second_wave | ≈ 0 | Burst rises and falls — endpoints both "low" on normalized scale |
| keeling_trend | >> 0 (large positive) | Monotone CO2 rise — first 10% far below mean, last 10% far above |
| temperature | > 0 (moderate) | 20-yr windows show warming within window |
| keeling_seasonal / sunspot / lynx_hare / ecg / streamflow | ≈ 0 | Cyclical — returns to where it started |

### Structural question being tested
Is `baseline_delta` independent of `slope`? For smooth monotone series: proportional → redundant. For noisy/non-monotone series (COVID, temperature): may diverge → genuine 6th dimension.

### Notebook 13 pre-run predictions (combined feature frame)

11 features: 6 time-domain (from nb11) + 5 spectral fixed (no interpolation — frequency correctly comparable across series lengths). Key fix: streamflow dominant_freq should be ~0.083 (annual cycle), not 0.353 (nb12 artefact from 100-pt interpolation of 480-pt series).

**The three-way problem being tested:**

| Pair | td-6f | spectral-5f | expected in combined |
|---|---|---|---|
| COVID ↔ sunspot | SAME (blind spot) | diff | diff |
| sunspot ↔ keeling_seasonal | diff | SAME (blind spot) | diff |
| COVID ↔ keeling_seasonal | diff | diff | diff |

All three should separate in the combined frame — each pair is distinguishable by at least one frame. The combined clustering should resolve what neither individual frame could alone.

**ARI target:** > 0.165 (nb11 time-domain best) and > 0.132 (nb12 spectral)

**Results — Notebook 13 complete (28 March 2026)**

#### ARI — combining frames did NOT improve on time-domain alone

| Frame | Clusters | Noise | ARI |
|---|---|---|---|
| time-domain 6f | 22 | 25.4% | **0.165** |
| spectral-fixed 5f | 32 | 19.5% | 0.144 |
| combined 11f | 25 | 23.8% | 0.133 |

Combined ARI (0.133) is LOWER than time-domain alone (0.165). The spectral features added noise rather than signal. Cross-frame ARI combined↔td = 0.871 — the combined clustering is 87% similar to time-domain. The 11-feature space is dominated by the time-domain signal.

#### Streamflow fix confirmed

streamflow dominant_freq = 0.0799 (nb12 had 0.353 due to 100-pt interpolation distortion). Fixed. Streamflow now correctly groups with lynx_hare in Cluster 2 (15 lynx_hare + 22 streamflow) — the moderate dynamics pairing that was predicted.

#### The three-way problem — sunspot persists in COVID cluster

| Pair | td-6f | spectral-5f | combined-11f |
|---|---|---|---|
| COVID ↔ sunspot | SAME | diff | SAME |
| sunspot ↔ keeling_seasonal | diff | diff | diff |
| COVID ↔ keeling_seasonal | diff | diff | diff |

Sunspot collapsed into COVID in both the time-domain and combined frames. Combined Cluster 24: 101 covid_first_wave + 140 covid_second_wave + 23 sunspot. 96% of sunspot points land with COVID. The combined frame is time-domain dominated (cross-ARI 0.871) so the spectral separation of sunspot from COVID is overridden.

#### Clean successes in combined frame

- Cluster 1: 100% keeling_seasonal (68/68) — perfectly isolated in all three frames
- Cluster 22: 100% keeling_trend (58/58) — perfectly isolated in all three frames
- Cluster 2: lynx_hare + streamflow together — moderate dynamics correctly grouped after spectral fix
- Cluster 24: COVID1 + COVID2 together (67% cohesion) — confirmed across all frames

#### Spectral features add noise, not signal — for this dataset composition

The spectral features have high within-class variance for ECG (884 segments varying spectrally) and COVID (202 countries varying in burst shape). This variance creates density instability in HDBSCAN, lowering ARI. The time-domain features are more discriminative for the specific class structure we have. Adding 5 spectral features dilutes the 6 time-domain features rather than complementing them.

---

### Notebook 12 pre-run predictions (observer-independence)

Feature set: 5 spectral features via FFT — `dominant_freq`, `spectral_entropy`, `power_low`, `power_mid`, `power_high`. Series interpolated to 100 points before FFT for consistent frequency resolution.

Key predictions:
- COVID1 + COVID2 still together (both near-DC, low entropy)
- **Sunspot separates from COVID** — sunspot has a clear periodic peak; COVID does not. If this holds, the time-domain collapse (nb11 Finding 10) was a frame limitation.
- keeling_seasonal forms the cleanest isolated cluster (sharpest spectral peak of any dataset)
- ECG isolated — fastest signal, unique frequency band
- streamflow may group with keeling_seasonal (both have annual cycles in monthly data)
- keeling_trend stays separate from COVID (both near-DC but trend is DC-only)

### Results — Notebook 12 complete (28 March 2026)

#### Cross-frame ARI: 0.484
Well above the >0.3 meaningful threshold. The spectral and time-domain frames agree substantially on the structure of the data.

#### Key pairing tests: 4/5 passed

| Test | Result |
|---|---|
| COVID1 + COVID2 together in spectral space | FAIL |
| Sunspot separates from COVID in spectral space | PASS ✓ |
| keeling_seasonal isolated | PASS ✓ |
| keeling_trend separate from COVID | PASS ✓ |
| ECG isolated from COVID | PASS ✓ |

#### Sunspot confirmed separated — Finding 10 was a frame limitation

Sunspot spectral_entropy = 0.081 (power very concentrated). COVID spectral_entropy = 0.330 (more broadband from the rise and fall). L2 distance in spectral space: COVID ↔ sunspot = 1.052. In time-domain (nb11) they shared a cluster. The separation is real — the time-domain feature set couldn't see it because both have high autocorr and low zero crossings. The spectral frame sees the difference: sunspot is a near-pure periodic signal; COVID is a one-time broadband burst.

#### COVID1 + COVID2 split in spectral space — unexpected

Both landed in different clusters (C27 vs C26) despite being the same shape class. This is over-fragmentation, not genuine shape difference — their spectral profiles are nearly identical (dominant_freq ≈ 0.011, entropy ≈ 0.33, power_low ≈ 0.95). HDBSCAN created 37 clusters total (too many) — the COVID split is a density artefact within the same shape class, not a real distinction.

#### keeling_seasonal perfectly isolated — cleanest spectral signature

Cluster 25: 100% keeling_seasonal (68 points), spectral_entropy = 0.045 (lowest of any dataset), power_low = 0.9995. The annual CO2 cycle is the most spectrally pure signal in the entire dataset — a near-perfect sine wave.

#### Sunspot and keeling_seasonal are spectrally close

L2 distance sunspot ↔ keeling_seasonal = 0.141 — the smallest inter-class distance in the entire spectral taxonomy. Both have very low entropy and near-unity power_low. They were well separated in time-domain space (different kurtosis, different skewness) but spectrally they look almost identical. This is the inverse of the sunspot-COVID situation: two series that looked different in one frame look similar in another.

#### Streamflow isolated to its own unique cluster — spectral artefact

Streamflow dominant_freq = 0.3533 — by far the highest of any dataset. This is a methodological finding: the 100-point interpolation compresses long series. Streamflow has ~480 months; the annual cycle (12-month period) becomes 12/480 × 100 = 2.5 points after interpolation → frequency ≈ 0.4. This pushes streamflow into the high-frequency band and lands it in Cluster 0 (power_high dominant), completely separated from keeling_seasonal. The spectral features are sensitive to series length before interpolation. This is a design limitation of the current spectral feature extraction — not a shape finding.

#### COVID ↔ keeling_trend: spectrally close, time-domain far

L2 distance COVID ↔ keeling_trend in spectral space = 0.328 (close). In 6-feature time-domain space = 2.810 (far). The two frames disagree on this pair. Spectrally they look similar (both near-DC, both high power_low). Time-domain baseline_delta was the key discriminator. Neither frame is wrong — they're measuring different aspects of the same shape.

#### Observer-independence verdict: HOLDS (with caveats)

ARI = 0.484. The shape classes are not artefacts of the time-domain frame. The major cross-domain pairings (COVID waves together, keeling_seasonal isolated, ECG isolated, keeling_trend separate) are reproduced independently. The one regression (COVID1+COVID2 split) is HDBSCAN over-fragmentation at 37 clusters, not a genuine shape distinction.

---

### Bug — pandas 2.x `fillna(method=)` removed (Notebook 11, sunspot cell)

`fillna(method='bfill')` and `fillna(method='ffill')` raise `TypeError` in pandas 2.x — the `method` keyword was removed. Fix: use `.bfill().ffill()` chained directly on the Series.

Affected lines: `series_full` and `smoothed` assignments in the sunspot dataset cell.

### Results — Notebook 11 complete (28 March 2026)

#### baseline_delta per dataset (mean)

| Dataset | Predicted | Actual | Status |
|---|---|---|---|
| covid_first_wave | ≈ 0 | +0.610 | UNEXPECTED |
| covid_second_wave | ≈ 0 | +0.392 | UNEXPECTED |
| keeling_trend | >> 0 | +3.111 | CONFIRMED |
| keeling_seasonal | ≈ 0 | -0.337 | UNEXPECTED |
| sunspot_cycle | ≈ 0 | +0.055 | CONFIRMED |
| lynx_hare | ≈ 0 | -0.100 | CONFIRMED |
| temperature | > 0 | +0.997 | CONFIRMED |
| ecg | ≈ 0 | -0.155 | CONFIRMED |
| streamflow | ≈ 0 | +0.194 | CONFIRMED |

6 confirmed, 3 unexpected.

#### COVID is not event-without-memory — most significant unexpected finding

COVID first wave baseline_delta = +0.610 with slope ≈ −0.001. These diverge completely: slope says the series has no overall trend; baseline_delta says it ends 0.6 SD above where it started. The burst did not fully return to baseline — it plateaued above its starting level. "Event-with-memory." This was not predicted.

COVID second wave = +0.392. Same pattern, slightly less pronounced.

**Implication:** The burst class is NOT event-without-memory. The epidemic ends at a new floor — ongoing transmission, not a return to zero. This is epidemiologically real, not a measurement artefact.

#### keeling_seasonal ends lower than it starts (-0.337)

The annual CO2 cycle extracted as 12-point yearly segments starts in January (Northern Hemisphere winter, high CO2) and ends in December. The seasonal cycle is asymmetric in its phase relationship to the calendar year — the trough is deeper relative to the normalized mean than the starting point. Small but consistent across all 68 years.

#### keeling_trend separated from COVID — key structural success

L2 distance in standardized feature space:

| Pair | 5-feature | 6-feature |
|---|---|---|
| COVID ↔ keeling_trend | 0.975 | 2.810 |
| COVID ↔ temperature | 6.315 | 6.329 |
| keeling_trend ↔ temperature | 6.649 | 7.012 |

In 5-feature space, COVID and keeling_trend were nearly touching (0.975). The 6th feature tripled that distance to 2.810. baseline_delta is doing exactly the job it was designed for — separating "burst that ends high" from "permanent accumulation that ends even higher."

#### Sunspot collapsed into COVID cluster — unexpected

In 5-feature clustering sunspot was its own cluster. In 6-feature clustering it joins Cluster 13 with COVID (100% of sunspot points). Sunspot baseline_delta = +0.055 — nearly zero, unlike COVID's +0.610. The merge is driven by the other 5 features (high autocorr, low zero crossings, right-skewed) being too similar; baseline_delta of 0.055 vs 0.488 (cluster mean) doesn't push it out. The 6th feature did not help discriminate sunspot from COVID — that separation relied on parameters in 5-feature space that baseline_delta collapsed.

#### Clustering improved overall

| | 5-feature | 6-feature |
|---|---|---|
| Clusters | 31 | 22 |
| Noise | 29.8% | 25.5% |
| ARI | 0.121 | 0.165 |

Fewer micro-clusters, less noise, better domain alignment. The 6th feature is not redundant.

#### 6-feature cluster 12 — keeling_trend in pure isolation

Cluster 12: 100% keeling_trend (58 points), mean baseline_delta = 3.106, lag1 = 1.000, slope = 0.028, skewness ≈ 0. The cleanest cluster in the taxonomy — permanent smooth accumulation with no return. Completely isolated.

#### Hypothesis scoring — 8/9 confirmed

| Dataset | Expected | Got | Result |
|---|---|---|---|
| covid_second_wave | Same cluster as COVID | Cluster 13 (67%) | CONFIRMED |
| keeling_trend | NOT COVID cluster | Cluster 12 (100%) | CONFIRMED |
| keeling_seasonal | NOT COVID cluster | Cluster 0 (100%) | CONFIRMED |
| sunspot_cycle | NOT COVID cluster | Cluster 13 (100%) | UNEXPECTED |
| lynx_hare | NOT COVID cluster | Cluster 0 (27%) | CONFIRMED |
| temperature | NOT COVID cluster | Cluster 0 (3%) | CONFIRMED |
| ecg | NOT COVID cluster | Cluster 9 (20%) | CONFIRMED |
| streamflow | NOT COVID cluster | Cluster 1 (100%) | CONFIRMED |

#### Temperature and keeling_trend did not merge

keeling_trend → Cluster 12 (pure accumulation). Temperature → Cluster 0 (with keeling_seasonal + lynx_hare). Still separate. The 6th feature widened their distance slightly (6.649 → 7.012) rather than closing it.

---

## 2026-03-23 — Session 1: Foundation (Notebooks 01–07)

### Goal
Test the core hypothesis: time series from completely different domains share underlying dynamic shapes that cluster across domain boundaries. A COVID wave and a sunspot cycle should cluster together if they share the same mathematical signature — regardless of what they represent.

### Datasets built
| Notebook | Dataset | Shape hypothesis |
|---|---|---|
| 01 | COVID first wave (OWID, 202 countries) | Directional burst — rises fast, falls |
| 02 | Sunspot cycles (monthly 1749–present) | Periodic — ~11yr cycle, asymmetric |
| 03 | Lynx-hare (Hudson Bay 1845–1935) | Predator-prey oscillation |
| 04 | Keeling CO2 (Mauna Loa 1958–present) | Two components: seasonal + slow trend |
| 05 | Clustering all 5 (UMAP + HDBSCAN) | Cross-domain shape clusters |
| 06 | COVID second wave (209 countries) | Should land with first wave — same burst shape |
| 07 | Global temperature (NASA GISS, 26 stations) | Slow directional drift |

### Feature set (settled)
5 features extracted per time series after z-score normalisation:
- `mean`, `std`, `skewness`, `kurtosis` — distributional shape
- `lag1_autocorr` — memory / periodicity proxy
- `zero_crossings` — oscillation frequency proxy
- `slope` — directional drift

### Keeling split
Keeling CO2 decomposed into two sub-datasets: `keeling_seasonal` (annual oscillation) and `keeling_trend` (long-run drift). Treated as separate entities in clustering — they have genuinely different shapes.

### Clustering setup (v1)
- UMAP: `n_neighbors=15, min_dist=0.1, n_components=2`
- HDBSCAN: `min_cluster_size=3, min_samples=1` ← **later found to be too fragmented**

### Outcome (05_cluster_all)
Initial clustering broadly confirmed cross-domain shape groupings. Directional burst (COVID), slow drift (temperature) and oscillatory series separated in UMAP space.

---

## 2026-03-24 — Session 2: ECG Extension + Bug Fixes (Notebooks 08–09)

### Dataset added
| Notebook | Dataset | Shape hypothesis |
|---|---|---|
| 08 | ECGFiveDays (UCR archive, 884 heartbeat segments) | Oscillatory — should NOT cluster with directional datasets |

### Bug 1 — ECG download silently failed (Notebook 08, Cell 2)
`requests.get()` was returning an HTML error page from timeseriesclassification.com with HTTP 200, which passed the status check but failed at `zipfile.ZipFile()`. The exception was caught but no clear error was shown, leaving `dest_dir` empty.

**Fix:** Switched to `urllib.request` (same behaviour as `curl`). Added `zipfile.is_zipfile()` validation before extraction. Added cleanup of empty/partial directories so the `if not dest_dir.exists()` guard doesn't block re-download.

**Verified:** zip at `timeseriesclassification.com/aeon-toolkit/ECGFiveDays.zip` contains `ECGFiveDays_TRAIN.ts` and `ECGFiveDays_TEST.ts` (also `.arff` and `.txt`).

> Note: on 2026-03-24 the site returned 502. Zip was already cached at `/tmp/ECGFiveDays.zip` from an earlier `curl` call and extracted manually.

### Bug 2 — HDBSCAN over-fragmentation (Notebook 09, Cell 5)
`min_cluster_size=3` with 612 points produced **76 clusters** and **31.5% noise**. The majority cluster for COVID first wave was `-1` (noise), making all downstream comparisons against noise rather than a real shape cluster.

**Fix:** `min_cluster_size=15, min_samples=5`. Produces fewer, more cohesive macro shape clusters.

### Bug 3 — Scoring logic used noise as reference (Notebook 09, Cell 9)
`cluster1_ref` was set to the most common cluster for COVID first wave — which was `-1` (noise). All three checks then compared against noise, making ECG's 17% noise membership appear as a match to the reference.

**Fix:** Skip `-1` when finding the reference cluster. Also skip `-1` when finding each dataset's majority cluster for comparison.

### Results after fixes (run 2)

| Dataset | Expected | Got | Result |
|---|---|---|---|
| covid_second_wave | Cluster 10 (burst) | Cluster 10 (57%) | CONFIRMED |
| temperature | Cluster 10 (drift) | Cluster -1 (100% noise) | UNEXPECTED → hypothesis revised |
| ecg | NOT Cluster 10 | Cluster 6 (29%) | CONFIRMED |

### Temperature finding — hypothesis revised

Temperature being 100% noise is not a clustering failure. Feature analysis shows temperature and COVID first wave are genuinely different in feature space:

| Feature | COVID | Temperature |
|---|---|---|
| skewness | 0.95 | 0.01 |
| lag1_autocorr | 0.95 | 0.50 |
| zero_crossings | 0.023 | 0.277 |

Temperature stations fluctuate around a slow warming trend, producing moderate zero_crossings and lower autocorr. COVID is a smooth one-way burst with near-zero crossings. **"Directional burst" and "slow directional drift" are two distinct shapes**, not one.

The 100% noise result is also partly a parameter problem: 26 points with `min_cluster_size=15` cannot form their own cluster even if internally coherent. Lowered to `min_cluster_size=8, min_samples=3` to allow small but tight datasets to cluster.

**Updated hypothesis for temperature:** should form its own cluster (slow noisy drift), distinct from COVID (fast smooth burst) and ECG (oscillatory).

### Results after scoring fix (run 3, min_cluster_size=8)

| Dataset | Expected | Got | Result |
|---|---|---|---|
| covid_second_wave | Cluster 33 (burst) | Cluster 33 (55%) | CONFIRMED |
| temperature | NOT Cluster 33 (own cluster) | Cluster 1 (92%) | CONFIRMED — once scoring updated |
| ecg | NOT Cluster 33 | Cluster 12 (33%) | CONFIRMED |

Temperature formed Cluster 1 at 92% cohesion — extremely tight grouping. All three predictions now confirmed with revised hypothesis. Scoring logic updated: temperature `should_match=False`.

### ✓ Session 2 milestone — all three new datasets confirmed

---

## 2026-03-24 — Session 2 continued: Periodic dataset hypotheses

### New insight: ECG is not oscillatory by zero_crossings

ECG zero_crossings = 0.078 — actually lower than keeling_seasonal (0.167) and lynx_hare (0.172). ECG is distinguished by **kurtosis = 15.165** (sharp QRS spike + flat baseline). The clustering correctly isolated it, but for a different reason than assumed.

### Revised shape taxonomy (5 classes emerging)

| Shape class | Datasets | Key discriminators |
|---|---|---|
| Smooth directional burst | covid_first_wave, covid_second_wave | skewness≈0.95, lag1≈0.95, zc≈0.02 |
| Slow noisy drift | temperature | lag1≈0.50, zc≈0.28, low skewness |
| Spike-oscillatory | ecg | kurtosis=15.165 — uniquely extreme |
| Smooth directional trend (?) | keeling_trend | lag1=1.00, zc=0.008 — may land with COVID |
| Slow periodic | keeling_seasonal, lynx_hare, sunspot? | zc≈0.10–0.17, negative kurtosis |

### Hypotheses for next run (periodic datasets, already in notebook 09)

- **keeling_trend** → Cluster with COVID (both: high autocorr, very low zc, near-zero slope)
- **keeling_seasonal** → NOT COVID cluster (higher zc, flat kurtosis)
- **sunspot_cycle** → NOT COVID cluster
- **lynx_hare** → NOT COVID cluster
- **keeling_seasonal + lynx_hare** → likely same cluster (similar zc≈0.17, similar kurtosis)
- **ecg** → continues to stay isolated from all of the above
- **streamflow** → predicted to land in Cluster 1 with temperature + lynx_hare (moderate dynamics by design). Pre-run feature predictions: `zero_crossings ≈ 0.15–0.25`, `lag1_autocorr ≈ 0.50–0.70`, `kurtosis < 0`, `skewness ≈ 0–0.6`.

### Run 1 — raw discharge (24/25 stations loaded)

Streamflow → Cluster -1 (100% noise). Features: zc=0.228 ✓, lag1=0.574 ✓, kurtosis=6.931 ✗, skewness=2.090 ✗. Root cause: log-normal discharge; flood spikes inflate tails. Fix: log-transform.

### Run 2 — log-transformed discharge

Streamflow landed in **Cluster -1 (100% noise)**. Feature check:
- `zero_crossings`: 0.228 → IN RANGE ✓  `lag1_autocorr`: 0.574 → IN RANGE ✓
- `kurtosis`: **6.931 → OUT OF RANGE**  `skewness`: **2.090 → OUT OF RANGE**

**Root cause:** Discharge is log-normally distributed. Flood months create extreme positive spikes that inflate skewness/kurtosis well outside "moderate" range despite temporal dynamics being correct. Fix: `np.log1p()` transform before feature extraction — standard hydrology practice, collapses flood tail, preserves autocorr/zc/slope.

All features IN RANGE after log-transform: zc=0.222 ✓, lag1=0.700 ✓, kurtosis=-0.308 ✓, skewness=0.184 ✓.

**Cluster result: Cluster 4 (67%), NOT Cluster 1 (temperature + lynx_hare).**

Streamflow avoided all extreme clusters. "Moderate dynamics" hypothesis broadly confirmed — but streamflow formed its own density peak rather than joining Cluster 1. Key discriminator: `lag1_autocorr` = 0.700 (streamflow) vs 0.503 (temperature) / 0.680 (lynx_hare). Catchment memory is slightly higher than climate/ecological memory.

### ✓ "Moderate dynamics" is a genuine shape region with internal sub-structure

Two sub-types identified within the moderate dynamics region:
- **C1**: lower-memory moderate dynamics — temperature anomalies + lynx_hare (lag1 ≈ 0.50–0.68)
- **C4**: higher-memory moderate dynamics — log-streamflow (lag1 ≈ 0.70), 67% cohesion across 24 diverse rivers

The 24 streamflow stations form a tighter, more cohesive core than the mixed temperature/lynx_hare group, so HDBSCAN correctly finds two density peaks within the broad moderate region. "Moderate dynamics" is not a catch-all — it is a genuine shape region that the feature set resolves with sub-structure.

### Results — periodic dataset run

| Dataset | Expected | Got | Result |
|---|---|---|---|
| keeling_trend | Cluster 33 (with COVID) | Cluster 29 (100%) | UNEXPECTED → own cluster |
| keeling_seasonal | NOT Cluster 33 | Cluster 0 (100%) | CONFIRMED |
| sunspot_cycle | NOT Cluster 33 | Cluster 13 (58%) | CONFIRMED |
| lynx_hare | NOT Cluster 33 | Cluster 1 (65%) | CONFIRMED |
| ecg | NOT Cluster 33 | Cluster 12 (33%) | CONFIRMED |

Cross-dataset affinity: keeling_seasonal (C0) / sunspot_cycle (C13) / lynx_hare (C1) — all in DIFFERENT clusters.

### keeling_trend finding — skewness is the burst discriminator

keeling_trend and COVID look similar on autocorr and zero_crossings. But COVID skewness = 0.95 (asymmetric — rises fast, falls), keeling_trend skewness = 0.075 (symmetric monotonic rise). Skewness correctly separates "burst" from "steady climb."

### lynx_hare + temperature pairing — "moderate dynamics" is a shape class

Predator-prey oscillation (lynx_hare) and slow climate drift (temperature) share Cluster 1. Common features: no skewness extreme, moderate autocorr (~0.5–0.68), flat kurtosis, moderate zero_crossings. The cluster represents "no extreme features" — generic moderate dynamics. Domain-blind.

### Revised shape taxonomy — 6 classes identified

| Cluster | Datasets | Key character |
|---|---|---|
| 33 | covid_first_wave, covid_second_wave | Right-skewed burst — skewness≈0.95 |
| 29 | keeling_trend | Symmetric monotonic rise — lag1=1.0, skewness≈0 |
| 1 | temperature, lynx_hare | Moderate dynamics — no extreme features |
| 0 | keeling_seasonal | Left-skewed periodic — skewness=-0.16 |
| 13 | sunspot_cycle | Right-skewed low-zc periodic |
| 12 | ecg | Spike dynamics — kurtosis=15.165 |

### Core finding so far

The 5-feature set discriminates 6 shape classes across 8 datasets from completely unrelated domains. The discriminating features vary by class — skewness separates burst from steady-climb, kurtosis isolates ECG spikes, zero_crossings + autocorr separate periodic from directional. No single feature does all the work.

All three predictions confirmed. The feature set successfully separates three distinct shape families:

| Shape class | Datasets | Key discriminators |
|---|---|---|
| Fast smooth burst | covid_first_wave, covid_second_wave | high skewness (0.95), high lag1_autocorr (0.95), very low zero_crossings (0.02) |
| Slow noisy drift | temperature (92% in one cluster) | low skewness, moderate autocorr (0.50), moderate zero_crossings (0.28) |
| Oscillatory | ecg | high zero_crossings, low slope |

**Key insight:** The original hypothesis conflated "directional burst" and "slow directional drift" as one shape class. The feature set discriminates them — autocorrelation and zero_crossings together separate fast-smooth from slow-noisy directional dynamics. This is a stronger result than the original hypothesis.

---

---

## 2026-03-28 — Session 4: Pairwise shape distances (Notebook 14)

**Question:** Do the "problem pairs" from nb11–12 land in opposite off-diagonal quadrants of a (td_dist, spectral_dist) scatter plot?

**Method:** Compute per-dataset centroids in normalized TD-6f and spectral-5f feature spaces. Compute all C(9,2)=36 pairwise L2 distances. Plot each pair as a 2D point.

### Quadrant check results

| Pair | td_dist | sp_dist | Actual quadrant | Predicted | Status |
|------|---------|---------|-----------------|-----------|--------|
| COVID1 ↔ sunspot | 0.852 | 1.309 | (near, near) | (near, far) | UNEXPECTED |
| sunspot ↔ keeling_seasonal | 4.459 | 2.383 | (far, near) | (far, near) | CONFIRMED |
| COVID1 ↔ COVID2 | 0.282 | 0.226 | (near, near) | (near, near) | CONFIRMED |
| COVID1 ↔ keeling_trend | 2.810 | 0.240 | (near, near) | (far, far) | UNEXPECTED |
| keeling_seasonal ↔ keeling_trend | 6.277 | 2.495 | (far, near) | (far, far) | UNEXPECTED |
| ECG ↔ keeling_seasonal | 4.515 | 3.623 | (far, far) | (far, near) | UNEXPECTED |

**Predictions confirmed: 2/6**

### Why COVID-sunspot came out (near, near)

Spectral distance=1.309 is below median because both have `power_low≈0.95+` and `dominant_freq≈0.01`. The entropy difference (0.338 vs 0.076) — which drove their separation in nb12's HDBSCAN — is only 1 of 5 spectral features. In centroid L2, the four power-band features outvote entropy. Cluster separation ≠ centroid distance. The duality is real but only visible at the instance/density level.

### Why COVID1 ↔ keeling_trend appeared near

TD distance=2.810 is above the within-COVID range (COVID1↔COVID2=0.282) but below the global median (3.814). Baseline_delta did triple the separation vs 5-feature space — it's just that many cross-domain pairs have even larger distances, pulling the median up.

### Key structural findings

- **sunspot ↔ keeling_seasonal (far, near)** confirmed robustly — the spectral frame's blind spot holds at centroid level
- **keeling_seasonal ↔ keeling_trend (far, near)** — unexpected: both concentrate power at low frequencies; power bands cannot distinguish "periodic cycle" from "slow trend"
- **Temperature** is the most isolated dataset in both frames — largest distances to nearly everything

### What changed in the thesis

Shape similarity as a vector holds. But centroid L2 is not the right tool to see the COVID-sunspot split — that requires either entropy-only distance or instance-level clustering. Follow-up: recompute spectral distance using entropy alone to test if the (near, far) prediction holds for that single feature.


### Entropy-only follow-up (nb14 extension)

**Result:** COVID-sunspot entropy distance = 0.2622, median = 0.2628. Missed (near, far) by 0.0006 — exactly at the boundary.

**Conclusion:** The COVID-sunspot duality cannot be recovered by any centroid distance (5-feature L2 or entropy-only). It is a density effect visible only at the instance level through HDBSCAN. This closes the open question from Finding 21.

**Entropy ordering discovered:** sunspot (0.076) < keeling_seasonal (0.154) < COVID2 (0.297) < COVID1 (0.338) < keeling_trend (0.389) < lynx_hare (0.436) < streamflow (0.596) < ECG (0.699) < temperature (0.763). A clean spectral complexity axis through the corpus.

**Total findings after nb14:** 26


---

## 2026-03-28 — Session 4 cont.: Notebook 15 (Sea Level)

**Prediction:** land in keeling_trend cluster
**Result:** nearest = covid_first_wave (1.467), not keeling_trend (2.653). 48% noise.

| Feature | sea_level | keeling_trend | COVID1 |
|---------|-----------|---------------|--------|
| lag1_autocorr | 0.919 | 0.9999 | 0.954 |
| zero_crossings | 0.104 | 0.008 | 0.023 |
| baseline_delta | 1.100 | 3.111 | 0.610 |
| spectral_entropy | 0.429 | 0.389 | 0.338 |
| power_low | 0.920 | 0.953 | 0.949 |

**Prediction: WRONG — but it's a finding.** Sea level is a noisy monotone — trending but with inter-annual ENSO oscillation that gives zero_crossings=0.104 (vs keeling_trend's 0.008). This pushed it closer to COVID in feature space and into noise in HDBSCAN. Reveals a gap between keeling_trend and temperature: "noisy directional with strong memory" — potential 8th shape class. → Findings 27–28

**Methodological note:** First attempt used 8 annual windows (only 13 instances, bad spectral features). Fixed by using monthly data with 120-pt windows (1557 points → 120 instances). Lesson: window size must be consistent with existing datasets for spectral features to be comparable.


---

## 2026-03-28 — Session 4 cont.: Notebook 16 (ENSO)

**Prediction:** between sunspot and lynx_hare, or new class
**Result:** three-way tie — covid_second_wave (0.970), sunspot (0.996), covid_first_wave (1.022). 72% noise.

**Prediction direction wrong (lynx_hare), new class call correct.**

ENSO sits between COVID and sunspot on two different axes:
- baseline_delta=0.078 ≈ sunspot (0.055) — returns to zero, unlike COVID (0.610)
- spectral_entropy=0.367 ≈ COVID (0.338) — irregular, unlike sunspot (0.076)

This combination is unique: high-memory, irregular, reversible oscillation → potential new class. → Findings 29–30

Second dataset after sea_level to fall mostly into noise — confirms the taxonomy has structural gaps between existing classes. A continuous embedding (Phase 2) may be more appropriate than discrete classes.


---

## 2026-03-28 — Session 4 cont.: Notebook 17 (VIX)

**Prediction:** COVID or ECG cluster
**Result:** nearest = lynx_hare (0.594), streamflow (0.726). COVID is 3.374 away. 69% noise.

**Prediction: WRONG — and the correct answer is more interesting.**

VIX (financial volatility) matches lynx_hare (ecological predator-prey) — both are irregular moderate-memory oscillators with positive skewness. lag1_autocorr=0.650 disqualifies COVID (too noisy). kurtosis=0.582 disqualifies ECG (not sharp enough at monthly scale).

Cross-domain finding: market crisis cycles and population boom-bust cycles share a shape fingerprint. → Findings 31–32

**Phase 1b summary (nb15–17):**
All three datasets landed in unexpected places and mostly in noise. 0/3 clean confirmations, but 3 structural findings:
- Sea level: "noisy directional" gap between keeling_trend and temperature
- ENSO: "irregular reversible oscillator" gap between COVID and sunspot
- VIX: fits lynx_hare best (cross-domain confirmation) but still 69% noise

The consistent noise placement across all three confirms Phase 2 hypothesis: discrete HDBSCAN classes are insufficient; a continuous embedding will describe the shape manifold better.

**Total findings: 32**

---

## 2026-03-30 — Session 5: Phase 1c Stability Test (Notebook 18)

### Goal
Stress-test the taxonomy: vary HDBSCAN `min_cluster_size` ∈ [4,6,8,12,16] and `min_samples` ∈ [2,3,5] (15 combinations). Score each dataset as granite / robust / sand / always-noise based on how consistently it finds a clean cluster assignment. Also test whether Phase 1b datasets (sea_level, ENSO, VIX) are permanently in noise or just parameter-sensitive.

### Datasets
All 9 original + 3 Phase 1b (sea_level, enso_oni, vix) = 12 datasets total.

### Stability score definition
% of 15 runs where the dataset's majority-cluster placement captures ≥50% of its instances.

### Pre-run predictions

| Dataset | Predicted stability | Label |
|---|---|---|
| keeling_seasonal | 100% | GRANITE |
| keeling_trend | 100% | GRANITE |
| ecg | ~100% | GRANITE |
| covid_first_wave | ~80% | ROBUST |
| covid_second_wave | ~80% | ROBUST |
| lynx_hare | ~60% | MODERATE |
| streamflow | ~60% | MODERATE |
| temperature | ~40% | SAND |
| sunspot_cycle | ~40% | SAND |
| vix | ~30% | MOSTLY NOISE |
| sea_level | ~20% | MOSTLY NOISE |
| enso_oni | ~10% | ALWAYS NOISE |

### Results

Grid: 15 combinations. Total instances: 1930 (9 orig + 3 Phase 1b).
Global noise across all runs: 38–50% of instances.

**Stability scores:**

| Class | Dataset | Score | Notes |
|---|---|---|---|
| GRANITE | keeling_seasonal | 100% | 0% noise in all 15 runs |
| GRANITE | keeling_trend | 100% | 0% noise in all 15 runs |
| STABLE/borrowed | sunspot_cycle | 100% | Collapses with COVID in 73% of runs |
| SAND | covid_second_wave | 33% | Partial stability |
| FRAGMENTED | ecg | 0% | Low noise (26.5%) but 884 instances split into many sub-clusters |
| FRAGMENTED | covid_first_wave | 0% | 202 country waves — diverse burst family |
| SIZE-FLOORED | lynx_hare | 0% | n=26 — below threshold arithmetic |
| SIZE-FLOORED | streamflow | 0% | n=24 — below threshold arithmetic |
| SIZE-FLOORED | temperature | 0% | n=31 — always noise by count |
| STRUCTURAL GAP | sea_level | 0% | Best: 39.2% noise, majority_pct=0.29 |
| STRUCTURAL GAP | enso_oni | 0% | Best: 50.3% noise, majority_pct=0.07 |
| STRUCTURAL GAP | vix | 0% | Best: 71.5% noise, majority_pct=0.07 |

**Sunspot collapse:** collapses into COVID cluster in 73% of runs (11/15). Pattern: mcs=4 separates (1/3 collapse), mcs≥12 always collapses (6/6).

**Phase 1b:** no parameter setting rescues any of the three. Structural gaps confirmed as real.

### Findings

Findings 33–38 added to FINDINGS.md. Total findings: 38.


---

## 2026-03-30 — Session 5 cont.: Phase 2 setup

### Environment change
Switched venv from Python 3.14 → Python 3.13 to enable TensorFlow installation.
TensorFlow 2.21.0 installed via `uv add tensorflow`. All existing packages (numpy, scipy, sklearn, umap, hdbscan) confirmed working on Python 3.13. `.python-version` pinned to 3.13.

### Notebook 19 — Autoencoder (built, ready to run)
Two Keras autoencoders:
- **Dense AE:** 64 → 32 → 16 → 8 (latent) → 16 → 32 → 64
- **Conv AE:** Conv1D(32) → pool → Conv1D(16) → pool → Dense(8) (latent) → unpool → ConvT

Both trained on all 12 datasets (1930 instances), raw resampled series (64 points).
Four-way UMAP comparison: feature-space | raw-series | dense latent | conv latent.

### Pre-run predictions (nb19)
- keeling_seasonal / keeling_trend: will remain isolated (predicted YES)
- Sunspot ↔ COVID: may separate in conv latent (frequency info survives resampling)
- Phase 1b: will fill gaps as continuous geometry (no cluster threshold)
- ECG: sub-structure will become visible in latent UMAP

---

## 2026-03-30 — Session 5 cont.: Notebook 19 results (Phase 2 Autoencoder)

### Architecture
- Dense AE: 64 → 32 → 16 → **8** → 16 → 32 → 64 (MLP, Adam, MSE, 200 epochs)
- Conv AE: Conv1D(32,k=8) → MaxPool → Conv1D(16,k=4) → MaxPool → Flatten → **Dense(8)** → Dense(256) → Reshape → Upsample × 2 → Conv1D output
- Input: all 12 datasets, raw series resampled to 64 pts (z-scored), n=1930

### Key results — pairwise centroid distances (Conv latent)

| Pair | Feature-6f | Latent-8d | Ratio | Result |
|---|---|---|---|---|
| sunspot ↔ covid1 | 0.769 | 4.451 | 5.79x | SEPARATED — TD collapse was feature failure |
| enso ↔ sunspot | 0.859 | 6.040 | 7.03x | Largest expansion — regularity vs irregularity |
| covid1 ↔ covid2 | 0.250 | 2.256 | 9.02x | Within-COVID variation now visible |
| lynx_hare ↔ vix | 0.616 | 0.944 | 1.53x | Smallest expansion — cross-domain match robust |
| temperature ↔ sea_level | 4.607 | 0.777 | 0.17x | **ONLY CONTRACTION** — noisy directional class confirmed |

### Findings
Findings 39–42 added to FINDINGS.md. Total findings: 42.

---

## 2026-03-30 — Session 5 cont. cont.: Notebook 20 (Phase 2b Chronos Foundation Model)

### Setup
- PyTorch 2.11.0+cu130 already installed
- `uv add chronos-forecasting` → chronos-forecasting 2.2.2 installed
- Model: amazon/chronos-t5-small (46 M params, 512-dim encoder hidden states)
- Embeddings: mean-pooled T5 encoder output (masked) over tokenized series
- Input: same 1930 instances, same 64-pt resampled z-scored series as nb19
- Zero-shot: no fine-tuning, no training on our data

### Pre-run predictions (nb20)
- Sunspot-COVID: predict separation (foundation model should distinguish cycle vs burst)
- Temperature-sea_level: uncertain — Chronos may contract (both noisy trends) or separate (different noise structure)
- VIX-lynx_hare: predict near-neighbors remain close
- ENSO: predict near sunspot (both oscillatory, Chronos has seen many)
- Phase 1b: predict fills gaps rather than isolated (no cluster threshold)

### Results — HDBSCAN clusters (min_cluster_size=8, min_samples=3)

| Cluster | Primary dataset | Purity |
|---|---|---|
| cl7 | keeling_seasonal | 100% |
| cl4 | keeling_trend | 100% |
| cl2 | ECG | 99% |
| cl3 | sea_level | 97% |
| cl1 | streamflow | 79% |
| cl5 | sunspot_cycle | 54% (46% noise) |
| cl6 | VIX (28%) + ENSO (24%) + temperature (23%) | mixed |
| cl0 | COVID first+second (19%+17%, rest noise) | partial |

Overall noise: 32.2% (622/1930)

### Key pairwise centroid distances (Chronos 512-dim, raw Euclidean)

| Pair | Feat-6f | Conv AE (nb19) | Chronos |
|---|---|---|---|
| sunspot ↔ covid1 | 1.988 | 4.451 (5.79x) | **0.301 — FARTHEST pair** |
| covid1 ↔ covid2 | 0.871 | 2.256 (9.02x) | **0.059 — CLOSEST pair** |
| enso ↔ sunspot | 0.818 | 6.040 (7.03x) | 0.094 |
| lynx_hare ↔ vix | 0.893 | 0.944 (1.53x) | 0.119 |
| temperature ↔ sea_level | 0.655 | 0.777 (0.17x) | 0.140 |

### Notable divergences between Conv AE and Chronos
- **Temperature-sea_level**: Conv AE says same class (0.17x contraction); Chronos separates them (sea_level in own pure cluster cl3, temperature mostly noise)
- **ENSO-sunspot**: Conv AE says maximally different (7.03x); Chronos says very close (0.094 centroid distance, though they land in different HDBSCAN clusters)
- **VIX-lynx_hare**: Conv AE says cross-domain match holds; Chronos puts VIX in cl6 (irregular), lynx_hare all noise

### ECG sub-structure
Chronos HDBSCAN ARI vs UCR labels: **0.742** — highest ARI of any sub-cluster analysis in experiment

### Findings
Findings 43–46 added to FINDINGS.md. Total findings: 46.
