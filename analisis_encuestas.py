"""
Análisis de Encuestas Estudiantiles VCM - Universidad San Sebastián
===================================================================
Script para homologación, agrupación por similitud y detección de hallazgos
en bases de datos de encuestas anuales (2021-2025).
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import pandas as pd
import numpy as np
import os
import json
from collections import defaultdict
from rapidfuzz import fuzz

# ============================================================
# PASO 1: LECTURA Y EXPLORACIÓN
# ============================================================

BASE_DIR = r"c:\Users\oyarc\OneDrive - Universidad San Sebastian\VCM\Encuestas Estudiantes\RV_ BASE ENCUESTA ESTUDIANTES 2021-2025"

archivos = {
    2021: os.path.join(BASE_DIR, "Encuesta estudiantes 2021 Reporte.xlsx"),
    2022: os.path.join(BASE_DIR, "Encuesta estudiantes 2022 Reporte.xlsx"),
    2023: os.path.join(BASE_DIR, "Encuesta estudiantes 2023 Reporte.xlsx"),
    2024: os.path.join(BASE_DIR, "BASE ENCUESTA ESTUDIANTES 2024.xlsx"),
    2025: os.path.join(BASE_DIR, "BASE ENCUESTA ESTUDIANTES 2025.xlsx"),
}

print("=" * 80)
print("PASO 1: LECTURA Y EXPLORACIÓN DE ARCHIVOS")
print("=" * 80)

# Cargar todos los archivos
dataframes = {}
esquemas = {}

for year, filepath in archivos.items():
    print(f"\n{'─' * 60}")
    print(f"Cargando archivo {year}...")
    
    # Leer todas las hojas
    xls = pd.ExcelFile(filepath)
    print(f"  Hojas disponibles: {xls.sheet_names}")
    
    # Leer la primera hoja (datos principales)
    df = pd.read_excel(filepath, sheet_name=0)
    dataframes[year] = df
    esquemas[year] = list(df.columns)
    
    print(f"  Dimensiones: {df.shape[0]} filas × {df.shape[1]} columnas")
    print(f"  Columnas ({len(df.columns)}):")
    for i, col in enumerate(df.columns):
        null_pct = df[col].isnull().mean() * 100
        unique_vals = df[col].nunique()
        print(f"    [{i:3d}] {col[:100]}  |  Nulos: {null_pct:.1f}%  |  Únicos: {unique_vals}")

# ============================================================
# PASO 2: HOMOLOGACIÓN EXACTA
# ============================================================

print("\n\n" + "=" * 80)
print("PASO 2: HOMOLOGACIÓN EXACTA DE PREGUNTAS")
print("=" * 80)

def extraer_preguntas_y_alternativas(df, year):
    """
    Extrae las preguntas y sus alternativas de respuesta.
    Retorna un dict: {pregunta_normalizada: {alternativas: set, columna_original: str}}
    """
    preguntas = {}
    for col in df.columns:
        col_str = str(col).strip()
        # Ignorar columnas de metadata/identificadores comunes
        skip_keywords = ['timestamp', 'marca temporal', 'correo', 'email', 'rut', 
                         'nombre', 'carrera', 'sede', 'facultad', 'jornada',
                         'proyecto', 'actividad', 'asignatura', 'código',
                         'periodo', 'año', 'semestre', 'id']
        
        is_metadata = False
        col_lower = col_str.lower()
        for kw in skip_keywords:
            if kw in col_lower and len(col_str) < 80:
                is_metadata = True
                break
        
        if is_metadata:
            continue
            
        # Obtener alternativas de respuesta únicas (no nulas)
        alternativas = set()
        for val in df[col].dropna().unique():
            alternativas.add(str(val).strip())
        
        if len(alternativas) > 0:
            preguntas[col_str] = {
                'alternativas': frozenset(alternativas),
                'columna_original': col,
                'n_respuestas': df[col].notna().sum(),
                'n_alternativas': len(alternativas)
            }
    
    return preguntas

# Extraer preguntas por año
preguntas_por_año = {}
for year, df in dataframes.items():
    preguntas_por_año[year] = extraer_preguntas_y_alternativas(df, year)
    print(f"\n  {year}: {len(preguntas_por_año[year])} preguntas identificadas (excluyendo metadata)")

# Buscar coincidencias exactas (mismo enunciado Y mismas alternativas)
print("\n\nBuscando coincidencias exactas...")

# Crear fingerprint para cada pregunta: (enunciado_normalizado, alternativas_ordenadas)
def normalizar_texto(texto):
    """Normaliza texto para comparación."""
    t = str(texto).strip().lower()
    # Normalizar espacios
    t = ' '.join(t.split())
    return t

# Crear índice de fingerprints
fingerprints = {}  # {(enunciado_norm, frozenset_alternativas): [(year, col_original)]}

for year, preguntas in preguntas_por_año.items():
    for enunciado, info in preguntas.items():
        enunciado_norm = normalizar_texto(enunciado)
        fp = (enunciado_norm, info['alternativas'])
        if fp not in fingerprints:
            fingerprints[fp] = []
        fingerprints[fp].append((year, info['columna_original']))

# Filtrar solo las que aparecen en más de un año
homologadas = {}
for fp, ocurrencias in fingerprints.items():
    años = set(y for y, _ in ocurrencias)
    if len(años) > 1:
        homologadas[fp] = ocurrencias

print(f"\n  Total de preguntas homologadas exactas: {len(homologadas)}")

# Construir tabla resumen de homologación
tabla_homologacion = []
for i, (fp, ocurrencias) in enumerate(homologadas.items(), 1):
    enunciado_norm, alternativas = fp
    años = sorted(set(y for y, _ in ocurrencias))
    # Obtener el enunciado original (del primer año)
    primer_año, primer_col = ocurrencias[0]
    
    tabla_homologacion.append({
        'ID_Pregunta': f'H{i:03d}',
        'Enunciado': str(primer_col)[:200],
        'Alternativas': ' | '.join(sorted(str(a) for a in alternativas))[:300],
        'N_Alternativas': len(alternativas),
        'Años_Presentes': ', '.join(str(a) for a in años),
        'N_Años': len(años),
    })

df_homologacion = pd.DataFrame(tabla_homologacion)
if not df_homologacion.empty:
    df_homologacion = df_homologacion.sort_values('N_Años', ascending=False)

print("\n\n── TABLA 1: PREGUNTAS HOMOLOGADAS EXACTAMENTE ──")
if df_homologacion.empty:
    print("  No se encontraron preguntas idénticas entre años.")
else:
    print(df_homologacion.to_string(index=False, max_colwidth=80))

# ============================================================
# PASO 2b: CONSTRUIR DATAFRAME UNIFICADO
# ============================================================

print("\n\n" + "=" * 80)
print("PASO 2b: CONSTRUCCIÓN DEL DATAFRAME UNIFICADO")
print("=" * 80)

# Crear el DataFrame unificado
frames_unificados = []

for i, (fp, ocurrencias) in enumerate(homologadas.items(), 1):
    enunciado_norm, alternativas = fp
    pregunta_id = f'H{i:03d}'
    
    for year, col_original in ocurrencias:
        df_year = dataframes[year]
        # Crear un mini-dataframe con la respuesta y metadata
        temp = pd.DataFrame({
            'Año': year,
            'ID_Pregunta': pregunta_id,
            'Enunciado': str(col_original)[:200],
            'Respuesta': df_year[col_original].values,
        })
        
        # Agregar columnas de metadata si existen
        for meta_col in df_year.columns:
            meta_lower = str(meta_col).lower()
            if any(kw in meta_lower for kw in ['sede', 'carrera', 'facultad', 'jornada']):
                temp[str(meta_col).strip()] = df_year[meta_col].values
        
        frames_unificados.append(temp)

if frames_unificados:
    df_unificado = pd.concat(frames_unificados, ignore_index=True)
    print(f"  DataFrame unificado creado: {df_unificado.shape[0]} filas × {df_unificado.shape[1]} columnas")
    print(f"  Preguntas homologadas: {df_unificado['ID_Pregunta'].nunique()}")
    print(f"  Años cubiertos: {sorted(df_unificado['Año'].unique())}")
else:
    df_unificado = pd.DataFrame()
    print("  No hay datos para unificar (no se encontraron coincidencias exactas).")

# ============================================================
# PASO 3: AGRUPACIÓN POR SIMILITUD
# ============================================================

print("\n\n" + "=" * 80)
print("PASO 3: AGRUPACIÓN POR SIMILITUD")
print("=" * 80)

# Recopilar todas las preguntas NO homologadas
preguntas_no_homologadas = []
homologadas_cols = set()
for fp, ocurrencias in homologadas.items():
    for year, col in ocurrencias:
        homologadas_cols.add((year, str(col).strip()))

for year, preguntas in preguntas_por_año.items():
    for enunciado, info in preguntas.items():
        if (year, enunciado) not in homologadas_cols:
            preguntas_no_homologadas.append({
                'year': year,
                'enunciado': enunciado,
                'enunciado_norm': normalizar_texto(enunciado),
                'alternativas': info['alternativas'],
                'n_alternativas': info['n_alternativas'],
            })

print(f"\n  Preguntas no homologadas a agrupar: {len(preguntas_no_homologadas)}")

# Agrupar por similitud de enunciado usando rapidfuzz
# Threshold de similitud: 70%
THRESHOLD = 70

grupos_similares = []
usados = set()

for i, p1 in enumerate(preguntas_no_homologadas):
    if i in usados:
        continue
    
    grupo = [p1]
    usados.add(i)
    
    for j, p2 in enumerate(preguntas_no_homologadas):
        if j in usados or j <= i:
            continue
        if p1['year'] == p2['year']:
            continue  # No comparar preguntas del mismo año
            
        # Comparar enunciados
        similitud = fuzz.token_sort_ratio(p1['enunciado_norm'], p2['enunciado_norm'])
        
        if similitud >= THRESHOLD:
            grupo.append(p2)
            usados.add(j)
    
    if len(grupo) > 1:
        # Solo incluir grupos con preguntas de diferentes años
        años_grupo = set(p['year'] for p in grupo)
        if len(años_grupo) > 1:
            grupos_similares.append(grupo)

print(f"  Grupos de preguntas similares encontrados: {len(grupos_similares)}")

# Construir tabla de agrupaciones similares
tabla_similares = []
for g_idx, grupo in enumerate(grupos_similares, 1):
    for p in grupo:
        # Calcular similitud promedio con el primer enunciado del grupo
        ref = grupo[0]['enunciado_norm']
        sim = fuzz.token_sort_ratio(ref, p['enunciado_norm'])
        
        # Verificar si alternativas coinciden
        alt_ref = grupo[0]['alternativas']
        alt_match = "Sí" if p['alternativas'] == alt_ref else "No"
        
        tabla_similares.append({
            'Grupo': f'G{g_idx:03d}',
            'Año': p['year'],
            'Enunciado': p['enunciado'][:150],
            'N_Alternativas': p['n_alternativas'],
            'Similitud_Enunciado_%': sim,
            'Alternativas_Coinciden': alt_match,
        })

df_similares = pd.DataFrame(tabla_similares)

print("\n\n── TABLA 2: AGRUPACIONES DE PREGUNTAS SIMILARES PARA REVISIÓN MANUAL ──")
if df_similares.empty:
    print("  No se encontraron agrupaciones de preguntas similares.")
else:
    # Mostrar grupo por grupo
    for grupo_id in df_similares['Grupo'].unique():
        grupo_df = df_similares[df_similares['Grupo'] == grupo_id]
        print(f"\n  {'═' * 70}")
        print(f"  GRUPO {grupo_id} ({len(grupo_df)} preguntas)")
        print(f"  {'─' * 70}")
        for _, row in grupo_df.iterrows():
            print(f"  Año {row['Año']}: {row['Enunciado'][:120]}")
            print(f"           Alternativas: {row['N_Alternativas']} | "
                  f"Similitud: {row['Similitud_Enunciado_%']}% | "
                  f"Alt. Coinciden: {row['Alternativas_Coinciden']}")

# ============================================================
# PASO 4: DETECCIÓN DE HALLAZGOS Y ANOMALÍAS
# ============================================================

print("\n\n" + "=" * 80)
print("PASO 4: DETECCIÓN DE HALLAZGOS Y ANOMALÍAS")
print("=" * 80)

hallazgos = []

for year, df in dataframes.items():
    print(f"\n{'─' * 60}")
    print(f"  AÑO {year}")
    print(f"{'─' * 60}")
    
    # 4.1 Valores nulos
    nulos = df.isnull().mean() * 100
    cols_alto_nulo = nulos[nulos > 50].sort_values(ascending=False)
    if not cols_alto_nulo.empty:
        print(f"\n  ⚠ Columnas con >50% valores nulos:")
        for col, pct in cols_alto_nulo.items():
            print(f"    - {str(col)[:80]}: {pct:.1f}%")
            hallazgos.append({
                'Año': year,
                'Tipo': 'Alto % Nulos',
                'Detalle': f"{str(col)[:80]} ({pct:.1f}% nulos)"
            })
    
    # 4.2 Columnas completamente vacías
    cols_vacias = [col for col in df.columns if df[col].isnull().all()]
    if cols_vacias:
        print(f"\n  ⚠ Columnas completamente vacías ({len(cols_vacias)}):")
        for col in cols_vacias:
            print(f"    - {str(col)[:80]}")
            hallazgos.append({
                'Año': year,
                'Tipo': 'Columna Vacía',
                'Detalle': str(col)[:80]
            })
    
    # 4.3 Filas duplicadas
    n_duplicados = df.duplicated().sum()
    if n_duplicados > 0:
        print(f"\n  ⚠ Filas duplicadas: {n_duplicados} ({n_duplicados/len(df)*100:.1f}%)")
        hallazgos.append({
            'Año': year,
            'Tipo': 'Filas Duplicadas',
            'Detalle': f"{n_duplicados} filas duplicadas ({n_duplicados/len(df)*100:.1f}%)"
        })
    
    # 4.4 Verificar cambios en número de columnas
    print(f"\n  📊 Total columnas: {len(df.columns)} | Total filas: {len(df)}")
    
    # 4.5 Tipos de datos mixtos
    for col in df.columns:
        tipos = df[col].dropna().apply(type).unique()
        if len(tipos) > 1:
            tipos_str = ', '.join(t.__name__ for t in tipos)
            print(f"\n  ⚠ Tipos mixtos en '{str(col)[:60]}': {tipos_str}")
            hallazgos.append({
                'Año': year,
                'Tipo': 'Tipos Mixtos',
                'Detalle': f"{str(col)[:60]}: {tipos_str}"
            })
    
    # 4.6 Distribución de respuestas (escalas)
    for col in df.columns:
        vals = df[col].dropna().unique()
        if len(vals) <= 7 and len(vals) >= 2:
            # Podría ser una escala tipo Likert
            vals_str = [str(v).strip().lower() for v in vals]
            likert_keywords = ['muy de acuerdo', 'de acuerdo', 'en desacuerdo', 
                             'totalmente', 'satisfecho', 'insatisfecho',
                             'siempre', 'nunca', 'a veces']
            is_likert = any(kw in ' '.join(vals_str) for kw in likert_keywords)
            if is_likert:
                print(f"\n  📋 Escala Likert detectada en: {str(col)[:60]}")
                print(f"     Valores: {sorted(vals_str)}")

# Resumen de hallazgos
print("\n\n" + "=" * 80)
print("RESUMEN DE HALLAZGOS")
print("=" * 80)

df_hallazgos = pd.DataFrame(hallazgos)
if not df_hallazgos.empty:
    print(f"\n  Total hallazgos: {len(df_hallazgos)}")
    print(f"\n  Por tipo:")
    print(df_hallazgos['Tipo'].value_counts().to_string())
    print(f"\n  Por año:")
    print(df_hallazgos['Año'].value_counts().sort_index().to_string())

# ============================================================
# PASO 5: ANÁLISIS ADICIONAL - COMPARACIÓN DE ESCALAS
# ============================================================

print("\n\n" + "=" * 80)
print("PASO 5: ANÁLISIS DE ESCALAS DE RESPUESTA POR AÑO")
print("=" * 80)

for year, preguntas in preguntas_por_año.items():
    print(f"\n  {year}: Escalas de respuesta encontradas:")
    escalas = defaultdict(list)
    for enunciado, info in preguntas.items():
        alt_key = tuple(sorted(str(a) for a in info['alternativas']))
        if len(alt_key) <= 10:  # Solo escalas cortas
            escalas[alt_key].append(enunciado[:80])
    
    for alt_key, pregs in sorted(escalas.items(), key=lambda x: -len(x[1])):
        if len(pregs) >= 2:  # Solo escalas usadas en más de una pregunta
            print(f"\n    Escala ({len(alt_key)} opciones, usada en {len(pregs)} preguntas):")
            print(f"    Opciones: {' | '.join(alt_key[:5])}{'...' if len(alt_key) > 5 else ''}")
            for p in pregs[:3]:
                print(f"      → {p}")
            if len(pregs) > 3:
                print(f"      ... y {len(pregs)-3} más")

# ============================================================
# EXPORTACIÓN
# ============================================================

print("\n\n" + "=" * 80)
print("EXPORTACIÓN DE RESULTADOS")
print("=" * 80)

OUTPUT_DIR = r"c:\Users\oyarc\OneDrive - Universidad San Sebastian\VCM\Encuestas Estudiantes"

# Exportar DataFrame unificado
if not df_unificado.empty:
    path_unificado = os.path.join(OUTPUT_DIR, "preguntas_homologadas_unificadas.csv")
    df_unificado.to_csv(path_unificado, index=False, encoding='utf-8-sig')
    print(f"\n  ✅ DataFrame unificado exportado: {path_unificado}")
else:
    print("\n  ⚠ No hay DataFrame unificado para exportar.")

# Exportar tabla de homologación
if not df_homologacion.empty:
    path_homologacion = os.path.join(OUTPUT_DIR, "tabla_homologacion.csv")
    df_homologacion.to_csv(path_homologacion, index=False, encoding='utf-8-sig')
    print(f"  ✅ Tabla de homologación exportada: {path_homologacion}")

# Exportar tabla de similares
if not df_similares.empty:
    path_similares = os.path.join(OUTPUT_DIR, "tabla_similares_revision.csv")
    df_similares.to_csv(path_similares, index=False, encoding='utf-8-sig')
    print(f"  ✅ Tabla de similares exportada: {path_similares}")

# Exportar hallazgos
if not df_hallazgos.empty:
    path_hallazgos = os.path.join(OUTPUT_DIR, "hallazgos_anomalias.csv")
    df_hallazgos.to_csv(path_hallazgos, index=False, encoding='utf-8-sig')
    print(f"  ✅ Hallazgos exportados: {path_hallazgos}")

print("\n\n" + "=" * 80)
print("ANÁLISIS COMPLETADO")
print("=" * 80)
