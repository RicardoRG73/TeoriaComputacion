#!/usr/bin/env python3
"""
Convierte los apuntes en Markdown de la carpeta `notas/` a documentos PDF
con un tema claro inspirado en la paleta "Industrial Brick" (#B94A3E, #204254, #121B22).

Uso:
    python convertir_notas_pdf.py
    python convertir_notas_pdf.py --file notas/1-0-introduccion.md
    python convertir_notas_pdf.py --input-dir notas --output-dir notas/pdf --workers 4
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import html
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request

import markdown


# Paleta de colores "Industrial Brick" — Tema Claro
PALETTE = {
    # Colores base extraídos de la imagen de referencia
    "brick_red": "#B94A3E",
    "steel_blue": "#204254",
    "charcoal_ink": "#121B22",
    # Tonos derivados para tema claro editorial
    "bg_page": "#FFFFFF",
    "bg_header": "#FAF7F5",
    "bg_surface": "#F4F6F8",
    "bg_callout": "#FDF4F2",
    "bg_inline_code": "#F6ECEA",
    "text_primary": "#121B22",
    "text_secondary": "#2B3D4A",
    "text_muted": "#516370",
    "border_subtle": "#D5DEE4",
    "border_warm": "#E7C5C0",
    "brick_hover": "#98392F",
    "steel_soft": "#EEF3F6",
}

KATEX_VERSION = "0.16.11"
MERMAID_VERSION = "10.9.1"

KATEX_CSS_URL = f"https://cdn.jsdelivr.net/npm/katex@{KATEX_VERSION}/dist/katex.min.css"
KATEX_JS_URL = f"https://cdn.jsdelivr.net/npm/katex@{KATEX_VERSION}/dist/katex.min.js"
KATEX_AUTORENDER_URL = (
    f"https://cdn.jsdelivr.net/npm/katex@{KATEX_VERSION}/dist/contrib/auto-render.min.js"
)
MERMAID_JS_URL = f"https://cdn.jsdelivr.net/npm/mermaid@{MERMAID_VERSION}/dist/mermaid.min.js"

# Patrones para proteger código, Mermaid y matemáticas antes del parseo Markdown
FENCED_CODE_RE = re.compile(r"^[ \t]*```([a-zA-Z0-9_-]*)[ \t]*\r?\n(.*?)^[ \t]*```[ \t]*$", re.MULTILINE | re.DOTALL)
INLINE_CODE_RE = re.compile(r"(`+)([^`\n]+?)\1")
BLOCK_MATH_RE = re.compile(r"(?<!\\)\$\$(.+?)(?<!\\)\$\$", re.DOTALL)
INLINE_MATH_RE = re.compile(r"(?<!\\)\$(?!\s)((?:\\.|[^\\\$\n])+?)(?<!\s)\$")


def find_browser_executable() -> Path:
    """Localiza Microsoft Edge o Google Chrome en Windows/Linux/macOS."""
    candidates = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\Application\msedge.exe"),
    ]
    for cmd in ("msedge", "microsoft-edge", "google-chrome", "chromium", "chrome"):
        found = shutil.which(cmd)
        if found:
            return Path(found)
    for path_str in candidates:
        p = Path(path_str)
        if p.is_file():
            return p
    raise FileNotFoundError(
        "No se encontró Microsoft Edge ni Google Chrome para renderizar los PDFs."
    )


def ensure_web_assets(cache_dir: Path) -> dict[str, str]:
    """
    Descarga y cachea localmente KaTeX y Mermaid para acelerar la conversión
    y evitar fallos de red al generar múltiples PDFs en paralelo.
    """
    cache_dir.mkdir(parents=True, exist_ok=True)
    files = {
        "katex_css": (KATEX_CSS_URL, cache_dir / f"katex-{KATEX_VERSION}.min.css"),
        "katex_js": (KATEX_JS_URL, cache_dir / f"katex-{KATEX_VERSION}.min.js"),
        "katex_auto": (KATEX_AUTORENDER_URL, cache_dir / f"auto-render-{KATEX_VERSION}.min.js"),
        "mermaid_js": (MERMAID_JS_URL, cache_dir / f"mermaid-{MERMAID_VERSION}.min.js"),
    }

    uris: dict[str, str] = {}
    for key, (url, local_path) in files.items():
        if not local_path.exists() or local_path.stat().st_size == 0:
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=20) as resp:
                    data = resp.read()
                if key == "katex_css":
                    text = data.decode("utf-8")
                    # Resolver URLs relativas de fuentes hacia el CDN oficial
                    text = text.replace(
                        "url(fonts/",
                        f"url(https://cdn.jsdelivr.net/npm/katex@{KATEX_VERSION}/dist/fonts/",
                    )
                    local_path.write_text(text, encoding="utf-8")
                else:
                    local_path.write_bytes(data)
            except Exception:
                # Si falla la descarga, usar directamente la URL del CDN
                uris[key] = url
                continue
        uris[key] = local_path.resolve().as_uri()
    return uris


def extract_document_badge(filename: str) -> str:
    """Genera una etiqueta breve según la nomenclatura `X-0-*.md` o `X-Y-*.md`."""
    match = re.match(r"^(\d+)-(\d+)-", filename)
    if not match:
        return "APUNTES DE CLASE"
    unit, sub = match.group(1), match.group(2)
    if sub == "0":
        return f"UNIDAD {unit}"
    return f"UNIDAD {unit} · TEMA {unit}.{sub}"


def extract_title(md_text: str, fallback: str) -> str:
    """Obtiene el título principal `# ...` del archivo Markdown."""
    for line in md_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return fallback


def preprocess_markdown(md_text: str) -> tuple[str, dict[str, tuple[str, str]]]:
    """
    Protege bloques Mermaid, bloques de código, código en línea y expresiones LaTeX
    con marcadores alfanuméricos antes de convertir Markdown a HTML.
    """
    placeholders: dict[str, tuple[str, str]] = {}
    counter = 0

    def next_token(kind: str, payload: str, meta: str = "") -> str:
        nonlocal counter
        token = f"XKTCPH{kind}{counter}END"
        counter += 1
        placeholders[token] = (meta, payload)
        return token

    # 1. Bloques cercados (Mermaid y código normal)
    def repl_fenced(match: re.Match[str]) -> str:
        lang = (match.group(1) or "").strip().lower()
        body = match.group(2)
        if lang == "mermaid":
            return next_token("MERMAID", body, "mermaid")
        return next_token("CODEBLOCK", body, lang)

    text = FENCED_CODE_RE.sub(repl_fenced, md_text)

    # 2. Código en línea (para evitar que `$` dentro de backticks se interprete como LaTeX)
    def repl_inline_code(match: re.Match[str]) -> str:
        return next_token("INLINECODE", match.group(2), "code")

    text = INLINE_CODE_RE.sub(repl_inline_code, text)

    # 3. Matemáticas en bloque $$...$$
    def repl_block_math(match: re.Match[str]) -> str:
        return next_token("BLOCKMATH", match.group(1).strip(), "blockmath")

    text = BLOCK_MATH_RE.sub(repl_block_math, text)

    # 4. Matemáticas en línea $...$
    def repl_inline_math(match: re.Match[str]) -> str:
        return next_token("INLINEMATH", match.group(1), "inlinemath")

    text = INLINE_MATH_RE.sub(repl_inline_math, text)

    # 5. Asegurar línea en blanco antes de listas que siguen directo a un párrafo
    list_item_re = re.compile(r"^([ \t]*)(?:[-*+]|\d+\.)\s+")
    normalized_lines: list[str] = []
    for line in text.splitlines():
        if (
            normalized_lines
            and list_item_re.match(line)
            and normalized_lines[-1].strip() != ""
            and not list_item_re.match(normalized_lines[-1])
            and not normalized_lines[-1].lstrip().startswith((">", "#", "|"))
        ):
            normalized_lines.append("")
        normalized_lines.append(line)

    return "\n".join(normalized_lines), placeholders


def restore_placeholders(html_body: str, placeholders: dict[str, tuple[str, str]]) -> str:
    """Restaura los bloques protegidos ya con HTML seguro para KaTeX, Mermaid y código."""
    for token, (meta, payload) in placeholders.items():
        if meta == "mermaid":
            escaped = html.escape(payload.strip(), quote=False)
            replacement = f'<div class="diagram-card"><div class="mermaid">\n{escaped}\n</div></div>'
        elif meta == "blockmath":
            escaped = html.escape(payload, quote=False)
            replacement = f'<div class="math-display">$$\n{escaped}\n$$</div>'
        elif meta == "inlinemath":
            escaped = html.escape(payload, quote=False)
            replacement = f"${escaped}$"
        elif meta == "code":
            escaped = html.escape(payload, quote=False)
            replacement = f"<code>{escaped}</code>"
        else:
            escaped = html.escape(payload.rstrip("\r\n"), quote=False)
            lang_class = f' class="language-{html.escape(meta)}"' if meta else ""
            replacement = f"<pre><code{lang_class}>{escaped}</code></pre>"
        html_body = html_body.replace(token, replacement)
    return html_body


def convert_markdown_to_html(md_path: Path, assets: dict[str, str]) -> str:
    """Convierte un archivo Markdown en un documento HTML autocontenido listo para PDF."""
    raw_md = md_path.read_text(encoding="utf-8")
    title = extract_title(raw_md, md_path.stem)
    badge = extract_document_badge(md_path.name)

    protected_md, placeholders = preprocess_markdown(raw_md)

    md_parser = markdown.Markdown(extensions=["tables", "sane_lists"], tab_length=2)
    html_fragment = md_parser.convert(protected_md)
    html_fragment = restore_placeholders(html_fragment, placeholders)

    # Enlaces relativos a otros .md -> estilo discreto sin romper lectura
    html_fragment = re.sub(
        r'href="([^"]+\.md)"',
        r'href="\1" class="doc-link"',
        html_fragment,
    )

    # Resolver rutas relativas de imágenes (p. ej. ../figuras/*.svg) a URI absoluta
    def resolve_img_src(match: re.Match[str]) -> str:
        src = match.group(1)
        if src.startswith(("http://", "https://", "data:", "file://")):
            return match.group(0)
        resolved = (md_path.parent / src).resolve()
        return f'src="{resolved.as_uri()}"' if resolved.exists() else match.group(0)

    html_fragment = re.sub(r'src="([^"]+)"', resolve_img_src, html_fragment)

    p = PALETTE
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{html.escape(title)}</title>
  <link rel="stylesheet" href="{assets['katex_css']}" />
  <style>
    :root {{
      --brick-red: {p['brick_red']};
      --brick-hover: {p['brick_hover']};
      --steel-blue: {p['steel_blue']};
      --steel-soft: {p['steel_soft']};
      --charcoal-ink: {p['charcoal_ink']};
      --bg-page: {p['bg_page']};
      --bg-header: {p['bg_header']};
      --bg-surface: {p['bg_surface']};
      --bg-callout: {p['bg_callout']};
      --bg-inline-code: {p['bg_inline_code']};
      --text-primary: {p['text_primary']};
      --text-secondary: {p['text_secondary']};
      --text-muted: {p['text_muted']};
      --border-subtle: {p['border_subtle']};
      --border-warm: {p['border_warm']};
    }}

    @page {{
      size: letter;
      margin: 18mm 16mm 18mm 16mm;
    }}

    * {{
      box-sizing: border-box;
      -webkit-print-color-adjust: exact !important;
      print-color-adjust: exact !important;
    }}

    html, body {{
      margin: 0;
      padding: 0;
      background-color: var(--bg-page);
      color: var(--text-primary);
      font-family: "Segoe UI", "Inter", "Helvetica Neue", Arial, sans-serif;
      font-size: 10.5pt;
      line-height: 1.62;
    }}

    .page-container {{
      width: 100%;
      margin: 0 auto;
    }}

    /* Cinta superior inspirada en el degradado de la paleta Industrial Brick */
    .course-banner {{
      background-color: var(--bg-header);
      border: 1px solid var(--border-subtle);
      border-top: 5px solid var(--brick-red);
      border-radius: 6px;
      padding: 10px 14px;
      margin-bottom: 18px;
      position: relative;
      overflow: hidden;
    }}

    .course-banner::before {{
      content: "";
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 5px;
      background: linear-gradient(90deg, var(--brick-red) 0%, var(--steel-blue) 70%, var(--charcoal-ink) 100%);
    }}

    .course-banner-row {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
      flex-wrap: wrap;
    }}

    .course-meta {{
      font-size: 8.2pt;
      font-weight: 600;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      color: var(--steel-blue);
    }}

    .course-badge {{
      display: inline-block;
      background-color: var(--brick-red);
      color: #FFFFFF;
      font-size: 7.8pt;
      font-weight: 700;
      letter-spacing: 0.05em;
      padding: 2px 9px;
      border-radius: 999px;
    }}

    /* Jerarquía tipográfica */
    h1 {{
      font-size: 20pt;
      line-height: 1.25;
      color: var(--charcoal-ink);
      margin: 4px 0 14px 0;
      padding-bottom: 8px;
      border-bottom: 2.5px solid var(--brick-red);
      font-weight: 700;
      break-after: avoid;
    }}

    h2 {{
      font-size: 14.2pt;
      line-height: 1.3;
      color: var(--steel-blue);
      margin: 22px 0 10px 0;
      padding-left: 10px;
      border-left: 4px solid var(--brick-red);
      font-weight: 700;
      break-after: avoid;
    }}

    h3 {{
      font-size: 11.8pt;
      line-height: 1.35;
      color: var(--charcoal-ink);
      margin: 16px 0 6px 0;
      font-weight: 700;
      break-after: avoid;
    }}

    h4 {{
      font-size: 10.6pt;
      line-height: 1.35;
      color: var(--brick-red);
      margin: 12px 0 5px 0;
      font-weight: 700;
      break-after: avoid;
    }}

    p {{
      margin: 0 0 9px 0;
      text-align: justify;
      hyphens: auto;
    }}

    strong {{
      color: var(--charcoal-ink);
      font-weight: 700;
    }}

    em {{
      color: var(--text-secondary);
    }}

    a {{
      color: var(--steel-blue);
      text-decoration: none;
      border-bottom: 1px dotted var(--brick-red);
    }}

    hr {{
      border: none;
      height: 1px;
      background: linear-gradient(90deg, var(--brick-red) 0%, var(--border-subtle) 45%, transparent 100%);
      margin: 16px 0;
    }}

    ul, ol {{
      margin: 6px 0 10px 0;
      padding-left: 22px;
    }}

    li {{
      margin-bottom: 4px;
    }}

    li::marker {{
      color: var(--brick-red);
      font-weight: 700;
    }}

    /* Citas / Notas / Teoremas */
    blockquote {{
      margin: 12px 0;
      padding: 10px 14px;
      background-color: var(--bg-callout);
      border-left: 4px solid var(--brick-red);
      border-top: 1px solid var(--border-warm);
      border-right: 1px solid var(--border-warm);
      border-bottom: 1px solid var(--border-warm);
      border-radius: 0 6px 6px 0;
      color: var(--text-primary);
      break-inside: avoid;
    }}

    blockquote p:last-child {{
      margin-bottom: 0;
    }}

    /* Código en línea y bloques de código */
    code {{
      font-family: "Cascadia Code", "Consolas", "Fira Code", monospace;
      font-size: 9.2pt;
      background-color: var(--bg-inline-code);
      color: var(--brick-hover);
      padding: 1px 5px;
      border-radius: 4px;
      border: 1px solid var(--border-warm);
    }}

    pre {{
      background-color: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-left: 4px solid var(--steel-blue);
      border-radius: 6px;
      padding: 10px 12px;
      margin: 10px 0 12px 0;
      overflow-x: auto;
      white-space: pre-wrap;
      word-break: break-word;
      break-inside: avoid;
    }}

    pre code {{
      background: transparent;
      color: var(--charcoal-ink);
      border: none;
      padding: 0;
      font-size: 9pt;
      line-height: 1.48;
    }}

    /* Tablas */
    table {{
      width: 100%;
      border-collapse: collapse;
      margin: 12px 0 14px 0;
      font-size: 9.5pt;
      border: 1px solid var(--border-subtle);
      border-radius: 6px;
      overflow: hidden;
      break-inside: avoid;
    }}

    thead tr {{
      background-color: var(--steel-blue);
      color: #FFFFFF;
    }}

    th {{
      padding: 7px 10px;
      font-weight: 600;
      text-align: left;
      border-bottom: 2.5px solid var(--brick-red);
    }}

    td {{
      padding: 6px 10px;
      border-bottom: 1px solid var(--border-subtle);
      border-right: 1px solid var(--border-subtle);
      vertical-align: middle;
    }}

    td:last-child, th:last-child {{
      border-right: none;
    }}

    tbody tr:nth-child(even) {{
      background-color: var(--bg-surface);
    }}

    tbody tr:nth-child(odd) {{
      background-color: var(--bg-page);
    }}

    /* Ecuaciones KaTeX */
    .math-display {{
      margin: 10px 0;
      padding: 6px 10px;
      background-color: var(--steel-soft);
      border-left: 3px solid var(--steel-blue);
      border-radius: 0 5px 5px 0;
      overflow-x: auto;
      break-inside: avoid;
    }}

    .katex-display {{
      margin: 0.35em 0 !important;
    }}

    .katex {{
      font-size: 1.03em;
    }}

    /* Diagramas Mermaid */
    .diagram-card {{
      margin: 12px 0 14px 0;
      padding: 10px 12px;
      background-color: var(--bg-page);
      border: 1px solid var(--border-subtle);
      border-top: 3px solid var(--steel-blue);
      border-radius: 6px;
      text-align: center;
      break-inside: avoid;
    }}

    .mermaid svg {{
      max-width: 100%;
      height: auto;
    }}

    .markdown-body img {{
      display: block;
      max-width: 100%;
      height: auto;
      margin: 14px auto;
      border-radius: 8px;
      break-inside: avoid;
    }}

    .doc-footer {{
      margin-top: 24px;
      padding-top: 8px;
      border-top: 1px solid var(--border-subtle);
      font-size: 8pt;
      color: var(--text-muted);
      display: flex;
      justify-content: space-between;
    }}
  </style>
</head>
<body>
  <div class="page-container">
    <header class="course-banner">
      <div class="course-banner-row">
        <span class="course-meta">UVAQ · Ingeniería en Sistemas y Seguridad Informática · Teoría de la Computación (ISYSI0430)</span>
        <span class="course-badge">{html.escape(badge)}</span>
      </div>
    </header>
    <main class="markdown-body">
      {html_fragment}
    </main>
    <footer class="doc-footer">
      <span>Fuente: {html.escape(md_path.name)}</span>
      <span>Paleta Industrial Brick · Tema Claro</span>
    </footer>
  </div>

  <script src="{assets['katex_js']}"></script>
  <script src="{assets['katex_auto']}"></script>
  <script src="{assets['mermaid_js']}"></script>
  <script>
    (async function renderDocument() {{
      try {{
        if (typeof renderMathInElement === "function") {{
          renderMathInElement(document.body, {{
            delimiters: [
              {{ left: "$$", right: "$$", display: true }},
              {{ left: "$", right: "$", display: false }}
            ],
            throwOnError: false,
            strict: false
          }});
        }}

        if (typeof mermaid !== "undefined") {{
          mermaid.initialize({{
            startOnLoad: false,
            theme: "base",
            securityLevel: "loose",
            flowchart: {{
              useMaxWidth: true,
              htmlLabels: true,
              curve: "basis"
            }},
            themeVariables: {{
              background: "#FFFFFF",
              primaryColor: "{p['steel_soft']}",
              primaryTextColor: "{p['charcoal_ink']}",
              primaryBorderColor: "{p['steel_blue']}",
              lineColor: "{p['brick_red']}",
              secondaryColor: "{p['bg_callout']}",
              secondaryBorderColor: "{p['brick_red']}",
              tertiaryColor: "{p['bg_surface']}",
              tertiaryBorderColor: "{p['steel_blue']}",
              textColor: "{p['charcoal_ink']}",
              edgeLabelBackground: "{p['bg_header']}",
              clusterBkg: "{p['bg_header']}",
              clusterBorder: "{p['steel_blue']}",
              fontFamily: '"Segoe UI", "Inter", "Helvetica Neue", Arial, sans-serif',
              fontSize: "13px"
            }}
          }});
          await mermaid.run({{ querySelector: ".mermaid" }});
        }}
      }} catch (err) {{
        console.error("Render error:", err);
      }} finally {{
        document.body.dataset.renderComplete = "true";
      }}
    }})();
  </script>
</body>
</html>
"""


def render_html_to_pdf(
    browser_exe: Path,
    html_path: Path,
    pdf_path: Path,
    virtual_time_budget_ms: int = 12000,
) -> tuple[bool, str]:
    """Invoca Edge/Chrome headless para imprimir un HTML local a PDF."""
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="edge_pdf_profile_") as profile_dir:
        cmd = [
            str(browser_exe),
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            "--allow-file-access-from-files",
            "--no-pdf-header-footer",
            "--run-all-compositor-stages-before-draw",
            f"--virtual-time-budget={virtual_time_budget_ms}",
            f"--user-data-dir={profile_dir}",
            f"--print-to-pdf={pdf_path.resolve()}",
            html_path.resolve().as_uri(),
        ]
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
        )
        if proc.returncode != 0 or not pdf_path.is_file() or pdf_path.stat().st_size == 0:
            err_msg = (proc.stderr or proc.stdout or f"Exit code {proc.returncode}").strip()
            return False, err_msg
    return True, ""


def convert_single_file(
    md_path: Path,
    output_dir: Path,
    browser_exe: Path,
    assets: dict[str, str],
    work_dir: Path,
) -> tuple[Path, Path, bool, str]:
    """Convierte un archivo `.md` individual a `.pdf`."""
    html_content = convert_markdown_to_html(md_path, assets)
    html_path = work_dir / f"{md_path.stem}.html"
    html_path.write_text(html_content, encoding="utf-8")

    pdf_path = output_dir / f"{md_path.stem}.pdf"
    ok, msg = render_html_to_pdf(browser_exe, html_path, pdf_path)
    return md_path, pdf_path, ok, msg


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convierte archivos Markdown de notas/ a PDF con paleta Industrial Brick (tema claro)."
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path("notas"),
        help="Directorio con los archivos .md de entrada (por defecto: notas).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("notas/pdf"),
        help="Directorio de salida para los PDFs (por defecto: notas/pdf).",
    )
    parser.add_argument(
        "--file",
        type=Path,
        nargs="*",
        help="Archivo(s) .md específicos a convertir. Si se omite, convierte todos los .md de --input-dir.",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="Número de conversiones en paralelo (por defecto: 4).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    browser_exe = find_browser_executable()

    if args.file:
        md_files = [p.resolve() for p in args.file]
        for p in md_files:
            if not p.is_file():
                print(f"[ERROR] No existe el archivo: {p}", file=sys.stderr)
                return 1
    else:
        if not args.input_dir.is_dir():
            print(f"[ERROR] No existe el directorio de entrada: {args.input_dir}", file=sys.stderr)
            return 1
        md_files = sorted(args.input_dir.resolve().glob("*.md"))

    if not md_files:
        print("[AVISO] No se encontraron archivos .md para convertir.")
        return 0

    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    cache_dir = Path(tempfile.gettempdir()) / "teoria_computacion_pdf_assets"
    assets = ensure_web_assets(cache_dir)

    print(f"Navegador: {browser_exe}")
    print(f"Archivos a convertir: {len(md_files)} -> {output_dir}")

    failures: list[tuple[Path, str]] = []
    with tempfile.TemporaryDirectory(prefix="tc_html_build_") as tmp_html_dir:
        work_dir = Path(tmp_html_dir)
        workers = max(1, min(args.workers, len(md_files)))
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {
                executor.submit(
                    convert_single_file, md_path, output_dir, browser_exe, assets, work_dir
                ): md_path
                for md_path in md_files
            }
            for idx, future in enumerate(as_completed(futures), start=1):
                md_path, pdf_path, ok, msg = future.result()
                if ok:
                    size_kb = pdf_path.stat().st_size / 1024
                    print(f"[{idx:02d}/{len(md_files):02d}] OK   {md_path.name} -> {pdf_path.name} ({size_kb:.1f} KB)")
                else:
                    print(f"[{idx:02d}/{len(md_files):02d}] FAIL {md_path.name}: {msg}", file=sys.stderr)
                    failures.append((md_path, msg))

    if failures:
        print(f"\nFinalizado con {len(failures)} error(es).", file=sys.stderr)
        return 1

    print(f"\nConversión completada exitosamente: {len(md_files)} PDFs generados en {output_dir}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
