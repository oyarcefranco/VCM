"""
Análisis de Encuestas VCM USS - v2 con parsing correcto de headers multi-fila
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import pandas as pd
import numpy as np
import os
from collections import defaultdict
from rapidfuzz import fuzz

BASE = r"c:\Users\oyarc\OneDrive - Universidad San Sebastian\VCM\Encuestas Estudiantes\RV_ BASE ENCUESTA ESTUDIANTES 2021-2025"
OUT = r"c:\Users\oyarc\OneDrive - Universidad San Sebastian\VCM\Encuestas Estudiantes"

archivos = {
    2021: ("Encuesta estudiantes 2021 Reporte.xlsx", "Base de datos"),
    2022: ("Encuesta estudiantes 2022 Reporte.xlsx", "Base de datos"),
    2023: ("Encuesta estudiantes 2023 Reporte.xlsx", "Base de datos encuestas ajuste"),
    2024: ("BASE ENCUESTA ESTUDIANTES 2024.xlsx", "Reporte"),
    2025: ("BASE ENCUESTA ESTUDIANTES 2025.xlsx", "Reporte"),
}

# ── PASO 1: Parsear estructura real de cada archivo ──

def parse_2021_2022(filepath, sheet):
    """2021-2022: Fila1=secciones/preguntas, Fila2=sub-alternativas, Fila3=códigos, Datos desde Fila4"""
    raw = pd.read_excel(filepath, sheet_name=sheet, header=None)
    row_sections = raw.iloc[1]   # preguntas principales
    row_alts = raw.iloc[2]       # alternativas/sub-items
    row_codes = raw.iloc[3]      # códigos técnicos (KEY, RUT, O1, etc.)
    data = raw.iloc[4:].reset_index(drop=True)
    
    # Construir nombres de columna informativos
    preguntas = {}
    current_pregunta = None
    metadata_codes = {'KEY','RUT','CARRERA','FACULTAD','SEDE_DETALLE','SEDE',
                      'ID PROYECTO','NOMBRE PROYECTO','SEDE PC','FACULTAD PC'}
    
    for i in range(len(raw.columns)):
        code = str(row_codes.iloc[i]).strip() if pd.notna(row_codes.iloc[i]) else f"Col{i}"
        section = str(row_sections.iloc[i]).strip() if pd.notna(row_sections.iloc[i]) else None
        alt = str(row_alts.iloc[i]).strip() if pd.notna(row_alts.iloc[i]) else None
        
        if code in metadata_codes:
            data.rename(columns={i: code}, inplace=True)
            continue
        
        if section and section != 'nan':
            current_pregunta = section
        
        if current_pregunta:
            if code not in metadata_codes:
                if current_pregunta not in preguntas:
                    preguntas[current_pregunta] = {'cols': [], 'alternativas': [], 'codes': []}
                preguntas[current_pregunta]['cols'].append(i)
                preguntas[current_pregunta]['codes'].append(code)
                if alt and alt != 'nan':
                    preguntas[current_pregunta]['alternativas'].append(alt)
    
    return data, preguntas

def parse_2023(filepath, sheet):
    """2023: Fila0=secciones/preguntas, Fila3=alternativas/sub-items, Fila4=códigos, Datos desde Fila5"""
    raw = pd.read_excel(filepath, sheet_name=sheet, header=None)
    row_preguntas = raw.iloc[0]
    row_alts = raw.iloc[3]
    row_codes = raw.iloc[4]
    data = raw.iloc[5:].reset_index(drop=True)
    
    preguntas = {}
    current_pregunta = None
    metadata_codes = {'Nombre','RUT *','Key','Columna1','Proyecto en el que participaste:',
                      'Sede','Facultad del alumno','Carrera','Carrera '}
    metadata_map = {'Sede':'SEDE','Facultad del alumno':'FACULTAD','Carrera':'CARRERA','Carrera ':'CARRERA'}
    
    for i in range(len(raw.columns)):
        code = str(row_codes.iloc[i]).strip() if pd.notna(row_codes.iloc[i]) else f"Col{i}"
        preg = str(row_preguntas.iloc[i]).strip() if pd.notna(row_preguntas.iloc[i]) else None
        alt = str(row_alts.iloc[i]).strip() if pd.notna(row_alts.iloc[i]) else None
        
        if code in metadata_codes:
            mapped = metadata_map.get(code, code)
            data.rename(columns={i: mapped}, inplace=True)
            continue
        
        if preg and preg != 'nan' and preg != 'INFORMACION BASICA':
            current_pregunta = preg
        
        if current_pregunta:
            if current_pregunta not in preguntas:
                preguntas[current_pregunta] = {'cols': [], 'alternativas': [], 'codes': []}
            preguntas[current_pregunta]['cols'].append(i)
            preguntas[current_pregunta]['codes'].append(code)
            if alt and alt != 'nan':
                preguntas[current_pregunta]['alternativas'].append(alt)
    
    return data, preguntas

def parse_2024_2025(filepath, sheet):
    """2024-2025: Fila0=preguntas, Fila2=alternativas escala, Datos desde Fila4"""
    raw = pd.read_excel(filepath, sheet_name=sheet, header=None)
    row_preguntas = raw.iloc[0]
    row_alts = raw.iloc[2]
    data = raw.iloc[4:].reset_index(drop=True)
    
    preguntas = {}
    current_pregunta = None
    metadata_fields = {'Rut Encuestado','Nombres y apellidos encuestado','Correo',
                       'Tipo iniciativa','ID proyecto/Iniciativa','Nombre Proyecto/Iniciativa',
                       'ID Aplicacion','ID Aplicación','Sede Encuestado','Facultad Encuestado',
                       'Carrera Encuestado'}
    metadata_map = {'Sede Encuestado':'SEDE','Facultad Encuestado':'FACULTAD','Carrera Encuestado':'CARRERA'}
    
    for i in range(len(raw.columns)):
        preg = str(row_preguntas.iloc[i]).strip() if pd.notna(row_preguntas.iloc[i]) else None
        alt = str(row_alts.iloc[i]).strip() if pd.notna(row_alts.iloc[i]) else None
        
        if preg and preg in metadata_fields:
            mapped = metadata_map.get(preg, preg)
            data.rename(columns={i: mapped}, inplace=True)
            continue
        
        if preg and preg != 'nan':
            current_pregunta = preg
        
        if current_pregunta and current_pregunta not in metadata_fields:
            if current_pregunta not in preguntas:
                preguntas[current_pregunta] = {'cols': [], 'alternativas': [], 'codes': []}
            preguntas[current_pregunta]['cols'].append(i)
            if alt and alt != 'nan':
                preguntas[current_pregunta]['alternativas'].append(alt)
    
    return data, preguntas

# ── Cargar todos ──
datos = {}
preguntas_por_año = {}

for year, (fname, sheet) in archivos.items():
    fp = os.path.join(BASE, fname)
    if year in (2021, 2022):
        data, pregs = parse_2021_2022(fp, sheet)
    elif year == 2023:
        data, pregs = parse_2023(fp, sheet)
    else:
        data, pregs = parse_2024_2025(fp, sheet)
    
    datos[year] = data
    preguntas_por_año[year] = pregs
    print(f"{year}: {len(data)} registros, {len(pregs)} preguntas parseadas")

# ── Mostrar preguntas por año ──
print("\n" + "="*80)
print("CATALOGO DE PREGUNTAS POR AÑO")
print("="*80)
for year, pregs in preguntas_por_año.items():
    print(f"\n--- {year} ({len(pregs)} preguntas) ---")
    for i, (preg, info) in enumerate(pregs.items(), 1):
        alts_str = " | ".join(info['alternativas'][:5])
        if len(info['alternativas']) > 5:
            alts_str += f" ... (+{len(info['alternativas'])-5})"
        print(f"  P{i:02d}: {preg[:120]}")
        print(f"       Alternativas ({len(info['alternativas'])}): {alts_str[:150]}")

# ── PASO 2: HOMOLOGACIÓN EXACTA ──
print("\n" + "="*80)
print("PASO 2: HOMOLOGACION EXACTA")
print("="*80)

def norm(t):
    return ' '.join(str(t).strip().lower().split())

# Crear fingerprints: (pregunta_normalizada, alternativas_como_frozenset)
fps = {}  # {fingerprint: [(year, pregunta_original, info)]}
for year, pregs in preguntas_por_año.items():
    for preg, info in pregs.items():
        fp = (norm(preg), frozenset(norm(a) for a in info['alternativas']))
        if fp not in fps:
            fps[fp] = []
        fps[fp].append((year, preg, info))

# Filtrar multi-año
homologadas = {fp: occ for fp, occ in fps.items() if len(set(y for y,_,_ in occ)) > 1}
print(f"\nPreguntas homologadas exactas (mismo enunciado + mismas alternativas): {len(homologadas)}")

tabla1 = []
for i, (fp, occ) in enumerate(homologadas.items(), 1):
    años = sorted(set(y for y,_,_ in occ))
    preg_orig = occ[0][1]
    alts = sorted(fp[1])
    tabla1.append({
        'ID': f'H{i:03d}',
        'Enunciado': preg_orig[:150],
        'Alternativas': ' | '.join(alts)[:200],
        'N_Alt': len(alts),
        'Años': ', '.join(str(a) for a in años),
        'N_Años': len(años),
    })

df_t1 = pd.DataFrame(tabla1)
if not df_t1.empty:
    df_t1 = df_t1.sort_values('N_Años', ascending=False)
    print("\n--- TABLA 1: PREGUNTAS HOMOLOGADAS ---")
    for _, r in df_t1.iterrows():
        print(f"  {r['ID']} | Años: {r['Años']} | {r['Enunciado'][:100]}")
        print(f"         Alt: {r['Alternativas'][:120]}")
else:
    print("  No se encontraron coincidencias exactas.")

# ── PASO 2b: DataFrame unificado ──
frames = []
for i, (fp, occ) in enumerate(homologadas.items(), 1):
    pid = f'H{i:03d}'
    for year, preg, info in occ:
        df_yr = datos[year]
        for col_idx in info['cols']:
            if col_idx < len(df_yr.columns):
                col_name = df_yr.columns[col_idx]
                temp = pd.DataFrame({
                    'Año': year, 'ID_Pregunta': pid,
                    'Enunciado': preg[:150],
                    'Respuesta': df_yr[col_name].values,
                })
                for mc in ['SEDE','FACULTAD','CARRERA']:
                    if mc in df_yr.columns:
                        temp[mc] = df_yr[mc].values
                frames.append(temp)

if frames:
    df_unificado = pd.concat(frames, ignore_index=True)
    print(f"\nDataFrame unificado: {df_unificado.shape}")
else:
    df_unificado = pd.DataFrame()
    print("\nNo hay DataFrame unificado.")

# ── PASO 3: AGRUPACIÓN POR SIMILITUD ──
print("\n" + "="*80)
print("PASO 3: AGRUPACION POR SIMILITUD")
print("="*80)

# Todas las preguntas únicas por año
all_pregs = []
homo_keys = set()
for fp, occ in homologadas.items():
    for y, p, _ in occ:
        homo_keys.add((y, norm(p)))

for year, pregs in preguntas_por_año.items():
    for preg, info in pregs.items():
        if (year, norm(preg)) not in homo_keys:
            all_pregs.append({'year': year, 'preg': preg, 'norm': norm(preg), 
                            'alts': frozenset(norm(a) for a in info['alternativas'])})

print(f"Preguntas no homologadas: {len(all_pregs)}")

# Agrupar por similitud
grupos = []
usado = set()
for i, p1 in enumerate(all_pregs):
    if i in usado:
        continue
    grupo = [p1]
    usado.add(i)
    for j, p2 in enumerate(all_pregs):
        if j in usado or p1['year'] == p2['year']:
            continue
        sim = fuzz.token_sort_ratio(p1['norm'], p2['norm'])
        if sim >= 70:
            grupo.append(p2)
            usado.add(j)
    if len(grupo) > 1 and len(set(g['year'] for g in grupo)) > 1:
        grupos.append(grupo)

print(f"Grupos similares encontrados: {len(grupos)}")

tabla2 = []
for gi, grupo in enumerate(grupos, 1):
    for p in grupo:
        ref_norm = grupo[0]['norm']
        sim = fuzz.token_sort_ratio(ref_norm, p['norm'])
        alt_match = "Si" if p['alts'] == grupo[0]['alts'] else "No"
        tabla2.append({
            'Grupo': f'G{gi:03d}',
            'Año': p['year'],
            'Enunciado': p['preg'][:120],
            'Sim%': sim,
            'AltCoinciden': alt_match,
        })

df_t2 = pd.DataFrame(tabla2)
print("\n--- TABLA 2: GRUPOS SIMILARES PARA REVISION MANUAL ---")
for gid in df_t2['Grupo'].unique() if not df_t2.empty else []:
    gdf = df_t2[df_t2['Grupo'] == gid]
    print(f"\n  === {gid} ===")
    for _, r in gdf.iterrows():
        print(f"  {r['Año']}: {r['Enunciado'][:100]} | Sim:{r['Sim%']}% | AltOK:{r['AltCoinciden']}")

# ── PASO 4: HALLAZGOS ──
print("\n" + "="*80)
print("PASO 4: HALLAZGOS Y ANOMALIAS")
print("="*80)

for year, df in datos.items():
    n = len(df)
    nulos_pct = df.isnull().mean() * 100
    alto_nulo = nulos_pct[nulos_pct > 50]
    dupes = df.duplicated().sum()
    print(f"\n{year}: {n} filas, {len(df.columns)} cols")
    if dupes: print(f"  ! {dupes} filas duplicadas ({dupes/n*100:.1f}%)")
    if not alto_nulo.empty:
        print(f"  ! {len(alto_nulo)} columnas con >50% nulos")

# Evolución del nro de preguntas
print("\n--- Evolución estructural ---")
for year, pregs in preguntas_por_año.items():
    print(f"  {year}: {len(pregs)} preguntas | {len(datos[year])} encuestados")

# ── EXPORTAR ──
print("\n" + "="*80)
print("EXPORTACION")
print("="*80)

if not df_unificado.empty:
    p1 = os.path.join(OUT, "preguntas_homologadas_unificadas.csv")
    df_unificado.to_csv(p1, index=False, encoding='utf-8-sig')
    print(f"OK: {p1}")

if not df_t1.empty:
    p2 = os.path.join(OUT, "tabla_homologacion.csv")
    df_t1.to_csv(p2, index=False, encoding='utf-8-sig')
    print(f"OK: {p2}")

if not df_t2.empty:
    p3 = os.path.join(OUT, "tabla_similares_revision.csv")
    df_t2.to_csv(p3, index=False, encoding='utf-8-sig')
    print(f"OK: {p3}")

print("\nFIN.")
