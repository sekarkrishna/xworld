# Session Summary — 01 May 2026 (nb46)

**Notebook:** 46 (Shape Composition Grokking)
**Findings:** F139–F144
**Total findings:** 144

---

## nb46 — Shape Composition Grokking

Tested two questions simultaneously: (1) does the 8-class composition table (what class results from mixing two shape signals?) have discoverable algebraic structure? (2) does a token-level transformer grokk over it (Power et al. 2022 protocol)?

### Composition table (Part A)

8×8 = 64 pairs, 500 samples each. Mixed signal = zscore(0.5*A_z + 0.5*B_z).

```
        BUR   OSC   SEA   TRE   INT   IRR   DCO   DCM
 BUR:   BUR   DCO   DCO   INT   INT   DCO   DCO   DCM
 OSC:   DCO   OSC   DCO   TRE   TRE   SEA   DCO   DCO
 SEA:   DCO   DCO   SEA   OSC   OSC   SEA   DCO   DCO
 TRE:   INT   TRE   OSC   TRE   INT   SEA   OSC   IRR
 INT:   INT   TRE   OSC   INT   INT   OSC   OSC   IRR
 IRR:   DCO   SEA   SEA   SEA   OSC   SEA   DCO   DCO
 DCO:   DCO   DCO   DCO   OSC   OSC   DCO   DCO   DCO
 DCM:   DCM   DCO   DCO   IRR   IRR   DCO   DCO   DCM
```

**Surprises:**
- Off-diagonal dominated by **declining_osc (43%)** — not irregular_osc (only 7%). The declining oscillator is the composition attractor.
- Diagonal: 7/8 idempotent. Exception: T[IRR, IRR] = seasonal. Two independent amplitude-modulated oscillations averaged together reduce variance → regular seasonal signal.
- **100% commutative** (T[i][j]=T[j][i] for all 28 symmetric pairs). Non-trivial: independently generated signals, nonlinear fingerprint.

### Grokking experiment (Part C)

Token-level transformer (2-layer, 128-dim, 4 heads, ~400k params). AdamW, weight_decay=1.0, 50k steps. Train=51 pairs × 3000 instances; Test=13 pairs × 3000 instances.

- **No grokking** confirmed (consistent with nb25's immediate-generalisation finding).
- Train → 100% at step 200. Val = 84.6% simultaneously — no memorisation gap.
- Val oscillates 53.8–84.6% under weight decay throughout training. Final = 69.2%.
- 9/13 test pairs succeed at 100%; 4 fail: (burst, oscillator) and (oscillator, integrated_trend) in both symmetric directions. These pairs' composition (→ declining_osc and → trend respectively) conflicts with the pattern the model extracts from training.

### Embedding analysis (Part D)

- **Spearman ρ(embedding, fingerprint) = +0.399** (p=0.035).
- Massive improvement over nb25's address-book geometry (ρ=−0.31).
- The composition task forces dynamic-similarity structure into token embeddings; the classification task does not.
- Closest embedding pair: trend/integrated_trend (emb_dist=0.047), consistent with their fingerprint proximity.

---

## Key results

| Finding | Prediction | Result |
|---|---|---|
| F139: off-diagonal dominant class | irregular_osc >50% | declining_osc 43% — **refuted** |
| F140: grokking | No grokking | Confirmed; val oscillates under WD |
| F141: ρ(embedding, fingerprint) | ρ > 0.0 | **ρ=+0.399** — confirmed |
| F142: dominant-disorder rule | >50% accuracy | 32% — **refuted** |
| F143: commutativity | approximate | **100% exact** — emergent |
| F144: T[IRR,IRR]=seasonal | — | Noise averaging → regularity — emergent |

---

## Next

**nb47:** Investigate the declining_osc composition attractor. Why does mixing two structurally distinct classes so often produce declining_osc? Map the feature-space geometry: where is the declining_osc centroid relative to the mixing paths between other class pairs? Test whether all inter-class mixing paths pass through or near the declining_osc basin.
