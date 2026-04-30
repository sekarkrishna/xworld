# Session Summary — 30 April 2026 (nb41)

## Notebook 41 — Sensory Grounding Test

**Session goal:** Phase 2 opener. Test whether raw sensory transduction signals classify more cleanly than cognitively-constructed indices (VIX, ENSO), and whether same-sense datasets cluster nearer to each other.

**Short answer:** The sensory grounding hypothesis failed in its simple form. Temporal scale and physical process coherence are stronger predictors of classification quality than sensory category.

---

## Results

### Intel Lab thermistor (touch/thermoreception)
- Full 20-day trace → **burst** (d=2.683): building occupancy drift over 20 days gives burst fingerprint
- 7-day window → **burst** (d=2.496)
- Daily means (20 pts) → **irregular_osc** (d=6.305): under-sampled, noise dominates

The class REVERSES between temporal scales. This is the window-observer finding (nb38) applied to temporal aggregation resolution — same physical phenomenon, different temporal window, different class.

### NOAA NDBC wave height (vestibular)
- Wave height (hourly/daily) → **burst** (d=6.6): storm spikes produce right-skewed fingerprint; not a clean fit
- **Barometric pressure → declining_osc (d=2.85)**: SURPRISE — seasonal oscillation + annual drift matches declining_osc. Much cleaner than wave height. Two signals from the same buoy, different classes.

### Sensory vs cognitive comparison

| Dataset | Grounding | Class | d_min |
|---|---|---|---|
| Intel thermistor [daily] | sensory (touch) | irregular_osc | 6.305 |
| NDBC wave height [daily] | sensory (vestib.) | burst | 6.609 |
| GISS temperature [annual] | sensory (touch) | burst | 1.962 |
| VIX monthly | cognitive | burst | 11.505 |
| ENSO MEI v2 | cognitive | burst | 1.910 |

- Sensory mean d_min = 4.959 vs cognitive mean = 6.707 (ratio 1.35×, direction correct but weak)
- ENSO (cognitive composite) classifies at d=1.910 — **cleaner than both new raw sensors**
- Same-sense clustering fails: thermistor↔GISS = 8.243 > thermistor↔ENSO = 7.778

---

## Core findings

**F122:** Temporal scale determines class for the thermistor, not sensory modality. Full trace → burst; daily means → irregular_osc. Window-observer finding generalizes to aggregation resolution.

**F123:** Wave height → burst (storm-spike profile). Barometric pressure → declining_osc (d=2.85). Same physical sensor package, different variable, completely different classes.

**F124:** Sensory grounding hypothesis refuted in simple form. Revised hypothesis: classification quality = coherence of dominant physical process. ENSO (thermodynamically forced) classifies cleanly despite being cognitive. VIX (collective human cognition, no dominant physical process) is far from all centroids due to extreme kurtosis (=7.0), not due to cognitive construction per se.

---

## Revised hypothesis for Phase 2

> A signal classifies cleanly when it is dominated by a **single coherent physical process** at the temporal scale of observation. Sensory grounding is a correlate of this: physical sensors often capture single processes, but not always (under-sampled sensors are noisy). Cognitive constructs often aggregate multiple processes, but not always (ENSO is cognitively labelled but physically dominated).

**Next test:** Control for temporal scale. Use all signals at comparable scales and comparable n_points. Test whether signals with a known single dominant physical process (e.g., tidal pressure, solar irradiance) classify consistently regardless of whether they are "raw" or "processed".

---

*Total findings after nb41: 124*
