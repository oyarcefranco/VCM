"""Debug: estructura exacta de Q01,Q15,Q16,Q17,Q18,Q19 en 2024-2025"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
import pandas as pd, os

BASE = r"c:\Users\oyarc\OneDrive - Universidad San Sebastian\VCM\Encuestas Estudiantes\RV_ BASE ENCUESTA ESTUDIANTES 2021-2025"

for year, fname, sheet in [(2024,"BASE ENCUESTA ESTUDIANTES 2024.xlsx","Reporte"),
                            (2025,"BASE ENCUESTA ESTUDIANTES 2025.xlsx","Reporte")]:
    raw = pd.read_excel(os.path.join(BASE, fname), sheet_name=sheet, header=None)
    r0, r1, r2 = raw.iloc[0], raw.iloc[1], raw.iloc[2]
    data = raw.iloc[4:]
    print(f"\n{'='*60}\n  {year}\n{'='*60}")
    
    targets = ['significativ','impacto','percepción','conocer','campo laboral',
               'cumplió','expectativas','recomendarías','vinculación']
    
    curr = None
    for i in range(raw.shape[1]):
        p = str(r0.iloc[i]).strip() if pd.notna(r0.iloc[i]) else None
        a1 = str(r1.iloc[i]).strip() if pd.notna(r1.iloc[i]) else 'None'
        a2 = str(r2.iloc[i]).strip() if pd.notna(r2.iloc[i]) else 'None'
        if p and p != 'nan': curr = p
        if not curr: continue
        cl = curr.lower()
        if any(t in cl for t in targets):
            # Mostrar r0, r1, r2 y primeros datos
            sample_vals = [str(data.iloc[j,i]) for j in range(min(3,len(data)))]
            print(f"  Col {i}: R0='{curr[:50]}' R1='{a1[:30]}' R2='{a2[:30]}' datos={sample_vals}")

print("\nFIN")
