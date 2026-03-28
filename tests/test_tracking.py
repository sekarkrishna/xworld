"""Tests for pipeline/tracking.py — ExperimentTracker protocol and implementations."""
import json
import sqlite3
from unittest.mock import MagicMock, patch

import pytest

from pipeline.tracking import (
    ExperimentTracker,
    MLflowTracker,
    SQLiteTracker,
    get_tracker,
)


# ---------------------------------------------------------------------------
# Protocol conformance
# ---------------------------------------------------------------------------


def test_sqlite_tracker_satisfies_protocol():
    assert isinstance(SQLiteTracker(), ExperimentTracker)


def test_mlflow_tracker_satisfies_protocol():
    mock_mlflow = MagicMock()
    with patch.dict("sys.modules", {"mlflow": mock_mlflow}):
        tracker = MLflowTracker(SQLiteTracker())
        assert isinstance(tracker, ExperimentTracker)


# ---------------------------------------------------------------------------
# SQLiteTracker
# ---------------------------------------------------------------------------


@pytest.fixture()
def _init_db(tmp_path, monkeypatch):
    """Create a temporary xworld.db with the experiments and nodes tables."""
    db_path = tmp_path / "xworld.db"
    conn = sqlite3.connect(db_path)
    conn.execute(
        """CREATE TABLE nodes (
            id TEXT PRIMARY KEY, type TEXT, title TEXT, content TEXT,
            status TEXT, verdict TEXT, created_at TEXT, updated_at TEXT
        )"""
    )
    conn.execute(
        """CREATE TABLE experiments (
            id TEXT PRIMARY KEY, node_id TEXT, dataset TEXT,
            script_path TEXT, parameters_json TEXT, artifact_paths TEXT,
            result_summary TEXT, llm_interpretation TEXT, created_at TEXT
        )"""
    )
    conn.execute(
        """CREATE TABLE settings (
            key TEXT PRIMARY KEY, value TEXT, updated_at TEXT
        )"""
    )
    # Seed a node and experiment
    conn.execute(
        "INSERT INTO nodes VALUES ('n1','experiment','Test Exp','',  'pending','',  '2025-01-01','2025-01-01')"
    )
    conn.execute(
        "INSERT INTO experiments VALUES ('e1','n1','ds','script.py','{}','[]','','','2025-01-01')"
    )
    conn.commit()
    conn.close()

    # Patch DB_PATH so pipeline.graph uses the temp DB
    monkeypatch.setattr("pipeline.graph.DB_PATH", db_path)
    return db_path


def _read_exp(db_path: str, node_id: str = "n1") -> dict:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM experiments WHERE node_id=?", (node_id,)).fetchone()
    conn.close()
    return dict(row) if row else {}


def _read_node(db_path: str, node_id: str = "n1") -> dict:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM nodes WHERE id=?", (node_id,)).fetchone()
    conn.close()
    return dict(row) if row else {}


def test_sqlite_start_run(_init_db):
    db_path = _init_db
    tracker = SQLiteTracker()
    tracker.start_run("n1", {"lr": 0.01, "epochs": 10})

    exp = _read_exp(db_path)
    params = json.loads(exp["parameters_json"])
    assert params == {"lr": 0.01, "epochs": 10}
    assert tracker._current_node_id == "n1"


def test_sqlite_log_params(_init_db):
    tracker = SQLiteTracker()
    tracker.start_run("n1", {"a": 1})
    tracker.log_params({"b": 2})
    assert tracker._params == {"a": 1, "b": 2}


def test_sqlite_log_metrics(_init_db):
    db_path = _init_db
    tracker = SQLiteTracker()
    tracker.start_run("n1", {})
    tracker.log_metrics({"accuracy": 0.95, "loss": 0.05})

    exp = _read_exp(db_path)
    metrics = json.loads(exp["result_summary"])
    assert metrics == {"accuracy": 0.95, "loss": 0.05}


def test_sqlite_log_artifact(_init_db):
    db_path = _init_db
    tracker = SQLiteTracker()
    tracker.start_run("n1", {})
    tracker.log_artifact("artifacts/plot.png")
    tracker.log_artifact("artifacts/data.csv", artifact_name="results")

    exp = _read_exp(db_path)
    paths = json.loads(exp["artifact_paths"])
    assert paths == ["artifacts/plot.png", "artifacts/data.csv"]


def test_sqlite_end_run(_init_db):
    db_path = _init_db
    tracker = SQLiteTracker()
    tracker.start_run("n1", {})
    tracker.end_run("completed")

    node = _read_node(db_path)
    assert node["status"] == "completed"


def test_sqlite_end_run_failed(_init_db):
    db_path = _init_db
    tracker = SQLiteTracker()
    tracker.start_run("n1", {})
    tracker.end_run("failed")

    node = _read_node(db_path)
    assert node["status"] == "failed"


# ---------------------------------------------------------------------------
# MLflowTracker
# ---------------------------------------------------------------------------


def test_mlflow_tracker_dual_write(_init_db):
    db_path = _init_db
    mock_mlflow = MagicMock()

    with patch.dict("sys.modules", {"mlflow": mock_mlflow}):
        sqlite = SQLiteTracker()
        tracker = MLflowTracker(sqlite)

        tracker.start_run("n1", {"lr": 0.01})
        mock_mlflow.start_run.assert_called_once_with(run_name="n1")
        mock_mlflow.log_params.assert_called_with({"lr": 0.01})
        # SQLite side
        exp = _read_exp(db_path)
        assert json.loads(exp["parameters_json"]) == {"lr": 0.01}

        tracker.log_params({"batch": 32})
        assert mock_mlflow.log_params.call_count == 2

        tracker.log_metrics({"acc": 0.9})
        mock_mlflow.log_metrics.assert_called_once_with({"acc": 0.9})

        tracker.log_artifact("out.png")
        mock_mlflow.log_artifact.assert_called_once_with("out.png")

        tracker.end_run("completed")
        mock_mlflow.end_run.assert_called_once_with(status="FINISHED")

        node = _read_node(db_path)
        assert node["status"] == "completed"


def test_mlflow_end_run_maps_failed_status(_init_db):
    mock_mlflow = MagicMock()
    with patch.dict("sys.modules", {"mlflow": mock_mlflow}):
        tracker = MLflowTracker(SQLiteTracker())
        tracker.start_run("n1", {})
        tracker.end_run("failed")
        mock_mlflow.end_run.assert_called_once_with(status="FAILED")


# ---------------------------------------------------------------------------
# get_tracker() factory
# ---------------------------------------------------------------------------


def test_get_tracker_returns_sqlite_by_default(_init_db):
    tracker = get_tracker()
    assert isinstance(tracker, SQLiteTracker)


def test_get_tracker_returns_mlflow_when_enabled(_init_db):
    db_path = _init_db
    # Set mlflow_enabled = true in settings
    conn = sqlite3.connect(str(db_path))
    conn.execute(
        "INSERT INTO settings VALUES ('mlflow_enabled', 'true', '2025-01-01')"
    )
    conn.commit()
    conn.close()

    mock_mlflow = MagicMock()
    with patch.dict("sys.modules", {"mlflow": mock_mlflow}):
        tracker = get_tracker()
        assert isinstance(tracker, MLflowTracker)


def test_get_tracker_falls_back_when_mlflow_not_installed(_init_db):
    db_path = _init_db
    conn = sqlite3.connect(str(db_path))
    conn.execute(
        "INSERT INTO settings VALUES ('mlflow_enabled', 'true', '2025-01-01')"
    )
    conn.commit()
    conn.close()

    # Simulate mlflow not installed
    with patch.dict("sys.modules", {"mlflow": None}):
        tracker = get_tracker()
        assert isinstance(tracker, SQLiteTracker)
