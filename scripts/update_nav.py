"""
Auto-update the Sessions section of mkdocs.yml from notebooks/summary_*.md files.
Run before mkdocs gh-deploy so new summaries appear on the site without manual edits.
"""
import re
from pathlib import Path
from datetime import datetime


def make_label(path: Path) -> str:
    """Convert 'summary_30MAR2026_nb20.md' → '30 Mar 2026 (nb20)'"""
    stem = path.stem[len("summary_"):]          # e.g. 30MAR2026_nb20
    m = re.match(r"(\d{1,2})([A-Z]{3})(\d{4})(.*)", stem)
    if not m:
        return stem
    day, mon, year, extra = m.groups()
    try:
        dt = datetime.strptime(f"{day}{mon}{year}", "%d%b%Y")
        label = dt.strftime("%-d %b %Y")
    except ValueError:
        label = f"{day} {mon} {year}"
    if extra:
        label += f" ({extra.lstrip('_')})"
    return label


def sort_key(path: Path):
    """Sort by date descending (newest first), then by extra suffix."""
    stem = path.stem[len("summary_"):]
    m = re.match(r"(\d{1,2})([A-Z]{3})(\d{4})(.*)", stem)
    if not m:
        return (datetime.min, "")
    day, mon, year, extra = m.groups()
    try:
        dt = datetime.strptime(f"{day}{mon}{year}", "%d%b%Y")
    except ValueError:
        dt = datetime.min
    return (dt, extra)


repo_root = Path(__file__).parent.parent
mkdocs_path = repo_root / "mkdocs.yml"
summaries = sorted(
    (repo_root / "notebooks").glob("summary_*.md"),
    key=sort_key,
    reverse=True,
)

session_lines = ["  - Sessions:"]
for s in summaries:
    label = make_label(s)
    session_lines.append(f'      - "{label}": {s.name}')
sessions_block = "\n".join(session_lines)

content = mkdocs_path.read_text()
content = re.sub(
    r"  - Sessions:.*",
    sessions_block,
    content,
    flags=re.DOTALL,
)
mkdocs_path.write_text(content)

print(f"Nav updated — {len(summaries)} sessions:")
for s in summaries:
    print(f"  {make_label(s)}: {s.name}")
