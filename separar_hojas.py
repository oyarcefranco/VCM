"""Separar base unificada en hojas comparables dentro de un Excel"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
import pandas as pd, numpy as np, os

OUT = r"c:\Users\oyarc\OneDrive - Universidad San Sebastian\VCM\Encuestas Estudiantes"
df = pd.read_csv(os.path.join(OUT, "base_unificada_homologada.csv"), encoding='utf-8-sig')
META = ['Año','SEDE','FACULTAD','CARRERA']

sheets = {}

# 1. Importancia Aspectos — Likert 1-5 idéntica todos los años
cols = ['Q02_Importancia_Aspectos_Aplicar','Q03_Importancia_Aspectos_Realidad',
        'Q04_Importancia_Aspectos_Vocacion','Q05_Importancia_Aspectos_Valores']
sheets['Importancia_Aspectos'] = df[META + cols].copy()

# 2. Habilidades — Likert 1-5 idéntica todos los años
cols = ['Q06_Habilidad_Empatia','Q07_Habilidad_Comunicacion','Q08_Habilidad_Colaboracion',
        'Q09_Habilidad_Resolucion','Q10_Habilidad_Adaptacion','Q11_Habilidad_Competencia',
        'Q12_Habilidad_Prolijidad','Q13_Habilidad_Manejo_Info']
sheets['Habilidades'] = df[META + cols].copy()

# 3. Q15 Importancia Beneficiados — Likert 1-5, solo 2023-2025
sub = df[df['Año'].isin([2023,2024,2025])].copy()
sheets['Q15_Importancia_Benef'] = sub[META + ['Q15_Importancia_Beneficiados']]

# 4. Q18 Recomendaría — Sí/No, 2023-2025
sub = df[df['Año'].isin([2023,2024,2025])].copy()
sheets['Q18_Recomendaria'] = sub[META + ['Q18_Recomendaria']]

# 5. Q19 Vinculación Medio — Sí/No, 2024-2025
sub = df[df['Año'].isin([2024,2025])].copy()
sheets['Q19_Vinculacion_Medio'] = sub[META + ['Q19_Vinculacion_Medio']]

# 6. Q01 escala "Significativo" — 2023-2024
sub = df[df['Año'].isin([2023,2024])].copy()
sheets['Q01_Significativo_23_24'] = sub[META + ['Q01_Significancia_Formacion']]

# 7. Q01 escala "Impacto positivo/negativo" — 2025 (NO comparable con 2023-2024)
sub = df[df['Año']==2025].copy()
sheets['Q01_Impacto_2025'] = sub[META + ['Q01_Significancia_Formacion']]

# 8. Q16 Campo laboral Likert 1-5 — 2021-2022
sub = df[df['Año'].isin([2021,2022])].copy()
sheets['Q16_Likert_21_22'] = sub[META + ['Q16_Conocer_Campo_Laboral']]

# 9. Q16 Campo laboral Sí/No — 2023-2024
sub = df[df['Año'].isin([2023,2024])].copy()
sheets['Q16_SiNo_23_24'] = sub[META + ['Q16_Conocer_Campo_Laboral']]

# 10. Q17 Expectativas escala Acuerdo — 2023
sub = df[df['Año']==2023].copy()
sheets['Q17_Acuerdo_2023'] = sub[META + ['Q17_Cumplimiento_Expectativas']]

# 11. Q17 Expectativas escala Cumplimiento — 2024-2025
sub = df[df['Año'].isin([2024,2025])].copy()
sheets['Q17_Cumplimiento_24_25'] = sub[META + ['Q17_Cumplimiento_Expectativas']]

# 12. Q14 Valores Sebastianos — Texto, 2021-2024
sub = df[df['Año'].isin([2021,2022,2023,2024])].copy()
sheets['Q14_Valores_Texto'] = sub[META + ['Q14_Valores_Sebastianos']]

# 13. Diccionario
dict_rows = [
    {'Hoja':'Importancia_Aspectos','Preguntas':'Q02-Q05','Escala':'Likert 1-5 (Nada→Muy importante)','Años':'2021-2025','Comparable':'✅ Sí'},
    {'Hoja':'Habilidades','Preguntas':'Q06-Q13','Escala':'Likert 1-5 (No se fortalece→Muy fortalecida)','Años':'2021-2025','Comparable':'✅ Sí'},
    {'Hoja':'Q15_Importancia_Benef','Preguntas':'Q15','Escala':'Likert 1-5 (Nada→Muy importante)','Años':'2023-2025','Comparable':'✅ Sí'},
    {'Hoja':'Q18_Recomendaria','Preguntas':'Q18','Escala':'0=No, 1=Sí','Años':'2023-2025','Comparable':'✅ Sí'},
    {'Hoja':'Q19_Vinculacion_Medio','Preguntas':'Q19','Escala':'0=No, 1=Sí','Años':'2024-2025','Comparable':'✅ Sí'},
    {'Hoja':'Q01_Significativo_23_24','Preguntas':'Q01','Escala':'1-5 (Nada→Muy significativo)','Años':'2023-2024','Comparable':'✅ Sí entre sí'},
    {'Hoja':'Q01_Impacto_2025','Preguntas':'Q01','Escala':'1-5 (Muy negativo→Muy positivo)','Años':'2025','Comparable':'⚠️ NO comparable con 2023-2024'},
    {'Hoja':'Q16_Likert_21_22','Preguntas':'Q16','Escala':'Likert 1-5','Años':'2021-2022','Comparable':'✅ Sí entre sí'},
    {'Hoja':'Q16_SiNo_23_24','Preguntas':'Q16','Escala':'0=No, 1=Sí','Años':'2023-2024','Comparable':'⚠️ NO comparable con 2021-2022'},
    {'Hoja':'Q17_Acuerdo_2023','Preguntas':'Q17','Escala':'1-5 (Muy en desacuerdo→Muy de acuerdo)','Años':'2023','Comparable':'⚠️ Escala distinta a 2024-2025'},
    {'Hoja':'Q17_Cumplimiento_24_25','Preguntas':'Q17','Escala':'1-5 (No cumplió→Totalmente/Superó)','Años':'2024-2025','Comparable':'⚠️ 2025 agrega "Superó expectativas"'},
    {'Hoja':'Q14_Valores_Texto','Preguntas':'Q14','Escala':'Texto (valores separados por |)','Años':'2021-2024','Comparable':'✅ Cualitativo'},
]
sheets['Diccionario'] = pd.DataFrame(dict_rows)

# Exportar
path = os.path.join(OUT, "base_unificada_por_hojas.xlsx")
with pd.ExcelWriter(path, engine='openpyxl') as writer:
    for name, sdf in sheets.items():
        sdf.to_excel(writer, sheet_name=name, index=False)
        print(f"  {name}: {sdf.shape[0]:,} filas x {sdf.shape[1]} cols")

print(f"\n✅ {path}")
