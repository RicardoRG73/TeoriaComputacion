#!/usr/bin/env python3
"""
Convierte las presentaciones Marp en Markdown de `diapositivas/` a PDFs 16:9 (1280x720 px)
respetando la hoja de estilos `diapositivas/industrial-brick.css` (tema claro con
diapositivas oscuras `lead` e `invert`/`dark`), KaTeX, Mermaid y figuras SVG.

Uso:
    python convertir_diapositivas_pdf.py
    python convertir_diapositivas_pdf.py --file diapositivas/1-0-introduccion.md
    python convertir_diapositivas_pdf.py --input-dir diapositivas --output-dir diapositivas/pdf --workers 6
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import html
from pathlib import Path
import re
import sys
import tempfile

import markdown

from convertir_notas_pdf import (
    PALETTE,
    ensure_web_assets,
    find_browser_executable,
    render_html_to_pdf,
)


# Patrones para parsear Marp, bloques de código, etiquetas div y fórmulas LaTeX
FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)
FENCED_CODE_RE = re.compile(
    r"^[ \t]*```([a-zA-Z0-9_-]*)[ \t]*\r?\n(.*?)^[ \t]*```[ \t]*$",
    re.MULTILINE | re.DOTALL,
)
INLINE_CODE_RE = re.compile(r"(`+)([^`\n]+?)\1")
BLOCK_MATH_RE = re.compile(r"(?<!\\)\$\$(.+?)(?<!\\)\$\$", re.DOTALL)
INLINE_MATH_RE = re.compile(r"(?<!\\)\$(?!\s)((?:\\.|[^\\\$\n])+?)(?<!\s)\$")
DIV_TAG_RE = re.compile(r"</?div(?:\s+[^>]*)?>", re.IGNORECASE)
SLIDE_CLASS_RE = re.compile(r"<!--\s*_class:\s*([^>]+?)\s*-->")
SLIDE_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
MARP_WIDTH_RE = re.compile(r"\bw:(\d+)\b|\bwidth:(\d+)\b")


def parse_frontmatter(md_text: str) -> tuple[dict[str, str], str]:
    """Extrae el bloque YAML inicial de Marp y devuelve (metadatos, cuerpo)."""
    match = FRONTMATTER_RE.match(md_text)
    if not match:
        return {}, md_text

    meta: dict[str, str] = {}
    for raw_line in match.group(1).splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip().lower()
        value = value.strip()
        if len(value) >= 2 and (
            (value.startswith("'") and value.endswith("'"))
            or (value.startswith('"') and value.endswith('"'))
        ):
            value = value[1:-1]
        meta[key] = value

    return meta, md_text[match.end():]


def split_slides(body_md: str) -> list[str]:
    """Divide el cuerpo Markdown en diapositivas respetando separadores `---` fuera de código."""
    slides: list[str] = []
    current_lines: list[str] = []
    in_fence = False

    for line in body_md.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            current_lines.append(line)
            continue

        if not in_fence and re.fullmatch(r"---+", stripped):
            slide_text = "\n".join(current_lines).strip()
            if slide_text:
                slides.append(slide_text)
            current_lines = []
        else:
            current_lines.append(line)

    tail = "\n".join(current_lines).strip()
    if tail:
        slides.append(tail)
    return slides


def extract_slide_title(md_text: str, fallback: str) -> str:
    """Obtiene el primer encabezado `# ...` como título del documento HTML."""
    for line in md_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return fallback


def preprocess_slide_markdown(slide_md: str) -> tuple[str, dict[str, tuple[str, str]]]:
    """
    Protege bloques de código, Mermaid, código en línea, matemáticas LaTeX y
    etiquetas `<div ...>` / `</div>` antes de ejecutar el parser Markdown.
    """
    placeholders: dict[str, tuple[str, str]] = {}
    counter = 0

    def next_token(kind: str, payload: str, meta: str = "") -> str:
        nonlocal counter
        token = f"XKTCPH{kind}{counter}END"
        counter += 1
        placeholders[token] = (meta, payload)
        return token

    def repl_fenced(match: re.Match[str]) -> str:
        lang = (match.group(1) or "").strip().lower()
        body = match.group(2)
        if lang == "mermaid":
            return next_token("MERMAID", body, "mermaid")
        return next_token("CODEBLOCK", body, lang)

    text = FENCED_CODE_RE.sub(repl_fenced, slide_md)

    def repl_inline_code(match: re.Match[str]) -> str:
        return next_token("INLINECODE", match.group(2), "code")

    text = INLINE_CODE_RE.sub(repl_inline_code, text)

    def repl_block_math(match: re.Match[str]) -> str:
        return next_token("BLOCKMATH", match.group(1).strip(), "blockmath")

    text = BLOCK_MATH_RE.sub(repl_block_math, text)

    def repl_inline_math(match: re.Match[str]) -> str:
        return next_token("INLINEMATH", match.group(1), "inlinemath")

    text = INLINE_MATH_RE.sub(repl_inline_math, text)

    # Proteger <div ...> y </div> para que Markdown siga procesando el contenido interno
    def repl_div_tag(match: re.Match[str]) -> str:
        return f"\n\n{next_token('DIVTAG', match.group(0), 'divtag')}\n\n"

    text = DIV_TAG_RE.sub(repl_div_tag, text)

    # Asegurar línea en blanco antes de listas pegadas a un párrafo
    list_item_re = re.compile(r"^([ \t]*)(?:[-*+]|\d+\.)\s+")
    normalized_lines: list[str] = []
    for line in text.splitlines():
        if (
            normalized_lines
            and list_item_re.match(line)
            and normalized_lines[-1].strip() != ""
            and not list_item_re.match(normalized_lines[-1])
            and not normalized_lines[-1].lstrip().startswith((">", "#", "|"))
            and "XKTCPHDIVTAG" not in normalized_lines[-1]
        ):
            normalized_lines.append("")
        normalized_lines.append(line)

    return "\n".join(normalized_lines), placeholders


def restore_slide_placeholders(
    html_body: str, placeholders: dict[str, tuple[str, str]]
) -> str:
    """Restaura los bloques protegidos en el HTML generado de una diapositiva."""
    for token, (meta, payload) in placeholders.items():
        if meta == "mermaid":
            escaped = html.escape(payload.strip(), quote=False)
            replacement = f'<div class="mermaid">\n{escaped}\n</div>'
        elif meta == "blockmath":
            escaped = html.escape(payload, quote=False)
            replacement = f'<div class="math-display">$$\n{escaped}\n$$</div>'
        elif meta == "inlinemath":
            escaped = html.escape(payload, quote=False)
            replacement = f"${escaped}$"
        elif meta == "code":
            escaped = html.escape(payload, quote=False)
            replacement = f"<code>{escaped}</code>"
        elif meta == "divtag":
            replacement = payload
        else:
            escaped = html.escape(payload.rstrip("\r\n"), quote=False)
            lang_class = f' class="language-{html.escape(meta)}"' if meta else ""
            replacement = f"<pre><code{lang_class}>{escaped}</code></pre>"
        html_body = html_body.replace(token, replacement)

    # Desenvolver <p><div ...></p> y <p></div></p> generados por bloques aislados
    html_body = re.sub(r"<p>\s*(</?div(?:\s+[^>]*)?>)\s*</p>", r"\1", html_body)
    return html_body


def transform_slide_images(html_fragment: str, md_path: Path) -> str:
    """Resuelve rutas relativas de imágenes y aplica directivas Marp (`w:<N>` / `center`)."""

    def repl_img(match: re.Match[str]) -> str:
        attrs = match.group(1)
        src_match = re.search(r'src="([^"]+)"', attrs)
        alt_match = re.search(r'alt="([^"]*)"', attrs)

        new_attrs = attrs
        if src_match:
            src = src_match.group(1)
            if not src.startswith(("http://", "https://", "data:", "file://")):
                resolved = (md_path.parent / src).resolve()
                if resolved.exists():
                    new_attrs = new_attrs.replace(
                        f'src="{src}"', f'src="{resolved.as_uri()}"'
                    )

        if alt_match:
            alt_text = alt_match.group(1)
            w_match = MARP_WIDTH_RE.search(alt_text)
            if w_match and "style=" not in new_attrs:
                width_px = w_match.group(1) or w_match.group(2)
                new_attrs += f' style="width: {width_px}px; max-width: 100%;"'

        return f"<img {new_attrs.strip()} />"

    return re.sub(r"<img\s+([^>]*?)\s*/?>", repl_img, html_fragment)


def load_theme_css(css_path: Path) -> str:
    """Carga el CSS de Marp eliminando `@import 'default';` para uso autónomo."""
    raw_css = css_path.read_text(encoding="utf-8")
    return re.sub(r"@import\s+['\"]default['\"]\s*;\s*", "", raw_css)


def convert_slides_to_html(md_path: Path, css_text: str, assets: dict[str, str]) -> str:
    """Convierte una presentación Marp completa en un documento HTML listo para imprimir a PDF."""
    raw_md = md_path.read_text(encoding="utf-8")
    meta, body_md = parse_frontmatter(raw_md)
    raw_slides = split_slides(body_md)

    title = meta.get("title") or extract_slide_title(body_md, md_path.stem)
    header_text = meta.get("header", "")
    footer_text = meta.get("footer", "")
    paginate = meta.get("paginate", "false").lower() in ("true", "1", "yes")

    md_parser = markdown.Markdown(extensions=["tables", "sane_lists"], tab_length=2)
    sections_html: list[str] = []

    for idx, slide_md in enumerate(raw_slides, start=1):
        classes: list[str] = []
        for cls_raw in SLIDE_CLASS_RE.findall(slide_md):
            classes.extend(cls_raw.split())

        cleaned_md = SLIDE_COMMENT_RE.sub("", slide_md).strip()
        protected_md, placeholders = preprocess_slide_markdown(cleaned_md)

        md_parser.reset()
        slide_html = md_parser.convert(protected_md)
        slide_html = restore_slide_placeholders(slide_html, placeholders)
        slide_html = transform_slide_images(slide_html, md_path)

        class_attr = f' class="{" ".join(classes)}"' if classes else ""
        header_html = f"<header>{html.escape(header_text)}</header>" if header_text else ""
        footer_html = f"<footer>{html.escape(footer_text)}</footer>" if footer_text else ""
        page_num_html = (
            f'<div class="slide-page-number">{idx}</div>' if paginate else ""
        )

        sections_html.append(
            f"<section{class_attr}>\n"
            f"  {header_html}\n"
            f'  <div class="slide-body">\n{slide_html}\n  </div>\n'
            f"  {footer_html}\n"
            f"  {page_num_html}\n"
            f"</section>"
        )

    p = PALETTE
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{html.escape(title)}</title>
  <link rel="stylesheet" href="{assets['katex_css']}" />
  <style>
    @page {{
      size: 1280px 720px;
      margin: 0;
    }}

    * {{
      box-sizing: border-box;
      -webkit-print-color-adjust: exact !important;
      print-color-adjust: exact !important;
    }}

    html, body {{
      margin: 0;
      padding: 0;
      background: #FAF8F5;
    }}

    section {{
      position: relative;
      display: flex;
      flex-direction: column;
      overflow: hidden;
      margin: 0;
      page-break-after: always;
      break-after: page;
    }}

    section:last-of-type {{
      page-break-after: auto;
      break-after: auto;
    }}

    header,
    footer,
    .slide-page-number {{
      position: absolute;
      margin: 0;
      z-index: 2;
    }}

    .slide-body {{
      width: 100%;
    }}

    .slide-body > *:first-child {{
      margin-top: 0;
    }}

    .slide-body > *:last-child {{
      margin-bottom: 0;
    }}

    .slide-page-number {{
      bottom: 15px;
      right: 66px;
      font-size: 13px;
      font-weight: 700;
      color: #B94A3E;
    }}

    section.lead .slide-page-number {{
      color: rgba(250, 248, 245, 0.72);
    }}

    section.invert .slide-page-number,
    section.dark .slide-page-number {{
      color: #E87466;
    }}

    .math-display {{
      margin: 8px 0;
      text-align: center;
      overflow-x: auto;
    }}

    .katex-display {{
      margin: 0.25em 0 !important;
    }}

{css_text}

    section::after {{
      display: none;
    }}
  </style>
</head>
<body>
  {''.join(sections_html)}

  <script src="{assets['katex_js']}"></script>
  <script src="{assets['katex_auto']}"></script>
  <script src="{assets['mermaid_js']}"></script>
  <script>
    (async function renderPresentation() {{
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

        if (typeof mermaid !== "undefined" && document.querySelector(".mermaid")) {{
          mermaid.initialize({{
            startOnLoad: false,
            theme: "base",
            securityLevel: "loose",
            flowchart: {{ useMaxWidth: true, htmlLabels: true, curve: "basis" }},
            themeVariables: {{
              background: "#FFFFFF",
              primaryColor: "{p['steel_soft']}",
              primaryTextColor: "{p['charcoal_ink']}",
              primaryBorderColor: "{p['steel_blue']}",
              lineColor: "{p['brick_red']}",
              fontFamily: '"Segoe UI", "Inter", "Helvetica Neue", Arial, sans-serif',
              fontSize: "13px"
            }}
          }});
          await mermaid.run({{ querySelector: ".mermaid" }});
        }}

        // Ajuste fino para evitar recorte vertical si una diapositiva excede el área útil
        for (const sec of document.querySelectorAll("section")) {{
          const body = sec.querySelector(".slide-body");
          if (!body) continue;
          const style = window.getComputedStyle(sec);
          const padTop = parseFloat(style.paddingTop) || 58;
          const padBottom = parseFloat(style.paddingBottom) || 52;
          const available = sec.clientHeight - padTop - padBottom;
          if (body.scrollHeight > available + 2) {{
            let fontPx = parseFloat(style.fontSize) || 23;
            while (body.scrollHeight > available + 2 && fontPx > 15) {{
              fontPx -= 1;
              sec.style.fontSize = fontPx + "px";
            }}
            if (body.scrollHeight > available + 2) {{
              const ratio = Math.max(0.72, available / body.scrollHeight);
              body.style.zoom = ratio.toFixed(3);
            }}
          }}
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


def convert_single_slide_deck(
    md_path: Path,
    output_dir: Path,
    css_text: str,
    browser_exe: Path,
    assets: dict[str, str],
    work_dir: Path,
) -> tuple[Path, Path, bool, str]:
    """Convierte un archivo `.md` de diapositivas Marp a PDF 16:9."""
    html_content = convert_slides_to_html(md_path, css_text, assets)
    html_path = work_dir / f"{md_path.stem}.html"
    html_path.write_text(html_content, encoding="utf-8")

    pdf_path = output_dir / f"{md_path.stem}.pdf"
    ok, msg = render_html_to_pdf(browser_exe, html_path, pdf_path)
    return md_path, pdf_path, ok, msg


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convierte presentaciones Marp de diapositivas/ a PDF (16:9) con tema Industrial Brick."
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path("diapositivas"),
        help="Directorio con las presentaciones .md de entrada (por defecto: diapositivas).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("diapositivas/pdf"),
        help="Directorio de salida para los PDFs (por defecto: diapositivas/pdf).",
    )
    parser.add_argument(
        "--css",
        type=Path,
        default=Path("diapositivas/industrial-brick.css"),
        help="Hoja de estilos Marp a aplicar (por defecto: diapositivas/industrial-brick.css).",
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
    css_path = args.css.resolve()
    if not css_path.is_file():
        print(f"[ERROR] No existe la hoja de estilos CSS: {css_path}", file=sys.stderr)
        return 1

    css_text = load_theme_css(css_path)
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
    print(f"Tema CSS:  {css_path}")
    print(f"Presentaciones a convertir: {len(md_files)} -> {output_dir}")

    failures: list[tuple[Path, str]] = []
    with tempfile.TemporaryDirectory(prefix="tc_slides_build_") as tmp_html_dir:
        work_dir = Path(tmp_html_dir)
        workers = max(1, min(args.workers, len(md_files)))
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {
                executor.submit(
                    convert_single_slide_deck,
                    md_path,
                    output_dir,
                    css_text,
                    browser_exe,
                    assets,
                    work_dir,
                ): md_path
                for md_path in md_files
            }
            for idx, future in enumerate(as_completed(futures), start=1):
                md_path, pdf_path, ok, msg = future.result()
                if ok:
                    size_kb = pdf_path.stat().st_size / 1024
                    print(
                        f"[{idx:02d}/{len(md_files):02d}] OK   {md_path.name} -> {pdf_path.name} ({size_kb:.1f} KB)"
                    )
                else:
                    print(
                        f"[{idx:02d}/{len(md_files):02d}] FAIL {md_path.name}: {msg}",
                        file=sys.stderr,
                    )
                    failures.append((md_path, msg))

    if failures:
        print(f"\n[ERROR] Fallaron {len(failures)} archivos.", file=sys.stderr)
        return 1

    print(f"\nConversión completada exitosamente: {len(md_files)} PDFs generados en {output_dir}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
