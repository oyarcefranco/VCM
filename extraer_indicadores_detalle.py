"""
Extrae distribuciones Likert y dicotómicas de los indicadores clave 
para insertar en dashboard_vcm_detalle.html (sección Indicadores Clave).
También extrae distribución Likert de Significancia para Dim5.
"""
import pandas as pd, json

f = 'base_homologada_final.xlsx'

# --- Likert indicators (1-5) ---
likert_sheets = {
    'Significancia en Formación': ('Significancia_Formacion', 'Q01_Significancia'),
    'Importancia para Beneficiados': ('Importancia_Beneficiados', 'Importancia_Beneficiados'),
    'Expectativas Cumplidas': ('Cumplimiento_Expectativas', 'Cumplimiento_Expectativas'),
}

results = []
for ind_name, (sheet, col) in likert_sheets.items():
    df = pd.read_excel(f, sheet_name=sheet)
    # Use Año column (may be 'Año' or 'A\u00f1o' due to encoding)
    year_col = [c for c in df.columns if 'o' in c.lower() and c.startswith('A')][0]
    for year in sorted(df[year_col].unique()):
        subset = df[df[year_col] == year][col].dropna()
        n = len(subset)
        if n == 0:
            continue
        dist = {}
        for level in [1, 2, 3, 4, 5]:
            dist[f'% {level}'] = round((subset == level).sum() / n, 6)
        t2b = dist['% 4'] + dist['% 5']
        results.append({
            'Año': int(year),
            'Indicador': ind_name,
            'N_Respuestas': n,
            'Resultado (%)': round(t2b, 6),
            **dist
        })

# --- Dichotomous indicators (0/1 → Sí/No) ---
dichot_sheets = {
    'Recomendaría a compañeros': ('Recomendaria', 'Recomendaria'),
    'Permitió conocer campo laboral': ('Campo_Laboral_SiNo', 'Campo_Laboral_SiNo'),
}

for ind_name, (sheet, col) in dichot_sheets.items():
    df = pd.read_excel(f, sheet_name=sheet)
    year_col = [c for c in df.columns if 'o' in c.lower() and c.startswith('A')][0]
    for year in sorted(df[year_col].unique()):
        subset = df[df[year_col] == year][col].dropna()
        n = len(subset)
        if n == 0:
            continue
        pct_si = round((subset == 1).sum() / n, 6)
        pct_no = round(1 - pct_si, 6)
        results.append({
            'Año': int(year),
            'Indicador': ind_name,
            'N_Respuestas': n,
            'Resultado (%)': pct_si,
            '% Sí': pct_si,
            '% No': pct_no
        })

# Sort by indicator then year
results.sort(key=lambda x: (x['Indicador'], x['Año']))

# Print summary
for r in results:
    likert_str = ''
    if '% 1' in r:
        likert_str = f"  1:{r['% 1']:.1%} 2:{r['% 2']:.1%} 3:{r['% 3']:.1%} 4:{r['% 4']:.1%} 5:{r['% 5']:.1%}"
    elif '% Sí' in r:
        likert_str = f"  Sí:{r['% Sí']:.1%} No:{r['% No']:.1%}"
    print(f"{r['Indicador']} {r['Año']}: n={r['N_Respuestas']} T2B/Sí={r['Resultado (%)']:.1%}{likert_str}")

# Output JSON
print("\n\n--- JSON ---")
print(json.dumps(results, ensure_ascii=False, indent=2))
