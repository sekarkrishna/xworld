# Session Summary — 19 Apr 2026 (Notebook 26)

**Notebook:** `26_contrastive_shape_manifold.ipynb`
**Question:** Does Supervised Contrastive Loss (SupCon) produce shape-similarity geometry? Does ρ go positive?

---

## Predictions

- SupCon would force same-class instances together and different-class apart — encoding similarity structure
- Spearman ρ (transformer vs 6-feature distances) would be positive
- Distance range would be wider than CE geometry (1.27× ratio)

---

## Setup

Same synthetic dataset as nb25 (8 classes × 200 instances × 64-length sequences).
Same transformer backbone (d_model=64, n_heads=4, n_layers=2, d_ff=256).
Added projection head: encoder_output (64-dim) → MLP (256) → L2-normalize (128-dim).
Loss: SupCon with temperature τ=0.07, using all positive pairs in batch.
Training: AdamW lr=3e-4, weight_decay=1e-4, batch=512, 2000 epochs.
Analysis on raw 64-dim encoder output (not projection), matching nb25 methodology.

---

## Results

**Spearman ρ = +0.38 (p=0.044).** Sign flipped from −0.31 to +0.38. Loss was the problem.

**Distance range 2.81×** (vs 1.27× for CE). Contrastive training spreads the inter-class distances — some classes genuinely close, some genuinely far.

**trend ↔ integrated_trend = #1 closest pair** in contrastive space. Also #1 closest pair in 6-feature space (F57 from nb21). The two representations agree on the tightest relationship in the corpus.

---

## Findings

- **F67:** SupCon loss gives Spearman ρ = +0.38 (p=0.044) between contrastive encoder and 6-feature pairwise distances. Cross-entropy vs contrastive = −0.31 vs +0.38. Architecture unchanged; loss determined geometry.
- **F68:** Contrastive distance range 2.81× vs CE 1.27×. SupCon encodes genuine inter-class similarity gradients; CE collapses them.
- **F69:** trend ↔ integrated_trend is the #1 closest pair in both contrastive encoder space and 6-feature fingerprint space — first cross-representation agreement on a specific pair relationship.

---

## Interpretation

The transformer has sufficient capacity to encode shape similarity — it just needs the right loss signal. SupCon explicitly rewards distance structure (similar classes near, dissimilar far) while CE ignores it. ρ = +0.38 is moderate but significant: the contrastive encoder is partially consistent with the 6-feature fingerprint. The remaining gap (ρ not approaching 1.0) likely reflects synthetic-to-real transfer limitations — the encoder was trained on pure archetypes.

F69 (trend↔integrated_trend agreement) is the first result where two independent representations converge on the same inter-class relationship. This is evidence that the clean monotonic / clean integrated distinction is structural, not receptor-dependent.

---

## Next

Notebook 27: test synthetic-to-real transfer. Do contrastive encoder embeddings of real datasets reflect their known shape classes? Also: does the 6-feature MLP grok?
