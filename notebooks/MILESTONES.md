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
- [ ] Notebook 17: VIX volatility (FRED) — spiky bursts, predicted: COVID or ECG cluster
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
- [ ] Run all 9 datasets through a pre-trained time series model (TimesFM or Chronos)
- [ ] Extract hidden state embeddings — no fine-tuning, zero-shot
- [ ] Cluster the embeddings, compare to the hand-crafted taxonomy
- [ ] Key question: does a model trained on millions of unrelated series organize your 9 datasets the same way?

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
**Active phase:** Phase 1 — starting with Notebook 14 (pairwise shape distances)
**Last updated:** 28 March 2026
**Total findings:** 20 (see FINDINGS.md)
**Notebooks completed:** 01–13
