"""HOMOLOGACIÓN FINAL — Base completa con todas las decisiones aprobadas"""
import sys,io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
sys.stderr=io.TextIOWrapper(sys.stderr.buffer,encoding='utf-8',errors='replace')
import pandas as pd,numpy as np,os,re

BASE=r"c:\Users\oyarc\OneDrive - Universidad San Sebastian\VCM\Encuestas Estudiantes\RV_ BASE ENCUESTA ESTUDIANTES 2021-2025"
OUT=r"c:\Users\oyarc\OneDrive - Universidad San Sebastian\VCM\Encuestas Estudiantes"

# Mapeos de texto a número
M_IMP={'muy importante':5,'importante':4,'medianamente importante':3,'poco importante':2,'nada importante':1}
M_FORT={'muy fortalecida':5,'se fortalece':4,'medianamente fortalecida':3,'poco fortalecida':2,'no se fortalece':1}
M_SIG={'muy significativo':5,'significativo':4,'medianamente significativo':3,'poco significativo':2,'nada significativo':1}
M_IMPACTO={'muy positivo':5,'positivo':4,'neutro (no impactó)':3,'negativo':2,'muy negativo':1}
M_ACU={'muy de acuerdo':5,'de acuerdo':4,'ni de acuerdo ni en desacuerdo':3,'en desacuerdo':2,'muy en desacuerdo':1}
M_CUMP={'totalmente':5,'casi totalmente':4,'medianamente':3,'sólo en parte':2,'no las cumplió':1}
M_CUMP25={'superó mis expectativas':5,'totalmente':4,'en gran medida':3,'sólo en parte':2,'no las cumplió':1}
M_SINO={'sí':1,'si':1,'no':0}

def clean(s):
    if pd.isna(s): return None
    return re.sub(r'\[\d+\]','',re.sub(r'\s+',' ',str(s))).strip().lower().rstrip('.')

def parse_text(val,mapping):
    c=clean(val)
    if c is None or c in ('sin información','nan','none','','0','0.0','no responde'): return np.nan
    v=mapping.get(c)
    if v is not None: return float(v)
    try: return float(c)
    except: return np.nan

def extract_onehot(data,raw,r2,col_start,n_opts,mapping):
    """Extrae valor de n_opts columnas one-hot. Detecta etiqueta en dato o en header."""
    n=len(data)
    # Primero: intentar detectar si los datos son 0/1 (one-hot binario)
    # y las etiquetas están en las celdas de datos (no en R2)
    # Buscar la etiqueta escaneando celdas de datos no-0/1
    col_labels={}
    for off in range(n_opts):
        ci=col_start+off
        if ci>=data.shape[1]: continue
        for j in range(min(50,len(data))):
            v=data.iloc[j,ci]
            if pd.notna(v):
                sv=str(v).strip()
                if sv not in ('0','1','0.0','1.0','Sin información','nan',''):
                    col_labels[off]=clean(v)
                    break
    # Si encontramos etiquetas en datos, usarlas
    if col_labels:
        result=np.full(n,np.nan)
        for i in range(n):
            for off in range(n_opts):
                ci=col_start+off
                if ci>=data.shape[1]: continue
                v=data.iloc[i,ci]
                if pd.notna(v):
                    sv=str(v).strip()
                    if sv in ('1','1.0'):
                        lb=col_labels.get(off)
                        if lb:
                            mapped=mapping.get(lb)
                            if mapped is not None: result[i]=float(mapped)
                        break
                    elif sv not in ('0','0.0','Sin información','nan',''):
                        lb=clean(v)
                        mapped=mapping.get(lb)
                        if mapped is not None: result[i]=float(mapped)
                        break
        return result
    # Fallback: etiquetas en R2
    labels=[]
    for off in range(n_opts):
        ci=col_start+off
        if ci<raw.shape[1]:
            lb=clean(raw.iloc[r2,ci])
            if lb and lb not in ('nan','none',''): labels.append((ci,lb))
    result=np.full(n,np.nan)
    for i in range(n):
        for ci,lb in labels:
            v=data.iloc[i,ci]
            if pd.notna(v) and str(v).strip()=='1':
                mapped=mapping.get(lb)
                if mapped is not None: result[i]=float(mapped)
                break
    return result

def extract_onehot_sino(data,raw,r2,col_start):
    return extract_onehot(data,raw,r2,col_start,2,M_SINO)

# Archivos
archivos={
    2021:("Encuesta estudiantes 2021 Reporte.xlsx","Base de datos",1,2,4),
    2022:("Encuesta estudiantes 2022 Reporte.xlsx","Base de datos",1,2,4),
    2023:("Encuesta estudiantes 2023 Reporte.xlsx","Base de datos encuestas ajuste",0,3,5),
    2024:("BASE ENCUESTA ESTUDIANTES 2024.xlsx","Reporte",0,2,4),
    2025:("BASE ENCUESTA ESTUDIANTES 2025.xlsx","Reporte",0,2,4),
}

# Configuración de columnas por año
# IMP: {code: col} — para 2024-2025 es col_start (5 cols one-hot)
IMP_COLS={
    2021:{'IMP_01':18,'IMP_02':22,'IMP_04':21,'IMP_05':19,'IMP_06':20,'IMP_07':23,'IMP_14':79},
    2022:{'IMP_01':18,'IMP_02':22,'IMP_03':20,'IMP_04':24,'IMP_05':19,'IMP_06':21,'IMP_07':23,'IMP_14':81},
    2023:{'IMP_01':10,'IMP_02':14,'IMP_03':12,'IMP_04':16,'IMP_05':11,'IMP_06':13,'IMP_07':15,'IMP_14':42},
    2024:{'IMP_01':15,'IMP_02':20,'IMP_03':25,'IMP_04':50,'IMP_07':30,'IMP_08':35,'IMP_09':40,'IMP_10':45,'IMP_14':123},
    2025:{'IMP_01':16,'IMP_02':21,'IMP_03':26,'IMP_04':56,'IMP_10':31,'IMP_11':36,'IMP_13':46,'IMP_14':51},
}

HAB_COLS={
    2021:{'HAB_02':37,'HAB_03':39,'HAB_04':36,'HAB_05':42,'HAB_07':38,'HAB_09':35,'HAB_10':40,'HAB_11':41},
    2022:{'HAB_01':47,'HAB_02':41,'HAB_03':43,'HAB_04':40,'HAB_05':46,'HAB_06':48,'HAB_07':42,'HAB_08':49,'HAB_09':39,'HAB_10':44,'HAB_11':45},
    2023:{'HAB_01':20,'HAB_02':21,'HAB_03':22,'HAB_04':27,'HAB_05':28,'HAB_06':25,'HAB_07':24,'HAB_08':29,'HAB_09':26,'HAB_10':23,'HAB_11':30},
    2024:{'HAB_01':65,'HAB_02':70,'HAB_03':75,'HAB_04':85,'HAB_05':90,'HAB_06':80,'HAB_07':100,'HAB_08':105,'HAB_11':95,'HAB_12':110},
    2025:{'HAB_01':71,'HAB_02':76,'HAB_03':81,'HAB_04':91,'HAB_05':96,'HAB_06':86,'HAB_07':101,'HAB_08':106,'HAB_10':111},
}

# RUT column indices
RUT_COL={2021:1,2022:1,2023:1,2024:0,2025:0}
# Meta columns (sede,facultad,carrera)
META_COLS={
    2021:{'SEDE':5,'FACULTAD':3,'CARRERA':2},
    2022:{'SEDE':5,'FACULTAD':3,'CARRERA':2},
    2023:{'SEDE':5,'FACULTAD':6,'CARRERA':7},
    2024:{'SEDE':7,'FACULTAD':8,'CARRERA':9},
    2025:{'SEDE':7,'FACULTAD':8,'CARRERA':9},
}

# Q01 Significancia columns
Q01_COL={2021:74,2022:76,2023:37,2024:10,2025:10}
# Beneficiados columns
BENEF_COL={2021:73,2022:75,2023:36,2024:140,2025:116}
# Expectativas columns
EXPECT_COL={2021:88,2022:88,2023:45,2024:151,2025:123}
# Campo laboral Sí/No
CAMPO_COL={2021:75,2022:77,2023:38,2024:115,2025:41}
# Recomendaría
RECOM_COL={2021:90,2022:90,2023:47,2024:156,2025:129}
# VcM
VCM_COL={2024:145,2025:121}
# Valores sebastianos: list of (col_start, n_options) per year
VAL_SEB={
    2021:[(24,10)],2022:[(28,10)],
    2023:'text3',  # 3 text columns 17,18,19
    2024:[(55,10)],2025:[(61,10)],
}
# Experiencia aprendizaje columns
EXP_COLS={
    2021:{'EXP_01':70,'EXP_02':71,'EXP_03':72,'EXP_04':85},
    2022:{'EXP_01':72,'EXP_02':73,'EXP_03':74,'EXP_04':87},
    2023:{'EXP_01':33,'EXP_02':34,'EXP_03':35,'EXP_04':44},
    2024:{'EXP_04':135},
}

ALL_IMP_KEYS=['IMP_01','IMP_02','IMP_03','IMP_04','IMP_05','IMP_06','IMP_07','IMP_08','IMP_09','IMP_10','IMP_11','IMP_13','IMP_14']
ALL_HAB_KEYS=['HAB_01','HAB_02','HAB_03','HAB_04','HAB_05','HAB_06','HAB_07','HAB_08','HAB_09','HAB_10','HAB_11','HAB_12']
ALL_EXP_KEYS=['EXP_01','EXP_02','EXP_03','EXP_04']
VAL_NAMES_2122=['Búsqueda de la verdad','Valor de la caridad y la justicia','Honestidad','Responsabilidad','Cultivo de la reflexión y la racionalidad','Solidaridad, alegría de servir y sentido del deber','Espíritu de superación y progreso personal','Laboriosidad y vocación por el trabajo bien hecho','Fortaleza y perseverancia','Ninguno']
VAL_NAMES_2425=['La racionalidad y capacidad de reflexión','La honestidad','La justicia','La responsabilidad y la prudencia','La tolerancia','La solidaridad y alegría de servir','El espíritu de superación','Fortaleza y perseverancia','La dignidad superior de la persona humana','El cultivo de la verdad']

frames=[]
for year,(fname,sheet,r_preg,r_alt,ds) in archivos.items():
    fp=os.path.join(BASE,fname)
    raw=pd.read_excel(fp,sheet_name=sheet,header=None)
    data=raw.iloc[ds:].reset_index(drop=True)
    n=len(data)
    is_oh=year in(2024,2025)
    print(f"\n{year}: {n} filas")

    # Base row
    row={'Año':[year]*n}
    # RUT
    rc=RUT_COL[year]
    row['RUT']=[str(data.iloc[i,rc]).strip() if pd.notna(data.iloc[i,rc]) else None for i in range(n)]
    # Meta
    for mk,ci in META_COLS[year].items():
        row[mk]=[str(data.iloc[i,ci]).strip() if pd.notna(data.iloc[i,ci]) else None for i in range(n)]

    # IMPORTANCIA ASPECTOS
    for k in ALL_IMP_KEYS:
        if k in IMP_COLS.get(year,{}):
            ci=IMP_COLS[year][k]
            if k == 'IMP_14':
                if year in (2021, 2022):
                    row[k] = [parse_text(data.iloc[i,ci], M_FORT) for i in range(n)]
                elif year == 2023:
                    row[k] = [parse_text(data.iloc[i,ci], M_ACU) for i in range(n)]
                elif year == 2024:
                    row[k] = extract_onehot(data, raw, r_alt, ci, 5, M_ACU)
                else:  # 2025
                    row[k] = extract_onehot(data, raw, r_alt, ci, 5, M_IMP)
            else:
                if is_oh: row[k]=extract_onehot(data,raw,r_alt,ci,5,M_IMP)
                else: row[k]=[parse_text(data.iloc[i,ci],M_IMP) for i in range(n)]
        else: row[k]=[np.nan]*n

    # HABILIDADES
    for k in ALL_HAB_KEYS:
        if k in HAB_COLS.get(year,{}):
            ci=HAB_COLS[year][k]
            if is_oh: row[k]=extract_onehot(data,raw,r_alt,ci,5,M_FORT)
            else: row[k]=[parse_text(data.iloc[i,ci],M_FORT) for i in range(n)]
        else: row[k]=[np.nan]*n

    # Q01 SIGNIFICANCIA (homologado: 2025 usa M_IMPACTO, resto M_SIG)
    ci=Q01_COL[year]
    if year==2025:
        row['Q01_Significancia']=extract_onehot(data,raw,r_alt,ci,5,M_IMPACTO)
    elif is_oh:
        row['Q01_Significancia']=extract_onehot(data,raw,r_alt,ci,5,M_SIG)
    else:
        row['Q01_Significancia']=[parse_text(data.iloc[i,ci],M_SIG) for i in range(n)]

    # BENEFICIADOS
    ci=BENEF_COL[year]
    if is_oh: row['Importancia_Beneficiados']=extract_onehot(data,raw,r_alt,ci,5,M_IMP)
    else: row['Importancia_Beneficiados']=[parse_text(data.iloc[i,ci],M_IMP) for i in range(n)]

    # EXPECTATIVAS (homologado: 2021-23=acuerdo, 2024=cump, 2025=cump+)
    ci=EXPECT_COL[year]
    if year<=2023:
        row['Cumplimiento_Expectativas']=[parse_text(data.iloc[i,ci],M_ACU) for i in range(n)]
    elif year==2024:
        row['Cumplimiento_Expectativas']=extract_onehot(data,raw,r_alt,ci,5,M_CUMP)
    else:
        row['Cumplimiento_Expectativas']=extract_onehot(data,raw,r_alt,ci,5,M_CUMP25)

    # CAMPO LABORAL Sí/No
    if year in CAMPO_COL:
        ci=CAMPO_COL[year]
        if year == 2025:
            # En 2025 es una escala likert de Importancia (1-5)
            # >= 3 es Sí (1), < 3 es No (0)
            raw_imp = extract_onehot(data, raw, r_alt, ci, 5, M_IMP)
            row['Campo_Laboral_SiNo'] = [1.0 if pd.notna(v) and v >= 3 else (0.0 if pd.notna(v) else np.nan) for v in raw_imp]
        else:
            if is_oh: row['Campo_Laboral_SiNo']=extract_onehot_sino(data,raw,r_alt,ci)
            else: row['Campo_Laboral_SiNo']=[parse_text(data.iloc[i,ci],M_SINO) for i in range(n)]
    else: row['Campo_Laboral_SiNo']=[np.nan]*n

    # RECOMENDARÍA
    ci=RECOM_COL[year]
    if is_oh: row['Recomendaria']=extract_onehot_sino(data,raw,r_alt,ci)
    else: row['Recomendaria']=[parse_text(data.iloc[i,ci],M_SINO) for i in range(n)]

    # VCM
    if year in VCM_COL:
        row['Vinculacion_Medio']=extract_onehot_sino(data,raw,r_alt,VCM_COL[year])
    else: row['Vinculacion_Medio']=[np.nan]*n

    # VALORES SEBASTIANOS (one-hot por valor)
    if year in (2021,2022):
        cs,no=VAL_SEB[year][0]
        for vi in range(min(no,len(VAL_NAMES_2122))):
            vn=VAL_NAMES_2122[vi]
            ci=cs+vi
            vals=[]
            for j in range(n):
                v=data.iloc[j,ci]
                if pd.notna(v) and str(v).strip() not in ('0','','nan','Sin información'):
                    vals.append(1.0)
                else: vals.append(0.0)
            row[f'VS_{vn}']=vals
    elif year==2023:
        # 3 text columns
        for vn in VAL_NAMES_2122:
            row[f'VS_{vn}']=[0.0]*n
        for col_i in [17,18,19]:
            for j in range(n):
                v=data.iloc[j,col_i]
                if pd.notna(v) and str(v).strip() not in ('','nan','Sin información'):
                    txt=str(v).strip()
                    for vn in VAL_NAMES_2122:
                        if vn.lower() in txt.lower():
                            row[f'VS_{vn}'][j]=1.0
    else:  # 2024,2025
        cs,no=VAL_SEB[year][0]
        for vi in range(min(no,len(VAL_NAMES_2425))):
            vn=VAL_NAMES_2425[vi]
            ci=cs+vi
            vals=[]
            for j in range(n):
                v=data.iloc[j,ci]
                if pd.notna(v) and str(v).strip()=='1':
                    vals.append(1.0)
                else: vals.append(0.0)
            row[f'VS_{vn}']=vals

    # EXPERIENCIA APRENDIZAJE
    for k in ALL_EXP_KEYS:
        if k in EXP_COLS.get(year,{}):
            ci=EXP_COLS[year][k]
            if year==2024:
                row[k]=extract_onehot(data,raw,r_alt,ci,5,M_ACU)
            else:
                row[k]=[parse_text(data.iloc[i,ci],M_ACU) for i in range(n)]
        else: row[k]=[np.nan]*n

    frames.append(pd.DataFrame(row))

df=pd.concat(frames,ignore_index=True)
print(f"\nBASE TOTAL: {len(df)} filas")

# === EXPORTAR ===
path=os.path.join(OUT,"base_homologada_final.xlsx")
meta=['Año','RUT','SEDE','FACULTAD','CARRERA']

with pd.ExcelWriter(path,engine='openpyxl') as w:
    # G1: Importancia Aspectos
    cols=meta+ALL_IMP_KEYS
    df[cols].to_excel(w,sheet_name='Importancia_Aspectos',index=False)
    print(f"  Importancia_Aspectos: {len(df)} filas")

    # G2: Habilidades
    cols=meta+ALL_HAB_KEYS
    df[cols].to_excel(w,sheet_name='Habilidades',index=False)

    # G3: Beneficiados
    df[meta+['Importancia_Beneficiados']].to_excel(w,sheet_name='Importancia_Beneficiados',index=False)

    # G4: Significancia
    df[meta+['Q01_Significancia']].to_excel(w,sheet_name='Significancia_Formacion',index=False)

    # G5: Expectativas
    df[meta+['Cumplimiento_Expectativas']].to_excel(w,sheet_name='Cumplimiento_Expectativas',index=False)

    # G6: Campo laboral
    df[meta+['Campo_Laboral_SiNo']].to_excel(w,sheet_name='Campo_Laboral_SiNo',index=False)

    # G7: Recomendaría
    df[meta+['Recomendaria']].to_excel(w,sheet_name='Recomendaria',index=False)

    # G8: VcM
    sub=df[df['Año'].isin([2024,2025])]
    sub[meta+['Vinculacion_Medio']].to_excel(w,sheet_name='Vinculacion_Medio',index=False)

    # G9: Valores
    vs_cols=[c for c in df.columns if c.startswith('VS_')]
    df[meta+vs_cols].to_excel(w,sheet_name='Valores_Sebastianos',index=False)

    # G10: Experiencia
    exp_sub=df[df['Año'].isin([2021,2022,2023,2024])]
    exp_sub[meta+ALL_EXP_KEYS].to_excel(w,sheet_name='Experiencia_Aprendizaje',index=False)

    # Diccionario
    dic=[
        {'Hoja':'Importancia_Aspectos','Descripción':'Importancia de aspectos formativos','Escala':'Likert 1-5','Años':'2021-2025','Homologación':'Escala idéntica todos los años'},
        {'Hoja':'Habilidades','Descripción':'Grado de fortalecimiento de habilidades','Escala':'Likert 1-5','Años':'2021-2025','Homologación':'Escala idéntica todos los años'},
        {'Hoja':'Importancia_Beneficiados','Descripción':'Importancia para comunidades beneficiadas','Escala':'Likert 1-5','Años':'2021-2025','Homologación':'Escala idéntica'},
        {'Hoja':'Significancia_Formacion','Descripción':'Significancia/impacto en formación','Escala':'Likert 1-5','Años':'2021-2025','Homologación':'2025 ajustado: Muy positivo=5, Positivo=4, Neutro=3, Negativo=2, Muy negativo=1'},
        {'Hoja':'Cumplimiento_Expectativas','Descripción':'Cumplimiento de expectativas','Escala':'Likert 1-5','Años':'2021-2025','Homologación':'2021-23: acuerdo→5pt. 2024: cumplimiento→5pt. 2025: Superó=5,Totalmente=4,Gran medida=3'},
        {'Hoja':'Campo_Laboral_SiNo','Descripción':'¿Permitió conocer campo laboral?','Escala':'0=No,1=Sí','Años':'2021-2024','Homologación':'Directo'},
        {'Hoja':'Recomendaria','Descripción':'¿Recomendaría participar?','Escala':'0=No,1=Sí','Años':'2021-2025','Homologación':'Directo'},
        {'Hoja':'Vinculacion_Medio','Descripción':'¿Sabía que era iniciativa VcM?','Escala':'0=No,1=Sí','Años':'2024-2025','Homologación':'Directo'},
        {'Hoja':'Valores_Sebastianos','Descripción':'Valores sebastianos seleccionados','Escala':'0/1 por valor','Años':'2021-2025','Homologación':'One-hot. 2021-23 tienen nombres cortos, 2024-25 nombres largos'},
        {'Hoja':'Experiencia_Aprendizaje','Descripción':'Evaluación experiencia de aprendizaje','Escala':'Likert 1-5 acuerdo','Años':'2021-2024','Homologación':'Escala idéntica'},
    ]
    pd.DataFrame(dic).to_excel(w,sheet_name='Diccionario',index=False)

# Verificación
print(f"\n{'='*50}\nVERIFICACIÓN\n{'='*50}")
for y in [2021,2022,2023,2024,2025]:
    sub=df[df['Año']==y]
    print(f"\n── {y} ({len(sub)}) ──")
    for c in ALL_IMP_KEYS[:4]+ALL_HAB_KEYS[:8]+['Q01_Significancia','Importancia_Beneficiados','Cumplimiento_Expectativas','Recomendaria']:
        vals=sub[c].dropna()
        if len(vals)>0: print(f"  {c}: n={len(vals)}, media={vals.mean():.2f}")

print(f"\n✅ Exportado: {path}")
print(f"Total filas: {len(df)}")
