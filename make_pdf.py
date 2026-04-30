import markdown
import sys
from pathlib import Path

md_path = Path("PAPER.md")
pdf_path = Path("XWorld_Phase1_Paper.pdf")

md_text = md_path.read_text()
body = markdown.markdown(md_text, extensions=["tables", "extra"])

html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  @page {{
    margin: 2cm 2.2cm 2.5cm 2.2cm;
    @bottom-center {{
      content: "github.com/sekarkrishna/xworld  ·  git.sekrad.org/xworld";
      font-family: Georgia, serif;
      font-size: 9pt;
      color: #888;
    }}
  }}
  body {{
    font-family: Georgia, serif;
    font-size: 11pt;
    line-height: 1.6;
    color: #111;
  }}
  h1 {{ font-size: 20pt; margin-bottom: 4pt; }}
  h2 {{ font-size: 14pt; border-bottom: 1px solid #ccc; padding-bottom: 3pt; margin-top: 24pt; color: #222; }}
  h3 {{ font-size: 11.5pt; color: #b34700; margin-top: 14pt; margin-bottom: 4pt; }}
  p {{ margin: 6pt 0 10pt 0; }}
  table {{
    border-collapse: collapse;
    width: 100%;
    font-size: 10pt;
    margin: 12pt 0;
  }}
  th {{ background: #f0f0f0; text-align: left; padding: 5pt 8pt; border: 1px solid #ccc; }}
  td {{ padding: 4pt 8pt; border: 1px solid #ddd; vertical-align: top; }}
  em {{ font-style: italic; }}
  strong {{ font-weight: bold; }}
  code {{ font-family: monospace; background: #f5f5f5; padding: 1pt 3pt; font-size: 9.5pt; }}
  hr {{ border: none; border-top: 1px solid #ccc; margin: 18pt 0; }}
</style>
</head>
<body>
{body}
</body>
</html>"""

try:
    from weasyprint import HTML
    HTML(string=html).write_pdf(str(pdf_path))
    print(f"PDF written to {pdf_path}")
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
