import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
import pandas as pd
import os
import json
import numpy as np

BASE_PATH = r"c:\Users\oyarc\OneDrive - Universidad San Sebastian\VCM\Encuestas Estudiantes\base_homologada_final.xlsx"
OUT_PATH = r"c:\Users\oyarc\OneDrive - Universidad San Sebastian\VCM\Encuestas Estudiantes\dashboard_data_detalle.json"

print("Cargando la base de datos homologada...")
xls = pd.ExcelFile(BASE_PATH)

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
    'IMP_12': 'Conocer campo laboral',
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

def calc_t2b(series):
    valid_data = series.dropna()
    if len(valid_data) == 0: return np.nan
    return valid_data[valid_data >= 4].count() / len(valid_data)

def calc_avg(series):
    return series.dropna().mean()

def calc_dist(series):
    valid = series.dropna()
    n = len(valid)
    if n == 0:
        return {1:0, 2:0, 3:0, 4:0, 5:0}
    counts = valid.value_counts(normalize=True).to_dict()
    return {
        1: counts.get(1, 0),
        2: counts.get(2, 0),
        3: counts.get(3, 0),
        4: counts.get(4, 0),
        5: counts.get(5, 0)
    }

output_data = {}

# 1. KPIs Generales
print("Procesando KPIs Generales...")
df_rec = pd.read_excel(xls, sheet_name='Recomendaria')
df_sig = pd.read_excel(xls, sheet_name='Significancia_Formacion')
df_exp = pd.read_excel(xls, sheet_name='Cumplimiento_Expectativas')

total_encuestados = len(df_rec)
output_data['kpis'] = [
    {"Métrica": "Total Estudiantes Impactados (2021-2025)", "Valor": total_encuestados},
    {"Métrica": "Índice de Recomendación Global", "Valor": f"{calc_avg(df_rec['Recomendaria'])*100:.1f}%"},
    {"Métrica": "Impacto Positivo en Formación (T2B Global)", "Valor": f"{calc_t2b(df_sig['Q01_Significancia'])*100:.1f}%"},
    {"Métrica": "Expectativas Cumplidas (T2B Global)", "Valor": f"{calc_t2b(df_exp['Cumplimiento_Expectativas'])*100:.1f}%"}
]

def process_likert_sheet(sheet_name, name_mapping, value_cols):
    df = pd.read_excel(xls, sheet_name=sheet_name)
    results = []
    for col in value_cols:
        if col not in df.columns: continue
        for year in [2021, 2022, 2023, 2024, 2025]:
            subset = df[df['Año'] == year][col]
            valid_n = subset.dropna().count()
            if valid_n > 0:
                dist = calc_dist(subset)
                results.append({
                    'Año': year,
                    'Código': col,
                    'Indicador': name_mapping.get(col, col),
                    'N_Respuestas': int(valid_n),
                    'Top_2_Box (%)': calc_t2b(subset),
                    'Promedio (1-5)': calc_avg(subset),
                    '% 1': dist[1],
                    '% 2': dist[2],
                    '% 3': dist[3],
                    '% 4': dist[4],
                    '% 5': dist[5]
                })
    return results

print("Procesando Importancia Aspectos...")
output_data['importancia'] = process_likert_sheet('Importancia_Aspectos', NOMBRES_IMP, NOMBRES_IMP.keys())

print("Procesando Habilidades...")
output_data['habilidades'] = process_likert_sheet('Habilidades', NOMBRES_HAB, NOMBRES_HAB.keys())

def process_single_var(sheet_name, col_name, label):
    df = pd.read_excel(xls, sheet_name=sheet_name)
    results = []
    for year in [2021, 2022, 2023, 2024, 2025]:
        if year not in df['Año'].values: continue
        subset = df[df['Año'] == year][col_name]
        valid_n = subset.dropna().count()
        if valid_n > 0:
            if set(subset.dropna().unique()).issubset({0, 1, 0.0, 1.0}):
                val = calc_avg(subset)
            else:
                val = calc_t2b(subset)
            results.append({
                'Año': year,
                'Indicador': label,
                'N_Respuestas': int(valid_n),
                'Resultado (%)': val
            })
    return results

print("Procesando Variables Generales...")
frames_gen = []
frames_gen.extend(process_single_var('Significancia_Formacion', 'Q01_Significancia', 'Significancia en Formación (T2B)'))
frames_gen.extend(process_single_var('Importancia_Beneficiados', 'Importancia_Beneficiados', 'Importancia para Beneficiados (T2B)'))
frames_gen.extend(process_single_var('Cumplimiento_Expectativas', 'Cumplimiento_Expectativas', 'Expectativas Cumplidas (T2B)'))
frames_gen.extend(process_single_var('Recomendaria', 'Recomendaria', 'Recomendaría a compañeros (% Sí)'))
frames_gen.extend(process_single_var('Campo_Laboral_SiNo', 'Campo_Laboral_SiNo', 'Permitió conocer campo laboral (% Sí)'))
frames_gen.extend(process_single_var('Vinculacion_Medio', 'Vinculacion_Medio', 'Sabía que era VcM (% Sí)'))
output_data['indicadores'] = frames_gen

print("Procesando Valores Sebastianos...")
df_vs = pd.read_excel(xls, sheet_name='Valores_Sebastianos')
vs_cols = [c for c in df_vs.columns if c.startswith('VS_')]
results_vs = []
for year in [2021, 2022, 2023, 2024, 2025]:
    sub_year = df_vs[df_vs['Año'] == year]
    n_year = len(sub_year)
    if n_year == 0: continue
    for col in vs_cols:
        subset = sub_year[col].dropna()
        if len(subset) > 0 and subset.sum() > 0:
            results_vs.append({
                'Año': year,
                'Valor Sebastiano': col.replace('VS_', ''),
                'Menciones': int(subset.sum()),
                '% de Estudiantes': float(subset.sum() / n_year)
            })
results_vs.sort(key=lambda x: (x['Año'], -x['% de Estudiantes']))
output_data['valores'] = results_vs

with open(OUT_PATH, 'w', encoding='utf-8') as f:
    json.dump(output_data, f, ensure_ascii=False)

print(f"JSON generado exitosamente en {OUT_PATH}")
