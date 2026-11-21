# TeoriaComputacion
Notas del curso de Teoría de la Computación

## Temario

**Institución:** Universidad Vasco de Quiroga (UVAQ)  
**Programa:** Ingeniería en Sistemas y Seguridad Informática  
**Unidad de aprendizaje:** Teoría de la Computación  
**Ciclo:** Primer Semestre  
**Clave:** ISYSI0430  

### Propósito general de la unidad de aprendizaje
La unidad de aprendizaje muestra la construcción matemática de la teoría de la computación, mediante el diseño de autómatas y lenguajes abstractos como base para la construcción de traductores y compiladores.

---

### Temas y subtemas

#### 1. Introducción
- **Duración:** 3 horas
- **Competencia(s) a desarrollar:** Analiza los conceptos y notaciones de máquinas y lenguajes abstractos mediante su estudio y desarrollo de ejercicios como base para su diseño y construcción.
- **Subtemas:**
  - 1.1 Máquinas de información
  - 1.2 Máquinas abstractas y algoritmos
  - 1.3 Lenguajes abstractos
  - 1.4 Aceptadores, generadores y traductores
  - 1.5 Cadenas de lenguajes
  - 1.6 Cadenas y sus operaciones
  - 1.7 Operaciones sobre lenguajes

#### 2. Gramáticas Formales
- **Duración:** 20 horas
- **Competencia(s) a desarrollar:** Compara las principales clases de gramáticas, construyendo gramáticas generadoras de lenguajes para conocer la relación que guardan con las clases de lenguajes de la jerarquía de Chomsky.
- **Subtemas:**
  - 2.1 Representación de los lenguajes
  - 2.2 Conceptos básicos de gramáticas
  - 2.3 Gramáticas formales
  - 2.4 Tipos de gramáticas
    - 2.4.1 Gramáticas sin restricción
    - 2.4.2 Gramáticas de contexto sensitivo
    - 2.4.3 Gramáticas libres del contexto
    - 2.4.4 Gramáticas regulares
  - 2.5 Árboles y diagramas de derivación
  - 2.6 Ambigüedad

#### 3. Máquinas de Estado Finito
- **Duración:** 20 horas
- **Competencia(s) a desarrollar:** Estudia la formulación matemática del autómata más simple: máquina de estado finito con la solución de ejercicios de manera creativa y transformando máquinas equivalentes.
- **Subtemas:**
  - 3.1 Propiedades de las máquinas de estado finito
    - 3.1.1 Máquinas de transición
    - 3.1.2 Máquinas de estado
  - 3.2 Conversión entre máquinas de transición y estados
  - 3.3 Equivalencia de máquinas de estado finito
  - 3.4 Estados equivalentes
  - 3.5 Reducción de estados y prueba de equivalencia
  - 3.6 Historia de máquinas y memoria finita

#### 4. Lenguajes de Estado Finito
- **Duración:** 15 horas
- **Competencia(s) a desarrollar:** Diseña máquinas abstractas, lenguajes generados por gramáticas formales y expresiones regulares mediante la solución de ejercicios para analizar las relaciones que guardan entre ellos.
- **Subtemas:**
  - 4.1 Aceptadores de estado finito
  - 4.2 Aceptadores de estado finito y gramáticas regulares
  - 4.3 Expresiones regulares y aceptadores de estado finito
  - 4.4 Propiedades de los lenguajes de estado finito

#### 5. Autómatas Pushdown
- **Duración:** 20 horas
- **Competencia(s) a desarrollar:** Analiza el alcance de los autómatas de cinta con relación a los lenguajes independientes al contexto.
- **Subtemas:**
  - 5.1 Introducción
    - 5.1.1 Autómatas de cinta
  - 5.2 Aceptadores "pushdown"
  - 5.3 Aceptadores propios y sin ciclos
  - 5.4 Aceptadores "pushdown" para lenguajes independientes al contexto
    - 5.4.1 Análisis de sintaxis
    - 5.4.2 Construcción de analizadores de sintaxis "pushdown"
    - 5.4.3 Prueba de la construcción
  - 5.5 Gramáticas independientes al contexto para aceptadores "pushdown"
  - 5.6 Ambigüedad

#### 6. Lenguajes Independientes del Contexto
- **Duración:** 18 horas
- **Competencia(s) a desarrollar:** Estudia las diferentes formas y estructuras de las gramáticas independientes al contexto para desarrollar gramáticas eficientes.
- **Subtemas:**
  - 6.1 Transformaciones elementales de gramáticas
    - 6.1.1 Equivalencia de gramáticas
    - 6.1.2 Transformación de gramáticas mediante substitución y expansión
    - 6.1.3 Eliminación de producciones inútiles
    - 6.1.4 Reemplazo de producciones no generativas
    - 6.1.5 Gramáticas bien formadas
  - 6.2 Formas canónicas de gramáticas
    - 6.2.1 Gramáticas en forma normal
    - 6.2.2 Gramáticas en forma estándar
  - 6.3 Estructura de los lenguajes independientes al contexto

---

### Actividades de aprendizaje (Horas totales: 128)
- **Bajo conducción docente (96 horas):**
  - Aprendizaje basado en problemas
  - Exposición
  - Casos prácticos
- **Independientes (32 horas):**
  - Resúmenes
  - Aprendizaje basado en problemas
  - Investigación de tópicos y problemas específicos

---

### Criterios y procedimientos de evaluación y acreditación
- **Instrumentos:**
  - Listas de cotejo
  - Rúbrica
  - Portafolios de habilidades
- **Criterios normativos para la evaluación:**
  - La escala de evaluación es de 0-10
  - La calificación aprobatoria es de 6-10
  - La calificación no aprobatoria es de 0-5
- **Evaluación:**
  - Investigaciones: 20%
  - Exposición: 10%
  - Participación en clase: 10%
  - Casos prácticos y proyecto: 60%
  - **Total:** 100%

---

## Referencias

### Texto principal
- De Castro Korgi, R. (2004). *Teoría de la computación: Lenguajes, autómatas, gramáticas*. Universidad Nacional de Colombia.

### Referencias complementarias
- Acevedo Juárez, A. (2006). *Teoría de la computación* [Tesis de licenciatura, Instituto Tecnológico de Celaya].

---

## Estructura del repositorio

```text
TeoriaComputacion/
├── README.md          # Temario oficial, evaluación, referencias y estructura
├── GEMINI.md          # Harness e instrucciones de contexto para asistentes de IA
├── MEMORY.md          # Registro histórico de cambios (límite máximo de 50 líneas)
├── LICENSE            # Licencia del repositorio
├── .referencias/      # Bibliografía de consulta en PDF (ignorada en Git)
├── diapositivas/      # Material de presentación por unidad
└── notas/             # Apuntes del curso en Markdown por unidad y subtema
    ├── 1-0-introduccion.md
    ├── 1-1..1-7-*.md
    ├── 2-0-gramaticas-formales.md
    ├── 2-1..2-6-*.md
    ├── 3-0-maquinas-de-estado-finito.md
    ├── 3-1..3-6-*.md
    ├── 4-0-lenguajes-de-estado-finito.md
    ├── 4-1..4-4-*.md
    ├── 5-0-automatas-pushdown.md
    ├── 5-1..5-6-*.md
    ├── 6-0-lenguajes-independientes-del-contexto.md
    └── 6-1..6-3-*.md
```

### Índice de notas por unidad
- [Unidad 1: Introducción](notas/1-0-introduccion.md)
- [Unidad 2: Gramáticas Formales](notas/2-0-gramaticas-formales.md)
- [Unidad 3: Máquinas de Estado Finito](notas/3-0-maquinas-de-estado-finito.md)
- [Unidad 4: Lenguajes de Estado Finito](notas/4-0-lenguajes-de-estado-finito.md)
- [Unidad 5: Autómatas Pushdown](notas/5-0-automatas-pushdown.md)
- [Unidad 6: Lenguajes Independientes del Contexto](notas/6-0-lenguajes-independientes-del-contexto.md)
