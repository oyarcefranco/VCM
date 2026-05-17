import pandas as pd
import numpy as np
import sqlite3
import os

BASE_DIR = r"c:\Users\oyarc\OneDrive - Universidad San Sebastian\VCM\Encuestas Estudiantes"
INPUT_FILE = os.path.join(BASE_DIR, "base_homologada_organizaciones.xlsx")
DB_PATH = os.path.join(BASE_DIR, "vcm_resultados_org.db")
EXCEL_PATH = os.path.join(BASE_DIR, "metricas_detalladas_org.xlsx")
MYSQL_PATH = os.path.join(BASE_DIR, "vcm_resultados_org_mysql.sql")

print(f"Cargando la base de datos homologada desde {os.path.basename(INPUT_FILE)}...")
df = pd.read_excel(INPUT_FILE)

# --- DEFINICIÓN DE PREGUNTAS ---
LIKERT_KEYS = [
    'ORG_USS_01', 'ORG_USS_02', 'ORG_USS_03', 'ORG_USS_04', 'ORG_USS_05_Likert',
    'ORG_EJE_01', 'ORG_EJE_02', 'ORG_EJE_03', 'ORG_EJE_04', 'ORG_EJE_05', 'ORG_EJE_06',
    'ORG_IMP_01', 'ORG_IMP_03'
]

DICO_KEYS = [
    'ORG_IMP_02', 'ORG_USS_05_SiNo', 'ORG_CONTRATACION', 'ORG_RECOMENDACION'
]

NOTA_KEYS = ['ORG_SATISFACCION_NOTA']

# Nombres legibles para Excel/DB
NOMBRES = {
    'ORG_USS_01': 'USS vincula adecuadamente',
    'ORG_USS_02': 'Proceso colaborativo mutuo',
    'ORG_USS_03': 'Aporte trabajar con USS',
    'ORG_USS_04': 'Contrataría profesionales USS',
    'ORG_USS_05_Likert': 'Interés en seguir trabajando (Likert)',
    'ORG_USS_05_SiNo': 'Interés en seguir trabajando (Sí/No)',
    'ORG_EJE_01': 'Planificación adecuada',
    'ORG_EJE_02': 'Ejecución cumplió objetivos',
    'ORG_EJE_03': 'Se cumplieron compromisos',
    'ORG_EJE_04': 'Comunicación eficaz',
    'ORG_EJE_05': 'Servicio/producto de calidad',
    'ORG_EJE_06': 'Acceso a nuevas redes',
    'ORG_IMP_01': 'Impacto positivo en comunidad',
    'ORG_IMP_02': 'Aporte trabajar con estudiantes',
    'ORG_IMP_03': 'Beneficioso para el estudiante',
    'ORG_CONTRATACION': 'Incorporó estudiantes/egresados',
    'ORG_RECOMENDACION': 'Recomendaría trabajar con USS',
    'ORG_SATISFACCION_NOTA': 'Nota Satisfacción General'
}

# --- FUNCIONES DE AGREGACIÓN ---
def agg_likert(df, value_col):
    df_valid = df.dropna(subset=[value_col]).copy()
    if df_valid.empty:
        return pd.DataFrame()
    
    df_valid['is_t2b'] = df_valid[value_col].isin([4, 5]).astype(int)
    for i in range(1, 6):
        df_valid[f'is_{i}'] = (df_valid[value_col] == i).astype(int)
        
    agg = df_valid.groupby(['Año']).agg(
        N_Respuestas=(value_col, 'count'),
        Promedio=(value_col, 'mean'),
        Frec_T2B=('is_t2b', 'sum'),
        Frec_5=('is_5', 'sum'),
        Frec_4=('is_4', 'sum'),
        Frec_3=('is_3', 'sum'),
        Frec_2=('is_2', 'sum'),
        Frec_1=('is_1', 'sum')
    ).reset_index()
    
    agg['Promedio'] = agg['Promedio'].round(2)
    agg['Pct_T2B'] = (agg['Frec_T2B'] / agg['N_Respuestas'] * 100).round(1)
    for i in range(1, 6):
        agg[f'Pct_{i}'] = (agg[f'Frec_{i}'] / agg['N_Respuestas'] * 100).round(1)
        
    agg.insert(0, 'Pregunta', NOMBRES.get(value_col, value_col))
    agg.insert(0, 'Codigo_Pregunta', value_col)
    return agg

def agg_dico(df, value_col):
    df_valid = df.dropna(subset=[value_col]).copy()
    if df_valid.empty:
        return pd.DataFrame()
        
    agg = df_valid.groupby(['Año']).agg(
        N_Respuestas=(value_col, 'count'),
        Frec_1=(value_col, 'sum')
    ).reset_index()
    
    agg['Frec_0'] = agg['N_Respuestas'] - agg['Frec_1']
    agg['Pct_Si'] = (agg['Frec_1'] / agg['N_Respuestas'] * 100).round(1)
    
    agg.insert(0, 'Pregunta', NOMBRES.get(value_col, value_col))
    agg.insert(0, 'Codigo_Pregunta', value_col)
    return agg

def agg_nota(df, value_col):
    df_valid = df.dropna(subset=[value_col]).copy()
    if df_valid.empty:
        return pd.DataFrame()
        
    for i in range(1, 8):
        df_valid[f'is_{i}'] = (df_valid[value_col] == i).astype(int)
        
    agg = df_valid.groupby(['Año']).agg(
        N_Respuestas=(value_col, 'count'),
        Promedio=(value_col, 'mean'),
        Frec_7=('is_7', 'sum'),
        Frec_6=('is_6', 'sum'),
        Frec_5=('is_5', 'sum'),
        Frec_4=('is_4', 'sum'),
        Frec_3=('is_3', 'sum'),
        Frec_2=('is_2', 'sum'),
        Frec_1=('is_1', 'sum')
    ).reset_index()
    
    for i in range(1, 8):
        agg[f'Pct_{i}'] = (agg[f'Frec_{i}'] / agg['N_Respuestas'] * 100).round(1)
        
    agg['Promedio'] = agg['Promedio'].round(2)
    agg.insert(0, 'Pregunta', NOMBRES.get(value_col, value_col))
    agg.insert(0, 'Codigo_Pregunta', value_col)
    return agg

# --- PROCESAMIENTO ---
print("Calculando métricas Likert...")
res_likert = []
for k in LIKERT_KEYS:
    if k in df.columns:
        res_likert.append(agg_likert(df, k))
df_likert = pd.concat(res_likert, ignore_index=True) if res_likert else pd.DataFrame()

print("Calculando métricas Dicotómicas...")
res_dico = []
for k in DICO_KEYS:
    if k in df.columns:
        res_dico.append(agg_dico(df, k))
df_dico = pd.concat(res_dico, ignore_index=True) if res_dico else pd.DataFrame()

print("Calculando métricas Notas (1 a 7)...")
res_nota = []
for k in NOTA_KEYS:
    if k in df.columns:
        res_nota.append(agg_nota(df, k))
df_nota = pd.concat(res_nota, ignore_index=True) if res_nota else pd.DataFrame()

# --- EXPORTAR A SQLITE ---
print(f"\nExportando resultados a SQLite: {os.path.basename(DB_PATH)}")
with sqlite3.connect(DB_PATH) as conn:
    if not df_likert.empty: df_likert.to_sql('metricas_likert_org', conn, if_exists='replace', index=False)
    if not df_dico.empty: df_dico.to_sql('metricas_dicotomicas_org', conn, if_exists='replace', index=False)
    if not df_nota.empty: df_nota.to_sql('metricas_nota_org', conn, if_exists='replace', index=False)

# --- EXPORTAR A EXCEL ---
print(f"Exportando resultados a Excel: {os.path.basename(EXCEL_PATH)}")
try:
    with pd.ExcelWriter(EXCEL_PATH, engine='openpyxl') as writer:
        if not df_likert.empty: df_likert.to_excel(writer, sheet_name='Metricas_Likert', index=False)
        if not df_dico.empty: df_dico.to_excel(writer, sheet_name='Metricas_Dicotomicas', index=False)
        if not df_nota.empty: df_nota.to_excel(writer, sheet_name='Metricas_Nota', index=False)
except PermissionError:
    print(f"\n[ERROR CRÍTICO] No se pudo escribir en el archivo {os.path.basename(EXCEL_PATH)}")
    print("Asegúrate de que Excel esté cerrado y vuelve a intentarlo.")

# --- EXPORTAR A MYSQL SCRIPT ---
print(f"Exportando resultados a script MySQL: {os.path.basename(MYSQL_PATH)}")
def export_to_mysql(df_to_export, table_name, f):
    if df_to_export.empty: return
    
    # Crear estructura de tabla
    cols = []
    for col_name, dtype in zip(df_to_export.columns, df_to_export.dtypes):
        if pd.api.types.is_integer_dtype(dtype):
            cols.append(f"`{col_name}` INT")
        elif pd.api.types.is_float_dtype(dtype):
            cols.append(f"`{col_name}` FLOAT")
        else:
            cols.append(f"`{col_name}` VARCHAR(255)")
    
    f.write(f"DROP TABLE IF EXISTS `{table_name}`;\n")
    f.write(f"CREATE TABLE `{table_name}` (\n  " + ",\n  ".join(cols) + "\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;\n\n")
    
    # Insertar datos en bloques
    values_list = []
    for _, row in df_to_export.iterrows():
        row_vals = []
        for val in row:
            if pd.isna(val):
                row_vals.append("NULL")
            elif isinstance(val, str):
                val_escaped = val.replace("'", "''")
                row_vals.append(f"'{val_escaped}'")
            else:
                row_vals.append(str(val))
        values_list.append("(" + ", ".join(row_vals) + ")")
    
    chunk_size = 500
    for i in range(0, len(values_list), chunk_size):
        chunk = values_list[i:i + chunk_size]
        f.write(f"INSERT INTO `{table_name}` VALUES\n")
        f.write(",\n".join(chunk) + ";\n")
    f.write("\n")

with open(MYSQL_PATH, 'w', encoding='utf-8') as f:
    f.write("SET NAMES utf8mb4;\n")
    f.write("SET FOREIGN_KEY_CHECKS = 0;\n\n")
    export_to_mysql(df_likert, 'metricas_likert_org', f)
    export_to_mysql(df_dico, 'metricas_dicotomicas_org', f)
    export_to_mysql(df_nota, 'metricas_nota_org', f)
    f.write("SET FOREIGN_KEY_CHECKS = 1;\n")

print("\n¡Cálculos de organizaciones finalizados con éxito!")
print(f"  -> SQLite: {DB_PATH}")
print(f"  -> Excel: {EXCEL_PATH}")
print(f"  -> MySQL: {MYSQL_PATH}")
