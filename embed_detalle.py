import json
import re

html_path = r'c:\Users\oyarc\OneDrive - Universidad San Sebastian\VCM\Encuestas Estudiantes\dashboard_vcm.html'
json_path = r'c:\Users\oyarc\OneDrive - Universidad San Sebastian\VCM\Encuestas Estudiantes\dashboard_data_detalle.json'
out_path = r'c:\Users\oyarc\OneDrive - Universidad San Sebastian\VCM\Encuestas Estudiantes\dashboard_vcm_detalle.html'

with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

json_str = json.dumps(data, ensure_ascii=False, default=str)

with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Replace the DATA object using a more robust regex
html = re.sub(r'DATA\s*=\s*\{.*?\};\s*init\(\);', 'DATA=' + json_str + '; init();', html, flags=re.DOTALL)

with open(out_path, 'w', encoding='utf-8') as f:
    f.write(html)

print('Created dashboard_vcm_detalle.html with embedded data.')
