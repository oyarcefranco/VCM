import pandas as pd, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
xls = pd.ExcelFile(r'c:\Users\oyarc\OneDrive - Universidad San Sebastian\VCM\Encuestas Estudiantes\metricas_dimensiones.xlsx')
print('Sheets:', xls.sheet_names)
for s in xls.sheet_names:
    df = pd.read_excel(xls, s)
    print(f"\n=== {s} ===")
    print("Columns:", list(df.columns))
    print(df.head(5).to_string())
    print(f"... ({len(df)} rows)")
