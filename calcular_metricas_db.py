import pandas as pd
import numpy as np
import sqlite3
import os

BASE_PATH = "base_homologada_final.xlsx"
DB_PATH = "vcm_resultados_analisis.db"
EXCEL_PATH = "metricas_detalladas_vcm.xlsx"

# Diccionarios de mapeo para nombres amigables
NOMBRES_IMP = {
    'IMP_01': 'Aplicar lo aprendido en clases',
    'IMP_02': 'Conocer la realidad (problemas/desafíos)',
    'IMP_03': 'Fortalecer vocación profesional',
    'IMP_04': 'Fortalecer valores sebastianos',
    'IMP_05': 'Potenciar desempeño futuro',
    'IMP_06': 'Desarrollar habilidades transversales',
    'IMP_07': 'Enfrentar desafíos con seguridad',
    'IMP_08': 'Compromiso con la sociedad',
    'IMP_09': 'Ser ciudadano responsable',
    'IMP_10': 'Incrementar redes de contactos',
    'IMP_11': 'Trabajar con otras carreras',
    'IMP_13': 'Interactuar en contexto real',
    'IMP_14': 'Aportar desde el rol profesional'
}

NOMBRES_HAB = {
    'HAB_01': 'Empatía',
    'HAB_02': 'Comunicación efectiva',
    'HAB_03': 'Trabajo en equipo / Colaboración',
    'HAB_04': 'Resolución de problemas',
    'HAB_05': 'Adaptación y flexibilidad',
    'HAB_06': 'Competencia disciplinar',
    'HAB_07': 'Manejo de información (toma de decisiones)',
    'HAB_08': 'Prolijidad / Atención al detalle',
    'HAB_09': 'Pensamiento crítico y reflexivo',
    'HAB_10': 'Ciudadanía responsable',
    'HAB_11': 'Creatividad / Pensamiento innovador',
    'HAB_12': 'Autoconsciencia'
}

print(f"Cargando la base de datos homologada desde {BASE_PATH}...")
xls = pd.ExcelFile(BASE_PATH)

def agg_likert(group, col):
    """Calcula frecuencias y métricas para variables Likert (1 a 5)"""
    s = group[col].dropna()
    n = len(s)
    if n == 0:
        return None
    
    # Contar frecuencias
    counts = s.value_counts()
    c1 = counts.get(1, 0)
    c2 = counts.get(2, 0)
    c3 = counts.get(3, 0)
    c4 = counts.get(4, 0)
    c5 = counts.get(5, 0)
    
    # Calcular porcentajes
    pct_1 = c1 / n
    pct_2 = c2 / n
    pct_3 = c3 / n
    pct_4 = c4 / n
    pct_5 = c5 / n
    t2b_count = c4 + c5
    t2b = t2b_count / n
    promedio = s.mean()
    
    return pd.Series({
        'N_Respuestas': n,
        'Frec_1': c1,
        'Frec_2': c2,
        'Frec_3': c3,
        'Frec_4': c4,
        'Frec_5': c5,
        'Frec_T2B': t2b_count,
        'Pct_1': pct_1,
        'Pct_2': pct_2,
        'Pct_3': pct_3,
        'Pct_4': pct_4,
        'Pct_5': pct_5,
        'Top_2_Box': t2b,
        'Promedio_1_5': promedio
    })

def process_likert_sheet(sheet_name, name_mapping, value_cols, category_name):
    print(f"Procesando hoja Likert: {sheet_name}...")
    df = pd.read_excel(xls, sheet_name=sheet_name)
    results = []
    
    # Filtrar solo las columnas que existan en esta hoja
    cols_to_use = [c for c in value_cols if c in df.columns]
    
    # Asegurar que las columnas de agrupación existen y limpiar strings
    for col in ['Año', 'SEDE', 'CARRERA']:
        if col not in df.columns:
            df[col] = "Desconocido"
        else:
            # Reemplazar nulos con "Sin Información"
            df[col] = df[col].fillna("Sin Información")

    for col in cols_to_use:
        # Agrupar por Año, Sede, Carrera
        grouped = df.groupby(['Año', 'SEDE', 'CARRERA']).apply(lambda g: agg_likert(g, col), include_groups=False).dropna().reset_index()
        
        # Formatear
        grouped['Categoria'] = category_name
        grouped['Pregunta'] = name_mapping.get(col, col)
        
        results.append(grouped)
        
    if results:
        return pd.concat(results, ignore_index=True)
    return pd.DataFrame()

def agg_dico(group, col):
    """Calcula frecuencias y métricas para variables dicotómicas (0 o 1)"""
    s = group[col].dropna()
    n = len(s)
    if n == 0:
        return None
    
    counts = s.value_counts()
    c0 = counts.get(0, 0)
    c1 = counts.get(1, 0)
    
    return pd.Series({
        'N_Respuestas': n,
        'Frec_Si': c1,
        'Frec_No': c0,
        'Pct_Si': c1 / n,
        'Pct_No': c0 / n
    })

def process_dico_sheet(sheet_name, col_name, category_name, label):
    print(f"Procesando hoja Dicotómica: {sheet_name}...")
    try:
        df = pd.read_excel(xls, sheet_name=sheet_name)
    except Exception as e:
        print(f"  Advertencia: Hoja {sheet_name} no encontrada o error.")
        return pd.DataFrame()

    if col_name not in df.columns:
        return pd.DataFrame()
        
    for col in ['Año', 'SEDE', 'CARRERA']:
        if col not in df.columns:
            df[col] = "Desconocido"
        else:
            df[col] = df[col].fillna("Sin Información")

    grouped = df.groupby(['Año', 'SEDE', 'CARRERA']).apply(lambda g: agg_dico(g, col_name), include_groups=False).dropna().reset_index()
    grouped['Categoria'] = category_name
    grouped['Pregunta'] = label
    
    return grouped

def process_vs():
    print("Procesando hoja: Valores_Sebastianos...")
    try:
        df = pd.read_excel(xls, sheet_name='Valores_Sebastianos')
    except Exception:
        return pd.DataFrame()

    for col in ['Año', 'SEDE', 'CARRERA']:
        if col not in df.columns:
            df[col] = "Desconocido"
        else:
            df[col] = df[col].fillna("Sin Información")

    vs_cols = [c for c in df.columns if c.startswith('VS_')]
    results = []

    for name, group in df.groupby(['Año', 'SEDE', 'CARRERA']):
        n_estudiantes = len(group)
        if n_estudiantes == 0:
            continue
            
        for col in vs_cols:
            menciones = group[col].dropna().sum()
            if menciones > 0:
                results.append({
                    'Año': name[0],
                    'SEDE': name[1],
                    'CARRERA': name[2],
                    'Valor_Sebastiano': col.replace('VS_', ''),
                    'N_Respuestas': n_estudiantes,
                    'Menciones': menciones,
                    'Pct_Menciones': menciones / n_estudiantes
                })

    return pd.DataFrame(results)

# ==============================================================================
# 1. Calcular Tabla Likert
# ==============================================================================
frames_likert = [
    process_likert_sheet('Importancia_Aspectos', NOMBRES_IMP, NOMBRES_IMP.keys(), 'Importancia Aspectos Formativos'),
    process_likert_sheet('Habilidades', NOMBRES_HAB, NOMBRES_HAB.keys(), 'Desarrollo de Habilidades'),
    process_likert_sheet('Significancia_Formacion', {'Q01_Significancia': 'Significancia en Formación'}, ['Q01_Significancia'], 'Significancia en Formación'),
    process_likert_sheet('Importancia_Beneficiados', {'Importancia_Beneficiados': 'Importancia para Comunidades Beneficiadas'}, ['Importancia_Beneficiados'], 'Importancia para Comunidades'),
    process_likert_sheet('Cumplimiento_Expectativas', {'Cumplimiento_Expectativas': 'Cumplimiento de Expectativas'}, ['Cumplimiento_Expectativas'], 'Cumplimiento Expectativas')
]
df_likert = pd.concat([f for f in frames_likert if not f.empty], ignore_index=True)

# Reordenar columnas
cols_likert = ['Año', 'SEDE', 'CARRERA', 'Categoria', 'Pregunta', 'N_Respuestas', 'Frec_1', 'Frec_2', 'Frec_3', 'Frec_4', 'Frec_5', 'Frec_T2B', 'Pct_1', 'Pct_2', 'Pct_3', 'Pct_4', 'Pct_5', 'Top_2_Box', 'Promedio_1_5']
df_likert = df_likert[cols_likert]

# ==============================================================================
# 2. Calcular Tabla Dicotómica
# ==============================================================================
frames_dico = [
    process_dico_sheet('Recomendaria', 'Recomendaria', 'Recomendación', 'Recomendaría a compañeros'),
    process_dico_sheet('Campo_Laboral_SiNo', 'Campo_Laboral_SiNo', 'Campo Laboral', 'Permitió conocer campo laboral'),
    process_dico_sheet('Vinculacion_Medio', 'Vinculacion_Medio', 'Conocimiento VcM', 'Sabía que era iniciativa VcM')
]
df_dico = pd.concat([f for f in frames_dico if not f.empty], ignore_index=True)

cols_dico = ['Año', 'SEDE', 'CARRERA', 'Categoria', 'Pregunta', 'N_Respuestas', 'Frec_Si', 'Frec_No', 'Pct_Si', 'Pct_No']
df_dico = df_dico[cols_dico]

# ==============================================================================
# 3. Calcular Tabla Valores Sebastianos
# ==============================================================================
df_vs = process_vs()
cols_vs = ['Año', 'SEDE', 'CARRERA', 'Valor_Sebastiano', 'N_Respuestas', 'Menciones', 'Pct_Menciones']
if not df_vs.empty:
    df_vs = df_vs[cols_vs]

# ==============================================================================
# EXPORTAR RESULTADOS A SQLITE, EXCEL Y MYSQL (.SQL)
# ==============================================================================
print(f"\nExportando resultados a SQLite: {DB_PATH}")
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

conn = sqlite3.connect(DB_PATH)
df_likert.to_sql('metricas_likert', conn, if_exists='replace', index=False)
df_dico.to_sql('metricas_dicotomicas', conn, if_exists='replace', index=False)
if not df_vs.empty:
    df_vs.to_sql('metricas_valores_sebastianos', conn, if_exists='replace', index=False)
conn.close()

print(f"Exportando resultados a Excel: {EXCEL_PATH}")
try:
    with pd.ExcelWriter(EXCEL_PATH, engine='openpyxl') as writer:
        df_likert.to_excel(writer, sheet_name='Metricas_Likert', index=False)
        df_dico.to_excel(writer, sheet_name='Metricas_Dicotomicas', index=False)
        if not df_vs.empty:
            df_vs.to_excel(writer, sheet_name='Metricas_Valores_Sebastianos', index=False)
except PermissionError:
    print(f"  [!] ADVERTENCIA: No se pudo guardar '{EXCEL_PATH}' porque está abierto en otro programa. Cierra Excel si deseas actualizarlo.")

MYSQL_PATH = "vcm_resultados_mysql.sql"
print(f"Exportando resultados a script MySQL: {MYSQL_PATH}")
def export_to_mysql(df, table_name, f):
    if df.empty: return
    # Generar CREATE TABLE
    cols_def = []
    for c, dtype in zip(df.columns, df.dtypes):
        if pd.api.types.is_float_dtype(dtype):
            cols_def.append(f"`{c}` DOUBLE")
        elif pd.api.types.is_integer_dtype(dtype):
            cols_def.append(f"`{c}` INT")
        else:
            cols_def.append(f"`{c}` VARCHAR(255)")
    
    f.write(f"DROP TABLE IF EXISTS `{table_name}`;\n")
    f.write(f"CREATE TABLE `{table_name}` (\n  " + ",\n  ".join(cols_def) + "\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;\n\n")
    
    # Generar INSERTs en bloques
    values_list = []
    for _, row in df.iterrows():
        vals = []
        for v in row:
            if pd.isna(v):
                vals.append("NULL")
            elif isinstance(v, (str, object)):
                v_clean = str(v).replace("'", "''")
                vals.append(f"'{v_clean}'")
            else:
                vals.append(str(v))
        values_list.append(f"({', '.join(vals)})")
    
    # Escribir inserciones (agrupadas de 100 en 100 para evitar queries muy largos)
    chunk_size = 100
    for i in range(0, len(values_list), chunk_size):
        chunk = values_list[i:i + chunk_size]
        f.write(f"INSERT INTO `{table_name}` VALUES\n")
        f.write(",\n".join(chunk) + ";\n")
    f.write("\n")

with open(MYSQL_PATH, 'w', encoding='utf-8') as f:
    f.write("SET NAMES utf8mb4;\n")
    f.write("SET FOREIGN_KEY_CHECKS = 0;\n\n")
    export_to_mysql(df_likert, 'metricas_likert', f)
    export_to_mysql(df_dico, 'metricas_dicotomicas', f)
    if not df_vs.empty:
        export_to_mysql(df_vs, 'metricas_valores_sebastianos', f)
    f.write("SET FOREIGN_KEY_CHECKS = 1;\n")

print("\n¡Cálculos detallados finalizados con éxito!")
print(f"  -> Base de Datos SQLite: {DB_PATH}")
print(f"  -> Archivo Excel: {EXCEL_PATH}")
print(f"  -> Script MySQL: {MYSQL_PATH}")
