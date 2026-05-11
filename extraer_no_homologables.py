import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
import pandas as pd, os

BASE = r"c:\Users\oyarc\OneDrive - Universidad San Sebastian\VCM\Encuestas Estudiantes\RV_ BASE ENCUESTA ESTUDIANTES 2021-2025"
OUT = r"c:\Users\oyarc\OneDrive - Universidad San Sebastian\VCM\Encuestas Estudiantes"

archivos = {
    2021: ("Encuesta estudiantes 2021 Reporte.xlsx", "Base de datos", 4),
    2022: ("Encuesta estudiantes 2022 Reporte.xlsx", "Base de datos", 4),
    2023: ("Encuesta estudiantes 2023 Reporte.xlsx", "Base de datos encuestas ajuste", 5),
    2024: ("BASE ENCUESTA ESTUDIANTES 2024.xlsx", "Reporte", 4),
    2025: ("BASE ENCUESTA ESTUDIANTES 2025.xlsx", "Reporte", 4),
}

RUT_COL = {2021: 1, 2022: 1, 2023: 1, 2024: 0, 2025: 0}
META_COLS = {
    2021: {'SEDE': 5, 'FACULTAD': 3, 'CARRERA': 2},
    2022: {'SEDE': 5, 'FACULTAD': 3, 'CARRERA': 2},
    2023: {'SEDE': 5, 'FACULTAD': 6, 'CARRERA': 7},
    2024: {'SEDE': 7, 'FACULTAD': 8, 'CARRERA': 9},
    2025: {'SEDE': 7, 'FACULTAD': 8, 'CARRERA': 9},
}

def get_meta(data, year, n):
    rc = RUT_COL[year]
    res = {'Año': [year]*n}
    res['RUT'] = [str(data.iloc[i, rc]).strip() if pd.notna(data.iloc[i, rc]) else None for i in range(n)]
    for mk, ci in META_COLS[year].items():
        res[mk] = [str(data.iloc[i, ci]).strip() if pd.notna(data.iloc[i, ci]) else None for i in range(n)]
    return pd.DataFrame(res)

writer = pd.ExcelWriter(os.path.join(OUT, "preguntas_especificas_por_año.xlsx"), engine='openpyxl')

for year, (fname, sheet, ds) in archivos.items():
    fp = os.path.join(BASE, fname)
    raw = pd.read_excel(fp, sheet_name=sheet, header=None)
    data = raw.iloc[ds:].reset_index(drop=True)
    n = len(data)
    
    meta_df = get_meta(data, year, n)
    
    if year in [2021, 2022]:
        # Como se originó: cols 10 a 17. Vamos a extraer todo el texto que haya
        orig = []
        for i in range(n):
            resp = []
            for c in range(10, 18):
                v = data.iloc[i, c]
                if pd.notna(v) and str(v).strip() not in ('0', '', 'nan'):
                    resp.append(str(v).strip())
            orig.append(" | ".join(resp) if resp else None)
        df1 = meta_df.copy()
        df1['¿Cómo se originó tu participación?'] = orig
        df1.to_excel(writer, sheet_name=f'ComoSeOrigino_{year}', index=False)
        
        # Has comentado
        com = [str(data.iloc[i, 89]).strip() if pd.notna(data.iloc[i, 89]) else None for i in range(n)]
        df2 = meta_df.copy()
        df2['¿Has comentado a tus compañeros sobre tu participación?'] = com
        df2.to_excel(writer, sheet_name=f'HasComentado_{year}', index=False)

    elif year == 2023:
        # Como se originó: cols 8 y 9
        orig = []
        for i in range(n):
            resp = []
            for c in [8, 9]:
                v = data.iloc[i, c]
                if pd.notna(v) and str(v).strip() not in ('0', '', 'nan'):
                    resp.append(str(v).strip())
            orig.append(" | ".join(resp) if resp else None)
        df1 = meta_df.copy()
        df1['¿Cómo se originó tu participación?'] = orig
        df1.to_excel(writer, sheet_name=f'ComoSeOrigino_2023', index=False)
        
        # Has comentado: col 46
        com = [str(data.iloc[i, 46]).strip() if pd.notna(data.iloc[i, 46]) else None for i in range(n)]
        df2 = meta_df.copy()
        df2['¿Has comentado a tus compañeros sobre tu participación?'] = com
        df2.to_excel(writer, sheet_name=f'HasComentado_2023', index=False)

    elif year == 2024:
        # Recibiste info propósito: 147, 148 (one-hot) -> "Sí" en 147, "No" en 148
        prop = []
        for i in range(n):
            if str(data.iloc[i, 147]).strip() == '1': prop.append('Sí')
            elif str(data.iloc[i, 148]).strip() == '1': prop.append('No')
            else: prop.append(None)
        
        # Recibiste info aporte: 149, 150 (one-hot) -> "Sí" en 149, "No" en 150
        apor = []
        for i in range(n):
            if str(data.iloc[i, 149]).strip() == '1': apor.append('Sí')
            elif str(data.iloc[i, 150]).strip() == '1': apor.append('No')
            else: apor.append(None)
            
        df_info = meta_df.copy()
        df_info['¿Recibiste información sobre el fin o propósito?'] = prop
        df_info['¿Recibiste información sobre cuál sería tu aporte?'] = apor
        df_info.to_excel(writer, sheet_name='InfoRecibida_2024', index=False)
        
        # Nota: cols 159 a 165 (1 a 7)
        nota = []
        for i in range(n):
            val = None
            for idx, n_val in enumerate([1,2,3,4,5,6,7]):
                if str(data.iloc[i, 159+idx]).strip() in ('1', '1.0'):
                    val = n_val
                    break
            nota.append(val)
        df_nota = meta_df.copy()
        df_nota['¿Qué nota le pondrías a la experiencia vivida?'] = nota
        df_nota.to_excel(writer, sheet_name='NotaExperiencia_2024', index=False)

    elif year == 2025:
        # Por qué (impacto): 15
        pq = [str(data.iloc[i, 15]).strip() if pd.notna(data.iloc[i, 15]) else None for i in range(n)]
        
        # Dificultó: 128
        dif = [str(data.iloc[i, 128]).strip() if pd.notna(data.iloc[i, 128]) else None for i in range(n)]
        
        df_text = meta_df.copy()
        df_text['¿Por qué el impacto fue positivo/negativo?'] = pq
        df_text['¿Hubo algo que dificultó tu participación?'] = dif
        df_text.to_excel(writer, sheet_name='TextosLibres_2025', index=False)

writer.close()
print("Exportación de preguntas específicas completada.")
