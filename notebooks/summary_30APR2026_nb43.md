# Session Summary — 30 April 2026 (nb43)

## Notebook 43 — Scale Inflection Test

**Session goal:** Test whether d_min plateaus for single-process signals once the window captures ≥1 dominant cycle, and whether multi-process signals fail to plateau. Uses only cached data from nb41+nb42.

---

## Experiment design

**Signal A — Tidal gauge (NOAA CO-OPS Station 8518750, 2023):** 22 log-spaced windows from 6h to 8760h. Dominant process: M2 semi-diurnal tide (period 12.42h). Prediction: d_min drops sharply near 12.5h and plateaus; CV < 0.15.

**Signal B — Intel Lab thermistor hourly (sensor 48):** Same approach, 6h to 480h. Dominant cycle: diurnal (~24h solar+HVAC), competing with occupancy and weather. Prediction: d_min variable; CV > 0.30.

**Signal C — Scale stability comparison:** CV(d_min, windows ≥ 24h) for both. Class assignment across scales.

---

## Predictions

- **F128:** Tidal d_min < 1.5 for all windows ≥ 12.5h; CV(d_min, ≥24h) < 0.15.
- **F129:** Thermistor CV(d_min, ≥24h) > 0.30.
- **F130:** Steepest d_min drop near M2 period (12.5h) for tidal; near diurnal period (24h) for thermistor.

---

## Results

*[To be filled after running nb43]*

---

*Total findings after nb43: 130 (anticipated)*
