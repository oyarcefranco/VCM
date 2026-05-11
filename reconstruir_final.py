"""
RECONSTRUCCIÓN FINAL — Los datos 2024-2025 son Likert en 5 columnas por alternativa
Cada alternativa tiene 5 sub-columnas one-hot: la respuesta seleccionada aparece como texto
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
import pandas as pd, numpy as np, os, re

BASE = r"c:\Users\oyarc\OneDrive - Universidad San Sebastian\VCM\Encuestas Estudiantes\RV_ BASE ENCUESTA ESTUDIANTES 2021-2025"
OUT = r"c:\Users\oyarc\OneDrive - Universidad San Sebastian\VCM\Encuestas Estudiantes"

def load_raw(fp, sheet): return pd.read_excel(fp, sheet_name=sheet, header=None)

# Mapeo de textos Likert → numérico (limpia saltos de línea y códigos)
def parse_likert_cell(val):
    if pd.isna(val): return None
    s = str(val).strip()
    if s in ('Sin información','nan','None',''): return None
    s = re.sub(r'\s+', ' ', s)  # colapsar whitespace
    s = re.sub(r'\[\d+\]', '', s).strip()  # quitar [4], [5] etc
    m = {
        'muy importante':5,'importante':4,'medianamente importante':3,
        'poco importante':2,'nada importante':1,
        'muy fortalecida':5,'se fortalece':4,'medianamente fortalecida':3,
        'poco fortalecida':2,'no se fortalece':1,
        'muy significativo':5,'significativo':4,'medianamente significativo':3,
        'poco significativo':2,'nada significativo':1,
        'muy positivo':5,'positivo':4,'neutro (no impactó)':3,'negativo':2,'muy negativo':1,
        'totalmente':5,'casi totalmente':4,'medianamente':3,'sólo en parte':2,'no las cumplió':1,
        'superó mis expectativas':5,'en gran medida':3,
        'muy de acuerdo':5,'de acuerdo':4,'ni de acuerdo ni en desacuerdo':3,
        'en desacuerdo':2,'muy en desacuerdo':1,
        'sí':1,'no':0,'si':1,
    }
    return m.get(s.lower(), None)

def extract_likert_multicolumn(data, col_start, n_subcols=5):
    """De 5 columnas, extrae el valor Likert (la celda no-vacía)."""
    n = len(data)
    result = [None]*n
    for i in range(n):
        for offset in range(n_subcols):
            ci = col_start + offset
            if ci < data.shape[1]:
                v = parse_likert_cell(data.iloc[i, ci])
                if v is not None:
                    result[i] = v
                    break
    return result

# ════════════════════════════════════════════════════════════
# Cargar y procesar cada año
# ════════════════════════════════════════════════════════════
archivos = {
    2021: ("Encuesta estudiantes 2021 Reporte.xlsx", "Base de datos"),
    2022: ("Encuesta estudiantes 2022 Reporte.xlsx", "Base de datos"),
    2023: ("Encuesta estudiantes 2023 Reporte.xlsx", "Base de datos encuestas ajuste"),
    2024: ("BASE ENCUESTA ESTUDIANTES 2024.xlsx", "Reporte"),
    2025: ("BASE ENCUESTA ESTUDIANTES 2025.xlsx", "Reporte"),
}

frames = []
for year, (fname, sheet) in archivos.items():
    fp = os.path.join(BASE, fname)
    raw = load_raw(fp, sheet)
    
    # Determinar filas de header y datos
    if year in (2021,2022):
        r_preg, r_alt, data_start = 1, 2, 4
        r_code = 3
    elif year == 2023:
        r_preg, r_alt, data_start = 0, 3, 5
        r_code = 4
    else:  # 2024, 2025
        r_preg, r_alt, data_start = 0, 2, 4
        r_code = None
    
    data = raw.iloc[data_start:].reset_index(drop=True)
    n = len(data)
    print(f"\n{'='*60}\n  {year}: {n} filas\n{'='*60}")
    
    # Construir mapa de preguntas → columnas
    curr_preg = None
    preg_blocks = []  # [(pregunta, col_start, alternativa_name), ...]
    
    for i in range(raw.shape[1]):
        preg = str(raw.iloc[r_preg, i]).strip() if pd.notna(raw.iloc[r_preg, i]) else None
        alt = str(raw.iloc[r_alt, i]).strip() if pd.notna(raw.iloc[r_alt, i]) else None
        
        if preg and preg != 'nan': curr_preg = preg
        if not curr_preg: continue
        
        # Skip metadata
        cl = curr_preg.lower()
        if any(x in cl for x in ['rut','nombre','key','sede','facultad','carrera','proyecto',
               'correo','tipo iniciativa','id aplica','columna1','informaci']):
            if alt and alt != 'nan' and 'respuesta' not in alt.lower():
                pass  # might be data
            else:
                continue
        
        if alt and alt != 'nan' and alt != 'Respuesta':
            preg_blocks.append((curr_preg, i, alt))
    
    # Identificar metadata columns
    meta_cols = {}
    for i in range(raw.shape[1]):
        if r_code is not None:
            code = str(raw.iloc[r_code, i]).strip() if pd.notna(raw.iloc[r_code, i]) else ''
        else:
            code = str(raw.iloc[r_preg, i]).strip() if pd.notna(raw.iloc[r_preg, i]) else ''
        
        cl = code.lower()
        if 'sede' in cl and 'SEDE' not in meta_cols: meta_cols['SEDE'] = i
        elif 'facul' in cl and 'FACULTAD' not in meta_cols: meta_cols['FACULTAD'] = i
        elif 'carrera' in cl and 'CARRERA' not in meta_cols: meta_cols['CARRERA'] = i
    
    row = {'Año': [year]*n}
    for mk in ['SEDE','FACULTAD','CARRERA']:
        if mk in meta_cols:
            row[mk] = [str(data.iloc[i, meta_cols[mk]]).strip() 
                       if pd.notna(data.iloc[i, meta_cols[mk]]) else None for i in range(n)]
        else:
            row[mk] = [None]*n
    
    # Número de sub-columnas por alternativa: 2024-2025 usa 5, otros usa 1
    n_sub = 5 if year in (2024, 2025) else 1
    
    # ── Mapear cada pregunta canónica ──
    q_map = {}  # canonical_name → list of values
    
    for preg_text, col_i, alt_text in preg_blocks:
        pl = preg_text.lower()
        al = alt_text.lower().strip().rstrip('.')
        target = None
        
        # Q01: Significancia
        if 'significativo' in pl and 'formación' in pl:
            target = 'Q01_Significancia_Formacion'
        elif 'impacto' in pl and 'formación' in pl:
            target = 'Q01_Significancia_Formacion'
        # Q02-Q05: Importancia aspectos
        elif ('importante' in pl or 'importancia' in pl) and ('logro' in pl or 'aspectos' in pl):
            if 'aplicar' in al: target = 'Q02_Importancia_Aspectos_Aplicar'
            elif 'realidad' in al or 'conecta' in al: target = 'Q03_Importancia_Aspectos_Realidad'
            elif 'vocación' in al or 'vocacion' in al: target = 'Q04_Importancia_Aspectos_Vocacion'
            elif 'valores sebastianos' in al: target = 'Q05_Importancia_Aspectos_Valores'
        # Q06-Q13: Habilidades
        elif 'fortalecidas' in pl or 'fortalecimiento' in pl:
            if 'empatía' in al or 'empatia' in al: target = 'Q06_Habilidad_Empatia'
            elif 'comunicación' in al or 'comunicacion' in al: target = 'Q07_Habilidad_Comunicacion'
            elif 'colaboración' in al or 'colaboracion' in al or 'trabajo en equipo' in al: target = 'Q08_Habilidad_Colaboracion'
            elif 'resolución de problemas' in al or 'resolucion de problemas' in al: target = 'Q09_Habilidad_Resolucion'
            elif 'adaptación' in al or 'adaptacion' in al: target = 'Q10_Habilidad_Adaptacion'
            elif 'competencia disciplinar' in al: target = 'Q11_Habilidad_Competencia'
            elif 'prolijidad' in al: target = 'Q12_Habilidad_Prolijidad'
            elif 'manejo de información' in al or 'manejo de informacion' in al: target = 'Q13_Habilidad_Manejo_Info'
        # Q15: Beneficiados
        elif 'percepción' in pl and ('importancia' in pl or 'nivel' in pl):
            target = 'Q15_Importancia_Beneficiados'
        # Q16: Campo laboral
        elif 'conocer' in pl and 'campo laboral' in pl:
            target = 'Q16_Conocer_Campo_Laboral'
        # Q17: Expectativas
        elif 'cumplió' in pl and 'expectativas' in pl:
            target = 'Q17_Cumplimiento_Expectativas'
        # Q18: Recomendaría
        elif 'recomendarías' in pl and 'compañeros' in pl:
            target = 'Q18_Recomendaria'
        # Q19: VcM
        elif 'vinculación con el medio' in pl:
            target = 'Q19_Vinculacion_Medio'
        # Q14: Valores
        elif 'valores sebastianos' in pl and ('seleccione' in pl or 'cuáles' in pl or 'perspectiva' in pl):
            target = 'Q14_Valores_Sebastianos'
        
        if target and target not in q_map:
            if n_sub > 1:
                q_map[target] = extract_likert_multicolumn(data, col_i, n_sub)
            else:
                q_map[target] = [parse_likert_cell(data.iloc[i, col_i]) for i in range(n)]
            
            nn = sum(1 for v in q_map[target] if v is not None)
            print(f"  {target}: col {col_i}, n={nn} ({nn/n*100:.1f}%)")
    
    # Q14: Valores — tratamiento especial (texto compuesto, no Likert)
    if 'Q14_Valores_Sebastianos' not in q_map:
        for preg_text, col_i, alt_text in preg_blocks:
            if 'valores sebastianos' in preg_text.lower() and ('seleccione' in preg_text.lower() or 'cuáles' in preg_text.lower() or 'perspectiva' in preg_text.lower()):
                # One-hot para valores: juntar todas las alternativas seleccionadas
                val_alts = [(ci, at) for pt, ci, at in preg_blocks if pt == preg_text]
                vals = [None]*n
                for i in range(n):
                    selected = []
                    for ci, at in val_alts:
                        v = data.iloc[i, ci]
                        if pd.notna(v) and str(v).strip() not in ('0','Sin información','nan',''):
                            if str(v).strip() == '1':
                                selected.append(at)
                            elif not str(v).strip().isdigit():
                                selected.append(str(v).strip())
                    if selected:
                        vals[i] = ' | '.join(selected)
                q_map['Q14_Valores_Sebastianos'] = vals
                nn = sum(1 for v in vals if v)
                print(f"  Q14_Valores_Sebastianos: {nn} ({nn/n*100:.1f}%)")
                break
    
    # Agregar todas las Q al row
    all_qs = ['Q01_Significancia_Formacion',
              'Q02_Importancia_Aspectos_Aplicar','Q03_Importancia_Aspectos_Realidad',
              'Q04_Importancia_Aspectos_Vocacion','Q05_Importancia_Aspectos_Valores',
              'Q06_Habilidad_Empatia','Q07_Habilidad_Comunicacion','Q08_Habilidad_Colaboracion',
              'Q09_Habilidad_Resolucion','Q10_Habilidad_Adaptacion','Q11_Habilidad_Competencia',
              'Q12_Habilidad_Prolijidad','Q13_Habilidad_Manejo_Info','Q14_Valores_Sebastianos',
              'Q15_Importancia_Beneficiados','Q16_Conocer_Campo_Laboral',
              'Q17_Cumplimiento_Expectativas','Q18_Recomendaria','Q19_Vinculacion_Medio']
    
    for qc in all_qs:
        row[qc] = q_map.get(qc, [None]*n)
        if len(row[qc]) != n:
            row[qc] = (row[qc] + [None]*n)[:n]
    
    frames.append(pd.DataFrame(row))

# ════════════════════════════════════════════════════════════
# CONCAT Y EXPORTAR
# ════════════════════════════════════════════════════════════
df = pd.concat(frames, ignore_index=True)

# Verificación
print(f"\n{'='*60}\n  BASE FINAL: {df.shape[0]:,} x {df.shape[1]}\n{'='*60}")
num_qs = [c for c in df.columns if c.startswith('Q') and c != 'Q14_Valores_Sebastianos']
for year in [2021,2022,2023,2024,2025]:
    sub = df[df['Año']==year]
    print(f"\n── {year} ({len(sub)}) ──")
    for qc in num_qs:
        vals = sub[qc].dropna()
        if len(vals) > 0:
            print(f"  {qc}: n={len(vals)}, media={vals.mean():.2f}, rango=[{vals.min():.0f}-{vals.max():.0f}]")

# Exportar
path = os.path.join(OUT, "base_unificada_homologada.csv")
df.to_csv(path, index=False, encoding='utf-8-sig')
print(f"\n✅ {path}")
print("FIN.")
