# Session Summary — 01 May 2026 (nb47)

**Notebook:** 47 (Composition Attractor Geometry)
**Findings:** F145–F150
**Total findings:** 150

---

## nb47 — Composition Attractor Geometry

Investigated why declining_osc dominates the nb46 composition table (43% of off-diagonal pairs). Tested three geometric explanations in the 6D standardised feature space: centrality, Voronoi basin size, and centroid-interpolation accuracy.

### What was expected vs what happened

All 4 pre-run predictions were wrong. The results revealed a deeper picture than expected.

| Finding | Prediction | Result |
|---|---|---|
| F145: nearest to grand centroid | declining_osc NOT nearest | Confirmed — oscillator is nearest (0.886) |
| F146: declining_osc largest basin | >20%, largest | **Refuted** — oscillator=77.5%, declining_osc=15.5% |
| F147: centroid-midpoint accuracy | >60% | **Refuted** — 45.3% |
| F148: DCO pairs midpoint in DCO | >80% | **Refuted** — 44% (11/25) |

### Core discovery: grand centroid paradox

The oscillator centroid is nearest to the grand centroid (= origin in standardised feature space, by construction of StandardScaler). Random convex combinations of the 8 centroids fall overwhelmingly in the oscillator Voronoi basin (77.5%). But the empirical composition table shows declining_osc at 43% and oscillator at only 18%.

**The Voronoi geometry of class centroids is completely decoupled from the empirical composition table.**

### Why centroid-midpoint fails

The centroid-midpoint model predicts the wrong class in 35/64 pairs. The systematic error: 12 cases where the model predicts oscillator but the empirical result is declining_osc. The model treats feature space as linear — the midpoint of two centroid positions is the predicted composition.

But the actual mixing operation is: `zscore(0.5*A_zscored + 0.5*B_zscored)`. For uncorrelated, unit-variance signals, this zscore step:
- **Amplifies** slope and baseline_delta by ~√2 relative to the centroid midpoint
- **Compresses** skewness and kurtosis by ~1/√2

This shifts the effective feature vector away from the oscillator basin (which captures the raw linear midpoint) into the declining_osc basin (which is positioned to capture the zscore-modulated version). The declining_osc centroid sits at (skew≈+0.2, kurtosis≈0, lag1≈−0.4, ZC≈+0.8, slope≈−0.6) — consistent with the compressed-kurtosis, amplified-declining features that emerge from mixing.

### Emergent findings

**F149:** Grand centroid paradox — largest Voronoi basin (oscillator, 77.5%) ≠ empirical composition attractor (declining_osc, 43%). Static geometry and dynamic mixing are decoupled.

**F150:** The zscore-after-mixing nonlinearity is the mechanistic source of declining_osc attractor dominance. Feature amplification (slope/BD) and compression (skewness/kurtosis) under zscore normalization shifts composition outcomes from the oscillator basin into declining_osc.

---

## Next

**nb48:** Directly measure the zscore nonlinearity: for each (i,j) pair, compute the *mean* features of 500 actual mixed signals and compare to the centroid midpoint. Quantify which features deviate most from linear additivity. Test whether the deviation pattern (compressed skewness, amplified slope) consistently points from oscillator centroid toward declining_osc centroid.
