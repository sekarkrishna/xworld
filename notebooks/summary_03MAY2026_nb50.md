# Session Summary — 03 May 2026 (nb50)

**Notebook:** 50 (Embedding Midpoint Composition Test)
**Findings:** F166–F172
**Total findings:** 172

---

## nb50 — Embedding Midpoint Composition Test

Thread 2 of the May-2026 plan. The composition arc (nb46–49) established that geometric midpoints in the 6-d fingerprint space predict the composition table at only 45.3%, and per-feature linear correction has a hard 70.3% ceiling. nb50 tests whether the nb46 transformer's 128-d class embeddings do better — specifically whether the composition training task forces composable structure into the embedding geometry.

### What was expected vs what happened

| Finding | Prediction | Result |
|---|---|---|
| F166: embedding midpoint accuracy | 45–55% | **Refuted — 32.8%, worse than 6f baseline** |
| F167: forward-pass accuracy all 64 pairs | >80% | **Confirmed — 93.8%** |
| F168: gap (fwd pass − midpoint) | ≥20pp | **Confirmed, far exceeded — 60.9pp** |
| F169: ρ(emb, comp impurity) > ρ(emb, fingerprint) | comp ρ > 0.399 | **Refuted — 0.175 (p=0.37, not significant)** |

### Core discovery: composition is in the mechanism, not the geometry

The full accuracy ladder:

| Method | Accuracy |
|---|---|
| **Embedding midpoint (nb50)** | **32.8%** ← worse than 6f midpoint |
| 6f centroid midpoint (nb47) | 45.3% |
| Closed-form linear (nb49) | 70.3% |
| **Transformer forward pass (nb50)** | **93.8%** ← beats closed-form ceiling |
| Simulation oracle (nb48) | 96.9% |

The transformer's attention mechanism closes 97% of the gap to the oracle (93.8% vs 96.9%). Its embedding geometry is *worse* than the naive 6-d fingerprint midpoint. Composition knowledge lives entirely in the attention weights.

**Why embedding midpoints are worse than 6f midpoints:** The 128-d embeddings collapse to a geometric hub. Burst is predicted 17/64 times by midpoints vs 1/64 empirically — it occupies the "center" of the embedding space such that averaging any two class embeddings tends to land nearest to it. This mirrors the oscillator Voronoi-dominance problem from nb47, but in 128-d and for a different class (burst vs oscillator), and with more severe distortion.

**Why ρ(emb, composition) is non-significant:** The composition training task restructured the attention weights to encode composition rules, but it did not restructure the embedding geometry. The embeddings still encode fingerprint similarity (ρ=+0.399, unchanged from nb46's post-training measurement), not composition similarity. The model learned *which* classes are similar for classification purposes; it did not learn to position embeddings so their midpoints predict mixing outcomes.

**The 4 wrong transformer pairs:**
- (BUR,OSC) and (OSC,BUR): both output INT; empirical=DCO. Wrong by both forward-pass and midpoint. These are the most compositionally nonlinear pairs in the table.
- (OSC,INT) and (INT,OSC): forward-pass outputs INT; empirical=TRE. The midpoint *correctly* predicts TRE for these two — the only pairs where embedding geometry beats the attention mechanism.

### What this means for Thread 2

nb51 (Chronos) now has a precise question: does a large pretrained foundation model with no composition training show *more* geometric composition structure than the task-trained transformer? The task-trained transformer achieved ρ(emb, fingerprint) = +0.399 but ρ(emb, comp impurity) = +0.175. Chronos, trained on 27 billion time points across diverse domains, might have developed embedding geometry that encodes composition implicitly through its massive pretraining distribution — or it might show the same failure mode.

### Artifacts

- `notebooks/50_embedding_midpoint_composition.ipynb`
- `artifacts/nb50_embedding_midpoint.png` — accuracy bar chart, embedding distance heatmap, ρ scatter

### Findings added

- **F166** — Embedding midpoint: 32.8% (refuted, worse than 6f baseline)
- **F167** — Forward-pass all 64 pairs: 93.8% (confirmed, exceeds 70% ceiling)
- **F168** — Gap fwd−midpt: +60.9pp (confirmed, far exceeds 20pp threshold)
- **F169** — ρ(emb, comp impurity): +0.175, p=0.37 (refuted, not significant)
- **F170** — Emergent: burst is the geometric hub of 128-d embedding space (17/64 midpoint predictions)
- **F171** — Emergent: 60.9pp gap is the largest geometry-vs-mechanism gap in the project
- **F172** — Emergent: higher-d learned embeddings are *less* composable than 6-d fingerprint space
