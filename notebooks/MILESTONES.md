# XWorld — Milestones

A living document. Not a rigid plan — a map of where this is going. Update freely as interesting patterns pull the research in new directions. The point is curiosity, not completion.

---

## Phase 0 — Foundation (COMPLETE)
*23–28 March 2026*

Build the fingerprinting system, confirm cross-domain clustering works, establish the taxonomy.

- [x] 9 datasets across 7 unrelated domains
- [x] 5-feature time-domain fingerprint (skewness, kurtosis, lag1_autocorr, zero_crossings, slope)
- [x] 7 shape classes confirmed
- [x] `baseline_delta` as 6th feature — COVID is event-with-memory (not event-without)
- [x] Observer-independence test (spectral features) — ARI=0.484, taxonomy survives
- [x] Combined frame test — time-domain 6f is the most efficient ruler for this corpus
- [x] 20 findings documented in FINDINGS.md

**What was learned:** The domain is the costume. The dynamic is real. No single feature frame captures everything — shape similarity is multi-dimensional, not a scalar. keeling_seasonal and keeling_trend are the two most structurally stable shape classes across every run.

---

## Phase 1 — Close the current line cleanly
*Target: 6 weeks from 28 March 2026*

Finish the questions Phase 0 opened before moving to learned embeddings.

### 1a — Pairwise shape distance as a vector (Notebook 14)
- [ ] Compute pairwise distances between all dataset centroids in *both* frames (time-domain and spectral)
- [ ] Plot each pair as a point in 2D space: (td-distance, spectral-distance)
- [ ] Show that COVID-sunspot lands at (near, far) and sunspot-keeling_seasonal lands at (far, near)
- [ ] This closes the frame-dependent similarity question properly

**Why this matters:** The sunspot-COVID duality is not a bug. It's the finding. Shape similarity is a vector. This notebook makes that explicit.

### 1b — New datasets: stress-test the taxonomy (Notebooks 15–17)
Each notebook is a prediction made before running. Land where expected → taxonomy holds. Land somewhere new → new class.

- [x] Notebook 15: Global mean sea level (NASA) — predicted keeling_trend, landed nearest COVID (1.467). 48% noise. Gap found: "noisy directional" class. → Findings 27–28
- [x] Notebook 16: ENSO ONI (NOAA) — predicted sunspot/lynx_hare, landed equidistant COVID+sunspot (0.97-1.02). 72% noise. New region found. → Findings 29–30
- [x] Notebook 17: VIX volatility (CBOE) — predicted COVID/ECG, landed nearest lynx_hare (0.594). 69% noise. Cross-domain: finance ↔ ecology. → Findings 31–32
- [ ] Each prediction written down *before* running, scored after

**Why this matters:** All 9 current datasets were chosen somewhat intentionally. External validation from datasets chosen without knowing where they'll land is stronger evidence.

### 1c — Stability test (Notebook 19)
- [ ] Vary HDBSCAN min_cluster_size (4, 6, 8, 12, 16) and min_samples (2, 3, 5)
- [ ] For each parameter set, record which datasets stay in their cluster vs drift
- [ ] Produce a "stability score" per dataset — how often does it land in its expected class?
- [ ] Expected: keeling_seasonal and keeling_trend = 100% stable. Sunspot = unstable.

**Why this matters:** The taxonomy shouldn't rest on one parameter choice. This shows which classes are granite and which are sand.

---

## Phase 2 — Replace hand-crafted features with learned ones
*Target: 4 months from 28 March 2026*

The 6 features you chose are a measurement frame — your decision about what to measure. The question is: if a neural network decides what to measure, do the same 7 classes emerge?

### 2a — Autoencoder experiment
- [ ] Train a simple 1D convolutional autoencoder on all time series (interpolated to same length)
- [ ] Extract bottleneck embeddings (8–16 dimensional)
- [ ] Run UMAP + HDBSCAN on learned embeddings
- [ ] Compare: do the same cross-domain groupings appear without hand-crafted features?

**Why this matters:** If yes — the classes are real in a deeper sense. The network found them without being told what skewness or kurtosis is. If no — the classes depend on the specific measurement frame and the question shifts to why this frame works.

### 2b — Foundation model embeddings
- [x] Run all 12 datasets through Chronos-T5-Small (Amazon, 46 M params) — zero-shot
- [x] Extract mean-pooled T5 encoder embeddings (512-dim)
- [x] Cluster with HDBSCAN, compare to TD features and Conv AE
- [x] Key finding: sunspot-COVID confirmed as maximally separated (3 methods agree); sea_level isolated as its own cluster; ECG ARI=0.742 vs UCR labels; VIX+ENSO+temperature form a new cross-domain irregular cluster

**Why this matters:** These models have never seen your data. If they reproduce the same groupings, that's the strongest possible evidence that the taxonomy reflects something real about how time series structure is organized — not something specific to your feature choices.

---

## Phase 3 — The why question
*Target: 6–12 months from 28 March 2026*

Once the taxonomy is stable and replicated by learned embeddings, the question shifts from *what* to *why*.

Why do these 7 shapes keep appearing? What physical principle makes unrelated systems converge on the same dynamic forms?

### 3a — Design datasets to test a specific hypothesis
The burst class (COVID) exists because of exponential growth followed by resource depletion. Any system with that feedback structure should land in the same cluster — regardless of domain.

- [ ] Forest fire spread + burnout curve — same feedback as epidemic?
- [ ] Technology adoption curve (S-curve) — same burst shape?
- [ ] Predator population spike after prey boom — same class as COVID or lynx_hare?

### 3b — Connect shape to system structure
- [ ] Is spectral entropy measuring the complexity of the forcing function?
- [ ] Does the number of feedback loops in a system predict which shape class it lands in?
- [ ] Can you predict a system's shape class from its physical description — before measuring it?

**Why this matters:** This is where the cartography becomes theory. You stop describing the map and start explaining why the terrain is shaped the way it is.

---

## Guiding principles (not rules)

- **Predictions before runs.** Always write down where you expect a new dataset to land before clustering. The discipline of prediction is what separates finding from fitting.
- **Follow interesting anomalies.** If a dataset lands somewhere unexpected, that's more interesting than one that confirms a prediction. Investigate before moving on.
- **The taxonomy is not fixed.** 7 classes is what this ruler found at this resolution. New datasets, new features, or learned embeddings may reveal sub-structure or merge classes. Update FINDINGS.md when this happens.
- **No fixed timeline.** The phases above are approximate. If Phase 2 reveals something surprising, stay there. If a new domain pulls the research sideways, follow it.

---

## Current status
**Active phase:** Phase 3 substantially complete; entering composition-mechanics epilogue + cross-receiver audit
**Last updated:** 02 May 2026
**Total findings:** 157 (see FINDINGS.md)
**Notebooks completed:** 01–48

**Recent arcs:**
- Arc 1 — Cartography (nb01–31): 9-class taxonomy stable across 17-dataset corpus.
- Arc 2 — Mechanism (nb32–38): ODE parameter space → fingerprint manifold; eco_cycle is noise-driven.
- Arc 3 — Thunder hypothesis (nb39–43): TDA, RQA, and fingerprint achieve same ARI. Gross structure is observer-independent (4 families); 9-class vocabulary is observer-relative.
- Arc 4 — Composition mechanics (nb44–48): zscore-after-mix nonlinearity expels mixtures from oscillator basin (84%); actual mean features predict composition table at 96.9%; centroid-midpoint geometry fails (45.3%). The composition attractor is a property of the feature-extraction *operator*, not of feature-space *geometry*.

---

## Next session — pick up here

**Plan agreed 02 May 2026.** Three threads in sequence:

### Thread 1 — Close out composition (nb49, low effort, ~1 notebook)

**Question:** F157 predicted that a linear-with-intercept correction `actual ≈ a·midpoint + b` would dramatically outperform pure scaling. Fit the 6 (a,b) pairs from nb48 data, apply to centroid midpoints to predict actual mean features, then classify and compare to empirical composition table.

**Goal:** turn nb48's simulation-based 96.9% predictor into a closed-form predictor. If a 6-parameter linear correction recovers ≥90% accuracy, you have a usable analytical model of mixture-fingerprint deviation — useful for any future arithmetic-on-shapes work.

**Predictions:**
- Linear-with-intercept on slope/baseline_delta alone: ≥85% accuracy (these had ρ ≈ 0.98 in nb48).
- Full 6-feature linear correction: ≥90% accuracy.
- Residuals concentrate on lag1/ZC pairs where ρ < 0.25 (the genuinely nonlinear features).

### Thread 2 — Embedding-midpoint failure mode (nb50–51, medium effort, 1–2 notebooks)

**Question:** The latent-arithmetic and grokking-transfer hypotheses both rest on embedding-space midpoints being meaningful. nb46–48 showed that *6-feature centroid midpoints* fail at this in the synthetic-shape domain. Do learned embeddings (nb45 transformer, Chronos) implicitly approximate `mean_actual` (avoiding the failure), or do they inherit the same midpoint trap?

**Approach:**
- nb50: re-derive composition table using nb45 transformer embeddings and Chronos embeddings on the same 64 pair set (i.e., classify mixed signals using each embedding's nearest-class metric).
- nb51: compare embedding-space centroid midpoints to embedding-space actual mean activations on the 64 pairs. Report midpoint accuracy vs actual-mean accuracy for each receiver.

**Predictions (to be sharpened in the notebook):**
- Chronos: midpoint and actual-mean both ≥80% (smoother, less geometry-dependent).
- 6-feature: midpoint 45%, actual 97% (already known, baseline).
- Transformer (from nb25): midpoint accuracy ≈ 6-feature, since the equidistant address-book embedding has no meaningful midpoints.

This bridges Arc 4 back to the grokking-transfer thread that has been waiting in memory since April.

### Thread 3 — Audio / whale calls (nb52+, medium effort, on the futures list)

**Question:** Direct test of Phase 3's strongest claim — predator-prey vocalisations should land near lynx_hare regardless of acoustic medium.

**Approach:** NOAA or Cornell Lab labelled cetacean / songbird audio → amplitude envelope or call-rate series at behavioural timescale → 6-feature fingerprint → classify against existing 9-class system.

**Pre-commitment prediction:** cetacean foraging calls (with prey acoustic indicators) land in eco_cycle. Solo predator vocalisation series (no prey signal) land in burst or irregular_osc. Prey-rich songbird flock data lands in seasonal or eco_cycle.

This is the cleanest cross-modality test left — every receptor so far has been numerical / statistical. Switching domain to acoustic biology is the strongest available test of the receiver-vs-world question.

---

## Deferred / longer-horizon

- **Mirror distortions / invariance battery** (medium effort) — robustness map alongside taxonomy. nb23 hinted at directional vs shape-defined classes; this would systematise it.
- **Phase 3b — physical structure → shape class** (large) — predict class from feedback-loop count, conservation laws, forcing-function entropy *before* measurement. The original Phase 3 destination.
- **Video / amoeba chemotaxis** (largest, on futures list) — new extraction pipeline; highest payoff, multiple sessions before first data point.
- **Grokking transfer experiment** (large, in memory) — trigger by Thread 2 results; design depends on whether learned embeddings preserve composition geometry.
