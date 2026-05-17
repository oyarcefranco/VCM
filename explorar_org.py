import pandas as pd
import os

BASE_DIR = r"c:\Users\oyarc\OneDrive - Universidad San Sebastian\VCM\Encuestas Estudiantes\Encuesta organizaciones externas"

files = {
    2021: ("Encuesta organizaciones 2021 Reporte.xlsx", "Raw Data"),
    2022: ("Encuesta organizaciones 2022 Reporte N°2.xlsx", "Raw Data"),
    2023: ("Encuesta organizaciones 2023 Reporte.xlsx", "Raw Data"),
    2024: ("Encuesta Organizaciones externas_2024.xlsx", "Reporte"),
    2025: ("Base de datos encuesta organizaciones externas 2025.xlsx", "Reporte")
}

with open('output_org_headers.txt', 'w', encoding='utf-8') as f:
    for year, (filename, sheet) in files.items():
        path = os.path.join(BASE_DIR, filename)
        f.write(f"\n{'='*50}\n")
        f.write(f"AÑO {year} - {sheet}\n")
        f.write(f"{'='*50}\n")
        try:
            df = pd.read_excel(path, sheet_name=sheet, nrows=5)
            cols = list(df.columns)
            for i, c in enumerate(cols):
                f.write(f"[{i}] {c}\n")
        except Exception as e:
            f.write(f"Error: {e}\n")
