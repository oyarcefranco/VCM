"""
BASE UNIFICADA DEFINITIVA — Encuestas VCM USS 2021-2025
Reconstrucción completa con homologación de preguntas y respuestas.
Formato: 1 fila = 1 encuestado, columnas = preguntas homologadas.
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import pandas as pd
import numpy as np
import os

BASE = r"c:\Users\oyarc\OneDrive - Universidad San Sebastian\VCM\Encuestas Estudiantes\RV_ BASE ENCUESTA ESTUDIANTES 2021-2025"
OUT = r"c:\Users\oyarc\OneDrive - Universidad San Sebastian\VCM\Encuestas Estudiantes"

# ═══════════════════════════════════════════════════════════════
# PARSERS (reutilizados)
# ═══════════════════════════════════════════════════════════════
def load_raw(filepath, sheet):
    return pd.read_excel(filepath, sheet_name=sheet, header=None)

def parse_2021_2022(filepath, sheet):
    raw = load_raw(filepath, sheet)
    r1, r2, r3 = raw.iloc[1], raw.iloc[2], raw.iloc[3]
    data = raw.iloc[4:].reset_index(drop=True)
    meta_codes = {'KEY','RUT','CARRERA','FACULTAD','SEDE_DETALLE','SEDE',
                  'ID PROYECTO','NOMBRE PROYECTO','SEDE PC','FACULTAD PC'}
    meta = {}; preguntas = {}; curr = None
    for i in range(len(raw.columns)):
        code = str(r3.iloc[i]).strip() if pd.notna(r3.iloc[i]) else f"Col{i}"
        sec = str(r1.iloc[i]).strip() if pd.notna(r1.iloc[i]) else None
        alt = str(r2.iloc[i]).strip() if pd.notna(r2.iloc[i]) else None
        if code in meta_codes:
            meta[code] = i; continue
        if sec and sec != 'nan': curr = sec
        if curr:
            if curr not in preguntas: preguntas[curr] = {'cols':[], 'alts':[], 'codes':[]}
            preguntas[curr]['cols'].append(i)
            preguntas[curr]['codes'].append(code)
            if alt and alt != 'nan': preguntas[curr]['alts'].append((i, alt))
    return data, preguntas, meta

def parse_2023(filepath, sheet):
    raw = load_raw(filepath, sheet)
    r0, r3, r4 = raw.iloc[0], raw.iloc[3], raw.iloc[4]
    data = raw.iloc[5:].reset_index(drop=True)
    meta_codes = {'Nombre','RUT *','Key','Columna1','Proyecto en el que participaste:',
                  'Sede','Facultad del alumno','Carrera','Carrera '}
    meta_map = {'Sede':'SEDE','Facultad del alumno':'FACULTAD','Carrera':'CARRERA','Carrera ':'CARRERA'}
    meta = {}; preguntas = {}; curr = None
    for i in range(len(raw.columns)):
        code = str(r4.iloc[i]).strip() if pd.notna(r4.iloc[i]) else f"Col{i}"
        preg = str(r0.iloc[i]).strip() if pd.notna(r0.iloc[i]) else None
        alt = str(r3.iloc[i]).strip() if pd.notna(r3.iloc[i]) else None
        if code in meta_codes:
            mapped = meta_map.get(code, code)
            meta[mapped] = i; continue
        if preg and preg != 'nan' and 'INFORMACI' not in preg:
            curr = preg
        if curr:
            if curr not in preguntas: preguntas[curr] = {'cols':[], 'alts':[], 'codes':[]}
            preguntas[curr]['cols'].append(i)
            preguntas[curr]['codes'].append(code)
            if alt and alt != 'nan': preguntas[curr]['alts'].append((i, alt))
    return data, preguntas, meta

def parse_2024_2025(filepath, sheet):
    raw = load_raw(filepath, sheet)
    r0, r2 = raw.iloc[0], raw.iloc[2]
    data = raw.iloc[4:].reset_index(drop=True)
    meta_fields = {'Rut Encuestado','Nombres y apellidos encuestado','Correo',
                   'Tipo iniciativa','ID proyecto/Iniciativa','Nombre Proyecto/Iniciativa',
                   'ID Aplicacion','ID Aplicación','Sede Encuestado','Facultad Encuestado',
                   'Carrera Encuestado'}
    meta_map = {'Sede Encuestado':'SEDE','Facultad Encuestado':'FACULTAD','Carrera Encuestado':'CARRERA'}
    meta = {}; preguntas = {}; curr = None
    for i in range(len(raw.columns)):
        preg = str(r0.iloc[i]).strip() if pd.notna(r0.iloc[i]) else None
        alt = str(r2.iloc[i]).strip() if pd.notna(r2.iloc[i]) else None
        if preg and preg in meta_fields:
            mapped = meta_map.get(preg, preg)
            meta[mapped] = i; continue
        if preg and preg != 'nan': curr = preg
        if curr and curr not in meta_fields:
            if curr not in preguntas: preguntas[curr] = {'cols':[], 'alts':[], 'codes':[]}
            preguntas[curr]['cols'].append(i)
            if alt and alt != 'nan': preguntas[curr]['alts'].append((i, alt))
    return data, preguntas, meta

# ═══════════════════════════════════════════════════════════════
# CARGAR TODOS LOS DATOS
# ═══════════════════════════════════════════════════════════════
archivos = {
    2021: ("Encuesta estudiantes 2021 Reporte.xlsx", "Base de datos"),
    2022: ("Encuesta estudiantes 2022 Reporte.xlsx", "Base de datos"),
    2023: ("Encuesta estudiantes 2023 Reporte.xlsx", "Base de datos encuestas ajuste"),
    2024: ("BASE ENCUESTA ESTUDIANTES 2024.xlsx", "Reporte"),
    2025: ("BASE ENCUESTA ESTUDIANTES 2025.xlsx", "Reporte"),
}

all_data = {}
all_pregs = {}
all_meta = {}

for year, (fname, sheet) in archivos.items():
    fp = os.path.join(BASE, fname)
    if year in (2021,2022): d,p,m = parse_2021_2022(fp, sheet)
    elif year == 2023: d,p,m = parse_2023(fp, sheet)
    else: d,p,m = parse_2024_2025(fp, sheet)
    all_data[year] = d
    all_pregs[year] = p
    all_meta[year] = m
    print(f"{year}: {len(d)} filas, {len(p)} preguntas")

# ═══════════════════════════════════════════════════════════════
# FUNCIÓN: Extraer respuesta one-hot → texto
# ═══════════════════════════════════════════════════════════════
def onehot_to_text(data, alts_list, default_col=None):
    """Convierte columnas one-hot a respuesta textual.
    alts_list: [(col_idx, alt_text), ...]
    Si hay un default_col (respuesta directa), usarlo primero.
    """
    n = len(data)
    result = [None] * n
    
    if default_col is not None and len(alts_list) <= 1:
        # Respuesta directa (no es one-hot)
        for idx in range(n):
            val = data.iloc[idx, default_col]
            if pd.notna(val) and str(val).strip() not in ('0','nan',''):
                result[idx] = str(val).strip()
        return result
    
    for idx in range(n):
        selected = []
        for col_i, alt_text in alts_list:
            val = data.iloc[idx, col_i]
            if pd.notna(val):
                v = str(val).strip()
                if v == '1' or v.lower() == alt_text.lower():
                    selected.append(alt_text)
                elif v not in ('0','nan','') and not v.replace('.','').isdigit():
                    # Es texto directo
                    selected.append(v)
        if selected:
            result[idx] = ' | '.join(selected)
    return result

def extract_likert(data, col_idx):
    """Extrae respuesta Likert de una columna (puede ser numérica o textual)."""
    result = []
    for idx in range(len(data)):
        val = data.iloc[idx, col_idx]
        if pd.notna(val):
            result.append(str(val).strip())
        else:
            result.append(None)
    return result

# ═══════════════════════════════════════════════════════════════
# FUNCIÓN: Buscar pregunta en un año
# ═══════════════════════════════════════════════════════════════
def find_q(pregs, *keywords):
    for q, info in pregs.items():
        if all(kw.lower() in q.lower() for kw in keywords):
            return q, info
    return None, None

# ═══════════════════════════════════════════════════════════════
# CONSTRUIR BASE UNIFICADA
# ═══════════════════════════════════════════════════════════════
print("\n" + "="*80)
print("CONSTRUYENDO BASE UNIFICADA")
print("="*80)

# Preguntas canónicas a extraer (basado en el análisis previo)
PREGUNTAS_CANONICAS = [
    'Q01_Significancia_Formacion',
    'Q02_Importancia_Aspectos_Aplicar',
    'Q03_Importancia_Aspectos_Realidad',
    'Q04_Importancia_Aspectos_Vocacion',
    'Q05_Importancia_Aspectos_Valores',
    'Q06_Habilidad_Empatia',
    'Q07_Habilidad_Comunicacion',
    'Q08_Habilidad_Colaboracion',
    'Q09_Habilidad_Resolucion',
    'Q10_Habilidad_Adaptacion',
    'Q11_Habilidad_Competencia',
    'Q12_Habilidad_Prolijidad',
    'Q13_Habilidad_Manejo_Info',
    'Q14_Valores_Sebastianos',
    'Q15_Importancia_Beneficiados',
    'Q16_Conocer_Campo_Laboral',
    'Q17_Cumplimiento_Expectativas',
    'Q18_Recomendaria',
    'Q19_Vinculacion_Medio',
]

frames = []

for year in [2021, 2022, 2023, 2024, 2025]:
    data = all_data[year]
    pregs = all_pregs[year]
    meta = all_meta[year]
    n = len(data)
    
    print(f"\nProcesando {year} ({n} filas)...")
    
    # Metadata
    row = {'Año': [year]*n}
    for mk in ['SEDE','FACULTAD','CARRERA']:
        if mk in meta:
            row[mk] = [str(data.iloc[i, meta[mk]]).strip() if pd.notna(data.iloc[i, meta[mk]]) else None for i in range(n)]
        else:
            row[mk] = [None]*n
    
    # ── Q01: Significancia para formación profesional ──
    if year in (2021, 2022):
        # No existe directamente, buscar en sub-ítems
        row['Q01_Significancia_Formacion'] = [None]*n
    elif year == 2023:
        q, info = find_q(pregs, 'significativo', 'formación profesional')
        if q and info['cols']:
            row['Q01_Significancia_Formacion'] = extract_likert(data, info['cols'][0])
        else:
            row['Q01_Significancia_Formacion'] = [None]*n
    elif year == 2024:
        q, info = find_q(pregs, 'significativo', 'formación profesional')
        if q and info['alts']:
            vals = onehot_to_text(data, info['alts'])
            # Mapear a escala canónica 1-5
            m = {'Muy significativo':5,'Significativo':4,'Medianamente significativo':3,
                 'Poco significativo':2,'Nada significativo':1}
            row['Q01_Significancia_Formacion'] = [m.get(v, v) for v in vals]
        else:
            row['Q01_Significancia_Formacion'] = [None]*n
    elif year == 2025:
        q, info = find_q(pregs, 'impacto', 'formación profesional')
        if q and info['alts']:
            vals = onehot_to_text(data, info['alts'])
            m = {'Muy positivo':5,'Positivo':4,'Neutro (no impactó)':3,'Negativo':2,'Muy negativo':1}
            row['Q01_Significancia_Formacion'] = [m.get(v, v) for v in vals]
        else:
            row['Q01_Significancia_Formacion'] = [None]*n
    
    # ── Q02-Q05: Importancia para aspectos (sub-ítems comunes) ──
    # Buscar la pregunta "importancia/significativa para el logro de los siguientes aspectos"
    if year in (2021, 2022, 2023):
        q, info = find_q(pregs, 'importante', 'significativa', 'experiencia')
        if q:
            for col_i, alt in info['alts']:
                alt_l = alt.lower()
                val_col = extract_likert(data, col_i)
                if 'aplicar' in alt_l and 'contenido' in alt_l:
                    row['Q02_Importancia_Aspectos_Aplicar'] = val_col
                elif 'realidad' in alt_l and 'conectar' in alt_l:
                    row['Q03_Importancia_Aspectos_Realidad'] = val_col
                elif 'vocación' in alt_l:
                    row['Q04_Importancia_Aspectos_Vocacion'] = val_col
                elif 'valores sebastianos' in alt_l:
                    row['Q05_Importancia_Aspectos_Valores'] = val_col
    elif year in (2024, 2025):
        q, info = find_q(pregs, 'importante', 'logro', 'aspectos') if year==2024 else (None,None)
        if not q: q, info = find_q(pregs, 'importancia', 'logro', 'aspectos')
        if q:
            for col_i, alt in info['alts']:
                alt_l = alt.lower()
                vals = onehot_to_text(data, [(col_i, alt)])
                # Convertir: seleccionado=1, no seleccionado=0
                binary = []
                for i in range(n):
                    v = data.iloc[i, col_i]
                    binary.append(1 if pd.notna(v) and str(v).strip() == '1' else 0)
                
                if 'aplicar' in alt_l and 'aprendido' in alt_l:
                    row['Q02_Importancia_Aspectos_Aplicar'] = binary
                elif 'realidad' in alt_l and 'conecta' in alt_l:
                    row['Q03_Importancia_Aspectos_Realidad'] = binary
                elif 'vocación' in alt_l:
                    row['Q04_Importancia_Aspectos_Vocacion'] = binary
                elif 'valores sebastianos' in alt_l:
                    row['Q05_Importancia_Aspectos_Valores'] = binary
    
    # ── Q06-Q13: Habilidades ──
    hab_map = {
        'Q06_Habilidad_Empatia': ['empatía', 'empatia'],
        'Q07_Habilidad_Comunicacion': ['comunicación', 'comunicacion'],
        'Q08_Habilidad_Colaboracion': ['colaboración', 'colaboracion', 'trabajo en equipo'],
        'Q09_Habilidad_Resolucion': ['resolución de problemas', 'resolucion de problemas'],
        'Q10_Habilidad_Adaptacion': ['adaptación y flexibilidad', 'adaptacion y flexibilidad'],
        'Q11_Habilidad_Competencia': ['competencia disciplinar'],
        'Q12_Habilidad_Prolijidad': ['prolijidad'],
        'Q13_Habilidad_Manejo_Info': ['manejo de información', 'manejo de informacion'],
    }
    
    q, info = find_q(pregs, 'fortalecidas', 'habilidades')
    if not q: q, info = find_q(pregs, 'fortalecimiento', 'habilidades')
    
    if q:
        for qkey, keywords in hab_map.items():
            found = False
            for col_i, alt in info['alts']:
                alt_l = alt.lower().strip().rstrip('.')
                for kw in keywords:
                    if kw in alt_l:
                        if year in (2021, 2022, 2023):
                            row[qkey] = extract_likert(data, col_i)
                        else:
                            binary = []
                            for i in range(n):
                                v = data.iloc[i, col_i]
                                binary.append(1 if pd.notna(v) and str(v).strip() == '1' else 0)
                            row[qkey] = binary
                        found = True
                        break
                if found: break
    
    # ── Q14: Valores sebastianos (one-hot → texto) ──
    q, info = find_q(pregs, 'valores sebastianos')
    if q and info['alts']:
        if year in (2021, 2022):
            vals = onehot_to_text(data, info['alts'])
            # Mapear a valores canónicos
            mapeo_val = {
                'búsqueda de la verdad': 'Verdad',
                'valor de la caridad y la justicia': 'Justicia',
                'honestidad': 'Honestidad',
                'responsabilidad': 'Responsabilidad',
                'cultivo de la reflexión y la racionalidad': 'Racionalidad',
                'solidaridad, alegría de servir y sentido del deber': 'Solidaridad',
                'espíritu de superación y progreso personal': 'Superación',
                'laboriosidad y vocación por el trabajo bien hecho': 'Laboriosidad',
                'fortaleza y perseverancia': 'Fortaleza',
                'ninguno': 'Ninguno',
            }
            row['Q14_Valores_Sebastianos'] = vals  # dejar texto compuesto
        elif year in (2024, 2025):
            vals = onehot_to_text(data, info['alts'])
            mapeo_val2 = {
                'la racionalidad y capacidad de reflexión.': 'Racionalidad',
                'la honestidad.': 'Honestidad',
                'la justicia.': 'Justicia',
                'la responsabilidad y la prudencia.': 'Responsabilidad',
                'la tolerancia.': 'Tolerancia',
                'la solidaridad y alegría de servir.': 'Solidaridad',
                'el espíritu de superación.': 'Superación',
                'fortaleza y perseverancia.': 'Fortaleza',
                'la dignidad superior de la persona humana.': 'Dignidad',
                'el cultivo de la verdad.': 'Verdad',
            }
            row['Q14_Valores_Sebastianos'] = vals
    
    # ── Q15: Importancia para beneficiados ──
    q, info = find_q(pregs, 'percepción', 'importancia', 'personas')
    if not q: q, info = find_q(pregs, 'percepción', 'nivel', 'importancia')
    if q:
        if year == 2023:
            row['Q15_Importancia_Beneficiados'] = extract_likert(data, info['cols'][0])
        elif year in (2024, 2025):
            vals = onehot_to_text(data, info['alts'])
            m = {'Muy importante':5,'Importante':4,'Medianamente importante':3,
                 'Poco importante':2,'Nada importante':1}
            row['Q15_Importancia_Beneficiados'] = [m.get(v, v) for v in vals]
    
    # ── Q16: Conocer campo laboral ──
    q, info = find_q(pregs, 'conocer', 'campo laboral')
    if q:
        if year == 2023:
            row['Q16_Conocer_Campo_Laboral'] = extract_likert(data, info['cols'][0])
        elif year == 2024:
            vals = onehot_to_text(data, info['alts'])
            m = {'Sí':1,'No':0}
            row['Q16_Conocer_Campo_Laboral'] = [m.get(v, v) for v in vals]
    
    # ── Q17: Cumplimiento de expectativas ──
    q, info = find_q(pregs, 'cumplió', 'expectativas')
    if q:
        if year == 2023:
            row['Q17_Cumplimiento_Expectativas'] = extract_likert(data, info['cols'][0])
        elif year == 2024:
            vals = onehot_to_text(data, info['alts'])
            m = {'Totalmente':5,'Casi totalmente':4,'Medianamente':3,'Sólo en parte':2,'No las cumplió':1}
            row['Q17_Cumplimiento_Expectativas'] = [m.get(v, v) for v in vals]
        elif year == 2025:
            vals = onehot_to_text(data, info['alts'])
            m = {'Superó mis expectativas':5,'Totalmente':4,'En gran medida':3,'Sólo en parte':2,'No las cumplió':1}
            row['Q17_Cumplimiento_Expectativas'] = [m.get(v, v) for v in vals]
    
    # ── Q18: Recomendaría ──
    q, info = find_q(pregs, 'recomendarías', 'compañeros')
    if q:
        if year == 2023:
            row['Q18_Recomendaria'] = extract_likert(data, info['cols'][0])
        elif year in (2024, 2025):
            vals = onehot_to_text(data, info['alts'])
            m = {'Sí':1,'No':0}
            row['Q18_Recomendaria'] = [m.get(v, v) for v in vals]
    
    # ── Q19: Sabías que era vinculación con el medio ──
    q, info = find_q(pregs, 'vinculación con el medio')
    if q:
        if year in (2024, 2025):
            vals = onehot_to_text(data, info['alts'])
            m = {'Sí':1,'No':0}
            row['Q19_Vinculacion_Medio'] = [m.get(v, v) for v in vals]
    
    # Rellenar columnas faltantes con None
    for qc in PREGUNTAS_CANONICAS:
        if qc not in row:
            row[qc] = [None]*n
    
    # Verificar longitudes
    for k, v in row.items():
        if len(v) != n:
            print(f"  !! {k}: esperado {n}, tiene {len(v)} — truncando/rellenando")
            if len(v) > n: row[k] = v[:n]
            else: row[k] = v + [None]*(n-len(v))
    
    df_year = pd.DataFrame(row)
    frames.append(df_year)
    
    # Resumen de cobertura
    for qc in PREGUNTAS_CANONICAS:
        non_null = df_year[qc].notna().sum()
        if non_null > 0:
            print(f"  {qc}: {non_null} respuestas ({non_null/n*100:.1f}%)")

# ═══════════════════════════════════════════════════════════════
# CONCATENAR Y EXPORTAR
# ═══════════════════════════════════════════════════════════════
df_final = pd.concat(frames, ignore_index=True)

# Limpieza final
df_final = df_final.replace({'nan': None, 'None': None, '': None})

print(f"\n{'='*80}")
print(f"BASE FINAL: {df_final.shape[0]} filas x {df_final.shape[1]} columnas")
print(f"{'='*80}")

# Cobertura por pregunta y año
print("\nCOBERTURA (% respuestas no-nulas por pregunta y año):")
cobertura = df_final.groupby('Año')[PREGUNTAS_CANONICAS].apply(lambda x: x.notna().mean()*100)
print(cobertura.round(1).to_string())

# Valores únicos por pregunta
print("\n\nVALORES UNICOS POR PREGUNTA:")
for qc in PREGUNTAS_CANONICAS:
    vals = df_final[qc].dropna().unique()
    if len(vals) <= 15:
        print(f"\n  {qc}: {sorted(str(v) for v in vals)}")
    else:
        print(f"\n  {qc}: {len(vals)} valores únicos (primeros 10: {sorted(str(v) for v in vals[:10])})")

# Exportar
path_out = os.path.join(OUT, "base_unificada_homologada.csv")
df_final.to_csv(path_out, index=False, encoding='utf-8-sig')
print(f"\n✅ Exportado: {path_out}")

# Exportar diccionario de datos
dict_data = []
for qc in PREGUNTAS_CANONICAS:
    años_con_datos = []
    for y in [2021,2022,2023,2024,2025]:
        sub = df_final[df_final['Año']==y]
        if sub[qc].notna().sum() > 0:
            años_con_datos.append(str(y))
    
    vals = df_final[qc].dropna().unique()
    dict_data.append({
        'Variable': qc,
        'Años_Disponibles': ', '.join(años_con_datos),
        'N_Años': len(años_con_datos),
        'Tipo_Respuesta': 'Numérica' if all(str(v).replace('.','').replace('-','').isdigit() for v in vals if v) else 'Texto/Mixta',
        'Valores_Posibles': ' | '.join(sorted(set(str(v) for v in vals)))[:200] if len(vals) <= 15 else f'{len(vals)} valores',
    })

df_dict = pd.DataFrame(dict_data)
path_dict = os.path.join(OUT, "diccionario_base_unificada.csv")
df_dict.to_csv(path_dict, index=False, encoding='utf-8-sig')
print(f"✅ Diccionario: {path_dict}")

print("\nFIN.")
