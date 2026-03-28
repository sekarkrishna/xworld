"""
pipeline/scriptgen.py
Five-phase experiment script generation via LLM.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

FIVE_PHASE_TEMPLATE = '''# /// script
# requires-python = ">=3.13"
# dependencies = [
{dep_lines}
# ]
# ///

"""
Experiment: {title}
Hypothesis: {parent_hypothesis}
Generated: {timestamp}
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

ARTIFACT_DIR = ROOT / "artifacts" / Path(__file__).stem
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

# ── Phase 1: Data Acquisition ──────────────────────────────────────
from pipeline.datasets import ensure_dataset
{data_acquisition}

# ── Phase 2: Feature Extraction ────────────────────────────────────
from pipeline.extract import zscore, extract_features
{feature_extraction}

# ── Phase 3: Analysis ──────────────────────────────────────────────
{analysis}

# ── Phase 4: Artifacts ─────────────────────────────────────────────
{artifacts}

# ── Phase 5: Summary ──────────────────────────────────────────────
print(json.dumps({{
    "summary": {summary_expr},
    "metrics": {metrics_expr},
    "artifacts": {artifacts_list_expr},
    "verdict_suggestion": {verdict_expr},
    "datasets_used": {datasets_expr},
    "parameters_used": {params_expr},
}}))
'''


def generate_script(
    experiment_node_id: str,
    dataset_names: list[str],
    methodology: str,
    parameters: dict,
) -> str:
    """
    Generate a 5-phase experiment script via LLM.
    Returns the cleaned script content as a string.
    """
    from pipeline.graph import get_setting
    from pipeline.llm import call_model

    model = get_setting("autopilot_script_model", "claude-sonnet-4-6")

    prompt = f"""Generate a compact Python experiment script for XWorld.

Structure: PEP 723 header, then 5 phases:
1. Data Acquisition: ensure_dataset() calls
2. Feature Extraction: from pipeline.extract import zscore, extract_features
3. Analysis: the experiment logic
4. Artifacts: save to ARTIFACT_DIR
5. Summary: print(json.dumps({{"summary":..., "metrics":..., "artifacts":..., "verdict_suggestion":..., "datasets_used":..., "parameters_used":...}}))

Setup boilerplate:
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
ARTIFACT_DIR = ROOT / "artifacts" / Path(__file__).stem
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

Datasets: {json.dumps(dataset_names)}
Methodology: {methodology}
Parameters: {json.dumps(parameters)}

IMPORTANT: Keep the script concise. No verbose comments. The script MUST end with the json.dumps print statement.
Return ONLY the Python script."""

    script_content = call_model(
        model,
        [{"role": "user", "content": prompt}],
        max_tokens=8192,
    )
    cleaned = _clean_script(script_content)

    # Validate the script isn't truncated
    if not _is_complete_script(cleaned):
        raise RuntimeError(
            "Generated script appears truncated (missing Phase 5 JSON summary). "
            "Try again or use a model with higher output limits."
        )

    return cleaned


def save_script(experiment_node_id: str, script_content: str) -> str:
    """
    Save script to scripts/ directory using deterministic naming.
    Updates the experiment record in the DB with the script path.
    Returns the relative script path.
    """
    from pipeline.graph import _conn

    stem = f"exp_{experiment_node_id[:8]}"
    script_path = f"scripts/{stem}.py"
    full_path = ROOT / script_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(script_content)

    with _conn() as conn:
        conn.execute(
            "UPDATE experiments SET script_path = ? WHERE node_id = ?",
            (script_path, experiment_node_id),
        )

    return script_path


def _clean_script(raw: str) -> str:
    """Strip markdown fences if the LLM wrapped the script in them."""
    lines = raw.strip().splitlines()
    if lines and lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].startswith("```"):
        lines = lines[:-1]
    return "\n".join(lines)


def _is_complete_script(script: str) -> bool:
    """Check that a generated script has all 5 phases and ends with the JSON summary."""
    if not script or len(script) < 100:
        return False
    # Must contain the JSON summary print at the end (Phase 5)
    if "json.dumps(" not in script:
        return False
    # Check the script doesn't end mid-line (truncation indicator)
    last_line = script.rstrip().splitlines()[-1].strip()
    # Truncated scripts often end with an incomplete print(f or open paren
    if last_line.endswith("(") or last_line.endswith("f") or last_line.endswith(","):
        return False
    return True
