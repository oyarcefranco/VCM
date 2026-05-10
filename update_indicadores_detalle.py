"""
Updates dashboard_vcm_detalle.html to add Likert/dichotomous distribution data
to the indicadores array and adds N to valores.
"""
import pandas as pd, json, re

f = 'base_homologada_final.xlsx'

# --- Extract Likert distributions for indicators ---
likert_sheets = {
    'Significancia en Formación (T2B)': ('Significancia_Formacion', 'Q01_Significancia'),
    'Importancia para Beneficiados (T2B)': ('Importancia_Beneficiados', 'Importancia_Beneficiados'),
    'Expectativas Cumplidas (T2B)': ('Cumplimiento_Expectativas', 'Cumplimiento_Expectativas'),
}

new_ind = []
for ind_name, (sheet, col) in likert_sheets.items():
    df = pd.read_excel(f, sheet_name=sheet)
    year_col = [c for c in df.columns if c.startswith('A')][0]
    for year in sorted(df[year_col].unique()):
        subset = df[df[year_col] == year][col].dropna()
        n = len(subset)
        if n == 0: continue
        dist = {}
        for level in [1, 2, 3, 4, 5]:
            dist[f'% {level}'] = round((subset == level).sum() / n, 6)
        t2b = dist['% 4'] + dist['% 5']
        new_ind.append({
            'Año': int(year), 'Indicador': ind_name,
            'N_Respuestas': n, 'Resultado (%)': round(t2b, 6),
            'tipo': 'likert', **dist
        })

# Dichotomous
dichot_sheets = {
    'Recomendaría a compañeros (% Sí)': ('Recomendaria', 'Recomendaria'),
    'Permitió conocer campo laboral (% Sí)': ('Campo_Laboral_SiNo', 'Campo_Laboral_SiNo'),
}
for ind_name, (sheet, col) in dichot_sheets.items():
    df = pd.read_excel(f, sheet_name=sheet)
    year_col = [c for c in df.columns if c.startswith('A')][0]
    for year in sorted(df[year_col].unique()):
        subset = df[df[year_col] == year][col].dropna()
        n = len(subset)
        if n == 0: continue
        pct_si = round((subset == 1).sum() / n, 6)
        new_ind.append({
            'Año': int(year), 'Indicador': ind_name,
            'N_Respuestas': n, 'Resultado (%)': pct_si,
            'tipo': 'dicotomica', '% Sí': pct_si, '% No': round(1 - pct_si, 6)
        })

# Also add other indicators that may exist (Sabía que era VcM)
# Read existing detalle HTML to get existing data
with open('dashboard_vcm_detalle.html', 'r', encoding='utf-8') as fh:
    content = fh.read()

start = content.find('DATA = {')
end = content.find('; init();', start)
data_str = content[start+7:end]
data = json.loads(data_str)

# Add Sabía que era VcM from existing data (keep as-is since no distribution)
for r in data['indicadores']:
    ind = r['Indicador']
    if ind not in [k for k in likert_sheets] + [k for k in dichot_sheets]:
        # Keep existing record, mark as dicotómica with calculated %No
        entry = dict(r)
        entry['tipo'] = 'dicotomica'
        entry['% Sí'] = r['Resultado (%)']
        entry['% No'] = round(1 - r['Resultado (%)'], 6)
        new_ind.append(entry)

# Sort
new_ind.sort(key=lambda x: (x['Indicador'], x['Año']))

# Replace indicadores in DATA
data['indicadores'] = new_ind

# Add N_Respuestas to valores (need to calculate from base)
# Valores are from base_homologada_final.xlsx, Valores_Sebastianos sheet
try:
    df_val = pd.read_excel(f, sheet_name='Valores_Sebastianos')
    year_col = [c for c in df_val.columns if c.startswith('A')][0]
    # Get total respondents per year (non-null in any value column)
    val_cols = [c for c in df_val.columns if c not in [year_col, 'RUT', 'SEDE', 'FACULTAD', 'CARRERA']]
    for r in data['valores']:
        year = r['Año']
        yr_data = df_val[df_val[year_col] == year]
        # N = total students who answered the valores question
        n_val = len(yr_data)
        r['N_Encuestados'] = n_val
except Exception as e:
    print(f'Warning: Could not add N to valores: {e}')

# Write back
new_data_str = json.dumps(data, ensure_ascii=False)
new_content = content[:start+7] + new_data_str + content[end:]

with open('dashboard_vcm_detalle.html', 'w', encoding='utf-8') as fh:
    fh.write(new_content)

print('Updated indicadores count:', len(new_ind))
print('Sample:', new_ind[0])
print('Tipos:', set(r['tipo'] for r in new_ind))
print('Done!')
