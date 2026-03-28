"""
ui/app.py — XWorld v2
Hierarchical drill-down: Question → Hypothesis → Experiment → Result
Each level loads only its own data. AI panel with multi-model conversation
and integrated extractor at every step.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from pipeline.graph import (
    init_db,
    get_nodes_by_type,
    get_node,
    get_children,
    get_children_of_type,
    get_parents,
    get_experiment,
    get_queue,
    get_next_queued,
    enqueue,
    update_node_status,
    update_verdict,
    add_node,
    add_edge,
    add_experiment,
    get_setting,
    set_setting,
    add_ai_message,
    get_ai_thread,
    clear_ai_thread,
)

init_db()

# ─────────────────────────────────────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="XWorld",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────
VERDICT_OPTIONS = ["open", "supported", "refuted", "inconclusive", "deferred"]
VERDICT_LABEL = {
    "open":         "🟡 Open",
    "supported":    "🟢 Supported",
    "refuted":      "🔴 Refuted",
    "inconclusive": "🟠 Inconclusive",
    "deferred":     "⚫ Deferred",
}
STATUS_LABEL = {
    "pending":   "🟡 Pending",
    "running":   "🔵 Running",
    "completed": "🟢 Completed",
    "failed":    "🔴 Failed",
    "deferred":  "⚫ Deferred",
}
NODE_ICON = {
    "question":   "❓",
    "hypothesis": "💡",
    "experiment": "🔬",
    "result":     "📊",
    "insight":    "✨",
}

# ─────────────────────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────────────────────
st.sidebar.title("🌍 XWorld")
st.sidebar.caption("Cross-domain shape clustering")

_page_opts = ["❓ Questions", "📋 Queue", "⚙️ Settings"]
_page_default = _page_opts.index(st.session_state.pop("goto_page", "❓ Questions"))
page = st.sidebar.radio("Navigate", _page_opts, index=_page_default, label_visibility="collapsed")

if page != st.session_state.get("_cur_page"):
    st.session_state["_cur_page"] = page
    st.session_state["nav_stack"] = []

# Pending batches notice in sidebar
from pipeline.graph import get_pending_batches as _get_pending
_pending = _get_pending()
if _pending:
    st.sidebar.divider()
    st.sidebar.caption(f"⏳ {len(_pending)} batch(es) pending")
    if st.sidebar.button("Check batch results", key="sb_check_batches"):
        from pipeline.llm import check_pending_batches
        resolved = check_pending_batches()
        if resolved:
            st.sidebar.success(f"Resolved {len(resolved)} batch(es).")
        else:
            st.sidebar.info("None ready yet.")
        st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# Navigation helpers
# ─────────────────────────────────────────────────────────────────────────────
def _stack() -> list:
    return st.session_state.setdefault("nav_stack", [])

def _push(node_id: str) -> None:
    _stack().append(node_id)
    st.rerun()

def _pop_to(level: int) -> None:
    st.session_state["nav_stack"] = _stack()[:level]
    st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# Breadcrumb
# ─────────────────────────────────────────────────────────────────────────────
def _breadcrumb(stack: list) -> None:
    if not stack:
        return
    labels = ["All Questions"]
    for nid in stack:
        n = get_node(nid)
        if n:
            icon = NODE_ICON.get(n["type"], "•")
            t = n["title"]
            labels.append(f"{icon} {t[:30]}{'…' if len(t)>30 else ''}")

    # Render: equal-width columns alternating label | separator
    n_parts = len(labels)
    widths = []
    for i in range(n_parts * 2 - 1):
        widths.append(4 if i % 2 == 0 else 1)
    cols = st.columns(widths)
    for i, label in enumerate(labels):
        with cols[i * 2]:
            if i < n_parts - 1:
                if st.button(label, key=f"bc_{i}", use_container_width=True):
                    _pop_to(i)
            else:
                st.markdown(f"**{label}**")
        if i < n_parts - 1:
            with cols[i * 2 + 1]:
                st.markdown("›")
    st.divider()

# ─────────────────────────────────────────────────────────────────────────────
# AI panel helpers
# ─────────────────────────────────────────────────────────────────────────────
def _get_all_models() -> list[str]:
    from pipeline.llm import CLAUDE_MODELS, get_available_ollama_models
    ollama = get_available_ollama_models()
    return CLAUDE_MODELS + ollama


def _fmt_model(m: str) -> str:
    if m.startswith("claude"):
        return f"☁️  {m}"
    return f"🟠  {m}"


def _build_node_context(node_id: str, step_type: str) -> str:
    """
    Build a rich context briefing for the AI panel based on the node and step.
    Returns a formatted string ready to inject as the first message in the thread.
    """
    lines = ["## XWorld context briefing\n"]

    if step_type == "hypotheses":
        # node_id is a question
        q = get_node(node_id)
        if not q:
            return ""
        lines.append(f"**Research question:** {q['title']}")
        if q.get("content"):
            lines.append(f"\n{q['content']}")
        existing = get_children_of_type(node_id, "hypothesis")
        if existing:
            lines.append(f"\n**Hypotheses already in the graph ({len(existing)}):**")
            for h in existing:
                verdict = h.get("verdict") or "open"
                lines.append(f"- [{verdict}] {h['title']}")
        else:
            lines.append("\n**No hypotheses yet** — this is the first exploration.")

    elif step_type == "experiments":
        # node_id is a hypothesis
        h = get_node(node_id)
        if not h:
            return ""
        lines.append(f"**Hypothesis:** {h['title']}")
        verdict = h.get("verdict") or "open"
        lines.append(f"**Current verdict:** {verdict}")
        if h.get("content"):
            lines.append(f"\n{h['content']}")
        existing = get_children_of_type(node_id, "experiment")
        if existing:
            lines.append(f"\n**Experiments already designed ({len(existing)}):**")
            for e in existing:
                exp_d = get_experiment(e["id"])
                dataset = exp_d.get("dataset", "") if exp_d else ""
                script  = exp_d.get("script_path", "") if exp_d else ""
                meta = " · ".join(filter(None, [e["status"], dataset, script]))
                lines.append(f"- {e['title']}  [{meta}]")
        else:
            lines.append("\n**No experiments yet** — designing from scratch.")

    elif step_type == "result_discussion":
        # node_id is an experiment
        e = get_node(node_id)
        if not e:
            return ""
        lines.append(f"**Experiment:** {e['title']}")
        lines.append(f"**Status:** {e['status']}")
        if e.get("content"):
            lines.append(f"\n{e['content']}")
        exp_d = get_experiment(node_id)
        if exp_d:
            if exp_d.get("dataset"):
                lines.append(f"**Dataset:** {exp_d['dataset']}")
            if exp_d.get("script_path"):
                lines.append(f"**Script:** `{exp_d['script_path']}`")
            if exp_d.get("result_summary"):
                lines.append(f"\n**Result summary:**\n{exp_d['result_summary']}")
            if exp_d.get("llm_interpretation"):
                lines.append(f"\n**Prior interpretation:**\n{exp_d['llm_interpretation']}")
            if exp_d.get("artifacts"):
                lines.append(f"\n**Artifacts:** {', '.join(exp_d['artifacts'])}")
        branches = [c for c in get_children(node_id) if c["type"] not in ("result", "insight")]
        if branches:
            lines.append(f"\n**Already branched from this experiment:**")
            for b in branches:
                lines.append(f"- [{b['type']}] {b['title']}")

    return "\n".join(lines)


def _gather_related_nodes(node_id: str, step_type: str) -> dict[str, list[dict]]:
    """
    Walk the graph from node_id and return related nodes by category.
    This is the 'mini agent' — it traverses ancestors, siblings, and results
    so the user can pick what to include in the conversation context.
    """
    categories: dict[str, list[dict]] = {
        "Parent question": [],
        "Related hypotheses": [],
        "Experiments with results": [],
        "Branched questions": [],
    }
    node = get_node(node_id)
    if not node:
        return {}

    visited: set[str] = {node_id}

    # ── Walk up the ancestor chain ────────────────────────────────────────
    ancestors: list[dict] = []
    cur = node_id
    for _ in range(10):
        parents = get_parents(cur)
        if not parents:
            break
        p = parents[0]
        if p["id"] in visited:
            break
        visited.add(p["id"])
        ancestors.append(p)
        cur = p["id"]

    for a in ancestors:
        if a["type"] == "question":
            categories["Parent question"].append(a)
        elif a["type"] == "hypothesis":
            categories["Related hypotheses"].append(a)

    # ── Siblings at the same level ────────────────────────────────────────
    immediate_parents = get_parents(node_id)
    if immediate_parents:
        par_id = immediate_parents[0]["id"]
        for sib in get_children(par_id):
            if sib["id"] not in visited and sib["type"] == node["type"]:
                visited.add(sib["id"])
                if sib["type"] == "hypothesis":
                    categories["Related hypotheses"].append(sib)

    # ── Other hypotheses under the root question ──────────────────────────
    root_q = next((a for a in ancestors if a["type"] == "question"), None)
    if root_q:
        for h in get_children_of_type(root_q["id"], "hypothesis"):
            if h["id"] not in visited:
                visited.add(h["id"])
                categories["Related hypotheses"].append(h)

    # ── Completed experiments with results ───────────────────────────────
    # Collect from: this node (if hypothesis), all ancestor hypotheses,
    # and all hypotheses under the root question
    hyp_ids = []
    if node["type"] == "hypothesis":
        hyp_ids.append(node_id)
    hyp_ids += [a["id"] for a in ancestors if a["type"] == "hypothesis"]
    if root_q:
        for h in get_children_of_type(root_q["id"], "hypothesis"):
            if h["id"] not in hyp_ids:
                hyp_ids.append(h["id"])

    for h_id in hyp_ids:
        for exp in get_children_of_type(h_id, "experiment"):
            if exp["id"] in visited:
                continue
            exp_d = get_experiment(exp["id"])
            if exp_d and (exp_d.get("result_summary") or exp_d.get("llm_interpretation")):
                visited.add(exp["id"])
                categories["Experiments with results"].append({
                    **exp,
                    "_result": exp_d.get("result_summary", ""),
                    "_interpretation": exp_d.get("llm_interpretation", ""),
                    "_dataset": exp_d.get("dataset", ""),
                })

    # ── Questions that branched from completed experiments ─────────────────
    for item in categories["Experiments with results"]:
        for child in get_children(item["id"]):
            if child["type"] == "question" and child["id"] not in visited:
                visited.add(child["id"])
                categories["Branched questions"].append(child)

    # Remove empty categories
    return {k: v for k, v in categories.items() if v}


def _inject_selected_context(
    node_id: str,
    step_type: str,
    selected: list[dict],
) -> None:
    """Format selected related nodes and inject as a context message in the thread."""
    lines = ["## Historical context from graph\n"]
    for item in selected:
        icon = NODE_ICON.get(item["type"], "•")
        lines.append(f"### {icon} {item['title']}")
        if item.get("content"):
            lines.append(item["content"])
        if item.get("_dataset"):
            lines.append(f"**Dataset:** {item['_dataset']}")
        if item.get("_result"):
            lines.append(f"**Result:** {item['_result']}")
        if item.get("_interpretation"):
            lines.append(f"**Interpretation:** {item['_interpretation']}")
        lines.append("")
    add_ai_message(node_id, step_type, "user", "\n".join(lines), model="context")


def _render_context_builder(
    node_id: str,
    step_type: str,
    panel_key: str,
    question_id: str = "",
    hypothesis_id: str = "",
) -> None:
    """
    Right-column panel: query graph for related nodes, let user select,
    inject selected as a context message.
    """
    with st.expander("📎 Add historical context", expanded=False):
        related = _gather_related_nodes(node_id, step_type)
        if not related:
            st.caption("No related nodes found in the graph yet.")
            return

        # Render checkboxes; collect specs for the Add button
        checkbox_specs: list[tuple[str, dict]] = []
        for category, items in related.items():
            st.caption(f"**{category}**")
            for item in items:
                icon = NODE_ICON.get(item["type"], "•")
                label = f"{icon} {item['title'][:55]}"
                if item.get("_result"):
                    label += "  📊"
                key = f"ctx_cb_{panel_key}_{item['id']}"
                checkbox_specs.append((key, item))
                st.checkbox(label, key=key)

        selected = [
            item for key, item in checkbox_specs
            if st.session_state.get(key, False)
        ]
        if selected:
            if st.button(
                f"📎 Inject {len(selected)} item(s) into context",
                key=f"ctx_inject_{panel_key}",
                type="primary",
                use_container_width=True,
            ):
                _inject_selected_context(node_id, step_type, selected)
                for key, _ in checkbox_specs:
                    st.session_state.pop(key, None)
                st.rerun()


def _open_chat(
    node_id: str,
    step_type: str,
    title: str,
    parent_type: str,
    question_id: str = "",
    hypothesis_id: str = "",
) -> None:
    st.session_state["chat"] = {
        "node_id": node_id,
        "step_type": step_type,
        "title": title,
        "parent_type": parent_type,
        "question_id": question_id,
        "hypothesis_id": hypothesis_id,
    }
    st.rerun()


def _system_prompt(step_type: str, context: str) -> str:
    base = (
        "You are assisting with XWorld — a cross-domain time series shape clustering "
        "experiment. The core question: do time series from unrelated domains share "
        "underlying dynamic shapes detectable by 5 features (skewness, kurtosis, "
        "lag1_autocorr, zero_crossings, slope) + UMAP + HDBSCAN?\n\n"
    )
    if step_type == "hypotheses":
        return base + f"Current focus: generating and refining testable hypotheses.\nResearch question: {context}"
    if step_type == "experiments":
        return base + f"Current focus: designing experiments.\nHypothesis under test: {context}"
    if step_type == "result_discussion":
        return base + f"Current focus: interpreting results and planning next steps.\nResult context: {context}"
    return base


def _render_ai_panel(
    node_id: str,
    step_type: str,
    context: str = "",
    question_id: str = "",
    hypothesis_id: str = "",
) -> None:
    """
    Full AI panel: model selector, conversation thread, extractor.
    node_id      — the graph node this conversation belongs to
    step_type    — "hypotheses" | "experiments" | "result_discussion"
    context      — pre-context text (question/hypothesis/result)
    question_id  — for adding hypothesis nodes
    hypothesis_id — for adding experiment nodes
    """
    all_models = _get_all_models()
    panel_key = f"{node_id}_{step_type}"

    col_conv, col_ext = st.columns([6, 4])

    # ── Conversation column ───────────────────────────────────────────────
    with col_conv:
        st.caption("**Conversation**")

        # Model selector row
        c_model, c_mode = st.columns([3, 2])
        with c_model:
            model = st.selectbox(
                "Model",
                all_models if all_models else ["claude-sonnet-4-6"],
                key=f"conv_model_{panel_key}",
                format_func=_fmt_model,
                label_visibility="collapsed",
            )
        with c_mode:
            if model and model.startswith("claude"):
                mode = st.radio(
                    "Mode",
                    ["⚡ Live", "⏳ Batch"],
                    horizontal=True,
                    key=f"conv_mode_{panel_key}",
                    label_visibility="collapsed",
                )
            else:
                mode = "⚡ Live"
                st.caption("🟠 Local · always live")

        # Inject context button
        thread = get_ai_thread(node_id, step_type)
        has_context_msg = any(m.get("model") == "context" for m in thread)
        c_ctx, _ = st.columns([2, 6])
        with c_ctx:
            ctx_label = "✅ Context injected" if has_context_msg else "📋 Inject context"
            if st.button(ctx_label, key=f"inject_ctx_{panel_key}",
                         use_container_width=True, disabled=has_context_msg):
                ctx_text = _build_node_context(node_id, step_type)
                if ctx_text:
                    add_ai_message(node_id, step_type, "user", ctx_text, model="context")
                    st.rerun()

        # Thread display
        thread = get_ai_thread(node_id, step_type)
        if thread:
            with st.container(height=280):
                for msg in thread:
                    is_pending = ":batch:pending" in msg.get("model", "")
                    is_context = msg.get("model") == "context"
                    role = msg["role"]
                    with st.chat_message(role):
                        if is_context:
                            with st.expander("📋 Node context (injected)", expanded=False):
                                st.markdown(msg["content"])
                        else:
                            st.write(msg["content"])
                        mdl = msg.get("model", "")
                        if is_pending:
                            mdl = mdl.replace(":batch:pending", "") + " ⏳ batch pending"
                        if not is_context:
                            st.caption(f"{mdl} · {msg['created_at'][11:16]}")
        else:
            st.info(f"No conversation yet. Inject context above, then start the discussion.")

        # Input
        ctr_key = f"ctr_{panel_key}"
        st.session_state.setdefault(ctr_key, 0)
        inp_key = f"inp_{panel_key}_{st.session_state[ctr_key]}"
        user_input = st.text_area(
            "Message",
            key=inp_key,
            height=80,
            placeholder="Your message…",
            label_visibility="collapsed",
        )

        c_send, c_clear = st.columns([3, 1])
        with c_send:
            if st.button("Send →", key=f"send_{panel_key}", type="primary", use_container_width=True):
                if user_input.strip():
                    _handle_send(
                        node_id=node_id,
                        step_type=step_type,
                        user_input=user_input.strip(),
                        model=model,
                        mode=mode,
                        context=context,
                        thread=thread,
                    )
                    st.session_state[ctr_key] += 1
                    st.rerun()
        with c_clear:
            if st.button("Clear", key=f"clear_{panel_key}", use_container_width=True):
                st.session_state[f"confirm_clear_{panel_key}"] = True

        if st.session_state.pop(f"confirm_clear_{panel_key}", False):
            if st.button("Confirm clear thread", key=f"do_clear_{panel_key}"):
                clear_ai_thread(node_id, step_type)
                st.rerun()

    # ── Right column: context builder + extractor ────────────────────────
    with col_ext:
        _render_context_builder(
            node_id=node_id,
            step_type=step_type,
            panel_key=panel_key,
            question_id=question_id,
            hypothesis_id=hypothesis_id,
        )
        st.divider()
        _render_extractor(
            node_id=node_id,
            step_type=step_type,
            question_id=question_id,
            hypothesis_id=hypothesis_id,
        )


def _handle_send(
    node_id: str,
    step_type: str,
    user_input: str,
    model: str,
    mode: str,
    context: str,
    thread: list[dict],
) -> None:
    """Save user message and call model (live) or submit batch."""
    system = _system_prompt(step_type, context)

    # Build messages for the API (exclude batch-pending placeholders)
    api_msgs = [
        {"role": m["role"], "content": m["content"]}
        for m in thread
        if ":batch:pending" not in m.get("model", "")
    ]
    api_msgs.append({"role": "user", "content": user_input})

    # Persist user message
    add_ai_message(node_id, step_type, "user", user_input, model="you")

    if mode == "⏳ Batch":
        try:
            from pipeline.llm import submit_batch
            submit_batch(node_id, step_type, model, api_msgs, system=system)
        except Exception as e:
            add_ai_message(node_id, step_type, "assistant", f"[Batch error: {e}]", model=model)
    else:
        try:
            from pipeline.llm import call_model
            response = call_model(model, api_msgs, system=system)
            add_ai_message(node_id, step_type, "assistant", response, model=model)
        except Exception as e:
            add_ai_message(node_id, step_type, "assistant", f"[Error: {e}]", model=model)


def _render_extractor(
    node_id: str,
    step_type: str,
    question_id: str = "",
    hypothesis_id: str = "",
) -> None:
    st.caption("**Extract from conversation**")

    all_models = _get_all_models()
    panel_key = f"{node_id}_{step_type}"

    ext_model = st.selectbox(
        "Extractor model",
        all_models if all_models else ["claude-sonnet-4-6"],
        key=f"ext_model_{panel_key}",
        format_func=_fmt_model,
        label_visibility="collapsed",
    )

    thread = get_ai_thread(node_id, step_type)
    if not thread:
        st.caption("Have a conversation first.")
        return

    # Extract buttons vary by context
    ext_results_key = f"ext_results_{panel_key}"
    ext_type_key = f"ext_type_{panel_key}"

    if step_type == "hypotheses":
        if st.button("⬇ Extract hypotheses", key=f"ext_{panel_key}", use_container_width=True):
            _do_extract(thread, "hypotheses", ext_model, ext_results_key, ext_type_key)

    elif step_type == "experiments":
        if st.button("⬇ Extract experiments", key=f"ext_{panel_key}", use_container_width=True):
            _do_extract(thread, "experiments", ext_model, ext_results_key, ext_type_key)

    elif step_type == "result_discussion":
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("Hyp.", key=f"ext_h_{panel_key}", use_container_width=True,
                         help="Extract hypotheses"):
                _do_extract(thread, "hypotheses", ext_model, ext_results_key, ext_type_key)
        with c2:
            if st.button("Exp.", key=f"ext_e_{panel_key}", use_container_width=True,
                         help="Extract experiments"):
                _do_extract(thread, "experiments", ext_model, ext_results_key, ext_type_key)
        with c3:
            if st.button("Q.", key=f"ext_q_{panel_key}", use_container_width=True,
                         help="Extract questions"):
                _do_extract(thread, "questions", ext_model, ext_results_key, ext_type_key)

    # Render extracted items
    if ext_results_key in st.session_state:
        results = st.session_state[ext_results_key]
        item_type = st.session_state.get(ext_type_key, "")

        # Handle categorised (items) or flat list
        if isinstance(results, dict):
            for cat, items in results.items():
                if items:
                    st.caption(f"**{cat.capitalize()}**")
                    _render_extracted_items(
                        items, cat, panel_key, node_id,
                        question_id, hypothesis_id,
                    )
        else:
            _render_extracted_items(
                results, item_type, panel_key, node_id,
                question_id, hypothesis_id,
            )


def _do_extract(
    thread: list[dict],
    extract_type: str,
    model: str,
    results_key: str,
    type_key: str,
) -> None:
    try:
        from pipeline.llm import extract_from_thread
        with st.spinner(f"Extracting {extract_type}…"):
            results = extract_from_thread(thread, extract_type, model)
        st.session_state[results_key] = results
        st.session_state[type_key] = extract_type
        st.rerun()
    except Exception as e:
        st.error(f"Extraction error: {e}")


def _render_extracted_items(
    items: list[str],
    item_type: str,
    panel_key: str,
    node_id: str,
    question_id: str,
    hypothesis_id: str,
) -> None:
    if not items:
        return

    results_key = f"ext_results_{panel_key}"

    # Per-item: checkbox + editable text area
    selected: list[bool] = []
    edited_items: list[str] = []
    for i, item in enumerate(items):
        col_cb, col_text = st.columns([1, 9])
        with col_cb:
            st.write("")  # vertical alignment nudge
            checked = st.checkbox(
                "sel", value=True,
                key=f"ext_chk_{panel_key}_{item_type}_{i}",
                label_visibility="collapsed",
            )
        with col_text:
            edited = st.text_area(
                f"#{i+1}",
                value=item,
                key=f"ext_edit_{panel_key}_{item_type}_{i}",
                height=68,
                label_visibility="collapsed",
            )
        selected.append(checked)
        edited_items.append(edited)

    n_sel = sum(selected)
    btn_label = {
        "hypotheses": f"Add selected hypotheses ({n_sel})",
        "experiments": f"Add selected experiments ({n_sel})",
        "questions":   f"Add selected questions ({n_sel})",
    }.get(item_type, f"Add selected ({n_sel})")

    if st.button(btn_label, key=f"add_sel_{panel_key}_{item_type}",
                 use_container_width=True, type="primary", disabled=(n_sel == 0)):
        for is_sel, edited in zip(selected, edited_items):
            if is_sel:
                _add_extracted_item(
                    title=edited,
                    item_type=item_type,
                    node_id=node_id,
                    question_id=question_id,
                    hypothesis_id=hypothesis_id,
                )
        remaining = [it for it, sel in zip(items, selected) if not sel]
        if remaining:
            st.session_state[results_key] = remaining
        else:
            st.session_state.pop(results_key, None)
        st.rerun()


def _add_extracted_item(
    title: str,
    item_type: str,
    node_id: str,
    question_id: str,
    hypothesis_id: str,
) -> None:
    if not title.strip():
        return
    if item_type == "hypotheses":
        new_id = add_node(type="hypothesis", title=title.strip(), status="pending")
        parent = question_id or node_id
        add_edge(parent, new_id, "has_hypothesis")
    elif item_type == "experiments":
        new_id = add_node(type="experiment", title=title.strip(), status="pending")
        parent = hypothesis_id or node_id
        add_edge(parent, new_id, "has_experiment")
    elif item_type == "questions":
        new_id = add_node(type="question", title=title.strip(), status="pending")
        add_edge(node_id, new_id, "branched_into")


# ─────────────────────────────────────────────────────────────────────────────
# LEVEL 0 — Questions list
# ─────────────────────────────────────────────────────────────────────────────
def page_questions() -> None:
    c_title, c_btn = st.columns([8, 2])
    with c_title:
        st.title("Research Questions")
    with c_btn:
        st.write("")
        if st.button("➕ New Question", use_container_width=True):
            st.session_state["show_new_q"] = not st.session_state.get("show_new_q", False)

    if st.session_state.get("show_new_q"):
        with st.form("new_q_form", clear_on_submit=True):
            title = st.text_input("Question:")
            content = st.text_area("Context (optional):", height=68)
            c1, c2 = st.columns([1, 5])
            with c1:
                submitted = st.form_submit_button("Add", type="primary")
            with c2:
                cancelled = st.form_submit_button("Cancel")
            if submitted and title.strip():
                add_node(type="question", title=title.strip(), content=content.strip())
                st.session_state.pop("show_new_q", None)
                st.rerun()
            if cancelled:
                st.session_state.pop("show_new_q", None)
                st.rerun()

    questions = get_nodes_by_type("question")
    if not questions:
        st.info("No questions yet. Add one above.")
        return

    # Sort: active first, deferred last
    questions.sort(key=lambda q: (q["status"] == "deferred", q["created_at"]))

    for q in questions:
        hyps = get_children_of_type(q["id"], "hypothesis")
        n_supported = sum(1 for h in hyps if h.get("verdict") == "supported")
        n_refuted   = sum(1 for h in hyps if h.get("verdict") == "refuted")
        n_open      = sum(1 for h in hyps if not h.get("verdict") or h.get("verdict") == "open")

        with st.container(border=True):
            c1, c2 = st.columns([9, 2])
            with c1:
                st.markdown(f"**{q['title']}**")
                badges = []
                if hyps:
                    badges.append(f"💡 {len(hyps)}")
                if n_supported:
                    badges.append(f"🟢 {n_supported}")
                if n_refuted:
                    badges.append(f"🔴 {n_refuted}")
                if n_open and hyps:
                    badges.append(f"🟡 {n_open} open")
                if not hyps:
                    badges.append("No hypotheses yet")
                st.caption("  ·  ".join(badges))
            with c2:
                if st.button("Explore →", key=f"q_{q['id']}", use_container_width=True):
                    _push(q["id"])


# ─────────────────────────────────────────────────────────────────────────────
# LEVEL 1 — Hypotheses for a question
# ─────────────────────────────────────────────────────────────────────────────
def page_hypotheses(question_id: str) -> None:
    question = get_node(question_id)
    if not question:
        st.error("Question not found.")
        return

    st.title("Hypotheses")
    st.markdown(f"**❓ {question['title']}**")
    if question.get("content"):
        st.info(question["content"])

    hypotheses = get_children_of_type(question_id, "hypothesis")

    # ── Existing hypotheses ───────────────────────────────────────────────
    c_list, c_add = st.columns([8, 2])
    with c_add:
        if st.button("➕ Add manually", use_container_width=True):
            st.session_state[f"show_add_hyp_{question_id}"] = not st.session_state.get(
                f"show_add_hyp_{question_id}", False
            )

    if st.session_state.get(f"show_add_hyp_{question_id}"):
        with st.form(f"add_hyp_form_{question_id}", clear_on_submit=True):
            title = st.text_input("Hypothesis statement:")
            content = st.text_area("Description:", height=68)
            c1, _ = st.columns([1, 5])
            with c1:
                submitted = st.form_submit_button("Add", type="primary")
            if submitted and title.strip():
                new_id = add_node(type="hypothesis", title=title.strip(), content=content.strip())
                add_edge(question_id, new_id, "has_hypothesis")
                st.session_state.pop(f"show_add_hyp_{question_id}", None)
                st.rerun()

    if not hypotheses:
        st.info("No hypotheses yet. Add manually or use the AI panel below.")
    else:
        for h in hypotheses:
            verdict = h.get("verdict") or "open"
            exps = get_children_of_type(h["id"], "experiment")
            n_done = sum(1 for e in exps if e["status"] == "completed")

            with st.container(border=True):
                c1, c2, c3 = st.columns([6, 2, 2])
                with c1:
                    st.markdown(f"**{h['title']}**")
                    info = f"🔬 {len(exps)} exp"
                    if exps:
                        info += f"  ·  {n_done} completed"
                    st.caption(info)
                with c2:
                    v_idx = VERDICT_OPTIONS.index(verdict) if verdict in VERDICT_OPTIONS else 0
                    new_v = st.selectbox(
                        "Verdict",
                        VERDICT_OPTIONS,
                        index=v_idx,
                        key=f"vrd_{h['id']}",
                        format_func=lambda x: VERDICT_LABEL[x],
                        label_visibility="collapsed",
                    )
                    if new_v != verdict:
                        update_verdict(h["id"], new_v)
                        st.rerun()
                with c3:
                    if st.button("Experiments →", key=f"h_{h['id']}", use_container_width=True):
                        _push(h["id"])

    # ── AI panel ──────────────────────────────────────────────────────────
    st.divider()
    if st.button("💬 Discuss hypotheses with AI →",
                 key=f"chat_btn_hyp_{question_id}"):
        _open_chat(
            node_id=question_id,
            step_type="hypotheses",
            title=question["title"],
            parent_type="question",
            question_id=question_id,
        )


# ─────────────────────────────────────────────────────────────────────────────
# LEVEL 2 — Experiments for a hypothesis
# ─────────────────────────────────────────────────────────────────────────────
def page_experiments(question_id: str, hypothesis_id: str) -> None:
    hypothesis = get_node(hypothesis_id)
    if not hypothesis:
        st.error("Hypothesis not found.")
        return

    verdict = hypothesis.get("verdict") or "open"
    st.title("Experiments")
    st.markdown(f"**💡 {hypothesis['title']}**")
    st.caption(VERDICT_LABEL.get(verdict, "🟡 Open"))
    if hypothesis.get("content"):
        st.info(hypothesis["content"])

    experiments = get_children_of_type(hypothesis_id, "experiment")

    c_list, c_add = st.columns([8, 2])
    with c_add:
        if st.button("➕ New Experiment", use_container_width=True):
            st.session_state[f"show_add_exp_{hypothesis_id}"] = not st.session_state.get(
                f"show_add_exp_{hypothesis_id}", False
            )

    if st.session_state.get(f"show_add_exp_{hypothesis_id}"):
        with st.form(f"add_exp_form_{hypothesis_id}", clear_on_submit=True):
            title    = st.text_input("Title:", placeholder="EXP002: Vary HDBSCAN min_cluster_size")
            content  = st.text_area("Description:", height=68)
            dataset  = st.text_input("Dataset(s):")
            script   = st.text_input("Script path (from xworld/):", placeholder="scripts/exp002.py")
            var_opts = {"(standalone)": None}
            var_opts.update({e["title"]: e["id"] for e in experiments})
            var_lbl  = st.selectbox("Variant of:", list(var_opts.keys()))
            var_id   = var_opts[var_lbl]
            c1, _ = st.columns([1, 5])
            with c1:
                submitted = st.form_submit_button("Add", type="primary")
            if submitted and title.strip():
                new_id = add_node(type="experiment", title=title.strip(), content=content.strip())
                add_edge(hypothesis_id, new_id, "has_experiment")
                if script.strip() or dataset.strip():
                    add_experiment(new_id, dataset=dataset.strip(), script_path=script.strip())
                if var_id:
                    add_edge(var_id, new_id, "modifies")
                st.session_state.pop(f"show_add_exp_{hypothesis_id}", None)
                st.rerun()

    st.divider()

    if not experiments:
        st.info("No experiments yet. Add one or use the AI panel below.")
    else:
        for exp_node in experiments:
            exp_detail = get_experiment(exp_node["id"])
            status_badge = STATUS_LABEL.get(exp_node["status"], "🟡 Pending")

            parents = get_parents(exp_node["id"])
            parent_exp = next((p for p in parents if p.get("edge_type") == "modifies"), None)

            with st.container(border=True):
                c1, c2, c3 = st.columns([6, 2, 2])
                with c1:
                    st.markdown(f"**🔬 {exp_node['title']}**")
                    meta = [status_badge]
                    if exp_detail and exp_detail.get("dataset"):
                        meta.append(f"📂 {exp_detail['dataset']}")
                    if parent_exp:
                        meta.append(f"↪ variant of *{parent_exp['title'][:25]}…*")
                    st.caption("  ·  ".join(meta))
                    if exp_detail and exp_detail.get("result_summary"):
                        rs = exp_detail["result_summary"]
                        st.caption(f"📊 {rs[:110]}{'…' if len(rs)>110 else ''}")
                with c2:
                    if exp_node["status"] == "pending" and exp_detail and exp_detail.get("script_path"):
                        if st.button("+ Queue", key=f"q_{exp_node['id']}", use_container_width=True):
                            enqueue(exp_node["id"])
                            st.success("Queued")
                            st.rerun()
                with c3:
                    if st.button("View →", key=f"e_{exp_node['id']}", use_container_width=True):
                        _push(exp_node["id"])

    # ── AI panel ──────────────────────────────────────────────────────────
    st.divider()
    if st.button("💬 Design experiments with AI →",
                 key=f"chat_btn_exp_{hypothesis_id}"):
        _open_chat(
            node_id=hypothesis_id,
            step_type="experiments",
            title=hypothesis["title"],
            parent_type="hypothesis",
            question_id=question_id,
            hypothesis_id=hypothesis_id,
        )


# ─────────────────────────────────────────────────────────────────────────────
# LEVEL 3 — Experiment detail + Result + Branch
# ─────────────────────────────────────────────────────────────────────────────
def page_experiment_detail(
    question_id: str, hypothesis_id: str, experiment_id: str
) -> None:
    exp_node = get_node(experiment_id)
    if not exp_node:
        st.error("Experiment not found.")
        return

    exp_detail = get_experiment(experiment_id)

    st.title(f"🔬 {exp_node['title']}")
    st.caption(STATUS_LABEL.get(exp_node["status"], ""))

    if exp_node.get("content"):
        st.info(exp_node["content"])

    # ── Metadata + queue action ───────────────────────────────────────────
    if exp_detail:
        c_meta, c_action = st.columns([7, 3])
        with c_meta:
            if exp_detail.get("dataset"):
                st.markdown(f"**Dataset:** {exp_detail['dataset']}")
            if exp_detail.get("script_path"):
                st.markdown(f"**Script:** `{exp_detail['script_path']}`")
            if exp_detail.get("parameters"):
                with st.expander("Parameters"):
                    st.json(exp_detail["parameters"])
        with c_action:
            if exp_node["status"] == "pending":
                if exp_detail.get("script_path"):
                    if st.button("▶ Add to Queue", type="primary", use_container_width=True):
                        enqueue(experiment_id)
                        st.success("Added to queue.")
                        st.rerun()
                else:
                    st.warning("No script path set.")
            elif exp_node["status"] == "running":
                st.info("🔵 Running…")
            elif exp_node["status"] == "completed":
                st.success("✅ Completed")

    # ── Result section ────────────────────────────────────────────────────
    st.subheader("📊 Result")
    has_result = exp_detail and (
        exp_detail.get("result_summary") or exp_detail.get("llm_interpretation")
    )

    if has_result:
        if exp_detail.get("result_summary"):
            st.markdown(exp_detail["result_summary"])

        if exp_detail.get("llm_interpretation"):
            with st.expander("🤖 Claude interpretation"):
                st.markdown(exp_detail["llm_interpretation"])

        if exp_detail.get("artifacts"):
            with st.expander("📁 Artifacts"):
                for rel_path in exp_detail["artifacts"]:
                    fp = Path(__file__).parent.parent / rel_path
                    if fp.exists():
                        ext = fp.suffix.lower()
                        if ext in (".png", ".jpg", ".jpeg", ".svg"):
                            st.image(str(fp), caption=fp.name)
                        elif ext == ".csv":
                            import pandas as pd
                            try:
                                st.dataframe(pd.read_csv(fp), use_container_width=True)
                            except Exception:
                                st.code(rel_path)
                        elif ext == ".html":
                            st.components.v1.html(fp.read_text(), height=400, scrolling=True)
                        else:
                            st.code(rel_path)
                    else:
                        st.caption(f"⚠ Not found: {rel_path}")

        # Legacy result/insight nodes
        old = [c for c in get_children(experiment_id) if c["type"] in ("result", "insight")]
        if old:
            with st.expander("Legacy result nodes"):
                for r in old:
                    icon = NODE_ICON.get(r["type"], "")
                    st.markdown(f"**{icon} {r['title']}**")
                    if r.get("content"):
                        st.markdown(r["content"])
    else:
        st.info("No result yet — queue and run this experiment first.")

    # ── What branched from here ───────────────────────────────────────────
    branches = [
        c for c in get_children(experiment_id)
        if c["type"] not in ("result", "insight")
    ]
    if branches:
        st.subheader("🌿 Branched from this experiment")
        for c in branches:
            icon = NODE_ICON.get(c["type"], "•")
            edge = c.get("edge_type", "")
            label = "modification" if edge == "modifies" else edge
            st.markdown(f"- {icon} **{c['title']}** · _{label}_")

    # ── Branch from here (manual) ─────────────────────────────────────────
    st.divider()
    st.subheader("Branch from here")

    tab1, tab2, tab3 = st.tabs([
        "🔬 New experiment",
        "💡 New hypothesis",
        "❓ New question",
    ])

    with tab1:
        st.caption("Add an experiment under the same hypothesis (variant or independent).")
        with st.form(f"branch_exp_{experiment_id}", clear_on_submit=True):
            title   = st.text_input("Title:", placeholder="EXP001_MOD001: Re-run with min_cluster_size=5")
            content = st.text_area("What changes?", height=68)
            dataset = st.text_input("Dataset:")
            script  = st.text_input("Script path:")
            is_var  = st.checkbox("Mark as variant of this experiment", value=True)
            c1, _ = st.columns([1, 5])
            with c1:
                if st.form_submit_button("Add", type="primary"):
                    if title.strip():
                        new_id = add_node(type="experiment", title=title.strip(), content=content.strip())
                        add_edge(hypothesis_id, new_id, "has_experiment")
                        if script.strip() or dataset.strip():
                            add_experiment(new_id, dataset=dataset.strip(), script_path=script.strip())
                        if is_var:
                            add_edge(experiment_id, new_id, "modifies")
                        st.success("Experiment added.")
                        st.rerun()

    with tab2:
        st.caption("A new hypothesis under the same question, inspired by this result.")
        with st.form(f"branch_hyp_{experiment_id}", clear_on_submit=True):
            title   = st.text_input("Hypothesis:")
            content = st.text_area("Description:", height=68)
            c1, _ = st.columns([1, 5])
            with c1:
                if st.form_submit_button("Add", type="primary"):
                    if title.strip():
                        new_id = add_node(type="hypothesis", title=title.strip(), content=content.strip())
                        add_edge(question_id, new_id, "has_hypothesis")
                        add_edge(experiment_id, new_id, "branched_into")
                        st.success("Hypothesis added.")
                        st.rerun()

    with tab3:
        st.caption("A new research question opened by this result.")
        with st.form(f"branch_q_{experiment_id}", clear_on_submit=True):
            title = st.text_input("Question:")
            c1, _ = st.columns([1, 5])
            with c1:
                if st.form_submit_button("Add", type="primary"):
                    if title.strip():
                        new_id = add_node(type="question", title=title.strip(), status="pending")
                        add_edge(experiment_id, new_id, "branched_into")
                        st.success("Question added.")
                        st.rerun()

    # ── AI panel: result discussion ───────────────────────────────────────
    st.divider()
    result_context = (exp_detail.get("result_summary") or exp_node["title"]) if exp_detail else exp_node["title"]
    if st.button("💬 Discuss result with AI →",
                 key=f"chat_btn_result_{experiment_id}"):
        _open_chat(
            node_id=experiment_id,
            step_type="result_discussion",
            title=exp_node["title"],
            parent_type="experiment",
            question_id=question_id,
            hypothesis_id=hypothesis_id,
        )


# ─────────────────────────────────────────────────────────────────────────────
# Queue page
# ─────────────────────────────────────────────────────────────────────────────
def page_queue() -> None:
    st.title("Experiment Queue")

    items = get_queue()
    if not items:
        st.info("Queue is empty.")
        return

    queued  = [i for i in items if i["status"] == "queued"]
    running = [i for i in items if i["status"] == "running"]
    done    = [i for i in items if i["status"] in ("done", "failed")]

    if running:
        st.subheader("🔵 Running")
        for item in running:
            with st.expander(f"🔬 {item['title']}"):
                st.caption(f"Started: {item.get('started_at', '')}")
                if item.get("run_output"):
                    st.code(item["run_output"][-2000:])

    if queued:
        st.subheader(f"🟡 Queued ({len(queued)})")
        for item in queued:
            with st.container(border=True):
                c1, c2 = st.columns([8, 2])
                with c1:
                    icon = NODE_ICON.get(item["type"], "•")
                    st.markdown(f"{icon} **{item['title']}**")
                    if item.get("notes"):
                        st.caption(item["notes"])
                with c2:
                    st.caption(f"Priority: {item['priority']}")

        st.divider()
        next_item = get_next_queued()
        if next_item:
            st.markdown(f"**Next:** {NODE_ICON.get(next_item['type'],'')} {next_item['title']}")
        if st.button("▶ Run Next", type="primary"):
            with st.spinner("Running experiment…"):
                from pipeline.runner import run_next
                result = run_next()
            if result["status"] == "done":
                st.success("Done.")
                with st.expander("Output"):
                    st.code(result.get("output", "")[-3000:])
            elif result["status"] == "failed":
                st.error("Failed.")
                with st.expander("Output / error"):
                    st.code(result.get("output", "")[-3000:])
            else:
                st.warning(result.get("message", ""))
            st.rerun()

    if done:
        with st.expander(f"Completed / Failed ({len(done)})"):
            for item in done:
                icon = "✅" if item["status"] == "done" else "❌"
                with st.expander(f"{icon} {item['title']}"):
                    st.caption(f"Completed: {item.get('completed_at', '')}")
                    if item.get("run_output"):
                        st.code(item["run_output"][-2000:])


# ─────────────────────────────────────────────────────────────────────────────
# Settings page
# ─────────────────────────────────────────────────────────────────────────────
def page_settings() -> None:
    st.title("Settings")

    st.subheader("Claude API")
    current_key = get_setting("claude_api_key", "")
    masked = ("sk-…" + current_key[-6:]) if len(current_key) > 6 else ("set" if current_key else "not set")
    st.caption(f"Current key: `{masked}`")
    new_key = st.text_input("Claude API Key:", type="password", placeholder="sk-ant-…")
    if st.button("Save API Key"):
        if new_key.strip():
            set_setting("claude_api_key", new_key.strip())
            st.success("Saved.")

    st.divider()
    st.subheader("Models")

    reason_model = st.selectbox(
        "Default Claude model:",
        ["claude-sonnet-4-6", "claude-opus-4-6", "claude-haiku-4-5-20251001"],
        index=0,
    )
    if st.button("Save Claude model"):
        set_setting("claude_reason_model", reason_model)
        st.success("Saved.")

    ollama_url = st.text_input(
        "Ollama base URL:",
        value=get_setting("ollama_base_url", "http://localhost:11434"),
    )
    if st.button("Save Ollama URL"):
        set_setting("ollama_base_url", ollama_url.strip())
        st.success("Saved.")

    summary_model = st.text_input(
        "Ollama summarisation model:",
        value=get_setting("ollama_summary_model", "qwen2.5:latest"),
    )
    if st.button("Save Ollama model"):
        set_setting("ollama_summary_model", summary_model.strip())
        st.success("Saved.")

    st.divider()
    st.subheader("Ollama connectivity")
    if st.button("Test Ollama connection"):
        try:
            import httpx
            url = get_setting("ollama_base_url", "http://localhost:11434")
            resp = httpx.get(f"{url}/api/tags", timeout=5)
            models = [m["name"] for m in resp.json().get("models", [])]
            st.success(f"Connected. Models: {', '.join(models)}")
        except Exception as e:
            st.error(f"Cannot reach Ollama: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# Chat window (full-page conversation)
# ─────────────────────────────────────────────────────────────────────────────
def page_chat(chat: dict) -> None:
    node_id      = chat["node_id"]
    step_type    = chat["step_type"]
    title        = chat["title"]
    parent_type  = chat.get("parent_type", "")
    question_id  = chat.get("question_id", "")
    hypothesis_id = chat.get("hypothesis_id", "")

    STEP_LABEL = {
        "hypotheses":        ("💡", "Hypothesis generation"),
        "experiments":       ("🔬", "Experiment design"),
        "result_discussion": ("📊", "Result discussion"),
    }
    icon, label = STEP_LABEL.get(step_type, ("💬", "Discussion"))
    parent_icon = NODE_ICON.get(parent_type, "")

    # ── Header ────────────────────────────────────────────────────────────
    c_back, c_title = st.columns([1, 10])
    with c_back:
        if st.button("← Back", key="chat_back"):
            st.session_state.pop("chat", None)
            st.rerun()
    with c_title:
        st.markdown(f"### {icon} {label}")
        st.caption(f"{parent_icon} **{title}**")
    st.divider()

    # ── Full-page AI panel ────────────────────────────────────────────────
    _render_ai_panel(
        node_id=node_id,
        step_type=step_type,
        context=title,
        question_id=question_id,
        hypothesis_id=hypothesis_id,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Main router
# ─────────────────────────────────────────────────────────────────────────────
if "chat" in st.session_state:
    page_chat(st.session_state["chat"])
elif page == "❓ Questions":
    stack = _stack()
    _breadcrumb(stack)

    if len(stack) == 0:
        page_questions()
    elif len(stack) == 1:
        page_hypotheses(stack[0])
    elif len(stack) == 2:
        page_experiments(stack[0], stack[1])
    else:
        page_experiment_detail(stack[0], stack[1], stack[2])

elif page == "📋 Queue":
    page_queue()

elif page == "⚙️ Settings":
    page_settings()
