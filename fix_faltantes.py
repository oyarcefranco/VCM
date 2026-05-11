"""Fix preguntas faltantes en 2024-2025: Q01,Q14,Q15,Q17,Q18,Q19"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
import pandas as pd, numpy as np, os, re

BASE = r"c:\Users\oyarc\OneDrive - Universidad San Sebastian\VCM\Encuestas Estudiantes\RV_ BASE ENCUESTA ESTUDIANTES 2021-2025"
OUT = r"c:\Users\oyarc\OneDrive - Universidad San Sebastian\VCM\Encuestas Estudiantes"
df = pd.read_csv(os.path.join(OUT, "base_unificada_homologada.csv"), encoding='utf-8-sig')

def parse_cell(val):
    if pd.isna(val): return None
    s = re.sub(r'\s+', ' ', str(val)).strip()
    if s in ('Sin información','nan','None',''): return None
    s = re.sub(r'\[\d+\]', '', s).strip()
    m = {'muy importante':5,'importante':4,'medianamente importante':3,'poco importante':2,'nada importante':1,
         'muy significativo':5,'significativo':4,'medianamente significativo':3,'poco significativo':2,'nada significativo':1,
         'muy positivo':5,'positivo':4,'neutro (no impactó)':3,'negativo':2,'muy negativo':1,
         'totalmente':5,'casi totalmente':4,'medianamente':3,'sólo en parte':2,'no las cumplió':1,
         'superó mis expectativas':5,'en gran medida':3,
         'sí':1,'no':0,'si':1}
    return m.get(s.lower(), s)

for year, fname, sheet in [(2024,"BASE ENCUESTA ESTUDIANTES 2024.xlsx","Reporte"),
                            (2025,"BASE ENCUESTA ESTUDIANTES 2025.xlsx","Reporte")]:
    raw = pd.read_excel(os.path.join(BASE, fname), sheet_name=sheet, header=None)
    r0, r2 = raw.iloc[0], raw.iloc[2]
    data = raw.iloc[4:].reset_index(drop=True)
    n = len(data)
    mask = df['Año']==year
    
    print(f"\n{'='*50}\n  {year} — Preguntas faltantes\n{'='*50}")
    
    # Scan ALL columns for missing questions
    curr = None
    for i in range(raw.shape[1]):
        p = str(r0.iloc[i]).strip() if pd.notna(r0.iloc[i]) else None
        a = str(r2.iloc[i]).strip() if pd.notna(r2.iloc[i]) else None
        if p and p != 'nan': curr = p
        if not curr: continue
        cl = curr.lower()
        
        # Q01: Significancia/impacto formación
        if ('significativo' in cl and 'formación' in cl) or ('impacto' in cl and 'formación' in cl):
            if a and a != 'nan' and a not in ('None',):
                al = a.lower().strip().rstrip('.')
                if al in ('muy significativo','significativo','medianamente significativo','poco significativo','nada significativo',
                          'muy positivo','positivo','neutro (no impactó)','negativo','muy negativo'):
                    vals = [parse_cell(data.iloc[j,i]) for j in range(n)]
                    nn = sum(1 for v in vals if v is not None and isinstance(v,(int,float)))
                    if nn > 100:
                        df.loc[mask, 'Q01_Significancia_Formacion'] = vals
                        print(f"  Q01: col {i}, alt='{a}', n={nn}")
                        break
        
        # Q15: Importancia beneficiados
        if 'percepción' in cl and ('importancia' in cl or 'nivel' in cl) and ('personas' in cl or 'comunid' in cl):
            if a and 'muy importante' in a.lower():
                vals = [parse_cell(data.iloc[j,i]) for j in range(n)]
                nn = sum(1 for v in vals if v is not None and isinstance(v,(int,float)))
                if nn > 100:
                    df.loc[mask, 'Q15_Importancia_Beneficiados'] = vals
                    print(f"  Q15: col {i}, n={nn}")
                    break
        
        # Q19: Vinculación medio  
        if 'vinculación con el medio' in cl:
            if a and ('sí' in a.lower() or 'no' in a.lower()):
                vals = [parse_cell(data.iloc[j,i]) for j in range(n)]
                nn = sum(1 for v in vals if v is not None and isinstance(v,(int,float)))
                if nn > 100:
                    df.loc[mask, 'Q19_Vinculacion_Medio'] = vals
                    print(f"  Q19: col {i}, n={nn}")
                    break
        
        # Q17: Expectativas
        if 'cumplió' in cl and 'expectativas' in cl:
            if a and a != 'nan' and a != 'None':
                al = a.lower().strip().rstrip('.')
                if al in ('totalmente','casi totalmente','medianamente','sólo en parte','no las cumplió',
                          'superó mis expectativas','en gran medida'):
                    vals = [parse_cell(data.iloc[j,i]) for j in range(n)]
                    nn = sum(1 for v in vals if v is not None and isinstance(v,(int,float)))
                    if nn > 100:
                        df.loc[mask, 'Q17_Cumplimiento_Expectativas'] = vals
                        print(f"  Q17: col {i}, alt='{a}', n={nn}")
                        break
        
        # Q18: Recomendaría
        if 'recomendarías' in cl:
            if a and ('sí' in a.lower() or 'no' in a.lower()):
                vals = [parse_cell(data.iloc[j,i]) for j in range(n)]
                nn = sum(1 for v in vals if v is not None and isinstance(v,(int,float)))
                if nn > 100:
                    df.loc[mask, 'Q18_Recomendaria'] = vals
                    print(f"  Q18: col {i}, n={nn}")
                    break

    # Q14: Valores sebastianos — one-hot especial
    curr = None
    vals_cols = []
    for i in range(raw.shape[1]):
        p = str(r0.iloc[i]).strip() if pd.notna(r0.iloc[i]) else None
        a = str(r2.iloc[i]).strip() if pd.notna(r2.iloc[i]) else None
        if p and p != 'nan': curr = p
        if not curr: continue
        if 'valores sebastianos' in curr.lower() and ('cuáles' in curr.lower() or 'perspectiva' in curr.lower()):
            if a and a != 'nan' and a != 'None':
                vals_cols.append((i, a))
    
    if vals_cols:
        q14 = [None]*n
        for j in range(n):
            selected = []
            for ci, at in vals_cols:
                v = data.iloc[j, ci]
                if pd.notna(v) and str(v).strip() not in ('0','Sin información','nan',''):
                    if str(v).strip() == '1':
                        selected.append(at)
                    elif not str(v).strip().isdigit():
                        selected.append(str(v).strip())
            if selected:
                q14[j] = ' | '.join(selected)
        nn = sum(1 for v in q14 if v)
        df.loc[mask, 'Q14_Valores_Sebastianos'] = q14
        print(f"  Q14: {len(vals_cols)} alt cols, n={nn}")

# También fix 2021-2022 Q14 con mismo enfoque
for year, fname, sheet in [(2021,"Encuesta estudiantes 2021 Reporte.xlsx","Base de datos"),
                            (2022,"Encuesta estudiantes 2022 Reporte.xlsx","Base de datos")]:
    raw = pd.read_excel(os.path.join(BASE, fname), sheet_name=sheet, header=None)
    r1, r2, r3 = raw.iloc[1], raw.iloc[2], raw.iloc[3]
    data = raw.iloc[4:].reset_index(drop=True)
    n = len(data)
    mask = df['Año']==year
    
    curr = None; vals_cols = []
    for i in range(raw.shape[1]):
        sec = str(r1.iloc[i]).strip() if pd.notna(r1.iloc[i]) else None
        alt = str(r2.iloc[i]).strip() if pd.notna(r2.iloc[i]) else None
        if sec and sec != 'nan': curr = sec
        if not curr: continue
        if 'valores sebastianos' in curr.lower() and ('seleccione' in curr.lower()):
            if alt and alt != 'nan':
                vals_cols.append((i, alt))
    
    if vals_cols:
        q14 = [None]*n
        for j in range(n):
            selected = []
            for ci, at in vals_cols:
                v = data.iloc[j, ci]
                if pd.notna(v) and str(v).strip() not in ('0','Sin información','nan',''):
                    if str(v).strip() == '1': selected.append(at)
                    elif not str(v).strip().isdigit(): selected.append(str(v).strip())
            if selected: q14[j] = ' | '.join(selected)
        nn = sum(1 for v in q14 if v)
        df.loc[mask, 'Q14_Valores_Sebastianos'] = q14
        print(f"\n  {year} Q14: {len(vals_cols)} alt cols, n={nn}")

# Also fix 2023 Q01, Q15, Q17, Q18 — these are single-column Likert
year = 2023
raw = pd.read_excel(os.path.join(BASE,"Encuesta estudiantes 2023 Reporte.xlsx"), 
                    sheet_name="Base de datos encuestas ajuste", header=None)
r0 = raw.iloc[0]; data = raw.iloc[5:].reset_index(drop=True); n=len(data); mask=df['Año']==2023
curr = None
for i in range(raw.shape[1]):
    p = str(r0.iloc[i]).strip() if pd.notna(r0.iloc[i]) else None
    if p and p != 'nan': curr = p
    if not curr: continue
    cl = curr.lower()
    if 'significativo' in cl and 'formación' in cl:
        vals = [parse_cell(data.iloc[j,i]) for j in range(n)]
        nn = sum(1 for v in vals if v is not None and isinstance(v,(int,float)))
        if nn > 100:
            df.loc[mask, 'Q01_Significancia_Formacion'] = vals
            print(f"\n  2023 Q01: col {i}, n={nn}"); break
for i in range(raw.shape[1]):
    p = str(r0.iloc[i]).strip() if pd.notna(r0.iloc[i]) else None
    if p and p != 'nan': curr = p
    if not curr: continue
    cl = curr.lower()
    if 'percepción' in cl and 'nivel' in cl and 'importancia' in cl:
        vals = [parse_cell(data.iloc[j,i]) for j in range(n)]
        nn = sum(1 for v in vals if v is not None and isinstance(v,(int,float)))
        if nn > 100:
            df.loc[mask, 'Q15_Importancia_Beneficiados'] = vals
            print(f"  2023 Q15: col {i}, n={nn}"); break
for i in range(raw.shape[1]):
    p = str(r0.iloc[i]).strip() if pd.notna(r0.iloc[i]) else None
    if p and p != 'nan': curr = p
    if not curr: continue
    cl = curr.lower()
    if 'cumplió' in cl and 'expectativas' in cl:
        vals = [parse_cell(data.iloc[j,i]) for j in range(n)]
        nn = sum(1 for v in vals if v is not None and isinstance(v,(int,float)))
        if nn > 100:
            df.loc[mask, 'Q17_Cumplimiento_Expectativas'] = vals
            print(f"  2023 Q17: col {i}, n={nn}"); break
for i in range(raw.shape[1]):
    p = str(r0.iloc[i]).strip() if pd.notna(r0.iloc[i]) else None
    if p and p != 'nan': curr = p
    if not curr: continue
    cl = curr.lower()
    if 'recomendarías' in cl:
        vals = [parse_cell(data.iloc[j,i]) for j in range(n)]
        nn = sum(1 for v in vals if v is not None and isinstance(v,(int,float)))
        if nn > 100:
            df.loc[mask, 'Q18_Recomendaria'] = vals
            print(f"  2023 Q18: col {i}, n={nn}"); break

# Verificación final
print(f"\n{'='*60}\n  COBERTURA FINAL\n{'='*60}")
qcols = [c for c in df.columns if c.startswith('Q')]
for year in [2021,2022,2023,2024,2025]:
    sub = df[df['Año']==year]
    print(f"\n── {year} ({len(sub)}) ──")
    for qc in qcols:
        vals = sub[qc].dropna()
        if len(vals) > 10:
            try:
                print(f"  {qc}: n={len(vals)}, media={pd.to_numeric(vals,errors='coerce').mean():.2f}")
            except:
                print(f"  {qc}: n={len(vals)} (texto)")

df.to_csv(os.path.join(OUT, "base_unificada_homologada.csv"), index=False, encoding='utf-8-sig')
print(f"\n✅ Base actualizada: {df.shape}")
print("FIN.")
