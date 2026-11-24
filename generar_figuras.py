#!/usr/bin/env python3
"""
Genera las 38 figuras didácticas en formato SVG dentro de `figuras/`
con la paleta clara "Industrial Brick" (#B94A3E, #204254, #121B22)
para ilustrar las notas (`notas/`) y diapositivas (`diapositivas/`).
"""

from __future__ import annotations

import html
from pathlib import Path

W, H = 960, 360

# Paleta Industrial Brick (Tema Claro)
BRICK = "#B94A3E"
BRICK_DARK = "#93362C"
STEEL = "#204254"
INK = "#121B22"
MUTED = "#4E606D"
BG_PAGE = "#FAF8F5"
BG_CARD = "#FFFFFF"
STEEL_SOFT = "#EEF3F6"
BRICK_SOFT = "#FDF4F2"
BORDER = "#CBD6DE"
BORDER_WARM = "#E6C1BC"
FONT = "Segoe UI, Inter, Helvetica Neue, Arial, sans-serif"
MONO = "Cascadia Code, Consolas, monospace"


def esc(text: str) -> str:
    return html.escape(text, quote=True)


def svg_wrap(title: str, subtitle: str, body: str) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{esc(title)}">
  <defs>
    <linearGradient id="topGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{BRICK}"/>
      <stop offset="65%" stop-color="{STEEL}"/>
      <stop offset="100%" stop-color="{INK}"/>
    </linearGradient>
    <marker id="arrSteel" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M 0 1.5 L 9 5 L 0 8.5 z" fill="{STEEL}"/>
    </marker>
    <marker id="arrBrick" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M 0 1.5 L 9 5 L 0 8.5 z" fill="{BRICK}"/>
    </marker>
    <marker id="arrInk" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M 0 1.5 L 9 5 L 0 8.5 z" fill="{INK}"/>
    </marker>
  </defs>
  <rect x="0" y="0" width="{W}" height="{H}" rx="12" fill="{BG_PAGE}" stroke="{BORDER}" stroke-width="1.5"/>
  <rect x="0" y="0" width="{W}" height="6" rx="3" fill="url(#topGrad)"/>
  <text x="28" y="34" font-family="{FONT}" font-size="16" font-weight="700" fill="{INK}">{esc(title)}</text>
  <text x="28" y="54" font-family="{FONT}" font-size="12" font-weight="500" fill="{MUTED}">{esc(subtitle)}</text>
  <line x1="28" y1="64" x2="{W - 28}" y2="64" stroke="{BORDER}" stroke-width="1"/>
{body}
</svg>
'''


def box(x: float, y: float, w: float, h: float, title: str, sub: str = "", accent: str = "steel", dashed: bool = False) -> str:
    if accent == "brick":
        fill, stroke, tcolor = BRICK_SOFT, BRICK, INK
    elif accent == "dark":
        fill, stroke, tcolor = STEEL, INK, "#FFFFFF"
    elif accent == "brick_solid":
        fill, stroke, tcolor = BRICK, BRICK_DARK, "#FFFFFF"
    elif accent == "white":
        fill, stroke, tcolor = BG_CARD, BORDER, INK
    else:
        fill, stroke, tcolor = STEEL_SOFT, STEEL, INK
    dash_attr = ' stroke-dasharray="6,4"' if dashed else ""
    parts = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" fill="{fill}" stroke="{stroke}" stroke-width="2"{dash_attr}/>']
    cx = x + w / 2
    if sub:
        sub_lines = sub.splitlines()
        sub_color = "#DCE7EE" if accent in ("dark", "brick_solid") else MUTED
        total_lines = 1 + len(sub_lines)
        start_y = y + h / 2 - (total_lines - 1) * 8 + 4
        parts.append(f'<text x="{cx}" y="{start_y}" text-anchor="middle" font-family="{FONT}" font-size="13.5" font-weight="700" fill="{tcolor}">{esc(title)}</text>')
        for idx, line in enumerate(sub_lines, start=1):
            parts.append(f'<text x="{cx}" y="{start_y + idx * 17}" text-anchor="middle" font-family="{FONT}" font-size="11.5" fill="{sub_color}">{esc(line)}</text>')
    else:
        parts.append(f'<text x="{cx}" y="{y + h/2 + 5}" text-anchor="middle" font-family="{FONT}" font-size="13.5" font-weight="700" fill="{tcolor}">{esc(title)}</text>')
    return "\n  ".join(parts)


def state(cx: float, cy: float, r: float, label: str, sub: str = "", final: bool = False, initial: bool = False, accent: str = "steel") -> str:
    fill = BRICK_SOFT if (final or accent == "brick") else STEEL_SOFT
    stroke = BRICK if (final or accent == "brick") else STEEL
    out = []
    if initial:
        out.append(f'<line x1="{cx - r - 34}" y1="{cy}" x2="{cx - r - 3}" y2="{cy}" stroke="{BRICK}" stroke-width="2.2" marker-end="url(#arrBrick)"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="2.2"/>')
    if final:
        out.append(f'<circle cx="{cx}" cy="{cy}" r="{r - 5}" fill="none" stroke="{stroke}" stroke-width="1.6"/>')
    if sub:
        out.append(f'<text x="{cx}" y="{cy - 2}" text-anchor="middle" font-family="{FONT}" font-size="13.5" font-weight="700" fill="{INK}">{esc(label)}</text>')
        out.append(f'<text x="{cx}" y="{cy + 14}" text-anchor="middle" font-family="{FONT}" font-size="11" fill="{MUTED}">{esc(sub)}</text>')
    else:
        out.append(f'<text x="{cx}" y="{cy + 5}" text-anchor="middle" font-family="{FONT}" font-size="14" font-weight="700" fill="{INK}">{esc(label)}</text>')
    return "\n  ".join(out)


def arrow(x1: float, y1: float, x2: float, y2: float, label: str = "", color: str = "brick", dy: float = -8, dx: float = 0, dashed: bool = False) -> str:
    c = BRICK if color == "brick" else (STEEL if color == "steel" else INK)
    m = "arrBrick" if color == "brick" else ("arrSteel" if color == "steel" else "arrInk")
    dash = ' stroke-dasharray="5,4"' if dashed else ""
    out = [f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{c}" stroke-width="2.2"{dash} marker-end="url(#{m})"/>']
    if label:
        mx, my = (x1 + x2) / 2 + dx, (y1 + y2) / 2 + dy
        out.append(f'<rect x="{mx - len(label)*3.4 - 6}" y="{my - 12}" width="{len(label)*6.8 + 12}" height="17" rx="4" fill="{BG_PAGE}" fill-opacity="0.92"/>')
        out.append(f'<text x="{mx}" y="{my}" text-anchor="middle" font-family="{FONT}" font-size="11.5" font-weight="600" fill="{c}">{esc(label)}</text>')
    return "\n  ".join(out)


def curved_arrow(path_d: str, lx: float, ly: float, label: str = "", color: str = "brick") -> str:
    c = BRICK if color == "brick" else STEEL
    m = "arrBrick" if color == "brick" else "arrSteel"
    out = [f'<path d="{path_d}" fill="none" stroke="{c}" stroke-width="2.2" marker-end="url(#{m})"/>']
    if label:
        out.append(f'<rect x="{lx - len(label)*3.4 - 5}" y="{ly - 12}" width="{len(label)*6.8 + 10}" height="17" rx="4" fill="{BG_PAGE}" fill-opacity="0.92"/>')
        out.append(f'<text x="{lx}" y="{ly}" text-anchor="middle" font-family="{FONT}" font-size="11.5" font-weight="600" fill="{c}">{esc(label)}</text>')
    return "\n  ".join(out)


def tape(x: float, y: float, cells: list[str], cw: float = 42, ch: float = 36, active_idx: int | None = None) -> str:
    out = []
    for i, val in enumerate(cells):
        cx = x + i * cw
        is_act = (i == active_idx)
        fill = BRICK_SOFT if is_act else BG_CARD
        stroke = BRICK if is_act else STEEL
        out.append(f'<rect x="{cx}" y="{y}" width="{cw}" height="{ch}" fill="{fill}" stroke="{stroke}" stroke-width="1.8"/>')
        out.append(f'<text x="{cx + cw/2}" y="{y + ch/2 + 5}" text-anchor="middle" font-family="{MONO}" font-size="14" font-weight="700" fill="{INK}">{esc(val)}</text>')
    return "\n  ".join(out)


def txt(x: float, y: float, s: str, size: int = 12, weight: str = "600", color: str = INK, anchor: str = "middle", mono: bool = False) -> str:
    ff = MONO if mono else FONT
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="{ff}" font-size="{size}" font-weight="{weight}" fill="{color}">{esc(s)}</text>'


def badge(x: float, y: float, w: float, s: str, color: str = BRICK) -> str:
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="22" rx="11" fill="{color}"/>'
        f'<text x="{x + w/2}" y="{y + 15}" text-anchor="middle" font-family="{FONT}" font-size="11" font-weight="700" fill="#FFFFFF">{esc(s)}</text>'
    )


def generate_all(out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    figs: dict[str, str] = {}

    # 1-0 Introducción
    figs["1-0-introduccion"] = svg_wrap(
        "Unidad 1 · Ruta conceptual de la Teoría de la Computación",
        "De las máquinas discretas de información al álgebra de cadenas y lenguajes",
        "\n  ".join([
            box(40, 95, 240, 74, "1.1–1.2 Máquinas", "Discretas, algoritmos y MT", "steel"),
            box(360, 95, 240, 74, "1.3–1.4 Lenguajes", "Aceptadores, generadores, trad.", "brick"),
            box(680, 95, 240, 74, "1.5–1.7 Cadenas y Álgebra", "Σ, λ, Σ*, w^R, A*, A+", "steel"),
            arrow(280, 132, 355, 132, "", "brick"),
            arrow(600, 132, 675, 132, "", "brick"),
            box(120, 225, 720, 96, "Base matemática para Autómatas, Gramáticas y Compiladores", "Unidades 2 a 6: Gramáticas · MEF · Lenguajes Regulares · Pushdown · LIC", "dark"),
            arrow(200, 169, 320, 222, "", "steel"),
            arrow(480, 169, 480, 222, "", "brick"),
            arrow(760, 169, 640, 222, "", "steel"),
        ]),
    )

    # 1-1 Máquinas de información
    figs["1-1-maquinas-de-informacion"] = svg_wrap(
        "1.1 Arquitectura funcional de una máquina de información",
        "Interacción Entrada – Control – Estado interno – Salida y ejemplo del torniquete",
        "\n  ".join([
            box(38, 100, 185, 68, "Entrada simbólica", "u ∈ Σ* (discreta)", "steel"),
            box(280, 96, 220, 76, "Unidad de Procesamiento", "Reglas de transición", "dark"),
            box(280, 225, 220, 68, "Estado Interno (q ∈ Q)", "Memoria resumida del pasado", "brick"),
            box(560, 100, 175, 68, "Salida simbólica", "v ∈ Δ* o Acepta/Rechaza", "steel"),
            arrow(223, 134, 276, 134, "lee", "brick"),
            arrow(500, 134, 556, 134, "emite", "brick"),
            arrow(370, 172, 370, 221, "", "steel"),
            arrow(410, 225, 410, 176, "", "steel"),
            f'<rect x="748" y="88" width="188" height="240" rx="10" fill="{BG_CARD}" stroke="{BORDER}" stroke-width="1.5"/>',
            txt(842, 112, "Torniquete (Ejemplo)", 12.5, "700", STEEL),
            state(842, 164, 24, "q0", "Bloq.", initial=True),
            state(842, 272, 24, "q1", "Libre", accent="brick"),
            curved_arrow("M 860 182 Q 896 218 860 254", 894, 222, "m/Abrir", "brick"),
            curved_arrow("M 824 254 Q 788 218 824 182", 790, 222, "e/Cerrar", "steel"),
        ]),
    )

    # 1-2 Máquinas abstractas y algoritmos
    figs["1-2-maquinas-abstractas-y-algoritmos"] = svg_wrap(
        "1.2 Modelos de máquinas abstractas según su memoria auxiliar",
        "A mayor libertad de almacenamiento, mayor poder computacional (Tesis de Church-Turing)",
        "\n  ".join([
            f'<rect x="35" y="84" width="275" height="245" rx="10" fill="{BG_CARD}" stroke="{STEEL}" stroke-width="1.8"/>',
            badge(55, 96, 150, "1. Autómata Finito", STEEL),
            tape(55, 136, ["a", "b", "a", "b"], 42, 34, 1),
            txt(172, 195, "Cinta solo lectura (→)", 12, "600", MUTED),
            box(65, 220, 215, 58, "Solo estados Q (finito)", "No puede contar sin límite", "steel"),
            txt(172, 308, "Léxico · Tipo 3", 12, "700", BRICK),

            f'<rect x="342" y="84" width="275" height="245" rx="10" fill="{BG_CARD}" stroke="{BRICK}" stroke-width="2"/>',
            badge(362, 96, 175, "2. Autómata con Pila", BRICK),
            tape(362, 136, ["a", "a", "b", "b"], 42, 34, 2),
            txt(480, 195, "Cinta solo lectura + Pila LIFO", 12, "600", MUTED),
            box(372, 220, 215, 58, "Pila [A, A, z0] ilimitada", "Verifica {a^n b^n} y paréntesis", "brick"),
            txt(480, 308, "Sintáctico · Tipo 2", 12, "700", BRICK),

            f'<rect x="650" y="84" width="275" height="245" rx="10" fill="{BG_CARD}" stroke="{INK}" stroke-width="2"/>',
            badge(670, 96, 185, "3. Máquina de Turing", INK),
            tape(670, 136, ["#", "1", "0", "#"], 42, 34, 1),
            txt(788, 195, "Lectura/escritura (← y →)", 12, "600", MUTED),
            box(680, 220, 215, 58, "Cinta infinita universal", "Equivale a todo algoritmo", "dark"),
            txt(788, 308, "Computabilidad · Tipo 0", 12, "700", STEEL),
        ]),
    )

    # 1-3 Lenguajes abstractos
    figs["1-3-lenguajes-abstractos"] = svg_wrap(
        "1.3 Lenguajes abstractos: sintaxis frente a semántica",
        "Flujo de validación en compiladores y relación conjuntista ∅ ⊆ L ⊆ Σ*",
        "\n  ".join([
            box(35, 92, 165, 64, "Código fuente", "Cadena w ∈ Σ*", "white"),
            box(245, 92, 175, 64, "Análisis Léxico", "Símbolos y tokens", "steel"),
            box(465, 92, 195, 64, "Análisis Sintáctico", "¿Cumple gramática? (w ∈ L)", "brick"),
            box(705, 92, 220, 64, "Análisis Semántico", "Tipos y sentido válido", "dark"),
            arrow(200, 124, 241, 124, "", "brick"),
            arrow(420, 124, 461, 124, "", "brick"),
            arrow(660, 124, 701, 124, "", "brick"),
            f'<rect x="35" y="186" width="890" height="142" rx="10" fill="{BG_CARD}" stroke="{BORDER}" stroke-width="1.5"/>',
            txt(150, 216, "Universo Σ* (todas las cadenas)", 13, "700", STEEL, "start"),
            f'<ellipse cx="585" cy="257" rx="295" ry="54" fill="{STEEL_SOFT}" stroke="{STEEL}" stroke-width="2"/>',
            f'<ellipse cx="565" cy="260" rx="185" ry="37" fill="{BRICK_SOFT}" stroke="{BRICK}" stroke-width="2"/>',
            txt(565, 255, "Lenguaje L ⊆ Σ*", 13.5, "700", BRICK),
            txt(565, 275, "Ej.: x=42; ∈ L   |   42=x; ∈ Σ* \\ L", 11.5, "600", INK),
            txt(785, 240, "w ∉ L", 12, "700", STEEL),
            txt(195, 255, "Casos extremos:", 12.5, "700", INK),
            txt(195, 278, "∅ (vacío)  ⊆  L  ⊆  Σ* (universal)", 12, "600", MUTED),
        ]),
    )

    # 1-4 Aceptadores, generadores y traductores
    figs["1-4-aceptadores-generadores-y-traductores"] = svg_wrap(
        "1.4 Tres enfoques para operar con lenguajes formales",
        "Aceptador (decide pertenencia), Generador (construye cadenas) y Traductor (transforma entradas)",
        "\n  ".join([
            f'<rect x="35" y="84" width="275" height="245" rx="10" fill="{BG_CARD}" stroke="{STEEL}" stroke-width="1.8"/>',
            badge(55, 96, 120, "1. ACEPTADOR", STEEL),
            txt(172, 140, "Entrada: w ∈ Σ*", 12, "600", INK),
            arrow(172, 148, 172, 178, "", "steel"),
            box(70, 182, 205, 52, "Autómata M", "f_M : Σ* → {0, 1}", "steel"),
            arrow(125, 234, 105, 268, "", "brick"),
            arrow(220, 234, 240, 268, "", "steel"),
            txt(100, 290, "1 (Acepta)", 12.5, "700", BRICK),
            txt(240, 290, "0 (Rechaza)", 12.5, "700", STEEL),
            txt(172, 315, "Ej.: AFD, AFN, AFPN", 11.5, "500", MUTED),

            f'<rect x="342" y="84" width="275" height="245" rx="10" fill="{BG_CARD}" stroke="{BRICK}" stroke-width="2"/>',
            badge(362, 96, 125, "2. GENERADOR", BRICK),
            txt(480, 140, "Axioma inicial S", 12, "600", INK),
            arrow(480, 148, 480, 178, "", "brick"),
            box(377, 182, 205, 52, "Gramática G / ER", "Aplica reglas α → β", "brick"),
            arrow(480, 234, 480, 266, "", "brick"),
            txt(480, 288, "w₁, w₂, w₃, ... ∈ L(G)", 12.5, "700", INK),
            txt(480, 315, "Ej.: Gramáticas de Chomsky", 11.5, "500", MUTED),

            f'<rect x="650" y="84" width="275" height="245" rx="10" fill="{BG_CARD}" stroke="{INK}" stroke-width="1.8"/>',
            badge(670, 96, 125, "3. TRADUCTOR", INK),
            txt(788, 140, "Fuente: w ∈ Σ*", 12, "600", INK),
            arrow(788, 148, 788, 178, "", "steel"),
            box(685, 182, 205, 52, "Transductor T", "T : Σ* → Δ*", "dark"),
            arrow(788, 234, 788, 266, "", "brick"),
            txt(788, 288, "Destino: v = T(w) ∈ Δ*", 12.5, "700", BRICK),
            txt(788, 315, "Ej.: Mealy, Moore, compiladores", 11.5, "500", MUTED),
        ]),
    )

    # 1-5 Cadenas de lenguajes
    figs["1-5-cadenas-de-lenguajes"] = svg_wrap(
        "1.5 Distinción fundamental: ∅, λ, {λ}, {∅} y universos Σ*, Σ+",
        "No confundir una cadena sin símbolos (λ) con un conjunto sin cadenas (∅)",
        "\n  ".join([
            box(40, 88, 195, 100, "∅ (Lenguaje vacío)", "Conjunto con 0 cadenas", "white", dashed=True),
            box(265, 88, 195, 100, "λ (Cadena vacía)", "Secuencia de longitud 0", "brick"),
            box(490, 88, 195, 100, "{λ} (Unitario)", "Conjunto con 1 cadena: λ", "steel"),
            box(715, 88, 205, 100, "{∅} (Familia)", "Conjunto cuyo elemento es ∅", "white"),
            f'<rect x="40" y="210" width="880" height="122" rx="10" fill="{STEEL_SOFT}" stroke="{STEEL}" stroke-width="2"/>',
            txt(480, 235, "Universo Σ* = {λ} ∪ Σ+   (Infinito numerable, ejemplo Σ = {a, b})", 13.5, "700", STEEL),
            box(70, 250, 150, 62, "{λ} (long. 0)", "|λ| = 0", "brick"),
            box(245, 250, 645, 62, "Σ+ = Σ* - {λ}   (Cadenas no vacías: longitud ≥ 1)", "a, b  |  aa, ab, ba, bb  |  aaa, aab, aba, ...", "white"),
        ]),
    )

    # 1-6 Cadenas y sus operaciones
    figs["1-6-cadenas-y-sus-operaciones"] = svg_wrap(
        "1.6 Anatomía de una cadena: prefijos, subcadenas, sufijos y reflexión",
        "Descomposición u = x · v · y (ejemplo u = bcbaadb) y regla inversa (uv)^R = v^R u^R",
        "\n  ".join([
            txt(480, 96, "Cadena u = x · v · y  (longitud |u| = 7)", 13.5, "700", INK),
            tape(268, 110, ["b", "c", "b", "a", "a", "d", "b"], 60, 40),
            f'<rect x="268" y="156" width="120" height="24" rx="5" fill="{STEEL_SOFT}" stroke="{STEEL}" stroke-width="1.5"/>',
            txt(328, 172, "Prefijo x = bc", 11.5, "700", STEEL),
            f'<rect x="388" y="156" width="180" height="24" rx="5" fill="{BRICK_SOFT}" stroke="{BRICK}" stroke-width="1.5"/>',
            txt(478, 172, "Subcadena v = baa", 11.5, "700", BRICK),
            f'<rect x="568" y="156" width="120" height="24" rx="5" fill="{STEEL_SOFT}" stroke="{STEEL}" stroke-width="1.5"/>',
            txt(628, 172, "Sufijo y = db", 11.5, "700", STEEL),
            f'<rect x="55" y="205" width="850" height="122" rx="10" fill="{BG_CARD}" stroke="{BORDER}" stroke-width="1.5"/>',
            txt(480, 230, "Reflexión de una concatenación: (u · v)^R = v^R · u^R", 13.5, "700", BRICK),
            box(95, 248, 160, 56, "u = ab", "u^R = ba", "steel"),
            box(275, 248, 170, 56, "v = bca", "v^R = acb", "brick"),
            arrow(455, 276, 515, 276, "invertir", "brick"),
            box(525, 248, 340, 56, "(uv)^R = (abbca)^R = acbba", "v^R · u^R = (acb)(ba) = acbba", "dark"),
        ]),
    )

    # 1-7 Operaciones sobre lenguajes
    figs["1-7-operaciones-sobre-lenguajes"] = svg_wrap(
        "1.7 Operaciones conjuntistas y clausuras de Kleene (A* y A+)",
        "Construcción de lenguajes mediante unión, intersección, concatenación y potencias",
        "\n  ".join([
            f'<rect x="38" y="86" width="350" height="245" rx="10" fill="{BG_CARD}" stroke="{STEEL}" stroke-width="1.8"/>',
            txt(213, 112, "Operaciones booleanas sobre Σ*", 13, "700", STEEL),
            f'<circle cx="170" cy="195" r="58" fill="{STEEL_SOFT}" fill-opacity="0.7" stroke="{STEEL}" stroke-width="2"/>',
            f'<circle cx="255" cy="195" r="58" fill="{BRICK_SOFT}" fill-opacity="0.7" stroke="{BRICK}" stroke-width="2"/>',
            txt(140, 195, "A - B", 12, "700", STEEL),
            txt(212, 195, "A ∩ B", 12, "700", INK),
            txt(285, 195, "B - A", 12, "700", BRICK),
            txt(213, 285, "Unión: A ∪ B  |  Complemento: Σ* - A", 12, "600", MUTED),
            txt(213, 308, "A · ∅ = ∅  (absorbente)  vs.  A · {λ} = A  (neutro)", 11.5, "600", BRICK),

            f'<rect x="415" y="86" width="505" height="245" rx="10" fill="{BG_CARD}" stroke="{BRICK}" stroke-width="2"/>',
            txt(667, 112, "Clausura de Kleene (A*) y Positiva (A+)", 13, "700", BRICK),
            box(440, 134, 100, 56, "A^0 = {λ}", "0 cadenas", "brick"),
            box(556, 134, 105, 56, "A^1 = A", "1 cadena", "steel"),
            box(677, 134, 105, 56, "A^2 = AA", "2 cadenas", "steel"),
            box(798, 134, 100, 56, "A^3, ...", "n cadenas", "steel"),
            f'<path d="M 560 205 L 560 218 L 895 218 L 895 205" fill="none" stroke="{STEEL}" stroke-width="2"/>',
            txt(727, 238, "A+ = A^1 ∪ A^2 ∪ A^3 ∪ ...", 12.5, "700", STEEL),
            f'<path d="M 442 252 L 442 266 L 895 266 L 895 252" fill="none" stroke="{BRICK}" stroke-width="2.2"/>',
            txt(668, 288, "A* = {λ} ∪ A+   (A* = A+ ⇔ λ ∈ A)", 13, "700", BRICK),
            txt(668, 312, "Reflexión: (AB)^R = B^R A^R", 11.5, "600", MUTED),
        ]),
    )

    # 2-0 Gramáticas formales
    figs["2-0-gramaticas-formales"] = svg_wrap(
        "Unidad 2 · De la representación finita a la Jerarquía de Chomsky",
        "Los autómatas procesan cadenas; las gramáticas generan cadenas (De Castro Korgi, 2004)",
        "\n  ".join([
            box(40, 96, 200, 72, "2.1–2.2 Fundamentos", "Variables V, Terminales Σ, S", "steel"),
            box(275, 96, 205, 72, "2.3 Gramática Formal", "G = (V, Σ, P, S) y L(G)", "brick"),
            box(515, 96, 200, 72, "2.4 Tipos 0, 1, 2, 3", "Jerarquía de Chomsky", "steel"),
            box(750, 96, 175, 72, "2.5–2.6 Árboles", "⇒_lm, ⇒_rm, Ambigüedad", "brick"),
            arrow(240, 132, 272, 132, "", "brick"),
            arrow(480, 132, 512, 132, "", "brick"),
            arrow(715, 132, 747, 132, "", "brick"),
            box(100, 215, 760, 102, "Cuatro niveles de potencia generativa", "L₃ (Regulares)  ⊂  L₂ (Libres del contexto)  ⊂  L₁ (Contexto sensitivo)  ⊂  L₀ (Sin restricción)", "dark"),
        ]),
    )

    # 2-1 Representación de los lenguajes
    figs["2-1-representacion-de-los-lenguajes"] = svg_wrap(
        "2.1 Mecanismos de representación finita para lenguajes L ⊆ Σ*",
        "Cómo describir conjuntos infinitos con reglas finitas y precisas",
        "\n  ".join([
            box(55, 90, 250, 92, "1. Enfoque Descriptivo", "Extensión · Comprensión · Recursión · ER", "steel"),
            box(355, 90, 250, 92, "2. Enfoque Generativo", "Gramática formal G = (V, Σ, P, S)", "brick"),
            box(655, 90, 250, 92, "3. Enfoque Reconocedor", "Autómata o máquina abstracta M", "steel"),
            box(230, 232, 500, 86, "Lenguaje formal L ⊆ Σ* (finito o infinito)", "Nota teórica: existen lenguajes sin ninguna representación finita", "dark"),
            arrow(180, 182, 340, 230, "", "steel"),
            arrow(480, 182, 480, 230, "", "brick"),
            arrow(780, 182, 620, 230, "", "steel"),
        ]),
    )

    # 2-2 Conceptos básicos de gramáticas
    figs["2-2-conceptos-basicos-de-gramaticas"] = svg_wrap(
        "2.2 Anatomía de una producción y tránsito de formas sentenciales a sentencias",
        "Vocabulario total (V ∪ Σ) con V ∩ Σ = ∅",
        "\n  ".join([
            f'<rect x="40" y="88" width="420" height="238" rx="10" fill="{BG_CARD}" stroke="{STEEL}" stroke-width="1.8"/>',
            txt(250, 114, "Anatomía de una regla de producción", 13, "700", STEEL),
            box(65, 134, 155, 62, "Cabeza α", "≥ 1 variable de V", "brick"),
            arrow(220, 165, 275, 165, "produce", "brick"),
            box(280, 134, 155, 62, "Cuerpo β", "β ∈ (V ∪ Σ)*", "steel"),
            txt(250, 232, "Ejemplo BNF:  <id> → <letra><resto>", 12.5, "700", INK),
            txt(250, 258, "Variables V: se siguen expandiendo", 11.5, "600", MUTED),
            txt(250, 280, "Terminales Σ: símbolos finales (no cambian)", 11.5, "600", MUTED),
            txt(250, 304, "Axioma S ∈ V: punto de partida", 11.5, "600", MUTED),

            f'<rect x="490" y="88" width="430" height="238" rx="10" fill="{BG_CARD}" stroke="{BRICK}" stroke-width="2"/>',
            txt(705, 114, "De S a sentencias finales", 13, "700", BRICK),
            box(590, 132, 230, 42, "S (Axioma inicial)", "", "steel"),
            arrow(705, 174, 705, 198, "", "brick"),
            box(550, 200, 310, 48, "Formas sentenciales ∈ (V ∪ Σ)*", "Pueden mezclar variables y terminales", "white"),
            arrow(705, 248, 705, 272, "", "brick"),
            box(565, 274, 280, 42, "Sentencias w ∈ Σ* (sin variables)", "", "brick_solid"),
        ]),
    )

    # 2-3 Gramáticas formales
    figs["2-3-gramaticas-formales"] = svg_wrap(
        "2.3 Derivación directa (⇒_G) y metodología de prueba L(G) = L",
        "Reemplazo local uαv ⇒_G uβv y doble verificación: corrección + completitud",
        "\n  ".join([
            f'<rect x="40" y="88" width="880" height="110" rx="10" fill="{BG_CARD}" stroke="{STEEL}" stroke-width="1.8"/>',
            txt(480, 112, "Un paso de derivación directa:  γ₁ = u α v  ⇒_G  u β v = γ₂   (usando regla α → β ∈ P)", 13, "700", STEEL),
            box(105, 128, 80, 48, "u", "contexto", "white"),
            box(190, 128, 95, 48, "α", "cabeza", "brick"),
            box(290, 128, 80, 48, "v", "contexto", "white"),
            arrow(385, 152, 470, 152, "α → β", "brick"),
            box(485, 128, 80, 48, "u", "intacto", "white"),
            box(570, 128, 125, 48, "β", "cuerpo nuevo", "steel"),
            box(700, 128, 80, 48, "v", "intacto", "white"),

            box(40, 222, 425, 104, "1. Corrección: L(G) ⊆ L (sin intrusos)", "Toda cadena generada desde S cumple la regla de L (inducción en pasos k)", "steel"),
            box(495, 222, 425, 104, "2. Completitud: L ⊆ L(G) (sin olvidos)", "Toda cadena de L admite al menos una derivación S ⇒_G* w", "brick"),
        ]),
    )

    # 2-4 Tipos de gramáticas (Jerarquía de Chomsky)
    figs["2-4-tipos-de-gramaticas"] = svg_wrap(
        "2.4 Jerarquía de Chomsky: L₃ ⊊ L₂ ⊊ L₁ ⊊ L₀",
        "Cada nivel restringe las producciones y se corresponde con un modelo de autómata",
        "\n  ".join([
            f'<rect x="40" y="82" width="540" height="254" rx="14" fill="{STEEL_SOFT}" stroke="{INK}" stroke-width="2"/>',
            txt(310, 104, "Tipo 0 · Sin restricción (L₀) — Máquina de Turing", 12.5, "700", INK),
            f'<rect x="70" y="116" width="480" height="206" rx="12" fill="#E3ECF2" stroke="{STEEL}" stroke-width="1.8"/>',
            txt(310, 138, "Tipo 1 · Contexto sensitivo (L₁) — Autómata Linealmente Acotado", 12, "700", STEEL),
            f'<rect x="102" y="150" width="416" height="158" rx="10" fill="{BRICK_SOFT}" stroke="{BRICK}" stroke-width="2"/>',
            txt(310, 173, "Tipo 2 · Libres del contexto (L₂) — Autómata con Pila (AP)", 12, "700", BRICK_DARK),
            f'<rect x="138" y="186" width="344" height="106" rx="8" fill="{BG_CARD}" stroke="{BRICK}" stroke-width="2"/>',
            txt(310, 214, "Tipo 3 · Regulares (L₃)", 13, "700", BRICK),
            txt(310, 236, "Autómata Finito (AFD / AFN)", 12, "600", INK),
            txt(310, 258, "Testigo: a* b*", 11.5, "600", MUTED),

            box(608, 86, 314, 54, "Tipo 0: α → β (arbitraria)", "Permite borrar o acortar", "dark"),
            box(608, 150, 314, 54, "Tipo 1: |α| ≤ |β|", "Testigo: {a^n b^n c^n | n ≥ 1}", "steel"),
            box(608, 214, 314, 54, "Tipo 2: A → α (A ∈ V)", "Testigo: {a^n b^n | n ≥ 0}", "brick"),
            box(608, 278, 314, 54, "Tipo 3: A → aB | λ", "Lineal derecha o izquierda", "white"),
        ]),
    )

    # 2-5 Árboles y diagramas de derivación
    figs["2-5-arboles-y-diagramas-de-derivacion"] = svg_wrap(
        "2.5 Árbol de derivación y frontera (yield) para w = abba",
        "Gramática: S → AB,  A → a,  B → bBa | b  (⇒_lm y ⇒_rm producen el mismo árbol)",
        "\n  ".join([
            state(250, 102, 21, "S", accent="brick"),
            state(155, 175, 20, "A"),
            state(345, 175, 20, "B"),
            state(155, 252, 18, "a", final=True),
            state(265, 252, 18, "b", final=True),
            state(345, 252, 20, "B"),
            state(425, 252, 18, "a", final=True),
            state(345, 318, 18, "b", final=True),
            '<line x1="234" y1="116" x2="170" y2="158" stroke="#204254" stroke-width="2"/>',
            '<line x1="266" y1="116" x2="330" y2="158" stroke="#204254" stroke-width="2"/>',
            '<line x1="155" y1="195" x2="155" y2="234" stroke="#B94A3E" stroke-width="2"/>',
            '<line x1="330" y1="190" x2="278" y2="236" stroke="#B94A3E" stroke-width="2"/>',
            '<line x1="345" y1="195" x2="345" y2="232" stroke="#204254" stroke-width="2"/>',
            '<line x1="360" y1="190" x2="412" y2="236" stroke="#B94A3E" stroke-width="2"/>',
            '<line x1="345" y1="272" x2="345" y2="300" stroke="#B94A3E" stroke-width="2"/>',

            box(520, 96, 400, 66, "Frontera (yield): lectura izquierda → derecha", "Hojas terminales: a · b · b · a = abba", "brick"),
            box(520, 180, 400, 66, "Derivación más a la izquierda (⇒_lm)", "S ⇒ AB ⇒ aB ⇒ abBa ⇒ abba", "steel"),
            box(520, 264, 400, 66, "Derivación más a la derecha (⇒_rm)", "S ⇒ AB ⇒ AbBa ⇒ Abba ⇒ abba", "white"),
        ]),
    )

    # 2-6 Ambigüedad
    figs["2-6-ambiguedad"] = svg_wrap(
        "2.6 Ambigüedad: dos árboles distintos para 1 + 1 * 0",
        "Sin jerarquía de precedencia (E, T, F), una misma cadena admite interpretaciones opuestas",
        "\n  ".join([
            f'<rect x="38" y="82" width="428" height="252" rx="10" fill="{BG_CARD}" stroke="{STEEL}" stroke-width="1.8"/>',
            txt(252, 106, "Árbol 1: agrupa 1 + (1 * 0) = 1", 13, "700", STEEL),
            state(252, 142, 16, "S"),
            state(165, 200, 15, "S"), state(252, 200, 15, "+", accent="brick"), state(340, 200, 15, "S"),
            state(165, 262, 15, "1", final=True),
            state(275, 262, 15, "1", final=True), state(340, 262, 15, "*", accent="brick"), state(405, 262, 15, "0", final=True),
            '<line x1="238" y1="152" x2="178" y2="188" stroke="#204254" stroke-width="2"/>',
            '<line x1="252" y1="158" x2="252" y2="185" stroke="#204254" stroke-width="2"/>',
            '<line x1="266" y1="152" x2="327" y2="188" stroke="#204254" stroke-width="2"/>',
            '<line x1="165" y1="215" x2="165" y2="247" stroke="#B94A3E" stroke-width="2"/>',
            '<line x1="328" y1="211" x2="285" y2="249" stroke="#B94A3E" stroke-width="2"/>',
            '<line x1="340" y1="215" x2="340" y2="247" stroke="#B94A3E" stroke-width="2"/>',
            '<line x1="352" y1="211" x2="395" y2="249" stroke="#B94A3E" stroke-width="2"/>',
            txt(252, 316, "Prioriza '*' en la rama inferior", 11.5, "600", MUTED),

            f'<rect x="494" y="82" width="428" height="252" rx="10" fill="{BG_CARD}" stroke="{BRICK}" stroke-width="2"/>',
            txt(708, 106, "Árbol 2: agrupa (1 + 1) * 0 = 0", 13, "700", BRICK),
            state(708, 142, 16, "S", accent="brick"),
            state(620, 200, 15, "S"), state(708, 200, 15, "*", accent="brick"), state(795, 200, 15, "S"),
            state(555, 262, 15, "1", final=True), state(620, 262, 15, "+", accent="brick"), state(685, 262, 15, "1", final=True),
            state(795, 262, 15, "0", final=True),
            '<line x1="694" y1="152" x2="633" y2="188" stroke="#B94A3E" stroke-width="2"/>',
            '<line x1="708" y1="158" x2="708" y2="185" stroke="#B94A3E" stroke-width="2"/>',
            '<line x1="722" y1="152" x2="782" y2="188" stroke="#B94A3E" stroke-width="2"/>',
            '<line x1="608" y1="211" x2="565" y2="249" stroke="#204254" stroke-width="2"/>',
            '<line x1="620" y1="215" x2="620" y2="247" stroke="#204254" stroke-width="2"/>',
            '<line x1="632" y1="211" x2="675" y2="249" stroke="#204254" stroke-width="2"/>',
            '<line x1="795" y1="215" x2="795" y2="247" stroke="#204254" stroke-width="2"/>',
            txt(708, 316, "Solución: estratificar niveles E → T → F → N", 11.5, "700", BRICK),
        ]),
    )

    # 3-0 Máquinas de estado finito
    figs["3-0-maquinas-de-estado-finito"] = svg_wrap(
        "Unidad 3 · Máquinas de Estado Finito (MEF)",
        "De los modelos de Mealy y Moore a la minimización y límites de la memoria finita",
        "\n  ".join([
            box(45, 92, 200, 68, "3.1 Mealy y Moore", "Salida en arista vs. nodo", "steel"),
            box(280, 92, 200, 68, "3.2 Conversión", "Moore ↔ Mealy", "brick"),
            box(515, 92, 200, 68, "3.3 Equivalencia", "M₁ ≡ M₂ y AFN → AFD", "steel"),
            box(750, 92, 170, 68, "3.4–3.5 Reducción", "Particiones y M / ≡", "brick"),
            arrow(245, 126, 276, 126, "", "brick"),
            arrow(480, 126, 511, 126, "", "brick"),
            arrow(715, 126, 746, 126, "", "brick"),
            box(110, 212, 740, 102, "3.6 Historia y memoria finita", "El estado resume la historia pasada en ≤ |Q| clases; falla al contar sin límite (principio del palomar)", "dark"),
        ]),
    )

    # 3-1 Propiedades de MEF
    figs["3-1-propiedades-de-las-maquinas-de-estado-finito"] = svg_wrap(
        "3.1 Máquinas de transición (Mealy) vs. Máquinas de estado (Moore)",
        "Detector de '01': dónde se produce la salida y longitud resultante para entrada w",
        "\n  ".join([
            f'<rect x="38" y="84" width="428" height="246" rx="10" fill="{BG_CARD}" stroke="{STEEL}" stroke-width="1.8"/>',
            badge(56, 96, 160, "MEALY: ω : Q × Σ → Δ", STEEL),
            state(150, 195, 28, "q0", initial=True),
            state(340, 195, 28, "q1", accent="brick"),
            curved_arrow("M 176 180 Q 245 142 314 180", 245, 148, "0 / 0", "steel"),
            curved_arrow("M 314 212 Q 245 250 176 212", 245, 245, "1 / 1", "brick"),
            txt(252, 285, "Salida en la TRANSICIÓN (flecha)", 12, "700", STEEL),
            txt(252, 308, "Para |w| = m, emite m símbolos", 11.5, "600", MUTED),

            f'<rect x="494" y="84" width="428" height="246" rx="10" fill="{BG_CARD}" stroke="{BRICK}" stroke-width="2"/>',
            badge(512, 96, 150, "MOORE: ω : Q → Δ", BRICK),
            state(585, 195, 26, "q0", "ω=0", initial=True),
            state(715, 195, 26, "q1", "ω=0"),
            state(845, 195, 26, "q2", "ω=1", final=True),
            arrow(611, 195, 686, 195, "0", "steel"),
            arrow(741, 195, 816, 195, "1", "brick"),
            curved_arrow("M 830 220 Q 715 262 602 220", 715, 255, "1", "steel"),
            txt(708, 285, "Salida dentro del ESTADO (nodo)", 12, "700", BRICK),
            txt(708, 308, "Para |w| = m, emite m + 1 símbolos (incluye ω(q0))", 11.5, "600", MUTED),
        ]),
    )

    # 3-2 Conversión Mealy <-> Moore
    figs["3-2-conversion-entre-maquinas-de-transicion-y-estados"] = svg_wrap(
        "3.2 Conversión bidireccional: Moore → Mealy y Mealy → Moore",
        "Equivalencia entrada–salida módulo símbolo inicial ω(q₀)",
        "\n  ".join([
            f'<rect x="38" y="86" width="426" height="242" rx="10" fill="{BG_CARD}" stroke="{STEEL}" stroke-width="1.8"/>',
            txt(251, 112, "Moore → Mealy (conserva los estados)", 13, "700", STEEL),
            state(115, 195, 24, "q", "ω(q)"),
            state(235, 195, 24, "p", "y = 1", accent="brick"),
            arrow(139, 195, 208, 195, "a", "steel"),
            arrow(268, 195, 315, 195, "", "brick"),
            state(348, 195, 22, "q"),
            state(430, 195, 22, "p"),
            arrow(370, 195, 405, 195, "a / 1", "brick"),
            txt(251, 275, "ω_Mealy(q, a) = ω_Moore(δ(q, a))", 12, "700", INK),
            txt(251, 302, "Se traslada la salida del destino a la flecha", 11.5, "500", MUTED),

            f'<rect x="496" y="86" width="426" height="242" rx="10" fill="{BG_CARD}" stroke="{BRICK}" stroke-width="2"/>',
            txt(709, 112, "Mealy → Moore (desdoblamiento Q × Δ)", 13, "700", BRICK),
            state(585, 195, 26, "q1", "entran 0, 1"),
            arrow(525, 175, 558, 186, "0/0", "steel"),
            arrow(525, 215, 558, 204, "1/1", "brick"),
            arrow(620, 195, 685, 162, "", "steel"),
            arrow(620, 195, 685, 228, "", "brick"),
            box(690, 134, 205, 46, "Copia C = (q1, 0)", "ω(C) = 0", "steel"),
            box(690, 204, 205, 46, "Copia D = (q1, 1)", "ω(D) = 1", "brick"),
            txt(709, 282, "Cada salida entrante distinta crea una copia (q, y)", 11.5, "700", INK),
            txt(709, 304, "Todas las copias de q comparten las salidas δ", 11.5, "500", MUTED),
        ]),
    )

    # 3-3 Equivalencia de máquinas
    figs["3-3-equivalencia-de-maquinas-de-estado-finito"] = svg_wrap(
        "3.3 Equivalencia externa (M₁ ≡ M₂) y determinización AFN-λ → AFN → AFD",
        "Dos máquinas son equivalentes si producen la misma respuesta para toda cadena w ∈ Σ*",
        "\n  ".join([
            f'<rect x="38" y="84" width="415" height="244" rx="10" fill="{BG_CARD}" stroke="{STEEL}" stroke-width="1.8"/>',
            txt(245, 110, "Equivalencia entrada–salida (M₁ ≡ M₂)", 13, "700", STEEL),
            box(70, 136, 145, 56, "Máquina M₁", "3 estados", "steel"),
            box(70, 214, 145, 56, "Máquina M₂", "2 estados", "brick"),
            box(265, 165, 165, 76, "∀ w ∈ Σ*", "ω̂₁(q₀₁, w) = ω̂₂(q₀₂, w)", "dark"),
            arrow(215, 164, 262, 192, "", "steel"),
            arrow(215, 242, 262, 214, "", "brick"),
            txt(245, 304, "En aceptadores: L(M₁) = L(M₂)", 12, "700", BRICK),

            f'<rect x="478" y="84" width="444" height="244" rx="10" fill="{BG_CARD}" stroke="{BRICK}" stroke-width="2"/>',
            txt(700, 110, "Equivalencia de aceptadores finitos", 13, "700", BRICK),
            box(502, 142, 110, 60, "AFN-λ", "Con λ-saltos", "white"),
            arrow(612, 172, 650, 172, "λ[q]", "brick"),
            box(654, 142, 105, 60, "AFN", "No det.", "steel"),
            arrow(759, 172, 797, 172, "P(Q)", "brick"),
            box(801, 142, 100, 60, "AFD", "Det.", "brick_solid"),
            box(510, 228, 385, 76, "Construcción de subconjuntos", "Cada estado del AFD representa un conjunto S ⊆ Q de estados activos simultáneamente", "steel"),
        ]),
    )

    # 3-4 Estados equivalentes
    figs["3-4-estados-equivalentes"] = svg_wrap(
        "3.4 Refinamiento sucesivo de particiones (k-equivalencia ≡_k)",
        "Los estados se subdividen en cajas cada vez más finas hasta estabilizarse (P_{k+1} = P_k)",
        "\n  ".join([
            box(40, 100, 170, 180, "P₀ (k = 0)", "AFD: {F} vs {Q \\ F}\n[q₀,q₁,q₃] | [q₂,q₄]", "steel"),
            arrow(210, 190, 250, 190, "δ(q,a)", "brick"),
            box(254, 100, 200, 180, "P₁ (k = 1)", "q₀ se separa de q₁,q₃\n[q₀] | [q₁,q₃] | [q₂,q₄]", "brick"),
            arrow(454, 190, 494, 190, "δ(q,a)", "brick"),
            box(498, 100, 200, 180, "P₂ = P₁ (Estable)", "No hay más divisiones\n⇒  ≡  =  ≡₁", "dark"),
            arrow(698, 190, 738, 190, "fusiona", "steel"),
            box(742, 100, 180, 180, "Clases finales", "C₀ = {q₀}\nC₁ = {q₁, q₃}\nC₂ = {q₂, q₄}", "brick"),
            txt(480, 316, "Cota de Moore (1956): con n = |Q| estados, el refinamiento converge en a lo sumo n - 1 pasos", 12, "700", STEEL),
        ]),
    )

    # 3-5 Reducción y prueba de equivalencia
    figs["3-5-reduccion-de-estados-y-prueba-de-equivalencia"] = svg_wrap(
        "3.5 Minimización de estados: tabla de pares y máquina cociente M / ≡",
        "1) Quitar inaccesibles (ALC) → 2) Marcar pares distinguibles → 3) Fusionar clases equivalentes",
        "\n  ".join([
            f'<rect x="38" y="86" width="380" height="240" rx="10" fill="{BG_CARD}" stroke="{STEEL}" stroke-width="1.8"/>',
            txt(228, 112, "Tabla triangular de pares distinguibles", 12.5, "700", STEEL),
            # Mini grid
            box(70, 134, 65, 36, "q1", "", "white"), box(135, 134, 65, 36, "× (1)", "", "brick"),
            box(70, 170, 65, 36, "q2", "", "white"), box(135, 170, 65, 36, "× (0)", "", "brick"), box(200, 170, 65, 36, "× (0)", "", "brick"),
            box(70, 206, 65, 36, "q3", "", "white"), box(135, 206, 65, 36, "× (1)", "", "brick"), box(200, 206, 65, 36, "≡", "", "steel"), box(265, 206, 65, 36, "× (0)", "", "brick"),
            box(70, 242, 65, 36, "q4", "", "white"), box(135, 242, 65, 36, "× (0)", "", "brick"), box(200, 242, 65, 36, "× (0)", "", "brick"), box(265, 242, 65, 36, "≡", "", "steel"), box(330, 242, 65, 36, "× (0)", "", "brick"),
            txt(167, 298, "q₀", 11.5, "700", MUTED), txt(232, 298, "q₁", 11.5, "700", MUTED), txt(297, 298, "q₂", 11.5, "700", MUTED), txt(362, 298, "q₃", 11.5, "700", MUTED),

            arrow(422, 206, 466, 206, "colapsa", "brick"),
            f'<rect x="470" y="86" width="452" height="240" rx="10" fill="{BG_CARD}" stroke="{BRICK}" stroke-width="2"/>',
            txt(696, 112, "Máquina cociente mínima M_min = M / ≡", 12.5, "700", BRICK),
            state(545, 195, 28, "C0", "{q0}", initial=True),
            state(695, 195, 28, "C1", "{q1,q3}"),
            state(845, 195, 28, "C2", "{q2,q4}", final=True),
            arrow(573, 195, 664, 195, "0, 1", "steel"),
            arrow(723, 195, 814, 195, "1", "brick"),
            curved_arrow("M 683 170 Q 695 130 707 170", 695, 134, "0", "steel"),
            curved_arrow("M 833 170 Q 845 130 857 170", 845, 134, "0, 1", "brick"),
            txt(696, 298, "Única salvo renombramiento (Teorema de Myhill-Nerode)", 11.5, "700", INK),
        ]),
    )

    # 3-6 Historia y memoria finita
    figs["3-6-historia-de-maquinas-y-memoria-finita"] = svg_wrap(
        "3.6 Memoria finita de orden k y evolución histórica (1936–1959)",
        "El estado resume la historia de entradas; ventana deslizante de orden k",
        "\n  ".join([
            f'<rect x="38" y="82" width="884" height="106" rx="10" fill="{BG_CARD}" stroke="{STEEL}" stroke-width="1.8"/>',
            txt(480, 106, "Máquina definida de orden k = 2: el estado solo depende de los últimos k símbolos", 12.5, "700", STEEL),
            tape(105, 122, ["0", "1", "0", "1", "1"], 52, 38),
            f'<rect x="261" y="117" width="104" height="48" rx="6" fill="none" stroke="{BRICK}" stroke-width="2.5"/>',
            txt(313, 178, "sufijo z ∈ Σ²", 11, "700", BRICK),
            arrow(375, 141, 470, 141, "determina", "brick"),
            box(478, 118, 410, 48, "Mismo estado destino δ̂(p, z) = δ̂(q, z)", "Ejemplo contrario: paridad de unos NO tiene orden k finito", "steel"),

            txt(480, 215, "Hitos históricos de los autómatas finitos", 12.5, "700", INK),
            box(40, 230, 155, 86, "1936 · Turing", "Máquina de Turing", "dark"),
            box(215, 230, 165, 86, "1943 · McCulloch-Pitts", "Redes lógicas finitas", "steel"),
            box(400, 230, 165, 86, "1954–56 · Huffman", "Mealy, Moore, Kleene", "brick"),
            box(585, 230, 165, 86, "1957–58 · Myhill", "Nerode (autómata mín.)", "steel"),
            box(770, 230, 150, 86, "1959 · Rabin-Scott", "AFD/AFN modernos", "dark"),
            arrow(195, 273, 212, 273, "", "brick"),
            arrow(380, 273, 397, 273, "", "brick"),
            arrow(565, 273, 582, 273, "", "brick"),
            arrow(750, 273, 767, 273, "", "brick"),
        ]),
    )

    # 4-0 Lenguajes de estado finito
    figs["4-0-lenguajes-de-estado-finito"] = svg_wrap(
        "Unidad 4 · Triángulo de equivalencia de los Lenguajes Regulares (Tipo 3)",
        "Tres formalismos distintos que describen exactamente la misma familia de lenguajes",
        "\n  ".join([
            box(340, 86, 280, 68, "Expresiones Regulares (r)", "Enfoque algebraico (+, ·, *)", "brick"),
            box(70, 234, 290, 74, "Autómatas Finitos (AFD / AFN)", "Enfoque operacional (reconocedores)", "steel"),
            box(600, 234, 290, 74, "Gramáticas Regulares (Tipo 3)", "Enfoque generativo (A → aB | λ)", "steel"),
            box(380, 188, 200, 48, "Lenguajes Regulares", "L₃", "dark"),
            arrow(340, 138, 215, 230, "Thompson (Kleene I)", "brick", dy=-4),
            arrow(255, 230, 380, 154, "Arden (Kleene II)", "steel", dy=14),
            arrow(360, 272, 595, 272, "Teoremas 4.7.2 ↔ 4.7.3", "brick"),
            arrow(600, 146, 730, 230, "Equivalencia", "steel"),
        ]),
    )

    # 4-1 Aceptadores de estado finito
    figs["4-1-aceptadores-de-estado-finito"] = svg_wrap(
        "4.1 Tres modelos equivalentes: AFD, AFN y AFN-λ",
        "Determinismo (1 camino) vs. no determinismo (ramas paralelas) vs. transiciones espontáneas λ",
        "\n  ".join([
            f'<rect x="36" y="84" width="280" height="246" rx="10" fill="{BG_CARD}" stroke="{STEEL}" stroke-width="1.8"/>',
            badge(54, 96, 130, "AFD: Q × Σ → Q", STEEL),
            state(100, 185, 22, "q0", initial=True),
            state(235, 185, 22, "q1", final=True),
            arrow(122, 185, 210, 185, "a (único)", "steel"),
            txt(176, 265, "Exactamente 1 transición", 12, "700", INK),
            txt(176, 290, "por cada par (q, a)", 11.5, "500", MUTED),

            f'<rect x="340" y="84" width="280" height="246" rx="10" fill="{BG_CARD}" stroke="{BRICK}" stroke-width="1.8"/>',
            badge(358, 96, 155, "AFN: Q × Σ → P(Q)", BRICK),
            state(400, 185, 22, "q0", initial=True),
            state(535, 145, 20, "q1"),
            state(535, 225, 20, "q2", final=True),
            arrow(420, 174, 513, 148, "1", "brick"),
            arrow(420, 196, 513, 222, "1", "brick"),
            txt(480, 275, "Múltiples ramas posibles", 12, "700", INK),
            txt(480, 298, "Acepta si ≥ 1 rama llega a F", 11.5, "500", MUTED),

            f'<rect x="644" y="84" width="280" height="246" rx="10" fill="{BG_CARD}" stroke="{INK}" stroke-width="1.8"/>',
            badge(662, 96, 210, "AFN-λ: Q × (Σ ∪ {λ}) → P(Q)", INK),
            state(695, 185, 20, "q0", initial=True),
            state(785, 185, 20, "q1"),
            state(875, 185, 20, "q2", final=True),
            arrow(715, 185, 762, 185, "λ", "brick"),
            arrow(805, 185, 852, 185, "λ", "brick"),
            txt(784, 265, "Clausura-λ: E(q0) = {q0, q1, q2}", 12, "700", BRICK),
            txt(784, 290, "AFN-λ ≡ AFN ≡ AFD", 12, "700", STEEL),
        ]),
    )

    # 4-2 Aceptadores y gramáticas regulares
    figs["4-2-aceptadores-de-estado-finito-y-gramaticas-regulares"] = svg_wrap(
        "4.2 Traducción directa entre Autómata Finito y Gramática Regular",
        "Cada transición δ(q, a) = p equivale a la producción q → ap; cada estado final p ∈ F equivale a p → λ",
        "\n  ".join([
            f'<rect x="40" y="88" width="415" height="236" rx="10" fill="{BG_CARD}" stroke="{STEEL}" stroke-width="1.8"/>',
            txt(247, 114, "Autómata Finito (AFD / AFN)", 13, "700", STEEL),
            state(115, 190, 24, "S", initial=True),
            state(245, 190, 24, "A"),
            state(375, 190, 24, "B", final=True),
            curved_arrow("M 105 168 Q 115 130 125 168", 115, 134, "0", "steel"),
            arrow(139, 190, 218, 190, "1", "brick"),
            curved_arrow("M 235 168 Q 245 130 255 168", 245, 134, "0", "steel"),
            arrow(269, 190, 348, 190, "1", "brick"),
            curved_arrow("M 365 168 Q 375 130 385 168", 375, 134, "0", "steel"),
            txt(247, 282, "Acepta cadenas con exactamente dos unos", 12, "600", MUTED),

            arrow(462, 206, 502, 206, "↔", "brick"),
            f'<rect x="506" y="88" width="415" height="236" rx="10" fill="{BG_CARD}" stroke="{BRICK}" stroke-width="2"/>',
            txt(713, 114, "Gramática Regular Estricta (Tipo 3)", 13, "700", BRICK),
            box(540, 136, 345, 44, "S  →  0S  |  1A", "desde estado S", "steel"),
            box(540, 192, 345, 44, "A  →  0A  |  1B", "desde estado A", "steel"),
            box(540, 248, 345, 52, "B  →  0B  |  λ", "B ∈ F aporta la regla B → λ", "brick"),
        ]),
    )

    # 4-3 Expresiones regulares y Kleene
    figs["4-3-expresiones-regulares-y-aceptadores-de-estado-finito"] = svg_wrap(
        "4.3 Teorema de Kleene: Construcción de Thompson (I) y Eliminación de estados (II)",
        "Bloques modulares unidos por λ-transiciones y reducción algebraica R'ᵢⱼ = Rᵢⱼ + Rᵢₖ(Rₖₖ)*Rₖⱼ",
        "\n  ".join([
            f'<rect x="38" y="84" width="460" height="246" rx="10" fill="{BG_CARD}" stroke="{STEEL}" stroke-width="1.8"/>',
            txt(268, 110, "Síntesis de Thompson: estrella de Kleene r*", 12.5, "700", STEEL),
            state(90, 200, 18, "i", initial=True),
            box(165, 174, 150, 52, "M(r)", "i₁ → ... → f₁", "steel"),
            state(400, 200, 18, "f", final=True),
            arrow(108, 200, 162, 200, "λ", "brick"),
            arrow(315, 200, 378, 200, "λ", "brick"),
            curved_arrow("M 100 182 Q 245 120 390 182", 245, 136, "λ (acepta λ)", "steel"),
            curved_arrow("M 295 228 Q 240 278 185 228", 240, 282, "λ (repite r)", "brick"),
            txt(268, 312, "Unión (paralelo) · Concatenación (serie) · Estrella (lazo)", 11.5, "600", MUTED),

            f'<rect x="520" y="84" width="402" height="246" rx="10" fill="{BG_CARD}" stroke="{BRICK}" stroke-width="2"/>',
            txt(721, 108, "Análisis: Lema de Arden y eliminación de qₖ", 12.5, "700", BRICK),
            state(585, 192, 20, "qᵢ"),
            state(720, 192, 20, "qₖ", accent="brick"),
            state(855, 192, 20, "qⱼ"),
            arrow(605, 192, 697, 192, "Rᵢₖ", "steel"),
            arrow(740, 192, 832, 192, "Rₖⱼ", "steel"),
            curved_arrow("M 708 174 Q 720 138 732 174", 720, 142, "Rₖₖ", "brick"),
            arrow(720, 215, 720, 248, "eliminar qₖ", "brick", dy=4, dx=44),
            box(548, 252, 345, 62, "R'ᵢⱼ = Rᵢⱼ + Rᵢₖ (Rₖₖ)* Rₖⱼ", "Arden: X = AX + B ⇒ X = A*B (si λ ∉ A)", "dark"),
        ]),
    )

    # 4-4 Propiedades de los lenguajes regulares
    figs["4-4-propiedades-de-los-lenguajes-de-estado-finito"] = svg_wrap(
        "4.4 Lema de bombeo regular (w = uvx) y autómata producto",
        "Todo camino suficientemente largo (|w| ≥ n) repite un estado q formando un ciclo v bombeable",
        "\n  ".join([
            f'<rect x="38" y="86" width="510" height="242" rx="10" fill="{BG_CARD}" stroke="{BRICK}" stroke-width="2"/>',
            txt(293, 112, "Lema de bombeo: descomposición w = u · v · x", 13, "700", BRICK),
            state(110, 205, 24, "q₀", initial=True),
            state(270, 205, 26, "q", "repetido", accent="brick"),
            state(455, 205, 24, "p_f", "∈ F", final=True),
            arrow(134, 205, 241, 205, "u", "steel"),
            arrow(296, 205, 428, 205, "x", "steel"),
            curved_arrow("M 255 180 Q 270 125 285 180", 270, 132, "v  (|v| ≥ 1, |uv| ≤ n)", "brick"),
            txt(293, 272, "Entonces u vⁱ x ∈ L para todo i = 0, 1, 2, ...", 12.5, "700", INK),
            txt(293, 298, "Ejemplo: en {a^n b^n}, bombear v = a^s rompe #a = #b", 11.5, "600", MUTED),

            f'<rect x="572" y="86" width="350" height="242" rx="10" fill="{BG_CARD}" stroke="{STEEL}" stroke-width="1.8"/>',
            txt(747, 112, "Autómata producto M₁ × M₂", 13, "700", STEEL),
            box(598, 136, 298, 52, "Estados: Q₁ × Q₂", "Simula M₁ y M₂ en paralelo", "steel"),
            box(598, 202, 298, 104, "Elige F según operación:", "• Intersección: F₁ × F₂\n• Diferencia: F₁ × (Q₂ - F₂)\n• Unión: (F₁×Q₂) ∪ (Q₁×F₂)", "white"),
        ]),
    )

    # 5-0 Autómatas Pushdown
    figs["5-0-automatas-pushdown"] = svg_wrap(
        "Unidad 5 · Autómatas Pushdown (AP) y Lenguajes Independientes del Contexto",
        "Al añadir una pila LIFO al control finito, el modelo no determinista iguala a las GIC",
        "\n  ".join([
            box(45, 92, 250, 74, "5.1–5.2 Modelo Pushdown", "Cinta + Pila LIFO (AFPD vs. AFPN)", "steel"),
            box(345, 92, 260, 74, "5.3 Propios y sin ciclos", "Evitar bucles-λ vía FNG", "brick"),
            box(655, 92, 265, 74, "5.4–5.5 GIC ⇔ AFPN", "3 estados ↔ Variables triples", "steel"),
            arrow(295, 129, 341, 129, "", "brick"),
            arrow(605, 129, 651, 129, "", "brick"),
            box(95, 208, 770, 108, "Separación estricta de clases (5.6 Ambigüedad y determinismo)", "Regulares (L₃)  ⊊  L(AFPD)  ⊊  LIC No Ambiguos  ⊊  L(AFPN) = LIC (Tipo 2)", "dark"),
        ]),
    )

    # 5-1 Introducción a AP
    figs["5-1-introduccion"] = svg_wrap(
        "5.1 Arquitectura de un autómata de cinta con pila LIFO",
        "Cinta de entrada de solo lectura + unidad de control finita + pila ilimitada con acceso en el tope",
        "\n  ".join([
            f'<rect x="40" y="92" width="380" height="106" rx="10" fill="{BG_CARD}" stroke="{STEEL}" stroke-width="1.8"/>',
            txt(230, 116, "Cinta de entrada (solo lectura, avance →)", 12.5, "700", STEEL),
            tape(82, 134, ["a", "a", "b", "b", "λ"], 58, 38, 1),
            arrow(170, 178, 225, 224, "lee 'a'", "brick", dx=-28),

            box(110, 228, 255, 84, "Unidad de Control Finita", "Estado q ∈ Q y función Δ", "dark"),

            f'<rect x="465" y="92" width="455" height="226" rx="10" fill="{BG_CARD}" stroke="{BRICK}" stroke-width="2"/>',
            txt(692, 116, "Pila auxiliar LIFO (Last-In, First-Out)", 12.5, "700", BRICK),
            box(515, 138, 135, 36, "Tope: A", "", "brick"),
            box(515, 178, 135, 36, "A", "", "steel"),
            box(515, 218, 135, 36, "...", "", "white"),
            box(515, 258, 135, 36, "Fondo: z₀", "", "white"),
            arrow(365, 265, 505, 156, "apila / desapila", "brick", dy=-10),
            txt(785, 165, "Ejemplo {aⁿ bⁿ}:", 12.5, "700", INK),
            txt(785, 192, "• Cada 'a' apila A", 12, "600", STEEL),
            txt(785, 216, "• Cada 'b' desapila A", 12, "600", BRICK),
            txt(785, 240, "• Tope z₀ al final ⇒ Acepta", 12, "700", INK),
            txt(785, 280, "2 pilas ≡ Máquina de Turing", 11.5, "600", MUTED),
        ]),
    )

    # 5-2 Aceptadores pushdown
    figs["5-2-aceptadores-pushdown"] = svg_wrap(
        "5.2 Paso computacional (q, au, Aβ) ⊢ (p, u, γβ) y jerarquía AFPD ⊊ AFPN",
        "Operaciones en el tope de la pila y diferencia entre aceptación determinista y no determinista",
        "\n  ".join([
            f'<rect x="38" y="84" width="470" height="246" rx="10" fill="{BG_CARD}" stroke="{STEEL}" stroke-width="1.8"/>',
            txt(273, 110, "Efecto de (p, γ) ∈ Δ(q, a, A) sobre la pila", 12.5, "700", STEEL),
            box(60, 132, 130, 50, "γ = λ", "Desapila (pop A)", "brick"),
            box(208, 132, 130, 50, "γ = A", "Preserva el tope", "steel"),
            box(356, 132, 130, 50, "γ = BA", "Apila B sobre A", "dark"),
            box(62, 208, 422, 102, "Dos criterios equivalentes en AFPN:", "• Estado final L(M): termina en p ∈ F\n• Pila vacía N(M): deja pila = λ\n(En AFPD, pila vacía es estrictamente más débil)", "white"),

            f'<rect x="532" y="84" width="390" height="246" rx="10" fill="{BG_CARD}" stroke="{BRICK}" stroke-width="2"/>',
            txt(727, 110, "Separación AFPD vs. AFPN", 12.5, "700", BRICK),
            box(560, 136, 334, 72, "AFPD acepta {w c w^R}", "El marcador 'c' indica la mitad exacta", "steel"),
            box(560, 224, 334, 82, "Solo AFPN acepta {w w^R}", "Sin marcador central, debe adivinar la mitad usando ramas no deterministas", "brick"),
        ]),
    )

    # 5-3 Aceptadores propios y sin ciclos
    figs["5-3-aceptadores-propios-y-sin-ciclos"] = svg_wrap(
        "5.3 Eliminación de estados improductivos y bucles-λ (Aceptador sin ciclos)",
        "Conversión constructiva vía gramática bien formada y Forma Normal de Greibach",
        "\n  ".join([
            f'<rect x="38" y="86" width="360" height="240" rx="10" fill="{BRICK_SOFT}" stroke="{BRICK}" stroke-width="2"/>',
            txt(218, 112, "AP arbitrario (con anomalías)", 12.5, "700", BRICK),
            state(100, 185, 22, "q0", initial=True),
            state(215, 185, 22, "q1"),
            state(340, 145, 20, "q2", final=True),
            state(340, 240, 20, "q4", "muerto"),
            arrow(122, 185, 190, 185, "a", "steel"),
            arrow(235, 174, 318, 148, "b", "steel"),
            arrow(235, 196, 318, 232, "c", "brick"),
            curved_arrow("M 203 163 Q 215 122 227 163", 215, 128, "λ, A / AA (bucle ∞)", "brick"),
            txt(218, 304, "Riesgo: ciclo infinito sin leer cinta", 11.5, "700", BRICK_DARK),

            arrow(404, 206, 474, 206, "FNG", "brick"),
            f'<rect x="480" y="86" width="442" height="240" rx="10" fill="{BG_CARD}" stroke="{STEEL}" stroke-width="2"/>',
            txt(701, 112, "AP propio y sin ciclos (tiempo real)", 12.5, "700", STEEL),
            box(508, 142, 386, 56, "Reglas FNG: A → aα  (a ∈ Σ, α ∈ V*)", "Cada transición consume 1 terminal de la entrada", "steel"),
            box(508, 214, 386, 90, "Terminación garantizada", "• Sin estados inalcanzables ni muertos\n• Toda cadena w de longitud n termina en n pasos\n• Pertinencia w ∈ L(M) siempre decidible", "dark"),
        ]),
    )

    # 5-4 Aceptadores pushdown para LIC
    figs["5-4-aceptadores-pushdown-para-lenguajes-independientes-al-contexto"] = svg_wrap(
        "5.4 Analizador descendente de 3 estados (GIC → AFPN, Teorema 5.4.1)",
        "Simula en q₁ una derivación más a la izquierda: la cinta consume x y la pila guarda α",
        "\n  ".join([
            state(115, 155, 28, "q0", "Inicio", initial=True),
            state(445, 155, 34, "q1", "Trabajo", accent="brick"),
            state(795, 155, 28, "q2", "Acepta", final=True),
            arrow(143, 155, 408, 155, "λ, z₀ / S z₀", "steel"),
            arrow(479, 155, 764, 155, "λ, z₀ / z₀", "brick"),
            curved_arrow("M 424 126 Q 445 70 466 126", 445, 86, "Expande: λ, A / u  |  Empareja: a, a / λ", "brick"),
            box(60, 232, 840, 88, "Invariante de la demostración (espejo derivación ↔ pila)", "Forma sentencial S ⇒*_lm xα  ⟺  (q₁, xy, S) ⊢*_M (q₁, y, α)   [x ya leída, α pendiente en pila]", "dark"),
        ]),
    )

    # 5-5 GIC para aceptadores pushdown
    figs["5-5-gramaticas-independientes-al-contexto-para-aceptadores-pushdown"] = svg_wrap(
        "5.5 Método de variables triples [q, A, p] (AFPN por pila vacía → GIC)",
        "Cada tripleta [q, A, p] genera las cadenas w que vacían A pasando del estado q al estado p",
        "\n  ".join([
            box(45, 92, 870, 62, "Equivalencia por tripla:   [q, A, rₖ] ⇒*_G w   ⟺   (q, w, A) ⊢*_M (rₖ, λ, λ)", "Para regla (r₀, Y₁ Y₂ ... Yₖ) ∈ Δ(q, a, A):   [q, A, rₖ] → a [r₀, Y₁, r₁] [r₁, Y₂, r₂] ··· [rₖ₋₁, Yₖ, rₖ]", "dark"),
            box(55, 184, 160, 74, "Consume 'a'", "q → r₀", "brick"),
            arrow(215, 221, 255, 221, "", "steel"),
            box(258, 184, 200, 74, "[r₀, Y₁, r₁] ⇒* w₁", "Vacía Y₁ (r₀ → r₁)", "steel"),
            arrow(458, 221, 498, 221, "", "steel"),
            box(501, 184, 200, 74, "[r₁, Y₂, r₂] ⇒* w₂", "Vacía Y₂ (r₁ → r₂)", "steel"),
            arrow(701, 221, 741, 221, "", "steel"),
            box(744, 184, 165, 74, "... [rₖ₋₁, Yₖ, rₖ]", "Vacía tope hasta rₖ", "brick"),
            txt(480, 304, "Regla inicial: S → [q₀, z₀, p] para todo p ∈ Q   |   Luego se eliminan tripletas inútiles", 12, "700", STEEL),
        ]),
    )

    # 5-6 Ambigüedad en AFPN
    figs["5-6-ambiguedad"] = svg_wrap(
        "5.6 Ambigüedad en AFPN y jerarquía dentro de los LIC",
        "Una GIC es ambigua ⟺ su AFPN descendente admite ≥ 2 cómputos exitosos para alguna cadena",
        "\n  ".join([
            f'<rect x="38" y="86" width="430" height="240" rx="10" fill="{BG_CARD}" stroke="{BRICK}" stroke-width="2"/>',
            txt(253, 112, "Dos cómputos de aceptación para 1 + 1 * 0", 12.5, "700", BRICK),
            box(58, 134, 125, 52, "(q₁, 1+1*0, Sz₀)", "Inicio en q₁", "steel"),
            arrow(183, 152, 240, 140, "S→S+S", "steel"),
            arrow(183, 170, 240, 188, "S→S*S", "brick"),
            box(245, 118, 205, 42, "Cómputo 1 (Árbol 1)", "1 + (1 * 0) → q₂", "steel"),
            box(245, 172, 205, 42, "Cómputo 2 (Árbol 2)", "(1 + 1) * 0 → q₂", "brick"),
            txt(253, 255, "No determinismo ≠ Ambigüedad:", 12, "700", INK),
            txt(253, 278, "Un AFPN no ambiguo puede tener ramas", 11.5, "500", MUTED),
            txt(253, 298, "fallidas y un único cómputo ganador.", 11.5, "500", MUTED),

            f'<rect x="492" y="86" width="430" height="240" rx="10" fill="{BG_CARD}" stroke="{STEEL}" stroke-width="1.8"/>',
            txt(707, 112, "Inclusiones estrictas en los LIC", 12.5, "700", STEEL),
            box(522, 134, 370, 38, "1. Regulares (Tipo 3)", "", "white"),
            box(522, 180, 370, 42, "2. LIC Deterministas: L(AFPD)", "Siempre tienen GIC no ambigua", "steel"),
            box(522, 230, 370, 42, "3. LIC No Ambiguos (ej. {ww^R})", "", "brick"),
            box(522, 280, 370, 38, "4. Todos los LIC (incluye inherentemente ambiguos)", "", "dark"),
        ]),
    )

    # 6-0 Lenguajes independientes del contexto
    figs["6-0-lenguajes-independientes-del-contexto"] = svg_wrap(
        "Unidad 6 · Ruta de simplificación y normalización de una GIC",
        "De una gramática arbitraria a las formas canónicas de Chomsky (FNC) y Greibach (FNG)",
        "\n  ".join([
            box(38, 102, 170, 66, "GIC arbitraria G", "Con defectos", "white"),
            arrow(208, 135, 240, 135, "", "brick"),
            box(244, 102, 210, 66, "6.1 Gramática Bien Formada", "Sin λ, unitarias ni inútiles", "steel"),
            arrow(454, 135, 505, 112, "", "brick"),
            arrow(454, 135, 505, 162, "", "steel"),
            box(510, 82, 200, 50, "6.2 FNC: A → BC | a", "Árbol binario / CYK", "brick"),
            box(510, 146, 200, 50, "6.2 FNG: A → aα", "Sin recursividad izq.", "steel"),
            arrow(710, 107, 745, 135, "", "brick"),
            arrow(710, 171, 745, 145, "", "steel"),
            box(748, 102, 175, 66, "6.3 Estructura LIC", "Bombeo, clausura, decisión", "dark"),
            box(80, 224, 800, 88, "Orden estricto de limpieza (6.1.5)", "1. Eliminar producciones-λ (ANUL)  →  2. Eliminar unitarias (UNIT)  →  3. Eliminar inútiles (TERM → ALC)", "brick"),
        ]),
    )

    # 6-1 Transformaciones elementales
    figs["6-1-transformaciones-elementales-de-gramaticas"] = svg_wrap(
        "6.1 Orden estricto para obtener una Gramática Bien Formada",
        "Cada paso puede generar defectos del paso siguiente, pero nunca reintroduce los anteriores",
        "\n  ".join([
            box(40, 96, 185, 76, "Paso 1: Quitar λ", "Calcular ANUL", "brick"),
            arrow(225, 134, 265, 134, "", "brick"),
            box(268, 96, 205, 76, "Paso 2: Quitar unitarias", "Calcular UNIT(A)", "steel"),
            arrow(473, 134, 513, 134, "", "brick"),
            box(516, 96, 185, 76, "Paso 3a: TERM", "Quitar no terminables", "steel"),
            arrow(701, 134, 738, 134, "", "brick"),
            box(741, 96, 180, 76, "Paso 3b: ALC", "Quitar inalcanzables", "dark"),
            box(40, 208, 425, 110, "¿Por qué 1 → 2 → 3?", "• Quitar λ crea unitarias (A→BC, C→λ ⇒ A→B)\n• Quitar unitarias puede aislar variables\n• Quitar inútiles al final nunca crea λ ni unitarias", "white"),
            box(495, 208, 425, 110, "¿Por qué TERM antes que ALC?", "Ejemplo: S → a | AB,  A → aA | λ\nSi haces ALC primero, B mantiene viva a A;\nal quitar luego B, A queda inalcanzable.", "brick"),
        ]),
    )

    # 6-2 Formas canónicas
    figs["6-2-formas-canonicas-de-gramaticas"] = svg_wrap(
        "6.2 Formas canónicas: Chomsky (FNC) + CYK vs. Greibach (FNG)",
        "FNC produce árboles binarios (2n - 1 pasos); FNG produce un terminal por paso (n pasos)",
        "\n  ".join([
            f'<rect x="38" y="84" width="445" height="246" rx="10" fill="{BG_CARD}" stroke="{BRICK}" stroke-width="2"/>',
            txt(260, 110, "Forma Normal de Chomsky (A → BC | a) + CYK", 12.5, "700", BRICK),
            box(62, 128, 396, 46, "Aislar terminales (T_a → a) y binarizar (m ≥ 3)", "2n - 1 pasos para |w| = n", "brick"),
            txt(260, 198, "Tabla dinámica CYK (w = bbab, S ∈ X₁,₄ ⇒ Acepta)", 11.5, "700", STEEL),
            box(64, 212, 92, 32, "j=1: {A}", "", "white"), box(162, 212, 92, 32, "j=2: ∅", "", "white"), box(260, 212, 92, 32, "j=3: {B}", "", "white"), box(358, 212, 96, 32, "j=4: {S,C}", "", "brick_solid"),
            box(64, 250, 92, 32, "{A}", "", "white"), box(162, 250, 92, 32, "{B,S}", "", "white"), box(260, 250, 92, 32, "{S,C}", "", "white"),
            box(64, 288, 92, 32, "{B,C}", "", "white"), box(162, 288, 92, 32, "{S,C}", "", "white"),

            f'<rect x="506" y="84" width="416" height="246" rx="10" fill="{BG_CARD}" stroke="{STEEL}" stroke-width="1.8"/>',
            txt(714, 110, "Forma Normal de Greibach (A → aα)", 12.5, "700", STEEL),
            box(532, 130, 364, 54, "1. Eliminar recursividad izquierda", "A → Aα | β  ⇒  A → β | βZ,  Z → α | αZ", "steel"),
            box(532, 196, 364, 54, "2. Ordenar A₁,...,Aₘ y sustituir", "Fase ascendente + fase descendente", "white"),
            box(532, 262, 364, 52, "n pasos para |w| = n", "Base de AFPN sin transiciones-λ", "dark"),
        ]),
    )

    # 6-3 Estructura de los LIC
    figs["6-3-estructura-de-los-lenguajes-independientes-al-contexto"] = svg_wrap(
        "6.3 Lema de bombeo para LIC: árbol binario en FNC y bombeo z = uvwxy",
        "En un árbol suficientemente alto (> |V|+2), una variable A se repite generando uvⁱwxⁱy ∈ L",
        "\n  ".join([
            state(255, 98, 20, "S", accent="steel"),
            state(115, 175, 18, "u", final=True),
            state(255, 175, 22, "A", "1.ª vez", accent="brick"),
            state(395, 175, 18, "y", final=True),
            state(175, 255, 18, "v", final=True),
            state(255, 255, 22, "A", "2.ª vez", accent="brick"),
            state(335, 255, 18, "x", final=True),
            state(255, 322, 18, "w", final=True),
            '<line x1="238" y1="108" x2="131" y2="164" stroke="#204254" stroke-width="2"/>',
            '<line x1="255" y1="118" x2="255" y2="152" stroke="#B94A3E" stroke-width="2.2"/>',
            '<line x1="272" y1="108" x2="379" y2="164" stroke="#204254" stroke-width="2"/>',
            '<line x1="240" y1="191" x2="190" y2="242" stroke="#B94A3E" stroke-width="2"/>',
            '<line x1="255" y1="197" x2="255" y2="232" stroke="#B94A3E" stroke-width="2.2"/>',
            '<line x1="270" y1="191" x2="320" y2="242" stroke="#B94A3E" stroke-width="2"/>',
            '<line x1="255" y1="277" x2="255" y2="304" stroke="#204254" stroke-width="2"/>',

            box(465, 92, 455, 108, "Condiciones del bombeo (|z| > n = 2^|V|)", "1. |vwx| ≤ n    (subárbol superior acotado)\n2. |vx| ≥ 1      (v o x no vacía)\n3. uvⁱwxⁱy ∈ L   para todo i ≥ 0", "brick"),
            box(465, 214, 455, 108, "No son LIC (contraejemplos clásicos)", "• {aⁿbⁿcⁿ}  • {ww | w ∈ {a,b}*}  • {aⁱbʲcᵏ | i ≤ j ≤ k}\nAdemás, los LIC NO son cerrados bajo ∩ ni complemento", "dark"),
        ]),
    )

    written: list[Path] = []
    for stem, content in figs.items():
        p = out_dir / f"{stem}.svg"
        p.write_text(content, encoding="utf-8")
        written.append(p)
    return written


def main() -> int:
    out_dir = Path("figuras")
    files = generate_all(out_dir)
    print(f"Generadas {len(files)} figuras SVG en {out_dir.resolve()}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
