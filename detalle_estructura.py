"""Extraer detalle completo: Pregunta + todas sus alternativas, para cada año"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
import pandas as pd, os, re

BASE = r"c:\Users\oyarc\OneDrive - Universidad San Sebastian\VCM\Encuestas Estudiantes\RV_ BASE ENCUESTA ESTUDIANTES 2021-2025"

archivos = {
    2021: ("Encuesta estudiantes 2021 Reporte.xlsx", "Base de datos", 1, 2, 4),
    2022: ("Encuesta estudiantes 2022 Reporte.xlsx", "Base de datos", 1, 2, 4),
    2023: ("Encuesta estudiantes 2023 Reporte.xlsx", "Base de datos encuestas ajuste", 0, 3, 5),
    2024: ("BASE ENCUESTA ESTUDIANTES 2024.xlsx", "Reporte", 0, 2, 4),
    2025: ("BASE ENCUESTA ESTUDIANTES 2025.xlsx", "Reporte", 0, 2, 4),
}

for year, (fname, sheet, r_preg, r_alt, ds) in archivos.items():
    fp = os.path.join(BASE, fname)
    raw = pd.read_excel(fp, sheet_name=sheet, header=None)
    data = raw.iloc[ds:].reset_index(drop=True)
    n = len(data)
    
    print(f"\n{'#'*80}")
    print(f"#  AÑO {year}  ({n} encuestados, {raw.shape[1]} columnas)")
    print(f"{'#'*80}")
    
    curr_preg = ''
    preg_num = 0
    preg_alts = {}  # preg_num -> list of (col, alt_text)
    preg_texts = {}
    
    for i in range(raw.shape[1]):
        p = str(raw.iloc[r_preg, i]).strip() if pd.notna(raw.iloc[r_preg, i]) else ''
        a = str(raw.iloc[r_alt, i]).strip() if pd.notna(raw.iloc[r_alt, i]) else ''
        
        if p and p != 'nan' and p != curr_preg:
            curr_preg = p
            preg_num += 1
            preg_texts[preg_num] = curr_preg
            preg_alts[preg_num] = []
        
        if curr_preg and preg_num > 0:
            # Contar no-vacíos
            nn = sum(1 for j in range(n) if pd.notna(data.iloc[j,i]) and str(data.iloc[j,i]).strip() not in ('','nan','Sin información'))
            
            # Valores únicos (sample)
            vals = set()
            for j in range(min(n, 500)):
                v = data.iloc[j,i]
                if pd.notna(v) and str(v).strip() not in ('','nan','Sin información'):
                    vals.add(re.sub(r'\s+', ' ', str(v).strip()))
            
            alt_clean = re.sub(r'\s+', ' ', a) if a and a != 'nan' else ''
            preg_alts[preg_num].append((i, alt_clean, nn, sorted(vals)[:10]))
    
    # Imprimir
    for pn in sorted(preg_texts.keys()):
        pt = preg_texts[pn]
        alts = preg_alts[pn]
        
        # Skip metadata
        ptl = pt.lower()
        if any(x in ptl for x in ['rut','nombre','correo','tipo iniciativa','id aplica','id proyecto','columna1']):
            continue
        
        print(f"\n  P{pn}. {pt}")
        print(f"  {'─'*70}")
        
        for col, alt, nn, vals in alts:
            pct = f"{nn/n*100:.0f}%" if n > 0 else "0%"
            vals_str = str(vals[:6]) if vals else '[]'
            if alt:
                print(f"    Col {col:3d} | Alt: {alt[:55]:55s} | n={nn:5d} ({pct:>4s}) | Vals: {vals_str[:60]}")
            else:
                print(f"    Col {col:3d} | (sin alternativa)                                       | n={nn:5d} ({pct:>4s}) | Vals: {vals_str[:60]}")

print("\nFIN.")
