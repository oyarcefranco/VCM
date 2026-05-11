"""
Extraer estructura completa de cada encuesta: Pregunta → Categoría → Alternativas/Escala
Genera un Excel con una hoja por año mostrando toda la jerarquía.
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
import pandas as pd, numpy as np, os, re

BASE = r"c:\Users\oyarc\OneDrive - Universidad San Sebastian\VCM\Encuestas Estudiantes\RV_ BASE ENCUESTA ESTUDIANTES 2021-2025"
OUT = r"c:\Users\oyarc\OneDrive - Universidad San Sebastian\VCM\Encuestas Estudiantes"

archivos = {
    2021: ("Encuesta estudiantes 2021 Reporte.xlsx", "Base de datos"),
    2022: ("Encuesta estudiantes 2022 Reporte.xlsx", "Base de datos"),
    2023: ("Encuesta estudiantes 2023 Reporte.xlsx", "Base de datos encuestas ajuste"),
    2024: ("BASE ENCUESTA ESTUDIANTES 2024.xlsx", "Reporte"),
    2025: ("BASE ENCUESTA ESTUDIANTES 2025.xlsx", "Reporte"),
}

all_sheets = {}

for year, (fname, sheet) in archivos.items():
    fp = os.path.join(BASE, fname)
    raw = pd.read_excel(fp, sheet_name=sheet, header=None)
    
    print(f"\n{'='*60}")
    print(f"  {year} — {raw.shape[1]} columnas, {raw.shape[0]} filas totales")
    print(f"{'='*60}")
    
    # Mostrar las primeras filas de header para entender la estructura
    if year in (2021, 2022):
        header_rows = [0, 1, 2, 3]  # R0=sección?, R1=pregunta, R2=categoría/alt, R3=código
        data_start = 4
    elif year == 2023:
        header_rows = [0, 1, 2, 3, 4]  # R0=pregunta, R1-R2=?, R3=alt, R4=código
        data_start = 5
    else:  # 2024, 2025
        header_rows = [0, 1, 2, 3]  # R0=pregunta, R1=?, R2=alt, R3=?
        data_start = 4
    
    data = raw.iloc[data_start:].reset_index(drop=True)
    n_data = len(data)
    
    # Extraer info de cada columna
    rows = []
    for i in range(raw.shape[1]):
        row_vals = {}
        for ri in header_rows:
            val = raw.iloc[ri, i] if ri < raw.shape[0] else None
            row_vals[f'Fila_{ri}'] = str(val).strip() if pd.notna(val) else ''
        
        # Contar valores no vacíos en los datos
        non_null = 0
        sample_vals = []
        for j in range(min(n_data, 200)):
            v = data.iloc[j, i]
            if pd.notna(v) and str(v).strip() not in ('', 'nan'):
                non_null += 1
                sv = re.sub(r'\s+', ' ', str(v).strip())
                if sv not in sample_vals and len(sample_vals) < 8:
                    sample_vals.append(sv)
        
        rows.append({
            'Col': i,
            **row_vals,
            'N_Respuestas': non_null,
            'Valores_Ejemplo': ' | '.join(sample_vals),
        })
    
    df_struct = pd.DataFrame(rows)
    
    # Ahora construir la vista jerárquica: Pregunta → Categoría → Alternativa
    # Detectar la pregunta "padre" (celda combinada = se repite el valor de Fila_0 o Fila_1)
    
    if year in (2021, 2022):
        preg_row, cat_row, alt_row, code_row = 'Fila_1', 'Fila_2', 'Fila_2', 'Fila_3'
    elif year == 2023:
        preg_row, cat_row, alt_row, code_row = 'Fila_0', 'Fila_3', 'Fila_3', 'Fila_4'
    else:
        preg_row, cat_row, alt_row, code_row = 'Fila_0', 'Fila_2', 'Fila_2', 'Fila_1'
    
    # Construir tabla jerárquica
    hier_rows = []
    curr_pregunta = ''
    preg_num = 0
    
    for _, r in df_struct.iterrows():
        p = r[preg_row]
        a = r[alt_row]
        
        # Detectar nueva pregunta (celda combinada = valor nuevo en la fila de pregunta)
        if p and p != 'nan' and p != curr_pregunta:
            curr_pregunta = p
            preg_num += 1
        
        hier_rows.append({
            'Num_Pregunta': preg_num,
            'Pregunta': curr_pregunta,
            'Alternativa_Escala': a if a and a != 'nan' else '',
            'Col_Excel': r['Col'],
            'N_Respuestas': r['N_Respuestas'],
            'Valores_Ejemplo': r['Valores_Ejemplo'],
            # También incluir todas las filas de header para referencia
            **{k: r[k] for k in r.index if k.startswith('Fila_')},
        })
    
    df_hier = pd.DataFrame(hier_rows)
    all_sheets[str(year)] = df_hier
    
    # Resumen
    preguntas = df_hier[df_hier['Pregunta'] != ''].groupby('Num_Pregunta').first()
    print(f"  {len(preguntas)} preguntas/secciones detectadas")
    for _, p in preguntas.iterrows():
        alts = df_hier[df_hier['Num_Pregunta'] == p.name]
        n_alts = len(alts[alts['Alternativa_Escala'] != ''])
        print(f"    P{p.name}: [{n_alts} alts] {p['Pregunta'][:80]}")

# Exportar
path = os.path.join(OUT, "estructura_encuestas_por_año.xlsx")
with pd.ExcelWriter(path, engine='openpyxl') as writer:
    for name, sdf in all_sheets.items():
        sdf.to_excel(writer, sheet_name=name, index=False)

print(f"\n✅ {path}")
print("FIN.")
