# Session Summary — 25 April 2026 (nb33)

## What was done

nb33 — Blackjack Embedding: Geometric Navigation in a Finite Game.

**Parallel convergent experiment.** If XWorld's claim is that ODE fingerprints form a navigable geometric space, then any rule-governed system with a compressible structure should show the same property. Blackjack (200 decision states, analytic optimal policy via dynamic programming) provides a finite system with ground-truth geometry. The test: does a spectral embedding of the hit-transition graph correlate with the optimal value function V* and recover the optimal policy?

**Two tests:**
- T1: Spearman |ρ(V*, spectral component)| > 0.50 → positive
- T2: Logistic regression on spectral embedding → action accuracy > 70% → positive

**Result: NEGATIVE on both tests.**

| Test | Result | Threshold |
|---|---|---|
| T1: |ρ(V*, best spectral)| | 0.175 | >0.50 positive |
| T2: classifier accuracy | 0.495 ± 0.149 | >0.70 positive |
| T3: ρ(spectral, P(win)) | −0.186 | — |

---

## Root cause

The hit-transition graph decomposes into 10 structurally identical subgraphs — one per dealer upcard. Hit dynamics are dealer-blind: card draw probabilities are the same regardless of the dealer's face card. The spectral embedding assigns identical coordinates to states that differ only in dealer upcard. V* varies enormously across dealer upcards (du=6 is player-favourable; du=10 is not). The embedding is structurally blind to the dimension that matters most.

This is a failure of the specific graph encoding (transitions without payoffs), not a failure of the geometric navigation principle.

---

## Key findings

**F94:** Spectral embedding T1 NEGATIVE — |ρ| = 0.175. Dealer upcard is invisible to hit-topology; V* variation is concentrated in the invisible dimension.

**F95:** T2 NEGATIVE — accuracy 0.495, below majority baseline 0.550. Linear classifier on a 1D projection of a 2D decision boundary performs near-randomly.

**F96:** ρ(spectral, P(win)) = −0.186. Structural and oracle embeddings are unrelated because they encode different information: hit dynamics alone vs. dynamics + terminal payoffs. **Key constraint for structural embeddings:** the graph must contain full information for geometric navigation to work. XWorld's 6-feature fingerprint is a full encoding (dynamics + boundary structure); Blackjack hit-graph is partial.

---

## Implication for XWorld

The negative result clarifies why XWorld works: the 6-feature fingerprint encodes both dynamics (lag1, ZC) and boundary/terminal structure (slope, baseline_delta, skewness). The Blackjack experiment isolates exactly why a full encoding is required. Not escalating to Poker — the negative result has a clean structural explanation, not ambiguity about scale.

## Findings added
F94–F96. Total findings: 96.
