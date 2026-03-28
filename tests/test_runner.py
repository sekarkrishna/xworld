"""Tests for pipeline/runner.py — enhanced runner with auto-retry."""
import json
import sqlite3
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from pipeline.runner import (
    _ai_fix_script,
    _execute_script,
    _parse_summary,
    run_with_retry,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def init_db(tmp_path, monkeypatch):
    """Create a temporary xworld.db with the required tables and seed data."""
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
    conn.execute(
        "INSERT INTO nodes VALUES ('n1','experiment','Test','','pending','','2025-01-01','2025-01-01')"
    )

    # Create a real script file for tests
    script_dir = tmp_path / "scripts"
    script_dir.mkdir()
    script_file = script_dir / "exp_n1abcdef.py"
    script_file.write_text('print("hello")\n')

    script_rel = f"scripts/exp_n1abcdef.py"
    conn.execute(
        "INSERT INTO experiments VALUES ('e1','n1','ds',?,'{}','[]','','','2025-01-01')",
        (script_rel,),
    )
    conn.commit()
    conn.close()

    # Patch DB_PATH and ROOT
    monkeypatch.setattr("pipeline.graph.DB_PATH", db_path)
    monkeypatch.setattr("pipeline.runner.ROOT", tmp_path)
    return tmp_path


# ---------------------------------------------------------------------------
# _parse_summary
# ---------------------------------------------------------------------------


class TestParseSummary:
    def test_valid_json_last_line(self):
        stdout = 'Processing...\nDone.\n{"summary": "All good", "metrics": {"acc": 0.95}}\n'
        result = _parse_summary(stdout)
        assert result == {"summary": "All good", "metrics": {"acc": 0.95}}

    def test_json_not_last_line(self):
        stdout = 'Line 1\n{"summary": "result"}\nSome trailing text\n'
        # Should still find the JSON line scanning in reverse
        result = _parse_summary(stdout)
        assert result == {"summary": "result"}

    def test_no_json(self):
        stdout = "Just plain text\nNo JSON here\n"
        result = _parse_summary(stdout)
        assert result is None

    def test_empty_stdout(self):
        assert _parse_summary("") is None

    def test_invalid_json_skipped(self):
        stdout = '{invalid json}\n{"valid": true}\n'
        result = _parse_summary(stdout)
        assert result == {"valid": True}

    def test_multiple_json_lines_returns_last(self):
        stdout = '{"first": 1}\n{"second": 2}\n'
        result = _parse_summary(stdout)
        assert result == {"second": 2}


# ---------------------------------------------------------------------------
# _execute_script
# ---------------------------------------------------------------------------


class TestExecuteScript:
    def test_missing_experiment(self, init_db):
        result = _execute_script("nonexistent")
        assert result["status"] == "failed"
        assert "No script path" in result["output"]

    def test_missing_script_file(self, init_db, tmp_path):
        # Point experiment to a non-existent script
        db_path = tmp_path / "xworld.db"
        conn = sqlite3.connect(db_path)
        conn.execute(
            "UPDATE experiments SET script_path = 'scripts/missing.py' WHERE node_id = 'n1'"
        )
        conn.commit()
        conn.close()

        result = _execute_script("n1")
        assert result["status"] == "failed"
        assert "not found" in result["output"]

    def test_successful_execution(self, init_db, tmp_path):
        # Write a script that outputs valid JSON summary
        script = tmp_path / "scripts" / "exp_n1abcdef.py"
        script.write_text(
            'import json\nprint(json.dumps({"summary": "ok", "metrics": {"x": 1.0}, "artifacts": []}))\n'
        )

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = '{"summary": "ok", "metrics": {"x": 1.0}, "artifacts": []}\n'
        mock_result.stderr = ""

        with patch("pipeline.runner.subprocess.run", return_value=mock_result):
            result = _execute_script("n1")

        assert result["status"] == "done"
        assert result["summary"] == {"summary": "ok", "metrics": {"x": 1.0}, "artifacts": []}

    def test_failed_execution(self, init_db, tmp_path):
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "NameError: name 'foo' is not defined"

        with patch("pipeline.runner.subprocess.run", return_value=mock_result):
            result = _execute_script("n1")

        assert result["status"] == "failed"
        assert "NameError" in result["output"]

    def test_timeout(self, init_db, tmp_path):
        with patch(
            "pipeline.runner.subprocess.run",
            side_effect=subprocess.TimeoutExpired(cmd="uv run", timeout=600),
        ):
            result = _execute_script("n1")

        assert result["status"] == "failed"
        assert "timed out" in result["output"]


# ---------------------------------------------------------------------------
# _ai_fix_script
# ---------------------------------------------------------------------------


class TestAiFixScript:
    def test_no_experiment(self, init_db):
        assert _ai_fix_script("nonexistent", "error") is False

    def test_no_script_file(self, init_db, tmp_path):
        db_path = tmp_path / "xworld.db"
        conn = sqlite3.connect(db_path)
        conn.execute(
            "UPDATE experiments SET script_path = 'scripts/missing.py' WHERE node_id = 'n1'"
        )
        conn.commit()
        conn.close()

        assert _ai_fix_script("n1", "error") is False

    def test_successful_fix(self, init_db, tmp_path):
        script = tmp_path / "scripts" / "exp_n1abcdef.py"

        fixed_script = "# fixed script\n" + "x = 1\n" * 10  # > 50 chars

        with patch("pipeline.llm.call_model", return_value=fixed_script):
            result = _ai_fix_script("n1", "NameError: name 'foo' is not defined")

        assert result is True
        # _clean_script strips trailing whitespace, so compare stripped versions
        assert script.read_text().strip() == fixed_script.strip()

    def test_fix_too_short_rejected(self, init_db, tmp_path):
        with patch("pipeline.llm.call_model", return_value="x=1"):
            result = _ai_fix_script("n1", "error")

        assert result is False

    def test_llm_exception_returns_false(self, init_db, tmp_path):
        with patch("pipeline.llm.call_model", side_effect=RuntimeError("API down")):
            result = _ai_fix_script("n1", "error")

        assert result is False


# ---------------------------------------------------------------------------
# run_with_retry
# ---------------------------------------------------------------------------


class TestRunWithRetry:
    def test_success_on_first_attempt(self, init_db):
        with patch(
            "pipeline.runner._execute_script",
            return_value={"status": "done", "output": "ok", "summary": {}},
        ):
            result = run_with_retry("n1", max_retries=3)

        assert result["status"] == "done"

    def test_success_after_retry(self, init_db):
        call_count = {"n": 0}

        def mock_execute(node_id):
            call_count["n"] += 1
            if call_count["n"] < 3:
                return {"status": "failed", "output": "error"}
            return {"status": "done", "output": "ok", "summary": {}}

        with (
            patch("pipeline.runner._execute_script", side_effect=mock_execute),
            patch("pipeline.runner._ai_fix_script", return_value=True),
        ):
            result = run_with_retry("n1", max_retries=3)

        assert result["status"] == "done"
        assert call_count["n"] == 3

    def test_all_retries_exhausted(self, init_db):
        with (
            patch(
                "pipeline.runner._execute_script",
                return_value={"status": "failed", "output": "persistent error"},
            ),
            patch("pipeline.runner._ai_fix_script", return_value=True),
        ):
            result = run_with_retry("n1", max_retries=2)

        assert result["status"] == "failed"

    def test_stops_when_ai_cant_fix(self, init_db):
        execute_calls = {"n": 0}

        def mock_execute(node_id):
            execute_calls["n"] += 1
            return {"status": "failed", "output": "error"}

        with (
            patch("pipeline.runner._execute_script", side_effect=mock_execute),
            patch("pipeline.runner._ai_fix_script", return_value=False),
        ):
            result = run_with_retry("n1", max_retries=3)

        assert result["status"] == "failed"
        # Should stop after first failure + one failed AI fix attempt
        assert execute_calls["n"] == 1

    def test_uses_setting_for_default_retries(self, init_db, tmp_path):
        db_path = tmp_path / "xworld.db"
        conn = sqlite3.connect(db_path)
        conn.execute(
            "INSERT INTO settings VALUES ('max_retries', '1', '2025-01-01')"
        )
        conn.commit()
        conn.close()

        execute_calls = {"n": 0}

        def mock_execute(node_id):
            execute_calls["n"] += 1
            return {"status": "failed", "output": "error"}

        with (
            patch("pipeline.runner._execute_script", side_effect=mock_execute),
            patch("pipeline.runner._ai_fix_script", return_value=True),
        ):
            result = run_with_retry("n1")  # no max_retries — uses setting

        assert result["status"] == "failed"
        # max_retries=1 from setting → 2 total attempts
        assert execute_calls["n"] == 2
