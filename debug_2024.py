"""Debug: ver exactamente qué alternativas tiene cada pregunta en 2024-2025"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
import pandas as pd, os

BASE = r"c:\Users\oyarc\OneDrive - Universidad San Sebastian\VCM\Encuestas Estudiantes\RV_ BASE ENCUESTA ESTUDIANTES 2021-2025"

for year, fname, sheet in [(2024,"BASE ENCUESTA ESTUDIANTES 2024.xlsx","Reporte"),
                            (2025,"BASE ENCUESTA ESTUDIANTES 2025.xlsx","Reporte")]:
    raw = pd.read_excel(os.path.join(BASE, fname), sheet_name=sheet, header=None)
    r0, r2 = raw.iloc[0], raw.iloc[2]
    data = raw.iloc[4:]
    curr = None
    print(f"\n{'='*60}\n  {year}\n{'='*60}")
    for i in range(len(raw.columns)):
        preg = str(r0.iloc[i]).strip() if pd.notna(r0.iloc[i]) else None
        alt = str(r2.iloc[i]).strip() if pd.notna(r2.iloc[i]) else None
        if preg and preg != 'nan': curr = preg
        if not curr: continue
        cl = curr.lower()
        if ('importan' in cl and 'logro' in cl) or ('fortalecidas' in cl) or ('fortalecimiento' in cl):
            # Mostrar los primeros valores de datos
            sample = [str(data.iloc[j,i]) for j in range(min(5,len(data))) if pd.notna(data.iloc[j,i])]
            print(f"  Col {i}: [{curr[:60]}...] alt='{alt}' datos={sample[:3]}")
print("\nFIN")
