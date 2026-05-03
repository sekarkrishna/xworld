# Session Summary — 03 May 2026 (nb51)

**Notebook:** 51 (Chronos Embedding Composition Test)
**Findings:** F173–F179
**Total findings:** 179

---

## nb51 — Chronos Embedding Composition Test

Thread 2 closer. nb50 showed that the task-trained transformer's embedding midpoints (32.8%) perform worse than the naive 6f midpoint (45.3%), and that composition structure lives in attention, not geometry. nb51 tests Chronos-T5-Small (46M params, 512-d, pretrained on 27B time-series points) — a foundation model with no composition training but vastly richer pretraining.

### What was expected vs what happened

| Finding | Prediction | Result |
|---|---|---|
| F173: ρ(Chronos, fingerprint) > 0.399 | More pretraining → better geometry | **Refuted — 0.304 (p=0.115, not significant)** |
| F174: Chronos midpoint ≈ 40–55% | No composition training → similar to 6f | **Refuted — 26.6%, worst of all methods** |
| F175: Chronos actual-mean < 96.9% | Confirmed | **Confirmed — 37.5%, surprisingly low** |
| F176: actual-mean > midpoint | Confirmed | **Confirmed — 37.5% vs 26.6% (+10.9pp)** |

### Complete Thread 2 accuracy ladder

| Method | Accuracy | Space |
|---|---|---|
| Chronos emb midpoint | **26.6%** | 512-d pretrained |
| Transformer emb midpoint | 32.8% | 128-d task-trained |
| Chronos actual-mean | **37.5%** | 512-d pretrained |
| 6f centroid midpoint | 45.3% | 6-d fingerprint |
| Closed-form linear | 70.3% | 6-d fingerprint |
| Transformer forward pass | 93.8% | attention mechanism |
| Simulation oracle | **96.9%** | 6-d fingerprint |

### Core discoveries

**Chronos has a completely different geometry from 6f.** The closest Chronos class pairs are oscillator↔seasonal (0.091) and integrated_trend↔declining_monotonic (0.096) — both far apart in 6f space. Chronos weights trend/level structure over oscillatory features. ρ(Chronos, fingerprint) = +0.304, not significant.

**Chronos actual-mean (37.5%) < 6f midpoint (45.3%).** This is the cross-receiver result: Chronos and the 6f classifier disagree on how to categorize mixed signals. Chronos massively over-predicts irregular_osc (23x vs 4x empirical) and under-predicts seasonal (1x vs 8x) and integrated_trend (1x vs 7x). The empirical composition table is 6f-classifier-relative — a different receiver would produce a different table. Observer-relativity at the composition level (F177).

**ρ(Chronos, comp impurity) = -0.233** — slightly negative, meaning closer Chronos embeddings tend to produce *more* uncertain compositions. Composition structure is orthogonal to Chronos geometry.

### Thread 2 conclusion (nb50 + nb51)

Composition structure is not stored in embedding geometry across any of the three spaces tested:
- 6-d fingerprint space: midpoints = 45.3% (geometry partially captures shape order)
- 128-d task-trained transformer: midpoints = 32.8% (geometry worse despite composition training)
- 512-d Chronos pretrained: midpoints = 26.6% (geometry worst despite massive pretraining)

The only paths to high composition accuracy are:
1. Simulation (96.9%): run the actual mixing operator
2. Task-trained attention (93.8%): train a mechanism explicitly on (A, B) → T[A,B]

The grokking-transfer hypothesis assumed embedding midpoints encode learned rules. Thread 2 refutes this: composition rules are in mechanisms (attention), not in geometric structure of embedding spaces.

### Artifacts

- `notebooks/51_chronos_embedding_composition.ipynb`
- `artifacts/nb51_chronos_embedding.png` — full accuracy ladder, Chronos distance heatmap, ρ scatter

### Findings added

- **F173** — ρ(Chronos, fingerprint) = +0.304, p=0.115 (refuted; lower than task-trained transformer)
- **F174** — Chronos midpoint: 26.6% (refuted; worst of all methods)
- **F175** — Chronos actual-mean: 37.5% (confirmed < oracle; surprisingly low)
- **F176** — actual-mean > midpoint: +10.9pp (confirmed)
- **F177** — Emergent: Chronos actual-mean < 6f midpoint — observer-relativity at composition level
- **F178** — Emergent: ρ(Chronos, comp impurity) = -0.233, orthogonal to composition structure
- **F179** — Emergent: complete ladder — no embedding space achieves >50% via midpoints
