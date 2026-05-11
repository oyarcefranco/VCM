"""Fix Q01,Q15,Q16,Q17,Q18,Q19 en 2024-2025 — one-hot binario con etiquetas en R2"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
import pandas as pd, numpy as np, os, re

BASE = r"c:\Users\oyarc\OneDrive - Universidad San Sebastian\VCM\Encuestas Estudiantes\RV_ BASE ENCUESTA ESTUDIANTES 2021-2025"
OUT = r"c:\Users\oyarc\OneDrive - Universidad San Sebastian\VCM\Encuestas Estudiantes"
df = pd.read_csv(os.path.join(OUT, "base_unificada_homologada.csv"), encoding='utf-8-sig')

m = {'muy significativo':5,'significativo':4,'medianamente significativo':3,'poco significativo':2,'nada significativo':1,
     'muy positivo':5,'positivo':4,'neutro (no impactó)':3,'negativo':2,'muy negativo':1,
     'muy importante':5,'importante':4,'medianamente importante':3,'poco importante':2,'nada importante':1,
     'totalmente':5,'casi totalmente':4,'medianamente':3,'sólo en parte':2,'no las cumplió':1,
     'superó mis expectativas':5,'en gran medida':3,
     'sí':1,'no':0}

def extract_onehot_labeled(data, raw, r2_row, col_start, n_options):
    """Extrae de n_options columnas one-hot donde R2 tiene la etiqueta"""
    n = len(data)
    labels = []
    for off in range(n_options):
        ci = col_start + off
        label = str(raw.iloc[r2_row, ci]).strip() if pd.notna(raw.iloc[r2_row, ci]) else None
        if label and label != 'nan' and label != 'None':
            labels.append((ci, label))
    
    result = [np.nan]*n
    for i in range(n):
        for ci, label in labels:
            v = data.iloc[i, ci]
            if pd.notna(v) and str(v).strip() == '1':
                lk = re.sub(r'\s+', ' ', label).strip().lower().rstrip('.')
                mapped = m.get(lk)
                if mapped is not None:
                    result[i] = float(mapped)
                break
    return result

for year, fname, sheet in [(2024,"BASE ENCUESTA ESTUDIANTES 2024.xlsx","Reporte"),
                            (2025,"BASE ENCUESTA ESTUDIANTES 2025.xlsx","Reporte")]:
    raw = pd.read_excel(os.path.join(BASE, fname), sheet_name=sheet, header=None)
    data = raw.iloc[4:].reset_index(drop=True)
    n = len(data)
    mask = df['Año']==year
    
    print(f"\n{'='*50}\n  {year}\n{'='*50}")
    
    # Q01: cols 10-14
    vals = extract_onehot_labeled(data, raw, 2, 10, 5)
    nn = sum(1 for v in vals if v is not None)
    df.loc[mask, 'Q01_Significancia_Formacion'] = vals
    print(f"  Q01: n={nn}, media={np.nanmean([v for v in vals if v]):.2f}")
    
    # Q15: Importancia beneficiados
    if year == 2024:
        vals = extract_onehot_labeled(data, raw, 2, 140, 5)
    else:  # 2025
        vals = extract_onehot_labeled(data, raw, 2, 116, 5)
    nn = sum(1 for v in vals if v is not None)
    df.loc[mask, 'Q15_Importancia_Beneficiados'] = vals
    print(f"  Q15: n={nn}, media={np.nanmean([v for v in vals if v]):.2f}")
    
    # Q16: Conocer campo laboral (Sí/No)
    if year == 2024:
        vals = extract_onehot_labeled(data, raw, 2, 115, 2)
    else:  # 2025 — NO tiene esta pregunta
        vals = [np.nan]*n
    nn = sum(1 for v in vals if v is not None)
    df.loc[mask, 'Q16_Conocer_Campo_Laboral'] = vals
    print(f"  Q16: n={nn}")
    
    # Q17: Expectativas
    if year == 2024:
        vals = extract_onehot_labeled(data, raw, 2, 151, 5)
    else:  # 2025
        vals = extract_onehot_labeled(data, raw, 2, 123, 5)
    nn = sum(1 for v in vals if v is not None)
    df.loc[mask, 'Q17_Cumplimiento_Expectativas'] = vals
    print(f"  Q17: n={nn}, media={np.nanmean([v for v in vals if v]):.2f}")
    
    # Q18: Recomendaría (Sí/No)
    if year == 2024:
        vals = extract_onehot_labeled(data, raw, 2, 156, 2)
    else:  # 2025
        vals = extract_onehot_labeled(data, raw, 2, 129, 2)
    nn = sum(1 for v in vals if v is not None)
    df.loc[mask, 'Q18_Recomendaria'] = vals
    print(f"  Q18: n={nn}")
    
    # Q19: VcM (Sí/No)
    if year == 2024:
        vals = extract_onehot_labeled(data, raw, 2, 145, 2)
    else:  # 2025
        vals = extract_onehot_labeled(data, raw, 2, 121, 2)
    nn = sum(1 for v in vals if v is not None)
    df.loc[mask, 'Q19_Vinculacion_Medio'] = vals
    print(f"  Q19: n={nn}")

# Verificación
print(f"\n{'='*50}\n  VERIFICACIÓN FINAL\n{'='*50}")
num_cols = [c for c in df.columns if c.startswith('Q') and c != 'Q14_Valores_Sebastianos']
for y in [2021,2022,2023,2024,2025]:
    sub = df[df['Año']==y]
    print(f"\n── {y} ({len(sub)}) ──")
    for c in num_cols:
        vals = sub[c].dropna()
        if len(vals) > 0:
            print(f"  {c}: n={len(vals)}, media={vals.mean():.2f}")

df.to_csv(os.path.join(OUT, "base_unificada_homologada.csv"), index=False, encoding='utf-8-sig')
print(f"\n✅ Base actualizada: {df.shape}")
print("FIN.")
