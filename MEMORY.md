# MEMORY.md — Memoria y Registro de Modificaciones

> **Regla de mantenimiento:** Este archivo debe tener **como máximo 50 líneas**. Registrar cada cambio con `- YYYY-MM-DD: <descripción>` (del más reciente al más antiguo) y depurar entradas antiguas u obsoletas para no exceder el límite.

## Estado actual del repositorio
- **Temario y referencias (`README.md`):** Completo (Primer Semestre, clave `ISYSI0430`, referencias APA 7.ª ed. con De Castro Korgi como texto principal, estructura e índice de unidades).
- **Apuntes (`notas/`):** 38 archivos desarrollados completamente (6 unidades `X-0-*.md` y 32 subtemas `X-Y-*.md`) con teoría formal, notación LaTeX, diagramas `mermaid`, ejemplos paso a paso, ejercicios propuestos y referencias APA basadas en De Castro Korgi (2004) y Acevedo Juárez (2006).
- **Exportación a PDF (`convertir_notas_pdf.py` y `notas/pdf/`):** Script en Python con paleta clara *Industrial Brick* (`#B94A3E`, `#204254`, `#121B22`), soporte para KaTeX y Mermaid; 38 PDFs generados y verificados en `notas/pdf/`.
- **Figuras (`figuras/` y `generar_figuras.py`):** 38 diagramas vectoriales SVG con paleta *Industrial Brick*, integrados en `notas/`, `notas/pdf/` y `diapositivas/`.
- **Diapositivas (`diapositivas/`, `diapositivas/pdf/`, `convertir_diapositivas_pdf.py` y `.vscode/settings.json`):** 38 presentaciones Marp (366 diapositivas con figuras integradas), tema `diapositivas/industrial-brick.css` (claro + oscuras `lead`/`invert`), configuración Marp en `.vscode/settings.json` y 38 PDFs 16:9 generados y verificados en `diapositivas/pdf/`.

## Historial de cambios
- 2026-11-24: Creación de `convertir_diapositivas_pdf.py` y generación de los 38 PDFs 16:9 (366 páginas) en `diapositivas/pdf/` respetando `industrial-brick.css`, KaTeX y figuras SVG.
- 2026-11-24: Generación de 38 figuras SVG en `figuras/` (`generar_figuras.py`), integración en los 38 archivos de `notas/` y `diapositivas/`, soporte de imágenes en `convertir_notas_pdf.py` y regeneración de `notas/pdf/`.
- 2026-11-24: Creación de las 38 presentaciones Marp en `diapositivas/` (328 diapositivas), el tema `diapositivas/industrial-brick.css` (tema claro + diapositivas oscuras `lead`/`invert`) y `.vscode/settings.json`.
- 2026-11-24: Revisión pedagógica y adecuación de 16 archivos de `notas/` al nivel de primer semestre (glosas intuitivas, puentes previos a demostraciones y simplificación de jerga avanzada) con regeneración completa de `notas/pdf/`.
- 2026-11-24: Se agregó en `GEMINI.md` la regla de respetar el nivel de primer semestre para la creación de las notas.
- 2026-11-24: Creación de `convertir_notas_pdf.py` con tema claro *Industrial Brick* (KaTeX + Mermaid via Edge headless) y generación de los 38 PDFs en `notas/pdf/`.
- 2026-11-21: Desarrollo teórico completo de los 38 archivos de apuntes en `notas/` (Unidades 1 a 6) con definiciones formales, teoremas, diagramas `mermaid`, ejemplos resueltos, ejercicios propuestos y referencias APA.
- 2026-11-21: Se agregó la sección `## Estructura del repositorio` e índice de unidades en `README.md`; se ampliaron y mejoraron `GEMINI.md` (notación matemática, diagramas y flujo de trabajo) y `MEMORY.md` (sección de estado actual).
- 2026-11-21: Creación inicial de `GEMINI.md` (harness del proyecto) y `MEMORY.md` (registro de cambios con límite de 50 líneas).
- 2026-11-21: Creación de los 38 archivos Markdown base en `notas/` para las 6 unidades y 32 subtemas del temario.
- 2026-11-21: Organización de `## Referencias` en `README.md` en formato APA (7.ª ed.), definiendo a De Castro Korgi (2004) como texto principal y a Acevedo Juárez (2006) como referencia complementaria.
- 2026-11-21: Corrección del ciclo académico en `README.md` de `Cuarto Semestre` a `Primer Semestre`.
