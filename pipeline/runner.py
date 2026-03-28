"""
pipeline/runner.py
Experiment queue runner.
Picks the next queued item, executes the associated script, captures output,
then updates the database with results.
"""
from __future__ import annotations

import subprocess
from datetime import datetime, timezone
from pathlib import Path

import json as _json

from pipeline.graph import (
    get_next_queued,
    update_queue_item,
    update_node_status,
    get_node,
    get_experiment,
    update_experiment_results,
    add_node,
    add_edge,
    enqueue,
    init_db,
)

ROOT = Path(__file__).parent.parent


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def run_next() -> dict:
    """
    Pick the next queued item and run it.
    Returns a status dict with keys: status, queue_id, node_id, output.
    """
    item = get_next_queued()
    if not item:
        return {"status": "empty", "message": "Nothing in queue."}

    queue_id = item["id"]
    node_id = item["node_id"]
    node = get_node(node_id)

    update_queue_item(queue_id, "running", started_at=_now())
    update_node_status(node_id, "running")

    exp = get_experiment(node_id)
    if not exp or not exp.get("script_path"):
        msg = f"No script path set for node {node_id}. Cannot execute."
        update_queue_item(queue_id, "failed", run_output=msg, completed_at=_now())
        update_node_status(node_id, "pending")
        return {"status": "failed", "queue_id": queue_id, "node_id": node_id, "output": msg}

    script = ROOT / exp["script_path"]
    if not script.exists():
        msg = f"Script not found: {script}"
        update_queue_item(queue_id, "failed", run_output=msg, completed_at=_now())
        update_node_status(node_id, "pending")
        return {"status": "failed", "queue_id": queue_id, "node_id": node_id, "output": msg}

    # Tracking protocol integration
    from pipeline.tracking import get_tracker
    tracker = get_tracker()
    params = _json.loads(exp.get("parameters_json") or "{}")
    tracker.start_run(node_id, params)

    try:
        result = subprocess.run(
            ["uv", "run", str(script)],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
            timeout=600,
        )
        output = result.stdout + ("\n--- STDERR ---\n" + result.stderr if result.stderr else "")

        if result.returncode == 0:
            # Auto-collect artifacts and parse result summary from stdout
            result_summary, artifact_paths = _collect_artifacts(
                exp["script_path"], result.stdout
            )

            # Log metrics and artifacts via tracker
            summary_data = _parse_summary(result.stdout)
            if summary_data and isinstance(summary_data.get("metrics"), dict):
                tracker.log_metrics(summary_data["metrics"])
            for ap in artifact_paths:
                tracker.log_artifact(ap)
            tracker.end_run(status="completed")

            update_experiment_results(
                node_id,
                result_summary=result_summary,
                llm_interpretation="",
                artifact_paths=artifact_paths if artifact_paths else None,
            )
            update_queue_item(queue_id, "done", run_output=output, completed_at=_now())
            update_node_status(node_id, "completed")
            return {"status": "done", "queue_id": queue_id, "node_id": node_id, "output": output}
        else:
            tracker.end_run(status="failed")
            update_queue_item(queue_id, "failed", run_output=output, completed_at=_now())
            update_node_status(node_id, "pending")
            return {"status": "failed", "queue_id": queue_id, "node_id": node_id, "output": output}

    except subprocess.TimeoutExpired:
        tracker.end_run(status="failed")
        msg = "Script timed out after 600 seconds."
        update_queue_item(queue_id, "failed", run_output=msg, completed_at=_now())
        update_node_status(node_id, "pending")
        return {"status": "failed", "queue_id": queue_id, "node_id": node_id, "output": msg}


def _collect_artifacts(script_path: str, stdout: str) -> tuple[str, list[str]]:
    """
    Parse stdout JSON for result_summary.
    Scan artifacts/{script_stem}/ for PNG, CSV, JSON, HTML files.
    Returns (result_summary, [relative artifact paths]).
    """
    # Parse summary from stdout
    result_summary = ""
    for line in reversed(stdout.splitlines()):
        line = line.strip()
        if line.startswith("{"):
            try:
                data = _json.loads(line)
                result_summary = data.get("summary") or data.get("result") or ""
                if not result_summary:
                    # Use first string value found
                    for v in data.values():
                        if isinstance(v, str) and len(v) > 10:
                            result_summary = v
                            break
                break
            except _json.JSONDecodeError:
                pass

    # Scan artifact directory
    artifact_paths: list[str] = []
    script_stem = Path(script_path).stem
    artifact_dir = ROOT / "artifacts" / script_stem
    if artifact_dir.exists():
        for ext in (".png", ".jpg", ".jpeg", ".svg", ".csv", ".json", ".html"):
            for fp in sorted(artifact_dir.glob(f"*{ext}")):
                artifact_paths.append(str(fp.relative_to(ROOT)))

    return result_summary, artifact_paths


def run_llm_post_process(node_id: str, raw_output: str, taxonomy_summary: str = "") -> None:
    """
    After a script completes, call Ollama to summarise and Claude to interpret,
    then generate branch questions.
    """
    from pipeline.llm import summarize_result, interpret_result, generate_branches

    summary = summarize_result(raw_output)
    interpretation = interpret_result(summary, experiment_context=taxonomy_summary)

    update_experiment_results(node_id, result_summary=summary, llm_interpretation=interpretation)

    branches = generate_branches(summary, current_taxonomy=taxonomy_summary)
    for branch_q in branches:
        child_id = add_node(
            type="question",
            title=branch_q,
            content="Auto-generated from experiment result.",
            status="pending",
        )
        add_edge(node_id, child_id, "branched_into")


def _parse_summary(stdout: str) -> dict | None:
    """
    Extract JSON summary dict from stdout.
    Scans lines in reverse, finds the first line starting with '{',
    attempts json.loads, and returns the dict or None.
    """
    for line in reversed(stdout.strip().splitlines()):
        line = line.strip()
        if line.startswith("{"):
            try:
                return _json.loads(line)
            except _json.JSONDecodeError:
                continue
    return None


def _execute_script(node_id: str) -> dict:
    """
    Run a single experiment script via ``uv run``.

    Resolves the script path from the DB, executes with a configurable timeout,
    captures stdout/stderr, parses the JSON summary, and integrates with the
    tracking protocol (start_run / log_metrics / log_artifact / end_run).

    Returns a dict with keys: status ("done" | "failed"), output, and optionally summary.
    """
    from pipeline.graph import get_experiment, get_setting
    from pipeline.tracking import get_tracker

    exp = get_experiment(node_id)
    if not exp or not exp.get("script_path"):
        return {"status": "failed", "output": f"No script path for node {node_id}"}

    script_path = ROOT / exp["script_path"]
    if not script_path.exists():
        return {"status": "failed", "output": f"Script not found: {script_path}"}

    timeout = int(get_setting("script_timeout", "600"))

    tracker = get_tracker()
    params = _json.loads(exp.get("parameters_json") or "{}")
    tracker.start_run(node_id, params)

    try:
        result = subprocess.run(
            ["uv", "run", str(script_path)],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        tracker.end_run(status="failed")
        return {"status": "failed", "output": f"Script timed out after {timeout}s"}

    combined = result.stdout + ("\n--- STDERR ---\n" + result.stderr if result.stderr else "")

    if result.returncode != 0:
        tracker.end_run(status="failed")
        return {"status": "failed", "output": combined}

    # Parse JSON summary and log via tracker
    summary = _parse_summary(result.stdout)
    if summary:
        if isinstance(summary.get("metrics"), dict):
            tracker.log_metrics(summary["metrics"])
        for artifact in summary.get("artifacts", []):
            tracker.log_artifact(str(artifact))

    tracker.end_run(status="completed")
    return {"status": "done", "output": combined, "summary": summary}


def _ai_fix_script(node_id: str, error_output: str) -> bool:
    """
    Send the failing script + error output to Claude for an AI-assisted fix.

    Reads the script file, calls the LLM with a fix prompt, cleans the response
    with ``_clean_script``, and overwrites the script file.

    Returns True if a fix was applied, False if the AI couldn't produce one.
    """
    from pipeline.graph import get_experiment, get_setting
    from pipeline.llm import call_model
    from pipeline.scriptgen import _clean_script

    exp = get_experiment(node_id)
    if not exp or not exp.get("script_path"):
        return False

    script_path = ROOT / exp["script_path"]
    if not script_path.exists():
        return False

    script_content = script_path.read_text()
    model = get_setting("autopilot_script_model", "claude-sonnet-4-6")

    prompt = (
        "This experiment script failed. Fix it.\n\n"
        f"Script:\n```python\n{script_content}\n```\n\n"
        f"Error output:\n```\n{error_output}\n```\n\n"
        "Return ONLY the fixed Python script, no explanation."
    )

    try:
        fixed = call_model(
            model,
            [{"role": "user", "content": prompt}],
            max_tokens=8192,
        )
        fixed = _clean_script(fixed)
        if fixed and len(fixed) > 50:  # sanity check
            script_path.write_text(fixed)
            return True
    except Exception:
        pass
    return False


def run_with_retry(node_id: str, max_retries: int | None = None) -> dict:
    """
    Execute an experiment script with AI-assisted auto-retry on failure.

    On each failure the script is sent to the LLM for a fix, then re-executed.
    After *max_retries + 1* total attempts (1 initial + max_retries retries)
    the final failure result is returned.

    ``max_retries`` defaults to the ``max_retries`` setting in the knowledge
    graph (itself defaulting to 3).
    """
    from pipeline.graph import get_setting

    if max_retries is None:
        max_retries = int(get_setting("max_retries", "3"))

    result: dict = {"status": "failed", "output": "No execution attempted"}

    for attempt in range(max_retries + 1):
        result = _execute_script(node_id)
        if result["status"] == "done":
            return result
        # Don't attempt AI fix after the last allowed attempt
        if attempt < max_retries:
            fixed = _ai_fix_script(node_id, result["output"])
            if not fixed:
                break  # AI couldn't produce a fix — stop retrying
    return result


if __name__ == "__main__":
    init_db()
    result = run_next()
    print(result)
