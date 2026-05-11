# Análisis de Homologación — Encuestas Estudiantiles VCM USS (2021-2025)

## 1. Exploración de Esquemas

Los 5 archivos tienen **estructuras radicalmente distintas** con headers multi-fila:

| Año | Encuestados | Columnas | Preguntas | Estructura Header |
|-----|-------------|----------|-----------|-------------------|
| 2021 | 911 | 114 | 6 preguntas macro | 4 filas de header (secciones → preguntas → alternativas → códigos) |
| 2022 | 2,422 | 113 | 6 preguntas macro | 4 filas de header (idéntica a 2021) |
| 2023 | 1,953 | 70 | 14 preguntas | 5 filas de header (formato distinto) |
| 2024 | 3,970 | 166 | 15 preguntas | 3 filas de header (pregunta → vacío → alternativas) |
| 2025 | 4,629 | 131 | 10 preguntas | 3 filas de header (igual formato a 2024) |

> [!IMPORTANT]
> Las bases 2021-2022 usan codificación tipo **one-hot encoding** (cada alternativa es una columna con 0/1), mientras que 2024-2025 también usan one-hot pero con estructura de preguntas más granular. La base 2023 es un **híbrido** con mezcla de respuestas textuales y codificadas.

---

## 2. TABLA 1: Preguntas Homologadas Exactamente

> Criterio: **Mismo enunciado + Mismas alternativas de respuesta**

| ID | Años | Enunciado | Alternativas |
|----|------|-----------|-------------|
| **H001** | 2021, 2022 | ¿Cómo se originó tu participación en este proyecto? | Como parte de su práctica o internado \| Como parte de una pasantía \| Convocatoria abierta \| Invitación de otro estudiante \| Petición específica |
| **H002** | 2021, 2022 | Seleccione los tres valores sebastianos que más se fortalecieron según tu experiencia… | 10 valores (Búsqueda de la verdad, Honestidad, Responsabilidad, etc.) |
| **H003** | 2021, 2022 | Evalúa tu participación en el proyecto como experiencia de aprendizaje… | 6 afirmaciones (aplicación de lo aprendido, instancia de evaluación, etc.) |
| **H004** | 2022, 2023 | Indica cuán importante o significativa consideras que fue tu experiencia… para el logro de los siguientes aspectos | 7 aspectos (Aplicar contenidos, Fortalecer vocación, Desarrollar habilidades, etc.) |
| **H005** | 2024, 2025 | ¿Sabías que este proyecto era una iniciativa de vinculación con el medio? | Sí \| No |

> [!NOTE]
> Solo **5 preguntas** lograron homologación exacta, todas entre **pares de años consecutivos** (nunca cruzando más de 2 años). Esto confirma que el instrumento cambia significativamente cada año.

---

## 3. TABLA 2: Agrupaciones Similares para Revisión Manual

| Grupo | Años | Pregunta (resumen) | Similitud | ¿Alt. coinciden? |
|-------|------|--------------------|-----------|------------------|
| **G001** | 2021, 2024, 2025 | Importancia/significancia de la experiencia para logro de aspectos | 71-100% | No — cambian las sub-dimensiones |
| **G002** | 2021, 2022, 2023, 2024 | Fortalecimiento de habilidades transversales | 72-100% | No — las habilidades listadas varían |
| **G003** | 2021, 2022, 2023 | Cómo el proyecto permitió conocer el campo laboral (condicional) | 100% | No — cambian alternativas |
| **G004** | 2023, 2024 | Valores sebastianos fortalecidos | 74% | No — reformulación de valores |
| **G005** | 2023, 2024, 2025 | Nivel de importancia para personas/instituciones beneficiadas | 91-100% | No — escalas distintas |
| **G006** | 2023, 2024 | ¿Qué tan significativo fue para tu formación profesional? | 100% | No — escalas distintas |
| **G007** | 2023, 2024 | ¿El proyecto permitió conocer más de tu campo laboral? | 81-100% | No |
| **G008** | 2023, 2024 | Colaboración con personas de otras carreras/disciplinas | 77% | No — cambio de redacción |
| **G009** | 2023, 2024, 2025 | ¿El Proyecto Colaborativo cumplió con (mis/tus) expectativas? | 93% | No — escalas distintas |
| **G010** | 2023, 2024, 2025 | ¿Recomendarías participar en Proyectos Colaborativos? | 82-100% | No — varía formulación |

> [!TIP]
> Los grupos **G001, G002, G005, G009 y G010** son los más prometedores para homologación manual, ya que cubren **3+ años** y miden conceptos muy similares. Lo que impide la homologación automática son principalmente **cambios en la escala de respuesta** (ej. escala Likert de 7 → 5 puntos) y **reformulaciones menores** del enunciado.

---

## 4. Hallazgos y Anomalías

### 4.1 Estructura General
- **Crecimiento sostenido**: De 911 encuestados (2021) a 4,629 (2025) → **5x de crecimiento**
- **Variabilidad del instrumento**: El número de preguntas osciló entre 6 (2021-22) y 15 (2024)
- **Formato de datos**: 2021-2022 usan codificación binaria extensiva (114 columnas para 6 preguntas), mientras que 2024-2025 son más compactos

### 4.2 Calidad de Datos

| Año | Columnas >50% nulos | Observación |
|-----|---------------------|-------------|
| 2021 | **55 columnas** (48% del total) | Muchas alternativas de respuesta abierta casi vacías |
| 2022 | 14 columnas | Mejora significativa respecto a 2021 |
| 2023 | **25 columnas** (36% del total) | Incluye 20 columnas 100% vacías (residuos de formato) |
| 2024 | 0 | Base más limpia |
| 2025 | 0 | Base más limpia |

### 4.3 Patrones Clave para Dashboard

> [!WARNING]
> - Las escalas de respuesta cambian entre años: Likert 7 puntos (2021-23) → Likert 5 puntos (2024-25)
> - La pregunta sobre **valores sebastianos** cambió de "3 valores" a "2 valores" en 2025
> - Las **habilidades evaluadas** varían significativamente (34 en 2021 → 10 en 2024 → 9 en 2025)
> - El enunciado "¿Cumplió con mis/tus expectativas?" cambió el pronombre posesivo entre años

---

## 5. Archivos Exportados

Los siguientes archivos CSV fueron generados en la carpeta `Encuestas Estudiantes`:

| Archivo | Contenido |
|---------|-----------|
| `preguntas_homologadas_unificadas.csv` | DataFrame unificado con las 5 preguntas exactas (138,414 filas) |
| `tabla_homologacion.csv` | Resumen de la Tabla 1 |
| `tabla_similares_revision.csv` | Detalle de la Tabla 2 para revisión manual |

### Código de Exportación (reproducible)

```python
import pandas as pd

# Cargar el DataFrame unificado exportado
df = pd.read_csv("preguntas_homologadas_unificadas.csv", encoding='utf-8-sig')

# Filtrar por pregunta específica
df_h001 = df[df['ID_Pregunta'] == 'H001']

# Tabla cruzada para dashboard (ejemplo: distribución por año)
pivot = df_h001.groupby(['Año', 'Respuesta']).size().unstack(fill_value=0)
print(pivot)

# Re-exportar si se necesita otro formato
df.to_excel("homologadas_para_dashboard.xlsx", index=False)
```

---

## 6. Recomendaciones para el Dashboard

1. **Fase 1 — Exactas**: Usar las 5 preguntas homologadas (H001-H005) como base del dashboard longitudinal inmediato
2. **Fase 2 — Revisión manual**: Revisar los 10 grupos similares; con decisiones de mapeo de escalas se podrían agregar ~8 preguntas más cubriendo 3-4 años
3. **Normalización de escalas**: Para los grupos G005, G006, G009 será necesario definir un mapeo de equivalencia entre escalas (ej. "Muy significativo" ↔ "Muy positivo")
4. **Script completo**: El archivo `analisis_v2.py` queda disponible para re-ejecución cuando se agreguen nuevos años
