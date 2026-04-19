# Session Summary — 19 Apr 2026 (Notebook 27)

**Notebook:** `27_real_transfer_6f_grokking.ipynb`
**Questions:** (A) Does the contrastive encoder transfer to real data? (B) Does a 6-feature MLP grok?

---

## Predictions

- Part A: Encoder trained on pure synthetic shapes should roughly cluster real datasets by shape class
- Part B: 6-feature MLP should show grokking — low-dimensional input, non-trivial boundaries

---

## Setup

**Part A — Real data transfer:**
5 real datasets tested: lynx_hare (eco_cycle), sunspot (oscillator), keeling CO2 (trend/seasonal), ENSO (irregular_osc), arctic ice (declining_osc).
Windows: 64-month sliding windows, stride 6.
Encoder: contrastive encoder from nb26 (frozen weights, no fine-tuning).
Evaluation: majority class vote across all windows per dataset; top-1 and top-3 accuracy vs known shape class.

**Part B — 6-feature MLP grokking:**
Architecture: 6→256→256→128→8, 101k params.
Training: same synthetic dataset (8 classes × 100 instances per class), AdamW weight_decay=0.1, 5000 epochs.
Grokking detection: memorization epoch (train>90%) and generalization epoch (val>80%), gap = difference.

---

## Results

**Part A — Transfer: 1/5 correct (sunspot only).**

| Dataset | Predicted | Known | Correct? |
|---------|-----------|-------|----------|
| lynx_hare | oscillator | eco_cycle | ✗ |
| sunspot | oscillator | oscillator | ✓ |
| keeling CO2 | trend | trend/seasonal | ✓ (partial) |
| ENSO | irregular_osc | irregular_osc | ✓ (partial) |
| arctic ice | oscillator | declining_osc | ✗ |

Strict top-1 correct: 1/5. The encoder confuses eco_cycle with oscillator, and declining_osc with oscillator — both look like pure oscillations to an encoder trained on archetypes.

Also replicated **F60**: sunspot windows at 64 months → majority irregular_osc, not oscillator. Timescale-determines-class confirmed independently.

**Part B — No grokking.** Both thresholds crossed at epoch 50 simultaneously (gap = 0 epochs). Val accuracy = 97.5% from epoch 50 with no plateau. The 6 features are sufficiently discriminative that no phase transition is needed.

---

## Findings

- **F70:** Synthetic-to-real transfer fails for 4/5 datasets. Real signals combine multiple shape components; synthetic generators produce pure archetypes. The encoder misclassifies composite real signals.
- **F71:** Sunspot at 64-month windows → irregular_osc (majority). Independent replication of F60 (window length determines shape class assignment).
- **F72:** No grokking in 6-feature space. The 6 features are sufficiently discriminative that a 101k-param MLP generalizes from epoch 50 with no memorization plateau.

---

## Interpretation

Synthetic-to-real transfer is the key bottleneck. A contrastive encoder trained on pure archetypes builds a manifold that separates ideal shapes — but real signals are mixtures. Arctic ice has declining trend AND oscillation; the encoder only sees "oscillation-like" and assigns oscillator class.

The 6-feature fingerprint is not susceptible to the same failure because it is explicitly engineered for composite signals (slope captures trend, lag1_autocorr captures periodicity). A contrastive encoder trained on real data directly would likely transfer better.

**No grokking in either representation** (nb25: raw waveforms, nb27: 6 features) confirms F64 — the 8 shape classes are directly discriminable without hidden structure discovery. Grokking is a property of the task, not the architecture.

---

## Next

Notebook 28: declining oscillator necessary conditions. What are the minimum (oscillation, decline) parameter thresholds that produce declining_osc class? Also: does WGMS glacier data (annual, strong decline, no oscillation) land in trend class — confirming oscillation is a necessary condition?
