# GEMINI.md — Harness del Proyecto

## 1. Contexto académico
- **Institución:** Universidad Vasco de Quiroga (UVAQ)
- **Programa:** Ingeniería en Sistemas y Seguridad Informática
- **Unidad de aprendizaje:** Teoría de la Computación (Clave: `ISYSI0430`)
- **Ciclo:** Primer Semestre (128 horas totales: 96 h bajo conducción docente, 32 h independientes)
- **Propósito:** Construcción matemática de la teoría de la computación mediante el diseño de autómatas, gramáticas y lenguajes abstractos como base para traductores y compiladores.

## 2. Estructura del repositorio
- `README.md`: Temario completo, actividades de aprendizaje, criterios de evaluación, referencias APA y estructura del repositorio.
- `GEMINI.md`: Harness del proyecto con reglas de estilo, notación y flujo de trabajo.
- `MEMORY.md`: Estado actual y bitácora de modificaciones (estrictamente **máximo 50 líneas**).
- `notas/`: 38 archivos Markdown organizados en 6 unidades (`X-0-<tema>.md`) y 32 subtemas (`X-Y-<subtema>.md`).
- `diapositivas/`: Presentaciones de apoyo para las sesiones del curso.
- `.referencias/`: Carpeta local (excluida en `.gitignore`) con los PDFs de consulta:
  - `Rodrigo De Castro Korgi Teoría de la Computación.pdf` (**texto principal**)
  - `Teoria Computacion tesis.pdf` (**referencia complementaria**)

## 3. Reglas de contenido y estilo
1. **Idioma y tono:** Español académico claro y riguroso. Mantener consistencia terminológica con el temario oficial de `README.md`.
2. **Bibliografía y citas (APA 7.ª edición):**
   - **Texto principal:** De Castro Korgi, R. (2004). *Teoría de la computación: Lenguajes, autómatas, gramáticas*. Universidad Nacional de Colombia.
   - **Complementaria:** Acevedo Juárez, A. (2006). *Teoría de la computación* [Tesis de licenciatura, Instituto Tecnológico de Celaya].
3. **Notación matemática y diagramas:**
   - Usar LaTeX en Markdown (`$...$` en línea y `$$...$$` en bloque).
   - Seguir la notación de De Castro Korgi (2004): alfabetos ($\Sigma$), cadenas ($u, v, w$), cadena vacía ($\lambda$), longitud ($|w|$), concatenación, potencia ($w^n$), reflexión ($w^R$), clausura de Kleene ($\Sigma^*, L^*$), clausura positiva ($\Sigma^+, L^+$), gramáticas ($G$) y autómatas ($M$).
   - Representar diagramas de transición de autómatas y árboles de derivación preferentemente con bloques `mermaid` (`stateDiagram-v2` o `flowchart LR` / `TD`) o tablas de transición en Markdown.
4. **Convenciones para archivos en `notas/`:**
   - Nombres en `kebab-case` (minúsculas, sin acentos ni caracteres especiales).
   - **Archivos de unidad (`X-0-<slug>.md`):** Título `# Unidad X: <Nombre>`, duración, competencia(s) a desarrollar y lista de enlaces a los archivos de sus subtemas.
   - **Archivos de subtema (`X-Y-<slug>.md`):** Título `# X.Y <Nombre>` y subtítulos `## X.Y.Z <Nombre>` según el temario. Al desarrollar el contenido de cada tema, incluir definiciones formales, explicación intuitiva, ejemplos paso a paso y ejercicios.

## 4. Gestión de la memoria (`MEMORY.md`)
- Antes de realizar cambios mayores, consultar `MEMORY.md` para revisar el estado actual.
- Al finalizar cualquier modificación relevante, registrar una entrada con formato `- YYYY-MM-DD: <descripción concisa y archivos afectados>`.
- **Restricción de longitud:** `MEMORY.md` **nunca debe superar las 50 líneas**. Cuando se acerque al límite, eliminar o resumir las entradas más antiguas u obsoletas preservando la sección de estado actual.
