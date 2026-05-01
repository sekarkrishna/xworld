# Session Summary — 01 May 2026 (nb44, nb45)

**Notebooks:** 44 (Full Corpus Scale Scan) and 45 (Signal Decomposition Test)
**Findings:** F131–F138
**Total findings:** 138

---

## nb44 — Full Corpus Scale Scan

Applied the scale-CV metric from nb43 to all 19 datasets in the extended corpus (17 canonical + snow_cover + tidal + wave_height). For each dataset: log-spaced growing-window scan, CV(d_min, windows ≥ N//4).

**Data quality fix:** Arctic/antarctic sea ice cached data contained -9999 fill values; PDO contained 99.99 fill values. Without filtering these, d_min_full was 447 and CV was 2.95 (artifacts of corrupted zscore). Fixed by filtering extent>0 and |pdo|<90.

**Three regimes emerged:**

1. **Scale-stable, well-classified (CV < 0.12, d_min_full < 3):** keeling_seasonal (0.033), arctic_sea_ice (0.066), tidal_nyc (0.072), antarctic_sea_ice (0.075), ENSO (0.086), keeling_trend (0.086), sea_level (0.100), sunspot (0.121).
2. **Scale-stable, ambiguous (CV < 0.12, d_min_full > 10):** snow_cover (0.011, d=27.2), NAO (0.057, d=13.1) — stable fingerprint but outside all class basins.
3. **Scale-variable (CV > 0.23):** PDO (0.232), temperature (0.261), ocean_heat (0.295), WGMS (0.344), wave_height (0.425), PIOMAS (0.505), VIX (0.762), COVID (0.951).

**Key surprises:**
- Sea ice is the 4th/7th most scale-stable signal — the annual glacial cycle amplitude (~12 million km²) overwhelms the long-term decline at every window length tested
- NAO is scale-stable (CV=0.057) — not scale-variable as predicted. It's consistently irregular_osc at all scales but always far from the centroid ("orbiting outside the basin")
- VIX (0.762) and COVID (0.951) are correctly at the high end

**F132 confirmed:** Spearman ρ=0.833 for the 4 nb42-overlap signals (keeling_trend < ENSO < temperature < VIX).

**F134 (emergent):** The 2D diagnostic (CV × d_min_mean) identifies "taxonomically foreign" signals. Snow_cover and NAO are not multi-process (low CV) but are outside the 8-class taxonomy at every scale (high d_min). Best candidates for revealing unrepresented process types.

---

## nb45 — Signal Decomposition Test

STL (Seasonal-Trend-Loess) and bandpass decomposition of the thermistor (168h) and tidal gauge (336h). Does decomposing a multi-process signal make each sub-process more coherent?

**STL thermistor (period=24h):**
- Composite: irregular_osc, d=2.219
- seasonal_24h: **declining_osc, d=1.685** (50.4% variance) — BETTER
- trend: **integrated_trend, d=1.845** (15.2%) — BETTER
- residual: **burst, d=12.062** (45.5%) — FAR WORSE

The dominant-variance components gain coherence; the incoherent residual loses it. Not uniformly better.

Surprise: seasonal_24h is declining_osc because building diurnal amplitude is modulated by occupancy rhythm (weekday vs weekend) — the dominant process is itself modulated by a slower process.

**STL tidal (period=12h ≈ M2):**
- Composite: seasonal, d=0.686
- seasonal_12h: **seasonal, d=0.655** (86.1% variance) — slightly better
- trend: burst, d=2.075 (4.1%)
- residual: irregular_osc, d=5.652 (3.1%)

86.1% of tidal variance is the M2 tidal process. The thermistor/tidal contrast is the core prediction: 86.1% single-process → clean composite; 50.4%/45.5% split → intermediate composite.

**Bandpass thermistor:**
- Diurnal band (6-36h, 64.8% variance): d=1.121 — lowest, as predicted
- HVAC transients (<6h, 9.4% variance): d=26.709 — worst
- Variance fraction predicts d_min ordering

**Scale-CV of STL components:** Dominant seasonal component (CV=0.129) is 1.71× more scale-stable than composite (CV=0.221). Noise components are worse.

---

## Next

**nb46-48: Grokking transfer hypothesis.** Post-grokking transformer embeddings should form domain-agnostic representations testable via zero-shot geometry probe across domains. This is the experiment deferred since nb25 (which showed no grokking because shape classes were too syntactically distinct). Now: train a small transformer on the 8-class generators with weight decay, push past the plateau, look for the post-grokking embedding structure.
