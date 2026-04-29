# XWorld: Cross-Domain Time Series Shape Clustering and the Geometry of Dynamical Systems

*A research paper based on 38 notebooks, 115 findings, and 17 real-world datasets across 8 unrelated domains.*

*April 2026*

---

## Abstract

Do time series from completely unrelated domains share underlying dynamic shapes that cluster together, independent of what they represent? Does a glacier melting and a turtle breathing share the same numerical signature? Can you read the nature of a system from the shape of its ripple?

XWorld is an empirical investigation of this question. Starting from 9 datasets spanning epidemiology, astronomy, ecology, climate science, hydrology, and cardiology, the project extracts a minimal 6-feature fingerprint from z-score normalised time series and clusters them using UMAP + HDBSCAN. The central finding: time series cluster by dynamic shape, not by domain of origin. COVID epidemic waves and sunspot cycles, financial volatility and predator-prey population dynamics, glacier retreat and atmospheric CO2 accumulation — all land in mathematically predictable regions of a 9-class shape taxonomy that maps directly onto the complex eigenvalue plane of ordinary differential equations.

The taxonomy has been validated by three independent measurement architectures (hand-crafted time-domain features, a convolutional autoencoder, and Amazon's Chronos foundation model), stress-tested across 15 HDBSCAN parameter combinations, and grounded in ODE theory. 12 of 17 real-world datasets are classified robustly regardless of observation window. The remaining 5 are periodic signals whose classification depends on the analyst's window length — a finding that itself reveals the boundary between observer-independent and observer-relative properties of dynamical systems.

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

## 3. The 9-Class Shape Taxonomy

The taxonomy emerged empirically and was later grounded in ODE theory:

| Class | Canonical example | Key features | ODE family |
|---|---|---|---|
| Burst | COVID epidemic wave | High skewness, high lag1, low ZC, positive baseline_delta | 2nd-order, displacement IC |
| Oscillator | Pure sinusoid (1–4 cycles) | Low skewness, moderate lag1, moderate ZC | 2nd-order, complex eigenvalues |
| Declining oscillator | Arctic sea ice | Oscillation + long-term decline | 2nd-order, velocity IC |
| Seasonal | CO2 annual cycle | High ZC, very low spectral entropy | Two-frequency superposition |
| Eco cycle | Noisy asymmetric oscillation | Negative skewness, noise-dependent | Two-frequency + noise |
| Trend | Quadratic acceleration | High lag1, positive slope, positive baseline_delta | 1st-order, quadratic drift |
| Integrated trend | CO2 accumulation, CH4 | lag1≈1.0, ZC≈0, large positive baseline_delta | 1st-order, positive drift |
| Declining monotonic | Glacier retreat, forest loss | lag1≈1.0, ZC≈0, large negative baseline_delta | 1st-order, negative drift |
| Irregular oscillator | Temperature, VIX, ENSO | Intermediate lag1, high ZC, noise-dominated | Universal noise attractor |

These 9 classes organise into 4 structurally isolated ODE families. No parameter sweep within one family reaches another — they are separated by changes in equation order, initial conditions, or the presence of stochastic forcing.

---

## 4. Key Findings

### 4.1 The domain is the costume

Financial market volatility (VIX) and ecological predator-prey dynamics (lynx-hare) share the same time-domain fingerprint. Market crises boom and revert; predator-prey populations boom and collapse. The domain is different; the dynamic is the same. This cross-domain match survived validation by three independent measurement architectures.

### 4.2 Shape similarity is a vector, not a scalar

Sunspot cycles and COVID waves look identical in time-domain features (both smooth, high-memory, right-skewed) but completely different in spectral space (sunspot is a near-pure periodic signal; COVID is a broadband burst). Sunspot and CO2 seasonal look completely different in time-domain but nearly identical spectrally (both concentrate power at low frequencies). No single feature frame separates everything. Shape similarity is multi-dimensional.

### 4.3 The 8 class boundaries are in the world; the geometry between classes is in the measurement

Three independent architectures — 6 hand-crafted features, a convolutional autoencoder, and Amazon's Chronos foundation model — all separate the 9 shape classes with >99% accuracy. But the inter-class distances disagree: Spearman ρ = −0.31 between the transformer and the 6-feature fingerprint. The boundaries are robust; the manifold between them is receptor-dependent. This is the "thunder hypothesis": the separations are real; the distances are constructed.

### 4.4 Observer-invariance holds for 12/17 datasets

Trend-type signals (CO2 accumulation, glacier retreat, sea level rise) classify identically regardless of observation window length. Oscillatory signals (CO2 seasonal, sea ice, ENSO) are window-sensitive — their classification depends on how many cycles the analyst observes. The ODE territory is observer-independent; the fingerprint map from observation to class is observer-relative for periodic dynamics.

### 4.5 The eigenvalue plane is the territory

The 9 shape classes map to distinct regions of the complex eigenvalue plane (α, ν) where α is the decay rate and ν is the frequency. The boundary between oscillator and burst slopes with frequency (ρ = −0.917): higher-frequency signals tolerate more decay before losing their oscillatory fingerprint. All classes converge to irregular_osc under heavy noise (σ ≥ 0.25) — the universal noise attractor.

### 4.6 Attractor geometry is fingerprint-visible

Three projections of the same Lorenz attractor land in three different fingerprint classes. The x-axis (slow cross-wing oscillation) classifies as eco_cycle; y and z classify as irregular_osc. The two-lobed butterfly geometry is detectable through the fingerprint — attractor topology is not invisible to simple statistics.

---

## 5. What Did Not Work

### 5.1 Combining feature frames lowered performance

Adding 5 spectral features to the 6 time-domain features produced an 11-feature space with lower ARI (0.133) than time-domain alone (0.165). The spectral features added within-class variance for ECG and COVID that destabilised density-based clustering.

### 5.2 No grokking occurred

A small transformer trained on the 8 shape classes generalised immediately — no memorisation-then-generalisation phase transition. Shape classes are syntactically distinct at the raw waveform level. There is no hidden algebraic structure to discover; the signal is on the surface.

### 5.3 Synthetic-to-real transfer failed

A contrastive encoder trained on synthetic shape archetypes correctly mapped only 1 of 5 real datasets. Synthetic generators produce pure archetypes; real data is composite. Chronos transfers because it trained on real series.

### 5.4 eco_cycle has no real-world anchor

The actual lynx-hare population data classifies as burst/declining_osc, not eco_cycle. The class captures a mathematical waveform shape (sin(x) + A·sin(2x) with noise) that does not match actual ecological dynamics. It is the only class without a clean ODE basis — it exists as a noise-displaced region of the oscillator basin.

---

## 6. Where This Goes

### 6.1 Next 1 Year (2026–2027): Complete the Map

The cartography phase. The 9-class taxonomy is established and grounded in ODE theory. The next year is about filling gaps, hardening boundaries, and making the system usable.

**Expand the corpus to 50+ datasets.** The current 17 datasets span 8 domains. Critical gaps: biology (gene expression time courses, neural spike trains, circadian rhythms), geophysics (seismic waveforms, volcanic tremor), engineering (vibration signatures, power grid frequency), and social systems (city traffic flow, social media activity bursts). Each new dataset is a prediction-before-measurement test. The taxonomy either absorbs it or reveals a 10th class.

**Build the autoencoder properly.** The Phase 2a autoencoder (nb19) was a proof of concept. A production-quality 1D convolutional autoencoder trained on the full 50+ dataset corpus, with bottleneck dimensionality tuned by reconstruction loss, would produce the continuous shape manifold that HDBSCAN discrete clusters cannot capture. The key question: does the learned manifold have 9 dense regions matching the ODE families, or does it reveal sub-structure invisible to 6 scalar features?

**Publish the window-aliasing result.** The finding that oscillatory shape classes are observer-relative while trend classes are observer-invariant is a standalone methodological contribution. Any time series classification system that does not account for the ratio of observation window to signal period is making an implicit assumption about observability. This deserves a focused paper with the sinusoid sweep, the multi-signal aliasing map, and the corpus robustness audit.

**Formalise the fingerprint as a Python library.** The current implementation lives in Jupyter notebooks. A clean `xworld` package with `extract_features()`, `classify()`, `predict_class()`, and `plot_eigenvalue_map()` would make the taxonomy accessible to researchers in other domains. Include the 9-class centroid table, the ODE generators, and the window-aliasing lookup.

### 6.2 Next 5 Years (2027–2031): From Cartography to Theory

The question shifts from "what shapes exist" to "why these shapes and not others."

**Connect shape classes to feedback structure.** The burst class exists because of exponential growth followed by resource depletion. The declining oscillator exists because of periodic forcing superimposed on secular decline. Can you predict a system's shape class from its physical description — before measuring it? This requires building a catalogue of feedback loop topologies (positive feedback → burst, negative feedback → oscillator, mixed → declining_osc) and testing whether the mapping is injective.

**Multi-scale shape analysis.** A single time series observed at different timescales may traverse multiple shape classes. Ocean temperature at daily resolution is irregular_osc; at decadal resolution it is integrated_trend. The window-aliasing work (nb37-38) showed this for synthetic signals. Extending it to real multi-scale datasets (climate reanalysis at hourly/daily/monthly/annual) would reveal whether the 9-class taxonomy is scale-invariant or whether different classes dominate at different scales. The hypothesis: the 4 ODE families are scale-invariant; the 9 classes within them are scale-dependent.

**Interaction dynamics.** All current datasets measure a single variable from a single system. The "runner vs substrate" question from the open questions list: is the shape in the participant or in the exchange relationship between them? Predator-prey is already an interaction, but we measure predator and prey separately. Measuring the ratio (predator/prey) or the phase relationship between them may reveal shape classes that single-variable analysis cannot see. Candidate datasets: currency exchange rates (interaction between two economies), predator-prey phase portraits, neural synchronisation between brain regions.

**Cross-domain anomaly detection.** If a system's shape class is known, departures from that class are anomalies. A glacier that stops declining (leaves the declining_monotonic class) or a financial market that stops oscillating (leaves irregular_osc) would be detectable as class transitions. This is a practical application: domain-agnostic anomaly detection based on shape class membership, where the "normal" class is learned from the system's own history and validated against the ODE taxonomy.

**Foundation model fine-tuning.** Chronos reproduced the taxonomy zero-shot. Fine-tuning a time series foundation model on the 9-class taxonomy (with the ODE-generated training data as augmentation) could produce a classifier that operates on raw waveforms without feature extraction. The key advantage over the 6-feature fingerprint: the model could learn sub-class structure (ECG morphologies, COVID wave variants) that scalar statistics cannot resolve.

### 6.3 Next 10 Years (2031–2036): A Periodic Table of Dynamics

**The analogy is deliberate.** Mendeleev's periodic table organised elements by atomic weight and predicted gaps before the elements were discovered. The XWorld eigenvalue map organises dynamical shapes by decay rate and frequency and has already predicted gaps (the declining_monotonic class was predicted by symmetry before PIOMAS and forest cover confirmed it). In 10 years, the goal is a complete, predictive classification of dynamical behaviours — not just for time series, but for any system that can be described by differential equations.

**Extend to spatial dynamics.** Time series are 1D projections of higher-dimensional systems. Video of fluid turbulence, satellite imagery of deforestation, fMRI of brain activity — all are spatiotemporal signals. The 6-feature fingerprint applies to any 1D slice, but the spatial structure (how shape classes are distributed across space, how they propagate) is a new dimension. A "shape field" — a map from spatial location to shape class — would describe how dynamics vary across a system. Forest fire spread would show a burst wavefront propagating through an oscillator background.

**Causal shape inference.** If two systems share a shape class, do they share a causal structure? The ODE grounding suggests yes — systems in the same eigenvalue region are governed by similar differential equations. But correlation of shape is not causation of mechanism. A rigorous test: given two systems in the same shape class from different domains, can you transfer a control strategy from one to the other? If damping an oscillator in one domain (adding friction to a mechanical system) moves it to the declining_osc class, does the analogous intervention in another domain (adding regulation to a financial market) produce the same class transition? This is the strongest possible test of whether shape classes reflect shared causal structure.

**Learned ODE discovery.** Neural ODE methods (Chen et al. 2018) learn differential equations from data. Training a neural ODE on each shape class and comparing the learned equations across domains would reveal whether the mathematical structure is truly shared or merely analogous. If the learned ODE for COVID epidemic dynamics and the learned ODE for forest fire spread have the same functional form (up to parameter rescaling), the universality claim moves from empirical observation to mathematical proof.

### 6.4 Beyond 10 Years: The Shape of Everything

The deepest version of the XWorld question is not about time series. It is about whether the space of possible dynamics is finite and classifiable — whether nature reuses a small set of dynamical forms across all scales and domains, the way it reuses a small set of crystal structures across all materials.

**A universal dynamics ontology.** If the 9-class taxonomy (or its successor with 15 or 20 classes) proves stable across 100+ datasets from 20+ domains, it becomes an ontology — a shared vocabulary for describing how things change over time, independent of what is changing. Epidemiologists, ecologists, economists, and physicists would share a common language for dynamics, the way they already share a common language for statistics.

**Connecting to universality in physics.** The renormalisation group in statistical physics shows that systems near critical points fall into universality classes determined by symmetry and dimensionality, not by microscopic details. XWorld's shape classes may be the time-series analogue: universality classes for temporal dynamics, determined by feedback structure and noise level, not by the specific physical system. The 4 ODE families (2nd-order linear, 1st-order stochastic, two-frequency superposition, noise attractor) may correspond to 4 universality classes of temporal behaviour. Proving this connection — or disproving it — would place XWorld within the broader framework of theoretical physics.

**The philosophical question.** The project began with a question: does a glacier melting and a turtle breathing share the same numerical signature? After 115 findings, the answer is nuanced. They can share the same shape class — if the glacier's decline and the turtle's respiration happen to occupy the same region of the eigenvalue plane. But "same shape class" does not mean "same system." It means the same mathematical form governs both, at the level of abstraction captured by 6 numbers. Whether that level of abstraction is deep or shallow — whether it reveals something about the nature of change itself, or merely reflects the poverty of 6-dimensional measurement — remains the open question that will outlast any specific taxonomy.

The domain is the costume. The shape may be real. The question is how real.

---

## Appendix: Project Statistics

| Metric | Value |
|---|---|
| Notebooks completed | 38 |
| Findings documented | 115 |
| Datasets in corpus | 17 |
| Domains covered | 8 |
| Shape classes | 9 |
| ODE families | 4 |
| Robust classifications | 12/17 (71%) |
| Independent validation methods | 3 (TD features, Conv AE, Chronos) |
| Project duration | 23 March – 26 April 2026 (35 days) |
| Predictions made before runs | ~80 |
| Predictions confirmed | ~45% |
| Predictions wrong but informative | ~55% |

---

*XWorld is an open research project. The notebooks, findings, and data are available on GitHub.*
