"""
FIX: Reconstruir base con binarios 2024-2025 correctos para Q02-Q13
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import pandas as pd
import numpy as np
import os

OUT = r"c:\Users\oyarc\OneDrive - Universidad San Sebastian\VCM\Encuestas Estudiantes"
df = pd.read_csv(os.path.join(OUT, "base_unificada_homologada.csv"), encoding='utf-8-sig')
print(f"Cargada: {df.shape}")

# El problema: Q02-Q13 para 2024-2025 tienen NaN porque el "0" binario fue limpiado
# Necesito recargar la base PRE-normalización y re-procesar

# Recargar la base original (antes de normalizar)
BASE = r"c:\Users\oyarc\OneDrive - Universidad San Sebastian\VCM\Encuestas Estudiantes\RV_ BASE ENCUESTA ESTUDIANTES 2021-2025"

def load_raw(fp, sheet):
    return pd.read_excel(fp, sheet_name=sheet, header=None)

# Solo necesito recargar 2024 y 2025 para corregir Q02-Q13
for year, fname, sheet in [(2024,"BASE ENCUESTA ESTUDIANTES 2024.xlsx","Reporte"),
                            (2025,"BASE ENCUESTA ESTUDIANTES 2025.xlsx","Reporte")]:
    fp = os.path.join(BASE, fname)
    raw = load_raw(fp, sheet)
    r0, r2 = raw.iloc[0], raw.iloc[2]
    data = raw.iloc[4:].reset_index(drop=True)
    n = len(data)
    
    # Encontrar columnas de importancia y habilidades
    curr = None
    for i in range(len(raw.columns)):
        preg = str(r0.iloc[i]).strip() if pd.notna(r0.iloc[i]) else None
        alt = str(r2.iloc[i]).strip() if pd.notna(r2.iloc[i]) else None
        if preg and preg != 'nan': curr = preg
        if not curr or not alt or alt == 'nan': continue
        alt_l = alt.lower().strip().rstrip('.')
        
        # Mapear alternativas a columnas Q
        target = None
        if 'importan' in curr.lower() and 'logro' in curr.lower():
            if 'aplicar' in alt_l: target = 'Q02_Importancia_Aspectos_Aplicar'
            elif 'realidad' in alt_l: target = 'Q03_Importancia_Aspectos_Realidad'
            elif 'vocación' in alt_l or 'vocacion' in alt_l: target = 'Q04_Importancia_Aspectos_Vocacion'
            elif 'valores sebastianos' in alt_l: target = 'Q05_Importancia_Aspectos_Valores'
        elif 'fortalecidas' in curr.lower() or 'fortalecimiento' in curr.lower():
            if 'empatía' in alt_l or 'empatia' in alt_l: target = 'Q06_Habilidad_Empatia'
            elif 'comunicación' in alt_l or 'comunicacion' in alt_l: target = 'Q07_Habilidad_Comunicacion'
            elif 'colaboración' in alt_l or 'trabajo en equipo' in alt_l: target = 'Q08_Habilidad_Colaboracion'
            elif 'resolución de problemas' in alt_l or 'resolucion de problemas' in alt_l: target = 'Q09_Habilidad_Resolucion'
            elif 'adaptación' in alt_l or 'adaptacion' in alt_l: target = 'Q10_Habilidad_Adaptacion'
            elif 'competencia disciplinar' in alt_l: target = 'Q11_Habilidad_Competencia'
            elif 'prolijidad' in alt_l: target = 'Q12_Habilidad_Prolijidad'
            elif 'manejo de información' in alt_l or 'manejo de informacion' in alt_l: target = 'Q13_Habilidad_Manejo_Info'
        
        if target:
            mask = df['Año'] == year
            vals = []
            for idx in range(n):
                v = data.iloc[idx, i]
                if pd.notna(v):
                    vs = str(v).strip()
                    if vs == '1': vals.append(1.0)
                    elif vs == '0': vals.append(0.0)
                    else: vals.append(np.nan)
                else:
                    vals.append(np.nan)
            df.loc[mask, target] = vals
            non_null = sum(1 for v in vals if not np.isnan(v))
            print(f"  {year} {target}: {non_null} valores restaurados")

# Recalcular TopBox para 2024-2025
tb_cols = [c for c in df.columns if c.endswith('_TopBox')]
for qc in ['Q02_Importancia_Aspectos_Aplicar','Q03_Importancia_Aspectos_Realidad',
           'Q04_Importancia_Aspectos_Vocacion','Q05_Importancia_Aspectos_Valores',
           'Q06_Habilidad_Empatia','Q07_Habilidad_Comunicacion','Q08_Habilidad_Colaboracion',
           'Q09_Habilidad_Resolucion','Q10_Habilidad_Adaptacion','Q11_Habilidad_Competencia',
           'Q12_Habilidad_Prolijidad','Q13_Habilidad_Manejo_Info']:
    tb = qc + '_TopBox'
    if tb in df.columns:
        mask_bin = df['Año'].isin([2024,2025])
        df.loc[mask_bin, tb] = df.loc[mask_bin, qc]

# Verificación final
print("\n% TOP-BOX POR AÑO (comparable):")
for year in [2021,2022,2023,2024,2025]:
    sub = df[df['Año']==year]
    print(f"\n── {year} ({len(sub)}) ──")
    for qc in ['Q02_Importancia_Aspectos_Aplicar','Q07_Habilidad_Comunicacion',
               'Q09_Habilidad_Resolucion','Q15_Importancia_Beneficiados',
               'Q17_Cumplimiento_Expectativas','Q18_Recomendaria']:
        tb = qc + '_TopBox'
        if tb in df.columns:
            vals = sub[tb].dropna()
            if len(vals) > 0:
                print(f"  {qc}: {vals.mean()*100:.1f}% (n={len(vals)})")
        else:
            vals = sub[qc].dropna()
            if len(vals) > 0:
                print(f"  {qc}: media={vals.mean():.2f} (n={len(vals)})")

# Exportar
path = os.path.join(OUT, "base_unificada_homologada.csv")
df.to_csv(path, index=False, encoding='utf-8-sig')
print(f"\n✅ Base corregida: {path}")
print(f"   {df.shape[0]:,} filas x {df.shape[1]} columnas")
print("\nFIN.")
