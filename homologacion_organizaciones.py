import pandas as pd
import numpy as np
import os
import re

BASE_DIR = r"c:\Users\oyarc\OneDrive - Universidad San Sebastian\VCM\Encuestas Estudiantes\Encuesta organizaciones externas"
OUTPUT_PATH = r"c:\Users\oyarc\OneDrive - Universidad San Sebastian\VCM\Encuestas Estudiantes\base_homologada_organizaciones.xlsx"

# Archivos por año
FILES = {
    2021: ("Encuesta organizaciones 2021 Reporte.xlsx", "Raw Data", 3),
    2022: ("Encuesta organizaciones 2022 Reporte N°2.xlsx", "Raw Data", 3),
    2023: ("Encuesta organizaciones 2023 Reporte.xlsx", "Raw Data", 3),
    2024: ("Encuesta Organizaciones externas_2024.xlsx", "Reporte", 4),
    2025: ("Base de datos encuesta organizaciones externas 2025.xlsx", "Reporte", 4)
}

# Diccionarios de mapeo para parsear texto a numérico
M_ACU = {
    'muy de acuerdo': 5, 'de acuerdo': 4, 'ni de acuerdo ni en desacuerdo': 3,
    'en desacuerdo': 2, 'muy en desacuerdo': 1
}
M_SINO = {'sí': 1, 'si': 1, 'no': 0, 'sí.': 1, 'no.': 0, 's.': 1, 's': 1}

# Columnas objetivo a generar
ALL_USS_KEYS = ['ORG_USS_01', 'ORG_USS_02', 'ORG_USS_03', 'ORG_USS_04']
ALL_EJE_KEYS = ['ORG_EJE_01', 'ORG_EJE_02', 'ORG_EJE_03', 'ORG_EJE_04', 'ORG_EJE_05', 'ORG_EJE_06']
ALL_IMP_KEYS = ['ORG_IMP_01', 'ORG_IMP_03']
ALL_DICO_KEYS = ['ORG_IMP_02', 'ORG_USS_05_SiNo', 'ORG_CONTRATACION', 'ORG_RECOMENDACION']
ALL_OTRAS_KEYS = ['ORG_USS_05_Likert', 'ORG_SATISFACCION_NOTA']

# Ubicación de las columnas por año (índices 0-based)
USS_COLS = {
    2021: {'ORG_USS_01': 53, 'ORG_USS_02': 54, 'ORG_USS_03': 55, 'ORG_USS_04': 56, 'ORG_USS_05_Likert': 57},
    2022: {'ORG_USS_01': 85, 'ORG_USS_02': 90, 'ORG_USS_03': 95, 'ORG_USS_04': 100, 'ORG_USS_05_Likert': 105},
    2023: {'ORG_USS_01': 85, 'ORG_USS_02': 90, 'ORG_USS_03': 95, 'ORG_USS_04': 100, 'ORG_USS_05_Likert': 105},
    2024: {'ORG_USS_01': 8, 'ORG_USS_02': 13, 'ORG_USS_03': 18, 'ORG_USS_04': 23}, 
    2025: {'ORG_USS_01': 8, 'ORG_USS_02': 13, 'ORG_USS_03': 18, 'ORG_USS_04': 23}  
}

EJE_COLS = {
    2021: {'ORG_EJE_01': 46, 'ORG_EJE_02': 47, 'ORG_EJE_03': 48, 'ORG_EJE_04': 49, 'ORG_EJE_05': 50, 'ORG_EJE_06': 51},
    2022: {'ORG_EJE_01': 55, 'ORG_EJE_02': 60, 'ORG_EJE_03': 65, 'ORG_EJE_04': 70, 'ORG_EJE_05': 75, 'ORG_EJE_06': 80},
    2023: {'ORG_EJE_01': 55, 'ORG_EJE_02': 60, 'ORG_EJE_03': 65, 'ORG_EJE_04': 70, 'ORG_EJE_05': 75, 'ORG_EJE_06': 80},
    2024: {'ORG_EJE_01': 36, 'ORG_EJE_03': 41, 'ORG_EJE_04': 46, 'ORG_EJE_05': 51, 'ORG_EJE_06': 56}, 
    2025: {'ORG_EJE_04': 33, 'ORG_EJE_03': 38, 'ORG_EJE_05': 43, 'ORG_EJE_06': 48} 
}

IMP_COLS = {
    2021: {'ORG_IMP_01': 31, 'ORG_IMP_03': 45}, 
    2022: {'ORG_IMP_01': 21, 'ORG_IMP_03': 35},
    2023: {'ORG_IMP_01': 21, 'ORG_IMP_03': 35},
    2024: {'ORG_IMP_01': 61}, 
    2025: {'ORG_IMP_01': 53} 
}

DICO_COLS = {
    2021: {'ORG_IMP_02': 43, 'ORG_RECOMENDACION': 61},
    2022: {'ORG_IMP_02': 34, 'ORG_CONTRATACION': 37, 'ORG_RECOMENDACION': 111},
    2023: {'ORG_IMP_02': 34, 'ORG_CONTRATACION': 37, 'ORG_RECOMENDACION': 111},
    2024: {'ORG_IMP_02': 66, 'ORG_CONTRATACION': 68, 'ORG_RECOMENDACION': 31, 'ORG_USS_05_SiNo': 28},
    2025: {'ORG_CONTRATACION': 58, 'ORG_RECOMENDACION': 31, 'ORG_USS_05_SiNo': 28}
}

NOTA_COLS = {
    2021: 60,
    2022: 110,
    2023: 110,
    2024: 71
}

def clean_text(val):
    if pd.isna(val): return ""
    v = str(val).strip().lower()
    return v

def parse_text(val, mapping):
    v = clean_text(val)
    if v == "": return np.nan
    # Exact match
    if v in mapping: return mapping[v]
    # Partial match (sort by length descending)
    sorted_keys = sorted(mapping.keys(), key=len, reverse=True)
    for k in sorted_keys:
        if k in v: return mapping[k]
    # Try parsing as float directly
    try:
        f = float(val)
        if not np.isnan(f): return f
    except:
        pass
    return np.nan

def extract_onehot(data, raw_df, col_start, n_cols, mapping):
    """
    Lee 5 columnas a partir de col_start. Busca el encabezado de esa columna 
    en las filas 3 a 0, y lo mapea de manera estricta.
    """
    res = []
    sorted_keys = sorted(mapping.keys(), key=len, reverse=True)
    # Buscar el texto del header para estas 5 columnas
    headers_text = []
    for c in range(col_start, col_start + n_cols):
        found_txt = ""
        # Buscar de abajo hacia arriba para evitar atrapar la pregunta larga en row 0
        for r in reversed(range(4)): 
            cell = clean_text(raw_df.iloc[r, c])
            if cell == "": continue
            
            # Exact match primero
            if cell in mapping:
                found_txt = cell
                break
                
            # Partial match solo si es un texto razonablemente corto (opción de respuesta)
            if len(cell) < 60:
                for k in sorted_keys:
                    if k in cell:
                        found_txt = cell
                        break
            if found_txt: break
            
        headers_text.append(found_txt)

    for i in range(len(data)):
        row_vals = data.iloc[i, col_start:col_start+n_cols]
        mapped_val = np.nan
        for j, val in enumerate(row_vals):
            # En la matriz de 2022-2025, si seleccionaron la opción viene un 1 (numérico o texto) o "Sí"
            try:
                v = float(val)
                if v == 1.0:
                    # Encontró la marca
                    mapped_val = parse_text(headers_text[j], mapping)
                    break
            except:
                if clean_text(val) in ['1', 'x', 'sí', 'si', 's', 's.']:
                    mapped_val = parse_text(headers_text[j], mapping)
                    break
        res.append(mapped_val)
    return res

print(f"Iniciando homologación de Organizaciones Externas...")
all_dfs = []

for year in [2021, 2022, 2023, 2024, 2025]:
    if year not in FILES: continue
    filename, sheet, data_start = FILES[year]
    path = os.path.join(BASE_DIR, filename)
    print(f"\nProcesando {year} - {filename}")
    
    try:
        raw = pd.read_excel(path, sheet_name=sheet, header=None)
    except Exception as e:
        print(f"  [ERROR] No se pudo leer el archivo: {e}")
        continue
    
    data = raw.iloc[data_start:].reset_index(drop=True)
    n = len(data)
    
    # Crear un diccionario para la nueva data
    row_dict = {'Año': [year] * n}
    
    # Evaluar si el año es one-hot
    is_oh = year >= 2022
    
    def process_likert(val, year):
        v = parse_text(val, M_ACU)
        if year == 2021 and pd.notna(v):
            v_str = str(clean_text(val)).replace('.0', '')
            if v_str in ['1', '2', '3', '4', '5']:
                return 6 - v
        return v

    # 1. EVALUACION TRABAJO USS
    for k in ALL_USS_KEYS + ['ORG_USS_05_Likert']:
        if k in USS_COLS.get(year, {}):
            ci = USS_COLS[year][k]
            if is_oh and year >= 2022:
                row_dict[k] = extract_onehot(data, raw, ci, 5, M_ACU)
            else:
                row_dict[k] = [process_likert(data.iloc[i, ci], year) for i in range(n)]
        else:
            row_dict[k] = [np.nan] * n

    # 2. EJECUCION PROYECTO
    for k in ALL_EJE_KEYS:
        if k in EJE_COLS.get(year, {}):
            ci = EJE_COLS[year][k]
            if is_oh and year >= 2022:
                row_dict[k] = extract_onehot(data, raw, ci, 5, M_ACU)
            else:
                row_dict[k] = [process_likert(data.iloc[i, ci], year) for i in range(n)]
        else:
            row_dict[k] = [np.nan] * n

    # 3. IMPACTO
    for k in ALL_IMP_KEYS:
        if k in IMP_COLS.get(year, {}):
            ci = IMP_COLS[year][k]
            if is_oh and year >= 2022:
                row_dict[k] = extract_onehot(data, raw, ci, 5, M_ACU)
            else:
                row_dict[k] = [process_likert(data.iloc[i, ci], year) for i in range(n)]
        else:
            row_dict[k] = [np.nan] * n

    # 4. DICOTOMICAS
    for k in ALL_DICO_KEYS:
        if k in DICO_COLS.get(year, {}):
            ci = DICO_COLS[year][k]
            col_data = []
            for i in range(n):
                val = data.iloc[i, ci]
                v_clean = clean_text(val).replace('.0', '')
                if v_clean in ['1', 'sí', 'si', 's', 's.', 'sí.']:
                    col_data.append(1.0)
                elif v_clean in ['2', '0', 'no', 'no.']:
                    col_data.append(0.0)
                else:
                    col_data.append(np.nan)
            row_dict[k] = col_data
        else:
            row_dict[k] = [np.nan] * n

    # 5. SATISFACCION NOTA (1 a 7)
    if year in NOTA_COLS:
        ci = NOTA_COLS[year]
        col_data = []
        for i in range(n):
            try:
                val = float(data.iloc[i, ci])
                if 1 <= val <= 7:
                    col_data.append(val)
                else:
                    col_data.append(np.nan)
            except:
                col_data.append(np.nan)
        row_dict['ORG_SATISFACCION_NOTA'] = col_data
    else:
        row_dict['ORG_SATISFACCION_NOTA'] = [np.nan] * n

    df_year = pd.DataFrame(row_dict)
    # Limpiar filas donde TODAS las métricas sean NaN (para evitar basura de excel)
    metrics_cols = ALL_USS_KEYS + ['ORG_USS_05_Likert'] + ALL_EJE_KEYS + ALL_IMP_KEYS + ALL_DICO_KEYS + ['ORG_SATISFACCION_NOTA']
    df_year.dropna(subset=metrics_cols, how='all', inplace=True)
    print(f"  Filas procesadas: {len(df_year)}")
    all_dfs.append(df_year)

if all_dfs:
    final_df = pd.concat(all_dfs, ignore_index=True)
    
    # Eliminar posibles filas completamente vacías al final
    final_df = final_df[final_df['Año'].notna()]
    
    try:
        final_df.to_excel(OUTPUT_PATH, index=False)
        print(f"\n==================================================")
        print(f"EXITO Base homologada exportada a:")
        print(f"   {OUTPUT_PATH}")
        print(f"   Total filas: {len(final_df)}")
        print(f"==================================================")
    except Exception as e:
        print(f"\n[ERROR CRÍTICO] No se pudo guardar el archivo Excel: {e}")
        print("Asegúrate de tener Excel CERRADO.")

