"""
XWorld Research Workbench — Streamlit UI
Three-layer drill-down: Questions → Hypotheses/Experiments → Experiment Detail
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Ensure project root is on sys.path so `pipeline` package is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from pipeline.graph import (
    init_db,
    get_node,
    get_nodes_by_type,
    get_children,
    get_children_of_type,
    get_parents,
    get_experiment,
    get_roots,
    build_tree,
    add_node,
    add_edge,
    add_experiment,
    update_verdict,
    update_node_status,
    enqueue,
    get_setting,
    set_setting,
    _conn,
)

ROOT = Path(__file__).resolve().parent.parent

# ── Constants ───────────────────────────────────────────────────────

VERDICT_COLOURS = {
    "open": "#9CA3AF",
    "supported": "#22C55E",
    "refuted": "#EF4444",
    "inconclusive": "#EAB308",
    "deferred": "#3B82F6",
}

VERDICT_OPTIONS = list(VERDICT_COLOURS.keys())

STATUS_ICONS = {
    "pending": "⏳",
    "running": "🔄",
    "completed": "✅",
    "failed": "❌",
}

NODE_ICONS = {
    "question": "❓",
    "hypothesis": "💡",
    "experiment": "🔬",
    "result": "📊",
    "insight": "✨",
}

TERMINAL_VERDICTS = {"supported", "refuted", "deferred"}

LAYER_MAP = {
    "question": "hypotheses",
    "hypothesis": "experiments",
    "experiment": "detail",
    "result": "detail",
    "insight": "detail",
}


# ═══════════════════════════════════════════════════════════════════
# Session State & Navigation Helpers
# ═══════════════════════════════════════════════════════════════════

def _init_session_state() -> None:
    """Initialise all session state keys with defaults."""
    st.session_state.setdefault("nav_stack", [])
    st.session_state.setdefault("selected_node", None)
    st.session_state.setdefault("autopilot_step", None)
    st.session_state.setdefault("autopilot_candidates", [])


def push_nav(node_id: str, layer: str, label: str) -> None:
    """Push a new layer onto the navigation stack and rerun."""
    st.session_state.nav_stack.append(
        {"node_id": node_id, "layer": layer, "label": label}
    )
    st.rerun()


def pop_to(index: int) -> None:
    """Truncate the navigation stack to *index + 1* items and rerun."""
    st.session_state.nav_stack = st.session_state.nav_stack[: index + 1]
    st.rerun()


def navigate_to_node(node_id: str) -> None:
    """Build the full parent chain for *node_id* and set the nav stack."""
    node = get_node(node_id)
    if not node:
        return
    chain = _build_parent_chain(node_id)
    st.session_state.nav_stack = [
        {
            "node_id": n["id"],
            "layer": LAYER_MAP.get(n["type"], "hypotheses"),
            "label": n["title"],
        }
        for n in chain
    ]
    st.rerun()


def _build_parent_chain(node_id: str) -> list[dict]:
    """Walk parents up to the root and return the chain (root-first)."""
    chain: list[dict] = []
    visited: set[str] = set()
    current_id = node_id
    while current_id and current_id not in visited:
        visited.add(current_id)
        node = get_node(current_id)
        if not node:
            break
        chain.append(node)
        parents = get_parents(current_id)
        current_id = parents[0]["id"] if parents else None
    chain.reverse()
    return chain


# ═══════════════════════════════════════════════════════════════════
# Shared UI Helpers
# ═══════════════════════════════════════════════════════════════════

def verdict_badge(verdict: str | None) -> str:
    """Return an HTML badge span for a verdict value."""
    v = verdict or "open"
    colour = VERDICT_COLOURS.get(v, "#9CA3AF")
    return (
        f'<span style="background:{colour};color:#fff;padding:2px 8px;'
        f'border-radius:10px;font-size:0.8em;">{v}</span>'
    )


def status_icon(status: str | None) -> str:
    """Return an emoji icon for an experiment status."""
    return STATUS_ICONS.get(status or "pending", "⏳")


def node_icon(node_type: str) -> str:
    """Return an emoji icon for a node type."""
    return NODE_ICONS.get(node_type, "📄")


def verdict_summary(hypotheses: list[dict]) -> str:
    """Build a human-readable verdict summary string."""
    counts: dict[str, int] = {}
    for h in hypotheses:
        v = h.get("verdict") or "open"
        counts[v] = counts.get(v, 0) + 1
    parts = [f"{count} {verdict}" for verdict, count in counts.items()]
    return " · ".join(parts) if parts else "no hypotheses"


def _is_image(path: str) -> bool:
    """Check if a file path looks like an image."""
    return Path(path).suffix.lower() in {".png", ".jpg", ".jpeg", ".svg", ".gif"}


# ═══════════════════════════════════════════════════════════════════
# Sidebar & Breadcrumb
# ═══════════════════════════════════════════════════════════════════

def render_node_explorer_page() -> None:
    """Render the graph viewer as a full-screen main pane page."""
    st.header("🗺️ Node Explorer")

    roots = get_roots()
    if not roots:
        st.info("No nodes in the knowledge graph yet. Create a question first.")
        return

    tree = build_tree(roots[0]["id"])
    tree_json = json.dumps(tree, default=str)

    html_path = Path(__file__).parent / "graph-viewer" / "dist" / "index.html"
    if not html_path.exists():
        st.warning("Graph viewer not built. Run: `cd ui/graph-viewer && npm install && npm run build`")
        return

    html_template = html_path.read_text()
    data_script = f'<script id="graph-data" type="application/json">{tree_json}</script>'
    html_content = html_template.replace("</head>", f"{data_script}\n</head>")

    st.components.v1.html(html_content, height=700, scrolling=False)


def render_sidebar() -> None:
    """Render the sidebar with navigation links."""
    with st.sidebar:
        st.title("🌍 XWorld")
        st.caption("Cross-domain shape clustering")
        st.divider()

        if st.button("❓ Questions", use_container_width=True):
            st.session_state.nav_stack = []
            st.rerun()

        if st.button("🗺️ Node Explorer", use_container_width=True):
            st.session_state.nav_stack = [
                {"node_id": "__graph__", "layer": "graph", "label": "Node Explorer"}
            ]
            st.rerun()

        if st.button("📋 Queue", use_container_width=True):
            st.session_state.nav_stack = [
                {"node_id": "__queue__", "layer": "queue", "label": "Queue"}
            ]
            st.rerun()

        if st.button("⚙️ Settings", use_container_width=True):
            st.session_state.nav_stack = [
                {"node_id": "__settings__", "layer": "settings", "label": "Settings"}
            ]
            st.rerun()


def render_breadcrumb() -> None:
    """Render a clickable breadcrumb trail from the nav stack."""
    stack = st.session_state.nav_stack
    if not stack:
        return

    cols = st.columns(len(stack) + 1)
    with cols[0]:
        if st.button("🏠 Home", key="bc_home"):
            st.session_state.nav_stack = []
            st.rerun()

    for i, entry in enumerate(stack):
        with cols[i + 1]:
            icon = node_icon(entry.get("layer", ""))
            label = entry["label"]
            if len(label) > 25:
                label = label[:22] + "…"
            if st.button(f"{icon} {label}", key=f"bc_{i}"):
                pop_to(i)


# ═══════════════════════════════════════════════════════════════════
# Layer 1 — Questions & Hypotheses
# ═══════════════════════════════════════════════════════════════════

def page_layer1() -> None:
    """Default view: central question + expandable sub-question branches."""
    st.header("❓ Research Questions")

    roots = get_roots()
    if not roots:
        st.info("No research questions yet. Create one below.")
        _form_create_root_question()
        return

    for root in roots:
        _render_question_branch(root, is_root=True)

    st.divider()
    _form_create_root_question()


def _render_question_branch(question: dict, is_root: bool = False) -> None:
    """Render a question with its hypotheses and sub-questions."""
    q_id = question["id"]
    title = question["title"]
    icon = "🌍" if is_root else "❓"

    hypotheses = get_children_of_type(q_id, "hypothesis")
    sub_questions = get_children_of_type(q_id, "question")

    # Auto-resolution check
    _check_auto_resolve(q_id, hypotheses)

    with st.expander(f"{icon} {title}", expanded=is_root):
        # Progress summary
        if hypotheses:
            summary = verdict_summary(hypotheses)
            st.caption(f"Hypotheses: {summary}")

        # Status
        if question.get("status") == "resolved":
            st.success("✅ Resolved")

        # Hypotheses list
        for h in hypotheses:
            _render_hypothesis_row(h)

        # Sub-questions (recursive)
        for sq in sub_questions:
            _render_question_branch(sq)

        # Action buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"➕ Sub-Question", key=f"add_sq_{q_id}"):
                push_nav(q_id, "hypotheses", title)
        with col2:
            if st.button(f"💡 Hypothesis", key=f"add_hyp_{q_id}"):
                push_nav(q_id, "hypotheses", title)


def page_layer1_question(question_id: str) -> None:
    """Focused view on a single question — its hypotheses and sub-questions."""
    question = get_node(question_id)
    if not question:
        st.error("Question not found.")
        return

    st.header(f"❓ {question['title']}")
    if question.get("content"):
        st.markdown(question["content"])

    hypotheses = get_children_of_type(question_id, "hypothesis")
    sub_questions = get_children_of_type(question_id, "question")

    # Auto-resolution check
    _check_auto_resolve(question_id, hypotheses)

    # Progress summary
    if hypotheses:
        summary = verdict_summary(hypotheses)
        st.info(f"📊 Progress: {summary}")

    if question.get("status") == "resolved":
        st.success("✅ This question is resolved — all hypotheses have terminal verdicts.")

    # Hypotheses
    st.subheader("💡 Hypotheses")
    if not hypotheses:
        st.caption("No hypotheses yet.")
    for h in hypotheses:
        _render_hypothesis_row(h)

    # Sub-questions
    if sub_questions:
        st.subheader("❓ Sub-Questions")
        for sq in sub_questions:
            col1, col2 = st.columns([5, 1])
            with col1:
                st.write(f"❓ {sq['title']}")
            with col2:
                if st.button("Open", key=f"open_sq_{sq['id']}"):
                    push_nav(sq["id"], "hypotheses", sq["title"])

    st.divider()

    # Create forms
    _form_create_sub_question(question_id)
    _form_create_hypothesis(question_id)

    # AI Chat panel
    st.divider()
    render_chat_panel(question_id, step_type="chat")


def _render_hypothesis_row(h: dict) -> None:
    """Render a single hypothesis row with verdict badge and click-to-drill."""
    v = h.get("verdict") or "open"
    colour = VERDICT_COLOURS.get(v, "#9CA3AF")
    col1, col2, col3 = st.columns([4, 1, 1])
    with col1:
        st.markdown(
            f"💡 {h['title']} "
            f'<span style="background:{colour};color:#fff;padding:2px 8px;'
            f'border-radius:10px;font-size:0.8em;">{v}</span>',
            unsafe_allow_html=True,
        )
    with col2:
        exps = get_children_of_type(h["id"], "experiment")
        st.caption(f"{len(exps)} exp{'s' if len(exps) != 1 else ''}")
    with col3:
        if st.button("→", key=f"drill_hyp_{h['id']}"):
            push_nav(h["id"], "experiments", h["title"])


def _check_auto_resolve(question_id: str, hypotheses: list[dict]) -> None:
    """If all hypotheses have terminal verdicts, mark the question resolved."""
    if not hypotheses:
        return
    all_terminal = all(
        (h.get("verdict") or "open") in TERMINAL_VERDICTS for h in hypotheses
    )
    question = get_node(question_id)
    if not question:
        return
    if all_terminal and question.get("status") != "resolved":
        update_node_status(question_id, "resolved")
    elif not all_terminal and question.get("status") == "resolved":
        update_node_status(question_id, "pending")


def _form_create_root_question() -> None:
    """Form to create a new root-level question."""
    with st.form("new_root_question", clear_on_submit=True):
        st.subheader("Create Root Question")
        title = st.text_input("Question title")
        content = st.text_area("Description (optional)")
        if st.form_submit_button("Create") and title.strip():
            add_node(type="question", title=title.strip(), content=content.strip())
            st.rerun()


def _form_create_sub_question(parent_id: str) -> None:
    """Form to create a sub-question under a parent question."""
    with st.form(f"new_sub_question_{parent_id}", clear_on_submit=True):
        st.subheader("➕ New Sub-Question")
        title = st.text_input("Sub-question title", key=f"sq_title_{parent_id}")
        content = st.text_area("Description", key=f"sq_content_{parent_id}")
        if st.form_submit_button("Create") and title.strip():
            nid = add_node(type="question", title=title.strip(), content=content.strip())
            add_edge(parent_id, nid, "has_sub_question")
            st.rerun()


def _form_create_hypothesis(parent_id: str) -> None:
    """Form to create a hypothesis under a question."""
    with st.form(f"new_hypothesis_{parent_id}", clear_on_submit=True):
        st.subheader("💡 New Hypothesis")
        title = st.text_input("Hypothesis statement", key=f"hyp_title_{parent_id}")
        content = st.text_area("Rationale", key=f"hyp_content_{parent_id}")
        if st.form_submit_button("Create") and title.strip():
            nid = add_node(
                type="hypothesis",
                title=title.strip(),
                content=content.strip(),
                status="pending",
            )
            add_edge(parent_id, nid, "has_hypothesis")
            update_verdict(nid, "open")
            st.rerun()


# ═══════════════════════════════════════════════════════════════════
# Layer 2 — Experiment Progression Under a Hypothesis
# ═══════════════════════════════════════════════════════════════════

def page_layer2(hypothesis_id: str) -> None:
    """Show experiments under a hypothesis with verdict controls."""
    hyp = get_node(hypothesis_id)
    if not hyp:
        st.error("Hypothesis not found.")
        return

    # Header with verdict
    v = hyp.get("verdict") or "open"
    st.markdown(
        f"## 💡 {hyp['title']} {verdict_badge(v)}",
        unsafe_allow_html=True,
    )
    if hyp.get("content"):
        st.markdown(hyp["content"])

    # Experiments listed chronologically
    experiments = get_children_of_type(hypothesis_id, "experiment")

    st.subheader(f"🔬 Experiments ({len(experiments)})")

    if not experiments:
        st.caption("No experiments yet. Add one below.")
    else:
        # Verdict suggestion logic
        _render_verdict_suggestion(hypothesis_id, experiments)

        for exp in experiments:
            _render_experiment_row(exp)

    st.divider()

    # Manual verdict override
    _render_verdict_override(hypothesis_id, v)

    # Run All Pending batch button (Task 15.3)
    _render_run_all_pending(hypothesis_id)

    st.divider()

    # Add experiment form
    _form_add_experiment(hypothesis_id)

    # AI Chat panel
    st.divider()
    render_chat_panel(hypothesis_id, step_type="chat")

    # Report generation (Task 16.6)
    v_current = get_node(hypothesis_id)
    if v_current and (v_current.get("verdict") or "open") in ("supported", "refuted"):
        st.divider()
        _render_report_buttons(hypothesis_id)


def _render_experiment_row(exp: dict) -> None:
    """Render a single experiment with status badge and result summary."""
    exp_data = get_experiment(exp["id"])
    status = exp.get("status") or "pending"
    icon = status_icon(status)

    with st.container(border=True):
        col1, col2, col3 = st.columns([4, 1, 1])
        with col1:
            st.markdown(f"{icon} **{exp['title']}**")
        with col2:
            st.caption(status)
        with col3:
            if st.button("Details →", key=f"detail_{exp['id']}"):
                push_nav(exp["id"], "detail", exp["title"])

        # Result summary for completed experiments
        if status == "completed" and exp_data:
            summary = exp_data.get("result_summary", "")
            if summary:
                st.caption(f"📝 {summary[:200]}")

            # Artifact thumbnails
            _render_artifact_thumbnails(exp_data)


def _render_artifact_thumbnails(exp_data: dict) -> None:
    """Show thumbnail images for completed experiment artifacts."""
    artifacts = exp_data.get("artifacts", [])
    if not artifacts:
        return

    image_artifacts = [a for a in artifacts if _is_image(a)]
    if not image_artifacts:
        return

    cols = st.columns(min(len(image_artifacts), 4))
    for i, art_path in enumerate(image_artifacts[:4]):
        full_path = ROOT / art_path
        if full_path.exists():
            with cols[i]:
                st.image(str(full_path), width=150)


def _render_verdict_suggestion(hypothesis_id: str, experiments: list[dict]) -> None:
    """Suggest a verdict based on experiment outcomes."""
    completed = [e for e in experiments if e.get("status") == "completed"]
    if not completed:
        return

    # Check experiment result summaries for verdict suggestions
    suggestions = []
    for exp in completed:
        exp_data = get_experiment(exp["id"])
        if not exp_data or not exp_data.get("result_summary"):
            continue
        summary = exp_data["result_summary"].lower()
        # Try to parse JSON summary for verdict_suggestion
        try:
            parsed = json.loads(exp_data["result_summary"])
            if isinstance(parsed, dict) and parsed.get("verdict_suggestion"):
                suggestions.append(parsed["verdict_suggestion"])
                continue
        except (json.JSONDecodeError, TypeError):
            pass
        # Heuristic fallback
        if "support" in summary:
            suggestions.append("supports")
        elif "contradict" in summary or "refute" in summary:
            suggestions.append("contradicts")

    if not suggestions:
        return

    all_support = all(s == "supports" for s in suggestions)
    any_contradict = any(s == "contradicts" for s in suggestions)

    if all_support and len(suggestions) == len(completed):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.success("All experiments support this hypothesis.")
        with col2:
            if st.button("✅ Set Supported", key=f"suggest_sup_{hypothesis_id}"):
                update_verdict(hypothesis_id, "supported")
                st.rerun()
    elif any_contradict:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.warning("Some experiments contradict this hypothesis.")
        with col2:
            if st.button("Set Refuted", key=f"suggest_ref_{hypothesis_id}"):
                update_verdict(hypothesis_id, "refuted")
                st.rerun()


def _render_verdict_override(hypothesis_id: str, current_verdict: str) -> None:
    """Manual verdict dropdown for the hypothesis."""
    st.subheader("⚖️ Manual Verdict")
    current_idx = VERDICT_OPTIONS.index(current_verdict) if current_verdict in VERDICT_OPTIONS else 0
    new_verdict = st.selectbox(
        "Set verdict",
        VERDICT_OPTIONS,
        index=current_idx,
        key=f"verdict_select_{hypothesis_id}",
    )
    if st.button("Update Verdict", key=f"update_verdict_{hypothesis_id}"):
        update_verdict(hypothesis_id, new_verdict)
        st.success(f"Verdict updated to **{new_verdict}**")
        st.rerun()


def _form_add_experiment(hypothesis_id: str) -> None:
    """Form to add a new experiment under a hypothesis."""
    with st.form(f"add_experiment_{hypothesis_id}", clear_on_submit=True):
        st.subheader("🔬 Add Experiment")
        title = st.text_input("Experiment title", key=f"exp_title_{hypothesis_id}")
        dataset = st.text_input("Dataset(s)", key=f"exp_dataset_{hypothesis_id}")
        methodology = st.text_area("Methodology", key=f"exp_method_{hypothesis_id}")
        params_str = st.text_area(
            "Parameters (JSON)",
            value="{}",
            key=f"exp_params_{hypothesis_id}",
        )

        if st.form_submit_button("Create Experiment") and title.strip():
            try:
                params = json.loads(params_str)
            except json.JSONDecodeError:
                params = {}

            nid = add_node(
                type="experiment",
                title=title.strip(),
                content=methodology.strip(),
                status="pending",
            )
            add_edge(hypothesis_id, nid, "has_experiment")
            add_experiment(
                node_id=nid,
                dataset=dataset.strip(),
                parameters=params,
            )
            st.rerun()


# ═══════════════════════════════════════════════════════════════════
# Layer 3 — Experiment Detail
# ═══════════════════════════════════════════════════════════════════

def page_layer3(experiment_id: str) -> None:
    """Full experiment detail: design, script, execution, results."""
    exp_node = get_node(experiment_id)
    if not exp_node:
        st.error("Experiment not found.")
        return

    exp_data = get_experiment(experiment_id)
    status = exp_node.get("status") or "pending"

    # Header
    st.markdown(f"## 🔬 {exp_node['title']}  {status_icon(status)} *{status}*")

    # Design display
    _render_experiment_design(exp_node, exp_data)

    st.divider()

    # Script display
    _render_script_section(experiment_id, exp_data)

    st.divider()

    # Execution controls
    _render_execution_controls(experiment_id, exp_node, exp_data)

    # Results (if completed)
    if status == "completed" and exp_data:
        st.divider()
        _render_results(exp_data)

    # Autopilot progress indicator (Task 15.1)
    st.divider()
    _render_autopilot_progress(experiment_id)

    # Parameter editing & re-run
    st.divider()
    _render_parameter_editor(experiment_id, exp_data)

    # AI Chat panel
    st.divider()
    render_chat_panel(experiment_id, step_type="chat")


def _render_experiment_design(exp_node: dict, exp_data: dict | None) -> None:
    """Display experiment design: dataset, parameters, methodology."""
    st.subheader("📋 Experiment Design")

    col1, col2 = st.columns(2)
    with col1:
        dataset = exp_data.get("dataset", "") if exp_data else ""
        st.markdown(f"**Dataset:** {dataset or 'Not specified'}")
    with col2:
        st.markdown(f"**Status:** {exp_node.get('status', 'pending')}")

    # Parameters
    if exp_data and exp_data.get("parameters"):
        params = exp_data["parameters"]
        if params:
            st.markdown("**Parameters:**")
            for k, v in params.items():
                st.markdown(f"- `{k}`: `{v}`")

    # Methodology
    content = exp_node.get("content", "")
    if content:
        st.markdown("**Methodology:**")
        st.markdown(content)


def _render_script_section(experiment_id: str, exp_data: dict | None) -> None:
    """Display the experiment script with syntax highlighting + generate button."""
    st.subheader("📜 Script")

    script_path = exp_data.get("script_path", "") if exp_data else ""

    if script_path:
        full_path = ROOT / script_path
        if full_path.exists():
            script_content = full_path.read_text()
            st.code(script_content, language="python")
        else:
            st.warning(f"Script file not found: {script_path}")
    else:
        st.caption("No script generated yet.")

    # Generate Script button
    if st.button("🤖 Generate Script", key=f"gen_script_{experiment_id}"):
        _generate_script_action(experiment_id, exp_data)


def _generate_script_action(experiment_id: str, exp_data: dict | None) -> None:
    """Generate a script via LLM and save it."""
    from pipeline.scriptgen import generate_script, save_script

    dataset = exp_data.get("dataset", "") if exp_data else ""
    datasets = [d.strip() for d in dataset.split(",") if d.strip()] if dataset else []
    params = exp_data.get("parameters", {}) if exp_data else {}
    exp_node = get_node(experiment_id)
    methodology = exp_node.get("content", "") if exp_node else ""

    with st.spinner("Generating script via LLM..."):
        try:
            script_content = generate_script(
                experiment_node_id=experiment_id,
                dataset_names=datasets,
                methodology=methodology,
                parameters=params,
            )
            script_path = save_script(experiment_id, script_content)
            st.success(f"Script saved to `{script_path}`")
            st.rerun()
        except Exception as e:
            st.error(f"Script generation failed: {e}")


def _render_execution_controls(
    experiment_id: str, exp_node: dict, exp_data: dict | None
) -> None:
    """Run Experiment button with spinner and persistent result display."""
    st.subheader("▶️ Execution")

    script_path = exp_data.get("script_path", "") if exp_data else ""
    status = exp_node.get("status") or "pending"

    if not script_path:
        st.caption("Generate a script first before running.")
        return

    if status == "running":
        st.info("🔄 Experiment is currently running...")
        return

    # Show last run result if stored in session state
    run_result_key = f"run_result_{experiment_id}"
    if run_result_key in st.session_state:
        result = st.session_state[run_result_key]
        if result.get("status") == "done":
            st.success("✅ Last run completed successfully.")
            if result.get("summary") and isinstance(result["summary"], dict):
                st.caption(f"📝 {result['summary'].get('summary', '')}")
        else:
            st.error("❌ Last run failed.")
            with st.expander("View error output", expanded=True):
                st.code(result.get("output", "No output captured"), language="text")
        if st.button("🗑️ Clear result", key=f"clear_result_{experiment_id}"):
            st.session_state.pop(run_result_key, None)
            st.rerun()

    # Run button + manual command hint
    col1, col2 = st.columns([1, 3])
    with col1:
        run_clicked = st.button("▶️ Run Experiment", key=f"run_exp_{experiment_id}")
    with col2:
        st.caption(f"Or run manually: `uv run {script_path}`")

    if run_clicked:
        from pipeline.runner import run_with_retry

        update_node_status(experiment_id, "running")
        with st.spinner("Running experiment (with auto-retry on failure)..."):
            try:
                result = run_with_retry(experiment_id)
                st.session_state[run_result_key] = result
                if result.get("status") == "done":
                    update_node_status(experiment_id, "completed")
                else:
                    update_node_status(experiment_id, "failed")
            except Exception as e:
                update_node_status(experiment_id, "failed")
                st.session_state[run_result_key] = {
                    "status": "failed",
                    "output": f"Exception: {type(e).__name__}: {e}",
                }
        st.rerun()


def _render_results(exp_data: dict) -> None:
    """Display results: summary, artifacts, LLM interpretation side by side."""
    st.subheader("📊 Results")

    col1, col2 = st.columns(2)

    with col1:
        # Summary
        st.markdown("**Summary**")
        summary = exp_data.get("result_summary", "")
        if summary:
            # Try to render as parsed JSON
            try:
                parsed = json.loads(summary)
                if isinstance(parsed, dict):
                    st.markdown(parsed.get("summary", summary))
                    metrics = parsed.get("metrics", {})
                    if metrics:
                        st.markdown("**Metrics:**")
                        for k, v in metrics.items():
                            st.metric(k, v)
                else:
                    st.markdown(summary)
            except (json.JSONDecodeError, TypeError):
                st.markdown(summary)
        else:
            st.caption("No summary available.")

    with col2:
        # LLM Interpretation
        st.markdown("**LLM Interpretation**")
        interp = exp_data.get("llm_interpretation", "")
        if interp:
            with st.expander("View interpretation", expanded=True):
                st.markdown(interp)
        else:
            st.caption("No interpretation yet.")

    # Artifacts
    artifacts = exp_data.get("artifacts", [])
    if artifacts:
        st.markdown("**Artifacts**")
        image_arts = [a for a in artifacts if _is_image(a)]
        other_arts = [a for a in artifacts if not _is_image(a)]

        if image_arts:
            cols = st.columns(min(len(image_arts), 3))
            for i, art in enumerate(image_arts):
                full_path = ROOT / art
                if full_path.exists():
                    with cols[i % 3]:
                        st.image(str(full_path), caption=Path(art).name)

        for art in other_arts:
            full_path = ROOT / art
            st.markdown(f"📎 `{art}`" + (" ✅" if full_path.exists() else " ⚠️ missing"))


def _render_parameter_editor(experiment_id: str, exp_data: dict | None) -> None:
    """Allow editing parameters and re-running the experiment."""
    st.subheader("🔧 Parameters")

    params = exp_data.get("parameters", {}) if exp_data else {}
    if not params:
        st.caption("No parameters defined.")
        return

    with st.form(f"edit_params_{experiment_id}"):
        edited = {}
        for key, value in params.items():
            edited[key] = st.text_input(f"{key}", value=str(value), key=f"param_{experiment_id}_{key}")

        col1, col2 = st.columns(2)
        with col1:
            save_only = st.form_submit_button("💾 Save Parameters")
        with col2:
            rerun = st.form_submit_button("🔄 Save & Re-run")

        if save_only or rerun:
            # Convert values back to appropriate types
            converted = {}
            for k, v in edited.items():
                try:
                    converted[k] = json.loads(v)
                except (json.JSONDecodeError, TypeError):
                    converted[k] = v

            # Update parameters in DB
            from pipeline.graph import _conn
            with _conn() as conn:
                conn.execute(
                    "UPDATE experiments SET parameters_json = ? WHERE node_id = ?",
                    (json.dumps(converted), experiment_id),
                )

            if save_only:
                st.success("Parameters saved.")
                st.rerun()

            if rerun:
                from pipeline.runner import run_with_retry

                update_node_status(experiment_id, "running")
                with st.spinner("Re-running experiment..."):
                    try:
                        result = run_with_retry(experiment_id)
                        if result.get("status") == "done":
                            update_node_status(experiment_id, "completed")
                            st.success("Re-run completed!")
                        else:
                            update_node_status(experiment_id, "failed")
                            st.error(f"Re-run failed: {result.get('output', '')[:500]}")
                    except Exception as e:
                        update_node_status(experiment_id, "failed")
                        st.error(f"Execution error: {e}")
                st.rerun()


# ═══════════════════════════════════════════════════════════════════
# AI Chat Integration (Task 12)
# ═══════════════════════════════════════════════════════════════════

def _build_chat_context(node_id: str) -> str:
    """Build context string for AI chat: node content + parent chain + experiment results."""
    parts: list[str] = []

    # Current node content
    node = get_node(node_id)
    if not node:
        return ""
    parts.append(f"Current {node['type']}: {node['title']}")
    if node.get("content"):
        parts.append(node["content"])

    # Parent chain up to root
    chain = _build_parent_chain(node_id)
    if len(chain) > 1:
        parts.append("\n--- Ancestor Context ---")
        for ancestor in chain[:-1]:
            parts.append(f"{ancestor['type'].title()}: {ancestor['title']}")
            if ancestor.get("content"):
                parts.append(ancestor["content"])

    # Related experiment results
    experiments = get_children_of_type(node_id, "experiment")
    if experiments:
        parts.append("\n--- Related Experiment Results ---")
        for exp in experiments:
            exp_data = get_experiment(exp["id"])
            if exp_data and exp_data.get("result_summary"):
                parts.append(f"Experiment: {exp['title']}")
                parts.append(f"Result: {exp_data['result_summary'][:500]}")

    # If this is an experiment, include its own result
    if node["type"] == "experiment":
        exp_data = get_experiment(node_id)
        if exp_data and exp_data.get("result_summary"):
            parts.append(f"\n--- This Experiment's Result ---\n{exp_data['result_summary']}")

    return "\n\n".join(parts)


def render_chat_panel(node_id: str, step_type: str = "chat") -> None:
    """Render an AI chat panel scoped to a node. Can be called from any layer."""
    from pipeline.graph import add_ai_message, get_ai_thread
    from pipeline.llm import call_model, get_all_models, extract_from_thread

    st.subheader("💬 AI Chat")

    # Model selector
    models = get_all_models()
    if not models:
        models = ["claude-sonnet-4-6"]
    selected_model = st.selectbox(
        "Model",
        models,
        key=f"chat_model_select_{node_id}_{step_type}",
    )

    # Display existing messages
    thread = get_ai_thread(node_id, step_type)
    for msg in thread:
        role = msg["role"]
        with st.chat_message("user" if role == "user" else "assistant"):
            st.markdown(msg["content"])

    # Send message
    user_input = st.chat_input("Ask about this node...", key=f"chat_input_{node_id}_{step_type}")
    if user_input:
        add_ai_message(node_id, step_type, "user", user_input)

        context = _build_chat_context(node_id)
        system_prompt = (
            "You are a research assistant for the XWorld time series shape clustering project. "
            "Use the provided context to give informed answers. "
            "When suggesting new research directions, format them as numbered lists under "
            "clear headings: 'Questions:', 'Hypotheses:', or 'Experiments:'."
        )

        messages = [{"role": "user", "content": f"Context:\n{context}\n\n---\n\n"}]
        for msg in thread:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": user_input})

        with st.spinner("Thinking..."):
            try:
                response = call_model(selected_model, messages, system=system_prompt)
                add_ai_message(node_id, step_type, "assistant", response, model=selected_model)
                st.rerun()
            except Exception as e:
                st.error(f"Chat error: {e}")

    # Extract structured items button
    if thread and any(m["role"] == "assistant" for m in thread):
        if st.button("🔍 Extract Items from Chat", key=f"extract_{node_id}_{step_type}"):
            _extract_and_add_items(node_id, step_type, thread, selected_model)


def _extract_and_add_items(
    node_id: str, step_type: str, thread: list[dict], model: str
) -> None:
    """Extract structured items from chat and offer Add to Graph."""
    from pipeline.llm import extract_from_thread

    with st.spinner("Extracting items..."):
        try:
            items = extract_from_thread(thread, "items", model)
        except Exception as e:
            st.error(f"Extraction failed: {e}")
            return

    if not isinstance(items, dict):
        st.warning("No structured items found.")
        return

    has_items = False
    for category, item_list in items.items():
        if not item_list:
            continue
        has_items = True
        st.markdown(f"**{category.title()}:**")
        for i, item_text in enumerate(item_list):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"- {item_text}")
            with col2:
                if st.button("➕ Add", key=f"add_{category}_{i}_{node_id}"):
                    _add_extracted_item_to_graph(node_id, category, item_text)

    if not has_items:
        st.info("No questions, hypotheses, or experiments found in the conversation.")


def _add_extracted_item_to_graph(node_id: str, category: str, title: str) -> None:
    """Add an extracted item to the knowledge graph linked to the current node."""
    type_map = {"questions": "question", "hypotheses": "hypothesis", "experiments": "experiment"}
    edge_map = {"questions": "has_sub_question", "hypotheses": "has_hypothesis", "experiments": "has_experiment"}

    node_type = type_map.get(category, "question")
    edge_type = edge_map.get(category, "has_sub_question")

    nid = add_node(type=node_type, title=title, content="Extracted from AI chat", status="pending")
    add_edge(node_id, nid, edge_type)

    if node_type == "hypothesis":
        update_verdict(nid, "open")
    elif node_type == "experiment":
        add_experiment(node_id=nid, dataset="", parameters={})

    st.success(f"Added {node_type}: {title}")
    st.rerun()


# ═══════════════════════════════════════════════════════════════════
# Queue Dashboard (Task 13)
# ═══════════════════════════════════════════════════════════════════

def _now_str() -> str:
    """Return current UTC time as ISO string."""
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def page_queue() -> None:
    """Queue dashboard — sortable list of queued/running/completed experiments."""
    from pipeline.graph import get_queue, get_next_queued, update_queue_item
    from pipeline.runner import run_with_retry

    st.header("📋 Experiment Queue")

    # Run Next button + filter
    col1, col2 = st.columns([1, 3])
    with col1:
        run_next = st.button("▶️ Run Next", type="primary")
    with col2:
        filter_status = st.selectbox(
            "Filter by status",
            ["all", "queued", "running", "done", "failed"],
            key="queue_filter",
        )

    if run_next:
        next_item = get_next_queued()
        if next_item:
            update_queue_item(next_item["id"], "running", started_at=_now_str())
            update_node_status(next_item["node_id"], "running")
            with st.spinner(f"Running: {next_item.get('title', 'experiment')}..."):
                try:
                    result = run_with_retry(next_item["node_id"])
                    if result.get("status") == "done":
                        update_queue_item(
                            next_item["id"], "done",
                            run_output=result.get("output", ""),
                            completed_at=_now_str(),
                        )
                        update_node_status(next_item["node_id"], "completed")
                        st.success("Experiment completed!")
                    else:
                        update_queue_item(
                            next_item["id"], "failed",
                            run_output=result.get("output", ""),
                            completed_at=_now_str(),
                        )
                        update_node_status(next_item["node_id"], "failed")
                        st.error("Experiment failed.")
                except Exception as e:
                    update_queue_item(
                        next_item["id"], "failed",
                        run_output=str(e),
                        completed_at=_now_str(),
                    )
                    update_node_status(next_item["node_id"], "failed")
                    st.error(f"Error: {e}")
            st.rerun()
        else:
            st.info("No queued experiments.")

    # Get queue items
    queue_items = get_queue(status=filter_status if filter_status != "all" else None)

    if not queue_items:
        st.info("Queue is empty.")
        return

    for item in queue_items:
        _render_queue_item(item)


def _render_queue_item(item: dict) -> None:
    """Render a single queue item with priority, status, removal, and log viewer."""
    from pipeline.graph import update_queue_item, _conn

    status = item.get("status", "queued")
    title = item.get("title", "Unknown")
    priority = item.get("priority", 0)
    q_status_icons = {"queued": "⏳", "running": "🔄", "done": "✅", "failed": "❌"}
    icon = q_status_icons.get(status, "⏳")

    with st.container(border=True):
        col1, col2, col3, col4 = st.columns([4, 1, 1, 1])
        with col1:
            st.markdown(f"{icon} **{title}**")
        with col2:
            st.caption(status)
        with col3:
            # Running elapsed time
            if status == "running" and item.get("started_at"):
                try:
                    from datetime import datetime, timezone
                    started = datetime.fromisoformat(item["started_at"])
                    elapsed = (datetime.now(timezone.utc) - started).total_seconds()
                    mins, secs = divmod(int(elapsed), 60)
                    st.caption(f"⏱️ {mins}m {secs}s")
                except Exception:
                    st.caption("⏱️ running")
            else:
                st.caption(f"pri: {priority}")
        with col4:
            # Priority reordering for queued items
            if status == "queued":
                new_priority = st.number_input(
                    "Priority",
                    value=priority,
                    step=1,
                    key=f"pri_{item['id']}",
                    label_visibility="collapsed",
                )
                if new_priority != priority:
                    with _conn() as conn:
                        conn.execute(
                            "UPDATE queue SET priority=? WHERE id=?",
                            (new_priority, item["id"]),
                        )
                    st.rerun()

        # Remove button (only for queued items)
        if status == "queued":
            if st.button("🗑️ Remove", key=f"remove_{item['id']}"):
                with _conn() as conn:
                    conn.execute("DELETE FROM queue WHERE id=? AND status='queued'", (item["id"],))
                st.rerun()

        # Expandable log viewer for completed/failed items
        if status in ("done", "failed") and item.get("run_output"):
            with st.expander("📜 View Log"):
                st.code(item["run_output"], language="text")


# ═══════════════════════════════════════════════════════════════════
# Settings Page (Task 14)
# ═══════════════════════════════════════════════════════════════════

def page_settings() -> None:
    """Settings page — API keys, model selectors, MLflow, DB stats, snapshots."""
    import subprocess

    st.header("⚙️ Settings")

    # --- API Key ---
    st.subheader("🔑 API Configuration")
    current_key = get_setting("claude_api_key", "")
    new_key = st.text_input(
        "Claude API Key",
        value=current_key,
        type="password",
        key="settings_api_key",
    )
    if new_key != current_key:
        set_setting("claude_api_key", new_key)
        st.success("API key updated.")

    st.divider()

    # --- Model Selectors ---
    st.subheader("🤖 Autopilot Model Configuration")
    from pipeline.llm import get_all_models
    all_models = get_all_models()
    if not all_models:
        all_models = ["claude-sonnet-4-6", "claude-opus-4-6", "claude-haiku-4-5-20251001"]

    model_settings = [
        ("autopilot_summarise_model", "Summarisation Model", "qwen2.5:latest"),
        ("autopilot_interpret_model", "Interpretation Model", "claude-sonnet-4-6"),
        ("autopilot_branch_model", "Branch Generation Model", "claude-sonnet-4-6"),
        ("autopilot_design_model", "Experiment Design Model", "claude-sonnet-4-6"),
        ("autopilot_script_model", "Script Generation Model", "claude-sonnet-4-6"),
    ]

    for setting_key, label, default in model_settings:
        current = get_setting(setting_key, default)
        options = all_models if current in all_models else [current] + all_models
        idx = options.index(current) if current in options else 0
        new_val = st.selectbox(label, options, index=idx, key=f"setting_{setting_key}")
        if new_val != current:
            set_setting(setting_key, new_val)

    st.divider()

    # --- MLflow Toggle ---
    st.subheader("📊 MLflow Integration")
    mlflow_enabled = get_setting("mlflow_enabled", "false").lower() == "true"
    new_mlflow = st.toggle("Enable MLflow Tracking", value=mlflow_enabled, key="mlflow_toggle")
    if new_mlflow != mlflow_enabled:
        set_setting("mlflow_enabled", "true" if new_mlflow else "false")
        st.success(f"MLflow {'enabled' if new_mlflow else 'disabled'}.")

    if new_mlflow:
        _render_mlflow_controls()

    st.divider()

    # --- Database Statistics ---
    st.subheader("📈 Database Statistics")
    _render_db_stats()

    st.divider()

    # --- Snapshot ---
    st.subheader("💾 Database Snapshot")
    if st.button("📸 Create Snapshot"):
        from pipeline.graph import create_snapshot
        try:
            snap_path = create_snapshot()
            st.success(f"Snapshot created: `{snap_path}`")
        except Exception as e:
            st.error(f"Snapshot failed: {e}")


def _render_mlflow_controls() -> None:
    """Start/Stop MLflow server buttons and UI link."""
    import subprocess

    mlflow_process = st.session_state.get("mlflow_process")

    # Check if process is still running
    if mlflow_process and mlflow_process.poll() is not None:
        st.session_state["mlflow_process"] = None
        mlflow_process = None

    if mlflow_process is None:
        if st.button("🚀 Start MLflow Server"):
            try:
                proc = subprocess.Popen(
                    [
                        "mlflow", "server",
                        "--backend-store-uri", f"sqlite:///{ROOT / 'mlflow.db'}",
                        "--default-artifact-root", str(ROOT / "mlflow-artifacts"),
                        "--port", "5000",
                    ],
                    cwd=str(ROOT),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                st.session_state["mlflow_process"] = proc
                st.success("MLflow server starting on port 5000...")
                st.rerun()
            except FileNotFoundError:
                st.error("MLflow not installed. Run: `pip install mlflow`")
            except Exception as e:
                st.error(f"Failed to start MLflow: {e}")
    else:
        st.success("MLflow server is running.")
        st.markdown("[🔗 Open MLflow UI](http://localhost:5000)")
        if st.button("🛑 Stop MLflow Server"):
            mlflow_process.terminate()
            try:
                mlflow_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                mlflow_process.kill()
            st.session_state["mlflow_process"] = None
            st.info("MLflow server stopped.")
            st.rerun()


def _render_db_stats() -> None:
    """Display database statistics: node counts by type, edge count, file size."""
    from pipeline.graph import _conn

    with _conn() as conn:
        rows = conn.execute(
            "SELECT type, COUNT(*) as cnt FROM nodes GROUP BY type ORDER BY type"
        ).fetchall()
        node_counts = {r["type"]: r["cnt"] for r in rows}
        total_nodes = sum(node_counts.values())

        edge_count = conn.execute("SELECT COUNT(*) as cnt FROM edges").fetchone()["cnt"]
        exp_count = conn.execute("SELECT COUNT(*) as cnt FROM experiments").fetchone()["cnt"]

    db_path = ROOT / "xworld.db"
    if db_path.exists():
        size_bytes = db_path.stat().st_size
        if size_bytes < 1024:
            size_str = f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            size_str = f"{size_bytes / 1024:.1f} KB"
        else:
            size_str = f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        size_str = "N/A"

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Nodes", total_nodes)
    with col2:
        st.metric("Edges", edge_count)
    with col3:
        st.metric("Experiments", exp_count)
    with col4:
        st.metric("DB Size", size_str)

    if node_counts:
        st.markdown("**Nodes by type:**")
        for ntype, count in node_counts.items():
            st.markdown(f"- {node_icon(ntype)} {ntype}: {count}")


# ═══════════════════════════════════════════════════════════════════
# Autopilot UI Integration (Task 15)
# ═══════════════════════════════════════════════════════════════════

def _render_autopilot_progress(experiment_id: str) -> None:
    """Show autopilot progress indicator in Layer 3 (current step)."""
    from pipeline.autopilot import AutopilotStep

    state = st.session_state.get(f"autopilot_state_{experiment_id}")
    if not state:
        return

    step = state.current_step
    steps = [
        AutopilotStep.SUMMARISE,
        AutopilotStep.INTERPRET,
        AutopilotStep.GENERATE_BRANCHES,
        AutopilotStep.AWAITING_APPROVAL,
        AutopilotStep.COMPLETE,
    ]
    step_labels = ["Summarising", "Interpreting", "Generating Branches", "Awaiting Approval", "Complete"]

    st.subheader("🤖 Autopilot Progress")
    current_idx = steps.index(step) if step in steps else 0
    cols = st.columns(len(steps))
    for i, (s, label) in enumerate(zip(steps, step_labels)):
        with cols[i]:
            if i < current_idx:
                st.markdown(f"✅ {label}")
            elif i == current_idx:
                st.markdown(f"🔄 **{label}**")
            else:
                st.markdown(f"⬜ {label}")

    # Show summary and interpretation if available
    if state.summary:
        with st.expander("📝 Summary", expanded=False):
            st.markdown(state.summary)
    if state.interpretation:
        with st.expander("🔍 Interpretation", expanded=False):
            st.markdown(state.interpretation)

    # Candidate approval UI
    if step == AutopilotStep.AWAITING_APPROVAL and state.candidates:
        _render_candidate_approval(experiment_id, state)


def _render_candidate_approval(experiment_id: str, state) -> None:
    """Render candidate approval/rejection UI — list of suggestions with approve/reject buttons."""
    from pipeline.autopilot import approve_candidate, reject_candidate, commit_approved

    st.subheader("📋 Candidate Suggestions")
    st.caption("Review AI-generated suggestions. Approve to add to the knowledge graph, or reject with a reason.")

    # Iterate in reverse to handle index shifts from removals
    candidates_to_render = list(enumerate(state.candidates))
    for i, candidate in candidates_to_render:
        with st.container(border=True):
            col1, col2, col3 = st.columns([4, 1, 1])
            with col1:
                ctype = candidate.get("type", "question")
                st.markdown(f"{node_icon(ctype)} **{candidate['title']}**")
                if candidate.get("content"):
                    st.caption(candidate["content"][:200])
            with col2:
                if st.button("✅ Approve", key=f"approve_{experiment_id}_{i}"):
                    approve_candidate(state, i)
                    st.rerun()
            with col3:
                if st.button("❌ Reject", key=f"reject_{experiment_id}_{i}"):
                    st.session_state[f"rejecting_{experiment_id}_{i}"] = True
                    st.rerun()

            # Rejection reason input
            if st.session_state.get(f"rejecting_{experiment_id}_{i}"):
                reason = st.text_input("Rejection reason", key=f"reject_reason_{experiment_id}_{i}")
                if st.button("Confirm Reject", key=f"confirm_reject_{experiment_id}_{i}"):
                    reject_candidate(state, i, reason or "No reason given")
                    st.session_state.pop(f"rejecting_{experiment_id}_{i}", None)
                    st.rerun()

    # Show approved/rejected counts
    if state.approved:
        st.success(f"✅ {len(state.approved)} approved")
    if state.rejected:
        st.warning(f"❌ {len(state.rejected)} rejected")

    # Commit button
    if state.approved or (not state.candidates and state.rejected):
        if st.button("💾 Commit Approved to Graph", key=f"commit_{experiment_id}", type="primary"):
            new_ids = commit_approved(state)
            st.success(f"Added {len(new_ids)} nodes to the knowledge graph.")
            st.session_state.pop(f"autopilot_state_{experiment_id}", None)
            st.rerun()


def _render_run_all_pending(hypothesis_id: str) -> None:
    """Render 'Run All Pending' batch button in Layer 2."""
    experiments = get_children_of_type(hypothesis_id, "experiment")
    pending = [e for e in experiments if e.get("status") == "pending"]

    if not pending:
        return

    st.divider()
    st.subheader("🚀 Batch Execution")
    st.caption(f"{len(pending)} pending experiment(s)")

    if st.button("▶️ Run All Pending", key=f"batch_run_{hypothesis_id}", type="primary"):
        from pipeline.autopilot import run_hypothesis_batch

        with st.spinner(f"Running {len(pending)} experiments with autopilot..."):
            try:
                batch_result = run_hypothesis_batch(hypothesis_id)
                st.session_state[f"batch_result_{hypothesis_id}"] = batch_result
                st.success(f"Batch complete: {batch_result.completed}/{batch_result.total} processed.")
                st.rerun()
            except Exception as e:
                st.error(f"Batch execution failed: {e}")

    # Show batch results if available
    batch_result = st.session_state.get(f"batch_result_{hypothesis_id}")
    if batch_result:
        _render_batch_results(hypothesis_id, batch_result)


def _render_batch_results(hypothesis_id: str, batch_result) -> None:
    """Render batch results review UI — all suggestions collected for batch approval."""
    from pipeline.autopilot import approve_candidate, reject_candidate, commit_approved

    st.subheader("📊 Batch Results Review")
    st.caption(f"{batch_result.completed} of {batch_result.total} experiments generated suggestions.")

    for idx, state in enumerate(batch_result.experiment_results):
        with st.expander(f"🔬 Experiment: {state.experiment_node_id[:8]}...", expanded=True):
            if state.summary:
                st.markdown(f"**Summary:** {state.summary[:300]}")
            if state.interpretation:
                st.markdown(f"**Interpretation:** {state.interpretation[:300]}")

            if state.candidates:
                st.markdown("**Candidates:**")
                for i, candidate in enumerate(list(state.candidates)):
                    col1, col2, col3 = st.columns([4, 1, 1])
                    with col1:
                        st.write(f"- {candidate['title']}")
                    with col2:
                        if st.button("✅", key=f"batch_approve_{idx}_{i}_{hypothesis_id}"):
                            approve_candidate(state, i)
                            st.rerun()
                    with col3:
                        if st.button("❌", key=f"batch_reject_{idx}_{i}_{hypothesis_id}"):
                            reject_candidate(state, i, "Rejected in batch review")
                            st.rerun()

            if state.approved:
                st.success(f"{len(state.approved)} approved")

    # Commit all approved across all batch results
    all_approved = sum(len(s.approved) for s in batch_result.experiment_results)
    if all_approved > 0:
        if st.button(
            f"💾 Commit All Approved ({all_approved} items)",
            key=f"batch_commit_{hypothesis_id}",
            type="primary",
        ):
            total_new = 0
            for state in batch_result.experiment_results:
                if state.approved:
                    new_ids = commit_approved(state)
                    total_new += len(new_ids)
            st.success(f"Added {total_new} nodes to the knowledge graph.")
            st.session_state.pop(f"batch_result_{hypothesis_id}", None)
            st.rerun()


# ═══════════════════════════════════════════════════════════════════
# Report Generation UI (Task 16.6)
# ═══════════════════════════════════════════════════════════════════

def _render_report_buttons(hypothesis_id: str) -> None:
    """Render 'Generate Report' and 'Build Site' buttons in Layer 2."""
    import subprocess

    st.subheader("📄 Report Generation")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📝 Generate Report", key=f"gen_report_{hypothesis_id}"):
            from pipeline.report import generate_hypothesis_report
            with st.spinner("Generating report..."):
                try:
                    report_path = generate_hypothesis_report(hypothesis_id)
                    st.success(f"Report generated: `{report_path}`")
                except Exception as e:
                    st.error(f"Report generation failed: {e}")

    with col2:
        if st.button("🏗️ Build Site", key=f"build_site_{hypothesis_id}"):
            with st.spinner("Building MkDocs site..."):
                try:
                    result = subprocess.run(
                        ["mkdocs", "build"],
                        cwd=str(ROOT / "docs"),
                        capture_output=True,
                        text=True,
                        timeout=60,
                    )
                    if result.returncode == 0:
                        st.success("Site built successfully in `docs/site/`")
                    else:
                        st.error(f"Build failed: {result.stderr}")
                except FileNotFoundError:
                    st.error("mkdocs not installed. Run: `pip install mkdocs mkdocs-material`")
                except Exception as e:
                    st.error(f"Build error: {e}")


# ═══════════════════════════════════════════════════════════════════
# Main Entry Point
# ═══════════════════════════════════════════════════════════════════

def main() -> None:
    """App entry point: init DB, render sidebar + breadcrumb, dispatch page."""
    st.set_page_config(
        page_title="XWorld Research Workbench",
        page_icon="🌍",
        layout="wide",
    )

    init_db()
    _init_session_state()

    render_sidebar()
    render_breadcrumb()

    # Page routing based on nav_stack
    stack = st.session_state.nav_stack
    if not stack:
        page_layer1()
    elif stack[-1]["layer"] == "graph":
        render_node_explorer_page()
    elif stack[-1]["layer"] == "hypotheses":
        page_layer1_question(stack[-1]["node_id"])
    elif stack[-1]["layer"] == "experiments":
        page_layer2(stack[-1]["node_id"])
    elif stack[-1]["layer"] == "detail":
        page_layer3(stack[-1]["node_id"])
    elif stack[-1]["layer"] == "queue":
        page_queue()
    elif stack[-1]["layer"] == "settings":
        page_settings()
    else:
        page_layer1()


if __name__ == "__main__":
    main()
