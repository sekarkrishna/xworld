# Session Summary — 02 May 2026 (nb48)

**Notebook:** 48 (Zscore Mixing Nonlinearity)
**Findings:** F151–F157
**Total findings:** 157

---

## nb48 — Zscore Mixing Nonlinearity

Direct measurement of the gap that nb47 left open. Where nb47 showed that centroid-midpoint interpolation predicts only 45% of the empirical composition table — and conjectured that the missing 55% was the `zscore(0.5*A + 0.5*B)` nonlinearity — nb48 measures, per-feature and per-pair, exactly how the actual mixed feature distribution deviates from the midpoint, and how much of the composition table is recovered when that deviation is accounted for.

### What was expected vs what happened

| Finding | Prediction | Result |
|---|---|---|
| F151: skew/kurt compressed by ~1/√2 / ×0.5, ρ>0.90 | confirmed | **Partial** — direction right, magnitude more extreme (slope 0.21/0.26), ρ<0.35 |
| F152: slope/BD ×√2; lag1/ZC linear | confirmed | **Partial** — slope/BD confirmed (ρ ≈ 0.98); lag1/ZC NOT linear (ρ < 0.25) |
| F153: actual-feature accuracy >65% | confirmed | **Confirmed, far exceeded** — 96.9% (62/64) |
| F154: all 25 DCO pairs closer to DCO centroid | confirmed | **Refuted** — only 64% (16/25); but 84% farther from OSC |

### Core discovery: the zscore step is a current that flows *away from* oscillator

The model going in was: "the nonlinearity pulls mixtures toward declining_osc." The data shows something subtler. Only 38% of mixtures land closer to the DCO centroid after the nonlinearity, but **84% land farther from the oscillator centroid**. Combined with nb47's finding that OSC owns 77.5% of the Voronoi volume, the picture inverts:

- **Voronoi geometry (linear):** oscillator is the dominant attractor (77.5% of convex combinations).
- **Zscore nonlinearity:** oscillator is the dominant *repeller* (84% of mixtures pushed out of its basin).

The composition table is the residue: signals leave OSC, scatter into adjacent basins, and declining_osc happens to be the largest neighbouring basin in the directions the nonlinearity pushes.

### Two-regime feature behaviour

Per-feature analysis (Part B) splits the 6 features cleanly into two clusters:

| Cluster | Features | ρ(actual, midpt) | Theory match |
|---|---|---|---|
| **Linear functionals** | slope, baseline_delta | 0.98 | Excellent (slope ≈ 1.25, theory √2 ≈ 1.41) |
| **Nonlinear functionals** | skewness, kurtosis, lag1, zero_crossings | < 0.35 | Fails — these depend on the *joint* signal, not the average |

This explains why nb47's centroid-midpoint model worked at all: it correctly handles the two linear features, which alone discriminate 45% of pairs. The four nonlinear features carry the rest, and they are not interpolatable — they require simulation.

### Additive bias in three features

Mean deviation (Part A) reveals that three features have a one-sided shift:
- **kurtosis +0.63** (mixed signals are more leptokurtic than constituent average)
- **zero_crossings +0.74** (more sign-changes than average)
- **lag1_autocorr −0.52** (less autocorrelated than average)

These are constant additive offsets, not multiplicative scaling. A linear-with-intercept correction model `actual ≈ a·midpoint + b` would dramatically improve over pure scaling. Mechanistically: mixing a smooth signal with a noisy one always moves lag-1 toward zero, but the higher-order tail and zero-crossing structure tend to *grow* due to constructive/destructive interference between the two waveforms.

### Composition table recovered: 96.9%

Using `mean_actual[i,j]` (mean over 500 simulated mixed feature vectors) instead of the centroid midpoint, classification accuracy on the empirical composition table rises from 45.3% to **96.9%** (62/64). All 33 prediction changes are improvements; none regress.

This is the conclusive answer to nb47's open question. The composition attractor is **not** a property of feature-space geometry. It is a property of the **functional form of feature extraction applied to the mixture**. The geometry of the centroids in 6D is a misleading picture; the relevant object is the empirical distribution of `extract_6f(zscore(0.5*A + 0.5*B))`, which deviates from the centroid midpoint in a structured, feature-specific way.

### Where this leaves the thread

- **nb46 → nb47 → nb48** is now closed as a coherent story: declining_osc dominance is fully accounted for as the joint effect of (a) OSC having a large but fragile Voronoi basin and (b) the zscore-after-mix step systematically expelling mixtures from that basin into surrounding territory dominated by DCO.
- The midpoint-interpolation toolkit (used implicitly in many embedding-arithmetic and latent-arithmetic experiments) is shown to be **not safe for the synthetic-shape domain** — accuracy 45% vs 97% is a 2× error rate.
- Open: do learned embeddings (e.g., the transformer in nb45) implicitly approximate `mean_actual` (giving them a 97%-style prediction power) or do they inherit the centroid-midpoint failure mode? Concrete next-step probe: compare embedding-space midpoints to nb45's transformer activations on the 64 pair set.

### Artifacts

- `notebooks/48_zscore_mixing_nonlinearity.ipynb`
- `artifacts/nb48_zscore_nonlinearity.png` — per-feature actual vs midpoint scatter, theory slope overlaid
- `artifacts/nb48_pca_shift.png` — 2D PCA showing midpoint→actual shift arrows for all 64 pairs

### Findings added

- **F151** — skew/kurt compressed (partial: direction right, magnitude more aggressive than theory)
- **F152** — slope/BD amplified (partial: confirmed for slope/BD, refuted for lag1/ZC)
- **F153** — actual mean features hit 96.9% accuracy (confirmed, far exceeds 65% prediction)
- **F154** — DCO pairs not consistently closer to DCO centroid (refuted as stated)
- **F155** — emergent: zscore mixing depletes the oscillator Voronoi basin (84%)
- **F156** — emergent: two-regime feature behaviour (linear vs nonlinear functionals)
- **F157** — emergent: kurtosis, ZC, lag1 carry additive bias, not just scale changes
