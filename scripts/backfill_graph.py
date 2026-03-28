"""
scripts/backfill_graph.py
Backfill the XWorld knowledge graph with all work done in Sessions 1 and 2
(23-24 March 2026). Run once after init_db().

Source of truth: EXPERIMENTS.md, DECISIONS.md, summary_24MAR2026.md
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from pipeline.graph import init_db, add_node, add_edge, add_experiment, add_decision

# ---------------------------------------------------------------------------
# Initialise
# ---------------------------------------------------------------------------
init_db()
print("DB initialised.")

# ---------------------------------------------------------------------------
# ROOT QUESTION
# ---------------------------------------------------------------------------
n_root = add_node(
    type="question",
    title="Do time series from completely unrelated domains share underlying dynamic shapes that cluster together, independent of domain of origin?",
    content=(
        "Inspired by the philosophical question: can you read the nature of a system from the "
        "mathematical shape of its signal, regardless of what it is measuring? "
        "Origin: random_chats_x_world.txt — 'maybe there is a correlation between how glacier ice "
        "melts and how a turtle is breathing.' "
        "The XWorld experiment tests this computationally."
    ),
    status="completed",
)
print(f"Root question: {n_root}")

# ---------------------------------------------------------------------------
# INITIAL HYPOTHESES
# ---------------------------------------------------------------------------
n_h1 = add_node(
    type="hypothesis",
    title="5 features (skewness, kurtosis, lag1_autocorr, zero_crossings, slope) after z-score normalisation capture dynamic shape across domains",
    content=(
        "Minimal feature set — deliberately avoided domain-specific features. "
        "z-score removes amplitude, leaving only temporal shape. "
        "5 features cover: distributional shape, memory, oscillation frequency, directional drift."
    ),
    status="completed",
)
add_edge(n_root, n_h1, "branched_into")

n_h2 = add_node(
    type="hypothesis",
    title="UMAP + HDBSCAN can detect cross-domain shape clusters from this 5-feature representation",
    content=(
        "UMAP over PCA: preserves local structure. "
        "HDBSCAN over k-means: number of shape classes unknown a priori. "
        "Parameters settled: UMAP(n_neighbors=15, min_dist=0.1), HDBSCAN(min_cluster_size=8, min_samples=3)."
    ),
    status="completed",
)
add_edge(n_root, n_h2, "branched_into")

# ---------------------------------------------------------------------------
# SESSION 1 — Foundation (23 March 2026, notebooks 01-07)
# ---------------------------------------------------------------------------
n_exp1 = add_node(
    type="experiment",
    title="Session 1: Build 7-dataset feature matrix and run initial clustering (notebooks 01-07)",
    content=(
        "Datasets: COVID first wave (202 countries), sunspot cycles (1749-present), "
        "lynx-hare (1845-1935), Keeling CO2 seasonal, Keeling CO2 trend, "
        "COVID second wave (209 countries), global temperature (NASA GISS, 26 stations). "
        "Scripts: 01_covid_pipeline, 02_sunspot_pipeline, 03_lynx_hare_pipeline, "
        "04_keeling_pipeline, 05_cluster_all, 06_covid_second_wave, 07_temperature_pipeline."
    ),
    status="completed",
)
add_edge(n_h1, n_exp1, "prompted_by")
add_edge(n_h2, n_exp1, "prompted_by")
add_experiment(
    node_id=n_exp1,
    dataset="covid_first_wave, sunspot_cycles, lynx_hare, keeling_seasonal, keeling_trend, covid_second_wave, temperature",
    script_path="notebooks/05_cluster_all.ipynb",
    parameters={"umap_n_neighbors": 15, "umap_min_dist": 0.1, "hdbscan_min_cluster_size": 3, "hdbscan_min_samples": 1},
    artifact_paths=["data/processed/umap_by_domain.png", "data/processed/umap_by_cluster.png"],
    result_summary=(
        "Initial clustering broadly confirmed cross-domain shape groupings. "
        "Directional burst (COVID), slow drift, and oscillatory series separated in UMAP space. "
        "min_cluster_size=3 produced too many micro-clusters (76 in later run)."
    ),
)

n_r1 = add_node(
    type="result",
    title="Initial cross-domain clustering confirmed — shape groupings visible in UMAP space",
    content="COVID, temperature, oscillatory datasets separate. Parameter fragmentation (min_cluster_size=3) later identified as too small.",
    status="completed",
)
add_edge(n_exp1, n_r1, "answered_by")

# ---------------------------------------------------------------------------
# SESSION 2 — ECG + Bug Fixes (24 March 2026, notebooks 08-09)
# ---------------------------------------------------------------------------
n_exp2 = add_node(
    type="experiment",
    title="Session 2: Add ECG dataset, fix 3 bugs in clustering, re-run extended clustering (notebooks 08-09)",
    content=(
        "Bug 1: requests library silently received HTML instead of zip from timeseriesclassification.com. "
        "Fix: switch to urllib + zipfile.is_zipfile() validation. "
        "Bug 2: min_cluster_size=3 → 76 micro-clusters, COVID majority was noise (-1). "
        "Fix: min_cluster_size=15. "
        "Bug 3: scoring logic used -1 (noise) as reference cluster. "
        "Fix: skip -1 when finding reference and majority clusters. "
        "Final: min_cluster_size=8, min_samples=3 to allow small but cohesive datasets."
    ),
    status="completed",
)
add_edge(n_r1, n_exp2, "prompted_by")
add_experiment(
    node_id=n_exp2,
    dataset="ecg (UCR ECGFiveDays, 884 segments), all prior datasets",
    script_path="notebooks/09_cluster_extended.ipynb",
    parameters={"umap_n_neighbors": 15, "umap_min_dist": 0.1, "hdbscan_min_cluster_size": 8, "hdbscan_min_samples": 3},
    artifact_paths=["data/processed/xworld_extended_clustering.png", "data/processed/xworld_extended_profiles.png"],
    result_summary=(
        "All 3 predictions confirmed after fixes. "
        "COVID second wave → same cluster as first wave (55%). "
        "Temperature → own cluster (92% cohesion, Cluster 1). "
        "ECG → different cluster from COVID (Cluster 12, 33%). "
        "ECG distinguished by kurtosis=15.165 (spike dynamics), NOT by zero_crossings as assumed."
    ),
)

n_r2 = add_node(
    type="result",
    title="ECG isolated by kurtosis (spike dynamics), not oscillation frequency — unexpected discriminator",
    content=(
        "ECG zero_crossings=0.078, LOWER than keeling_seasonal (0.167) and lynx_hare (0.172). "
        "QRS complex creates extreme kurtosis on flat baseline. "
        "Clustering found ECG for the right reason, but not the assumed reason."
    ),
    status="completed",
)
add_edge(n_exp2, n_r2, "answered_by")

n_ins1 = add_node(
    type="insight",
    title="'Directional' is not one shape class — fast burst and slow drift are distinct, separated by skewness + autocorr",
    content=(
        "COVID: skewness=0.95, lag1=0.95, zc=0.023. "
        "Temperature: skewness=0.01, lag1=0.50, zc=0.277. "
        "Original hypothesis conflated these. The feature set correctly discriminates them."
    ),
    status="completed",
)
add_edge(n_r2, n_ins1, "prompted_by")

# ---------------------------------------------------------------------------
# SESSION 2 CONTINUED — Periodic datasets + keeling_trend (24 March 2026)
# ---------------------------------------------------------------------------
n_exp3 = add_node(
    type="experiment",
    title="Test periodic datasets and keeling_trend clustering predictions (notebook 09 extended)",
    content=(
        "Hypotheses tested: keeling_trend → Cluster with COVID (high lag1, low zc). "
        "keeling_seasonal, sunspot, lynx_hare → NOT COVID cluster. "
        "Result: keeling_trend formed own cluster (skewness difference, not autocorr). "
        "Periodic datasets did NOT cluster together — each formed own cluster."
    ),
    status="completed",
)
add_edge(n_ins1, n_exp3, "prompted_by")
add_experiment(
    node_id=n_exp3,
    dataset="keeling_trend, keeling_seasonal, sunspot_cycle, lynx_hare, ecg",
    script_path="notebooks/09_cluster_extended.ipynb",
    parameters={"umap_n_neighbors": 15, "umap_min_dist": 0.1, "hdbscan_min_cluster_size": 8, "hdbscan_min_samples": 3},
    artifact_paths=["data/processed/cluster_profiles_heatmap.png"],
    result_summary=(
        "keeling_trend: own cluster (C29, 100%) — not COVID. Discriminator: skewness (COVID=0.95, keeling_trend=0.075). "
        "keeling_seasonal: C0 (100%). sunspot_cycle: C13 (58%). lynx_hare: C1 (65%, same as temperature). "
        "ECG: C12 (33%). "
        "Lynx_hare + temperature share Cluster 1 — 'moderate dynamics' is a genuine shape class. "
        "Predator-prey oscillation and slow climate drift share 'no feature extremes'."
    ),
)

n_r3 = add_node(
    type="result",
    title="Skewness discriminates burst from steady climb — keeling_trend forms own cluster, not COVID",
    content=(
        "COVID skewness=0.95 (rises fast, falls). keeling_trend skewness=0.075 (symmetric monotonic rise). "
        "Both have high lag1 and low zc — but skewness separates the two directional classes."
    ),
    status="completed",
)
add_edge(n_exp3, n_r3, "answered_by")

n_r4 = add_node(
    type="result",
    title="Moderate dynamics is a genuine shape class — lynx-hare and temperature share Cluster 1",
    content=(
        "Common features: no extreme in any dimension. "
        "lag1≈0.50–0.68, zc≈0.17–0.28, flat kurtosis, low skewness. "
        "Predator-prey oscillation (ecology) and slow climate drift (climate science) — domain-blind pairing."
    ),
    status="completed",
)
add_edge(n_exp3, n_r4, "answered_by")

# ---------------------------------------------------------------------------
# SESSION 2 CONTINUED — Streamflow as moderate dynamics test
# ---------------------------------------------------------------------------
n_exp4 = add_node(
    type="experiment",
    title="Test streamflow as independent validation of 'moderate dynamics' shape class (notebook 10)",
    content=(
        "25 USGS gauging stations. Predicted features before running: zc≈0.15–0.25, lag1≈0.50–0.70, kurtosis<0, skewness≈0–0.6. "
        "Problem: raw discharge is log-normal. Flood spikes inflate skewness=2.09, kurtosis=6.93. "
        "Fix: np.log1p() transform (standard hydrology practice). "
        "After log-transform: zc=0.222 ✓, lag1=0.700 ✓, kurtosis=-0.308 ✓, skewness=0.184 ✓."
    ),
    status="completed",
)
add_edge(n_r4, n_exp4, "prompted_by")
add_experiment(
    node_id=n_exp4,
    dataset="streamflow_log (25 USGS stations)",
    script_path="notebooks/10_streamflow_pipeline.ipynb",
    parameters={"transform": "np.log1p", "umap_n_neighbors": 15, "hdbscan_min_cluster_size": 8},
    artifact_paths=["data/processed/features_streamflow.csv"],
    result_summary=(
        "Log-streamflow → Cluster 4 (67%), NOT Cluster 1 (temperature + lynx_hare). "
        "Sub-structure within moderate dynamics. Key discriminator: lag1_autocorr. "
        "Streamflow lag1=0.700 vs temperature lag1=0.503. Catchment memory > climate/ecological memory. "
        "Moderate dynamics confirmed as genuine shape region with internal sub-structure."
    ),
)

n_r5 = add_node(
    type="result",
    title="Moderate dynamics has internal sub-structure — lag1_autocorr splits it into two sub-clusters",
    content=(
        "C1: lower-memory moderate (temperature + lynx_hare, lag1≈0.50–0.68). "
        "C4: higher-memory moderate (log-streamflow, lag1≈0.70). "
        "Catchment buffering retains memory longer than climate/ecological variability. "
        "24 streamflow stations form tighter core than mixed C1."
    ),
    status="completed",
)
add_edge(n_exp4, n_r5, "answered_by")

# ---------------------------------------------------------------------------
# FINAL TAXONOMY INSIGHT
# ---------------------------------------------------------------------------
n_ins2 = add_node(
    type="insight",
    title="7-class shape taxonomy confirmed across 9 datasets from 7 domains — no single feature drives all separations",
    content=(
        "Classes: (1) fast smooth burst [COVID waves], "
        "(2) symmetric steady climb [keeling_trend], "
        "(3) moderate dynamics lower memory [temperature, lynx_hare], "
        "(4) moderate dynamics higher memory [log-streamflow], "
        "(5) left-skewed periodic [keeling_seasonal], "
        "(6) right-skewed slow periodic [sunspot_cycle], "
        "(7) spike dynamics [ECG]. "
        "Discriminators by class: skewness separates burst vs climb; "
        "kurtosis isolates ECG; lag1_autocorr + zc separate directional from periodic; "
        "lag1_autocorr sub-divides moderate dynamics."
    ),
    status="completed",
)
add_edge(n_r3, n_ins2, "prompted_by")
add_edge(n_r4, n_ins2, "prompted_by")
add_edge(n_r5, n_ins2, "prompted_by")

# ---------------------------------------------------------------------------
# OPEN BRANCHING QUESTIONS (pending, for next sessions)
# ---------------------------------------------------------------------------

n_q1 = add_node(
    type="question",
    title="Are the 3 separate periodic clusters (keeling_seasonal, sunspot_cycle, lynx_hare) genuinely different shapes, or an artefact of HDBSCAN parameter sensitivity?",
    content=(
        "All three are 'roughly periodic' but landed in different clusters (C0, C13, C1). "
        "Test: vary min_cluster_size and UMAP params — do they merge at coarser resolution? "
        "Add more datasets to each expected cluster to increase density."
    ),
    status="pending",
)
add_edge(n_ins2, n_q1, "branched_into")

n_q2 = add_node(
    type="question",
    title="What does the 'symmetric steady climb' shape class represent — is there another real-world series that lands with keeling_trend?",
    content=(
        "keeling_trend is currently the only member of its cluster (C29, 100%). "
        "Features: lag1≈1.0, skewness≈0, zc≈0.008, slope>0. "
        "Candidates: population growth curves, compound interest, cumulative adoption curves, glacier mass loss. "
        "Prediction: any smooth monotonic accumulation should land here."
    ),
    status="pending",
)
add_edge(n_ins2, n_q2, "branched_into")

n_q3 = add_node(
    type="question",
    title="Would more datasets in the moderate dynamics region produce more sub-clusters, or fold into the existing two?",
    content=(
        "Currently two sub-clusters: C1 (temperature, lynx_hare, lag1≈0.50–0.68) and C4 (streamflow, lag1≈0.70). "
        "Test: add ecological time series (predator-prey from other systems), "
        "other climate indices (ENSO, NAO), other river basins. "
        "Is lag1_autocorr the primary discriminator within moderate dynamics, or is a third sub-cluster possible?"
    ),
    status="pending",
)
add_edge(n_ins2, n_q3, "branched_into")

n_q4 = add_node(
    type="question",
    title="Can the 7 shape classes be given interpretable physical names that hold across domains?",
    content=(
        "Current labels are descriptive of features. Better: names from system dynamics. "
        "e.g., 'burst-decay' (COVID), 'monotonic accumulation' (keeling_trend), "
        "'damped noise' (temperature), 'catchment-buffered' (streamflow), "
        "'asymmetric cycle' (keeling_seasonal), 'resonant cycle' (sunspot), "
        "'spike-on-baseline' (ECG). "
        "Do these names hold when new datasets are added?"
    ),
    status="pending",
)
add_edge(n_ins2, n_q4, "branched_into")

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
print("\nBackfill complete.")
print("Nodes created:")
nodes_map = {
    "root_question": n_root,
    "hypothesis_features": n_h1,
    "hypothesis_clustering": n_h2,
    "exp_session1": n_exp1,
    "result_initial_clustering": n_r1,
    "exp_ecg_bugfixes": n_exp2,
    "result_ecg_kurtosis": n_r2,
    "insight_directional_split": n_ins1,
    "exp_periodic_datasets": n_exp3,
    "result_skewness_burst_vs_climb": n_r3,
    "result_moderate_dynamics": n_r4,
    "exp_streamflow": n_exp4,
    "result_moderate_substructure": n_r5,
    "insight_7class_taxonomy": n_ins2,
    "question_periodic_artefact": n_q1,
    "question_steady_climb": n_q2,
    "question_moderate_expansion": n_q3,
    "question_interpretable_names": n_q4,
}
for name, node_id in nodes_map.items():
    print(f"  {name}: {node_id}")
