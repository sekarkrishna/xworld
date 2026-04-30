# The Terrain Is Real, the Vocabulary Is the Receptor's: An Empirical Shape Taxonomy for Time Series Across Unrelated Domains

*A research paper based on 40 notebooks, 121 findings, and 17 real-world datasets across 8 unrelated domains.*

*April 2026*

---

## Abstract

Do time series from completely unrelated domains share underlying dynamic shapes that cluster together, independent of what they represent? Does a glacier melting and a turtle breathing share the same numerical signature? Can you read the nature of a system from the shape of its ripple?

XWorld is an empirical investigation of this question. Starting from 9 datasets spanning epidemiology, astronomy, ecology, climate science, hydrology, and cardiology, the project extracts a minimal 6-feature fingerprint from z-score normalised time series and clusters them using UMAP + HDBSCAN. The central finding: time series cluster by dynamic shape, not by domain of origin. COVID epidemic waves and sunspot cycles, financial volatility and predator-prey population dynamics, glacier retreat and atmospheric CO2 accumulation — all land in mathematically predictable regions of an 8-class shape taxonomy that maps directly onto the complex eigenvalue plane of ordinary differential equations.

The taxonomy has been validated by four independent measurement architectures (hand-crafted time-domain features, a convolutional autoencoder, Amazon's Chronos foundation model, and a combined topological/recurrence-quantification framework), stress-tested across 15 HDBSCAN parameter combinations, and grounded in ODE theory. The four architectures converge on the same discriminative resolution (ARI 0.410–0.415), and all independently identify the trend-family boundary as the most robust observer-independent division. 12 of 17 real-world datasets are classified robustly regardless of observation window. The remaining 5 are periodic signals whose classification depends on the analyst's window length — a finding that itself reveals the boundary between observer-independent and observer-relative properties of dynamical systems.

---

## 1. The Question

Time series are everywhere. An epidemic curve, a heartbeat, a stock market index, the annual CO2 cycle, the 11-year sunspot rhythm, the boom-and-bust of predator-prey populations, the slow rise of sea level. Each belongs to a domain with its own vocabulary, its own experts, its own journals.

But strip the labels. Normalise the amplitude. Look only at the shape — the temporal pattern of rise, fall, oscillation, memory, and return. Do unrelated systems converge on the same dynamic forms?

This is not a new question in spirit. Universality classes in statistical physics, normal forms in bifurcation theory, and the classification of attractors in dynamical systems theory all suggest that the space of possible dynamics is far smaller than the space of possible systems. XWorld asks whether this compression is detectable empirically, using simple statistics, across domains that have never been compared.

---

## 2. Method

### 2.1 Feature Representation

Each time series is z-score normalised (removing amplitude, preserving shape) and characterised by 6 features:

| Feature | What it captures |
|---|---|
| Skewness | Asymmetry — does the series rise faster than it falls? |
| Kurtosis | Tail weight — sharp spikes vs smooth undulations |
| Lag-1 autocorrelation | Memory — how much does the next value depend on the current one? |
| Zero crossings (rate) | Oscillation frequency — how often does the series cross its mean? |
| Slope | Directional drift — is the series going somewhere? |
| Baseline delta | Residue — did the series end where it started? |

The first 5 features were chosen to separate three shape families: directional bursts, oscillatory signals, and slow drifts. The 6th feature (baseline_delta = mean of last 10% minus mean of first 10%) was added after discovering that COVID epidemic waves do not return to baseline — they plateau at a new endemic floor. This single feature tripled the distance between the two most confusable shape classes (COVID burst and CO2 trend) from 0.975 to 2.810 in standardised feature space.

### 2.2 Clustering

UMAP (n_neighbors=15, min_dist=0.1) for dimensionality reduction, preserving local structure. HDBSCAN (min_cluster_size=8, min_samples=3) for density-based clustering with explicit noise handling. The number of clusters is not specified — it emerges from the data.

### 2.3 Datasets

The corpus grew from 9 to 17 datasets across the project:

| Dataset | Domain | Source |
|---|---|---|
| COVID first wave (202 countries) | Epidemiology | OWID |
| COVID second wave (209 countries) | Epidemiology | OWID |
| Sunspot cycles (1749–present) | Astronomy | SILSO |
| Lynx-hare (1845–1935) | Ecology | Hudson Bay Company |
| Keeling CO2 seasonal | Atmospheric chemistry | NOAA Mauna Loa |
| Keeling CO2 trend | Atmospheric chemistry | NOAA Mauna Loa |
| Global temperature | Climate | Berkeley Earth |
| ECG heartbeats (884 segments) | Cardiology | UCR Archive |
| River streamflow (24 stations) | Hydrology | USGS |
| Global mean sea level | Oceanography | NASA |
| ENSO ONI | Climate oscillation | NOAA |
| VIX volatility | Finance | CBOE |
| Arctic sea ice extent | Cryosphere | NSIDC |
| Antarctic sea ice extent | Cryosphere | NSIDC |
| CH4 trend | Atmospheric chemistry | NOAA GML |
| PIOMAS ice volume | Cryosphere | UW PSC |
| World Bank forest cover | Land use | World Bank |

### 2.4 Validation Architecture

Every new dataset was treated as a prediction: the expected shape class was written down before clustering. Predictions were scored honestly — wrong predictions were investigated, not discarded. Of the first 3 external datasets (sea level, ENSO, VIX), all 3 landed in unexpected places. All 3 unexpected results became findings.

---

## 3. The 8-Class Shape Taxonomy

The taxonomy emerged empirically and was later grounded in ODE theory:

| Class | Canonical example | Key features | ODE family |
|---|---|---|---|
| Burst | COVID epidemic wave | High skewness, high lag1, low ZC, positive baseline_delta | 2nd-order, displacement IC |
| Oscillator | Pure sinusoid (1–4 cycles) | Low skewness, moderate lag1, moderate ZC | 2nd-order, complex eigenvalues |
| Declining oscillator | Arctic sea ice | Oscillation + long-term decline | 2nd-order, velocity IC |
| Seasonal | CO2 annual cycle | High ZC, very low spectral entropy | Two-frequency superposition |
| Trend | Quadratic acceleration | High lag1, positive slope, positive baseline_delta | 1st-order, quadratic drift |
| Integrated trend | CO2 accumulation, CH4 | lag1≈1.0, ZC≈0, large positive baseline_delta | 1st-order, positive drift |
| Declining monotonic | Glacier retreat, forest loss | lag1≈1.0, ZC≈0, large negative baseline_delta | 1st-order, negative drift |
| Irregular oscillator | Temperature, VIX, ENSO | Intermediate lag1, high ZC, noise-dominated | Universal noise attractor |

A ninth label, *eco_cycle*, existed through most of the project as a candidate class for noisy asymmetric oscillations. It was formally retired in nb40 after meeting all eight retirement criteria (no ODE basis, no real-world anchor, noise-sufficient generation, gradual basin boundary, multi-target reclassification, zero corpus impact, small ARI penalty). It is retained as a transition-zone descriptor for signals in the noise-harmonic intermediate region between oscillator and irregular_osc (see Section 5.4).

These 8 classes organise into 4 structurally isolated ODE families. No parameter sweep within one family reaches another — they are separated by changes in equation order, initial conditions, or the presence of stochastic forcing.

---

## 4. Key Findings

### 4.1 The domain is the costume

Financial market volatility (VIX) and ecological predator-prey dynamics (lynx-hare) share the same time-domain fingerprint. Market crises boom and revert; predator-prey populations boom and collapse. The domain is different; the dynamic is the same. This cross-domain match survived validation by four independent measurement architectures.

### 4.2 Shape similarity is a vector, not a scalar

Sunspot cycles and COVID waves look identical in time-domain features (both smooth, high-memory, right-skewed) but completely different in spectral space (sunspot is a near-pure periodic signal; COVID is a broadband burst). Sunspot and CO2 seasonal look completely different in time-domain but nearly identical spectrally (both concentrate power at low frequencies). No single feature frame separates everything. Shape similarity is multi-dimensional.

### 4.3 The terrain is real; the vocabulary is the receptor's

The thunder hypothesis takes its name from a simple observation: lightning and thunder are one event, but an observer using sight and an observer using hearing construct different representations separated in time and detail. Applied to XWorld: if the 8 shape classes are an artifact of the 6-feature fingerprint receptor, a completely independent measurement system should classify them differently. If independent systems converge, the structure is in the world, not in the instrument.

Four independent measurement architectures — the 6-feature hand-crafted fingerprint, a convolutional autoencoder, Amazon's Chronos foundation model, and a combined topological/recurrence-quantification (TDA+RQA) framework — all achieve equivalent discriminative resolution over the 8 shape classes (ARI 0.410–0.415). The TDA+RQA result is particularly significant: two mathematical frameworks from entirely different traditions — persistent homology from algebraic topology, and recurrence quantification from nonlinear dynamics — combined, match the 6-feature fingerprint exactly (ARI 0.415 vs 0.410).

Both TDA and RQA independently identify the same most-robust division: the trend-family (integrated_trend, declining_monotonic, trend) versus all others. This boundary appears as H1≈0 in phase-space topology and LAM≈0.95–0.99 in recurrence structure — two numbers from different mathematical languages identifying the same division in the world.

Within families, discrimination is framework-relative: TDA cannot separate oscillator from eco_cycle; RQA cannot distinguish oscillator from irregular_osc; the fingerprint cannot see loop topology. Inter-class distances disagree across architectures (Spearman ρ = −0.31 between Chronos and the 6-feature fingerprint). The boundaries are robust; the manifold between them is receptor-dependent.

The revised thunder hypothesis: the gross structure — the trend-family boundary — is observer-independent, recovered by every receptor tested. The 8-class vocabulary within that structure is observer-relative: each measurement system has different blind spots, but all achieve the same total discriminative resolution. The terrain is real. The vocabulary is the receptor's contribution.

### 4.4 Observer-invariance holds for 12/17 datasets

Trend-type signals (CO2 accumulation, glacier retreat, sea level rise) classify identically regardless of observation window length. Oscillatory signals (CO2 seasonal, sea ice, ENSO) are window-sensitive — their classification depends on how many cycles the analyst observes. The ODE territory is observer-independent; the fingerprint map from observation to class is observer-relative for periodic dynamics.

### 4.5 The eigenvalue plane is the territory

The 8 shape classes map to distinct regions of the complex eigenvalue plane (α, ν) where α is the decay rate and ν is the frequency. The boundary between oscillator and burst slopes with frequency (ρ = −0.917): higher-frequency signals tolerate more decay before losing their oscillatory fingerprint. All classes converge to irregular_osc under heavy noise (σ ≥ 0.25) — the universal noise attractor.

### 4.6 Attractor geometry is fingerprint-visible

Three projections of the same Lorenz attractor land in three different fingerprint classes. The x-axis (slow cross-wing oscillation) classifies in the eco_cycle transition zone (between oscillator and irregular_osc); y and z classify as irregular_osc. The two-lobed butterfly geometry is detectable through the fingerprint — attractor topology is not invisible to simple statistics.

---

## 5. What Did Not Work

### 5.1 Combining feature frames lowered performance

Adding 5 spectral features to the 6 time-domain features produced an 11-feature space with lower ARI (0.133) than time-domain alone (0.165). The spectral features added within-class variance for ECG and COVID that destabilised density-based clustering.

### 5.2 No grokking occurred

A small transformer trained on the 8 shape classes generalised immediately — no memorisation-then-generalisation phase transition. Shape classes are syntactically distinct at the raw waveform level. There is no hidden algebraic structure to discover; the signal is on the surface.

### 5.3 Synthetic-to-real transfer failed

A contrastive encoder trained on synthetic shape archetypes correctly mapped only 1 of 5 real datasets. Synthetic generators produce pure archetypes; real data is composite. Chronos transfers because it trained on real series.

### 5.4 eco_cycle retired as a first-class category

The actual lynx-hare population data classifies as burst/declining_osc, not eco_cycle — the class that was named after it. eco_cycle captures a mathematical waveform shape (sin(x) + A·sin(2x) with noise) that does not match actual ecological dynamics. It is the only candidate class without a clean ODE basis: noise alone at σ≥0.12 is sufficient to generate it; no harmonic component is required.

In nb40, eco_cycle was formally retired against eight criteria: no ODE basis (nb32), no real-world anchor (nb34), noise-sufficient generation (nb34, nb40), gradual basin boundary with no sharp entry transition, multi-target reclassification (58% absorbed by oscillator, 27.5% by declining_osc, 14% by seasonal/irregular_osc), zero corpus impact (no dataset was ever classified as eco_cycle), small ARI penalty (Δ = −0.038), and lowest TDA+RQA purity of any candidate class (17%). All eight criteria met.

eco_cycle is retained as a transition-zone descriptor for signals in the noise-harmonic intermediate region between oscillator and irregular_osc. It is not a distinct attractor — it is a statistical intermediate region with a gradual entry boundary and a sharp exit boundary into irregular_osc under heavier noise.

---

## 6. Open Questions

Phase 1 established the terrain. What follows are not plans — they are the questions the terrain leaves open.

**Does the continuous manifold have structure?** HDBSCAN produces discrete clusters; the underlying shape space is continuous. The noise-landing of sea level, ENSO, and VIX suggests these signals occupy inter-class regions rather than noise proper. Whether the manifold between the 8 classes has smooth gradients or sharp boundaries is not answerable with the current method. An autoencoder bottleneck trained on the full corpus would reveal this directly.

**Are the 8 classes primitives, or composites?** The burst class and the oscillator class share high autocorrelation but differ in skewness and zero-crossing rate. Are they genuinely atomic, or does each factor into simpler sub-structures — the way 2(x + 2y) factors from 4x + 8y? If some classes are linear combinations of others in feature space, a smaller basis set of shape primitives may underlie the taxonomy.

**Is the window-aliasing result a standalone finding?** The discovery that trend-class signals are observer-invariant while oscillatory signals are observer-relative has methodological implications beyond XWorld. Any time series classifier that does not account for the ratio of observation window to signal period is making an implicit assumption about observability.

**Are shape classes signatures of the sensing mind?** The 17 datasets map suggestively onto physical sensory modalities — thermoreception, chemoreception, mechanoreception, interoception. VIX, the one dataset with no sensory grounding, consistently resists clean classification. A testable hypothesis: raw sensory transductions — accelerometer traces, thermistor readings, galvanic skin response, e-nose outputs — classify more robustly than cognitively constructed indices. If so, the shape classes may be signatures not only of nature's dynamics but of the geometry imposed by physical receptors. The terrain is real. The vocabulary may be the receptor's contribution.

**Does shape class predict causal structure?** Two systems in the same shape class are governed by ODEs in the same eigenvalue region. Whether this implies shared feedback topology — and whether interventions that move a system between classes in one domain produce analogous transitions in another — is untested. The ODE grounding makes this tractable.

**What does the Lorenz result imply?** Three projections of the same attractor land in three different shape classes. If a single dynamical system produces multiple shape classes depending on which variable is observed, shape class is a property of the observation, not the system. The full implications for the taxonomy's interpretation remain open.

The project began with a question: does a glacier melting and a turtle breathing share the same numerical signature? After 121 findings, the answer is: they can — if both occupy the same region of the eigenvalue plane. Whether that shared region reflects something deep about the nature of change, or merely the limited resolution of 6 numbers, is the question that outlasts Phase 1.

The domain is the costume. The shape may be real. The question is how real.

---

## Appendix: Project Statistics

| Metric | Value |
|---|---|
| Notebooks completed | 40 |
| Findings documented | 121 |
| Datasets in corpus | 17 |
| Domains covered | 8 |
| Shape classes | 8 (eco_cycle retired to transition-zone label) |
| ODE families | 4 |
| Robust classifications | 12/17 (71%) |
| Independent validation methods | 4 (TD features, Conv AE, Chronos, TDA+RQA) |
| Project duration | 23 March – 29 April 2026 (37 days) |
| Predictions made before runs | ~80 |
| Predictions confirmed | ~45% |
| Predictions wrong but informative | ~55% |

---

*XWorld is an open research project. The notebooks, findings, and data are available at [github.com/sekarkrishna/xworld](https://github.com/sekarkrishna/xworld) and [git.sekrad.org/xworld](https://git.sekrad.org/xworld).*
