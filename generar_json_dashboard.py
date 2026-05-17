"""Genera JSON desde metricas_detalladas_vcm.xlsx y Métricas_Dimensiones.xlsx"""
import sys,io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
import pandas as pd,numpy as np,json,os

BASE=r"c:\Users\oyarc\OneDrive - Universidad San Sebastian\VCM\Encuestas Estudiantes"
MET=os.path.join(BASE,"metricas_detalladas_vcm.xlsx")
DIM=os.path.join(BASE,"metricas_dimensiones.xlsx")
OUT=os.path.join(BASE,"dashboard_vcm_data.json")

print("Cargando metricas...")
df_lik=pd.read_excel(MET,'Metricas_Likert')
df_dic=pd.read_excel(MET,'Metricas_Dicotomicas')
df_vs=pd.read_excel(MET,'Metricas_Valores_Sebastianos')

def to_rec(df):
    recs=[]
    for _,r in df.iterrows():
        d={}
        for c in df.columns:
            v=r[c]
            if pd.isna(v):d[c]=None
            elif isinstance(v,(np.integer,int)):d[c]=int(v)
            elif isinstance(v,(np.floating,float)):d[c]=round(float(v),6)
            else:d[c]=str(v)
        recs.append(d)
    return recs

lik_recs=to_rec(df_lik)
dic_recs=to_rec(df_dic)
vs_recs=to_rec(df_vs)

# Dimensiones
print("Cargando dimensiones...")
dim_xls=pd.ExcelFile(DIM)
dim_desc={
    'Dim_1':{'t':'Despliegue territorial y articulación con el entorno','d':'Observar el nivel de cobertura territorial, el alcance del despliegue institucional y la capacidad de articulación con actores relevantes del entorno.'},
    'Dim_2':{'t':'Sostenibilidad y reputación del vínculo con el entorno','d':'Observar la capacidad institucional para sostener relaciones de colaboración con actores del entorno en el tiempo, así como la valoración y reconocimiento que dichos actores desarrollan respecto de la VcM.'},
    'Dim_5':{'t':'Resultados formativos en estudiantes','d':'Observar la contribución de la VcM al desarrollo formativo de los estudiantes, considerando el fortalecimiento de competencias disciplinares y transversales.'},
    'Dim_6':{'t':'Desarrollo académico y fortalecimiento de la práctica docente','d':'Observar el fortalecimiento del desarrollo académico, la innovación en la práctica docente y la consolidación del rol del académico en el marco de la VcM.'},
    'Dim_7':{'t':'Generación de conocimiento','d':'Observar la capacidad de la VcM para contribuir a la generación y difusión de conocimiento académico y disciplinar.'},
    'Dim_8':{'t':'Pertinencia territorial y conexión con el entorno','d':'Evaluar el despliegue institucional asociado al desarrollo territorial y la capacidad de la universidad para vincularse con las necesidades del entorno relevante.'},
    'Dim_9':{'t':'Valoración y contribución territorial de la VcM','d':'Evaluar la valoración que actores externos realizan respecto de la calidad y contribución de las iniciativas de VcM.'},
    'Dim_10':{'t':'Capacidades institucionales de la VcM','d':'Observar el nivel de desarrollo y consolidación de las capacidades institucionales destinadas a sostener la implementación de la VcM.'},
    'Dim_11':{'t':'Gestión y desempeño de la VcM','d':'Observar el nivel de cumplimiento, seguimiento y desempeño de las iniciativas y mecanismos institucionales asociados a la VcM.'},
    'Dim_12':{'t':'Recursos e inversión en VcM','d':'Observar el nivel de recursos humanos, financieros, tecnológicos y organizacionales destinados al desarrollo de la VcM.'}
}
dims={}
for s in dim_xls.sheet_names:
    df=pd.read_excel(dim_xls,s)
    yc=[c for c in df.columns if c!='Indicador']
    inds=[]
    for _,r in df.iterrows():
        ind={'nombre':str(r['Indicador'])}
        for y in yc:
            v=r[y]
            if pd.isna(v) or str(v).strip() in ['-','S/I','']:ind[str(y)]='Sin información'
            else:
                try:
                    fv=float(str(v).replace('%','').replace(',','.').replace('\xa0','').strip())
                    if '%' in str(v):ind[str(y)]=round(fv/100,4) if fv>1 else round(fv,4)
                    elif 0<fv<1:ind[str(y)]=round(fv,4)
                    else:ind[str(y)]=int(fv) if fv==int(fv) else round(fv,2)
                except:ind[str(y)]=str(v)
        inds.append(ind)
    info=dim_desc.get(s,{'t':s,'d':''})
    dims[s]={'titulo':info['t'],'descripcion':info['d'],'anios':[str(c) for c in yc],'indicadores':inds}

# Categorias metadata
cat_meta={
    'importancia':{'titulo':'Importancia Aspectos','descripcion':'Mide qué tan importante consideran los estudiantes que fue el Proyecto Colaborativo para diferentes aspectos de su vida académica y personal. La pregunta fue: "Evalúa el grado de importancia que tuvo participar en el Proyecto Colaborativo para el logro de los siguientes aspectos:". Fórmula Top-2-Box: (Número de respuestas Importante + Número de respuestas Muy importante) / Total de respuestas.','escala':['Nada importante','Poco importante','Medianamente importante','Importante','Muy importante'],'tip':'Seleccione un solo indicador y un año específico para ver el número de respuestas validadas (N).'},
    'habilidades':{'titulo':'Desarrollo de Habilidades','descripcion':'Mide el grado en que el estudiante percibe que el proyecto le ayudó a fortalecer habilidades blandas y transversales. La pregunta fue: "En base a tu experiencia en el Proyecto Colaborativo, evalúa el grado de fortalecimiento de las siguientes habilidades:". Fórmula Top-2-Box: (Número de respuestas Fortalecida + Número de respuestas Muy Fortalecida) / Total de respuestas.','escala':['Nada fortalecida','Poco fortalecida','Medianamente fortalecida','Fortalecida','Muy fortalecida'],'tip':'Seleccione un solo indicador y un año específico para ver el número de respuestas validadas (N).'},
    'indicadores':{'titulo':'Indicadores Clave','descripcion':'Métricas generales de percepción del impacto de los Proyectos Colaborativos de Vinculación con el Medio.','tip':'Seleccione un solo indicador y un año específico para ver el número de respuestas validadas (N).','sub':{
        'Significancia en Formación':{'p':'¿Cuán significativo fue el aporte del proyecto para tu formación profesional?','t':'likert','e':['Nada significativo','Poco significativo','Medianamente significativo','Significativo','Muy significativo']},
        'Cumplimiento de Expectativas':{'p':'En general, ¿en qué medida el Proyecto cumplió tus expectativas?','t':'likert','e':['No las cumplió','Sólo en parte','Medianamente','Casi totalmente','Totalmente']},
        'Importancia para Comunidades Beneficiadas':{'p':'Para las comunidades/entorno beneficiado, ¿cuán importante fue la ejecución del proyecto?','t':'likert','e':['Nada importante','Poco importante','Medianamente importante','Importante','Muy importante']},
        'Recomendaría a compañeros':{'p':'¿Recomendarías a otros estudiantes participar en un Proyecto Colaborativo VcM?','t':'dico'},
        'Permitió conocer campo laboral':{'p':'¿Te permitió conocer cómo se desarrolla tu profesión en la vida real/campo laboral?','t':'dico'},
        'Sabía que era iniciativa VcM':{'p':'¿Sabías que esta iniciativa corresponde a Vinculación con el Medio?','t':'dico'}
    }},
    'valores':{'titulo':'Valores Sebastianos','descripcion':'Pregunta: "Identifica qué Valores Sebastianos estuvieron presentes en el proyecto". Selección múltiple. Métrica: % de estudiantes que lo marcó. Nota: Esta pregunta solo fue respondida por los estudiantes que previamente declararon que el proyecto colaborativo les ayudó a fortalecer los Valores Sebastianos.'}
}

out={'likert':lik_recs,'dicotomicas':dic_recs,'valores_sebastianos':vs_recs,'dimensiones':dims,'categorias':cat_meta,'meta':{'anios':[2021,2022,2023,2024,2025]}}

print("Serializando...")
with open(OUT,'w',encoding='utf-8') as f:
    json.dump(out,f,ensure_ascii=False,separators=(',',':'))
sz=os.path.getsize(OUT)/(1024*1024)
print(f"JSON: {sz:.2f} MB | Likert: {len(lik_recs)} | Dico: {len(dic_recs)} | VS: {len(vs_recs)}")
