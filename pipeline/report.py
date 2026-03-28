"""
pipeline/report.py
MkDocs report generation for completed hypotheses.

Generates structured markdown pages for hypotheses with terminal verdicts,
copies artifacts, updates mkdocs.yml navigation, and generates an index page.
"""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).parent.parent
DOCS_DIR = ROOT / "docs"
ASSETS_DIR = DOCS_DIR / "assets"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _slugify(text: str) -> str:
    """Convert text to a URL-safe slug."""
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60]


def _build_report_markdown(
    hypothesis: dict,
    question: dict | None,
    experiment_sections: list[str],
) -> str:
    """Build the full markdown content for a hypothesis report page."""
    lines: list[str] = []

    # Title
    lines.append(f"# {hypothesis['title']}\n")

    # Verdict
    verdict = hypothesis.get("verdict") or "open"
    verdict_emoji = {
        "supported": "🟢", "refuted": "🔴", "inconclusive": "🟡",
        "open": "⚪", "deferred": "🔵",
    }.get(verdict, "⚪")
    lines.append(f"**Verdict:** {verdict_emoji} {verdict}\n")

    # Parent question
    if question:
        lines.append(f"**Research Question:** {question['title']}\n")

    # Hypothesis statement
    if hypothesis.get("content"):
        lines.append("## Hypothesis Statement\n")
        lines.append(f"{hypothesis['content']}\n")

    # Experiments
    if experiment_sections:
        lines.append("## Experiments\n")
        for section in experiment_sections:
            lines.append(section)
            lines.append("")

    # Verdict justification
    lines.append("## Verdict Justification\n")
    lines.append(
        f"Based on the experimental evidence above, this hypothesis has been "
        f"marked as **{verdict}**.\n"
    )

    return "\n".join(lines)


def _render_experiment_section(
    exp_node: dict,
    exp_data: dict | None,
    question_slug: str,
    hypothesis_slug: str,
) -> tuple[str, list[tuple[str, str]]]:
    """Render a single experiment as a markdown section.

    Returns (markdown_text, list_of_(source_path, dest_name) artifact refs).
    """
    lines: list[str] = []
    artifact_refs: list[tuple[str, str]] = []

    lines.append(f"### {exp_node['title']}\n")

    # Status
    status = exp_node.get("status") or "pending"
    lines.append(f"**Status:** {status}\n")

    # Parameters
    if exp_data and exp_data.get("parameters"):
        params = exp_data["parameters"]
        if isinstance(params, str):
            try:
                params = json.loads(params)
            except (json.JSONDecodeError, TypeError):
                params = {}
        if params:
            lines.append("**Parameters:**\n")
            for k, v in params.items():
                lines.append(f"- `{k}`: `{v}`")
            lines.append("")

    # Methodology
    if exp_node.get("content"):
        lines.append(f"**Methodology:** {exp_node['content']}\n")

    # Result summary
    if exp_data and exp_data.get("result_summary"):
        lines.append("**Result:**\n")
        summary = exp_data["result_summary"]
        try:
            parsed = json.loads(summary)
            if isinstance(parsed, dict):
                lines.append(f"{parsed.get('summary', summary)}\n")
                metrics = parsed.get("metrics", {})
                if metrics:
                    lines.append("| Metric | Value |")
                    lines.append("|--------|-------|")
                    for mk, mv in metrics.items():
                        lines.append(f"| {mk} | {mv} |")
                    lines.append("")
            else:
                lines.append(f"{summary}\n")
        except (json.JSONDecodeError, TypeError):
            lines.append(f"{summary}\n")

    # LLM interpretation
    if exp_data and exp_data.get("llm_interpretation"):
        lines.append(f"**Interpretation:** {exp_data['llm_interpretation']}\n")

    # Artifacts
    if exp_data and exp_data.get("artifact_paths"):
        art_paths = exp_data["artifact_paths"]
        if isinstance(art_paths, str):
            try:
                art_paths = json.loads(art_paths)
            except (json.JSONDecodeError, TypeError):
                art_paths = []
        if art_paths:
            lines.append("**Artifacts:**\n")
            for art in art_paths:
                art_path = Path(art)
                if art_path.suffix.lower() in {".png", ".jpg", ".jpeg", ".svg", ".gif"}:
                    dest_name = f"{hypothesis_slug}_{art_path.name}"
                    artifact_refs.append((art, dest_name))
                    lines.append(f"![{art_path.name}](../../assets/{dest_name})\n")
                else:
                    lines.append(f"- `{art_path.name}`")

    return "\n".join(lines), artifact_refs



# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_hypothesis_report(hypothesis_node_id: str) -> str:
    """Generate a MkDocs markdown page for a completed hypothesis.

    Returns the relative path to the generated file.
    """
    from pipeline.graph import get_node, get_parents, get_children, get_experiment

    hyp = get_node(hypothesis_node_id)
    if not hyp:
        raise ValueError(f"Node {hypothesis_node_id} not found")

    # Find parent question
    parents = get_parents(hypothesis_node_id)
    question = None
    for p in parents:
        node = get_node(p["id"])
        if node and node["type"] == "question":
            question = node
            break

    question_slug = _slugify(question["title"]) if question else "unknown"
    hypothesis_slug = _slugify(hyp["title"])

    # Collect experiments
    children = get_children(hypothesis_node_id)
    experiment_sections: list[str] = []
    artifact_refs: list[tuple[str, str]] = []

    for child_edge in children:
        exp_node = get_node(child_edge["to_node"])
        if not exp_node or exp_node["type"] != "experiment":
            continue
        exp_data = get_experiment(exp_node["id"])
        section, refs = _render_experiment_section(
            exp_node, exp_data, question_slug, hypothesis_slug
        )
        experiment_sections.append(section)
        artifact_refs.extend(refs)

    # Copy artifacts to docs/assets/
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    for src, dest_name in artifact_refs:
        src_path = ROOT / src
        if src_path.exists():
            shutil.copy2(src_path, ASSETS_DIR / dest_name)

    # Build markdown
    md = _build_report_markdown(hyp, question, experiment_sections)

    # Write file
    report_dir = DOCS_DIR / "questions" / question_slug / "hypotheses"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / f"{hypothesis_slug}.md"
    report_path.write_text(md)

    # Update mkdocs.yml nav
    _update_mkdocs_nav(
        question_slug,
        question["title"] if question else "Unknown",
        hypothesis_slug,
        hyp["title"],
    )

    # Regenerate index
    generate_index()

    return str(report_path.relative_to(ROOT))


def generate_index() -> None:
    """Generate docs/index.md summarising all questions and hypothesis verdicts."""
    from pipeline.graph import get_nodes_by_type, get_children, get_node

    questions = get_nodes_by_type("question")
    lines = ["# XWorld Research Log\n"]

    for q in questions:
        lines.append(f"## {q['title']}\n")
        children = get_children(q["id"])
        for edge in children:
            child = get_node(edge["to_node"])
            if child and child["type"] == "hypothesis":
                verdict = child.get("verdict") or "open"
                badge = {
                    "supported": "🟢", "refuted": "🔴", "inconclusive": "🟡",
                    "open": "⚪", "deferred": "🔵",
                }.get(verdict, "⚪")
                slug_q = _slugify(q["title"])
                slug_h = _slugify(child["title"])
                if verdict in ("supported", "refuted"):
                    lines.append(
                        f"- {badge} [{child['title']}](questions/{slug_q}/hypotheses/{slug_h}.md) — {verdict}"
                    )
                else:
                    lines.append(f"- {badge} {child['title']} — {verdict}")
        lines.append("")

    index_path = DOCS_DIR / "index.md"
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    index_path.write_text("\n".join(lines))


def _update_mkdocs_nav(
    question_slug: str,
    question_title: str,
    hypothesis_slug: str,
    hypothesis_title: str,
) -> None:
    """Add the report page to mkdocs.yml nav if not already present (idempotent)."""
    import yaml

    mkdocs_path = DOCS_DIR / "mkdocs.yml"
    if mkdocs_path.exists():
        config = yaml.safe_load(mkdocs_path.read_text()) or {}
    else:
        config = {}

    nav = config.get("nav", [{"Home": "index.md"}])
    page_path = f"questions/{question_slug}/hypotheses/{hypothesis_slug}.md"

    # Check if already present (idempotent)
    for entry in nav:
        if isinstance(entry, dict):
            for v in entry.values():
                if isinstance(v, list):
                    for sub in v:
                        if isinstance(sub, dict) and page_path in sub.values():
                            return
                elif v == page_path:
                    return

    # Add under question section
    question_section = None
    for entry in nav:
        if isinstance(entry, dict) and question_title in entry:
            question_section = entry[question_title]
            break

    if question_section is None:
        question_section = []
        nav.append({question_title: question_section})

    question_section.append({hypothesis_title: page_path})
    config["nav"] = nav
    mkdocs_path.write_text(yaml.dump(config, default_flow_style=False))
