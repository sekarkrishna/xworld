"""Tests for pipeline/autopilot.py"""
from unittest.mock import patch, MagicMock

import pytest

from pipeline.autopilot import (
    AutopilotState,
    AutopilotStep,
    BatchResult,
    approve_candidate,
    commit_approved,
    reject_candidate,
    run_hypothesis_batch,
    step_generate_branches,
    step_interpret,
    step_summarise,
)


# ── AutopilotStep enum ────────────────────────────────────────────


class TestAutopilotStep:
    def test_all_steps_present(self):
        names = {s.name for s in AutopilotStep}
        assert names == {
            "SUMMARISE",
            "INTERPRET",
            "GENERATE_BRANCHES",
            "DESIGN_EXPERIMENT",
            "GENERATE_SCRIPT",
            "AWAITING_APPROVAL",
            "COMPLETE",
        }

    def test_step_values_are_human_readable(self):
        assert AutopilotStep.SUMMARISE.value == "summarising"
        assert AutopilotStep.AWAITING_APPROVAL.value == "awaiting approval"
        assert AutopilotStep.COMPLETE.value == "complete"


# ── AutopilotState dataclass ──────────────────────────────────────


class TestAutopilotState:
    def test_defaults(self):
        state = AutopilotState(
            experiment_node_id="exp-1",
            current_step=AutopilotStep.SUMMARISE,
        )
        assert state.summary == ""
        assert state.interpretation == ""
        assert state.candidates == []
        assert state.approved == []
        assert state.rejected == []

    def test_mutable_default_lists_are_independent(self):
        s1 = AutopilotState("a", AutopilotStep.SUMMARISE)
        s2 = AutopilotState("b", AutopilotStep.SUMMARISE)
        s1.candidates.append({"title": "x"})
        assert s2.candidates == []


# ── step_summarise ─────────────────────────────────────────────────


class TestStepSummarise:
    @patch("pipeline.llm.call_model")
    @patch("pipeline.graph.get_setting")
    @patch("pipeline.graph.get_experiment")
    def test_calls_llm_and_advances_step(self, mock_exp, mock_setting, mock_call):
        mock_exp.return_value = {"result_summary": "p-value 0.03, clusters found"}
        mock_setting.return_value = "qwen2.5:latest"
        mock_call.return_value = "Three clusters were found with significance."

        state = AutopilotState("exp-1", AutopilotStep.SUMMARISE)
        result = step_summarise(state)

        assert result.summary == "Three clusters were found with significance."
        assert result.current_step == AutopilotStep.INTERPRET
        mock_call.assert_called_once()
        assert mock_call.call_args[0][0] == "qwen2.5:latest"

    @patch("pipeline.llm.call_model")
    @patch("pipeline.graph.get_setting")
    @patch("pipeline.graph.get_experiment")
    def test_handles_missing_experiment(self, mock_exp, mock_setting, mock_call):
        mock_exp.return_value = None
        mock_setting.return_value = "qwen2.5:latest"
        mock_call.return_value = "No data available."

        state = AutopilotState("missing", AutopilotStep.SUMMARISE)
        result = step_summarise(state)

        assert result.current_step == AutopilotStep.INTERPRET
        # Should still call LLM with empty content
        prompt_content = mock_call.call_args[0][1][0]["content"]
        assert "Summarise" in prompt_content


# ── step_interpret ─────────────────────────────────────────────────


class TestStepInterpret:
    @patch("pipeline.llm.call_model")
    @patch("pipeline.llm._load_prompt")
    @patch("pipeline.graph.get_setting")
    @patch("pipeline.graph.get_node")
    @patch("pipeline.graph.get_parents")
    def test_builds_context_and_advances(
        self, mock_parents, mock_node, mock_setting, mock_prompt, mock_call
    ):
        mock_parents.return_value = [
            {"id": "hyp-1", "type": "hypothesis", "title": "H1", "content": "test hyp", "edge_type": "tests"},
        ]
        mock_node.return_value = {
            "id": "hyp-1",
            "type": "hypothesis",
            "title": "H1",
            "content": "test hyp",
        }
        mock_setting.return_value = "claude-sonnet-4-6"
        mock_prompt.return_value = "Interpret: {result_summary}\nContext: {context}"
        mock_call.return_value = "The result supports the hypothesis."

        state = AutopilotState("exp-1", AutopilotStep.INTERPRET, summary="3 clusters found")
        result = step_interpret(state)

        assert result.interpretation == "The result supports the hypothesis."
        assert result.current_step == AutopilotStep.GENERATE_BRANCHES
        mock_call.assert_called_once()
        prompt_used = mock_call.call_args[0][1][0]["content"]
        assert "3 clusters found" in prompt_used
        assert "H1" in prompt_used


# ── step_generate_branches ─────────────────────────────────────────


class TestStepGenerateBranches:
    @patch("pipeline.llm._parse_numbered_list")
    @patch("pipeline.llm.call_model")
    @patch("pipeline.llm._load_prompt")
    @patch("pipeline.graph.get_setting")
    def test_generates_candidates(self, mock_setting, mock_prompt, mock_call, mock_parse):
        mock_setting.return_value = "claude-sonnet-4-6"
        mock_prompt.return_value = "Generate: {result_summary} {taxonomy} {n}"
        mock_call.return_value = "1. Branch A\n2. Branch B"
        mock_parse.return_value = ["Branch A", "Branch B"]

        state = AutopilotState(
            "exp-1", AutopilotStep.GENERATE_BRANCHES,
            summary="summary", interpretation="interp",
        )
        result = step_generate_branches(state)

        assert len(result.candidates) == 2
        assert result.candidates[0]["title"] == "Branch A"
        assert result.candidates[0]["type"] == "question"
        assert result.candidates[1]["title"] == "Branch B"
        assert result.current_step == AutopilotStep.AWAITING_APPROVAL


# ── approve / reject / commit ──────────────────────────────────────


class TestApprovalGate:
    def _make_state_with_candidates(self):
        return AutopilotState(
            experiment_node_id="exp-1",
            current_step=AutopilotStep.AWAITING_APPROVAL,
            candidates=[
                {"type": "question", "title": "Q1", "content": "c1"},
                {"type": "question", "title": "Q2", "content": "c2"},
                {"type": "question", "title": "Q3", "content": "c3"},
            ],
        )

    def test_approve_moves_to_approved(self):
        state = self._make_state_with_candidates()
        approve_candidate(state, 0)
        assert len(state.candidates) == 2
        assert len(state.approved) == 1
        assert state.approved[0]["title"] == "Q1"

    def test_reject_moves_to_rejected_with_reason(self):
        state = self._make_state_with_candidates()
        reject_candidate(state, 1, "Not relevant")
        assert len(state.candidates) == 2
        assert len(state.rejected) == 1
        assert state.rejected[0]["title"] == "Q2"
        assert state.rejected[0]["rejection_reason"] == "Not relevant"

    def test_approve_out_of_range_is_noop(self):
        state = self._make_state_with_candidates()
        approve_candidate(state, 10)
        assert len(state.candidates) == 3
        assert len(state.approved) == 0

    def test_reject_out_of_range_is_noop(self):
        state = self._make_state_with_candidates()
        reject_candidate(state, -1, "bad")
        assert len(state.candidates) == 3
        assert len(state.rejected) == 0

    @patch("pipeline.graph.add_decision")
    @patch("pipeline.graph.add_edge")
    @patch("pipeline.graph.add_node")
    def test_commit_creates_nodes_and_edges(self, mock_add_node, mock_add_edge, mock_add_decision):
        mock_add_node.side_effect = ["new-1", "new-2"]

        state = AutopilotState(
            experiment_node_id="exp-1",
            current_step=AutopilotStep.AWAITING_APPROVAL,
            approved=[
                {"type": "question", "title": "Q1", "content": "c1"},
                {"type": "hypothesis", "title": "H1", "content": "c2"},
            ],
            rejected=[
                {"type": "question", "title": "Q3", "rejection_reason": "Off-topic"},
            ],
        )

        new_ids = commit_approved(state)

        assert new_ids == ["new-1", "new-2"]
        assert mock_add_node.call_count == 2
        assert mock_add_edge.call_count == 2
        assert mock_add_decision.call_count == 1
        assert state.current_step == AutopilotStep.COMPLETE

        # Verify add_node calls
        first_call = mock_add_node.call_args_list[0]
        assert first_call.kwargs["type"] == "question"
        assert first_call.kwargs["title"] == "Q1"

        second_call = mock_add_node.call_args_list[1]
        assert second_call.kwargs["type"] == "hypothesis"
        assert second_call.kwargs["title"] == "H1"

    @patch("pipeline.graph.add_decision")
    @patch("pipeline.graph.add_edge")
    @patch("pipeline.graph.add_node")
    def test_commit_with_no_approved_or_rejected(self, mock_add_node, mock_add_edge, mock_add_decision):
        state = AutopilotState(
            experiment_node_id="exp-1",
            current_step=AutopilotStep.AWAITING_APPROVAL,
        )
        new_ids = commit_approved(state)
        assert new_ids == []
        assert mock_add_node.call_count == 0
        assert state.current_step == AutopilotStep.COMPLETE


# ── BatchResult ────────────────────────────────────────────────────


class TestBatchResult:
    def test_total_and_completed(self):
        results = [
            AutopilotState("e1", AutopilotStep.AWAITING_APPROVAL),
            AutopilotState("e2", AutopilotStep.AWAITING_APPROVAL),
            AutopilotState("e3", AutopilotStep.INTERPRET),  # not yet at approval
        ]
        batch = BatchResult(experiment_results=results)
        assert batch.total == 3
        assert batch.completed == 2

    def test_empty_batch(self):
        batch = BatchResult(experiment_results=[])
        assert batch.total == 0
        assert batch.completed == 0


# ── run_hypothesis_batch ───────────────────────────────────────────


class TestRunHypothesisBatch:
    @patch("pipeline.autopilot.step_generate_branches")
    @patch("pipeline.autopilot.step_interpret")
    @patch("pipeline.autopilot.step_summarise")
    @patch("pipeline.runner.run_with_retry")
    @patch("pipeline.graph.get_children_of_type")
    def test_runs_pending_experiments(
        self, mock_children, mock_run, mock_summ, mock_interp, mock_branch
    ):
        mock_children.return_value = [
            {"id": "e1", "status": "pending", "type": "experiment"},
            {"id": "e2", "status": "completed", "type": "experiment"},
            {"id": "e3", "status": "pending", "type": "experiment"},
        ]
        mock_run.side_effect = [
            {"status": "done"},
            {"status": "failed", "output": "error"},
        ]

        # step functions just return the state they receive
        mock_summ.side_effect = lambda s: s
        mock_interp.side_effect = lambda s: s
        mock_branch.side_effect = lambda s: s

        result = run_hypothesis_batch("hyp-1")

        # Only pending experiments are run (e1, e3)
        assert mock_run.call_count == 2
        # Only successful ones get autopilot (e1 succeeded, e3 failed)
        assert result.total == 1
        assert mock_summ.call_count == 1
        assert mock_interp.call_count == 1
        assert mock_branch.call_count == 1

    @patch("pipeline.runner.run_with_retry")
    @patch("pipeline.graph.get_children_of_type")
    def test_no_pending_experiments(self, mock_children, mock_run):
        mock_children.return_value = [
            {"id": "e1", "status": "completed", "type": "experiment"},
        ]

        result = run_hypothesis_batch("hyp-1")

        assert mock_run.call_count == 0
        assert result.total == 0
