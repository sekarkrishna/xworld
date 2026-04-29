# Session Summary — 29 April 2026 (nb39)

## What was done

nb39 — Thunder Hypothesis Phase 3 Test: TDA and RQA as Independent Measurement Systems

Applied two measurement frameworks from completely different mathematical traditions to the canonical 9-class generators and compared their discriminative power against the 6-feature fingerprint.

- **Part A:** Topological Data Analysis (ripser) — delay-embed each series (τ=4, dim=3) into a 56-point 3D point cloud, compute H0/H1 persistent homology, extract H1_max (loop prominence).
- **Part B:** Recurrence Quantification Analysis (pure NumPy) — compute recurrence matrix in phase space, extract DET (determinism), LAM (laminarity), ENTR.
- **Part C:** 100-instance cluster test — UMAP+HDBSCAN on all three feature sets, ARI vs 9-class ground truth.

---

## Part A: TDA results

| Class | H1_max | H1_count |
|---|---|---|
| oscillator | 2.180 | 1.3 |
| seasonal | 1.600 | 8.4 |
| eco_cycle | 1.326 | 9.7 |
| declining_osc | 1.281 | 18.2 |
| irregular_osc | 1.316 | 7.9 |
| burst | 1.468 | 7.4 |
| trend | 0.013 | 1.5 |
| integrated_trend | 0.000 | 1.0 |
| declining_monotonic | 0.000 | 1.0 |

Ratio (periodic/aperiodic groups) = **2.9x** — just below predicted 3x.

Key surprise: `irregular_osc` and `burst` have strong H1 comparable to periodic classes. Noisy signals create many short-lived phase-space loops; transient signals create brief loops. The real TDA boundary is **trend-family vs all-others**, not periodic vs aperiodic.

---

## Part B: RQA results

| Class | DET | LAM |
|---|---|---|
| integrated_trend | 0.497 | **0.994** |
| declining_monotonic | 0.494 | **0.994** |
| trend | 0.456 | **0.953** |
| oscillator | 0.460 | 0.738 |
| eco_cycle | 0.410 | 0.734 |
| declining_osc | 0.455 | 0.651 |
| irregular_osc | 0.349 | 0.663 |
| seasonal | 0.421 | 0.614 |
| burst | 0.318 | 0.671 |

**LAM confirmed:** trend-family = 0.95–0.99; all others = 0.61–0.74. Clean gap.  
**DET prediction reversed:** integrated_trend has highest DET (0.497), not seasonal. DET range (0.32–0.50) is too narrow to be a reliable discriminator.

---

## Part C: Cluster test

| Method | ARI | n_clusters |
|---|---|---|
| 6-feature fingerprint | 0.410 | 40 |
| TDA only | 0.185 | 48 |
| RQA only | 0.297 | 41 |
| **TDA + RQA combined** | **0.415** | 40 |

Receptor gap = **−0.004** (essentially zero). TDA+RQA combined matches the fingerprint exactly.

Both methods over-segment (40 clusters for 9 classes). Per-class: trend is 100% pure under TDA+RQA; eco_cycle is fragmented (17% dominant, 36% noise).

---

## Key findings

**F116:** TDA H1_max cleanly separates trend-family (H1≈0) from all others (H1≥1.28). The predicted boundary (periodic vs aperiodic) was wrong — irregular_osc and burst also have strong H1. Real TDA boundary: drift vs non-drift.

**F117:** LAM is the key RQA discriminator (trend-family: 0.95–0.99; others: 0.61–0.74). DET ranking prediction was reversed. Both TDA and RQA independently identify the same trend-family/all-others boundary.

**F118:** TDA+RQA ARI (0.415) ≈ fingerprint ARI (0.410). Receptor gap ≈ 0. The predicted fingerprint advantage from orientation-sensitive features did not appear. The 9-class taxonomy is not privileged to the fingerprint — independent measurement systems converge on the same cluster structure.

**Thunder hypothesis revised:** The dynamic structure (loop vs drift, regular vs chaotic) is in the world. The taxonomy is in the measurement. The trend-family boundary is the most robust observer-independent division. The 9-class within-family distinctions are real (multiple frameworks converge) but framework-relative (each method has different blind spots).

---

## Findings added
F116–F118. Total findings: **118**.
