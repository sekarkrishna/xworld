"""
pipeline/graph.py
SQLite knowledge graph — all read/write operations for xworld.db
"""
import sqlite3
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "xworld.db"


def _conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _uid() -> str:
    return str(uuid.uuid4())


# ---------------------------------------------------------------------------
# Schema initialisation
# ---------------------------------------------------------------------------

SCHEMA = """
CREATE TABLE IF NOT EXISTS nodes (
    id          TEXT PRIMARY KEY,
    type        TEXT NOT NULL,
    title       TEXT NOT NULL,
    content     TEXT,
    status      TEXT DEFAULT 'pending',
    created_at  TEXT DEFAULT (datetime('now')),
    updated_at  TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS edges (
    id          TEXT PRIMARY KEY,
    from_node   TEXT REFERENCES nodes(id),
    to_node     TEXT REFERENCES nodes(id),
    edge_type   TEXT NOT NULL,
    created_at  TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS experiments (
    id                  TEXT PRIMARY KEY,
    node_id             TEXT REFERENCES nodes(id),
    dataset             TEXT,
    script_path         TEXT,
    parameters_json     TEXT,
    artifact_paths      TEXT,
    result_summary      TEXT,
    llm_interpretation  TEXT,
    created_at          TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS decisions (
    id                TEXT PRIMARY KEY,
    fork_node         TEXT REFERENCES nodes(id),
    chosen_branch     TEXT REFERENCES nodes(id),
    deferred_branches TEXT,
    reason            TEXT,
    decided_at        TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS queue (
    id            TEXT PRIMARY KEY,
    node_id       TEXT REFERENCES nodes(id),
    priority      INTEGER DEFAULT 0,
    status        TEXT DEFAULT 'queued',
    notes         TEXT,
    run_output    TEXT,
    queued_at     TEXT DEFAULT (datetime('now')),
    started_at    TEXT,
    completed_at  TEXT
);

CREATE TABLE IF NOT EXISTS settings (
    key         TEXT PRIMARY KEY,
    value       TEXT,
    updated_at  TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS ai_messages (
    id          TEXT PRIMARY KEY,
    node_id     TEXT REFERENCES nodes(id),
    step_type   TEXT NOT NULL,
    role        TEXT NOT NULL,
    content     TEXT NOT NULL,
    model       TEXT DEFAULT '',
    created_at  TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS ai_requests (
    id           TEXT PRIMARY KEY,
    node_id      TEXT REFERENCES nodes(id),
    step_type    TEXT NOT NULL,
    model        TEXT NOT NULL,
    prompt       TEXT DEFAULT '',
    response     TEXT DEFAULT '',
    status       TEXT DEFAULT 'pending',
    batch_id     TEXT DEFAULT '',
    created_at   TEXT DEFAULT (datetime('now')),
    completed_at TEXT DEFAULT ''
);
"""


def init_db() -> None:
    with _conn() as conn:
        conn.executescript(SCHEMA)
    # Idempotent column migrations
    conn2 = sqlite3.connect(DB_PATH)
    try:
        conn2.execute("ALTER TABLE nodes ADD COLUMN verdict TEXT")
        conn2.commit()
    except sqlite3.OperationalError:
        pass
    finally:
        conn2.close()

    # Idempotent index migrations for query performance
    with _conn() as conn:
        conn.execute("CREATE INDEX IF NOT EXISTS idx_nodes_type ON nodes(type)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_nodes_status ON nodes(status)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_nodes_verdict ON nodes(verdict)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_edges_from_node ON edges(from_node)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_edges_to_node ON edges(to_node)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_queue_status ON queue(status)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_queue_priority ON queue(priority)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_experiments_node_id ON experiments(node_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_ai_messages_node_step ON ai_messages(node_id, step_type)")


# ---------------------------------------------------------------------------
# Nodes
# ---------------------------------------------------------------------------

def add_node(
    type: str,
    title: str,
    content: str = "",
    status: str = "pending",
    node_id: str | None = None,
) -> str:
    uid = node_id or _uid()
    with _conn() as conn:
        conn.execute(
            "INSERT INTO nodes (id, type, title, content, status, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (uid, type, title, content, status, _now(), _now()),
        )
    return uid


def update_node_status(node_id: str, status: str) -> None:
    with _conn() as conn:
        conn.execute(
            "UPDATE nodes SET status=?, updated_at=? WHERE id=?",
            (status, _now(), node_id),
        )


def get_node(node_id: str) -> dict | None:
    with _conn() as conn:
        row = conn.execute("SELECT * FROM nodes WHERE id=?", (node_id,)).fetchone()
    return dict(row) if row else None


def get_all_nodes() -> list[dict]:
    with _conn() as conn:
        rows = conn.execute("SELECT * FROM nodes ORDER BY created_at").fetchall()
    return [dict(r) for r in rows]


def get_nodes_by_type(type: str) -> list[dict]:
    with _conn() as conn:
        rows = conn.execute(
            "SELECT * FROM nodes WHERE type=? ORDER BY created_at", (type,)
        ).fetchall()
    return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# Edges
# ---------------------------------------------------------------------------

def add_edge(from_node: str, to_node: str, edge_type: str) -> str:
    uid = _uid()
    with _conn() as conn:
        conn.execute(
            "INSERT INTO edges (id, from_node, to_node, edge_type, created_at) VALUES (?, ?, ?, ?, ?)",
            (uid, from_node, to_node, edge_type, _now()),
        )
    return uid


def get_children(node_id: str) -> list[dict]:
    with _conn() as conn:
        rows = conn.execute(
            """
            SELECT n.*, e.edge_type
            FROM nodes n
            JOIN edges e ON e.to_node = n.id
            WHERE e.from_node = ?
            ORDER BY n.created_at
            """,
            (node_id,),
        ).fetchall()
    return [dict(r) for r in rows]


def get_parents(node_id: str) -> list[dict]:
    with _conn() as conn:
        rows = conn.execute(
            """
            SELECT n.*, e.edge_type
            FROM nodes n
            JOIN edges e ON e.from_node = n.id
            WHERE e.to_node = ?
            ORDER BY n.created_at
            """,
            (node_id,),
        ).fetchall()
    return [dict(r) for r in rows]


def get_edges_for_node(node_id: str) -> list[dict]:
    with _conn() as conn:
        rows = conn.execute(
            "SELECT * FROM edges WHERE from_node=? OR to_node=?",
            (node_id, node_id),
        ).fetchall()
    return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# Tree structure (for UI)
# ---------------------------------------------------------------------------

def get_roots() -> list[dict]:
    """Nodes with no parents."""
    with _conn() as conn:
        rows = conn.execute(
            """
            SELECT * FROM nodes
            WHERE id NOT IN (SELECT to_node FROM edges)
            ORDER BY created_at
            """
        ).fetchall()
    return [dict(r) for r in rows]


def build_tree(node_id: str, depth: int = 0, _visited: set | None = None) -> dict:
    if _visited is None:
        _visited = set()
    node = get_node(node_id)
    if not node:
        return {}
    node["depth"] = depth
    node["children"] = []
    if node_id in _visited:
        # Already rendered elsewhere in the tree — show as a reference stub
        node["_ref"] = True
        return node
    _visited.add(node_id)
    for child in get_children(node_id):
        node["children"].append(build_tree(child["id"], depth + 1, _visited))
    return node


# ---------------------------------------------------------------------------
# Experiments
# ---------------------------------------------------------------------------

def add_experiment(
    node_id: str,
    dataset: str = "",
    script_path: str = "",
    parameters: dict | None = None,
    artifact_paths: list | None = None,
    result_summary: str = "",
    llm_interpretation: str = "",
) -> str:
    uid = _uid()
    with _conn() as conn:
        conn.execute(
            """
            INSERT INTO experiments
            (id, node_id, dataset, script_path, parameters_json, artifact_paths,
             result_summary, llm_interpretation, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                uid, node_id, dataset, script_path,
                json.dumps(parameters or {}),
                json.dumps(artifact_paths or []),
                result_summary, llm_interpretation, _now(),
            ),
        )
    return uid


def get_experiment(node_id: str) -> dict | None:
    with _conn() as conn:
        row = conn.execute(
            "SELECT * FROM experiments WHERE node_id=? ORDER BY created_at DESC LIMIT 1",
            (node_id,),
        ).fetchone()
    if not row:
        return None
    d = dict(row)
    d["parameters"] = json.loads(d["parameters_json"] or "{}")
    d["artifacts"] = json.loads(d["artifact_paths"] or "[]")
    return d


def update_experiment_results(
    node_id: str,
    result_summary: str,
    llm_interpretation: str,
    artifact_paths: list | None = None,
) -> None:
    with _conn() as conn:
        if artifact_paths is not None:
            conn.execute(
                """
                UPDATE experiments
                SET result_summary=?, llm_interpretation=?, artifact_paths=?
                WHERE node_id=?
                """,
                (result_summary, llm_interpretation, json.dumps(artifact_paths), node_id),
            )
        else:
            conn.execute(
                "UPDATE experiments SET result_summary=?, llm_interpretation=? WHERE node_id=?",
                (result_summary, llm_interpretation, node_id),
            )


# ---------------------------------------------------------------------------
# Decisions
# ---------------------------------------------------------------------------

def add_decision(
    fork_node: str,
    chosen_branch: str,
    deferred_branches: list | None = None,
    reason: str = "",
) -> str:
    uid = _uid()
    with _conn() as conn:
        conn.execute(
            """
            INSERT INTO decisions (id, fork_node, chosen_branch, deferred_branches, reason, decided_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (uid, fork_node, chosen_branch, json.dumps(deferred_branches or []), reason, _now()),
        )
    return uid


# ---------------------------------------------------------------------------
# Queue
# ---------------------------------------------------------------------------

def enqueue(node_id: str, priority: int = 0, notes: str = "") -> str:
    uid = _uid()
    with _conn() as conn:
        conn.execute(
            "INSERT INTO queue (id, node_id, priority, status, notes, queued_at) VALUES (?, ?, ?, 'queued', ?, ?)",
            (uid, node_id, priority, notes, _now()),
        )
    return uid


def get_queue(status: str | None = None) -> list[dict]:
    with _conn() as conn:
        if status:
            rows = conn.execute(
                """
                SELECT q.*, n.title, n.type
                FROM queue q JOIN nodes n ON n.id = q.node_id
                WHERE q.status=?
                ORDER BY q.priority DESC, q.queued_at
                """,
                (status,),
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT q.*, n.title, n.type
                FROM queue q JOIN nodes n ON n.id = q.node_id
                ORDER BY q.status, q.priority DESC, q.queued_at
                """
            ).fetchall()
    return [dict(r) for r in rows]


def update_queue_item(
    queue_id: str,
    status: str,
    run_output: str = "",
    started_at: str | None = None,
    completed_at: str | None = None,
) -> None:
    with _conn() as conn:
        conn.execute(
            "UPDATE queue SET status=?, run_output=?, started_at=?, completed_at=? WHERE id=?",
            (status, run_output, started_at, completed_at, queue_id),
        )


def get_next_queued() -> dict | None:
    with _conn() as conn:
        row = conn.execute(
            """
            SELECT q.*, n.title, n.type
            FROM queue q JOIN nodes n ON n.id = q.node_id
            WHERE q.status='queued'
            ORDER BY q.priority DESC, q.queued_at
            LIMIT 1
            """
        ).fetchone()
    return dict(row) if row else None


# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------

def get_setting(key: str, default: str = "") -> str:
    with _conn() as conn:
        row = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    return row["value"] if row else default


def set_setting(key: str, value: str) -> None:
    with _conn() as conn:
        conn.execute(
            "INSERT INTO settings (key, value, updated_at) VALUES (?, ?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at",
            (key, value, _now()),
        )


# ---------------------------------------------------------------------------
# Typed children (for drill-down hierarchy)
# ---------------------------------------------------------------------------

def get_children_of_type(node_id: str, node_type: str) -> list[dict]:
    """Children of node_id filtered to a specific node type."""
    with _conn() as conn:
        rows = conn.execute(
            """
            SELECT n.*, e.edge_type
            FROM nodes n
            JOIN edges e ON e.to_node = n.id
            WHERE e.from_node = ? AND n.type = ?
            ORDER BY n.created_at
            """,
            (node_id, node_type),
        ).fetchall()
    return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# Verdict (hypothesis outcome)
# ---------------------------------------------------------------------------

def update_verdict(node_id: str, verdict: str) -> None:
    with _conn() as conn:
        conn.execute(
            "UPDATE nodes SET verdict=?, updated_at=? WHERE id=?",
            (verdict, _now(), node_id),
        )


# ---------------------------------------------------------------------------
# AI messages (conversation threads)
# ---------------------------------------------------------------------------

def add_ai_message(
    node_id: str,
    step_type: str,
    role: str,
    content: str,
    model: str = "",
) -> str:
    uid = _uid()
    with _conn() as conn:
        conn.execute(
            "INSERT INTO ai_messages (id, node_id, step_type, role, content, model, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (uid, node_id, step_type, role, content, model, _now()),
        )
    return uid


def get_ai_thread(node_id: str, step_type: str) -> list[dict]:
    with _conn() as conn:
        rows = conn.execute(
            "SELECT * FROM ai_messages WHERE node_id=? AND step_type=? ORDER BY created_at",
            (node_id, step_type),
        ).fetchall()
    return [dict(r) for r in rows]


def clear_ai_thread(node_id: str, step_type: str) -> None:
    with _conn() as conn:
        conn.execute(
            "DELETE FROM ai_messages WHERE node_id=? AND step_type=?",
            (node_id, step_type),
        )


# ---------------------------------------------------------------------------
# AI requests (batch tracking)
# ---------------------------------------------------------------------------

def add_ai_request(
    node_id: str,
    step_type: str,
    model: str,
    prompt: str = "",
    batch_id: str = "",
) -> str:
    uid = _uid()
    with _conn() as conn:
        conn.execute(
            "INSERT INTO ai_requests (id, node_id, step_type, model, prompt, batch_id, status, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, 'processing', ?)",
            (uid, node_id, step_type, model, prompt, batch_id, _now()),
        )
    return uid


def update_ai_request(
    request_id: str,
    status: str,
    response: str = "",
    completed_at: str | None = None,
) -> None:
    with _conn() as conn:
        conn.execute(
            "UPDATE ai_requests SET status=?, response=?, completed_at=? WHERE id=?",
            (status, response, completed_at or _now(), request_id),
        )


def get_pending_batches() -> list[dict]:
    with _conn() as conn:
        rows = conn.execute(
            "SELECT * FROM ai_requests WHERE status='processing' AND batch_id != '' ORDER BY created_at",
        ).fetchall()
    return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# Snapshots
# ---------------------------------------------------------------------------

def create_snapshot() -> Path:
    """Copy xworld.db to snapshots/xworld_{YYYYMMDD_HHMMSS}.db."""
    import shutil
    snapshots_dir = DB_PATH.parent / "snapshots"
    snapshots_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = snapshots_dir / f"xworld_{timestamp}.db"
    shutil.copy2(DB_PATH, dest)
    return dest


if __name__ == "__main__":
    init_db()
    print(f"Database initialised at {DB_PATH}")
