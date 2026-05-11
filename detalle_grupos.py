"""
Detalle de alternativas por grupo similar para propuesta de homologación
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import pandas as pd
import os
from rapidfuzz import fuzz

BASE = r"c:\Users\oyarc\OneDrive - Universidad San Sebastian\VCM\Encuestas Estudiantes\RV_ BASE ENCUESTA ESTUDIANTES 2021-2025"

archivos = {
    2021: ("Encuesta estudiantes 2021 Reporte.xlsx", "Base de datos"),
    2022: ("Encuesta estudiantes 2022 Reporte.xlsx", "Base de datos"),
    2023: ("Encuesta estudiantes 2023 Reporte.xlsx", "Base de datos encuestas ajuste"),
    2024: ("BASE ENCUESTA ESTUDIANTES 2024.xlsx", "Reporte"),
    2025: ("BASE ENCUESTA ESTUDIANTES 2025.xlsx", "Reporte"),
}

# Reusar parsers del script anterior
def parse_2021_2022(filepath, sheet):
    raw = pd.read_excel(filepath, sheet_name=sheet, header=None)
    row_sections = raw.iloc[1]
    row_alts = raw.iloc[2]
    row_codes = raw.iloc[3]
    data = raw.iloc[4:].reset_index(drop=True)
    preguntas = {}
    current_pregunta = None
    metadata_codes = {'KEY','RUT','CARRERA','FACULTAD','SEDE_DETALLE','SEDE',
                      'ID PROYECTO','NOMBRE PROYECTO','SEDE PC','FACULTAD PC'}
    for i in range(len(raw.columns)):
        code = str(row_codes.iloc[i]).strip() if pd.notna(row_codes.iloc[i]) else f"Col{i}"
        section = str(row_sections.iloc[i]).strip() if pd.notna(row_sections.iloc[i]) else None
        alt = str(row_alts.iloc[i]).strip() if pd.notna(row_alts.iloc[i]) else None
        if code in metadata_codes:
            continue
        if section and section != 'nan':
            current_pregunta = section
        if current_pregunta:
            if current_pregunta not in preguntas:
                preguntas[current_pregunta] = {'alternativas': [], 'codes': []}
            preguntas[current_pregunta]['codes'].append(code)
            if alt and alt != 'nan':
                preguntas[current_pregunta]['alternativas'].append(alt)
    return data, preguntas

def parse_2023(filepath, sheet):
    raw = pd.read_excel(filepath, sheet_name=sheet, header=None)
    row_preguntas = raw.iloc[0]
    row_alts = raw.iloc[3]
    row_codes = raw.iloc[4]
    data = raw.iloc[5:].reset_index(drop=True)
    preguntas = {}
    current_pregunta = None
    metadata_codes = {'Nombre','RUT *','Key','Columna1','Proyecto en el que participaste:',
                      'Sede','Facultad del alumno','Carrera','Carrera '}
    for i in range(len(raw.columns)):
        code = str(row_codes.iloc[i]).strip() if pd.notna(row_codes.iloc[i]) else f"Col{i}"
        preg = str(row_preguntas.iloc[i]).strip() if pd.notna(row_preguntas.iloc[i]) else None
        alt = str(row_alts.iloc[i]).strip() if pd.notna(row_alts.iloc[i]) else None
        if code in metadata_codes:
            continue
        if preg and preg != 'nan' and preg != 'INFORMACION BASICA' and 'INFORMACI' not in preg:
            current_pregunta = preg
        if current_pregunta:
            if current_pregunta not in preguntas:
                preguntas[current_pregunta] = {'alternativas': [], 'codes': []}
            preguntas[current_pregunta]['codes'].append(code)
            if alt and alt != 'nan':
                preguntas[current_pregunta]['alternativas'].append(alt)
    return data, preguntas

def parse_2024_2025(filepath, sheet):
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
    for i in range(len(raw.columns)):
        preg = str(row_preguntas.iloc[i]).strip() if pd.notna(row_preguntas.iloc[i]) else None
        alt = str(row_alts.iloc[i]).strip() if pd.notna(row_alts.iloc[i]) else None
        if preg and preg in metadata_fields:
            continue
        if preg and preg != 'nan':
            current_pregunta = preg
        if current_pregunta and current_pregunta not in metadata_fields:
            if current_pregunta not in preguntas:
                preguntas[current_pregunta] = {'alternativas': [], 'codes': []}
            if alt and alt != 'nan':
                preguntas[current_pregunta]['alternativas'].append(alt)
    return data, preguntas

# Cargar
preguntas_por_año = {}
for year, (fname, sheet) in archivos.items():
    fp = os.path.join(BASE, fname)
    if year in (2021, 2022):
        _, pregs = parse_2021_2022(fp, sheet)
    elif year == 2023:
        _, pregs = parse_2023(fp, sheet)
    else:
        _, pregs = parse_2024_2025(fp, sheet)
    preguntas_por_año[year] = pregs

# Definir los 10 grupos manualmente basado en los resultados anteriores
grupos_def = [
    {
        'id': 'G001',
        'tema': 'Importancia de la experiencia para logro de aspectos',
        'match': {
            2021: 'Indica cuán importante',
            2022: 'Indica cuán importante',  # homologada exacta con 2023
            2023: 'Indica cuán importante',
            2024: '¿Cuán importante consideras',
            2025: 'Evalúa el grado de importancia',
        }
    },
    {
        'id': 'G002',
        'tema': 'Fortalecimiento de habilidades',
        'match': {
            2021: 'En base a tu experiencia en el Proyecto Colaborativo ¿Cuán fortalecidas',
            2022: 'En base a tu experiencia en el Proyecto Colaborativo ¿Cuán fortalecidas',
            2023: 'En base a tu experiencia en el Proyecto Colaborativo ¿Cuán fortalecidas',
            2024: 'En base a tu experiencia en el Proyecto Colaborativo ¿Cuán fortalecidas',
            2025: 'En base a tu experiencia en el Proyecto Colaborativo',
        }
    },
    {
        'id': 'G003',
        'tema': 'Conocimiento del campo laboral (condicional)',
        'match': {
            2021: 'Si respondiste que',
            2022: 'Si respondiste que',
            2023: 'Si respondiste que',
        }
    },
    {
        'id': 'G004',
        'tema': 'Valores sebastianos',
        'match': {
            2021: 'Seleccione los tres valores',
            2022: 'Seleccione los tres valores',
            2023: 'Seleccione los tres valores',
            2024: '¿Cuáles son los tres valores',
            2025: 'Desde tu perspectiva ¿Cuáles son los dos valores',
        }
    },
    {
        'id': 'G005',
        'tema': 'Importancia para beneficiados',
        'match': {
            2023: 'Según tu percepción, evalúa el nivel',
            2024: 'Según tu percepción, ¿qué nivel',
            2025: 'Según tu percepción ¿Qué nivel',
        }
    },
    {
        'id': 'G006',
        'tema': 'Significancia para formación profesional',
        'match': {
            2023: '¿Qué tan significativo fue participar',
            2024: '¿Qué tan significativo fue participar',
            2025: '¿Cómo evaluarías el impacto',
        }
    },
    {
        'id': 'G007',
        'tema': 'Conocer campo laboral',
        'match': {
            2023: '¿Consideras que este proyecto te permitió conocer',
            2024: '¿Consideras que este proyecto te permitió conocer',
        }
    },
    {
        'id': 'G008',
        'tema': 'Colaboración interdisciplinaria',
        'match': {
            2023: 'Señala el grado de acuerdo o desacuerdo',
            2024: 'Señala el grado de acuerdo o desacuerdo',
        }
    },
    {
        'id': 'G009',
        'tema': 'Cumplimiento de expectativas',
        'match': {
            2023: '¿El Proyecto Colaborativo cumplió con mis',
            2024: '¿El Proyecto Colaborativo cumplió con tus',
            2025: '¿El Proyecto Colaborativo cumplió con tus',
        }
    },
    {
        'id': 'G010',
        'tema': 'Recomendación',
        'match': {
            2023: '¿Recomendarías a tus compañeros participar',
            2024: '¿Recomendarías a tus compañeros participar',
            2025: 'Finalmente ¿Recomendarías',
        }
    },
]

# Buscar y mostrar detalles
def find_question(pregs_dict, search_str):
    """Busca la pregunta que contiene el substring"""
    for preg, info in pregs_dict.items():
        if search_str.lower() in preg.lower():
            return preg, info
    return None, None

for grupo in grupos_def:
    print(f"\n{'='*90}")
    print(f"  {grupo['id']}: {grupo['tema']}")
    print(f"{'='*90}")
    
    for year, search in grupo['match'].items():
        preg, info = find_question(preguntas_por_año[year], search)
        if preg:
            print(f"\n  [{year}] {preg[:130]}")
            print(f"  Alternativas ({len(info['alternativas'])}):")
            for j, alt in enumerate(info['alternativas'], 1):
                print(f"    {j:2d}. {alt[:100]}")
        else:
            print(f"\n  [{year}] NO ENCONTRADA para '{search[:60]}'")

print("\n\nFIN")
