"""
Script de exploración profunda de la estructura real de los archivos Excel.
Detecta si los headers reales están en filas distintas a la fila 0.
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import pandas as pd
import os

BASE_DIR = r"c:\Users\oyarc\OneDrive - Universidad San Sebastian\VCM\Encuestas Estudiantes\RV_ BASE ENCUESTA ESTUDIANTES 2021-2025"

archivos = {
    2021: os.path.join(BASE_DIR, "Encuesta estudiantes 2021 Reporte.xlsx"),
    2022: os.path.join(BASE_DIR, "Encuesta estudiantes 2022 Reporte.xlsx"),
    2023: os.path.join(BASE_DIR, "Encuesta estudiantes 2023 Reporte.xlsx"),
    2024: os.path.join(BASE_DIR, "BASE ENCUESTA ESTUDIANTES 2024.xlsx"),
    2025: os.path.join(BASE_DIR, "BASE ENCUESTA ESTUDIANTES 2025.xlsx"),
}

for year, filepath in archivos.items():
    print(f"\n{'='*80}")
    print(f"  ARCHIVO {year}")
    print(f"{'='*80}")
    
    xls = pd.ExcelFile(filepath)
    print(f"  Hojas: {xls.sheet_names}")
    
    # Leer sin header para ver las primeras filas tal cual
    for sheet_name in xls.sheet_names:
        print(f"\n  --- Hoja: '{sheet_name}' ---")
        df_raw = pd.read_excel(filepath, sheet_name=sheet_name, header=None, nrows=5)
        print(f"  Shape (primeras 5 filas): {df_raw.shape}")
        
        # Mostrar las primeras 5 filas, primeras 15 columnas
        max_cols = min(15, df_raw.shape[1])
        for row_idx in range(min(5, len(df_raw))):
            print(f"\n  Fila {row_idx}:")
            for col_idx in range(max_cols):
                val = df_raw.iloc[row_idx, col_idx]
                val_str = str(val)[:120] if pd.notna(val) else "NaN"
                print(f"    Col[{col_idx:3d}]: {val_str}")
        
        # También mostrar las últimas columnas con nombre
        df_with_header = pd.read_excel(filepath, sheet_name=sheet_name, nrows=3)
        named_cols = [c for c in df_with_header.columns if not str(c).startswith('Unnamed')]
        print(f"\n  Columnas con nombre real ({len(named_cols)}):")
        for c in named_cols:
            print(f"    - {str(c)[:150]}")
        
        # Solo procesar la primera hoja relevante
        if sheet_name in ['Base de datos', 'Base de datos encuestas ajuste', 'Reporte']:
            break
