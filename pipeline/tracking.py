"""
pipeline/tracking.py
Experiment tracking protocol and implementations.

Provides a pluggable tracking interface that writes experiment parameters,
metrics, and artifacts to the SQLite knowledge graph, with optional MLflow
dual-write when enabled.
"""
from __future__ import annotations

import json
import logging
from typing import Protocol, runtime_checkable

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Protocol
# ---------------------------------------------------------------------------


@runtime_checkable
class ExperimentTracker(Protocol):
    """Abstract tracking interface for experiment runs."""

    def start_run(self, experiment_id: str, params: dict) -> None: ...

    def log_params(self, params: dict) -> None: ...

    def log_metrics(self, metrics: dict[str, float]) -> None: ...

    def log_artifact(self, local_path: str, artifact_name: str | None = None) -> None: ...

    def end_run(self, status: str = "completed") -> None: ...


# ---------------------------------------------------------------------------
# SQLite implementation (default)
# ---------------------------------------------------------------------------


class SQLiteTracker:
    """Default tracker that writes to the existing experiments table."""

    def __init__(self) -> None:
        self._current_node_id: str | None = None
        self._params: dict = {}

    def start_run(self, experiment_id: str, params: dict) -> None:
        self._current_node_id = experiment_id
        self._params = dict(params)
        from pipeline.graph import _conn

        with _conn() as conn:
            conn.execute(
                "UPDATE experiments SET parameters_json = ? WHERE node_id = ?",
                (json.dumps(self._params), experiment_id),
            )

    def log_params(self, params: dict) -> None:
        self._params.update(params)

    def log_metrics(self, metrics: dict[str, float]) -> None:
        from pipeline.graph import update_experiment_results

        update_experiment_results(
            self._current_node_id,
            result_summary=json.dumps(metrics),
            llm_interpretation="",
        )

    def log_artifact(self, local_path: str, artifact_name: str | None = None) -> None:
        from pipeline.graph import get_experiment, _conn

        exp = get_experiment(self._current_node_id)
        paths: list[str] = json.loads(exp.get("artifact_paths") or "[]") if exp else []
        paths.append(local_path)
        with _conn() as conn:
            conn.execute(
                "UPDATE experiments SET artifact_paths = ? WHERE node_id = ?",
                (json.dumps(paths), self._current_node_id),
            )

    def end_run(self, status: str = "completed") -> None:
        from pipeline.graph import update_node_status

        update_node_status(self._current_node_id, status)


# ---------------------------------------------------------------------------
# MLflow implementation (optional dual-write)
# ---------------------------------------------------------------------------


class MLflowTracker:
    """Optional MLflow tracker — wraps mlflow API, always delegates to SQLiteTracker for dual-write."""

    def __init__(self, sqlite_tracker: SQLiteTracker) -> None:
        self._sqlite = sqlite_tracker
        import mlflow

        self._mlflow = mlflow

    def start_run(self, experiment_id: str, params: dict) -> None:
        self._sqlite.start_run(experiment_id, params)
        self._mlflow.start_run(run_name=experiment_id)
        self._mlflow.log_params(params)

    def log_params(self, params: dict) -> None:
        self._sqlite.log_params(params)
        self._mlflow.log_params(params)

    def log_metrics(self, metrics: dict[str, float]) -> None:
        self._sqlite.log_metrics(metrics)
        self._mlflow.log_metrics(metrics)

    def log_artifact(self, local_path: str, artifact_name: str | None = None) -> None:
        self._sqlite.log_artifact(local_path, artifact_name)
        self._mlflow.log_artifact(local_path)

    def end_run(self, status: str = "completed") -> None:
        self._sqlite.end_run(status)
        mlflow_status = "FINISHED" if status == "completed" else "FAILED"
        self._mlflow.end_run(status=mlflow_status)


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def get_tracker() -> ExperimentTracker:
    """Return MLflowTracker if enabled and installed, else SQLiteTracker."""
    from pipeline.graph import get_setting

    sqlite_tracker = SQLiteTracker()

    if get_setting("mlflow_enabled", "false").lower() == "true":
        try:
            import mlflow  # noqa: F401

            return MLflowTracker(sqlite_tracker)
        except ImportError:
            logger.warning(
                "mlflow_enabled=true but mlflow is not installed. "
                "Falling back to SQLite-only tracking."
            )

    return sqlite_tracker
