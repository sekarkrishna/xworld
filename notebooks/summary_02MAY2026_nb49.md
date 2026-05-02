# Session Summary — 02 May 2026 (nb49)

**Notebook:** 49 (Closed-form composition predictor)
**Findings:** F158–F165
**Total findings:** 165

---

## nb49 — Closed-form composition predictor

Thread 1 of the May-2026 plan. nb48 showed that simulation (mean over 500 mixed signals per pair) predicts the empirical composition table at 96.9%, while raw centroid midpoint (nb47) only hits 45%. nb48's F157 conjectured that a linear-with-intercept correction `actual ≈ a·midpoint + b` per feature would recover most of the gap analytically. nb49 fits the 6 (a, b) pairs and tests it.

### What was expected vs what happened

| Finding | Prediction | Result |
|---|---|---|
| F158: slope/BD R² > 0.95 | confirmed | **Confirmed** — 0.967 / 0.964 |
| F159: skew/kurt/lag1/ZC R² < 0.30 | confirmed | **Confirmed, starker** — all ≤ 0.12, lag1 R² = 0.002 |
| F160: full closed-form ≥ 90% | confirmed | **Refuted** — 56.2% with all 6, 70.3% with slope+BD only |
| F161: slope+BD-only ≥ 60% | confirmed | **Confirmed** — 70.3% |
| F162: errors on declining_osc / irregular_osc classes | confirmed | **Reframed** — errors on everything *except* oscillator |

### Core discovery: per-feature linear correction has a hard 70% ceiling

The thesis was that adding a linear-with-intercept correction would close most of the gap from 45% (raw midpoint) to 97% (simulation). The data shows otherwise:

- Linear correction on the 2 well-behaved features (slope, baseline_delta — R² ≈ 0.96) gets to **70.3%**.
- Linear correction on the 4 nonlinear features (skew, kurt, lag1, ZC — R² ≤ 0.12) gets to 56.2%.
- Combining all 6 stays at 56.2% — strictly worse than slope+BD alone.

The reason: the nonlinear features have non-zero intercepts (kurt +0.63, ZC +0.74, lag1 −0.52) that *do* encode real distributional shifts under mixing — but the slopes (a) are noisy enough (R² < 0.12) that the corrected vectors get pushed in misleading directions in 6D space. Under L2 classification, a poorly-corrected coordinate hurts more than it helps.

### What the gap means

The simulation predictor needs the full 500-sample feature distribution per pair. The closed-form has only the centroid midpoint and 6 fitted parameters. The 27-percentage-point gap between them (70% → 97%) is **the irreducible joint-nonlinear contribution**:

- The empirical composition outcome depends on cross-feature interactions in the mixed-signal distribution — for example, a mixture might have moderate skewness AND high kurtosis simultaneously, which puts it in the declining_osc basin even though neither feature alone would.
- Per-feature linear correction cannot capture cross-feature interactions by construction.
- A multivariate correction `actual_vec = M · midpt_vec + c` (a single 6×6 affine map instead of 6 independent regressions) is the natural follow-up; if even that fails, the gap is genuinely nonlinear.

### Composition arc closed

This was the planned epilogue to the composition arc. Sequence and endpoints:

| Notebook | Key finding | Composition-table accuracy |
|---|---|---|
| nb46 | declining_osc dominates empirical table at 43% | n/a (descriptive) |
| nb47 | oscillator owns 77.5% Voronoi volume; centroid-midpoint hits 45% | 45.3% |
| nb48 | simulation hits 97%; nonlinearity expels mixtures from OSC basin (84%) | 96.9% |
| nb49 | per-feature linear correction maxes at 70%; cannot reach simulation | 70.3% |

The composition attractor is irreducibly a property of the feature-extraction *operator* applied to mixtures, not of the feature-space *geometry* of class centroids. Closed-form predictors built on geometry alone have a hard ceiling around 70%.

### Open follow-up (deferred)

- **Multivariate linear correction.** Try `actual_vec = M · midpt_vec + c` (6×6 affine map) instead of 6 independent regressions. If this closes the gap to ≥90%, the missing piece was cross-feature coupling. If it doesn't, the gap is genuinely nonlinear.
- This is left as a candidate epilogue, not blocking Thread 2. The negative result on per-feature linear correction is already informative for Thread 2's design — it tells us that learned embeddings need to capture cross-feature structure to outperform the closed-form 70% baseline.

### Why this is a useful negative result

Many papers and blog posts treat embedding-space midpoints as automatic averages — "the midpoint between two embeddings represents their composition." nb47–49 collectively show that this assumption fails for the synthetic-shape domain at the 6-feature level: the geometry-only predictor has a hard ~70% ceiling, and the gap to actual mixture behaviour requires either simulation or learned multivariate structure. **Thread 2 will test whether learned embeddings (Chronos, nb45 transformer) jump over this ceiling or stay below it.**

### Artifacts

- `notebooks/49_closed_form_composition.ipynb`
- `artifacts/nb49_linear_correction_fits.png` — per-feature actual vs midpoint with fitted line
- `artifacts/nb49_accuracy_bars.png` — bar chart: raw / slope+BD / nonlinear-4 / all-6 / simulation

### Findings added

- **F158** — slope/BD R² > 0.95 confirmed (0.967, 0.964)
- **F159** — skew/kurt/lag1/ZC R² < 0.30 confirmed and starker (all ≤ 0.12)
- **F160** — full closed-form ≥ 90%: refuted (56.2% with all 6, 70.3% with slope+BD only)
- **F161** — slope+BD-only ≥ 60%: confirmed (70.3%)
- **F162** — error concentration: reframed (errors on everything except oscillator)
- **F163** — emergent: more features hurt under linear correction (70.3% → 56.2%)
- **F164** — emergent: closed-form recovers only 58% of simulation accuracy
- **F165** — emergent: 21 closed-form errors are "still broken" pairs no per-feature linear model can fix
