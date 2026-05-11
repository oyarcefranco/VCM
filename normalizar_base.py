"""
NORMALIZACIÓN FINAL — Convertir todas las respuestas a escala numérica uniforme
Versión 2: Usa .map() y .replace() para evitar problemas de dtype
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import pandas as pd
import numpy as np
import os

OUT = r"c:\Users\oyarc\OneDrive - Universidad San Sebastian\VCM\Encuestas Estudiantes"
df = pd.read_csv(os.path.join(OUT, "base_unificada_homologada.csv"), encoding='utf-8-sig',
                 dtype=str)  # Forzar todo como string
df['Año'] = df['Año'].astype(int)
print(f"Cargada: {df.shape}")

# ═══════════════════════════════════════════════════════════════
# MAPEOS DE NORMALIZACIÓN (texto → str numérico)
# ═══════════════════════════════════════════════════════════════

m_signif = {
    'Nada significativo': '1', 'Poco significativo': '2',
    'Medianamente significativo': '3', 'Significativo': '4',
    'Muy significativo': '5',
    '1.0':'1','2.0':'2','3.0':'3','4.0':'4','5.0':'5',
    '1':'1','2':'2','3':'3','4':'4','5':'5',
}

m_import = {
    'Nada Importante': '1', 'Poco Importante': '2',
    'Medianamente Importante': '3', 'Importante': '4',
    'Muy Importante': '5', 'No Responde': '',
    '0':'', '0.0':'',
    '1.0':'1','2.0':'2','3.0':'3','4.0':'4','5.0':'5',
    '1':'1','2':'2','3':'3','4':'4','5':'5',
}

m_habil = {
    'No se fortalece': '1', 'Poco Fortalecida': '2',
    'Medianamente fortalecida': '3', 'Se fortalece': '4',
    'Muy fortalecida': '5', 'No Responde': '',
    '0':'', '0.0':'',
    'Empatía, respeto y apertura a la diversidad': '',  # residual
    'Responsabilidad y prolijidad': '',  # residual
    '1.0':'1','2.0':'2','3.0':'3','4.0':'4','5.0':'5',
    '1':'1','2':'2','3':'3','4':'4','5':'5',
}

m_benef = {
    'Nada importante': '1', 'Poco importante': '2',
    'Medianamente importante': '3', 'Importante': '4',
    'Muy importante': '5',
    '1.0':'1','2.0':'2','3.0':'3','4.0':'4','5.0':'5',
    '1':'1','2':'2','3':'3','4':'4','5':'5',
}

m_campo = {
    'No': '0', 'Sí': '1',
    '0.0':'0','1.0':'1','0':'0','1':'1',
}

m_expect = {
    'Muy en desacuerdo': '1', 'En desacuerdo': '2',
    'Ni de acuerdo ni en desacuerdo': '3', 'De acuerdo': '4',
    'Muy de acuerdo': '5',
    '1.0':'1','2.0':'2','3.0':'3','4.0':'4','5.0':'5',
    '1':'1','2':'2','3':'3','4':'4','5':'5',
}

m_recom = {
    'No': '0', 'Sí': '1',
    '0.0':'0','1.0':'1','0':'0','1':'1',
}

m_vcm = {
    '0.0':'0','1.0':'1','0':'0','1':'1',
}

# Para Q02-Q13 en 2024-2025 son binarios, necesitamos tratarlos distinto
# En estos años, 0=no seleccionó, 1=seleccionó (one-hot)
# Conversión: para análisis longitudinal, convertir BINARIO a % top-2-box

def normalize_simple(series, mapeo):
    """Aplica mapeo de string a string, luego convierte a numérico."""
    clean = series.astype(str).str.strip()
    clean = clean.replace(mapeo)
    clean = clean.replace({'nan':'','None':'','':'', 'none':''})
    return pd.to_numeric(clean, errors='coerce')

# ═══════════════════════════════════════════════════════════════
# APLICAR NORMALIZACIÓN
# ═══════════════════════════════════════════════════════════════
print("\nNormalizando...")

# Q01: Significancia
df['Q01_Significancia_Formacion'] = normalize_simple(df['Q01_Significancia_Formacion'], m_signif)

# Q02-Q05: Importancia aspectos
# Años 2021-2023: Likert textual → 1-5
# Años 2024-2025: ya es binario 0/1 → mantener pero marcar
for qc in ['Q02_Importancia_Aspectos_Aplicar','Q03_Importancia_Aspectos_Realidad',
           'Q04_Importancia_Aspectos_Vocacion','Q05_Importancia_Aspectos_Valores']:
    df[qc] = normalize_simple(df[qc], m_import)

# Q06-Q13: Habilidades
for qc in ['Q06_Habilidad_Empatia','Q07_Habilidad_Comunicacion','Q08_Habilidad_Colaboracion',
           'Q09_Habilidad_Resolucion','Q10_Habilidad_Adaptacion','Q11_Habilidad_Competencia',
           'Q12_Habilidad_Prolijidad','Q13_Habilidad_Manejo_Info']:
    df[qc] = normalize_simple(df[qc], m_habil)

# Q14: Valores — dejar como texto
# (pero limpiar None y nan)
df['Q14_Valores_Sebastianos'] = df['Q14_Valores_Sebastianos'].replace({'nan':None,'None':None,'':None})

# Q15-Q19: Escalas simples
df['Q15_Importancia_Beneficiados'] = normalize_simple(df['Q15_Importancia_Beneficiados'], m_benef)
df['Q16_Conocer_Campo_Laboral'] = normalize_simple(df['Q16_Conocer_Campo_Laboral'], m_campo)
df['Q17_Cumplimiento_Expectativas'] = normalize_simple(df['Q17_Cumplimiento_Expectativas'], m_expect)
df['Q18_Recomendaria'] = normalize_simple(df['Q18_Recomendaria'], m_recom)
df['Q19_Vinculacion_Medio'] = normalize_simple(df['Q19_Vinculacion_Medio'], m_vcm)

# Agregar tipo de escala
df['Tipo_Escala_Q02Q13'] = df['Año'].map({
    2021: 'Likert_1a5', 2022: 'Likert_1a5', 2023: 'Likert_1a5',
    2024: 'Binario_0_1', 2025: 'Binario_0_1'
})

# ═══════════════════════════════════════════════════════════════
# CREAR % TOP-BOX PARA COMPARACIÓN LONGITUDINAL
# ═══════════════════════════════════════════════════════════════
# Para Q02-Q13: crear columnas "_TopBox" que sean comparables entre años
# Likert (2021-23): % de 4 y 5 → 1, resto → 0
# Binario (2024-25): mantener como está (1=seleccionado=favorable)

print("\nCreando indicadores Top-Box para comparación longitudinal...")

likert_cols = ['Q02_Importancia_Aspectos_Aplicar','Q03_Importancia_Aspectos_Realidad',
               'Q04_Importancia_Aspectos_Vocacion','Q05_Importancia_Aspectos_Valores',
               'Q06_Habilidad_Empatia','Q07_Habilidad_Comunicacion','Q08_Habilidad_Colaboracion',
               'Q09_Habilidad_Resolucion','Q10_Habilidad_Adaptacion','Q11_Habilidad_Competencia',
               'Q12_Habilidad_Prolijidad','Q13_Habilidad_Manejo_Info']

for qc in likert_cols:
    tb_col = qc + '_TopBox'
    df[tb_col] = np.nan
    
    # Años Likert: 4 o 5 → 1, 1-3 → 0
    mask_likert = df['Año'].isin([2021,2022,2023])
    df.loc[mask_likert, tb_col] = df.loc[mask_likert, qc].apply(
        lambda x: 1 if pd.notna(x) and x >= 4 else (0 if pd.notna(x) else np.nan))
    
    # Años binarios: copiar directo
    mask_bin = df['Año'].isin([2024,2025])
    df.loc[mask_bin, tb_col] = df.loc[mask_bin, qc]

# ═══════════════════════════════════════════════════════════════
# REPORTE FINAL
# ═══════════════════════════════════════════════════════════════
print("\n" + "="*80)
print("BASE FINAL NORMALIZADA")
print("="*80)
print(f"Dimensiones: {df.shape}")

pregs_num = ['Q01_Significancia_Formacion',
             'Q02_Importancia_Aspectos_Aplicar','Q03_Importancia_Aspectos_Realidad',
             'Q04_Importancia_Aspectos_Vocacion','Q05_Importancia_Aspectos_Valores',
             'Q06_Habilidad_Empatia','Q07_Habilidad_Comunicacion','Q08_Habilidad_Colaboracion',
             'Q09_Habilidad_Resolucion','Q10_Habilidad_Adaptacion','Q11_Habilidad_Competencia',
             'Q12_Habilidad_Prolijidad','Q13_Habilidad_Manejo_Info',
             'Q15_Importancia_Beneficiados','Q16_Conocer_Campo_Laboral',
             'Q17_Cumplimiento_Expectativas','Q18_Recomendaria','Q19_Vinculacion_Medio']

print("\n\nVALORES UNICOS POR PREGUNTA (post-normalización):")
for qc in pregs_num:
    vals = df[qc].dropna().unique()
    print(f"  {qc}: {sorted(vals)}")

print("\n\nCOBERTURA Y PROMEDIOS POR AÑO:")
for year in [2021,2022,2023,2024,2025]:
    sub = df[df['Año']==year]
    print(f"\n── {year} ({len(sub)} encuestados) ──")
    for qc in pregs_num:
        vals = sub[qc].dropna()
        if len(vals) > 0:
            print(f"  {qc}: n={len(vals):,}, media={vals.mean():.2f}")

# Top-Box comparables
print("\n\n% TOP-BOX POR AÑO (indicador comparable entre años):")
tb_cols = [c for c in df.columns if c.endswith('_TopBox')]
for year in [2021,2022,2023,2024,2025]:
    sub = df[df['Año']==year]
    print(f"\n── {year} ──")
    for qc in tb_cols:
        vals = sub[qc].dropna()
        if len(vals) > 0:
            pct = vals.mean()*100
            print(f"  {qc.replace('_TopBox','')}: {pct:.1f}% favorable (n={len(vals):,})")

# Exportar
path_final = os.path.join(OUT, "base_unificada_homologada.csv")
df.to_csv(path_final, index=False, encoding='utf-8-sig')
print(f"\n✅ Base final: {path_final}")
print(f"   {df.shape[0]:,} filas x {df.shape[1]} columnas")

# Diccionario
dict_rows = []
all_q = [c for c in df.columns if c.startswith('Q')]
escala_info = {
    'Q01_Significancia_Formacion': '1-5 (1=Nada significativo, 5=Muy significativo)',
    'Q02_Importancia_Aspectos_Aplicar': '1-5 Likert (2021-23) | 0/1 Binario (2024-25)',
    'Q03_Importancia_Aspectos_Realidad': '1-5 Likert (2021-23) | 0/1 Binario (2024-25)',
    'Q04_Importancia_Aspectos_Vocacion': '1-5 Likert (2021-23) | 0/1 Binario (2024-25)',
    'Q05_Importancia_Aspectos_Valores': '1-5 Likert (2021-23) | 0/1 Binario (2024-25)',
    'Q06_Habilidad_Empatia': '1-5 Likert (2021-23) | 0/1 Binario (2024-25)',
    'Q07_Habilidad_Comunicacion': '1-5 Likert (2021-23) | 0/1 Binario (2024-25)',
    'Q08_Habilidad_Colaboracion': '1-5 Likert (2021-23) | 0/1 Binario (2024-25)',
    'Q09_Habilidad_Resolucion': '1-5 Likert (2021-23) | 0/1 Binario (2024-25)',
    'Q10_Habilidad_Adaptacion': '1-5 Likert (2021-23) | 0/1 Binario (2024-25)',
    'Q11_Habilidad_Competencia': '1-5 Likert (2021-23) | 0/1 Binario (2024-25)',
    'Q12_Habilidad_Prolijidad': '1-5 Likert (2021-23) | 0/1 Binario (2024-25)',
    'Q13_Habilidad_Manejo_Info': '1-5 Likert (2021-23) | 0/1 Binario (2024-25)',
    'Q14_Valores_Sebastianos': 'Texto (valores seleccionados separados por |)',
    'Q15_Importancia_Beneficiados': '1-5 (1=Nada importante, 5=Muy importante)',
    'Q16_Conocer_Campo_Laboral': '0/1 (0=No, 1=Sí)',
    'Q17_Cumplimiento_Expectativas': '1-5 (1=No cumplió, 5=Totalmente)',
    'Q18_Recomendaria': '0/1 (0=No, 1=Sí)',
    'Q19_Vinculacion_Medio': '0/1 (0=No sabía, 1=Sí sabía)',
}

for qc in all_q:
    if qc.endswith('_TopBox'):
        continue
    años = [str(y) for y in [2021,2022,2023,2024,2025] if df[df['Año']==y][qc].notna().sum() > 0]
    dict_rows.append({
        'Variable': qc,
        'Escala': escala_info.get(qc, 'Ver TopBox para comparable'),
        'Años_Disponibles': ', '.join(años),
        'N_Respuestas': int(df[qc].notna().sum()) if qc != 'Q14_Valores_Sebastianos' else int(df[qc].notna().sum()),
        'Columna_TopBox': f'{qc}_TopBox' if f'{qc}_TopBox' in df.columns else 'N/A',
    })

df_dict = pd.DataFrame(dict_rows)
path_dict = os.path.join(OUT, "diccionario_base_unificada.csv")
df_dict.to_csv(path_dict, index=False, encoding='utf-8-sig')
print(f"✅ Diccionario: {path_dict}")

print("\nFIN.")
