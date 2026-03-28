"""Tests for pipeline/scriptgen.py"""
import json
import sqlite3
from pathlib import Path
from unittest.mock import patch

import pytest

from pipeline.scriptgen import (
    FIVE_PHASE_TEMPLATE,
    ROOT,
    _clean_script,
    generate_script,
    save_script,
)


# ── _clean_script tests ────────────────────────────────────────────


class TestCleanScript:
    def test_strips_python_fences(self):
        raw = "```python\nprint('hello')\n```"
        assert _clean_script(raw) == "print('hello')"

    def test_strips_plain_fences(self):
        raw = "```\nprint('hello')\n```"
        assert _clean_script(raw) == "print('hello')"

    def test_no_fences_unchanged(self):
        raw = "print('hello')\nprint('world')"
        assert _clean_script(raw) == raw

    def test_strips_surrounding_whitespace(self):
        raw = "\n\n```python\ncode\n```\n\n"
        assert _clean_script(raw) == "code"

    def test_empty_string(self):
        assert _clean_script("") == ""

    def test_only_fences(self):
        raw = "```python\n```"
        assert _clean_script(raw) == ""

    def test_multiline_script_preserved(self):
        raw = "```python\nimport json\nprint(json.dumps({}))\n```"
        result = _clean_script(raw)
        assert "import json" in result
        assert "print(json.dumps({}))" in result
        assert "```" not in result


# ── FIVE_PHASE_TEMPLATE tests ──────────────────────────────────────


class TestFivePhaseTemplate:
    def test_contains_pep723_header(self):
        assert "# /// script" in FIVE_PHASE_TEMPLATE

    def test_contains_all_five_phases(self):
        assert "Phase 1: Data Acquisition" in FIVE_PHASE_TEMPLATE
        assert "Phase 2: Feature Extraction" in FIVE_PHASE_TEMPLATE
        assert "Phase 3: Analysis" in FIVE_PHASE_TEMPLATE
        assert "Phase 4: Artifacts" in FIVE_PHASE_TEMPLATE
        assert "Phase 5: Summary" in FIVE_PHASE_TEMPLATE

    def test_contains_ensure_dataset_import(self):
        assert "from pipeline.datasets import ensure_dataset" in FIVE_PHASE_TEMPLATE

    def test_contains_extract_import(self):
        assert "from pipeline.extract import zscore, extract_features" in FIVE_PHASE_TEMPLATE

    def test_contains_artifact_dir_setup(self):
        assert "ARTIFACT_DIR" in FIVE_PHASE_TEMPLATE

    def test_contains_json_summary_keys(self):
        assert '"summary"' in FIVE_PHASE_TEMPLATE
        assert '"metrics"' in FIVE_PHASE_TEMPLATE
        assert '"artifacts"' in FIVE_PHASE_TEMPLATE
        assert '"verdict_suggestion"' in FIVE_PHASE_TEMPLATE
        assert '"datasets_used"' in FIVE_PHASE_TEMPLATE
        assert '"parameters_used"' in FIVE_PHASE_TEMPLATE

    def test_has_format_placeholders(self):
        assert "{dep_lines}" in FIVE_PHASE_TEMPLATE
        assert "{title}" in FIVE_PHASE_TEMPLATE
        assert "{data_acquisition}" in FIVE_PHASE_TEMPLATE
        assert "{feature_extraction}" in FIVE_PHASE_TEMPLATE
        assert "{analysis}" in FIVE_PHASE_TEMPLATE
        assert "{artifacts}" in FIVE_PHASE_TEMPLATE


# ── ROOT tests ─────────────────────────────────────────────────────


class TestRoot:
    def test_root_is_xworld_dir(self):
        # ROOT should be the xworld project root (parent of pipeline/)
        assert ROOT.name == "xworld"
        assert (ROOT / "pipeline").is_dir()


# ── generate_script tests ─────────────────────────────────────────


class TestGenerateScript:
    @patch("pipeline.llm.call_model")
    @patch("pipeline.graph.get_setting")
    def test_calls_llm_with_correct_model(self, mock_setting, mock_call):
        mock_setting.return_value = "claude-sonnet-4-6"
        mock_call.return_value = "print('hello')"

        generate_script("abc-123", ["ecg_fivedays"], "clustering", {"k": 5})

        mock_setting.assert_called_once_with(
            "autopilot_script_model", "claude-sonnet-4-6"
        )
        mock_call.assert_called_once()
        model_arg = mock_call.call_args[0][0]
        assert model_arg == "claude-sonnet-4-6"

    @patch("pipeline.llm.call_model")
    @patch("pipeline.graph.get_setting")
    def test_prompt_includes_datasets(self, mock_setting, mock_call):
        mock_setting.return_value = "claude-sonnet-4-6"
        mock_call.return_value = "print('hello')"

        generate_script("abc-123", ["ecg_fivedays", "covid_first_wave"], "compare", {})

        prompt = mock_call.call_args[0][1][0]["content"]
        assert "ecg_fivedays" in prompt
        assert "covid_first_wave" in prompt

    @patch("pipeline.llm.call_model")
    @patch("pipeline.graph.get_setting")
    def test_prompt_includes_methodology(self, mock_setting, mock_call):
        mock_setting.return_value = "claude-sonnet-4-6"
        mock_call.return_value = "print('hello')"

        generate_script("abc-123", [], "kurtosis comparison", {})

        prompt = mock_call.call_args[0][1][0]["content"]
        assert "kurtosis comparison" in prompt

    @patch("pipeline.llm.call_model")
    @patch("pipeline.graph.get_setting")
    def test_prompt_includes_parameters(self, mock_setting, mock_call):
        mock_setting.return_value = "claude-sonnet-4-6"
        mock_call.return_value = "print('hello')"

        generate_script("abc-123", [], "test", {"min_cluster_size": 8})

        prompt = mock_call.call_args[0][1][0]["content"]
        assert "min_cluster_size" in prompt

    @patch("pipeline.llm.call_model")
    @patch("pipeline.graph.get_setting")
    def test_cleans_markdown_fences_from_output(self, mock_setting, mock_call):
        mock_setting.return_value = "claude-sonnet-4-6"
        mock_call.return_value = "```python\nprint('hello')\n```"

        result = generate_script("abc-123", [], "test", {})
        assert result == "print('hello')"


# ── save_script tests ─────────────────────────────────────────────


class TestSaveScript:
    def test_saves_to_correct_path(self, tmp_path, monkeypatch):
        """save_script writes the file and returns the relative path."""
        monkeypatch.setattr("pipeline.scriptgen.ROOT", tmp_path)

        # Create a minimal in-memory DB
        db = sqlite3.connect(":memory:")
        db.execute(
            "CREATE TABLE experiments (id TEXT, node_id TEXT, script_path TEXT)"
        )
        db.execute(
            "INSERT INTO experiments (id, node_id) VALUES ('e1', 'abcd1234-5678')"
        )
        db.commit()

        class FakeConn:
            def __enter__(self):
                return db
            def __exit__(self, *args):
                db.commit()
                return False

        with patch("pipeline.graph._conn", return_value=FakeConn()):
            path = save_script("abcd1234-5678", "print('test')")

        assert path == "scripts/exp_abcd1234.py"
        full = tmp_path / "scripts" / "exp_abcd1234.py"
        assert full.exists()
        assert full.read_text() == "print('test')"

    def test_creates_scripts_directory(self, tmp_path, monkeypatch):
        """save_script creates the scripts/ directory if it doesn't exist."""
        monkeypatch.setattr("pipeline.scriptgen.ROOT", tmp_path)

        db = sqlite3.connect(":memory:")
        db.execute(
            "CREATE TABLE experiments (id TEXT, node_id TEXT, script_path TEXT)"
        )
        db.commit()

        class FakeConn:
            def __enter__(self):
                return db
            def __exit__(self, *args):
                db.commit()
                return False

        with patch("pipeline.graph._conn", return_value=FakeConn()):
            save_script("xyz98765-abcd", "# test")

        assert (tmp_path / "scripts").is_dir()

    def test_deterministic_naming(self, tmp_path, monkeypatch):
        """Calling save_script twice with the same ID produces the same path."""
        monkeypatch.setattr("pipeline.scriptgen.ROOT", tmp_path)

        db = sqlite3.connect(":memory:")
        db.execute(
            "CREATE TABLE experiments (id TEXT, node_id TEXT, script_path TEXT)"
        )
        db.commit()

        class FakeConn:
            def __enter__(self):
                return db
            def __exit__(self, *args):
                db.commit()
                return False

        with patch("pipeline.graph._conn", return_value=FakeConn()):
            path1 = save_script("abcd1234-5678", "v1")
            path2 = save_script("abcd1234-5678", "v2")

        assert path1 == path2
        # Second write overwrites
        assert (tmp_path / "scripts" / "exp_abcd1234.py").read_text() == "v2"

    def test_updates_db_record(self, tmp_path, monkeypatch):
        """save_script updates the experiments table with the script path."""
        monkeypatch.setattr("pipeline.scriptgen.ROOT", tmp_path)

        db = sqlite3.connect(":memory:")
        db.execute(
            "CREATE TABLE experiments (id TEXT, node_id TEXT, script_path TEXT)"
        )
        db.execute(
            "INSERT INTO experiments (id, node_id) VALUES ('e1', 'abcd1234-5678')"
        )
        db.commit()

        class FakeConn:
            def __enter__(self):
                return db
            def __exit__(self, *args):
                db.commit()
                return False

        with patch("pipeline.graph._conn", return_value=FakeConn()):
            save_script("abcd1234-5678", "print('test')")

        row = db.execute(
            "SELECT script_path FROM experiments WHERE node_id = 'abcd1234-5678'"
        ).fetchone()
        assert row[0] == "scripts/exp_abcd1234.py"
