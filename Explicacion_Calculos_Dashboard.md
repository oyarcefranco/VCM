# Metodología y Cálculos del Dashboard VcM (2021-2025)

Este documento detalla la metodología de cálculo utilizada para generar el archivo `resumen_dashboard_vcm.xlsx`, diseñado para alimentar el Dashboard Ejecutivo y las presentaciones a jefaturas.

---

## 1. Metodologías de Cálculo Utilizadas

Para simplificar la visualización de datos complejos a nivel ejecutivo, se utilizaron tres metodologías matemáticas dependiendo del tipo de pregunta:

### A. Metodología "Top-2 Box" (T2B)

Utilizada para preguntas con **Escala Likert de 5 puntos** (Ej: Importancia, Habilidades, Significancia, Expectativas).

* **Fórmula:** `(Cantidad de respuestas 4 + Cantidad de respuestas 5) / Total de respuestas válidas`.
* **Explicación:** En lugar de mostrar 5 barras por cada pregunta, agrupa los dos niveles de valoración más altos (Ej: "Muy Importante" + "Importante", o "Totalmente de acuerdo" + "De acuerdo"). Representa el porcentaje neto de estudiantes con una **percepción francamente positiva**, ignorando a los neutros (3) y negativos (1, 2).

### B. Promedio de Aprobación (Binario)

Utilizado para preguntas dicotómicas (**Sí / No**).

* **Fórmula:** Se asigna Sí = 1, No = 0. Se calcula el `Promedio matemático`.
* **Explicación:** Un promedio de 0.95 en estas preguntas equivale directamente a decir "El 95% de los encuestados respondió 'Sí'".

### C. Frecuencia Relativa (One-Hot / Selección Múltiple)

Utilizado para los **Valores Sebastianos**, donde el alumno podía marcar múltiples opciones (hasta 3 en 2021-2023, hasta 2 en 2025).

* **Fórmula:** `(Cantidad de veces que se marcó el valor X) / Total de encuestados en ese año`.
* **Explicación:** Si un valor tiene 60%, significa que 60 de cada 100 alumnos lo incluyeron dentro de sus opciones seleccionadas.

---

## 2. Correspondencia por Hoja de Excel

A continuación, se detalla qué pregunta original alimenta cada hoja del archivo `resumen_dashboard_vcm.xlsx` y qué cálculo se le aplicó.

### Hoja 1: `KPIs_Generales`

Métricas macro que agrupan los 5 años completos.

* **Total Estudiantes Impactados:** Suma del total de filas válidas en la base (N = 13.885).
* **Índice de Recomendación Global:** Cálculo *Binario* de la pregunta *"¿Recomendarías a otros estudiantes participar...?"*
* **Impacto Positivo en Formación:** Cálculo *Top-2 Box* de la pregunta de *"¿Cuán significativo fue el aporte del proyecto para tu formación...?"*
* **Expectativas Cumplidas:** Cálculo *Top-2 Box* de la pregunta *"En general, ¿en qué medida el Proyecto cumplió tus expectativas...?"*

### Hoja 2: `Evolucion_Importancia`

* **Pregunta Original:** *"¿Cuán importante es para ti participar en Proyectos de Vinculación con el Medio porque te permiten...?"* (Con 14 sub-ítems como "Aplicar lo aprendido", "Conocer la realidad", etc.)
* **Escala Original:** 1 al 5 (Nada Importante a Muy Importante).
* **Cálculos en la hoja:**
  * `Top_2_Box (%)`: % de alumnos que respondió "Importante" o "Muy Importante".
  * `Promedio (1-5)`: Promedio aritmético clásico de la escala. Útil si se requiere un cálculo más tradicional.

### Hoja 3: `Evolucion_Habilidades`

* **Pregunta Original:** *"Pensando en tu experiencia, ¿en qué grado se fortalecen las siguientes habilidades transversales...?"* (Con 12 sub-ítems como "Trabajo en equipo", "Empatía", etc.)
* **Escala Original:** 1 al 5 (No se fortalece a Muy fortalecida).
* **Cálculos en la hoja:**
  * `Top_2_Box (%)`: % de alumnos que respondió "Se fortalece" o "Muy fortalecida".
  * `Promedio (1-5)`: Promedio aritmético clásico.

### Hoja 4: `Evolucion_Indicadores_Clave`

Agrupa métricas generales a través del tiempo.

* **Significancia en Formación (T2B):** Pregunta *"¿Cuán significativo fue el aporte... para tu formación profesional?"*. Escala 1 al 5. Se reporta el % Top-2 Box.
* **Importancia para Beneficiados (T2B):** Pregunta *"Para las comunidades/entorno beneficiado, ¿cuán importante fue la ejecución del proyecto?"*. Escala 1 al 5. Se reporta el % Top-2 Box.
* **Expectativas Cumplidas (T2B):** Pregunta de cumplimiento de expectativas iniciales. Escala 1 al 5 (Homologada). Se reporta el % Top-2 Box.
* **Recomendaría a compañeros (% Sí):** Pregunta de Recomendación. Se reporta el cálculo *Binario* (Porcentaje de "Sí").
* **Permitió conocer campo laboral (% Sí):** Pregunta *"Participar... ¿te permitió conocer cómo se desarrolla tu profesión en la vida real/campo laboral?"*. Se reporta el cálculo *Binario*. (Ojo: Pregunta ausente en la encuesta 2025).
* **Sabía que era VcM (% Sí):** Pregunta *"¿Sabías que esta iniciativa corresponde a Vinculación con el Medio?"*. Se reporta el cálculo *Binario*. (Pregunta existente solo en 2024 y 2025).

### Hoja 5: `Valores_Sebastianos_Ranking`

* **Pregunta Original:** *"Identifica qué Valores Sebastianos fueron fortalecidos/estuvieron presentes en el desarrollo del proyecto"* (Selección múltiple).
* **Cálculo en la hoja:** *Frecuencia Relativa*. Se reporta la cantidad de menciones absolutas (`Menciones`) y el porcentaje de estudiantes que lo seleccionó sobre el total de ese año (`% de Estudiantes`). Ordenado de mayor a menor para generar rankings inmediatos.

---
*Nota de Auditoría: Todas las filas omiten valores en blanco (NaN, "Sin información" o "No responde") en el denominador para no castigar estadísticamente el porcentaje con abstenciones.*
