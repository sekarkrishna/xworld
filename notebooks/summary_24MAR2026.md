# XWorld — Progress Summary
**Date:** 24 March 2026
**Covers:** 23 March 2026 (Session 1) through 24 March 2026 (Session 2)

---

## Where We Started

The starting point was a question that came out of a longer philosophical conversation: if you strip away what a time series *represents* — whether it is a pandemic, a sunspot cycle, a predator-prey population, or a heartbeat — and look only at the *shape* of how it moves through time, do series from completely unrelated domains cluster together?

The hypothesis was simple: a COVID wave and an atmospheric CO2 trend and a sunspot cycle are all different things, but some of them might share the same underlying mathematical shape. If they do, a clustering algorithm working purely on shape features should group them together, blind to their domain of origin.

This is the XWorld experiment. The name reflects the ambition — to find cross-domain shape signatures that exist independently of what the world is measuring.

---

## Session 1 — 23 March 2026: Building the Foundation

### Choosing the datasets

Five initial datasets were chosen to represent clearly distinct dynamic shapes:

- **COVID first wave** — 202 countries, from the Our World in Data dataset. Each country's case curve rises fast and then falls. The shape is an asymmetric burst.
- **Sunspot cycles** — monthly records going back to 1749. An approximately 11-year cycle with a characteristic asymmetric shape (rises faster than it falls).
- **Lynx and hare populations** — Hudson Bay Company fur trading records from 1845 to 1935. Classic predator-prey oscillation where the two populations chase each other in roughly 10-year cycles.
- **Keeling CO2** — the famous Mauna Loa measurements since 1958. This one was immediately split into two because it contains two distinct dynamics superimposed: an annual seasonal oscillation (CO2 goes up in winter, down in summer) and a long-run rising trend driven by emissions. Treating them as one dataset would blur two genuinely different shapes, so they became two separate entities.
- **Global temperature** — NASA GISS station anomalies from 26 stations worldwide. These are departures from a long-run baseline, showing the slow warming trend with year-to-year variability around it.

Two additional datasets were added later in the same session:
- **COVID second wave** — same structure as the first wave but a different period. Added as an internal consistency check: if the clustering is working, both COVID waves should land in the same cluster.
- **Temperature** was also added at this stage (notebook 07).

### How shape was measured

Each time series was first z-score normalised — meaning the scale and average were removed, leaving only the shape of how the series moves. A country with a million cases and a country with a thousand cases would then look identical if their outbreak followed the same pattern.

Five features were then extracted from each normalised series:
- **Skewness** — whether the distribution leans left or right. A COVID wave is right-skewed because it rises fast and falls more slowly.
- **Kurtosis** — how extreme the peaks and troughs are relative to a normal bell curve.
- **Lag-1 autocorrelation** — how much today's value predicts tomorrow's. A smooth, slowly-changing series has high autocorrelation. A noisy, jumpy series has low autocorrelation.
- **Zero crossings** — how often the series crosses its own mean. Something oscillating rapidly crosses its mean often. Something that rises steadily almost never crosses it.
- **Slope** — the overall direction of travel across the whole series.

These five numbers were the fingerprint for every time series in the experiment.

### Clustering approach

UMAP was used to compress those five features into two dimensions for visualisation, and HDBSCAN was used to find density-based clusters. HDBSCAN was chosen because the number of shape classes was unknown — unlike k-means it does not require you to specify how many clusters to look for. It also marks points that do not belong to any cluster as noise (label -1).

The initial clustering broadly confirmed the hypothesis. Series from different domains with similar shapes did group together in the UMAP space. The directional burst (COVID), the slow drift, and the oscillatory series separated visually.

---

## Session 2 — 24 March 2026: Extending, Debugging, and Discovering

### Adding ECG as a new test case

A ninth dataset was added: the ECGFiveDays dataset from the UCR Time Series archive — 884 heartbeat segments from an electrocardiogram. The hypothesis was that ECG, being fast and oscillatory (heartbeats), should cluster away from the directional datasets.

**Download problem encountered.** The download cell used the standard Python requests library, which silently received an HTML error page from the data provider's website instead of the actual zip file. The server returned a 200 OK status (success) but the content was not a zip — so the check passed but the extraction failed silently. The data directory ended up empty.

The fix was to switch to Python's urllib library, which behaved consistently with curl. A validation step was also added to check that the downloaded content was actually a zip before attempting to extract it. Additionally, the check that prevented re-downloading ("directory already exists") was updated to also verify that the directory actually contains files, so a failed previous attempt would not block a fresh download.

The site was also returning 502 errors on the day, so the zip that had been cached from an earlier test was extracted manually into the right location.

### First run of the extended clustering — three bugs found

Once ECG data was loaded, the extended clustering notebook was run. Three problems appeared together:

**Bug 1 — too many tiny clusters.** The clustering algorithm had been configured with a minimum cluster size of 3. With over 600 time series in the dataset, this produced 76 clusters — far too many to be meaningful shape classes. Most of them contained just a handful of series. The minimum cluster size was raised to 15, which forced the algorithm to only recognise clusters large enough to represent a genuine shape pattern.

**Bug 2 — noise was being used as the reference.** HDBSCAN assigns the label -1 to points that do not belong to any cluster — these are called noise. With 76 tiny clusters and many unclassified points, the most common label for the COVID first wave turned out to be -1 (noise), not a real cluster. The scoring logic then used this as its reference point, comparing everything against noise. ECG being 17% noise looked like a match. The fix was to skip the noise label when finding the reference cluster.

**Bug 3 — temperature was going to noise.** After the above fixes, temperature was 100% noise. This initially looked like another bug, but feature analysis showed it was actually correct: temperature (slow, noisy, multi-decadal warming) and COVID (fast, smooth, 2-month burst) have very different mathematical fingerprints. The autocorrelation is different (0.95 for COVID vs 0.50 for temperature), the skewness is different (0.95 vs 0.01), and the zero crossings are different (0.02 vs 0.28). The original hypothesis had lumped "directional burst" and "slow directional drift" together as one shape — the data showed they are two distinct shapes. The minimum cluster size was also a contributing factor: with only 26 temperature stations and a minimum cluster size of 15, temperature could not form its own cluster even if it wanted to. Lowering to 8 fixed this. The hypothesis for temperature was updated: it should form its own cluster, not join the COVID cluster.

### Results after fixes — all three confirmed

With the fixes in place, all three new datasets behaved as the revised hypothesis predicted:
- COVID second wave landed in the same cluster as COVID first wave (55% of points).
- Temperature formed its own tight cluster, separate from COVID (92% cohesion).
- ECG landed in a completely different cluster from COVID.

### Discovering what actually separates ECG

Looking more carefully at ECG's features revealed something unexpected. ECG was assumed to be "oscillatory" and therefore would have high zero crossings. In fact ECG's zero crossings (0.078) are *lower* than keeling seasonal (0.167) and lynx-hare (0.172). What actually distinguishes ECG is its kurtosis: 15.165. A heartbeat signal has a very sharp spike (the QRS complex) surrounded by a long flat baseline. That spike-and-flat pattern produces extreme kurtosis, not high zero crossings. The clustering found it for the right reason, but not the reason originally assumed.

### Testing the periodic datasets

Attention turned to the datasets that were expected to be "periodic" — keeling seasonal, sunspot cycles, and lynx-hare. The hypothesis had been that these would cluster together as a periodic shape class. Several specific predictions were made:

- **Keeling trend** (the rising CO2 line, not the seasonal wobble) was expected to land with COVID, because both have high autocorrelation and very low zero crossings.
- **Keeling seasonal, sunspot, and lynx-hare** were all expected to stay away from the COVID cluster.

Results:
- **Keeling trend did not land with COVID.** It formed its own cluster. The reason: both keeling trend and COVID have high autocorrelation and low zero crossings, but COVID is right-skewed (it rises fast then falls), while keeling trend is symmetric (it just rises). Skewness is what separates a burst from a steady climb.
- **Keeling seasonal, sunspot, and lynx-hare** all correctly avoided the COVID cluster, but they also did not cluster *together*. Each landed in its own separate cluster. The three "slow periodic" shapes are more different from each other than expected.
- **Lynx-hare ended up in the same cluster as temperature.** A predator-prey oscillation from the 1800s and slow climate drift from modern weather stations share a shape class. What they have in common: no feature is extreme. Moderate autocorrelation, moderate zero crossings, flat kurtosis, low skewness. The cluster represents "no extremes" — moderate dynamics. This was an unexpected cross-domain pairing.

The shape taxonomy at this point had grown to six classes, each with a different primary discriminating feature.

### Testing whether "moderate dynamics" is genuine — streamflow experiment

The lynx-hare and temperature pairing raised a question: is their shared cluster a genuine shape class, or just a catch-all for everything that does not fit elsewhere? The way to test this is to bring in a new dataset that should have moderate dynamics *by design* — before seeing where it clusters.

River streamflow from 25 USGS gauging stations across the United States was chosen. Rivers have physical properties that should produce moderate dynamics: the catchment acts as a memory buffer (moderate autocorrelation), seasonal rainfall and snowmelt drive a regular annual cycle (moderate zero crossings), and most rivers have no strong long-term trend. The features were predicted before running: zero crossings between 0.15 and 0.25, autocorrelation between 0.50 and 0.70, near-flat kurtosis, moderate skewness.

**Download problem encountered.** The USGS website has separate API endpoints for monthly and daily data. The monthly endpoint turned out to return a 404 error. The daily endpoint worked. The fix was to download daily discharge and compute monthly averages from that.

**First run — prediction partially wrong.** Zero crossings and autocorrelation landed exactly in the predicted range. But skewness came in at 2.09 (predicted 0–0.6) and kurtosis at 6.93 (predicted below zero). The cause: river discharge follows a log-normal distribution. Most months have moderate flow, but occasional flood months create extreme positive spikes. After z-score normalisation those flood spikes remain as extreme outliers, inflating both the skewness and kurtosis far outside the "moderate" range. The temporal dynamics were correct but the distributional shape was not.

The fix was to log-transform the discharge values before extracting features. This is standard practice in hydrology — flow is almost always analysed on a log scale. After log-transformation, all four features landed in the predicted range: zero crossings 0.222, autocorrelation 0.700, kurtosis -0.308, skewness 0.184.

**Cluster result — not quite as predicted, but informative.** Log-streamflow landed in its own cluster (Cluster 4, 67% of the 24 stations), separate from the temperature + lynx-hare cluster (Cluster 1). The two clusters are neighbours in feature space — streamflow avoided every extreme cluster — but they are distinguishable. The key difference is autocorrelation: streamflow averages 0.700, temperature averages 0.503. The river catchment retains memory of rainfall slightly longer than the year-to-year climate variability in temperature anomalies.

The conclusion: "moderate dynamics" is a genuine shape region, not a catch-all. It has internal sub-structure. The 24 river stations form a tighter, more coherent group than the mix of temperature stations and lynx-hare population series, so the clustering correctly found two density peaks within the same broad region.

---

## Where We Ended Up

After two days and ten notebooks, a shape taxonomy has emerged across nine datasets from completely unrelated domains:

| Shape class | Datasets | What defines it |
|---|---|---|
| Fast smooth burst | COVID first wave, COVID second wave | Rises fast, falls, right-skewed, very smooth |
| Symmetric steady climb | Keeling CO2 trend | Perfectly smooth rise, symmetric, near-perfect memory |
| Moderate dynamics — lower memory | Temperature anomalies, lynx-hare | No extreme features; moderate autocorrelation |
| Moderate dynamics — higher memory | River streamflow (log-scale) | Same moderate character but slightly stronger memory |
| Left-skewed periodic | Keeling CO2 seasonal | Regular annual cycle, slightly left-skewed |
| Right-skewed slow periodic | Sunspot cycles | Roughly 11-year cycle, right-skewed |
| Spike dynamics | ECG heartbeats | Extreme kurtosis from sharp spikes on flat baseline |

Several things were not known at the start and became clear through the experiment:

1. "Directional" is not one shape class — fast burst and steady climb are different shapes, separated by skewness.
2. "Periodic" is not one shape class — keeling seasonal, sunspot, and lynx-hare all ended up in different clusters despite all being roughly periodic.
3. ECG is distinguished by kurtosis (spike shape), not by oscillation frequency as originally assumed.
4. "Moderate dynamics" is a genuine region, confirmed by an independent dataset (streamflow) landing nearby, and with internal sub-structure driven by autocorrelation (memory).
5. Raw river discharge is log-normal and must be log-transformed before shape features are extracted — the temporal dynamics are moderate but the distributional shape is not.

No single feature does all the work. Skewness separates burst from climb. Kurtosis isolates ECG. Autocorrelation and zero crossings together separate directional from periodic. The combination of five simple features is enough to distinguish seven shape classes across datasets that have nothing in common in their domain of origin.

---

## Open Questions for Next Sessions

- Are the three separate periodic clusters (keeling seasonal, sunspot, lynx-hare) genuinely different shapes, or an artefact of the clustering parameters?
- The keeling trend forming its own cluster (separate from COVID) — what does that shape class represent in the broader taxonomy?
- What would happen with more datasets added to the moderate dynamics region — would more sub-clusters emerge, or would they all fold into the existing two?
- Can the shape taxonomy be given interpretable names that hold across domains?
