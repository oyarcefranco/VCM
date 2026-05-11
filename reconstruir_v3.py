"""
RECONSTRUCCIÓN COMPLETA v3 — Un solo script para extraer todo correctamente
Estructura 2024-2025: 5 sub-columnas por alternativa (one-hot categórica)
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
import pandas as pd, numpy as np, os, re

BASE = r"c:\Users\oyarc\OneDrive - Universidad San Sebastian\VCM\Encuestas Estudiantes\RV_ BASE ENCUESTA ESTUDIANTES 2021-2025"
OUT = r"c:\Users\oyarc\OneDrive - Universidad San Sebastian\VCM\Encuestas Estudiantes"

def parse_cell(val):
    """Convierte un valor de celda a número Likert"""
    if pd.isna(val): return None
    s = re.sub(r'\s+', ' ', str(val)).strip()
    if s in ('Sin información','nan','None','','0','0.0'): return None
    s = re.sub(r'\[\d+\]', '', s).strip()
    m = {'muy importante':5,'importante':4,'medianamente importante':3,'poco importante':2,'nada importante':1,
         'muy fortalecida':5,'se fortalece':4,'medianamente fortalecida':3,'poco fortalecida':2,'no se fortalece':1,
         'muy significativo':5,'significativo':4,'medianamente significativo':3,'poco significativo':2,'nada significativo':1,
         'muy positivo':5,'positivo':4,'neutro (no impactó)':3,'negativo':2,'muy negativo':1,
         'totalmente':5,'casi totalmente':4,'medianamente':3,'sólo en parte':2,'no las cumplió':1,
         'superó mis expectativas':5,'en gran medida':3,
         'muy de acuerdo':5,'de acuerdo':4,'ni de acuerdo ni en desacuerdo':3,'en desacuerdo':2,'muy en desacuerdo':1,
         'sí':1,'no':0,'si':1}
    sl = s.lower().rstrip('.')
    if sl in m: return m[sl]
    try: return float(s)
    except: return None

def extract_5col(data, col_start, n_cols=5):
    """Extrae Likert de 5 sub-columnas (estructura 2024-2025)"""
    n = len(data)
    result = [None]*n
    for i in range(n):
        for off in range(n_cols):
            ci = col_start + off
            if ci < data.shape[1]:
                v = parse_cell(data.iloc[i, ci])
                if v is not None:
                    result[i] = v
                    break
    return result

archivos = {
    2021: ("Encuesta estudiantes 2021 Reporte.xlsx", "Base de datos"),
    2022: ("Encuesta estudiantes 2022 Reporte.xlsx", "Base de datos"),
    2023: ("Encuesta estudiantes 2023 Reporte.xlsx", "Base de datos encuestas ajuste"),
    2024: ("BASE ENCUESTA ESTUDIANTES 2024.xlsx", "Reporte"),
    2025: ("BASE ENCUESTA ESTUDIANTES 2025.xlsx", "Reporte"),
}

Q_KEYS = ['Q01','Q02','Q03','Q04','Q05','Q06','Q07','Q08','Q09','Q10','Q11','Q12','Q13','Q14','Q15','Q16','Q17','Q18','Q19']
Q_NAMES = {
    'Q01':'Q01_Significancia_Formacion','Q02':'Q02_Importancia_Aspectos_Aplicar',
    'Q03':'Q03_Importancia_Aspectos_Realidad','Q04':'Q04_Importancia_Aspectos_Vocacion',
    'Q05':'Q05_Importancia_Aspectos_Valores','Q06':'Q06_Habilidad_Empatia',
    'Q07':'Q07_Habilidad_Comunicacion','Q08':'Q08_Habilidad_Colaboracion',
    'Q09':'Q09_Habilidad_Resolucion','Q10':'Q10_Habilidad_Adaptacion',
    'Q11':'Q11_Habilidad_Competencia','Q12':'Q12_Habilidad_Prolijidad',
    'Q13':'Q13_Habilidad_Manejo_Info','Q14':'Q14_Valores_Sebastianos',
    'Q15':'Q15_Importancia_Beneficiados','Q16':'Q16_Conocer_Campo_Laboral',
    'Q17':'Q17_Cumplimiento_Expectativas','Q18':'Q18_Recomendaria','Q19':'Q19_Vinculacion_Medio',
}

def match_alt(alt_text, targets):
    """Match una alternativa a un Q-key basado en keywords"""
    al = alt_text.lower().strip().rstrip('.')
    for qk, keywords in targets.items():
        for kw in keywords:
            if kw in al:
                return qk
    return None

IMP_TARGETS = {
    'Q02': ['aplicar'],
    'Q03': ['realidad', 'conecta'],
    'Q04': ['vocación', 'vocacion'],
    'Q05': ['valores sebastianos'],
}

HAB_TARGETS = {
    'Q06': ['empatía', 'empatia'],
    'Q07': ['comunicación', 'comunicacion'],
    'Q08': ['colaboración', 'trabajo en equipo'],
    'Q09': ['resolución de problemas', 'resolucion de problemas'],
    'Q10': ['adaptación', 'adaptacion'],
    'Q11': ['competencia disciplinar'],
    'Q12': ['prolijidad'],
    'Q13': ['manejo de información', 'manejo de informacion'],
}

frames = []
for year, (fname, sheet) in archivos.items():
    fp = os.path.join(BASE, fname)
    raw = pd.read_excel(fp, sheet_name=sheet, header=None)
    
    if year in (2021,2022): r_preg,r_alt,ds = 1,2,4
    elif year == 2023: r_preg,r_alt,ds = 0,3,5
    else: r_preg,r_alt,ds = 0,2,4
    
    data = raw.iloc[ds:].reset_index(drop=True)
    n = len(data)
    n_sub = 5 if year in (2024,2025) else 1
    
    print(f"\n{'='*50}\n {year}: {n} filas\n{'='*50}")
    
    # Meta
    meta = {'SEDE':None,'FACULTAD':None,'CARRERA':None}
    for i in range(raw.shape[1]):
        for ri in range(min(5, raw.shape[0])):
            v = str(raw.iloc[ri,i]).strip().lower() if pd.notna(raw.iloc[ri,i]) else ''
            if 'sede' in v and 'proyecto' not in v and meta['SEDE'] is None: meta['SEDE'] = i
            elif ('facultad' in v) and meta['FACULTAD'] is None: meta['FACULTAD'] = i
            elif 'carrera' in v and meta['CARRERA'] is None: meta['CARRERA'] = i
    
    row = {'Año': [year]*n}
    for mk, ci in meta.items():
        if ci is not None:
            row[mk] = [str(data.iloc[i,ci]).strip() if pd.notna(data.iloc[i,ci]) else None for i in range(n)]
        else:
            row[mk] = [None]*n
    
    q_data = {k: [None]*n for k in Q_KEYS}
    
    # Scan columnas
    curr = None
    preg_alt_pairs = []  # (pregunta, col_idx, alternativa)
    for i in range(raw.shape[1]):
        p = str(raw.iloc[r_preg,i]).strip() if pd.notna(raw.iloc[r_preg,i]) else None
        a = str(raw.iloc[r_alt,i]).strip() if pd.notna(raw.iloc[r_alt,i]) else None
        if p and p != 'nan': curr = p
        if curr:
            preg_alt_pairs.append((curr, i, a if a and a != 'nan' else None))
    
    seen = set()
    for preg, ci, alt in preg_alt_pairs:
        pl = preg.lower()
        
        # Q01
        if ('significativo' in pl and 'formación' in pl) or ('impacto' in pl and 'formación' in pl):
            if 'Q01' not in seen and alt:
                vals = extract_5col(data, ci, n_sub) if n_sub > 1 else [parse_cell(data.iloc[i,ci]) for i in range(n)]
                nn = sum(1 for v in vals if v is not None)
                if nn > 50:
                    q_data['Q01'] = vals; seen.add('Q01')
                    print(f"  Q01: col {ci}, n={nn}")
        
        # Q02-Q05: Importancia aspectos
        elif ('importante' in pl or 'importancia' in pl) and ('logro' in pl or 'aspectos' in pl or 'experiencia' in pl):
            if alt:
                qk = match_alt(alt, IMP_TARGETS)
                if qk and qk not in seen:
                    vals = extract_5col(data, ci, n_sub) if n_sub > 1 else [parse_cell(data.iloc[i,ci]) for i in range(n)]
                    nn = sum(1 for v in vals if v is not None)
                    if nn > 50:
                        q_data[qk] = vals; seen.add(qk)
                        print(f"  {qk}: col {ci}, alt='{alt[:40]}', n={nn}")
        
        # Q06-Q13: Habilidades
        elif 'fortalecidas' in pl or 'fortalecimiento' in pl or 'fortalecida' in pl:
            if alt:
                qk = match_alt(alt, HAB_TARGETS)
                if qk and qk not in seen:
                    vals = extract_5col(data, ci, n_sub) if n_sub > 1 else [parse_cell(data.iloc[i,ci]) for i in range(n)]
                    nn = sum(1 for v in vals if v is not None)
                    if nn > 50:
                        q_data[qk] = vals; seen.add(qk)
                        print(f"  {qk}: col {ci}, alt='{alt[:40]}', n={nn}")
        
        # Q14: Valores sebastianos — colectar TODAS las alternativas one-hot
        elif 'valores sebastianos' in pl and ('seleccione' in pl or 'cuáles' in pl or 'perspectiva' in pl):
            pass  # Procesamos después
        
        # Q15
        elif 'percepción' in pl and ('importancia' in pl or 'nivel' in pl):
            if 'Q15' not in seen and alt:
                vals = extract_5col(data, ci, n_sub) if n_sub > 1 else [parse_cell(data.iloc[i,ci]) for i in range(n)]
                nn = sum(1 for v in vals if v is not None)
                if nn > 50:
                    q_data['Q15'] = vals; seen.add('Q15')
                    print(f"  Q15: col {ci}, n={nn}")
        
        # Q16
        elif 'conocer' in pl and 'campo laboral' in pl:
            if 'Q16' not in seen and alt:
                vals = extract_5col(data, ci, n_sub) if n_sub > 1 else [parse_cell(data.iloc[i,ci]) for i in range(n)]
                nn = sum(1 for v in vals if v is not None)
                if nn > 50:
                    q_data['Q16'] = vals; seen.add('Q16')
                    print(f"  Q16: col {ci}, n={nn}")
        
        # Q17
        elif 'cumplió' in pl and 'expectativas' in pl:
            if 'Q17' not in seen and alt:
                vals = extract_5col(data, ci, n_sub) if n_sub > 1 else [parse_cell(data.iloc[i,ci]) for i in range(n)]
                nn = sum(1 for v in vals if v is not None)
                if nn > 50:
                    q_data['Q17'] = vals; seen.add('Q17')
                    print(f"  Q17: col {ci}, n={nn}")
        
        # Q18
        elif 'recomendarías' in pl:
            if 'Q18' not in seen and alt:
                vals = extract_5col(data, ci, n_sub) if n_sub > 1 else [parse_cell(data.iloc[i,ci]) for i in range(n)]
                nn = sum(1 for v in vals if v is not None)
                if nn > 50:
                    q_data['Q18'] = vals; seen.add('Q18')
                    print(f"  Q18: col {ci}, n={nn}")
        
        # Q19
        elif 'vinculación con el medio' in pl:
            if 'Q19' not in seen and alt:
                vals = extract_5col(data, ci, n_sub) if n_sub > 1 else [parse_cell(data.iloc[i,ci]) for i in range(n)]
                nn = sum(1 for v in vals if v is not None)
                if nn > 50:
                    q_data['Q19'] = vals; seen.add('Q19')
                    print(f"  Q19: col {ci}, n={nn}")
    
    # Q14: Valores — one-hot a texto
    if 'Q14' not in seen:
        val_preg = None
        val_cols = []
        for preg, ci, alt in preg_alt_pairs:
            if 'valores sebastianos' in preg.lower() and ('seleccione' in preg.lower() or 'cuáles' in preg.lower() or 'perspectiva' in preg.lower()):
                val_preg = preg
                if alt: val_cols.append((ci, alt))
        
        if val_cols:
            q14 = []
            for i in range(n):
                selected = []
                for ci, at in val_cols:
                    v = data.iloc[i, ci]
                    if pd.notna(v) and str(v).strip() not in ('0','Sin información','nan','','0.0'):
                        if str(v).strip() == '1': selected.append(at.strip().rstrip('.'))
                        elif not str(v).strip().replace('.','').isdigit(): selected.append(str(v).strip())
                q14.append(' | '.join(selected) if selected else None)
            q_data['Q14'] = q14
            nn = sum(1 for v in q14 if v)
            print(f"  Q14: {len(val_cols)} alts, n={nn}")
    
    for qk in Q_KEYS:
        row[Q_NAMES[qk]] = q_data[qk]
    
    frames.append(pd.DataFrame(row))

df = pd.concat(frames, ignore_index=True)

# Reporte
print(f"\n{'='*60}\n BASE: {df.shape[0]:,} x {df.shape[1]}\n{'='*60}")
num_cols = [Q_NAMES[k] for k in Q_KEYS if k != 'Q14']
for y in [2021,2022,2023,2024,2025]:
    sub = df[df['Año']==y]
    print(f"\n── {y} ({len(sub)}) ──")
    for c in num_cols:
        vals = sub[c].dropna()
        if len(vals) > 0:
            print(f"  {c}: n={len(vals)}, media={vals.mean():.2f}")

df.to_csv(os.path.join(OUT, "base_unificada_homologada.csv"), index=False, encoding='utf-8-sig')
print(f"\n✅ Exportado")
print("FIN.")
