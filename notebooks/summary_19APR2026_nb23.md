# Session Summary — 19 April 2026 (Notebook 23)

## What was done

**Notebook 23: Latent Arithmetic Space + XWorld Shape Distortion**

Two-part experiment connecting the arithmetic embedding ideas from today's theoretical session to XWorld's shape classes.

---

## Part A: Arithmetic Latent Space

Trained two arithmetic nets on +−×÷ examples up to n=1000:
- **Raw encoder**: input = n/1000 (1D scalar)
- **Structured encoder**: input = [log(n)/log(1000), n/1000, n%2, frac(log10(n))] (4D)

Both trained with MSE + inverse-consistency + commutativity losses. 50k training examples. 40 epochs.

### Key results

| Test | True | Raw err% | Structured err% |
|---|---|---|---|
| 27 + 48 | 75 | 3.6% | 14.6% |
| 489 + 578 | 1067 | 0.1% | 0.0% |
| 50k + 70k | 120k | 4.1% | 32.0% |
| 400 × 300 | 120k | 98.8% | 98.6% |
| 10k ÷ 50 | 200 | 4540% | 4918% |

Raw encoder outperformed structured on addition extrapolation. Both failed completely on multiplication and division extrapolation.

PCA of structured encoder: ×10 shifts in PC1 = −0.73 (1→10), −1.22 (10→100), −5.05 (100→1000). Non-uniform — linear geometry, not logarithmic.

---

## Part B: XWorld Shape Classes Under Distortion

8 synthetic shape classes, 50 instances each. 4 distortion types: time_reverse, amplitude_flip, noise (σ=0.1/0.3/0.7), time_warp (factor=0.7/1.4).

### Feature profile of canonical instances

| Class | skewness | lag1 | zero_cross | baseline_delta |
|---|---|---|---|---|
| burst | 1.177 | 0.976 | 0.036 | −0.135 |
| oscillator | −0.151 | 0.955 | 0.092 | −0.516 |
| irregular_osc | 0.276 | 0.832 | 0.127 | −0.756 |
| trend | 0.090 | 0.998 | 0.018 | +3.135 |
| integrated_trend | −0.007 | 1.000 | 0.016 | +3.139 |

Note: trend and integrated_trend are nearly identical in all 6 features — the two classes are adjacent in feature space.

### Boundary crossing rates

| Class | amplitude_flip | time_reverse | noise | time_warp |
|---|---|---|---|---|
| oscillator | 0% | 0% | 59% | 0% |
| burst | 100% | 0% | 41% | 0% |
| trend | 100% | 100% | 34% | 0% |
| integrated_trend | 100% | 100% | 69% | 4% |
| seasonal | 100% | 100% | 67% | 0% |
| declining_osc | 100% | 100% | 54% | 0% |
| irregular_osc | 18% | 4% | **1.3%** | **83%** |
| eco_cycle | 18% | 16% | 59% | 29% |

### Stability ranking (boundary crossing rate, any distortion)

1. oscillator — 0.254 (most robust)
2. irregular_osc — 0.274
3. burst — 0.317
4. eco_cycle — 0.383
5. trend — 0.431
6. declining_osc — 0.517
7. seasonal — 0.571
8. integrated_trend — 0.594 (most fragile)

### Crossing topology (where distorted instances go)

- trend → seasonal, irregular_osc
- integrated_trend → seasonal, trend
- seasonal → integrated_trend, irregular_osc
- declining_osc → irregular_osc, eco_cycle
- burst → irregular_osc, eco_cycle
- oscillator → irregular_osc, eco_cycle
- **irregular_osc is the central sink** — receives distorted instances from 5 of 7 other classes

---

## The main structural finding

The 8 shape classes split into two groups:

**Directionally-defined** (trend, integrated_trend, seasonal, declining_osc): class identity depends on slope sign and baseline_delta sign. Amplitude-flip and time-reversal = 100% boundary crossing. Tightest clusters in natural feature space (baseline spread 0.07–0.64) but most fragile attractors.

**Shape-defined** (oscillator, burst, irregular_osc, eco_cycle): class identity is orientation-invariant. Amplitude-flip and time-reversal = 0–18% crossing. Looser natural clusters but robust attractors.

**Contrast with Chronos (nb21 Finding 52):** Chronos is invariant to amplitude-flip and time-reversal for ALL 8 classes. The 6-feature fingerprint is NOT. This means Chronos encodes shape-defined features only; the 6-feature fingerprint encodes both directional and shape features. The two representations are complementary, not interchangeable.

**irregular_osc as feature-space attractor:** Noise barely affects irregular_osc (1.3% crossing) because chaotic amplitude variability is its defining feature. Time_warp destroys it (83%) because timescale is the one structural property it depends on. irregular_osc is the central attractor of the feature space — the default state when structure is partially destroyed.

---

## Prediction accuracy

| Prediction | Result |
|---|---|
| Structured encoder extrapolates better than raw | WRONG — raw encoder outperforms on addition extrapolation |
| Trend classes most stable, burst most fragile | WRONG — exact opposite. Oscillator most stable, integrated_trend most fragile |
| σ=0.1 noise preserves all classes | WRONG — eco_cycle and oscillator cross at high rates even at low noise |
| ×10 = uniform shift in PCA space | WRONG — shift grows with n (linear geometry, not log) |

All four main predictions were wrong. This is the most informative session in terms of overturned assumptions.

---

## Open questions

1. **Why did all predictions invert?** The inversion pattern is systematic: the tightest classes are the most fragile; the loosest are the most robust. Is this a general principle of attractor basins?
2. **Chronos vs 6-feature divergence on directionality** — should the 6-feature fingerprint be made orientation-invariant (use |slope|, |baseline_delta|)? Would that collapse the 8 classes or refine them?
3. **irregular_osc as sink** — does this reflect something real about the XWorld datasets, or is it an artefact of synthetic class generation?
4. **Arithmetic**: what loss function would force log-space geometry? Multiplicative consistency loss: `predict(a*b, b, '/') ≈ a` applied during training?

---

## Findings this session: 53–57 (5 new findings)

## Total findings to date: 57

## Notebooks completed: 01–22 (nb22 pending re-run), 23
