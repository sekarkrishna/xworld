# Session Summary — 19 Apr 2026 (Notebook 25)

**Notebook:** `25_xworld_grokking.ipynb`
**Question:** Can a transformer grok the 8 XWorld shape classes? Does grokking produce shape-similarity geometry?

---

## Predictions

- Grokking would require a delayed generalization phase (gap > 0 epochs between memorization and generalization)
- Post-grokking embeddings would reflect shape similarity (similar classes cluster nearby)
- Spearman ρ between transformer pairwise distances and 6-feature pairwise distances would be positive

---

## Setup

Synthetic dataset: 8 shape classes × 200 instances × 64-length sequences.
Generators: burst, eco_cycle, oscillator, seasonal, trend, integrated_trend, irregular_osc, declining_osc.
Architecture: CLS-token transformer encoder (d_model=64, n_heads=4, n_layers=2, d_ff=256) + linear classification head.
Training: AdamW weight_decay=0.1, 5000 epochs, batch=256, cross-entropy loss.

---

## Results

**No grokking.** Both memorization (train>90%) and generalization (val>80%) thresholds crossed at epoch 50 simultaneously. Gap = 0 epochs.

**Address-book geometry:** Post-training inter-class distance range = 10.3–13.1 (ratio 1.27×). All 8 classes are equidistant from each other — the encoder maps shape classes to orthogonal corners, not a manifold.

**Spearman ρ = −0.31** (transformer pairwise distances vs 6-feature pairwise distances). Negative correlation — the two representations actively disagree on which classes are similar.

---

## Findings

- **F64:** No grokking — shape classes are syntactically distinct at raw waveform level. A burst and an oscillator look completely different as 64 numbers; no hidden structure discovery required.
- **F65:** Cross-entropy training produces address-book geometry (distance range ratio 1.27×). The loss function forces equidistant class corners, not shape similarity.
- **F66:** Spearman ρ = −0.31 between transformer and 6-feature pairwise distances. Both representations achieve >99% class separation but disagree on inter-class similarity structure.

---

## Interpretation

Cross-entropy loss is indifferent to which classes are "close" — it only pushes the correct class probability to 1. The resulting geometry is wherever the optimizer finds it easiest to separate 8 classes: equidistant corners. The 6-feature fingerprint encodes shape similarity explicitly; the CE transformer does not. Loss function determines geometry more than architecture.

**Thunder hypothesis implication:** Both representations achieve the same class separation. The manifold *between* the classes is receptor-dependent — it is in the measurement, not the world.

---

## Next

Notebook 26: replace CE with Supervised Contrastive Loss (SupCon). Does the geometry change? Does ρ become positive?
