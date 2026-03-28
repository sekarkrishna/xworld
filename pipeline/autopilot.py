"""
pipeline/autopilot.py
Semi-autopilot orchestration loop for XWorld.

After an experiment completes, the autopilot runs a step-by-step pipeline:
  1. Summarise   — LLM summarises the raw result
  2. Interpret   — LLM interprets in context of parent hypothesis / question
  3. Generate    — LLM proposes candidate sub-questions and hypotheses
  4. Approval    — researcher approves / rejects candidates
  5. Commit      — approved items become nodes in the knowledge graph

BatchResult / run_hypothesis_batch provide a convenience wrapper that
executes all pending experiments under a hypothesis and collects autopilot
suggestions for batch approval.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


# ---------------------------------------------------------------------------
# Enum & state
# ---------------------------------------------------------------------------

class AutopilotStep(Enum):
    SUMMARISE = "summarising"
    INTERPRET = "interpreting"
    GENERATE_BRANCHES = "generating branches"
    DESIGN_EXPERIMENT = "designing experiment"
    GENERATE_SCRIPT = "generating script"
    AWAITING_APPROVAL = "awaiting approval"
    COMPLETE = "complete"


@dataclass
class AutopilotState:
    experiment_node_id: str
    current_step: AutopilotStep
    summary: str = ""
    interpretation: str = ""
    candidates: list[dict] = field(default_factory=list)
    approved: list[dict] = field(default_factory=list)
    rejected: list[dict] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Step functions
# ---------------------------------------------------------------------------

def step_summarise(state: AutopilotState) -> AutopilotState:
    """Step 1: Summarise the experiment result using a local LLM."""
    from pipeline.graph import get_experiment, get_setting
    from pipeline.llm import call_model

    exp = get_experiment(state.experiment_node_id)
    raw_output = exp.get("result_summary", "") if exp else ""
    model = get_setting("autopilot_summarise_model", "qwen2.5:latest")

    summary = call_model(
        model,
        [{"role": "user", "content": f"Summarise this experiment result:\n\n{raw_output}"}],
    )
    state.summary = summary
    state.current_step = AutopilotStep.INTERPRET
    return state


def step_interpret(state: AutopilotState) -> AutopilotState:
    """Step 2: Interpret the summary in context of parent hypothesis and question."""
    from pipeline.graph import get_node, get_parents, get_setting
    from pipeline.llm import call_model, _load_prompt

    parents = get_parents(state.experiment_node_id)
    context_parts: list[str] = []
    for p in parents:
        node = get_node(p["id"])
        if node:
            context_parts.append(
                f"{node['type']}: {node['title']}\n{node.get('content', '')}"
            )

    model = get_setting("autopilot_interpret_model", "claude-sonnet-4-6")
    prompt = _load_prompt("interpret_result").format(
        result_summary=state.summary,
        context="\n\n".join(context_parts),
    )

    state.interpretation = call_model(model, [{"role": "user", "content": prompt}])
    state.current_step = AutopilotStep.GENERATE_BRANCHES
    return state


def step_generate_branches(state: AutopilotState) -> AutopilotState:
    """Step 3: Generate candidate sub-questions and hypotheses."""
    from pipeline.graph import get_setting
    from pipeline.llm import call_model, _load_prompt, _parse_numbered_list

    model = get_setting("autopilot_branch_model", "claude-sonnet-4-6")
    prompt = _load_prompt("generate_branches").format(
        result_summary=state.summary,
        taxonomy=state.interpretation,
        n=4,
    )

    response = call_model(model, [{"role": "user", "content": prompt}])
    branches = _parse_numbered_list(response)

    state.candidates = [
        {
            "type": "question",
            "title": b,
            "content": f"Generated from: {state.experiment_node_id}",
        }
        for b in branches
    ]
    state.current_step = AutopilotStep.AWAITING_APPROVAL
    return state


# ---------------------------------------------------------------------------
# Approval gate
# ---------------------------------------------------------------------------

def approve_candidate(state: AutopilotState, index: int) -> None:
    """Move a candidate from pending to approved."""
    if 0 <= index < len(state.candidates):
        state.approved.append(state.candidates.pop(index))


def reject_candidate(state: AutopilotState, index: int, reason: str) -> None:
    """Move a candidate from pending to rejected with a reason."""
    if 0 <= index < len(state.candidates):
        item = state.candidates.pop(index)
        item["rejection_reason"] = reason
        state.rejected.append(item)


def commit_approved(state: AutopilotState) -> list[str]:
    """Write approved candidates to the knowledge graph. Returns new node IDs."""
    from pipeline.graph import add_node, add_edge, add_decision

    new_ids: list[str] = []
    for item in state.approved:
        node_id = add_node(
            type=item["type"],
            title=item["title"],
            content=item.get("content", ""),
            status="pending",
        )
        add_edge(state.experiment_node_id, node_id, "branched_into")
        new_ids.append(node_id)

    for item in state.rejected:
        add_decision(
            fork_node=state.experiment_node_id,
            chosen_branch="",
            reason=f"Rejected: {item['title']} — {item.get('rejection_reason', 'No reason given')}",
        )

    state.current_step = AutopilotStep.COMPLETE
    return new_ids


# ---------------------------------------------------------------------------
# Batch execution
# ---------------------------------------------------------------------------

@dataclass
class BatchResult:
    """Result of running all pending experiments under a hypothesis."""

    experiment_results: list[AutopilotState]

    @property
    def total(self) -> int:
        return len(self.experiment_results)

    @property
    def completed(self) -> int:
        return sum(
            1
            for r in self.experiment_results
            if r.current_step == AutopilotStep.AWAITING_APPROVAL
        )


def run_hypothesis_batch(hypothesis_id: str) -> BatchResult:
    """
    Run all pending experiments under a hypothesis sequentially.

    For each successful experiment, runs the autopilot interpretation loop
    (summarise → interpret → generate branches) and collects suggestions
    for batch approval.
    """
    from pipeline.graph import get_children_of_type
    from pipeline.runner import run_with_retry

    experiments = get_children_of_type(hypothesis_id, "experiment")
    pending = [e for e in experiments if e["status"] == "pending"]
    results: list[AutopilotState] = []

    for exp in pending:
        result = run_with_retry(exp["id"])
        if result["status"] == "done":
            state = AutopilotState(
                experiment_node_id=exp["id"],
                current_step=AutopilotStep.SUMMARISE,
            )
            state = step_summarise(state)
            state = step_interpret(state)
            state = step_generate_branches(state)
            results.append(state)

    return BatchResult(experiment_results=results)
