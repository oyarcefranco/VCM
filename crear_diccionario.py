import pandas as pd
import os

OUT_PATH = r"c:\Users\oyarc\OneDrive - Universidad San Sebastian\VCM\Encuestas Estudiantes\diccionario_codigos.xlsx"

nombres_imp = {
    'IMP_01': 'Aplicar lo aprendido en clases',
    'IMP_02': 'Conocer la realidad (problemas/desafíos)',
    'IMP_03': 'Fortalecer vocación profesional',
    'IMP_04': 'Fortalecer valores sebastianos',
    'IMP_05': 'Potenciar desempeño futuro',
    'IMP_06': 'Desarrollar habilidades transversales',
    'IMP_07': 'Enfrentar desafíos con seguridad',
    'IMP_08': 'Compromiso con la sociedad',
    'IMP_09': 'Ser ciudadano responsable',
    'IMP_10': 'Incrementar redes de contactos',
    'IMP_11': 'Trabajar con otras carreras',
    'IMP_12': 'Conocer campo laboral',
    'IMP_13': 'Interactuar en contexto real',
    'IMP_14': 'Aportar desde el rol profesional'
}

nombres_hab = {
    'HAB_01': 'Empatía',
    'HAB_02': 'Comunicación efectiva',
    'HAB_03': 'Trabajo en equipo / Colaboración',
    'HAB_04': 'Resolución de problemas',
    'HAB_05': 'Adaptación y flexibilidad',
    'HAB_06': 'Competencia disciplinar',
    'HAB_07': 'Manejo de información (toma de decisiones)',
    'HAB_08': 'Prolijidad / Atención al detalle',
    'HAB_09': 'Pensamiento crítico y reflexivo',
    'HAB_10': 'Ciudadanía responsable',
    'HAB_11': 'Creatividad / Pensamiento innovador',
    'HAB_12': 'Autoconsciencia'
}

df_imp = pd.DataFrame(list(nombres_imp.items()), columns=['Código', 'Nombre Real'])
df_hab = pd.DataFrame(list(nombres_hab.items()), columns=['Código', 'Nombre Real'])

with pd.ExcelWriter(OUT_PATH, engine='openpyxl') as writer:
    df_imp.to_excel(writer, sheet_name='Nombres_Importancia', index=False)
    df_hab.to_excel(writer, sheet_name='Nombres_Habilidades', index=False)

print("Diccionario creado con éxito.")
