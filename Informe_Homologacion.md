# Informe de Homologación — Encuestas Estudiantes VCM 2021-2025

## 1. Contexto

Se consolidaron 5 encuestas anuales (2021-2025) aplicadas a estudiantes de Proyectos Colaborativos de Vinculación con el Medio. Los instrumentos variaron en estructura, redacción de preguntas y escalas de respuesta, requiriendo un proceso riguroso de homologación.

**Resultado:** Archivo `base_homologada_final.xlsx` con **13,885 registros** distribuidos en **11 hojas temáticas** + 1 Diccionario.

| Año | n |
|---|---|
| 2021 | 911 |
| 2022 | 2,422 |
| 2023 | 1,953 |
| 2024 | 3,970 |
| 2025 | 4,629 |
| **Total** | **13,885** |

---

## 2. Decisiones de Homologación

### 2.1 Importancia de Aspectos Formativos (Hoja: `Importancia_Aspectos`)

- **Escala:** Likert 5 puntos idéntica en todos los años → *Nada Importante(1), Poco Importante(2), Medianamente Importante(3), Importante(4), Muy Importante(5)*
- **Acción:** Extracción directa sin ajuste. En 2024-2025 la respuesta estaba distribuida en 5 columnas binarias (one-hot); se identificó cuál columna tenía el "1" y se asignó el valor numérico correspondiente.
- **14 sub-ítems identificados.** Los 4 principales (Aplicar contenidos, Conocer realidad, Vocación, Valores sebastianos) están presentes en 4-5 años. Los demás aparecen en subconjuntos de años.

### 2.2 Habilidades Fortalecidas (Hoja: `Habilidades`)

- **Escala:** Likert 5 puntos idéntica → *No se fortalece(1), Poco Fortalecida(2), Medianamente fortalecida(3), Se fortalece(4), Muy fortalecida(5)*
- **Acción:** Extracción directa. En 2024 las etiquetas incluían códigos numéricos entre corchetes (ej: "Muy fortalecida [5]") que fueron eliminados durante la limpieza.
- **12 habilidades identificadas.** Las 8 principales están presentes en 4-5 años.

### 2.3 Significancia/Impacto en la Formación (Hoja: `Significancia_Formacion`)

- **Problema:** 2021-2024 usaron escala "significativo" (*Muy significativo → Nada significativo*), pero 2025 cambió a escala "impacto" (*Muy positivo → Muy negativo*).
- **Decisión:** Se homologaron las dos escalas a un único rango 1-5, con la siguiente justificación:
  - Ambas miden la **evaluación subjetiva del estudiante sobre la contribución del proyecto a su formación** en una escala bipolar de 5 niveles.
  - Los anclajes semánticos representan niveles de intensidad equivalentes: el extremo superior (Muy significativo / Muy positivo) captura una evaluación fuertemente favorable; el punto medio (Medianamente / Neutro) captura indiferencia; el extremo inferior (Nada significativo / Muy negativo) captura evaluación desfavorable.
  - El mapeo preserva la **equivalencia ordinal**: 5=máxima valoración positiva, 1=mínima.

| Escala 2021-2024 | Escala 2025 | Valor |
|---|---|---|
| Muy significativo | Muy positivo | **5** |
| Significativo | Positivo | **4** |
| Medianamente significativo | Neutro (no impactó) | **3** |
| Poco significativo | Negativo | **2** |
| Nada significativo | Muy negativo | **1** |

### 2.4 Cumplimiento de Expectativas (Hoja: `Cumplimiento_Expectativas`)

- **Problema:** 3 escalas distintas a lo largo de los años.
- **Decisión:** Se homologaron las tres a un rango 1-5, argumentando que todas miden **grado de satisfacción respecto a las expectativas previas** del estudiante:

| 2021-2023 (Acuerdo) | 2024 (Cumplimiento) | 2025 (Cumplimiento+) | Valor |
|---|---|---|---|
| Muy de acuerdo | Totalmente | Superó mis expectativas | **5** |
| De acuerdo | Casi totalmente | Totalmente | **4** |
| Ni de acuerdo ni en desacuerdo | Medianamente | En gran medida | **3** |
| En desacuerdo | Sólo en parte | Sólo en parte | **2** |
| Muy en desacuerdo | No las cumplió | No las cumplió | **1** |

**Justificación del mapeo 2025:** La escala 2025 agrega "Superó mis expectativas" como nivel máximo (5), desplazando "Totalmente" al nivel 4. Esto refleja que la encuesta 2025 distingue entre "cumplir completamente" (4) y "exceder" (5). Para comparabilidad, "Totalmente" en 2025 se mapea a 4 (no a 5 como en 2024), porque la pregunta ofrece una alternativa explícitamente superior. **Consecuencia:** las medias de 2025 pueden ser ligeramente menores que las de 2024 dado que el "techo" de la escala es más exigente.

### 2.5 Campo Laboral (Hoja: `Campo_Laboral_SiNo`)

- **Escala:** Sí(1)/No(0) — idéntica en 2021-2024.
- **2025 excluido:** No tiene pregunta equivalente directa (el concepto se integró como sub-ítem de importancia).

### 2.6 Recomendaría (Hoja: `Recomendaria`)

- **Escala:** Sí(1)/No(0) — idéntica los 5 años. Sin ajuste.

### 2.7 Vinculación con el Medio (Hoja: `Vinculacion_Medio`)

- **Escala:** Sí(1)/No(0) — solo 2024-2025. Sin ajuste.

### 2.8 Valores Sebastianos (Hoja: `Valores_Sebastianos`)

- **Formato:** Columnas one-hot (0/1) por cada valor, permitiendo calcular frecuencia de selección.
- **Nota:** 2021-2023 pedían seleccionar **3 valores**, 2025 solo **2 valores**. Esto afecta las frecuencias absolutas pero no las relativas (% de estudiantes que marcó cada valor).
- **Nombres:** 2021-2023 usan nombres cortos (ej: "Responsabilidad"), 2024-2025 usan nombres largos (ej: "La responsabilidad y la prudencia"). Las columnas están separadas por grupo de nombres.

### 2.9 Experiencia de Aprendizaje (Hoja: `Experiencia_Aprendizaje`)

- **Escala:** Likert 5 puntos de acuerdo — idéntica en todos los años disponibles (2021-2024).
- **2025 excluido:** No incluye estas afirmaciones.

### 2.10 Importancia para Beneficiados (Hoja: `Importancia_Beneficiados`)

- **Escala:** Likert 5 puntos de importancia — idéntica los 5 años. Sin ajuste.

---

## 3. Proceso Técnico

1. **Lectura:** Se cargaron los 5 Excel con `pandas.read_excel(header=None)` para preservar las celdas combinadas como filas de header.
2. **Identificación de estructura:** Se mapearon manualmente las posiciones de cada pregunta y alternativa en cada archivo.
3. **Extracción:**
   - **2021-2023:** Lectura directa de texto Likert, conversión a numérico mediante diccionario de mapeo.
   - **2024-2025:** Detección automática de estructura one-hot (5 columnas binarias por pregunta), lectura de la etiqueta de la columna marcada con "1".
4. **Limpieza:** Eliminación de códigos entre corchetes `[1]`-`[5]`, normalización de espacios y acentos, exclusión de "Sin información" y "No Responde".
5. **Exportación:** Un único archivo Excel con hojas separadas por grupo temático.

---

## 4. Estructura del Archivo Final

| Hoja | Contenido | Escala | Años |
|---|---|---|---|
| `Importancia_Aspectos` | 14 aspectos formativos | Likert 1-5 | 2021-2025 |
| `Habilidades` | 12 habilidades transversales | Likert 1-5 | 2021-2025 |
| `Significancia_Formacion` | Impacto en formación profesional | Likert 1-5 (ajustado) | 2021-2025 |
| `Cumplimiento_Expectativas` | Cumplimiento de expectativas | Likert 1-5 (ajustado) | 2021-2025 |
| `Importancia_Beneficiados` | Importancia para comunidades | Likert 1-5 | 2021-2025 |
| `Campo_Laboral_SiNo` | ¿Permitió conocer campo laboral? | Sí/No | 2021-2024 |
| `Recomendaria` | ¿Recomendaría participar? | Sí/No | 2021-2025 |
| `Vinculacion_Medio` | ¿Sabía que era iniciativa VcM? | Sí/No | 2024-2025 |
| `Valores_Sebastianos` | Valores seleccionados | One-hot 0/1 | 2021-2025 |
| `Experiencia_Aprendizaje` | Evaluación de aprendizaje | Likert 1-5 | 2021-2024 |
| `Diccionario` | Guía de cada hoja | — | — |

Cada hoja incluye: **Año, RUT, Sede, Facultad, Carrera** + las columnas de respuesta.
