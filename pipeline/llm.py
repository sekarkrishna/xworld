"""
pipeline/llm.py
Unified model router for XWorld.
  - call_model(model, messages, system)  →  routes to Claude or Ollama
  - submit_batch(...)                    →  Claude Batch API, stores in DB
  - check_pending_batches()              →  polls Anthropic, resolves pending
  - get_available_ollama_models()        →  live list from /api/tags
Convenience wrappers (generate_hypotheses, interpret_result, etc.) are kept
for backwards compat but now all go through call_model.
"""
from __future__ import annotations

import json
from pathlib import Path
from pipeline.graph import (
    get_setting,
    add_ai_request,
    update_ai_request,
    add_ai_message,
    get_pending_batches,
)

CLAUDE_MODELS = [
    "claude-sonnet-4-6",
    "claude-opus-4-6",
    "claude-haiku-4-5-20251001",
]


# ---------------------------------------------------------------------------
# Model discovery
# ---------------------------------------------------------------------------

def get_available_ollama_models() -> list[str]:
    """Return model names currently available in Ollama. Empty list on failure."""
    try:
        import httpx
        url = get_setting("ollama_base_url", "http://localhost:11434")
        resp = httpx.get(f"{url}/api/tags", timeout=5)
        resp.raise_for_status()
        return [m["name"] for m in resp.json().get("models", [])]
    except Exception:
        return []


def get_all_models() -> list[str]:
    """Claude models first, then available Ollama models."""
    return CLAUDE_MODELS + get_available_ollama_models()


# ---------------------------------------------------------------------------
# Unified call_model
# ---------------------------------------------------------------------------

def call_model(
    model: str,
    messages: list[dict],
    system: str = "",
    max_tokens: int = 2048,
) -> str:
    """
    Send messages to any model and return the response text.
    messages: list of {"role": "user"|"assistant", "content": "..."}
    Routing: claude-* → Anthropic API, anything else → Ollama /api/chat
    """
    if model.startswith("claude"):
        return _call_claude(model, messages, system=system, max_tokens=max_tokens)
    else:
        return _call_ollama(model, messages, system=system)


def _call_claude(
    model: str,
    messages: list[dict],
    system: str = "",
    max_tokens: int = 2048,
) -> str:
    client = _claude_client()
    kwargs: dict = dict(model=model, max_tokens=max_tokens, messages=messages)
    if system:
        kwargs["system"] = system
    msg = client.messages.create(**kwargs)
    return msg.content[0].text.strip()


def _call_ollama(
    model: str,
    messages: list[dict],
    system: str = "",
) -> str:
    import httpx
    url = get_setting("ollama_base_url", "http://localhost:11434")
    full_messages = []
    if system:
        full_messages.append({"role": "system", "content": system})
    full_messages.extend(messages)
    resp = httpx.post(
        f"{url}/api/chat",
        json={"model": model, "messages": full_messages, "stream": False},
        timeout=180,
    )
    resp.raise_for_status()
    return resp.json()["message"]["content"].strip()


# ---------------------------------------------------------------------------
# Batch API (Claude only)
# ---------------------------------------------------------------------------

def submit_batch(
    node_id: str,
    step_type: str,
    model: str,
    messages: list[dict],
    system: str = "",
) -> str:
    """
    Submit a Claude Batch API request.
    Stores the batch_id in ai_requests and adds a placeholder ai_message.
    Returns the batch_id.
    """
    if not model.startswith("claude"):
        raise ValueError(f"Batch API only supported for Claude models, got: {model}")

    client = _claude_client()

    params: dict = {
        "model": model,
        "max_tokens": 2048,
        "messages": messages,
    }
    if system:
        params["system"] = system

    batch = client.messages.batches.create(
        requests=[{"custom_id": f"{node_id}_{step_type}", "params": params}]
    )
    batch_id = batch.id

    # Persist in DB
    add_ai_request(node_id=node_id, step_type=step_type, model=model, batch_id=batch_id)
    add_ai_message(
        node_id=node_id,
        step_type=step_type,
        role="assistant",
        content=f"[Batch submitted — ID: {batch_id}]",
        model=f"{model}:batch:pending",
    )
    return batch_id


def check_pending_batches() -> list[dict]:
    """
    Poll Anthropic for all pending batches. Resolve completed ones.
    Returns list of resolved items: {"batch_id", "status", "response"}.
    """
    pending = get_pending_batches()
    if not pending:
        return []

    client = _claude_client()
    resolved = []

    for req in pending:
        batch_id = req["batch_id"]
        try:
            batch = client.messages.batches.retrieve(batch_id)
            if batch.processing_status != "ended":
                continue

            # Collect result
            response_text = ""
            for result in client.messages.batches.results(batch_id):
                if result.result.type == "succeeded":
                    response_text = result.result.message.content[0].text.strip()
                    break
                else:
                    response_text = f"[Batch failed: {result.result.type}]"

            update_ai_request(req["id"], status="done", response=response_text)

            # Update the placeholder message in the thread
            from pipeline.graph import _conn, _now
            with _conn() as conn:
                conn.execute(
                    """
                    UPDATE ai_messages
                    SET content=?, model=?
                    WHERE node_id=? AND step_type=? AND model LIKE '%:batch:pending'
                    ORDER BY created_at DESC
                    LIMIT 1
                    """,
                    (response_text, req["model"], req["node_id"], req["step_type"]),
                )

            resolved.append({
                "batch_id": batch_id,
                "node_id": req["node_id"],
                "step_type": req["step_type"],
                "response": response_text,
            })

        except Exception as e:
            update_ai_request(req["id"], status="failed", response=str(e))

    return resolved


# ---------------------------------------------------------------------------
# Extraction helpers
# ---------------------------------------------------------------------------

def extract_from_thread(
    thread: list[dict],
    extract_type: str,
    model: str,
) -> list[str] | dict[str, list[str]]:
    """
    extract_type: "hypotheses" | "experiments" | "questions" | "items" (all three)
    Returns list[str] for single types, dict for "items".
    """
    thread_text = _format_thread(thread)
    prompt = _load_prompt(f"extract_{extract_type}").format(thread=thread_text)
    response = call_model(model, [{"role": "user", "content": prompt}])

    if extract_type == "items":
        return _parse_categorised(response)
    return _parse_numbered_list(response)


def _format_thread(thread: list[dict]) -> str:
    lines = []
    for msg in thread:
        if ":batch:pending" in msg.get("model", ""):
            continue
        role = "You" if msg["role"] == "user" else msg.get("model", "AI")
        lines.append(f"{role}: {msg['content']}")
    return "\n\n".join(lines)


def _parse_categorised(text: str) -> dict[str, list[str]]:
    """Parse the extract_items response into {hypotheses: [], experiments: [], questions: []}."""
    result: dict[str, list[str]] = {"hypotheses": [], "experiments": [], "questions": []}
    current: str | None = None
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        lower = line.lower()
        if lower.startswith("hypothes"):
            current = "hypotheses"
        elif lower.startswith("experiment"):
            current = "experiments"
        elif lower.startswith("question"):
            current = "questions"
        elif current:
            import re
            m = re.match(r"^\d+[.)]\s+(.*)", line)
            if m:
                result[current].append(m.group(1).strip())
            elif line.startswith("- "):
                result[current].append(line[2:].strip())
    return result


# ---------------------------------------------------------------------------
# Convenience wrappers (backwards compat)
# ---------------------------------------------------------------------------

def generate_hypotheses(question: str, context: str = "", n: int = 4) -> list[str]:
    model = _claude_model()
    prompt = _load_prompt("generate_hypotheses").format(
        question=question, context=context, n=n
    )
    response = call_model(model, [{"role": "user", "content": prompt}])
    return _parse_numbered_list(response)


def interpret_result(result_summary: str, experiment_context: str = "") -> str:
    model = _claude_model()
    prompt = _load_prompt("interpret_result").format(
        result_summary=result_summary, context=experiment_context
    )
    return call_model(model, [{"role": "user", "content": prompt}])


def generate_branches(result_summary: str, current_taxonomy: str = "", n: int = 4) -> list[str]:
    model = _claude_model()
    prompt = _load_prompt("generate_branches").format(
        result_summary=result_summary, taxonomy=current_taxonomy, n=n
    )
    response = call_model(model, [{"role": "user", "content": prompt}])
    return _parse_numbered_list(response)


def summarize_result(text: str) -> str:
    """Ollama summarisation of raw script output."""
    model = get_setting("ollama_summary_model", "qwen2.5:latest")
    prompt = (
        "Summarise the following experiment output in 3-5 sentences. "
        "Focus on what was found, what was unexpected, and what it implies.\n\n"
        f"{text}"
    )
    try:
        return _call_ollama(model, [{"role": "user", "content": prompt}])
    except Exception as e:
        return f"[Summarisation failed: {e}]"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _claude_client():
    try:
        import anthropic
    except ImportError:
        raise RuntimeError("anthropic package not installed — run: uv add anthropic")
    api_key = get_setting("claude_api_key")
    if not api_key:
        raise RuntimeError("Claude API key not set. Go to Settings.")
    return anthropic.Anthropic(api_key=api_key)


def _claude_model() -> str:
    return get_setting("claude_reason_model", "claude-sonnet-4-6")


def _load_prompt(name: str) -> str:
    p = Path(__file__).parent.parent / "prompts" / f"{name}.txt"
    if p.exists():
        return p.read_text()
    return _fallback_prompts().get(name, "{question}")


def _parse_numbered_list(text: str) -> list[str]:
    import re
    lines = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        m = re.match(r"^\d+[.)]\s+(.*)", line)
        if m:
            lines.append(m.group(1).strip())
        elif line.startswith("- ") or line.startswith("* "):
            lines.append(line[2:].strip())
    return lines if lines else [text.strip()]


def _fallback_prompts() -> dict[str, str]:
    return {
        "generate_hypotheses": (
            "You are assisting a cross-domain time series shape clustering experiment called XWorld.\n"
            "Core hypothesis: time series from unrelated domains share underlying dynamic shapes "
            "detectable by 5 features (skewness, kurtosis, lag1_autocorr, zero_crossings, slope) "
            "plus UMAP + HDBSCAN clustering.\n\n"
            "Research question: {question}\n\nAdditional context: {context}\n\n"
            "Generate exactly {n} specific, testable hypotheses. Number them 1 to {n}. "
            "Each hypothesis: one sentence stating a predicted outcome."
        ),
        "interpret_result": (
            "You are interpreting results from the XWorld cross-domain time series clustering experiment.\n"
            "5-feature set: skewness, kurtosis, lag1_autocorr, zero_crossings, slope.\n"
            "Clustering: UMAP(n_neighbors=15, min_dist=0.1) + HDBSCAN(min_cluster_size=8, min_samples=3).\n\n"
            "Experiment context: {context}\n\nResult: {result_summary}\n\n"
            "Interpret in 2-3 paragraphs: what does it mean for the XWorld hypothesis? "
            "What does it reveal about the feature set? What is surprising?"
        ),
        "generate_branches": (
            "You are generating follow-up research questions for the XWorld experiment.\n"
            "Current shape taxonomy: {taxonomy}\n\nLatest result: {result_summary}\n\n"
            "Generate exactly {n} branching questions. Number them 1 to {n}. "
            "Each: one sentence. Prioritise questions that confirm, refute, or extend the taxonomy."
        ),
    }
